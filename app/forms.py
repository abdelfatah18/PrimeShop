from django import forms
from .models import ContactMessage 

class ContactForm(forms.ModelForm):
    class Meta:
        model = ContactMessage
        fields = ['name', 'email', 'subject', 'message']
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'First Name'}),
            'subject': forms.TextInput(attrs={'placeholder': 'Subject'}),
            'email': forms.EmailInput(attrs={'placeholder': 'Email Address '}),
            'message': forms.Textarea(attrs={'placeholder': 'Write message...'}),
        }
        
        
# forms.py
from django import forms
from accounts.models import User
from django.contrib.auth.forms import PasswordChangeForm

class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'profile_photo']




# forms.py
from django import forms

class EmailPreferencesForm(forms.Form):
    order_updates = forms.BooleanField(
        required=False,
        label="Order Updates",
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    promotions = forms.BooleanField(
        required=False,
        label="Promotions",
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    newsletter = forms.BooleanField(
        required=False,
        label="Newsletter",
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
