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

