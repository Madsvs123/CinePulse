import secrets
import uuid

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone

from common.models import TimeStampedModel, UUIDModel


class User(AbstractUser):
    class Role(models.TextChoices):
        VIEWER = "viewer", "Viewer"
        STREAMING = "streaming", "Streaming service"
        MEDIA = "media", "Media company"
        COMMUNITY = "community", "Community organizer"
        ADMIN = "admin", "Administrator"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True)
    display_name = models.CharField(max_length=120, blank=True)
    role = models.CharField(max_length=20, choices=Role.choices, default=Role.VIEWER)
    email_verified = models.BooleanField(default=False)
    onboarding_complete = models.BooleanField(default=False)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    def save(self, *args, **kwargs):
        if self.email:
            self.email = self.email.strip().lower()
        if not self.username:
            self.username = self.email.split("@")[0][:40]
        if not self.display_name:
            self.display_name = self.get_full_name() or self.username
        super().save(*args, **kwargs)

    def __str__(self):
        return self.display_name or self.email


class Profile(UUIDModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    bio = models.TextField(blank=True)
    location = models.CharField(max_length=120, blank=True)
    country = models.CharField(max_length=80, blank=True)
    avatar_url = models.URLField(blank=True)
    website = models.URLField(blank=True)
    birth_year = models.PositiveIntegerField(null=True, blank=True)
    favorite_quote = models.CharField(max_length=240, blank=True)

    def __str__(self):
        return f"Profile({self.user})"


class PrivacySettings(UUIDModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="privacy")
    public_profile = models.BooleanField(default=True)
    show_watch_history = models.BooleanField(default=False)
    show_ratings = models.BooleanField(default=True)
    show_watchlists = models.BooleanField(default=True)
    show_reviews = models.BooleanField(default=True)
    show_taste_profile = models.BooleanField(default=True)
    allow_follow = models.BooleanField(default=True)
    allow_recommendations_from_follows = models.BooleanField(default=True)


class NotificationPreference(UUIDModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="notify_prefs")
    new_releases = models.BooleanField(default=True)
    watchlist_availability = models.BooleanField(default=True)
    recommendations = models.BooleanField(default=True)
    replies = models.BooleanField(default=True)
    reactions = models.BooleanField(default=True)
    followed_activity = models.BooleanField(default=True)


class FavoriteGenre(TimeStampedModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="favorite_genres")
    genre = models.ForeignKey("movies.Genre", on_delete=models.CASCADE, related_name="fans")
    weight = models.FloatField(default=1.0)

    class Meta:
        unique_together = ("user", "genre")


class PreferredLanguage(TimeStampedModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="preferred_languages")
    language = models.ForeignKey("movies.Language", on_delete=models.CASCADE, related_name="preferred_by")
    weight = models.FloatField(default=1.0)

    class Meta:
        unique_together = ("user", "language")


class Follow(TimeStampedModel):
    follower = models.ForeignKey(User, on_delete=models.CASCADE, related_name="following")
    following = models.ForeignKey(User, on_delete=models.CASCADE, related_name="followers")

    class Meta:
        unique_together = ("follower", "following")


class EmailVerification(UUIDModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="verifications")
    token = models.CharField(max_length=64, unique=True, default=secrets.token_urlsafe)
    expires_at = models.DateTimeField()
    used_at = models.DateTimeField(null=True, blank=True)

    @property
    def is_valid(self):
        return self.used_at is None and self.expires_at > timezone.now()


class PasswordReset(UUIDModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="password_resets")
    token = models.CharField(max_length=64, unique=True, default=secrets.token_urlsafe)
    expires_at = models.DateTimeField()
    used_at = models.DateTimeField(null=True, blank=True)

    @property
    def is_valid(self):
        return self.used_at is None and self.expires_at > timezone.now()
