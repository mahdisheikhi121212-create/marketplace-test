from rest_framework import serializers

from .models import Category


class CategorySerializer(serializers.ModelSerializer):
    parent_name = serializers.CharField(
        source="parent.name",
        read_only=True
    )

    parent_slug = serializers.CharField(
        source="parent.slug",
        read_only=True
    )

    class Meta:
        model = Category
        fields = (
            "id",
            "name",
            "slug",
            "description",
            "parent",
            "parent_name",
            "parent_slug",
            "is_active",
            "created_at",
            "updated_at",
        )

        read_only_fields = (
            "id",
            "parent_name",
            "parent_slug",
            "created_at",
            "updated_at",
        )
