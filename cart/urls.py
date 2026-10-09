from django.urls import path

from .views import (
    CartDetailAPIView,
    CartItemCreateAPIView,
    CartItemUpdateDeleteAPIView,
)


urlpatterns = [
    path(
        "",
        CartDetailAPIView.as_view(),
        name="cart-detail"
    ),

    path(
        "items/",
        CartItemCreateAPIView.as_view(),
        name="cart-item-create"
    ),

    path(
        "items/<int:pk>/",
        CartItemUpdateDeleteAPIView.as_view(),
        name="cart-item-detail"
    ),
]