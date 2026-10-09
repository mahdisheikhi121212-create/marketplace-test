from rest_framework import serializers

from .models import Product


class ProductSerializer(
    serializers.ModelSerializer
):
    category_name = serializers.CharField(
        source="category.name",
        read_only=True
    )

    category_slug = serializers.CharField(
        source="category.slug",
        read_only=True
    )

    class Meta:
        model = Product

        fields = (
            "id",
            "name",
            "description",
            "price",
            "category",
            "category_name",
            "category_slug",
            "created_at",
        )

        read_only_fields = (
            "id",
            "category_name",
            "category_slug",
            "created_at",
        )


class SellerProductSerializer(
    serializers.ModelSerializer
):
    category_name = serializers.CharField(
        source="category.name",
        read_only=True
    )

    category_slug = serializers.CharField(
        source="category.slug",
        read_only=True
    )

    class Meta:
        model = Product

        fields = (
            "id",
            "name",
            "description",
            "price",
            "category",
            "category_name",
            "category_slug",
            "created_at",
        )

        read_only_fields = (
            "id",
            "category_name",
            "category_slug",
            "created_at",
        )

    def validate_price(
        self,
        value
    ):
        if value <= 0:
            raise serializers.ValidationError(
                "قیمت محصول باید بیشتر از صفر باشد."
            )

        return value