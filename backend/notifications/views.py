from rest_framework.decorators import api_view
from rest_framework.response import Response

from notifications.models import Notification
from notifications.serializers import NotificationSerializer
from notifications.services import mark_read


@api_view(["GET"])
def inbox(request):
    rows = Notification.objects.filter(user=request.user)[:50]
    unread = Notification.objects.filter(user=request.user, read_at__isnull=True).count()
    return Response({"unread": unread, "results": NotificationSerializer(rows, many=True).data})


@api_view(["POST"])
def read_one(request, pk):
    mark_read(request.user, pk)
    return Response({"detail": "Read."})


@api_view(["POST"])
def read_all(request):
    mark_read(request.user)
    return Response({"detail": "All notifications marked read."})
