from models import Billing, Transaction, Wallet
from django.db import models


def get_balance(walletHash, user_id):
    """
    Get the balance by calculating credited amount.

    Args:
        user_id (int): The ID of the user.

    Returns:
        float: The balance of the user's wallet.
    """
    try:
        wallet = Wallet.objects.get(hash=walletHash, user_id=user_id)
        credited_amount = (
            Transaction.objects.filter(
                type='credit'
            ).aggregate(total_amount=models.Sum('amount'))['total_amount'] or 0.0
        )
        debited_amount = (
            Transaction.objects.filter(
                wallet_id=wallet.id,
                type='debit'
            ).aggregate(total_amount=models.Sum('amount'))['total_amount'] or 0.0
        )
        balance = credited_amount - debited_amount
        return balance
    except Exception as e:
        print(f"Error getting balance for user {user_id}: {e}")
        return 0.0
