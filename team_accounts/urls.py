from django.urls import path
from django.contrib.auth.views import LogoutView
from .views import login_view, register_view, forgot_password_view, verify_code_view, change_password_view

urlpatterns = [
    path('login/', login_view, name='login'),
    path('register/', register_view, name='register'),
    path('forgot-password/', forgot_password_view, name='forgot_password'),
    path('verify-code/', verify_code_view, name='verify_code'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('password-change/', change_password_view, name='change_password'),
]