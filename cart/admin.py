from django.contrib import admin

from .models import Cart, CartItem


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = (
        "customer",
        "created_at",
        "updated_at",
    )

    search_fields = (
        "customer__user__username",
        "customer__phone",
    )

    ordering = (
        "-updated_at",
    )


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = (
        "cart",
        "product",
        "quantity",
        "created_at",
    )

    search_fields = (
        "product__name",
        "cart__customer__user__username",
    )

    ordering = (
        "-created_at",
    )