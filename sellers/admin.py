from django.contrib import admin

from .models import SellerProfile


@admin.register(SellerProfile)
class SellerProfileAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "phone",
        "is_verified",
        "created_at",
    )

    list_filter = (
        "is_verified",
        "created_at",
    )

    search_fields = (
        "user__username",
        "user__email",
        "phone",
    )

    ordering = (
        "-created_at",
    )