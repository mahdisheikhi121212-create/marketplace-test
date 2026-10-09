from django.contrib import admin

from .models import Shipping


@admin.register(Shipping)
class ShippingAdmin(admin.ModelAdmin):
    list_display = (
        "order",
        "status",
        "carrier",
        "tracking_number",
        "shipped_at",
        "delivered_at",
        "created_at",
    )

    list_filter = (
        "status",
        "created_at",
    )

    search_fields = (
        "order__order_number",
        "tracking_number",
        "carrier",
    )

    ordering = (
        "-created_at",
    )