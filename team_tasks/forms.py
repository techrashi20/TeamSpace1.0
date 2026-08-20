from django import forms
from .models import Task, TaskComment

class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['title', 'description', 'assigned_to', 'priority', 'status', 'due_date']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'w-full border rounded p-2 focus:ring-2 focus:ring-indigo-500'}),
            'description': forms.Textarea(attrs={'class': 'w-full border rounded p-2 h-28 focus:ring-2 focus:ring-indigo-500'}),
            'assigned_to': forms.Select(attrs={'class': 'w-full border rounded p-2 focus:ring-2 focus:ring-indigo-500'}),
            'priority': forms.Select(attrs={'class': 'w-full border rounded p-2 focus:ring-2 focus:ring-indigo-500'}),
            'status': forms.Select(attrs={'class': 'w-full border rounded p-2 focus:ring-2 focus:ring-indigo-500'}),
            'due_date': forms.DateInput(attrs={'type': 'date', 'class': 'w-full border rounded p-2 focus:ring-2 focus:ring-indigo-500'}),
        }

class TaskCommentForm(forms.ModelForm):
    class Meta:
        model = TaskComment
        fields = ['comment']
        widgets = {
            'comment': forms.Textarea(attrs={'class': 'w-full border rounded p-2 h-20 focus:ring-2 focus:ring-indigo-500', 'placeholder': 'Add a comment...'}),
        }