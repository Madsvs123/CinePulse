from django.conf import settings
from django.db import models

from common.models import UUIDModel


class EngagementEvent(UUIDModel):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name="engagements"
    )
    event_type = models.CharField(max_length=40)
    path = models.CharField(max_length=240, blank=True)
    movie = models.ForeignKey("movies.Movie", null=True, blank=True, on_delete=models.SET_NULL)
    metadata = models.JSONField(default=dict)


class SearchQuery(UUIDModel):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name="searches"
    )
    query = models.CharField(max_length=240)
    filters = models.JSONField(default=dict)
    result_count = models.PositiveIntegerField(default=0)


class DailyMetric(UUIDModel):
    date = models.DateField(unique=True)
    active_users = models.PositiveIntegerField(default=0)
    new_users = models.PositiveIntegerField(default=0)
    ratings_count = models.PositiveIntegerField(default=0)
    reviews_count = models.PositiveIntegerField(default=0)
    searches_count = models.PositiveIntegerField(default=0)
    rec_impressions = models.PositiveIntegerField(default=0)
    rec_clicks = models.PositiveIntegerField(default=0)
    catalog_views = models.PositiveIntegerField(default=0)
    extra = models.JSONField(default=dict)
