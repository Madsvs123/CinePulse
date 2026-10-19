from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import NotificationPreference, PrivacySettings, Profile, User


@receiver(post_save, sender=User)
def create_user_defaults(sender, instance, created, **kwargs):
    if not created:
        return
    Profile.objects.get_or_create(user=instance)
    PrivacySettings.objects.get_or_create(user=instance)
    NotificationPreference.objects.get_or_create(user=instance)
    from movies.models import Watchlist

    Watchlist.objects.get_or_create(user=instance, name="Watch later", defaults={"is_default": True})
