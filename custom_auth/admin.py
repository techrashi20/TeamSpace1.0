from django.contrib import admin
from .models import UserProfile, ClientEmployeeAccess

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'role', 'is_email_verified')
    list_filter = ('role', 'is_email_verified')
    search_fields = ('user__username', 'user__email')


@admin.register(ClientEmployeeAccess)
class ClientEmployeeAccessAdmin(admin.ModelAdmin):
    list_display = ('employee', 'external_user', 'granted_at')
    search_fields = ('employee__username', 'external_user__username', 'external_user__email')