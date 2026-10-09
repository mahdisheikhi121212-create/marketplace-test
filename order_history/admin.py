from django.contrib import admin

from .models import OrderHistory


@admin.register(OrderHistory)
class OrderHistoryAdmin(admin.ModelAdmin):
    list_display = (
        "order",
        "status",
        "description",
        "created_at",
    )

    list_filter = (
        "status",
        "created_at",
    )

    search_fields = (
        "order__order_number",
        "description",
    )

    ordering = (
        "-created_at",
    )