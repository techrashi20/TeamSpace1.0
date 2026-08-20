from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.conf import settings
from .models import UserProfile

def login_view(request):
    if request.user.is_authenticated:
        return redirect('inbox')

    if request.method == 'POST':
        selected_role = request.POST.get('role')  # EMPLOYEE, CLIENT, or CUSTOMER
        user_input = request.POST.get('identifier', '').strip()  # Username or Email
        password = request.POST.get('password', '')

        if not selected_role:
            messages.error(request, "Please select your Role before logging in.")
            return render(request, 'custom_auth/login.html')

        user = authenticate(request, username=user_input, password=password)

        if user is not None:
            profile = getattr(user, 'profile', None)

            # Verification: User's actual role must match the selected role (Superusers bypass)
            if not user.is_superuser and profile and profile.role != selected_role:
                messages.error(request, f"Role mismatch! You are registered as {profile.get_role_display()}, not {selected_role.capitalize()}.")
                return render(request, 'custom_auth/login.html')

            # OTP verification for Clients and Customers
            if profile and profile.role in ['CLIENT', 'CUSTOMER'] and not profile.is_email_verified:
                otp = profile.generate_otp()
                send_mail(
                    subject="Email Verification Code",
                    message=f"Your verification code is: {otp}",
                    from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@system.com'),
                    recipient_list=[user.email],
                    fail_silently=True
                )
                request.session['unverified_user_id'] = user.id
                messages.info(request, "Please verify your email using the OTP sent to your mailbox.")
                return redirect('verify_otp')

            login(request, user)
            messages.success(request, f"Welcome back, {user.username}!")
            return redirect('inbox')
        else:
            messages.error(request, "Invalid credentials. Please check your inputs.")

    return render(request, 'custom_auth/login.html')

def verify_otp_view(request):
    user_id = request.session.get('unverified_user_id')
    if not user_id:
        return redirect('login')

    if request.method == 'POST':
        otp_entered = request.POST.get('otp', '').strip()
        try:
            user = User.objects.get(id=user_id)
            profile = user.profile

            if profile.verification_otp == otp_entered:
                profile.is_email_verified = True
                profile.verification_otp = None
                profile.save()

                del request.session['unverified_user_id']
                login(request, user)
                messages.success(request, "Email verified successfully! You are now logged in.")
                return redirect('inbox')
            else:
                messages.error(request, "Invalid verification code.")
        except User.DoesNotExist:
            return redirect('login')

    return render(request, 'custom_auth/verify_otp.html')


def register_view(request):
    if request.method == 'POST':
        role = request.POST.get('role')  # CLIENT or CUSTOMER
        email = request.POST.get('email', '').strip()
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password')

        if User.objects.filter(email=email).exists():
            messages.error(request, "Email is already registered.")
            return render(request, 'custom_auth/register.html')

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username is already taken.")
            return render(request, 'custom_auth/register.html')

        # Role validation safeguard
        if role not in ['CLIENT', 'CUSTOMER']:
            messages.error(request, "Please select a valid role (Client or Customer).")
            return render(request, 'custom_auth/register.html')

        # Create user instance
        user = User.objects.create_user(username=username, email=email, password=password)
        
        # Profile updated with selected role
        profile = user.profile
        profile.role = role
        profile.save()

        # Send OTP
        otp = profile.generate_otp()
        send_mail(
            subject="Verification Code for Registration",
            message=f"Welcome! Your verification code is: {otp}",
            from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@system.com'),
            recipient_list=[email],
            fail_silently=True
        )

        request.session['unverified_user_id'] = user.id
        messages.success(request, "Account created! Check your email for the verification code.")
        return redirect('verify_otp')

    return render(request, 'custom_auth/register.html')

def logout_view(request):
    logout(request)
    messages.info(request, "Logged out successfully.")
    return redirect('login')