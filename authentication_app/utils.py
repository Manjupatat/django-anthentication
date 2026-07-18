import random
from django.core.mail import send_mail
from django.conf import settings


def generate_otp():
    return str(random.randint(100000, 999999))


def send_otp_email(email, otp):

    subject = "Email Verification OTP"

    message = f"""
Hello,

Your OTP is:

{otp}

This OTP is valid for 5 minutes.

Do not share it with anyone.

Regards,
Demo Project
"""

    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [email],
        fail_silently=False,
    )