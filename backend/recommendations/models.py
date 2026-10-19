from django.conf import settings
from django.db import models

from common.models import TimeStampedModel, UUIDModel


class RecommendationWeight(UUIDModel):
    name = models.CharField(max_length=80, unique=True, default="default")
    collaborative = models.FloatField(default=0.28)
    content = models.FloatField(default=0.22)
    preferences = models.FloatField(default=0.16)
    behavior = models.FloatField(default=0.14)
    ratings = models.FloatField(default=0.08)
    popularity = models.FloatField(default=0.07)
    recency = models.FloatField(default=0.05)
    is_active = models.BooleanField(default=True)

    def as_dict(self):
        return {
            "collaborative": self.collaborative,
            "content": self.content,
            "preferences": self.preferences,
            "behavior": self.behavior,
            "ratings": self.ratings,
            "popularity": self.popularity,
            "recency": self.recency,
        }


class MovieSimilarity(TimeStampedModel):
    source = models.ForeignKey("movies.Movie", on_delete=models.CASCADE, related_name="similar_from")
    target = models.ForeignKey("movies.Movie", on_delete=models.CASCADE, related_name="similar_to")
    score = models.FloatField()
    shared_signals = models.JSONField(default=list)

    class Meta:
        unique_together = ("source", "target")
        indexes = [models.Index(fields=["source", "-score"])]


class TasteProfile(UUIDModel):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="taste")
    genres = models.JSONField(default=dict)
    actors = models.JSONField(default=dict)
    directors = models.JSONField(default=dict)
    decades = models.JSONField(default=dict)
    languages = models.JSONField(default=dict)
    viewing_patterns = models.JSONField(default=dict)
    summary = models.TextField(blank=True)
    computed_at = models.DateTimeField(null=True, blank=True)


class RecommendationEvent(UUIDModel):
    class Section(models.TextChoices):
        TOP_PICKS = "top_picks", "Top Picks"
        BECAUSE_YOU_WATCHED = "because_you_watched", "Because You Watched"
        SIMILAR = "similar", "Similar Movies"
        HIDDEN_GEMS = "hidden_gems", "Hidden Gems"
        TRENDING = "trending", "Trending"
        NEW_RELEASES = "new_releases", "New Releases"
        CONTINUE_WATCHING = "continue_watching", "Continue Watching"
        GENRE = "genre", "Genre collection"

    class Action(models.TextChoices):
        IMPRESSION = "impression", "Impression"
        CLICK = "click", "Click"
        SAVE = "save", "Save"
        DISMISS = "dismiss", "Dismiss"
        WATCH = "watch", "Watch"

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="rec_events")
    movie = models.ForeignKey("movies.Movie", on_delete=models.CASCADE, related_name="rec_events")
    section = models.CharField(max_length=40, choices=Section.choices)
    action = models.CharField(max_length=20, choices=Action.choices)
    score = models.FloatField(default=0)
    reasons = models.JSONField(default=list)


class RecommendationHistory(UUIDModel):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="rec_history")
    movie = models.ForeignKey("movies.Movie", on_delete=models.CASCADE, related_name="shown_as_rec")
    section = models.CharField(max_length=40)
    score = models.FloatField(default=0)
    reasons = models.JSONField(default=list)

    class Meta:
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["user", "-created_at"])]
