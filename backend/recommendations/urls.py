from django.urls import path

from . import views

urlpatterns = [
    path("home/", views.home_feed),
    path("top-picks/", views.top_picks),
    path("taste/", views.taste),
    path("history/", views.history),
    path("track/", views.track),
    path("similar/<slug:slug>/", views.similar),
    path("weights/", views.weights),
    path("rebuild/", views.rebuild),
]
