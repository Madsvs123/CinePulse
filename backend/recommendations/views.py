from rest_framework import permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

from common.permissions import IsPlatformAdmin
from movies.models import Movie
from recommendations.engine import build_home_sections, refresh_taste_profile, score_catalog, serialize_reco, similar_movies
from recommendations.models import RecommendationHistory, RecommendationWeight
from recommendations.serializers import RecEventSerializer, RecHistorySerializer, TasteSerializer, WeightSerializer
from recommendations.tasks import rebuild_movie_similarities


@api_view(["GET"])
def home_feed(request):
    return Response(build_home_sections(request.user))


@api_view(["GET"])
def top_picks(request):
    ranked = score_catalog(request.user, limit=24)
    return Response([serialize_reco(movie, score, parts, request.user) for movie, score, parts in ranked])


@api_view(["GET"])
def taste(request):
    profile = refresh_taste_profile(request.user)
    return Response(TasteSerializer(profile).data)


@api_view(["GET"])
def history(request):
    rows = RecommendationHistory.objects.filter(user=request.user).select_related("movie")[:50]
    return Response(RecHistorySerializer(rows, many=True).data)


@api_view(["POST"])
def track(request):
    serializer = RecEventSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    serializer.save(user=request.user)
    return Response(serializer.data, status=201)


@api_view(["GET"])
def similar(request, slug):
    movie = Movie.objects.filter(slug=slug).first()
    if not movie:
        return Response({"detail": "Movie not found."}, status=404)
    return Response(similar_movies(movie, request.user))


@api_view(["GET", "PATCH"])
@permission_classes([IsPlatformAdmin])
def weights(request):
    row, _ = RecommendationWeight.objects.get_or_create(name="default", defaults={"is_active": True})
    if request.method == "PATCH":
        serializer = WeightSerializer(row, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)
    return Response(WeightSerializer(row).data)


@api_view(["POST"])
@permission_classes([IsPlatformAdmin])
def rebuild(request):
    rebuild_movie_similarities.delay()
    return Response({"detail": "Similarity rebuild queued."})
