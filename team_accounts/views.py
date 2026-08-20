from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from .forms import CustomLoginForm, RegisterForm
from .models import PasswordResetCode
from team_mailbox.models import Message

def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = CustomLoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            
            if not request.POST.get('remember_me'):
                request.session.set_expiry(0)
            else:
                request.session.set_expiry(1209600)
                
            messages.success(request, f"Welcome back, {user.username}!")
            return redirect('dashboard')
        else:
            messages.error(request, "Invalid username or password.")
    else:
        form = CustomLoginForm()

    return render(request, 'team_accounts/login.html', {'form': form})

def register_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            messages.success(request, "Account created successfully! Please login.")
            return redirect('login')
    else:
        form = RegisterForm()
    return render(request, 'team_accounts/register.html', {'form': form})

def forgot_password_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        try:
            user = User.objects.get(username=username)
            reset_obj = PasswordResetCode.generate_code(user)
            
            superusers = User.objects.filter(is_superuser=True)
            if superusers.exists():
                msg = Message.objects.create(
                    sender=user,
                    subject=f"Password Reset Code for {user.username}",
                    body=f"User '{user.username}' has requested a password reset.\nVerification Code: {reset_obj.code}"
                )
                msg.recipients.set(superusers)

            request.session['reset_user_id'] = user.id
            messages.info(request, "Verification code generated and sent to Superuser/Admin!")
            return redirect('verify_code')
        except User.DoesNotExist:
            messages.error(request, "Username not found.")
            
    return render(request, 'team_accounts/forgot_password.html')

def verify_code_view(request):
    user_id = request.session.get('reset_user_id')
    if not user_id:
        return redirect('forgot_password')

    if request.method == 'POST':
        code = request.POST.get('code')
        new_password = request.POST.get('new_password')
        
        user = get_object_or_404(User, id=user_id)
        reset_obj = PasswordResetCode.objects.filter(user=user, code=code).last()
        
        if reset_obj:
            user.set_password(new_password)
            user.save()
            reset_obj.delete()
            messages.success(request, "Password reset successful! You can now login.")
            return redirect('login')
        else:
            messages.error(request, "Invalid Verification Code.")

    return render(request, 'team_accounts/verify_code.html')

@login_required
def change_password_view(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, 'Your password was successfully updated!')
            return redirect('dashboard')
        else:
            messages.error(request, 'Please correct the error below.')
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'team_accounts/change_password.html', {'form': form})