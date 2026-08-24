from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from django.db.models import Q
from .models import Message, Attachment
from custom_auth.models import ClientEmployeeAccess
from team_notifications.models import Notification  # <--- IMPORTED NOTIFICATION MODEL


def get_allowed_recipients(user):
    if user.is_superuser:
        return User.objects.exclude(id=user.id)

    profile = getattr(user, 'profile', None)
    if not profile:
        return User.objects.none()

    role = profile.role

    if role == 'EMPLOYEE':
        granted_external_ids = ClientEmployeeAccess.objects.filter(
            employee=user
        ).values_list('external_user_id', flat=True)
        
        return User.objects.filter(
            Q(is_superuser=True) | 
            Q(profile__role='EMPLOYEE') | 
            Q(id__in=granted_external_ids)
        ).exclude(id=user.id).distinct()

    elif role in ['CLIENT', 'CUSTOMER']:
        assigned_employee_ids = ClientEmployeeAccess.objects.filter(
            external_user=user
        ).values_list('employee_id', flat=True)
        
        return User.objects.filter(
            Q(is_superuser=True) | 
            Q(id__in=assigned_employee_ids)
        ).exclude(id=user.id).distinct()

    return User.objects.none()


@login_required
def inbox_view(request):
    messages_list = Message.objects.filter(
        recipients=request.user, 
        is_draft=False
    ).exclude(
        deleted_by=request.user
    ).exclude(
        archived_by=request.user
    ).order_by('-timestamp')
    
    return render(request, 'team_mailbox/inbox.html', {
        'messages': messages_list, 
        'active_tab': 'inbox'
    })


@login_required
def sent_view(request):
    messages_list = request.user.sent_messages.filter(
        parent__isnull=True,
        is_draft=False
    ).exclude(
        deleted_by=request.user
    ).order_by('-timestamp')
    
    return render(request, 'team_mailbox/inbox.html', {
        'messages': messages_list, 
        'title': 'Sent Messages', 
        'active_tab': 'sent'
    })


@login_required
def drafts_view(request):
    drafts = Message.objects.filter(
        sender=request.user, 
        is_draft=True
    ).exclude(
        deleted_by=request.user
    ).order_by('-timestamp')
    
    return render(request, 'team_mailbox/drafts.html', {
        'drafts': drafts, 
        'active_tab': 'drafts'
    })


@login_required
def archive_view(request):
    archived_mails = Message.objects.filter(
        archived_by=request.user
    ).exclude(
        deleted_by=request.user
    ).order_by('-timestamp')
    
    return render(request, 'team_mailbox/archive.html', {
        'messages': archived_mails, 
        'active_tab': 'archive'
    })


@login_required
def compose_view(request, draft_id=None):
    draft_instance = None
    if draft_id:
        draft_instance = get_object_or_404(Message, id=draft_id, sender=request.user, is_draft=True)

    if request.method == 'POST':
        action = request.POST.get('action')
        recipients_ids = request.POST.getlist('recipients')
        subject = request.POST.get('subject')
        body = request.POST.get('body')
        uploaded_files = request.FILES.getlist('attachments')

        if draft_instance:
            msg = draft_instance
            msg.subject = subject
            msg.body = body
        else:
            msg = Message(sender=request.user, subject=subject, body=body)

        if action == 'save_draft':
            msg.is_draft = True
            msg.save()
            if recipients_ids:
                msg.recipients.set(recipients_ids)
            for file in uploaded_files:
                Attachment.objects.create(message=msg, file=file)
            messages.success(request, "Mail saved as draft.")
            return redirect('drafts')
            
        elif action == 'send':
            if not recipients_ids:
                messages.error(request, "Please select at least one recipient.")
                users = get_allowed_recipients(request.user)
                return render(request, 'team_mailbox/compose.html', {
                    'users': users, 
                    'draft': draft_instance
                })

            msg.is_draft = False
            msg.save()
            msg.recipients.set(recipients_ids)
            
            for file in uploaded_files:
                Attachment.objects.create(message=msg, file=file)

            # <--- AUTOMATICALLY CREATE NOTIFICATIONS FOR RECIPIENTS --->
            for recipient in msg.recipients.all():
                Notification.objects.create(
                    user=recipient,
                    title=f"New Mail from {request.user.username}",
                    message=subject if subject else "No Subject",
                    url=f"/mailbox/inbox/",
                    is_read=False
                )

            messages.success(request, "Mail sent successfully!")
            return redirect('inbox')

    users = get_allowed_recipients(request.user)
    return render(request, 'team_mailbox/compose.html', {
        'users': users, 
        'draft': draft_instance
    })


@login_required
def mail_detail_view(request, pk):
    message = get_object_or_404(Message, pk=pk)
    
    if request.user != message.sender and request.user not in message.recipients.all():
        messages.error(request, "You do not have permission to view this message.")
        return redirect('inbox')

    if request.user in message.recipients.all() and not message.is_read:
        message.is_read = True
        message.save()

    if request.method == 'POST':
        reply_body = request.POST.get('body')
        reply_files = request.FILES.getlist('attachments')
        if reply_body:
            reply_msg = Message.objects.create(
                sender=request.user,
                subject=f"Re: {message.subject}",
                body=reply_body,
                parent=message
            )
            recipients_to_notify = set(message.recipients.exclude(id=request.user.id))
            if message.sender != request.user:
                recipients_to_notify.add(message.sender)

            reply_msg.recipients.set(recipients_to_notify)
            
            for file in reply_files:
                Attachment.objects.create(message=reply_msg, file=file)
            
            # Create a notification for each recipient of the reply
            for recipient in recipients_to_notify:
                Notification.objects.create(
                    user=recipient,
                    title=f"New Reply from {request.user.username}",
                    message=f"Re: {message.subject}",
                    url=f"/mailbox/mail/{message.pk}/",
                    is_read=False
                )

            messages.success(request, "Reply sent successfully!")
            return redirect('message_detail', pk=pk)
            
    replies = message.replies.all().order_by('timestamp')
    return render(request, 'team_mailbox/detail.html', {
        'message': message, 
        'replies': replies
    })


@login_required
def toggle_archive_view(request, pk):
    msg = get_object_or_404(Message, pk=pk)
    if request.user in msg.archived_by.all():
        msg.archived_by.remove(request.user)
        messages.success(request, "Mail unarchived.")
    else:
        msg.archived_by.add(request.user)
        messages.success(request, "Mail archived.")
    return redirect('inbox')


@login_required
def delete_message_view(request, pk):
    message = get_object_or_404(Message, pk=pk)
    message.deleted_by.add(request.user)
    messages.success(request, "Message deleted.")
    return redirect('inbox')
