from django.contrib import admin
from django.urls import path, include
from team_audit.views import audit_log_view

urlpatterns = [
    path('admin/', admin.site.urls),
    path('auth/', include('custom_auth.urls')),
    path('accounts/', include('custom_auth.urls')),
    path('mailbox/', include('team_mailbox.urls')),
    path('tasks/', include('team_tasks.urls')),
    path('audit-logs/', audit_log_view, name='audit_logs'),
    path('notifications/', include('team_notifications.urls')),
    path('chat/', include('team_chat.urls')),
    path('', include('team_core.urls')),  # Includes dashboard, search, and notifications
]