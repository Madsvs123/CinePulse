from django.conf import settings
from django.db import models
from django.utils.text import slugify

from common.models import UUIDModel


class Review(UUIDModel):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="reviews")
    movie = models.ForeignKey("movies.Movie", on_delete=models.CASCADE, related_name="reviews")
    title = models.CharField(max_length=180)
    body = models.TextField()
    contains_spoilers = models.BooleanField(default=False)
    score = models.DecimalField(max_digits=3, decimal_places=1)
    helpful_count = models.PositiveIntegerField(default=0)

    class Meta:
        unique_together = ("user", "movie")
        ordering = ["-created_at"]


class ReviewReaction(UUIDModel):
    class Kind(models.TextChoices):
        HELPFUL = "helpful", "Helpful"
        LOVE = "love", "Love"
        INSIGHTFUL = "insightful", "Insightful"
        DISAGREE = "disagree", "Disagree"

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="review_reactions")
    review = models.ForeignKey(Review, on_delete=models.CASCADE, related_name="reactions")
    kind = models.CharField(max_length=20, choices=Kind.choices)

    class Meta:
        unique_together = ("user", "review", "kind")


class UserList(UUIDModel):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="lists")
    title = models.CharField(max_length=160)
    slug = models.SlugField(max_length=200, unique=True)
    description = models.TextField(blank=True)
    is_public = models.BooleanField(default=True)
    cover_url = models.URLField(blank=True)

    class Meta:
        ordering = ["-updated_at"]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(f"{self.title}-{str(self.id)[:8]}")
        super().save(*args, **kwargs)


class UserListItem(UUIDModel):
    list = models.ForeignKey(UserList, on_delete=models.CASCADE, related_name="items")
    movie = models.ForeignKey("movies.Movie", on_delete=models.CASCADE, related_name="list_items")
    note = models.CharField(max_length=280, blank=True)
    position = models.PositiveIntegerField(default=0)

    class Meta:
        unique_together = ("list", "movie")
        ordering = ["position", "created_at"]


class Discussion(UUIDModel):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="discussions")
    movie = models.ForeignKey("movies.Movie", null=True, blank=True, on_delete=models.SET_NULL, related_name="discussions")
    title = models.CharField(max_length=200)
    body = models.TextField()
    contains_spoilers = models.BooleanField(default=False)
    is_pinned = models.BooleanField(default=False)

    class Meta:
        ordering = ["-is_pinned", "-updated_at"]


class Comment(UUIDModel):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="comments")
    review = models.ForeignKey(Review, null=True, blank=True, on_delete=models.CASCADE, related_name="comments")
    discussion = models.ForeignKey(Discussion, null=True, blank=True, on_delete=models.CASCADE, related_name="comments")
    parent = models.ForeignKey("self", null=True, blank=True, on_delete=models.CASCADE, related_name="replies")
    body = models.TextField()
    contains_spoilers = models.BooleanField(default=False)

    class Meta:
        ordering = ["created_at"]
