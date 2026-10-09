from django.contrib import admin

from .models import Shop


@admin.register(Shop)
class ShopAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "seller",
        "city",
        "is_active",
        "created_at",
    )

    list_filter = (
        "is_active",
        "city",
        "created_at",
    )

    search_fields = (
        "name",
        "seller__user__username",
        "phone",
        "city",
    )

    ordering = (
        "-created_at",
    )