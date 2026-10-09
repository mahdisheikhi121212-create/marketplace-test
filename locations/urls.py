from django.urls import path

from .views import (
    ProvinceListAPIView,
    CityListAPIView,
)


urlpatterns = [
    path(
        "provinces/",
        ProvinceListAPIView.as_view(),
        name="province-list",
    ),
    path(
        "cities/",
        CityListAPIView.as_view(),
        name="city-list",
    ),
]