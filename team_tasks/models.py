from django.db import models
from django.contrib.auth.models import User
from team_mailbox.models import Message
from django.db.models.signals import post_save
from django.dispatch import receiver
from team_core.models import Notification


STATUS_CHOICES = (
    ('TODO', 'To Do'),
    ('IN_PROGRESS', 'In Progress'),
    ('COMPLETED', 'Completed'),
)

PRIORITY_CHOICES = (
    ('LOW', 'Low'),
    ('MEDIUM', 'Medium'),
    ('HIGH', 'High'),
)

class Task(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='TODO')
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='MEDIUM')
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_tasks')
    assigned_to = models.ManyToManyField(User, related_name='assigned_tasks', blank=True)
    due_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title} [{self.get_status_display()}]"


class TaskAttachment(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='attachments')
    file = models.FileField(upload_to='task_attachments/%Y/%m/%d/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def filename(self):
        return self.file.name.split('/')[-1]

class TaskComment(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comment by {self.author.username} on {self.task.title}"


@receiver(post_save, sender=Task)
def notify_on_task_creation(sender, instance, created, **kwargs):
    if created and instance.assigned_to != instance.created_by:
        Notification.objects.create(
            user=instance.assigned_to,
            title="New Task Assigned",
            message=f"You have been assigned: {instance.title}",
            link=f"/tasks/{instance.pk}/"
        )