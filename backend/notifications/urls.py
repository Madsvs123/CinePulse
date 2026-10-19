from django.urls import path

from . import views

urlpatterns = [
    path("", views.inbox),
    path("read/", views.read_all),
    path("<uuid:pk>/read/", views.read_one),
]
