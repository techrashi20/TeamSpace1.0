import random
from django.db import models
from django.contrib.auth.models import User

class PasswordResetCode(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)

    @classmethod
    def generate_code(cls, user):
        code = str(random.randint(100000, 999999))
        return cls.objects.create(user=user, code=code)