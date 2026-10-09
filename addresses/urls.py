from django.urls import path

from .views import (
    AddressListCreateAPIView,
    AddressDetailAPIView,
)


urlpatterns = [
    path(
        "",
        AddressListCreateAPIView.as_view(),
        name="address-list-create",
    ),

    path(
        "<int:pk>/",
        AddressDetailAPIView.as_view(),
        name="address-detail",
    ),
]