from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User

class CustomUserAdmin(BaseUserAdmin):
    def get_changeform_initial_data(self, request):
        initial = super().get_changeform_initial_data(request)
        # Check 'Staff status' by default when adding a new user in admin
        initial['is_staff'] = True
        return initial

# Re-register UserAdmin
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)