from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings


class CustomUser(AbstractUser):
    primary_key = models.CharField(max_length=300, unique=True, null=True, blank=True)
    public_key = models.CharField(max_length=300, unique=True, null=True, blank=True)

    def __str__(self):
        return self.username

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
    def __str__(self):
        return self.text

class Coin(models.Model):
    name = models.CharField(max_length=200)
    symbol = models.CharField(max_length=10)
    price = models.DecimalField(max_digits=20, decimal_places=8)
    market_cap = models.DecimalField(max_digits=20, decimal_places=2)
    volume_24h = models.DecimalField(max_digits=20, decimal_places=2)
    change_24h = models.DecimalField(max_digits=5, decimal_places=2)
    
    def __str__(self):
        return f"{self.name} ({self.symbol})"
    

class Wallet(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    coin = models.ForeignKey(Coin, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    amount = models.DecimalField(max_digits=20, decimal_places=8)
    value = models.DecimalField(max_digits=20, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user} - {self.coin.name} ({self.amount})"