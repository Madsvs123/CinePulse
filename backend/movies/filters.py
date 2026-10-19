from django.db.models import Q
from django_filters import rest_framework as filters

from movies.models import Movie


class MovieFilter(filters.FilterSet):
    genre = filters.CharFilter(method="filter_genres")
    genre_all = filters.CharFilter(method="filter_genres_all")
    language = filters.CharFilter(field_name="languages__code")
    country = filters.CharFilter(field_name="countries__code")
    year_min = filters.NumberFilter(field_name="release_date", lookup_expr="year__gte")
    year_max = filters.NumberFilter(field_name="release_date", lookup_expr="year__lte")
    rating_min = filters.NumberFilter(field_name="vote_average", lookup_expr="gte")
    rating_max = filters.NumberFilter(field_name="vote_average", lookup_expr="lte")
    runtime_min = filters.NumberFilter(field_name="runtime", lookup_expr="gte")
    runtime_max = filters.NumberFilter(field_name="runtime", lookup_expr="lte")
    age_rating = filters.CharFilter(field_name="age_rating")
    hidden_gems = filters.BooleanFilter(field_name="is_hidden_gem")
    provider = filters.CharFilter(field_name="availability__provider__slug")
    cast = filters.CharFilter(method="filter_cast")
    director = filters.CharFilter(method="filter_director")
    keyword = filters.CharFilter(field_name="keywords__slug")
    company = filters.CharFilter(field_name="companies__slug")

    class Meta:
        model = Movie
        fields = []

    def filter_genres(self, queryset, name, value):
        slugs = [item.strip() for item in value.split(",") if item.strip()]
        return queryset.filter(genres__slug__in=slugs).distinct()

    def filter_genres_all(self, queryset, name, value):
        slugs = [item.strip() for item in value.split(",") if item.strip()]
        for slug in slugs:
            queryset = queryset.filter(genres__slug=slug)
        return queryset.distinct()

    def filter_cast(self, queryset, name, value):
        return queryset.filter(
            Q(cast_credits__person__name__icontains=value) | Q(cast_credits__person__slug__icontains=value)
        ).distinct()

    def filter_director(self, queryset, name, value):
        return queryset.filter(Q(directors__name__icontains=value) | Q(directors__slug__icontains=value)).distinct()
