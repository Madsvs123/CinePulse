from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.utils import timezone

from accounts.models import NotificationPreference
from notifications.models import Notification


KIND_PREF = {
    "new_release": "new_releases",
    "watchlist": "watchlist_availability",
    "recommendation": "recommendations",
    "reply": "replies",
    "reaction": "reactions",
    "follow_activity": "followed_activity",
}


def notify(user, kind, title, body="", payload=None):
    prefs = getattr(user, "notify_prefs", None) or NotificationPreference.objects.filter(user=user).first()
    flag = KIND_PREF.get(kind)
    if prefs and flag and not getattr(prefs, flag, True):
        return None
    notification = Notification.objects.create(
        user=user, kind=kind, title=title, body=body, payload=payload or {}
    )
    layer = get_channel_layer()
    if layer:
        async_to_sync(layer.group_send)(
            f"user_{user.id}",
            {
                "type": "notify",
                "payload": {
                    "id": str(notification.id),
                    "kind": notification.kind,
                    "title": notification.title,
                    "body": notification.body,
                    "payload": notification.payload,
                    "created_at": notification.created_at.isoformat(),
                    "is_read": False,
                },
            },
        )
    return notification


def mark_read(user, notification_id=None):
    qs = Notification.objects.filter(user=user, read_at__isnull=True)
    if notification_id:
        qs = qs.filter(id=notification_id)
    return qs.update(read_at=timezone.now())
