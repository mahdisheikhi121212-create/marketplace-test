from django.urls import path

from .api_views import (
    ProductListAPIView,
    ProductDetailAPIView,
    SellerProductListCreateAPIView,
    SellerProductDetailAPIView,
)


urlpatterns = [
    path(
        "",
        ProductListAPIView.as_view(),
        name="product-list-api"
    ),

    path(
        "seller/",
        SellerProductListCreateAPIView.as_view(),
        name="seller-product-list-create-api"
    ),

    path(
        "seller/<int:pk>/",
        SellerProductDetailAPIView.as_view(),
        name="seller-product-detail-api"
    ),

    path(
        "<int:pk>/",
        ProductDetailAPIView.as_view(),
        name="product-detail-api"
    ),
]