
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from .models import EmailOTP
from .utils import generate_otp, send_otp_email

def home_view(request):
    return render(request, "home.html")


def login_view(request):

    if request.method == "POST":

        username_or_email = request.POST.get("username")
        password = request.POST.get("password")



        username = username_or_email
        # If the user entered an email, convert it to the username
        if "@" in username_or_email:
            try:
                user_obj = User.objects.get(email=username_or_email)
                username = user_obj.username
            except User.DoesNotExist:
                username = username_or_email
        # return redirect("home")
        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is not None:

            login(request, user)

            messages.success(request, "Login successful.")

            return redirect("home")

        else:

            messages.error(request, "Invalid username or password.")

    return render(request, "login.html")


# def signup_view(request):
#     # context = {
#     #     "email": "",
#     #     "otp": "",
#     #     "verified": "",
#     # }
#
#     context = {
#         "email": "",
#         "otp": "",
#         "verified": False,
#     }
#     if request.method == "POST":
#
#         action = request.POST.get("action")
#
#         email = request.POST.get("email", "")
#         context["email"] = email
#
#         if action == "send_otp":
#
#             otp = generate_otp()
#
#             EmailOTP.objects.update_or_create(
#                 email=email,
#                 defaults={
#                     "otp": otp,
#                     "verified": False
#                 }
#             )
#
#             send_otp_email(email, otp)
#
#             messages.success(request, "OTP sent successfully.")
#
#             return render(request, "signup.html", {"email": email})
#
#         elif action == "verify_otp":
#
#             otp2 = request.POST.get("otp", "")
#             context["otp"] = otp2
#             try:
#
#                 record = EmailOTP.objects.get(email=email)
#                 context["verified"] = record.verified
#                 if record.is_expired():
#
#                     messages.error(request, "OTP has expired.")
#
#                 elif record.otp == otp2:
#
#                     record.verified = True
#                     record.save()
#                     context["verified"] = True
#                     messages.success(request, "Email verified successfully.")
#
#                 else:
#
#                     messages.error(request, "Invalid OTP.")
#
#             except EmailOTP.DoesNotExist:
#
#                 messages.error(request, "Please send OTP first.")
#
#             return render(request, "signup.html", {"email": email})
#
#         elif action == "signup":
#
#             password = request.POST.get("password")
#             confirm = request.POST.get("confirm_password")
#
#             if password != confirm:
#
#                 messages.error(request, "Passwords do not match.")
#
#                 return render(request, "signup.html", {"email": email})
#
#             try:
#
#                 record = EmailOTP.objects.get(email=email)
#
#                 if not record.verified:
#
#                     messages.error(request, "Please verify your email first.")
#
#                     return render(request, "signup.html", {"email": email})
#
#             except EmailOTP.DoesNotExist:
#
#                 messages.error(request, "Please verify your email first.")
#
#                 return render(request, "signup.html", {"email": email})
#
#             username = email.split("@")[0]
#
#             User.objects.create_user(
#                 username=username,
#                 email=email,
#                 password=password
#             )
#
#             record.delete()
#
#             messages.success(request, "Account created successfully.")
#
#             return redirect("login")
#     context = {
#         "email": email,
#         "otp": otp2,
#         "verified": True
#     }
#
#     return render(request, "signup.html", context)


def signup_view(request):

    if request.method == "POST":

        email = request.POST.get("email")

        otp = generate_otp()

        EmailOTP.objects.update_or_create(
            email=email,
            defaults={
                "otp": otp,
                "verified": False,
            }
        )

        send_otp_email(email, otp)

        request.session["signup_email"] = email

        messages.success(request, "OTP sent successfully.")

        return redirect("verify_otp")

    return render(request, "signup.html")

def verify_otp_view(request):

    email = request.session.get("signup_email")

    if not email:
        return redirect("signup")

    if request.method == "POST":

        otp = request.POST.get("otp")

        try:

            record = EmailOTP.objects.get(email=email)

            if record.is_expired():
                messages.error(request, "OTP expired.")
                return render(request, "verify_otp.html")

            if record.otp != otp:
                messages.error(request, "Invalid OTP.")
                return render(request, "verify_otp.html")

            record.verified = True
            record.save()

            return redirect("complete_signup")

        except EmailOTP.DoesNotExist:

            messages.error(request, "Please send OTP first.")

    return render(request, "verify_otp.html", {"email":email})


def complete_signup_view(request):

    email = request.session.get("signup_email")

    if not email:
        return redirect("signup")

    try:
        record = EmailOTP.objects.get(email=email)

        if not record.verified:
            return redirect("verify_otp")

    except EmailOTP.DoesNotExist:
        return redirect("signup")

    if request.method == "POST":

        username = request.POST.get("username")
        password = request.POST.get("password")
        confirm = request.POST.get("confirm_password")

        if password != confirm:
            messages.error(request, "Passwords do not match.")
            return render(request, "complete_signup.html")

        User.objects.create_user(
            username=username,
            email=email,
            password=password
        )

        record.delete()

        del request.session["signup_email"]

        messages.success(request, "Account created successfully.")

        return redirect("login")

    return render(request, "complete_signup.html", {"email": email})

def logout_view(request):
    logout(request)
    messages.success(request, "Logged out successfully.")
    return redirect("login")

def forgot_password_view(request):

    if request.method == "POST":

        email = request.POST.get("email")

        if not User.objects.filter(email=email).exists():
            messages.error(request, "No account found with this email.")
            return render(request, "forgot_password.html")

        otp = generate_otp()

        EmailOTP.objects.update_or_create(
            email=email,
            defaults={
                "otp": otp,
                "verified": False,
            }
        )

        send_otp_email(email, otp)

        request.session["reset_email"] = email

        messages.success(request, "OTP sent successfully.")

        return redirect("verify_reset_otp")

    return render(request, "forgot_password.html")

def verify_reset_otp_view(request):

    email = request.session.get("reset_email")

    if not email:
        return redirect("forgot_password")

    if request.method == "POST":

        otp = request.POST.get("otp")

        try:
            record = EmailOTP.objects.get(email=email)

            if record.is_expired():
                messages.error(request, "OTP has expired.")
                return render(request, "verify_reset_otp.html", {"email": email})

            if record.otp != otp:
                messages.error(request, "Invalid OTP.")
                return render(request, "verify_reset_otp.html", {"email": email})

            record.verified = True
            record.save()

            return redirect("reset_password")

        except EmailOTP.DoesNotExist:
            messages.error(request, "Please request an OTP first.")

    return render(request, "verify_reset_otp.html", {"email": email})

def reset_password_view(request):

    email = request.session.get("reset_email")

    if not email:
        return redirect("forgot_password")

    try:
        otp_record = EmailOTP.objects.get(email=email)

        if not otp_record.verified:
            return redirect("verify_reset_otp")

    except EmailOTP.DoesNotExist:
        return redirect("forgot_password")

    if request.method == "POST":

        password = request.POST.get("password")
        confirm = request.POST.get("confirm_password")

        if password != confirm:
            # messages.error(request, "Passwords do not match.")
            return render(request, "reset_password.html",
                          {"email":email, "password_error": "Passwords do not match.",})

        user = User.objects.get(email=email)

        user.set_password(password)
        user.save()

        otp_record.delete()

        del request.session["reset_email"]

        messages.success(request, "Password reset successfully.")

        return redirect("login")

    return render(request, "reset_password.html",
                  {"email":email, "password_error": "Passwords do not match."})