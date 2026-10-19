from rest_framework import serializers

from accounts.serializers import PublicUserSerializer
from community.models import Comment, Discussion, Review, ReviewReaction, UserList, UserListItem
from movies.serializers import MovieListSerializer


class ReviewSerializer(serializers.ModelSerializer):
    user = PublicUserSerializer(read_only=True)
    movie = MovieListSerializer(read_only=True)
    movie_id = serializers.UUIDField(write_only=True)
    reactions = serializers.SerializerMethodField()

    class Meta:
        model = Review
        fields = (
            "id",
            "user",
            "movie",
            "movie_id",
            "title",
            "body",
            "contains_spoilers",
            "score",
            "helpful_count",
            "reactions",
            "created_at",
            "updated_at",
        )

    def get_reactions(self, obj):
        counts = {}
        for row in obj.reactions.all():
            counts[row.kind] = counts.get(row.kind, 0) + 1
        return counts


class ReviewReactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReviewReaction
        fields = ("id", "kind", "created_at")


class CommentSerializer(serializers.ModelSerializer):
    user = PublicUserSerializer(read_only=True)
    replies = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = ("id", "user", "body", "contains_spoilers", "parent", "replies", "created_at")

    def get_replies(self, obj):
        if obj.parent_id:
            return []
        return CommentSerializer(obj.replies.all(), many=True).data


class DiscussionSerializer(serializers.ModelSerializer):
    user = PublicUserSerializer(read_only=True)
    comments = CommentSerializer(many=True, read_only=True)
    comment_count = serializers.IntegerField(source="comments.count", read_only=True)

    class Meta:
        model = Discussion
        fields = (
            "id",
            "user",
            "movie",
            "title",
            "body",
            "contains_spoilers",
            "is_pinned",
            "comments",
            "comment_count",
            "created_at",
            "updated_at",
        )


class UserListItemSerializer(serializers.ModelSerializer):
    movie = MovieListSerializer(read_only=True)
    movie_id = serializers.UUIDField(write_only=True, required=False)

    class Meta:
        model = UserListItem
        fields = ("id", "movie", "movie_id", "note", "position")


class UserListSerializer(serializers.ModelSerializer):
    user = PublicUserSerializer(read_only=True)
    items = UserListItemSerializer(many=True, read_only=True)

    class Meta:
        model = UserList
        fields = ("id", "user", "title", "slug", "description", "is_public", "cover_url", "items", "created_at", "updated_at")
