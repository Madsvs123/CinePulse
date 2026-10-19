from datetime import timedelta

from celery import shared_task
from django.utils import timezone

from accounts.models import Follow, User
from movies.models import Movie, StreamingAvailability, WatchlistItem
from notifications.services import notify
from recommendations.engine import score_catalog


@shared_task
def notify_watchlist_availability():
    sent = 0
    items = WatchlistItem.objects.select_related("watchlist__user", "movie").filter(
        movie__availability__available=True
    )
    for item in items:
        user = item.watchlist.user
        notify(
            user,
            "watchlist",
            f"{item.movie.title} is available to stream",
            "A title on your watchlist just became available.",
            {"movie": item.movie.slug},
        )
        sent += 1
    return sent


@shared_task
def notify_new_releases():
    since = timezone.now().date() - timedelta(days=7)
    movies = Movie.objects.filter(release_date__gte=since)
    count = 0
    for user in User.objects.filter(is_active=True, notify_prefs__new_releases=True):
        for movie in movies[:5]:
            notify(user, "new_release", f"New release: {movie.title}", movie.tagline, {"movie": movie.slug})
            count += 1
    return count


@shared_task
def notify_personalized_picks():
    count = 0
    for user in User.objects.filter(is_active=True, notify_prefs__recommendations=True):
        ranked = score_catalog(user, limit=1)
        if not ranked:
            continue
        movie, score, _ = ranked[0]
        notify(
            user,
            "recommendation",
            f"A new pick for you: {movie.title}",
            f"CinePulse scored this {round(score, 2)} against your taste.",
            {"movie": movie.slug},
        )
        count += 1
    return count


@shared_task
def notify_follow_activity(actor_id, title, body, payload):
    actor = User.objects.filter(id=actor_id).first()
    if not actor:
        return 0
    count = 0
    for follow in Follow.objects.filter(following=actor).select_related("follower"):
        notify(follow.follower, "follow_activity", title, body, payload)
        count += 1
    return count
