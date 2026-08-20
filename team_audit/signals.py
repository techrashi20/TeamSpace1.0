from django.db.models.signals import post_save
from django.dispatch import receiver
from team_mailbox.models import Message
from team_tasks.models import Task
from .models import AuditLog

@receiver(post_save, sender=Message)
def log_message_activity(sender, instance, created, **kwargs):
    if created:
        AuditLog.objects.create(
            user=instance.sender,
            action="MESSAGE_SENT",
            details=f"Subject: {instance.subject}"
        )

@receiver(post_save, sender=Task)
def log_task_activity(sender, instance, created, **kwargs):
    if created:
        AuditLog.objects.create(
            user=instance.created_by,
            action="TASK_CREATED",
            details=f"Task: {instance.title} (Assigned to {instance.assigned_to.username})"
        )
    else:
        AuditLog.objects.create(
            user=instance.created_by,
            action="TASK_UPDATED",
            details=f"Task '{instance.title}' status changed to {instance.status}"
        )