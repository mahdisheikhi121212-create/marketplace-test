from rest_framework import generics
from rest_framework.permissions import AllowAny
from rest_framework.exceptions import PermissionDenied

from .models import Product
from .serializers import (
    ProductSerializer,
    SellerProductSerializer,
)
from .pagination import ProductPagination
from .permissions import IsVerifiedSeller


def public_products():
    return (
        Product.objects
        .filter(
            shop__is_active=True,
            shop__seller__is_verified=True,
        )
        .select_related(
            "shop",
            "shop__seller",
            "category",
        )
    )


class ProductListAPIView(generics.ListAPIView):
    serializer_class = ProductSerializer
    pagination_class = ProductPagination
    permission_classes = [AllowAny]

    def get_queryset(self):
        queryset = public_products()

        search = self.request.query_params.get("search")
        category_id = self.request.query_params.get("category")
        min_price = self.request.query_params.get("min_price")
        max_price = self.request.query_params.get("max_price")

        if search:
            queryset = queryset.filter(
                name__icontains=search
            )

        if category_id:
            queryset = queryset.filter(
                category_id=category_id
            )

        if min_price:
            queryset = queryset.filter(
                price__gte=min_price
            )

        if max_price:
            queryset = queryset.filter(
                price__lte=max_price
            )

        return queryset


class ProductDetailAPIView(generics.RetrieveAPIView):
    serializer_class = ProductSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        return public_products()


class SellerProductListCreateAPIView(
    generics.ListCreateAPIView
):
    serializer_class = SellerProductSerializer
    permission_classes = [IsVerifiedSeller]

    def get_queryset(self):
        seller = self.request.user.seller_profile

        try:
            shop = seller.shop
        except Exception:
            raise PermissionDenied(
                "فروشگاه برای این فروشنده وجود ندارد."
            )

        return Product.objects.filter(
            shop=shop
        )

    def perform_create(self, serializer):
        seller = self.request.user.seller_profile

        try:
            shop = seller.shop
        except Exception:
            raise PermissionDenied(
                "فروشگاه برای این فروشنده وجود ندارد."
            )

        serializer.save(
            shop=shop
        )


class SellerProductDetailAPIView(
    generics.RetrieveUpdateDestroyAPIView
):
    serializer_class = SellerProductSerializer
    permission_classes = [IsVerifiedSeller]

    def get_queryset(self):
        seller = self.request.user.seller_profile

        try:
            shop = seller.shop
        except Exception:
            raise PermissionDenied(
                "فروشگاه برای این فروشنده وجود ندارد."
            )

        return Product.objects.filter(
            shop=shop
        )