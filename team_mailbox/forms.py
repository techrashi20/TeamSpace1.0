from django import forms
from django.contrib.auth.models import User
from .models import Message

class MessageForm(forms.ModelForm):
    recipients = forms.ModelMultipleChoiceField(
        queryset=User.objects.all(),
        widget=forms.SelectMultiple(attrs={
            'class': 'w-full border rounded p-2 focus:ring-2 focus:ring-indigo-500'
        })
    )

    class Meta:
        model = Message
        fields = ['recipients', 'subject', 'body']
        widgets = {
            'subject': forms.TextInput(attrs={'class': 'w-full border rounded p-2 focus:ring-2 focus:ring-indigo-500'}),
            'body': forms.Textarea(attrs={'class': 'w-full border rounded p-2 h-32 focus:ring-2 focus:ring-indigo-500'}),
        }

class ReplyForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ['body']
        widgets = {
            'body': forms.Textarea(attrs={'class': 'w-full border rounded p-2 h-24 focus:ring-2 focus:ring-indigo-500', 'placeholder': 'Write your reply...'}),
        }