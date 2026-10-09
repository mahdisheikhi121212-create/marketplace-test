from django.contrib import admin

from .models import Order, OrderItem


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        "order_number",
        "customer",
        "status",
        "total_price",
        "shipping_address",
        "created_at",
    )

    list_filter = (
        "status",
        "created_at",
    )

    search_fields = (
        "order_number",
        "customer__user__username",
        "customer__phone",
    )

    ordering = (
        "-created_at",
    )


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = (
        "order",
        "product",
        "quantity",
        "price_at_purchase",
    )

    search_fields = (
        "order__order_number",
        "product__name",
    )