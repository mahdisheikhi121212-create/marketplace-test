from django.urls import path

from .views import (
    ShippingListCreateAPIView,
    ShippingDetailAPIView,
)


urlpatterns = [
    path(
        "",
        ShippingListCreateAPIView.as_view(),
        name="shipping-list-create",
    ),

    path(
        "<int:pk>/",
        ShippingDetailAPIView.as_view(),
        name="shipping-detail",
    ),
]