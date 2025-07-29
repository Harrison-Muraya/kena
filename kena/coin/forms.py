from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import CustomUser

class CreateNewlist(forms.Form):
    name = forms.CharField(label='Name', max_length=200)
    check_box = forms.BooleanField(required=False, label='Check this box if you want to add a new list')
    # Add any additional fields as needed

# This form is used for user registration
# It extends UserCreationForm to include fields for username, email, and password
class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'password1', 'password2')

WALLET_CHOICES = [
    ('personal', 'Personal Wallet'),
    ('business', 'Business Wallet'),
    ('miner', 'Miner Wallet'),
]

class WalletForm(forms.Form):
    name = forms.CharField(label="Wallet Name", max_length=100, widget=forms.TextInput(attrs={
        'placeholder': 'Enter your wallet name',
        'required': True,
        'id': 'walletName'
    }))
    password = forms.CharField(label="Create Password", widget=forms.PasswordInput(attrs={
        'placeholder': 'Create a secure password',
        'required': True,
        'id': 'password'
    }))
    confirmPassword = forms.CharField(label="Confirm Password", widget=forms.PasswordInput(attrs={
        'placeholder': 'Confirm your password',
        'required': True,
        'id': 'confirmPassword'
    }))
    walletType = forms.ChoiceField(label="Wallet Type", choices=WALLET_CHOICES, widget=forms.Select(attrs={
        'required': True,
        'id': 'walletType'
    }))

class SendKenaForm(forms.Form):
    name = forms.CharField(label="Username", max_length=100, widget=forms.TextInput(attrs={
        'placeholder': 'Enter your Username',
        'required': True,
        'id': 'username'
    }))
    password = forms.CharField(label="Create Password", widget=forms.PasswordInput(attrs={
        'placeholder': 'Create a secure password',
        'required': True,
        'id': 'password'
    }))
    confirmPassword = forms.CharField(label="Confirm Password", widget=forms.PasswordInput(attrs={
        'placeholder': 'Confirm your password',
        'required': True,
        'id': 'confirmPassword'
    }))
    walletType = forms.ChoiceField(label="Wallet Type", choices=WALLET_CHOICES, widget=forms.Select(attrs={
        'required': True,
        'id': 'walletType'
    }))

# class createWallet(forms.Form):
#     name = forms.CharField(label='Wallet Name', max_length=200)
#     coin = forms.CharField(label='Coin', max_length=200)
#     Wallettype = forms.ChoiceField(
#             choices=[   
#                 ('personal', 'Personal Wallet'),
#                 ('business', 'Business Wallet'),
#                 ('miner', 'Miner Wallet')
#             ],
#             label='Wallet Type',
#             initial='personal'
#         )
#     password = forms.CharField(widget=forms.PasswordInput, label='Password')

   