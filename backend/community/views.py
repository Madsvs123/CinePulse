from django.db.models import Q
from rest_framework import permissions, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from common.permissions import IsOwnerOrReadOnly
from community.models import Comment, Discussion, Review, ReviewReaction, UserList, UserListItem
from community.serializers import (
    CommentSerializer,
    DiscussionSerializer,
    ReviewSerializer,
    UserListItemSerializer,
    UserListSerializer,
)
from movies.models import Movie
from notifications.services import notify


class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly)
    filterset_fields = ("movie__slug", "contains_spoilers")
    ordering_fields = ("created_at", "score", "helpful_count")

    def get_queryset(self):
        return Review.objects.select_related("user", "user__profile", "movie").prefetch_related("reactions", "movie__genres")

    def perform_create(self, serializer):
        movie = Movie.objects.get(id=serializer.validated_data.pop("movie_id"))
        serializer.save(user=self.request.user, movie=movie)

    @action(detail=True, methods=["post"], permission_classes=[permissions.IsAuthenticated])
    def react(self, request, pk=None):
        review = self.get_object()
        kind = request.data.get("kind", ReviewReaction.Kind.HELPFUL)
        ReviewReaction.objects.get_or_create(user=request.user, review=review, kind=kind)
        if kind == ReviewReaction.Kind.HELPFUL:
            review.helpful_count = review.reactions.filter(kind="helpful").count()
            review.save(update_fields=["helpful_count"])
        if review.user != request.user:
            notify(
                review.user,
                "reaction",
                f"{request.user.display_name} reacted to your review",
                f"{kind} on {review.title}",
                {"review_id": str(review.id), "movie": review.movie.slug},
            )
        return Response({"kind": kind})

    @action(detail=True, methods=["get", "post"], permission_classes=[permissions.IsAuthenticatedOrReadOnly])
    def comments(self, request, pk=None):
        review = self.get_object()
        if request.method == "POST":
            comment = Comment.objects.create(
                user=request.user,
                review=review,
                parent_id=request.data.get("parent"),
                body=request.data.get("body", ""),
                contains_spoilers=bool(request.data.get("contains_spoilers")),
            )
            if review.user != request.user:
                notify(
                    review.user,
                    "reply",
                    f"{request.user.display_name} replied to your review",
                    comment.body[:180],
                    {"review_id": str(review.id)},
                )
            return Response(CommentSerializer(comment).data, status=201)
        return Response(CommentSerializer(review.comments.filter(parent__isnull=True), many=True).data)


class DiscussionViewSet(viewsets.ModelViewSet):
    serializer_class = DiscussionSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly)

    def get_queryset(self):
        qs = Discussion.objects.select_related("user", "movie").prefetch_related("comments__user")
        movie = self.request.query_params.get("movie")
        if movie:
            qs = qs.filter(movie__slug=movie)
        return qs

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=True, methods=["post"], permission_classes=[permissions.IsAuthenticated])
    def comments(self, request, pk=None):
        discussion = self.get_object()
        comment = Comment.objects.create(
            user=request.user,
            discussion=discussion,
            parent_id=request.data.get("parent"),
            body=request.data.get("body", ""),
            contains_spoilers=bool(request.data.get("contains_spoilers")),
        )
        if discussion.user != request.user:
            notify(
                discussion.user,
                "reply",
                f"{request.user.display_name} replied in {discussion.title}",
                comment.body[:180],
                {"discussion_id": str(discussion.id)},
            )
        return Response(CommentSerializer(comment).data, status=201)


class UserListViewSet(viewsets.ModelViewSet):
    serializer_class = UserListSerializer
    lookup_field = "slug"
    permission_classes = (permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly)

    def get_queryset(self):
        qs = UserList.objects.select_related("user").prefetch_related("items__movie__genres")
        if not self.request.user.is_authenticated:
            return qs.filter(is_public=True)
        if self.action == "list":
            return qs.filter(Q(is_public=True) | Q(user=self.request.user)).distinct()
        return qs.filter(Q(is_public=True) | Q(user=self.request.user)).distinct()

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=True, methods=["post"], permission_classes=[permissions.IsAuthenticated])
    def add(self, request, slug=None):
        lst = self.get_object()
        if lst.user != request.user:
            return Response({"detail": "Only the owner can edit this list."}, status=403)
        movie = Movie.objects.get(id=request.data.get("movie_id"))
        item, _ = UserListItem.objects.get_or_create(
            list=lst,
            movie=movie,
            defaults={"note": request.data.get("note", ""), "position": lst.items.count()},
        )
        return Response(UserListItemSerializer(item, context={"request": request}).data, status=201)
