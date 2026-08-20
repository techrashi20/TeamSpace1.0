# team_mailbox/context_processors.py
from .models import Message

def unread_counts(request):
    if request.user.is_authenticated:
        # Unread Mails Count
        unread_inbox = Message.objects.filter(
            recipients=request.user,
            is_read=False,
            is_draft=False
        ).exclude(
            deleted_by=request.user
        ).exclude(
            archived_by=request.user
        ).count()

        # Unread Tasks Count (agar Task model active hai, otherwise placeholder 0)
        # unread_tasks = Task.objects.filter(assigned_to=request.user, is_completed=False).count()
        unread_tasks = 0 

        # Unread Notifications Count
        unread_notifications = 0 

        return {
            'unread_inbox_count': unread_inbox,
            'unread_tasks_count': unread_tasks,
            'unread_notifications_count': unread_notifications,
        }
    return {}