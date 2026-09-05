from django.core.mail import send_mail
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.conf import settings


def send_password_reset_email(user):
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = PasswordResetTokenGenerator().make_token(user)
    reset_url = f"{settings.FRONTEND_URL}/reset-password?uid={uid}&token={token}"
    send_mail(
        subject="Reset your TravelMind password",
        message=(
            f"Hello {user.username},\n\n"
            f"Click the link below to reset your TravelMind password:\n\n"
            f"{reset_url}\n\n"
            f"This link expires in 24 hours.\n\n"
            f"If you didn't request a password reset, you can safely ignore this email."
        ),
        from_email=f"TravelMind <{settings.EMAIL_HOST_USER}>",
        recipient_list=[user.email],
        fail_silently=False,
    )
    return reset_url


class EmailVerificationTokenGenerator(PasswordResetTokenGenerator):
    """
    Separate stateless token generator (no new DB table needed, same pattern
    as the password-reset flow above). Including is_verified in the hash
    means a token becomes invalid the moment it's been used once - no
    separate "used" flag to track.
    """
    def _make_hash_value(self, user, timestamp):
        return f'{user.pk}{timestamp}{user.is_verified}'


email_verification_token = EmailVerificationTokenGenerator()


def send_verification_email(user):
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = email_verification_token.make_token(user)
    verify_url = f"{settings.FRONTEND_URL}/verify-email?uid={uid}&token={token}"
    send_mail(
        subject="Verify your TravelMind email address",
        message=(
            f"Hello {user.username},\n\n"
            f"Thanks for signing up for TravelMind! Click the link below to verify "
            f"your email address and activate your account:\n\n"
            f"{verify_url}\n\n"
            f"This link expires in 24 hours.\n\n"
            f"If you didn't create a TravelMind account, you can safely ignore this email."
        ),
        from_email=f"TravelMind <{settings.EMAIL_HOST_USER}>",
        recipient_list=[user.email],
        fail_silently=False,
    )
    return verify_url
