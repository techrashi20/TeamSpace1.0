from django.db import models
from django.contrib.auth.models import User

class Message(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    recipients = models.ManyToManyField(User, related_name='received_messages', blank=True)
    subject = models.CharField(max_length=255, blank=True)
    body = models.TextField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    is_draft = models.BooleanField(default=False)
    parent = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='replies')
    deleted_by = models.ManyToManyField(User, related_name='deleted_messages', blank=True)
    archived_by = models.ManyToManyField(User, related_name='archived_messages', blank=True)

    def __str__(self):
        return f"{self.sender.username} - {self.subject or 'No Subject'}"


class Attachment(models.Model):
    message = models.ForeignKey(Message, on_delete=models.CASCADE, related_name='attachments')
    file = models.FileField(upload_to='mail_attachments/%Y/%m/%d/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def filename(self):
        return self.file.name.split('/')[-1]