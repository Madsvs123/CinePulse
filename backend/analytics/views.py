from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

from analytics.models import DailyMetric
from analytics.services import dashboard
from common.permissions import IsAdminRole


@api_view(["GET"])
@permission_classes([IsAdminRole])
def overview(request):
    days = int(request.query_params.get("days") or 30)
    return Response(dashboard(days=days))


@api_view(["GET"])
@permission_classes([IsAdminRole])
def daily(request):
    rows = DailyMetric.objects.order_by("-date")[:60]
    return Response(
        [
            {
                "date": row.date,
                "active_users": row.active_users,
                "new_users": row.new_users,
                "ratings_count": row.ratings_count,
                "reviews_count": row.reviews_count,
                "searches_count": row.searches_count,
                "rec_impressions": row.rec_impressions,
                "rec_clicks": row.rec_clicks,
                "catalog_views": row.catalog_views,
            }
            for row in rows
        ]
    )
