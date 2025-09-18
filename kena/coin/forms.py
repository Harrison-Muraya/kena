from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser, Wallet, UserProfile
from django.core.exceptions import ValidationError
import re

class CreateNewlist(forms.Form):
    name = forms.CharField(label='Name', max_length=200)
    check_box = forms.BooleanField(required=False, label='Check this box if you want to add a new list')
    # Add any additional fields as needed

class RegisterForm(UserCreationForm):
    first_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'w-full p-4 bg-white/5 border border-white/10 rounded-xl text-white placeholder-gray-400 focus:border-kena-gold focus:ring-2 focus:ring-kena-gold/50 focus:outline-none transition-all',
            'placeholder': 'Harrison'
        })
    )    
    last_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'w-full p-4 bg-white/5 border border-white/10 rounded-xl text-white placeholder-gray-400 focus:border-kena-gold focus:ring-2 focus:ring-kena-gold/50 focus:outline-none transition-all',
            'placeholder': 'Doe'
        })
    )    
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'w-full p-4 bg-white/5 border border-white/10 rounded-xl text-white placeholder-gray-400 focus:border-kena-gold focus:ring-2 focus:ring-kena-gold/50 focus:outline-none transition-all',
            'placeholder': 'john@example.com'
        })
    )    
    phone = forms.CharField(
        max_length=15,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'w-full p-4 pl-20 bg-white/5 border border-white/10 rounded-xl text-white placeholder-gray-400 focus:border-kena-gold focus:ring-2 focus:ring-kena-gold/50 focus:outline-none transition-all',
            'placeholder': '712345678'
        })
    )    
    country_code = forms.CharField(
        max_length=5,
        initial='+254',
        widget=forms.Select(
            choices=[
                ('+254', '🇰🇪 +254'),
                ('+1', '🇺🇸 +1'),
                ('+44', '🇬🇧 +44'),
                ('+91', '🇮🇳 +91'),
                ('+86', '🇨🇳 +86'),
            ],
            attrs={
                'id': 'countryCode',
                'class': 'absolute left-0 top-0 h-full bg-white/5 border border-white/10 rounded-l-xl text-white text-sm px-3 focus:outline-none'
            }
        )
    )    
    terms_accepted = forms.BooleanField(
        required=True,
        error_messages={'required': 'You must agree to the Terms of Service and Privacy Policy'},
        widget=forms.CheckboxInput(attrs={
            'class': 'w-4 h-4 mt-1 text-kena-gold bg-white/10 border-white/20 rounded focus:ring-kena-gold focus:ring-2'
        })
    )    
    marketing_consent = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'w-4 h-4 mt-1 text-kena-gold bg-white/10 border-white/20 rounded focus:ring-kena-gold focus:ring-2'
        })
    )
    password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'w-full p-4 bg-white/5 border border-white/10 rounded-xl text-white placeholder-gray-400 focus:border-kena-gold focus:ring-2 focus:ring-kena-gold/50 focus:outline-none transition-all pr-12',
            'placeholder': 'Create a strong password'
        })
    )    
    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'w-full p-4 bg-white/5 border border-white/10 rounded-xl text-white placeholder-gray-400 focus:border-kena-gold focus:ring-2 focus:ring-kena-gold/50 focus:outline-none transition-all pr-12',
            'placeholder': 'Confirm your password'
        })
    )

    class Meta:
        model = CustomUser
        fields = ('first_name', 'last_name', 'email', 'password1', 'password2')

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if CustomUser.objects.filter(email=email).exists():
            raise ValidationError("This email address is already registered.")
        return email

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        country_code = self.cleaned_data.get('country_code', '+254')
        
        # Remove any non-digit characters
        phone_digits = re.sub(r'\D', '', phone)
        
        # Validate phone number format based on country code
        if country_code == '+254':  # Kenya
            if not re.match(r'^[17]\d{8}$', phone_digits):
                raise ValidationError("Please enter a valid Kenyan phone number (e.g., 712345678)")
        elif country_code == '+1':  # US
            if not re.match(r'^\d{10}$', phone_digits):
                raise ValidationError("Please enter a valid US phone number (10 digits)")
        
        return phone_digits

    def clean_password1(self):
        password1 = self.cleaned_data.get('password1')
        
        if len(password1) < 8:
            raise ValidationError("Password must be at least 8 characters long.")
        
        # Additional password strength checks
        if not re.search(r'[A-Z]', password1):
            raise ValidationError("Password must contain at least one uppercase letter.")
        
        if not re.search(r'[a-z]', password1):
            raise ValidationError("Password must contain at least one lowercase letter.")
        
        if not re.search(r'\d', password1):
            raise ValidationError("Password must contain at least one number.")
        
        return password1
    
    def _generate_unique_username(self, email):
            """Generate a unique username from email"""
            base_username = email.split('@')[0].lower()
            base_username = re.sub(r'[^a-zA-Z0-9]', '', base_username)  # Remove special chars
            
            if len(base_username) < 3:
                base_username = f"user{base_username}"
            
            username = base_username
            counter = 1
            
            while CustomUser.objects.filter(username=username).exists():
                username = f"{base_username}{counter}"
                counter += 1
                
            return username
        
    def save(self, commit=True):
        # Create the user first
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.terms_accepted = self.cleaned_data.get('terms_accepted', False)
        
        # Auto-generate username from email
        user.username = self._generate_unique_username(self.cleaned_data['email'])
        
        if commit:
            user.save()
            # Create user profile after user is saved
            UserProfile.objects.create(
                user=user,
                phone=f"{self.cleaned_data['country_code']}{self.cleaned_data['phone']}",
                marketing_consent=self.cleaned_data.get('marketing_consent', False)
            )
            # You can also create a default wallet here if needed
            Wallet.objects.create(
                user=user, 
                name="Default Wallet", 
                wallet_type="primary",
                password=self.cleaned_data['password']
            )

        
        return user


WALLET_CHOICES = [
    ('primary', 'Primary Wallet'),
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
    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        if user:
            self.fields['wallet'].queryset = Wallet.objects.filter(user=user)

    wallet = forms.ModelChoiceField(
        queryset=Wallet.objects.none(),  # Placeholder
        empty_label="Select your wallet",
        label="Wallet",
        widget=forms.Select(attrs={
            'required': True,
            'id': 'walletName'
        })
    )
    receiver = forms.CharField(label="Receiver Username", max_length=100, widget=forms.TextInput(attrs={
        'placeholder': 'Enter your recepient Username',
        'required': True,
        'id': 'receiverUsername'
    }))
    amount = forms.DecimalField(label="Amount", max_digits=20, decimal_places=8, widget=forms.NumberInput(attrs={
        'placeholder': 'Enter the amount to send',
        'required': True,
        'id': 'amount'
    }))
    password = forms.CharField(label="Password", widget=forms.PasswordInput(attrs={
        'placeholder': 'Enter your password',
        'required': True,
        'id': 'password'
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

   