from django.db.models.signals import post_delete
from django.dispatch import receiver
from django.db.models import Sum
from .models import Transaction

@receiver(post_delete, sender=Transaction)
def update_wallet_balance_on_delete(sender, instance, **kwargs):
    """Update wallet balance when a transaction is deleted"""
    wallet = instance.wallet
    
    if not wallet:
        return
    
    # Calculate total credits (use 'credit' field, not 'amount')
    credited = (
        Transaction.objects.filter(wallet=wallet, type='receive')
        .aggregate(total=Sum('credit'))['total'] or 0
    )
    
    # Calculate total debits (use 'debit' field, not 'amount')
    debited = (
        Transaction.objects.filter(wallet=wallet, type='send')
        .aggregate(total=Sum('debit'))['total'] or 0
    )
    
    # Calculate fees
    fees = (
        Transaction.objects.filter(wallet=wallet, type='fee')
        .aggregate(total=Sum('debit'))['total'] or 0
    )
    
    # Update balance
    wallet.amount = credited - debited - fees
    wallet.save(update_fields=['amount'])