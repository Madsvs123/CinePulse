from collections import Counter
from datetime import timedelta

from django.db.models import Avg, Count
from django.db.models.functions import TruncDate
from django.utils import timezone

from analytics.models import DailyMetric, EngagementEvent, SearchQuery
from movies.models import Movie, Rating, WatchHistory
from recommendations.models import RecommendationEvent
from accounts.models import User
from community.models import Review


def dashboard(days=30):
    since = timezone.now() - timedelta(days=days)
    users = User.objects.filter(date_joined__gte=since).count()
    active = EngagementEvent.objects.filter(created_at__gte=since, user__isnull=False).values("user").distinct().count()
    popular = list(
        WatchHistory.objects.filter(created_at__gte=since)
        .values("movie__title", "movie__slug")
        .annotate(plays=Count("id"))
        .order_by("-plays")[:8]
    )
    searches = list(
        SearchQuery.objects.filter(created_at__gte=since)
        .values("query")
        .annotate(n=Count("id"))
        .order_by("-n")[:8]
    )
    genres = Counter()
    for movie in Movie.objects.prefetch_related("genres"):
        for genre in movie.genres.all():
            genres[genre.name] += movie.trending_score or movie.popularity
    recs = RecommendationEvent.objects.filter(created_at__gte=since)
    impressions = recs.filter(action="impression").count()
    clicks = recs.filter(action="click").count()
    retention = {
        "d1": _retention(1),
        "d7": _retention(7),
        "d30": _retention(30),
    }
    timeline = list(
        EngagementEvent.objects.filter(created_at__gte=since)
        .annotate(day=TruncDate("created_at"))
        .values("day")
        .annotate(events=Count("id"))
        .order_by("day")
    )
    return {
        "kpis": {
            "catalog_size": Movie.objects.count(),
            "new_users": users,
            "active_users": active,
            "ratings": Rating.objects.filter(created_at__gte=since).count(),
            "reviews": Review.objects.filter(created_at__gte=since).count(),
            "searches": SearchQuery.objects.filter(created_at__gte=since).count(),
            "avg_rating": float(Rating.objects.aggregate(avg=Avg("score"))["avg"] or 0),
            "rec_ctr": round((clicks / impressions) * 100, 2) if impressions else 0,
        },
        "popular_movies": popular,
        "search_behavior": searches,
        "trending_genres": [{"name": name, "score": round(score, 2)} for name, score in genres.most_common(8)],
        "recommendation_performance": {
            "impressions": impressions,
            "clicks": clicks,
            "saves": recs.filter(action="save").count(),
            "watches": recs.filter(action="watch").count(),
        },
        "retention": retention,
        "timeline": timeline,
    }


def _retention(days):
    start = timezone.now() - timedelta(days=days + 7)
    cohort = User.objects.filter(date_joined__gte=start, date_joined__lt=start + timedelta(days=7))
    if not cohort.exists():
        return 0
    returned = (
        EngagementEvent.objects.filter(
            user__in=cohort,
            created_at__gte=start + timedelta(days=days),
        )
        .values("user")
        .distinct()
        .count()
    )
    return round(returned / cohort.count() * 100, 1)


def rollup_today():
    day = timezone.now().date()
    start = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
    recs = RecommendationEvent.objects.filter(created_at__gte=start)
    DailyMetric.objects.update_or_create(
        date=day,
        defaults={
            "active_users": EngagementEvent.objects.filter(created_at__gte=start, user__isnull=False)
            .values("user")
            .distinct()
            .count(),
            "new_users": User.objects.filter(date_joined__gte=start).count(),
            "ratings_count": Rating.objects.filter(created_at__gte=start).count(),
            "reviews_count": Review.objects.filter(created_at__gte=start).count(),
            "searches_count": SearchQuery.objects.filter(created_at__gte=start).count(),
            "rec_impressions": recs.filter(action="impression").count(),
            "rec_clicks": recs.filter(action="click").count(),
            "catalog_views": EngagementEvent.objects.filter(created_at__gte=start, path__contains="/movies/").count(),
        },
    )
