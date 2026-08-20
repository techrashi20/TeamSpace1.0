from django.db import models
from django.contrib.auth.models import User
from django.utils.crypto import get_random_string

class UserProfile(models.Model):
    ROLE_CHOICES = (
        ('ADMIN', 'Admin'),
        ('EMPLOYEE', 'Employee'),
        ('CLIENT', 'Client'),
        ('CUSTOMER', 'Customer'),
    )

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='EMPLOYEE')
    
    # Verification and Authentication
    is_email_verified = models.BooleanField(default=False)
    verification_otp = models.CharField(max_length=6, blank=True, null=True)
    otp_created_at = models.DateTimeField(blank=True, null=True)

    def generate_otp(self):
        otp = get_random_string(length=6, allowed_chars='0123456789')
        self.verification_otp = otp
        self.save()
        return otp

    def __str__(self):
        return f"{self.user.username} ({self.get_role_display()})"


class ClientEmployeeAccess(models.Model):
    """
    Admin mapping to grant Employees access to communicate 
    with specific Clients or Customers.
    """
    employee = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='allowed_contacts',
        limit_choices_to={'profile__role': 'EMPLOYEE'}
    )
    external_user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='assigned_employees',
        limit_choices_to={'profile__role__in': ['CLIENT', 'CUSTOMER']}
    )
    granted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('employee', 'external_user')
        verbose_name = "Client/Customer Access Permission"
        verbose_name_plural = "Client/Customer Access Permissions"

    def __str__(self):
        return f"Access: {self.employee.username} <---> {self.external_user.username}"