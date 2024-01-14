from django import forms
from .models import CustomUser
from django.contrib.auth.hashers import make_password


class SignupForm(forms.ModelForm):         
            
    class Meta:
        model=CustomUser
        fields=['first_name','last_name','username','email','password','address','phone_number','role']
    # def clean_password(self):
    #     password=make_password(self.cleaned_data['password'])
    #     return password
   
class EditUserForm(forms.Form):
    first_name=forms.CharField()
    last_name=forms.CharField()
    username=forms.CharField()
    email=forms.EmailField()
    phone_number=forms.CharField()
    address=forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)