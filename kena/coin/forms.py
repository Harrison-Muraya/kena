from django import forms

class CreateNewlist(forms.Form):
    name = forms.CharField(label='Name', max_length=200)
    check_box = forms.BooleanField(required=False, label='Check this box if you want to add a new list')
    # Add any additional fields as needed