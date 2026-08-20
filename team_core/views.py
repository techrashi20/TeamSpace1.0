from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from team_mailbox.models import Message
from team_tasks.models import Task
from .models import Notification
from django.db.models import Count

@login_required
def dashboard_view(request):
    # Tasks Analytics for the logged-in user
    user_tasks = Task.objects.filter(assigned_to=request.user)
    task_stats = user_tasks.values('status').annotate(total=Count('status'))
    
    # Unread Mails count
    unread_mails = Message.objects.filter(recipients=request.user, is_read=False).count()
    
    # Recent Notifications
    recent_notifs = request.user.team_notifications_set.filter(is_read=False)[:5]

    return render(request, 'team_core/dashboard.html', {
        'task_stats': list(task_stats),
        'unread_mails': unread_mails,
        'recent_notifs': recent_notifs,
        'active_tab': 'dashboard'
    })


# Context processor for global unread notifications
def notifications_processor(request):
    if request.user.is_authenticated:
        unread_notifications = Notification.objects.filter(user=request.user, is_read=False).order_by('-created_at')
        return {
            'unread_notifications': unread_notifications,
            'has_new_notifications': unread_notifications.exists()
        }
    return {'unread_notifications': [], 'has_new_notifications': False}

@login_required
def global_search_view(request):
    query = request.GET.get('q', '')
    tasks = []
    messages = []
    
    if query:
        tasks = Task.objects.filter(
            Q(title__icontains=query) | Q(description__icontains=query),
            Q(assigned_to=request.user) | Q(created_by=request.user)
        ).distinct()

        messages = Message.objects.filter(
            Q(subject__icontains=query) | Q(body__icontains=query),
            Q(recipients=request.user) | Q(sender=request.user)
        ).distinct()

    return render(request, 'team_core/search_results.html', {
        'query': query,
        'tasks': tasks,
        'messages': messages
    })

@login_required
def mark_notifications_read(request):
    Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
    return render(request, 'team_core/notifications.html')