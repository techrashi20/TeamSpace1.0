from django.contrib import admin
from .models import UserProfile, ClientEmployeeAccess
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import UserProfile

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'role', 'is_email_verified')
    list_filter = ('role', 'is_email_verified')
    search_fields = ('user__username', 'user__email')


@admin.register(ClientEmployeeAccess)
class ClientEmployeeAccessAdmin(admin.ModelAdmin):
    list_display = ('employee', 'external_user', 'granted_at')
    search_fields = ('employee__username', 'external_user__username', 'external_user__email')

class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Profile'

class CustomUserAdmin(BaseUserAdmin):
    inlines = (UserProfileInline,)

# Re-register User Admin
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)