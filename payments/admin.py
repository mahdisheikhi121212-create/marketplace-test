from django.contrib import admin

from .models import Payment


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = (
        "order",
        "amount",
        "status",
        "transaction_id",
        "created_at",
        "paid_at",
    )

    list_filter = (
        "status",
        "created_at",
    )

    search_fields = (
        "order__order_number",
        "transaction_id",
    )

    ordering = (
        "-created_at",
    )