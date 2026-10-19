from rest_framework import serializers

from recommendations.models import RecommendationEvent, RecommendationHistory, RecommendationWeight, TasteProfile


class WeightSerializer(serializers.ModelSerializer):
    class Meta:
        model = RecommendationWeight
        fields = (
            "id",
            "name",
            "collaborative",
            "content",
            "preferences",
            "behavior",
            "ratings",
            "popularity",
            "recency",
            "is_active",
        )


class TasteSerializer(serializers.ModelSerializer):
    class Meta:
        model = TasteProfile
        fields = (
            "genres",
            "actors",
            "directors",
            "decades",
            "languages",
            "viewing_patterns",
            "summary",
            "computed_at",
        )


class RecEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = RecommendationEvent
        fields = ("id", "movie", "section", "action", "score", "reasons", "created_at")
        read_only_fields = ("id", "created_at")


class RecHistorySerializer(serializers.ModelSerializer):
    title = serializers.CharField(source="movie.title", read_only=True)
    slug = serializers.CharField(source="movie.slug", read_only=True)
    poster_url = serializers.CharField(source="movie.poster_url", read_only=True)

    class Meta:
        model = RecommendationHistory
        fields = ("id", "title", "slug", "poster_url", "section", "score", "reasons", "created_at")
