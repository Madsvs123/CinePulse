from datetime import timedelta

from django.utils import timezone
from rest_framework import generics, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from accounts.models import EmailVerification, Follow, PasswordReset, User
from accounts.serializers import (
    NotifyPrefSerializer,
    OnboardingSerializer,
    PrivacySerializer,
    ProfileSerializer,
    PublicUserSerializer,
    RegisterSerializer,
    UserSerializer,
)
from accounts.tasks import send_password_reset_email, send_verification_email
from recommendations.engine import refresh_taste_profile
from recommendations.models import TasteProfile
from recommendations.tasks import refresh_user_taste_profile


def tokens_for(user):
    refresh = RefreshToken.for_user(user)
    return {"access": str(refresh.access_token), "refresh": str(refresh)}


class LoginView(TokenObtainPairView):
    permission_classes = (permissions.AllowAny,)


class RefreshView(TokenRefreshView):
    permission_classes = (permissions.AllowAny,)


@api_view(["POST"])
@permission_classes([permissions.AllowAny])
def register(request):
    serializer = RegisterSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    user = serializer.save()
    verification = EmailVerification.objects.create(
        user=user, expires_at=timezone.now() + timedelta(days=2)
    )
    send_verification_email.delay(user.email, verification.token)
    return Response({**UserSerializer(user).data, **tokens_for(user)}, status=status.HTTP_201_CREATED)


@api_view(["POST"])
@permission_classes([permissions.AllowAny])
def verify_email(request):
    token = request.data.get("token")
    record = EmailVerification.objects.filter(token=token).select_related("user").first()
    if not record or not record.is_valid:
        return Response({"detail": "Invalid or expired verification token."}, status=400)
    record.used_at = timezone.now()
    record.save(update_fields=["used_at"])
    record.user.email_verified = True
    record.user.save(update_fields=["email_verified"])
    return Response({"detail": "Email verified."})


@api_view(["POST"])
def resend_verification(request):
    if request.user.email_verified:
        return Response({"detail": "Email already verified."})
    verification = EmailVerification.objects.create(
        user=request.user, expires_at=timezone.now() + timedelta(days=2)
    )
    send_verification_email.delay(request.user.email, verification.token)
    return Response({"detail": "Verification email sent."})


@api_view(["POST"])
@permission_classes([permissions.AllowAny])
def request_password_reset(request):
    email = (request.data.get("email") or "").lower()
    user = User.objects.filter(email=email).first()
    if user:
        reset = PasswordReset.objects.create(user=user, expires_at=timezone.now() + timedelta(hours=4))
        send_password_reset_email.delay(user.email, reset.token)
    return Response({"detail": "If the account exists, a reset email is on the way."})


@api_view(["POST"])
@permission_classes([permissions.AllowAny])
def reset_password(request):
    token = request.data.get("token")
    password = request.data.get("password")
    record = PasswordReset.objects.filter(token=token).select_related("user").first()
    if not record or not record.is_valid:
        return Response({"detail": "Invalid or expired reset token."}, status=400)
    record.user.set_password(password)
    record.user.save()
    record.used_at = timezone.now()
    record.save(update_fields=["used_at"])
    return Response({"detail": "Password updated."})


@api_view(["GET", "PATCH"])
def me(request):
    if request.method == "PATCH":
        user = request.user
        for field in ("display_name", "first_name", "last_name", "username"):
            if field in request.data:
                setattr(user, field, request.data[field])
        user.save()
        if "profile" in request.data:
            profile = ProfileSerializer(user.profile, data=request.data["profile"], partial=True)
            profile.is_valid(raise_exception=True)
            profile.save()
    return Response(UserSerializer(request.user).data)


@api_view(["POST"])
def onboard(request):
    serializer = OnboardingSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    serializer.save(request.user)
    refresh_user_taste_profile.delay(str(request.user.id))
    return Response(UserSerializer(request.user).data)


@api_view(["GET", "PATCH"])
def privacy(request):
    instance = request.user.privacy
    if request.method == "PATCH":
        serializer = PrivacySerializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)
    return Response(PrivacySerializer(instance).data)


@api_view(["GET", "PATCH"])
def notify_prefs(request):
    instance = request.user.notify_prefs
    if request.method == "PATCH":
        serializer = NotifyPrefSerializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)
    return Response(NotifyPrefSerializer(instance).data)


@api_view(["GET"])
@permission_classes([permissions.AllowAny])
def public_profile(request, username):
    user = generics.get_object_or_404(User, username=username)
    if not user.privacy.public_profile and request.user != user:
        return Response({"detail": "This profile is private."}, status=403)
    data = PublicUserSerializer(user).data
    if user.privacy.show_taste_profile or request.user == user:
        taste = TasteProfile.objects.filter(user=user).first() or refresh_taste_profile(user)
        data["taste"] = {
            "genres": taste.genres,
            "actors": taste.actors,
            "directors": taste.directors,
            "decades": taste.decades,
            "languages": taste.languages,
            "viewing_patterns": taste.viewing_patterns,
            "summary": taste.summary,
        }
    data["is_following"] = (
        request.user.is_authenticated
        and Follow.objects.filter(follower=request.user, following=user).exists()
    )
    return Response(data)


@api_view(["POST"])
def follow_user(request, username):
    target = generics.get_object_or_404(User, username=username)
    if target == request.user:
        return Response({"detail": "You cannot follow yourself."}, status=400)
    if not target.privacy.allow_follow:
        return Response({"detail": "This viewer is not accepting follows."}, status=400)
    Follow.objects.get_or_create(follower=request.user, following=target)
    return Response({"detail": "Following."})


@api_view(["DELETE"])
def unfollow_user(request, username):
    target = generics.get_object_or_404(User, username=username)
    Follow.objects.filter(follower=request.user, following=target).delete()
    return Response(status=204)
