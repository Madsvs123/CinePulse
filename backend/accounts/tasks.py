from celery import shared_task
from django.conf import settings
from django.core.mail import send_mail


@shared_task
def send_verification_email(email, token):
    link = f"{settings.FRONTEND_URL}/verify-email?token={token}"
    send_mail(
        "Verify your CinePulse account",
        f"Welcome to CinePulse. Confirm your email to start discovering films:\n{link}",
        settings.DEFAULT_FROM_EMAIL,
        [email],
        fail_silently=True,
    )
    return email


@shared_task
def send_password_reset_email(email, token):
    link = f"{settings.FRONTEND_URL}/reset-password?token={token}"
    send_mail(
        "Reset your CinePulse password",
        f"Use this link to choose a new password:\n{link}",
        settings.DEFAULT_FROM_EMAIL,
        [email],
        fail_silently=True,
    )
    return email
