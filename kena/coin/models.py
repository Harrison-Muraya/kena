from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings
from . import blockchain


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
    amount = models.DecimalField(max_digits=20, decimal_places=8)
    value = models.DecimalField(max_digits=20, decimal_places=2)
    password = models.CharField(max_length=200, null=True, blank=True)
    Wallettype = models.CharField(max_length=20, default='personal')
    hash = models.CharField(max_length=64, unique=True)
    flag = models.IntegerField(default=1)
    status = models.IntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user}  -  {self.name}  -  {self.hash}  - {self.created_at}"


class Billing(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=20, decimal_places=2)
    uid = models.CharField(max_length=100, unique=True)
    type = models.CharField(max_length=20, default='gift')
    flag = models.IntegerField(default=1)
    status = models.CharField(max_length=20, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user} - {self.wallet.name} - {self.amount} - {self.type} - {self.status} - {self.created_at}"
    
    
class Transaction(models.Model):
    billing = models.ForeignKey(Billing, on_delete=models.CASCADE, null=False, blank=False)
    gateway = models.CharField(max_length=100, default='kena')
    sender = models.CharField(max_length=100)
    receiver = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=20, decimal_places=2)
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