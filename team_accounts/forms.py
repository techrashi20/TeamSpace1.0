from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm

class CustomLoginForm(AuthenticationForm):
    remember_me = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={'class': 'rounded border-gray-300 text-indigo-600 focus:ring-indigo-500'}))

class RegisterForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'w-full border rounded p-2 focus:ring-2 focus:ring-indigo-500'}))
    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'w-full border rounded p-2 focus:ring-2 focus:ring-indigo-500'}))

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'w-full border rounded p-2 focus:ring-2 focus:ring-indigo-500'}),
            'email': forms.EmailInput(attrs={'class': 'w-full border rounded p-2 focus:ring-2 focus:ring-indigo-500'}),
            'first_name': forms.TextInput(attrs={'class': 'w-full border rounded p-2 focus:ring-2 focus:ring-indigo-500'}),
            'last_name': forms.TextInput(attrs={'class': 'w-full border rounded p-2 focus:ring-2 focus:ring-indigo-500'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password != confirm_password:
            raise forms.ValidationError("Passwords do not match!")
        return cleaned_data