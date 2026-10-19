from rest_framework import serializers

from movies.models import (
    Country,
    Genre,
    Keyword,
    Language,
    Movie,
    Person,
    ProductionCompany,
    Rating,
    StreamingAvailability,
    StreamingProvider,
    WatchHistory,
    Watchlist,
    WatchlistItem,
)


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = ("id", "name", "slug", "description")


class LanguageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Language
        fields = ("id", "name", "code")


class CountrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Country
        fields = ("id", "name", "code")


class PersonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Person
        fields = ("id", "name", "slug", "biography", "photo_url", "birth_year", "known_for")


class KeywordSerializer(serializers.ModelSerializer):
    class Meta:
        model = Keyword
        fields = ("id", "name", "slug")


class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductionCompany
        fields = ("id", "name", "slug")


class ProviderSerializer(serializers.ModelSerializer):
    class Meta:
        model = StreamingProvider
        fields = ("id", "name", "slug", "logo_url", "website")


class AvailabilitySerializer(serializers.ModelSerializer):
    provider = ProviderSerializer(read_only=True)

    class Meta:
        model = StreamingAvailability
        fields = ("id", "provider", "region", "offer_type", "url", "available", "available_from", "available_until")


class MovieListSerializer(serializers.ModelSerializer):
    genres = GenreSerializer(many=True, read_only=True)
    user_reaction = serializers.SerializerMethodField()
    user_rating = serializers.SerializerMethodField()
    bookmarked = serializers.SerializerMethodField()
    year = serializers.IntegerField(read_only=True)

    class Meta:
        model = Movie
        fields = (
            "id",
            "title",
            "slug",
            "tagline",
            "description",
            "release_date",
            "year",
            "runtime",
            "age_rating",
            "poster_url",
            "backdrop_url",
            "trailer_url",
            "vote_average",
            "vote_count",
            "popularity",
            "trending_score",
            "is_hidden_gem",
            "genres",
            "user_reaction",
            "user_rating",
            "bookmarked",
        )

    def _user(self):
        request = self.context.get("request")
        return request.user if request and request.user.is_authenticated else None

    def get_user_reaction(self, obj):
        user = self._user()
        if not user:
            return None
        row = obj.reactions.filter(user=user).first()
        return row.kind if row else None

    def get_user_rating(self, obj):
        user = self._user()
        if not user:
            return None
        row = obj.ratings.filter(user=user).first()
        return float(row.score) if row else None

    def get_bookmarked(self, obj):
        user = self._user()
        return bool(user and obj.bookmarks.filter(user=user).exists())


class MovieDetailSerializer(MovieListSerializer):
    languages = LanguageSerializer(many=True, read_only=True)
    countries = CountrySerializer(many=True, read_only=True)
    keywords = KeywordSerializer(many=True, read_only=True)
    companies = CompanySerializer(many=True, read_only=True)
    directors = PersonSerializer(many=True, read_only=True)
    cast = serializers.SerializerMethodField()
    availability = AvailabilitySerializer(many=True, read_only=True)

    class Meta(MovieListSerializer.Meta):
        fields = MovieListSerializer.Meta.fields + (
            "original_title",
            "budget",
            "revenue",
            "languages",
            "countries",
            "keywords",
            "companies",
            "directors",
            "cast",
            "availability",
        )

    def get_cast(self, obj):
        return [
            {
                "id": str(credit.person_id),
                "name": credit.person.name,
                "slug": credit.person.slug,
                "character": credit.character,
                "billing_order": credit.billing_order,
                "photo_url": credit.person.photo_url,
            }
            for credit in obj.cast_credits.select_related("person")
        ]


class RatingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rating
        fields = ("id", "movie", "score", "created_at", "updated_at")
        read_only_fields = ("id", "created_at", "updated_at")


class WatchHistorySerializer(serializers.ModelSerializer):
    movie = MovieListSerializer(read_only=True)
    movie_id = serializers.UUIDField(write_only=True)

    class Meta:
        model = WatchHistory
        fields = ("id", "movie", "movie_id", "progress_seconds", "completed", "watched_at")


class WatchlistItemSerializer(serializers.ModelSerializer):
    movie = MovieListSerializer(read_only=True)
    movie_id = serializers.UUIDField(write_only=True, required=False)

    class Meta:
        model = WatchlistItem
        fields = ("id", "movie", "movie_id", "note", "created_at")


class WatchlistSerializer(serializers.ModelSerializer):
    items = WatchlistItemSerializer(many=True, read_only=True)
    item_count = serializers.IntegerField(source="items.count", read_only=True)

    class Meta:
        model = Watchlist
        fields = ("id", "name", "description", "is_default", "is_public", "items", "item_count", "created_at", "updated_at")
