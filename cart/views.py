from rest_framework import generics
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import (
    IsAuthenticated,
)

from .models import (
    Cart,
    CartItem,
)

from .serializers import (
    CartSerializer,
    CartItemSerializer,
)

from .services import (
    validate_cart_item_for_purchase,
)


def get_customer(user):
    customer = getattr(
        user,
        "customer_profile",
        None,
    )

    if customer is None:
        raise PermissionDenied(
            "این بخش فقط برای مشتریان قابل دسترسی است."
        )

    return customer


class CartDetailAPIView(
    generics.RetrieveAPIView
):
    serializer_class = CartSerializer

    permission_classes = [
        IsAuthenticated,
    ]

    def get_object(self):
        customer = get_customer(
            self.request.user
        )

        cart, created = (
            Cart.objects.get_or_create(
                customer=customer
            )
        )

        return cart


class CartItemCreateAPIView(
    generics.CreateAPIView
):
    serializer_class = CartItemSerializer

    permission_classes = [
        IsAuthenticated,
    ]

    def perform_create(
        self,
        serializer
    ):
        customer = get_customer(
            self.request.user
        )

        cart, created = (
            Cart.objects.get_or_create(
                customer=customer
            )
        )

        product = (
            serializer.validated_data[
                "product"
            ]
        )

        quantity = (
            serializer.validated_data.get(
                "quantity",
                1
            )
        )

        validate_cart_item_for_purchase(
            cart=cart,
            product=product,
            quantity=quantity,
            additive=True,
        )

        cart_item, item_created = (
            CartItem.objects.get_or_create(
                cart=cart,
                product=product,
                defaults={
                    "quantity": quantity
                }
            )
        )

        if not item_created:
            cart_item.quantity += quantity

            cart_item.save(
                update_fields=[
                    "quantity"
                ]
            )

        serializer.instance = cart_item


class CartItemUpdateDeleteAPIView(
    generics.RetrieveUpdateDestroyAPIView
):
    serializer_class = CartItemSerializer

    permission_classes = [
        IsAuthenticated,
    ]

    def get_queryset(self):
        customer = get_customer(
            self.request.user
        )

        return CartItem.objects.filter(
            cart__customer=customer
        )

    def perform_update(
        self,
        serializer
    ):
        cart_item = serializer.instance

        product = (
            serializer.validated_data.get(
                "product",
                cart_item.product,
            )
        )

        quantity = (
            serializer.validated_data.get(
                "quantity",
                cart_item.quantity,
            )
        )

        validate_cart_item_for_purchase(
            cart=cart_item.cart,
            product=product,
            quantity=quantity,
            current_item=cart_item,
            additive=False,
        )

        serializer.save()