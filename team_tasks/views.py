from django.db import models
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.contrib import messages
from django.contrib.auth.models import User
from .models import Task, TaskAttachment
from team_mailbox.models import Message
import json

@login_required
def task_board_view(request):
    user_tasks = Task.objects.filter(
        models.Q(created_by=request.user) | models.Q(assigned_to=request.user)
    ).distinct().order_by('-updated_at')

    todo_tasks = user_tasks.filter(status='TODO')
    in_progress_tasks = user_tasks.filter(status='IN_PROGRESS')
    completed_tasks = user_tasks.filter(status='COMPLETED')

    all_users = User.objects.exclude(id=request.user.id)

    return render(request, 'team_tasks/board.html', {
        'todo_tasks': todo_tasks,
        'in_progress_tasks': in_progress_tasks,
        'completed_tasks': completed_tasks,
        'all_users': all_users,
        'active_tab': 'tasks'
    })


@login_required
def task_list_view(request):
    """List view for tasks if you want a tabular format option"""
    tasks = Task.objects.filter(
        models.Q(created_by=request.user) | models.Q(assigned_to=request.user)
    ).distinct().order_by('-updated_at')

    return render(request, 'team_tasks/list.html', {
        'tasks': tasks,
        'active_tab': 'tasks'
    })


@login_required
def task_detail_view(request, pk):
    task = get_object_or_404(Task, pk=pk)
    
    # Check permission
    if request.user != task.created_by and request.user not in task.assigned_to.all() and not request.user.is_superuser:
        messages.error(request, "You do not have permission to view this task.")
        return redirect('task_board')

    if request.method == 'POST':
        # Handle updates or comments/attachments addition from detail page if needed
        title = request.POST.get('title')
        description = request.POST.get('description')
        status = request.POST.get('status')
        priority = request.POST.get('priority')
        due_date = request.POST.get('due_date') or None
        files = request.FILES.getlist('attachments')

        if title:
            task.title = title
            task.description = description
            task.status = status
            task.priority = priority
            task.due_date = due_date
            task.save()

            for file in files:
                TaskAttachment.objects.create(task=task, file=file)

            messages.success(request, "Task updated successfully!")
            return redirect('task_detail', pk=task.pk)

    all_users = User.objects.exclude(id=request.user.id)
    return render(request, 'team_tasks/detail.html', {
        'task': task,
        'all_users': all_users,
        'active_tab': 'tasks'
    })


@login_required
def create_task_view(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        priority = request.POST.get('priority', 'MEDIUM')
        due_date = request.POST.get('due_date') or None
        assigned_user_ids = request.POST.getlist('assigned_to')
        files = request.FILES.getlist('attachments')

        task = Task.objects.create(
            title=title,
            description=description,
            priority=priority,
            due_date=due_date,
            created_by=request.user
        )

        if assigned_user_ids:
            task.assigned_to.set(assigned_user_ids)

        for file in files:
            TaskAttachment.objects.create(task=task, file=file)

        messages.success(request, "Task created successfully!")
        return redirect('task_board')

    return redirect('task_board')


@login_required
def update_task_status_api(request):
    """API endpoint for Drag-and-Drop Kanban updates"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            task_id = data.get('task_id')
            new_status = data.get('status')

            task = get_object_or_404(Task, id=task_id)
            
            if request.user == task.created_by or request.user in task.assigned_to.all() or request.user.is_superuser:
                if new_status in ['TODO', 'IN_PROGRESS', 'COMPLETED']:
                    task.status = new_status
                    task.save()
                    return JsonResponse({'status': 'success', 'new_status': new_status})
            
            return JsonResponse({'status': 'error', 'message': 'Permission denied'}, status=403)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

    return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)


@login_required
def update_task_status(request, pk):
    """Standard form-based status updater redirecting back"""
    task = get_object_or_404(Task, pk=pk)
    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status in ['TODO', 'IN_PROGRESS', 'COMPLETED']:
            task.status = new_status
            task.save()
            messages.success(request, "Task status updated.")
    return redirect('task_board')


@login_required
def convert_mail_to_task(request, mail_id):
    """Directly converts a mail message and its attachments into a Task"""
    mail = get_object_or_404(Message, pk=mail_id)
    
    # Check if user has access to the mail
    if request.user != mail.sender and request.user not in mail.recipients.all():
        messages.error(request, "Permission denied.")
        return redirect('inbox')

    # Create Task from Mail data
    task = Task.objects.create(
        title=f"Task from Mail: {mail.subject or 'No Subject'}",
        description=mail.body,
        status='TODO',
        priority='MEDIUM',
        created_by=request.user
    )
    task.assigned_to.add(request.user)

    # Copy attachments if any exist in mail
    for mail_att in mail.attachments.all():
        # Re-using the file field or copying reference for task attachment
        TaskAttachment.objects.create(task=task, file=mail_att.file)

    messages.success(request, "Mail successfully converted into a Task!")
    return redirect('task_board')

@login_required
def calendar_view(request):
    # Get all tasks for the logged-in user that have a due date
    tasks = Task.objects.filter(assigned_to=request.user, due_date__isnull=False).order_by('due_date')
    
    return render(request, 'team_tasks/calendar.html', {
        'tasks': tasks,
        'active_tab': 'calendar'
    })