from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings
from . import blockchain

# This model is used to create a custom user model that extends the default Django user model
# It includes additional fields for private key, public key, flag, and status
class CustomUser(AbstractUser):
    private_key = models.CharField(max_length=300, unique=True, null=True, blank=True)
    public_key = models.CharField(max_length=300, unique=True, null=True, blank=True)
    flag = models.IntegerField(default=1)
    status = models.BooleanField(default=1)

    def __str__(self):
        return f"{self.username} - {self.email} - {self.date_joined}"

class Todolist(models.Model):
    name = models.CharField(max_length=200)
    check_box = models.BooleanField(default=False)
    flag = models.IntegerField(default=1)
    def __str__(self):
        return self.name
    
class Item (models.Model):
    todo_list = models.ForeignKey(Todolist, on_delete=models.CASCADE)
    text = models.CharField(max_length=200)
    complete = models.BooleanField()
    flag = models.IntegerField(default=1)
    status = models.BooleanField(default=1)
    def __str__(self):
        return self.text

class Coin(models.Model):
    name = models.CharField(max_length=200)
    symbol = models.CharField(max_length=10)
    price = models.DecimalField(max_digits=20, decimal_places=8)
    market_cap = models.DecimalField(max_digits=20, decimal_places=2)
    volume_24h = models.DecimalField(max_digits=20, decimal_places=2)
    change_24h = models.DecimalField(max_digits=5, decimal_places=2)
    flag = models.IntegerField(default=1)
    status = models.BooleanField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.name} ({self.symbol})"
    

class Wallet(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    coin = models.ForeignKey(Coin, null=True, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    amount = models.DecimalField(max_digits=20, decimal_places=5)
    value = models.DecimalField(max_digits=20, decimal_places=2)
    password = models.CharField(max_length=200, null=True, blank=True)
    Wallettype = models.CharField(max_length=20, default='personal')
    hash = models.CharField(max_length=64, unique=True)
    flag = models.IntegerField(default=1)
    status = models.IntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.name} - Balance: {self.amount}K"

# This model is used to store billing information for users
# It includes fields for user, wallet, amount, unique identifier (uid), type, flag, status, and timestamps
class Billing(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=20, decimal_places=5)
    uid = models.CharField(max_length=100, unique=True)
    type = models.CharField(max_length=20, default='gift')
    flag = models.IntegerField(default=1)
    status = models.CharField(max_length=20, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user} - {self.wallet.name} - {self.amount} - {self.type} - {self.status} - {self.created_at}"
    
# This model is used to store transaction details
# It includes fields for billing, gateway, sender, receiver, amount, fee, time, and a unique hash
# The save method calculates the hash for the transaction based on the provided data   
class Transaction(models.Model):
    billing = models.ForeignKey(Billing, on_delete=models.CASCADE, null=False, blank=False)
    gateway = models.CharField(max_length=100, default='kena')
    sender = models.CharField(max_length=100)
    receiver = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=20, decimal_places=5)
    fee = models.DecimalField(max_digits=20, decimal_places=2)
    time = models.DateTimeField(auto_now_add=True)
    hash = models.CharField(max_length=64, unique=True)
    

    def __str__(self):
        return f"Transaction from {self.sender} to {self.receiver} of {self.amount} at {self.time}"
    
    def save(self, *args, **kwargs):
        data = {
            "billing": self.billing.id if self.billing else None,
            "gateway": self.gateway,
            "sender": self.sender,
            "receiver": self.receiver,
            "amount": str(self.amount),
            "time": str(self.time)
        }
        self.hash = blockchain.CalculateHash(data).calculate()
        super().save(*args, **kwargs)  # Call the "real" save() method

# This model is used to store blocks in the blockchain
# It includes fields for height, nonce, timestamp, previous hash, hash, and transactions    
class Block(models.Model):
    height = models.IntegerField()
    nonce = models.IntegerField()
    timestamp = models.FloatField()
    previous_hash = models.CharField(max_length=64)
    hash = models.CharField(max_length=64, unique=True)
    transactions = models.TextField()  # JSON serialized transactions

    def __str__(self):
        return f"Block {self.height} - {self.hash[:10]}..."

# This model is used to store pending transactions
# It includes fields for sender, receiver, amount, timestamp, and a unique hash
class PendingTransaction(models.Model):
    sender = models.CharField(max_length=100)
    receiver = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=20, decimal_places=2)
    timestamp = models.DateTimeField(auto_now_add=True)
    hash = models.CharField(max_length=64, unique=True)

    def __str__(self):
        return f"{self.sender} -> {self.receiver}: {self.amount}"
