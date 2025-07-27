from django.contrib import admin
from .models import CustomUser, Todolist, Item, Coin, Wallet

# Register your models here.
admin.site.register(CustomUser)
admin.site.register(Todolist)
admin.site.register(Item)
admin.site.register(Coin)
admin.site.register(Wallet)
