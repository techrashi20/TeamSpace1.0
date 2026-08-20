from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.models import User
from django.db.models import Q

class RoleBasedAuthBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        if not username:
            return None

        try:
            # Check if input matches username or email
            user = User.objects.get(Q(username=username) | Q(email=username))
            
            # Fetch profile if exists
            profile = getattr(user, 'profile', None)

            # Case 1: Superuser bypasses role checks
            if user.is_superuser:
                if user.check_password(password):
                    return user
                return None

            # Case 2: Employee Login (Requires matching username explicitly)
            if profile and profile.role == 'EMPLOYEE':
                if user.username == username and user.check_password(password):
                    return user
                return None

            # Case 3: Client / Customer Login (Requires email input)
            if profile and profile.role in ['CLIENT', 'CUSTOMER']:
                if user.email == username and user.check_password(password):
                    return user
                return None

        except User.DoesNotExist:
            return None

        return None