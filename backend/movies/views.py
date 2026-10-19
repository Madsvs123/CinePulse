from django.contrib.postgres.search import SearchQuery, SearchRank, SearchVector
from django.db.models import Prefetch
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response

from analytics.models import SearchQuery as SearchLog
from movies.filters import MovieFilter
from movies.models import (
    Bookmark,
    Country,
    Genre,
    Language,
    Movie,
    MovieReaction,
    Person,
    Rating,
    WatchHistory,
    Watchlist,
    WatchlistItem,
)
from movies.serializers import (
    CountrySerializer,
    GenreSerializer,
    LanguageSerializer,
    MovieDetailSerializer,
    MovieListSerializer,
    PersonSerializer,
    RatingSerializer,
    WatchHistorySerializer,
    WatchlistItemSerializer,
    WatchlistSerializer,
)
from recommendations.engine import movie_card, similar_movies
from recommendations.tasks import refresh_user_taste_profile


class CatalogMixin:
    def get_queryset(self):
        return (
            Movie.objects.prefetch_related("genres", "languages", "countries", "keywords", "companies", "directors")
            .prefetch_related(Prefetch("cast_credits"))
            .distinct()
        )


class MovieViewSet(CatalogMixin, viewsets.ReadOnlyModelViewSet):
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    filterset_class = MovieFilter
    search_fields = ("title", "original_title", "description", "tagline")
    ordering_fields = ("release_date", "vote_average", "popularity", "trending_score", "runtime", "title")
    lookup_field = "slug"

    def get_serializer_class(self):
        return MovieDetailSerializer if self.action == "retrieve" else MovieListSerializer

    @action(detail=False, methods=["get"])
    def search(self, request):
        query = (request.query_params.get("q") or "").strip()
        qs = self.filter_queryset(self.get_queryset())
        if query:
            search = SearchQuery(query, search_type="websearch")
            qs = (
                qs.annotate(rank=SearchRank(SearchVector("title", "description", "tagline"), search))
                .filter(rank__gte=0.02)
                .order_by("-rank", "-popularity")
            )
        page = self.paginate_queryset(qs)
        SearchLog.objects.create(
            user=request.user if request.user.is_authenticated else None,
            query=query,
            filters={k: v for k, v in request.query_params.items() if k != "q"},
            result_count=qs.count(),
        )
        serializer = MovieListSerializer(page, many=True, context={"request": request})
        return self.get_paginated_response(serializer.data)

    @action(detail=True, methods=["get"])
    def similar(self, request, slug=None):
        movie = self.get_object()
        return Response(similar_movies(movie, request.user))

    @action(detail=True, methods=["post"], permission_classes=[permissions.IsAuthenticated])
    def rate(self, request, slug=None):
        movie = self.get_object()
        score = request.data.get("score")
        rating, _ = Rating.objects.update_or_create(user=request.user, movie=movie, defaults={"score": score})
        refresh_user_taste_profile.delay(str(request.user.id))
        return Response(RatingSerializer(rating).data)

    @action(detail=True, methods=["post"], permission_classes=[permissions.IsAuthenticated])
    def react(self, request, slug=None):
        movie = self.get_object()
        kind = request.data.get("kind")
        if kind not in {MovieReaction.Kind.LIKE, MovieReaction.Kind.DISLIKE}:
            return Response({"detail": "kind must be like or dislike."}, status=400)
        MovieReaction.objects.update_or_create(user=request.user, movie=movie, defaults={"kind": kind})
        return Response({"kind": kind})

    @action(detail=True, methods=["post", "delete"], permission_classes=[permissions.IsAuthenticated])
    def bookmark(self, request, slug=None):
        movie = self.get_object()
        if request.method == "DELETE":
            Bookmark.objects.filter(user=request.user, movie=movie).delete()
            return Response(status=204)
        Bookmark.objects.get_or_create(user=request.user, movie=movie)
        return Response({"bookmarked": True})

    @action(detail=True, methods=["post"], permission_classes=[permissions.IsAuthenticated])
    def watch(self, request, slug=None):
        movie = self.get_object()
        progress = int(request.data.get("progress_seconds") or 0)
        completed = bool(request.data.get("completed")) or progress >= movie.runtime * 60 * 0.9
        item, _ = WatchHistory.objects.update_or_create(
            user=request.user,
            movie=movie,
            defaults={"progress_seconds": progress, "completed": completed},
        )
        refresh_user_taste_profile.delay(str(request.user.id))
        return Response(WatchHistorySerializer(item, context={"request": request}).data)


class WatchlistViewSet(viewsets.ModelViewSet):
    serializer_class = WatchlistSerializer

    def get_queryset(self):
        return Watchlist.objects.filter(user=self.request.user).prefetch_related("items__movie__genres")

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=True, methods=["post"])
    def add(self, request, pk=None):
        watchlist = self.get_object()
        movie = Movie.objects.get(id=request.data.get("movie_id"))
        item, _ = WatchlistItem.objects.get_or_create(
            watchlist=watchlist, movie=movie, defaults={"note": request.data.get("note", "")}
        )
        return Response(WatchlistItemSerializer(item, context={"request": request}).data, status=201)

    @action(detail=True, methods=["delete"], url_path="items/(?P<movie_id>[^/.]+)")
    def remove_item(self, request, pk=None, movie_id=None):
        WatchlistItem.objects.filter(watchlist=self.get_object(), movie_id=movie_id).delete()
        return Response(status=204)


@api_view(["GET"])
@permission_classes([permissions.IsAuthenticated])
def my_library(request):
    history = WatchHistory.objects.filter(user=request.user).select_related("movie").prefetch_related("movie__genres")
    ratings = Rating.objects.filter(user=request.user).select_related("movie").prefetch_related("movie__genres")
    bookmarks = Bookmark.objects.filter(user=request.user).select_related("movie").prefetch_related("movie__genres")
    likes = MovieReaction.objects.filter(user=request.user, kind="like").select_related("movie")
    return Response(
        {
            "history": WatchHistorySerializer(history, many=True, context={"request": request}).data,
            "ratings": [
                {"score": float(row.score), "movie": MovieListSerializer(row.movie, context={"request": request}).data}
                for row in ratings
            ],
            "bookmarks": [MovieListSerializer(row.movie, context={"request": request}).data for row in bookmarks],
            "likes": [movie_card(row.movie, request.user) for row in likes],
        }
    )


@api_view(["GET"])
@permission_classes([permissions.AllowAny])
def facets(request):
    return Response(
        {
            "genres": GenreSerializer(Genre.objects.all(), many=True).data,
            "languages": LanguageSerializer(Language.objects.all(), many=True).data,
            "countries": CountrySerializer(Country.objects.all(), many=True).data,
            "people": PersonSerializer(Person.objects.all()[:80], many=True).data,
        }
    )
