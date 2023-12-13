from django import forms

from .models import CustomUser


class SignupForm(forms.Form):
    """Form for  validating user creation."""
    first_name = forms.CharField()
    last_name = forms.CharField()
    username = forms.CharField()
    email = forms.EmailField()
    phone_number = forms.CharField()
    password = forms.CharField()
    

class EditUserForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'email', 'username', 'phone_number']