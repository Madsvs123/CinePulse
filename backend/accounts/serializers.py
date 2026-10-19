from django.contrib.auth.password_validation import validate_password
from django.utils import timezone
from rest_framework import serializers

from accounts.models import (
    FavoriteGenre,
    Follow,
    NotificationPreference,
    PreferredLanguage,
    PrivacySettings,
    Profile,
    User,
)
from movies.models import Genre, Language


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ("bio", "location", "country", "avatar_url", "website", "birth_year", "favorite_quote")


class PrivacySerializer(serializers.ModelSerializer):
    class Meta:
        model = PrivacySettings
        fields = (
            "public_profile",
            "show_watch_history",
            "show_ratings",
            "show_watchlists",
            "show_reviews",
            "show_taste_profile",
            "allow_follow",
            "allow_recommendations_from_follows",
        )


class NotifyPrefSerializer(serializers.ModelSerializer):
    class Meta:
        model = NotificationPreference
        fields = (
            "new_releases",
            "watchlist_availability",
            "recommendations",
            "replies",
            "reactions",
            "followed_activity",
        )


class UserSerializer(serializers.ModelSerializer):
    profile = ProfileSerializer(read_only=True)
    privacy = PrivacySerializer(read_only=True)
    notify_prefs = NotifyPrefSerializer(read_only=True)
    favorite_genres = serializers.SerializerMethodField()
    preferred_languages = serializers.SerializerMethodField()
    followers_count = serializers.IntegerField(source="followers.count", read_only=True)
    following_count = serializers.IntegerField(source="following.count", read_only=True)

    class Meta:
        model = User
        fields = (
            "id",
            "email",
            "username",
            "display_name",
            "first_name",
            "last_name",
            "role",
            "email_verified",
            "onboarding_complete",
            "profile",
            "privacy",
            "notify_prefs",
            "favorite_genres",
            "preferred_languages",
            "followers_count",
            "following_count",
            "date_joined",
        )

    def get_favorite_genres(self, obj):
        return [
            {"id": str(row.genre_id), "name": row.genre.name, "slug": row.genre.slug, "weight": row.weight}
            for row in obj.favorite_genres.select_related("genre")
        ]

    def get_preferred_languages(self, obj):
        return [
            {"id": str(row.language_id), "name": row.language.name, "code": row.language.code, "weight": row.weight}
            for row in obj.preferred_languages.select_related("language")
        ]


class PublicUserSerializer(serializers.ModelSerializer):
    profile = ProfileSerializer(read_only=True)
    followers_count = serializers.IntegerField(source="followers.count", read_only=True)

    class Meta:
        model = User
        fields = ("id", "username", "display_name", "role", "profile", "followers_count")


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ("email", "username", "display_name", "password", "role", "first_name", "last_name")

    def validate_password(self, value):
        validate_password(value)
        return value

    def create(self, validated):
        password = validated.pop("password")
        role = validated.get("role") or User.Role.VIEWER
        if role == User.Role.ADMIN:
            validated["role"] = User.Role.VIEWER
        user = User(**validated)
        user.set_password(password)
        user.save()
        return user


class OnboardingSerializer(serializers.Serializer):
    display_name = serializers.CharField(required=False, allow_blank=True)
    bio = serializers.CharField(required=False, allow_blank=True)
    country = serializers.CharField(required=False, allow_blank=True)
    genre_ids = serializers.ListField(child=serializers.UUIDField(), required=False)
    language_ids = serializers.ListField(child=serializers.UUIDField(), required=False)

    def save(self, user):
        data = self.validated_data
        if data.get("display_name"):
            user.display_name = data["display_name"]
        user.onboarding_complete = True
        user.save(update_fields=["display_name", "onboarding_complete"])
        profile = user.profile
        profile.bio = data.get("bio", profile.bio)
        profile.country = data.get("country", profile.country)
        profile.save()
        if "genre_ids" in data:
            user.favorite_genres.all().delete()
            for genre in Genre.objects.filter(id__in=data["genre_ids"]):
                FavoriteGenre.objects.create(user=user, genre=genre)
        if "language_ids" in data:
            user.preferred_languages.all().delete()
            for language in Language.objects.filter(id__in=data["language_ids"]):
                PreferredLanguage.objects.create(user=user, language=language)
        return user
