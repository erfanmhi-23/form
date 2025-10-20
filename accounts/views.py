from django.shortcuts import render , redirect
from accounts.forms import EmailForm , SignupForm , UserForm , DeleteAccountForm
from accounts.models import EmailOTP
from django.core.mail import send_mail
from django.contrib import messages
from django.http import HttpResponse
from django.contrib.auth import get_user_model, login , logout , update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm

def send_email_otp(request):
    if request.method == "POST":
        form = EmailForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data["email"]
            otp_code = EmailOTP.generate_otp()
            EmailOTP.objects.create(email=email, code=otp_code)
            send_mail(
                "کد ورود شما",
                f"کد ورود شما: {otp_code}",
                "noreply@example.com",
                [email],
                fail_silently=False,
            )
            request.session["email"] = email
            messages.success(request, "کد OTP به ایمیل شما ارسال شد.")
            return redirect("verify_email_otp")
    else:
        form = EmailForm()
    return render(request, "user/email_form.html", {"form": form})

def verify_email_otp(request):
    if request.method == "POST":
        code = request.POST.get("code")
        email = request.session.get("email")
        try:
            otp = EmailOTP.objects.filter(email=email, code=code, is_used=False).latest("created_at")
        except EmailOTP.DoesNotExist:
            messages.error(request, "کد اشتباه است یا پیدا نشد.")
            return redirect("verify_email_otp")
        if otp.is_expired():
            messages.error(request, "کد منقضی شده است.")
            return redirect("send_email_otp")
        otp.is_used = True
        otp.save()
        user = get_user_model().objects.get_or_create(username=email, defaults={"email": email})
        login(request, user)
        messages.success(request, "ورود موفقیت‌آمیز بود.")
        return redirect("home")
    return render(request, "user/verify_email_otp.html")

def google_callback(request):
    code = request.GET.get('code')
    if not code:
        return HttpResponse("کد OAuth گوگل پیدا نشد!")

    return HttpResponse(f"ورود با گوگل موفق! کد برگشتی گوگل: {code}")

def signup(request):
    form = SignupForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.save()
        user.save()
        login(request, user)
        return redirect("user:post_login_router")
    return render(request, "registration/signup.html", {"form": form})

@login_required
def profile(request):
    form = UserForm(request.POST or None, instance=request.user)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "پروفایل ذخیره شد.")
        return redirect("user:profile")
    return render(request, "user/profile.html", {"form": form})

@login_required
def delete_account(request):
    form = DeleteAccountForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        if not request.user.check_password(form.cleaned_data["password"]):
            form.add_error("password", "رمز عبور اشتباه است.")
        else:
            u = request.user
            logout(request)
            u.delete()
            messages.success(request, "حساب شما حذف شد.")
            return redirect("user:select_role")
    return render(request, "user/delete_account.html", {"form": form})

@login_required
def change_password(request):
    if request.method == "POST":
        form = PasswordChangeForm(request.user, data=request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, "رمز عبور با موفقیت تغییر کرد.")
            return redirect("user:post_login_router")
    else:
        form = PasswordChangeForm(request.user)
    return render(request, "user/change_password.html", {"form": form})
