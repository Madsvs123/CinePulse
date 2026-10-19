from analytics.models import EngagementEvent


class ActivityMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        path = request.path
        if path.startswith("/api/") and request.method in {"GET", "POST"}:
            user = request.user if getattr(request, "user", None) and request.user.is_authenticated else None
            if "analytics" not in path:
                EngagementEvent.objects.create(
                    user=user,
                    event_type=request.method.lower(),
                    path=path[:240],
                    metadata={"status": response.status_code},
                )
        return response
