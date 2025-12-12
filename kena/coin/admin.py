from django.contrib import admin
from .models import CustomUser, Todolist, Item, Coin, Wallet, Billing, Transaction, Block, PendingTransaction, UserProfile, MpesaTransaction, PaypalTransaction, RejectedTransaction

# Register your models here.
admin.site.register(CustomUser)
admin.site.register(Todolist)
admin.site.register(Item)
admin.site.register(Coin)
admin.site.register(Wallet)
admin.site.register(Billing) 
admin.site.register(Transaction)
admin.site.register(Block)
admin.site.register(PendingTransaction)
admin.site.register(UserProfile)
admin.site.register(MpesaTransaction)
admin.site.register(PaypalTransaction)
admin.site.register(RejectedTransaction)
