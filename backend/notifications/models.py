from django.conf import settings
from django.db import models

from common.models import UUIDModel


class Notification(UUIDModel):
    class Kind(models.TextChoices):
        NEW_RELEASE = "new_release", "New release"
        WATCHLIST = "watchlist", "Watchlist availability"
        RECOMMENDATION = "recommendation", "Recommendation"
        REPLY = "reply", "Reply"
        REACTION = "reaction", "Reaction"
        FOLLOW_ACTIVITY = "follow_activity", "Followed-user activity"

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="notifications")
    kind = models.CharField(max_length=32, choices=Kind.choices)
    title = models.CharField(max_length=180)
    body = models.TextField(blank=True)
    payload = models.JSONField(default=dict)
    read_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["user", "-created_at"])]

    @property
    def is_read(self):
        return self.read_at is not None
