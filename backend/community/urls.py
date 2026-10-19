from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register("reviews", views.ReviewViewSet, basename="review")
router.register("discussions", views.DiscussionViewSet, basename="discussion")
router.register("lists", views.UserListViewSet, basename="user-list")

urlpatterns = [path("", include(router.urls))]
