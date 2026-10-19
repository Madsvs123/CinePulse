from datetime import timedelta

from celery import shared_task
from django.db.models import Count
from django.utils import timezone

from accounts.models import User
from movies.models import Movie, WatchHistory
from recommendations.engine import build_similarity_graph, refresh_taste_profile


@shared_task
def rebuild_movie_similarities():
    return build_similarity_graph()


@shared_task
def refresh_trending_scores():
    recent = timezone.now() - timedelta(days=14)
    counts = dict(
        WatchHistory.objects.filter(watched_at__gte=recent).values("movie_id").annotate(n=Count("id")).values_list("movie_id", "n")
    )
    updated = 0
    for movie in Movie.objects.all():
        recency_boost = 8 if movie.release_date and (timezone.now().date() - movie.release_date).days < 45 else 0
        movie.trending_score = movie.popularity * 0.4 + counts.get(movie.id, 0) * 3 + movie.vote_average + recency_boost
        movie.save(update_fields=["trending_score"])
        updated += 1
    return updated


@shared_task
def refresh_user_taste_profile(user_id):
    user = User.objects.filter(id=user_id).first()
    if not user:
        return None
    profile = refresh_taste_profile(user)
    return str(profile.id)


@shared_task
def refresh_all_taste_profiles():
    count = 0
    for user in User.objects.filter(is_active=True):
        refresh_taste_profile(user)
        count += 1
    return count
