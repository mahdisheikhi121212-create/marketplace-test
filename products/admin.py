from django.contrib import admin

from .models import Product


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "shop",
        "price",
        "created_at",
    )

    list_filter = (
        "shop",
        "created_at",
    )

    search_fields = (
        "name",
        "description",
        "shop__name",
    )

    ordering = (
        "-created_at",
    )