from django.shortcuts import render
from django.contrib.auth.decorators import login_required, user_passes_test
from .models import AuditLog

@login_required
@user_passes_test(lambda u: u.is_staff)
def audit_log_view(request):
    logs = AuditLog.objects.all().order_by('-timestamp')[:50]
    return render(request, 'team_audit/audit_logs.html', {'logs': logs})