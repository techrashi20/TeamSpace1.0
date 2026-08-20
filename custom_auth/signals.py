from django.db.models.signals import post_save
from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.conf import settings
from .models import UserProfile

@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        # UserProfile create karke default EMPLOYEE role force karein
        profile, _ = UserProfile.objects.get_or_create(user=instance)
        profile.role = 'EMPLOYEE'
        profile.save()
    else:
        if hasattr(instance, 'profile'):
            instance.profile.save()
            
# Send notification email to Superusers when Client or Customer logs in
@receiver(user_logged_in)
def notify_superuser_on_client_customer_login(sender, request, user, **kwargs):
    profile = getattr(user, 'profile', None)
    
    # Trigger alert only for Client or Customer logins
    if profile and profile.role in ['CLIENT', 'CUSTOMER']:
        superusers = User.objects.filter(is_superuser=True, email__isnull=False).values_list('email', flat=True)
        
        if superusers:
            subject = f"🚨 Login Alert: {profile.get_role_display()} logged in"
            message = (
                f"Hello Admin,\n\n"
                f"A {profile.get_role_display()} has just logged into the portal.\n\n"
                f"User Details:\n"
                f"- Username: {user.username}\n"
                f"- Email: {user.email}\n"
                f"- Role: {profile.get_role_display()}\n\n"
                f"Please log in to review or reach out if required."
            )
            
            try:
                send_mail(
                    subject=subject,
                    message=message,
                    from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@system.com'),
                    recipient_list=list(superusers),
                    fail_silently=True,
                )
            except Exception as e:
                print(f"Failed to send email alert to superuser: {e}")