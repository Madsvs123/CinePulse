from django.urls import path

from . import views

urlpatterns = [
    path("register/", views.register),
    path("login/", views.LoginView.as_view()),
    path("refresh/", views.RefreshView.as_view()),
    path("verify-email/", views.verify_email),
    path("resend-verification/", views.resend_verification),
    path("forgot-password/", views.request_password_reset),
    path("reset-password/", views.reset_password),
    path("me/", views.me),
    path("onboarding/", views.onboard),
    path("privacy/", views.privacy),
    path("notification-preferences/", views.notify_prefs),
    path("users/<str:username>/", views.public_profile),
    path("users/<str:username>/follow/", views.follow_user),
    path("users/<str:username>/unfollow/", views.unfollow_user),
]
