from django.conf import settings
from django.contrib.postgres.indexes import GinIndex
from django.contrib.postgres.search import SearchVectorField
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils.text import slugify

from common.models import TimeStampedModel, UUIDModel


class Genre(UUIDModel):
    name = models.CharField(max_length=80, unique=True)
    slug = models.SlugField(max_length=80, unique=True)
    description = models.TextField(blank=True)

    class Meta:
        ordering = ["name"]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Language(UUIDModel):
    name = models.CharField(max_length=80, unique=True)
    code = models.CharField(max_length=12, unique=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Country(UUIDModel):
    name = models.CharField(max_length=80, unique=True)
    code = models.CharField(max_length=8, unique=True)

    class Meta:
        ordering = ["name"]
        verbose_name_plural = "countries"

    def __str__(self):
        return self.name


class Person(UUIDModel):
    name = models.CharField(max_length=160)
    slug = models.SlugField(max_length=180, unique=True)
    biography = models.TextField(blank=True)
    photo_url = models.URLField(blank=True)
    birth_year = models.PositiveIntegerField(null=True, blank=True)
    known_for = models.CharField(max_length=40, default="acting")

    class Meta:
        ordering = ["name"]
        indexes = [models.Index(fields=["name"])]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Keyword(UUIDModel):
    name = models.CharField(max_length=80, unique=True)
    slug = models.SlugField(max_length=80, unique=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class ProductionCompany(UUIDModel):
    name = models.CharField(max_length=160, unique=True)
    slug = models.SlugField(max_length=180, unique=True)
    country = models.ForeignKey(Country, null=True, blank=True, on_delete=models.SET_NULL)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class StreamingProvider(UUIDModel):
    name = models.CharField(max_length=120, unique=True)
    slug = models.SlugField(max_length=140, unique=True)
    logo_url = models.URLField(blank=True)
    website = models.URLField(blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Movie(UUIDModel):
    title = models.CharField(max_length=240)
    original_title = models.CharField(max_length=240, blank=True)
    slug = models.SlugField(max_length=280, unique=True)
    tagline = models.CharField(max_length=280, blank=True)
    description = models.TextField()
    release_date = models.DateField(null=True, blank=True)
    runtime = models.PositiveIntegerField(default=90)
    age_rating = models.CharField(max_length=16, default="PG-13")
    poster_url = models.URLField(blank=True)
    backdrop_url = models.URLField(blank=True)
    trailer_url = models.URLField(blank=True)
    popularity = models.FloatField(default=0)
    trending_score = models.FloatField(default=0)
    vote_average = models.FloatField(default=0)
    vote_count = models.PositiveIntegerField(default=0)
    budget = models.BigIntegerField(default=0)
    revenue = models.BigIntegerField(default=0)
    is_hidden_gem = models.BooleanField(default=False)
    search_vector = SearchVectorField(null=True)

    genres = models.ManyToManyField(Genre, related_name="movies", blank=True)
    languages = models.ManyToManyField(Language, related_name="movies", blank=True)
    countries = models.ManyToManyField(Country, related_name="movies", blank=True)
    keywords = models.ManyToManyField(Keyword, related_name="movies", blank=True)
    companies = models.ManyToManyField(ProductionCompany, related_name="movies", blank=True)
    directors = models.ManyToManyField(Person, related_name="directed_movies", blank=True)
    cast = models.ManyToManyField(Person, through="CastCredit", related_name="acted_movies", blank=True)

    class Meta:
        ordering = ["-release_date", "title"]
        indexes = [
            models.Index(fields=["-release_date"]),
            models.Index(fields=["-popularity"]),
            models.Index(fields=["-trending_score"]),
            models.Index(fields=["-vote_average"]),
            GinIndex(fields=["search_vector"]),
        ]

    def save(self, *args, **kwargs):
        if not self.slug:
            year = self.release_date.year if self.release_date else "na"
            self.slug = slugify(f"{self.title}-{year}")
        super().save(*args, **kwargs)

    @property
    def year(self):
        return self.release_date.year if self.release_date else None

    def __str__(self):
        return self.title


class CastCredit(TimeStampedModel):
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name="cast_credits")
    person = models.ForeignKey(Person, on_delete=models.CASCADE, related_name="cast_credits")
    character = models.CharField(max_length=160, blank=True)
    billing_order = models.PositiveIntegerField(default=0)

    class Meta:
        unique_together = ("movie", "person", "character")
        ordering = ["billing_order"]


class StreamingAvailability(UUIDModel):
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name="availability")
    provider = models.ForeignKey(StreamingProvider, on_delete=models.CASCADE, related_name="titles")
    region = models.CharField(max_length=8, default="US")
    offer_type = models.CharField(max_length=20, default="subscription")
    url = models.URLField(blank=True)
    available = models.BooleanField(default=True)
    available_from = models.DateField(null=True, blank=True)
    available_until = models.DateField(null=True, blank=True)

    class Meta:
        unique_together = ("movie", "provider", "region", "offer_type")


class WatchHistory(UUIDModel):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="watch_history")
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name="watch_events")
    progress_seconds = models.PositiveIntegerField(default=0)
    completed = models.BooleanField(default=False)
    watched_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("user", "movie")
        ordering = ["-watched_at"]


class Rating(UUIDModel):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="ratings")
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name="ratings")
    score = models.DecimalField(max_digits=3, decimal_places=1, validators=[MinValueValidator(0.5), MaxValueValidator(10)])

    class Meta:
        unique_together = ("user", "movie")


class MovieReaction(UUIDModel):
    class Kind(models.TextChoices):
        LIKE = "like", "Like"
        DISLIKE = "dislike", "Dislike"

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="movie_reactions")
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name="reactions")
    kind = models.CharField(max_length=12, choices=Kind.choices)

    class Meta:
        unique_together = ("user", "movie")


class Bookmark(UUIDModel):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="bookmarks")
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name="bookmarks")

    class Meta:
        unique_together = ("user", "movie")
        ordering = ["-created_at"]


class Watchlist(UUIDModel):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="watchlists")
    name = models.CharField(max_length=120)
    description = models.TextField(blank=True)
    is_default = models.BooleanField(default=False)
    is_public = models.BooleanField(default=False)

    class Meta:
        unique_together = ("user", "name")
        ordering = ["-updated_at"]


class WatchlistItem(UUIDModel):
    watchlist = models.ForeignKey(Watchlist, on_delete=models.CASCADE, related_name="items")
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name="watchlist_items")
    note = models.CharField(max_length=240, blank=True)

    class Meta:
        unique_together = ("watchlist", "movie")
        ordering = ["-created_at"]
