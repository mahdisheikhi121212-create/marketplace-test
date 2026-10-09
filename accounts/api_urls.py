from django.urls import path

from rest_framework_simplejwt.views import TokenRefreshView

from .api_views import (
    LoginAPIView,
    LogoutAPIView,
    MeAPIView,
    ProfileAPIView,
    ChangePasswordAPIView,
)


urlpatterns = [
    path(
        "login/",
        LoginAPIView.as_view(),
        name="login",
    ),
    path(
        "logout/",
        LogoutAPIView.as_view(),
        name="logout",
    ),
    path(
        "me/",
        MeAPIView.as_view(),
        name="me",
    ),
    path(
        "profile/",
        ProfileAPIView.as_view(),
        name="profile",
    ),
    path(
        "change-password/",
        ChangePasswordAPIView.as_view(),
        name="change-password",
    ),
    path(
        "token/refresh/",
        TokenRefreshView.as_view(),
        name="token-refresh",
    ),
]