from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import User
from django.conf import settings
from . import blockchain
from django.utils.timezone import now

# This model is used to create a custom user model that extends the default Django user model
# It includes additional fields for private key, public key, flag, and status
class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)
    private_key = models.TextField(unique=True, null=True, blank=True)
    public_key = models.TextField(unique=True, null=True, blank=True)
    terms_accepted = models.BooleanField(default=False)
    flag = models.IntegerField(default=1)
    status = models.BooleanField(default=1)
    
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    def __str__(self):
        return f"{self.username} - {self.email} - {self.date_joined}"
    

    
class UserProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    phone = models.CharField(max_length=20)
    marketing_consent = models.BooleanField(default=False)
    email_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    flag = models.IntegerField(default=1)
    status = models.BooleanField(default=1)

    def __str__(self):
        return f"{self.user.username}'s Profile"

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
    
# This model is used to store information about different cryptocurrencies
# It includes fields for name, symbol, price, market cap, volume in the last 24 hours, change in the last 24 hours, flag, status, and creation timestamp
# The __str__ method returns a string representation of the coin including its name and symbol
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
    
# This model is used to store wallet information for users
# It includes fields for user, coin, name, amount, value, password, wallet type, hash, flag, status, and creation timestamp
# The __str__ method returns a string representation of the wallet including its name and balance
class Wallet(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    coin = models.ForeignKey(Coin, null=True, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    amount = models.DecimalField(max_digits=20, decimal_places=5, default=0)
    value = models.DecimalField(max_digits=20, decimal_places=2)
    password = models.CharField(max_length=200, null=True, blank=True)
    wallettype = models.CharField(max_length=20, default='personal')
    hash = models.CharField(max_length=64, unique=True)
    flag = models.IntegerField(default=1)
    status = models.IntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.name} - Balance: {self.amount}K"
    
    def get_color_scheme(self):
        """Return Tailwind CSS gradient classes based on wallet type"""
        color_schemes = {
            'personal': {
                'gradient': 'from-kena-gold via-yellow-500 to-orange-500',
                'text': 'text-black',
                'overlay_top': 'bg-white/20',
                'overlay_bottom': 'bg-black/10',
                'badge': 'bg-black/20',
            },
            'business': {
                'gradient': 'from-purple-600 via-blue-600 to-indigo-700',
                'text': 'text-white',
                'overlay_top': 'bg-white/10',
                'overlay_bottom': 'bg-white/5',
                'badge': 'bg-white/20',
            },
            'miner': {
                'gradient': 'from-green-600 via-emerald-600 to-teal-700',
                'text': 'text-white',
                'overlay_top': 'bg-white/10',
                'overlay_bottom': 'bg-white/5',
                'badge': 'bg-white/20',
            },
        }
        return color_schemes.get(self.wallettype, color_schemes['personal'])
    
    def get_wallet_label(self):
        """Return human-readable wallet type label"""
        labels = {
            'personal': 'Personal Wallet',
            'business': 'Business Wallet',
            'miner': 'Mining Rewards',
        }
        return labels.get(self.wallettype, 'Personal Wallet')
    
    def get_wallet_subtitle(self):
        """Return subtitle for wallet type"""
        subtitles = {
            'personal': 'Main Account',
            'business': 'Business Holdings',
            'miner': 'Earned from Mining',
        }
        return subtitles.get(self.wallettype, 'Main Account')

# This model is used to store billing information for users
# It includes fields for user, wallet, amount, unique identifier (uid), type, flag, status, and timestamps
class Billing(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=20, decimal_places=5)
    fee = models.DecimalField(max_digits=20, decimal_places=5, default=0)
    total = models.DecimalField(max_digits=20, decimal_places=5, default=0)
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
    type = models.CharField(max_length=20, default='send')
    debit = models.DecimalField(max_digits=20, decimal_places=5, default=0)
    credit = models.DecimalField(max_digits=20, decimal_places=5, default=0)
    sender = models.CharField(max_length=100)
    receiver = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=20, decimal_places=5)
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
    # type = models.CharField(max_length=20, default='receive')
    timestamp = models.DateTimeField(default=now)  
    previous_hash = models.CharField(max_length=64)
    hash = models.CharField(max_length=64, unique=True)
    transactions = models.JSONField() # to strore transactions in a json format

    def __str__(self):
        return f"Block {self.height} - {self.hash[:10]}..."

# This model is used to store pending transactions
# It includes fields for sender, receiver, amount, timestamp, and a unique hash
class PendingTransaction(models.Model):
    billing = models.ForeignKey(Billing, on_delete=models.CASCADE)
    gateway = models.CharField(max_length=100, default='kena')
    type = models.CharField(max_length=20, default='send')
    debit = models.DecimalField(max_digits=20, decimal_places=5, default=0)
    credit = models.DecimalField(max_digits=20, decimal_places=5, default=0)
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    receiver = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='receiver', null=True, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=20, decimal_places=5)
    timestamp = models.DateTimeField(default=now)  # Manually set timestamp
    hash = models.CharField(max_length=64, unique=True, blank=True)
    signature = models.CharField(null=True, blank=True)

    def save(self, *args, **kwargs):
        # Only calculate hash if not already set
        if not self.hash:
            data = {
                "sender": str(self.sender),
                "receiver": str(self.receiver),
                "amount": str(self.amount),
                "timestamp": str(self.timestamp),
            }
            self.hash = blockchain.CalculateHash(data).calculate()

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.sender} -> {self.receiver}: {self.amount}-> {self.signature}"
    
# 

# class PendingTransaction(models.Model, object):
#     def __init__(self, billing, sender, receiver, amt, time):
#         self.billing = billing
#         self.sender = sender
#         self.receiver = receiver
#         self.amt = amt
#         self.time = time

#         data = {
#             "billing": self.billing,
#             "sender": self.sender,
#             "receiver": self.receiver,
#             "amt": str(self.amt),
#             "time": str(self.time)
#         }
#         self.hash = blockchain.CalculateHash(data).calculate()
#         print("Pending Transaction Hash: ", self.hash)
#         super().__init__()
#     billing = models.ForeignKey(Billing, on_delete=models.CASCADE)
#     gateway = models.CharField(max_length=100, default='kena')
#     type = models.CharField(max_length=20, default='send')
#     debit = models.DecimalField(max_digits=20, decimal_places=5, default=0)
#     credit = models.DecimalField(max_digits=20, decimal_places=5, default=0)
#     sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
#     receiver = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='receiver', null=True, on_delete=models.CASCADE)
#     amount = models.DecimalField(max_digits=20, decimal_places=5)
#     timestamp = models.DateTimeField(default=now)  # Manually set timestamp
#     hash = models.CharField(max_length=64, unique=True, blank=True)

#     def save(self, *args, **kwargs):
#         # Only calculate hash if not already set
#         if not self.hash:
#             data = {
#                 "sender": str(self.sender),
#                 "receiver": str(self.receiver),
#                 "amount": str(self.amount),
#                 "timestamp": str(self.timestamp),
#             }
#             self.hash = blockchain.CalculateHash(data).calculate()

#         super().save(*args, **kwargs)

#     def __str__(self):
#         return f"{self.sender} -> {self.receiver}: {self.amount}"
