from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register("catalog", views.MovieViewSet, basename="movie")
router.register("watchlists", views.WatchlistViewSet, basename="watchlist")

urlpatterns = [
    path("library/", views.my_library),
    path("facets/", views.facets),
    path("", include(router.urls)),
]
