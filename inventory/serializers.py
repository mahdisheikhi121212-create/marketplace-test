from rest_framework import serializers

from .models import (
    InventoryLocation,
    InventoryStock,
    InventoryTransaction,
)


class InventoryLocationSerializer(
    serializers.ModelSerializer
):
    class Meta:
        model = InventoryLocation
        fields = "__all__"


class InventoryStockSerializer(
    serializers.ModelSerializer
):
    product_name = serializers.CharField(
        source="product.name",
        read_only=True,
    )

    location_name = serializers.CharField(
        source="location.name",
        read_only=True,
    )

    city = serializers.CharField(
        source="location.city",
        read_only=True,
    )

    available_quantity = serializers.IntegerField(
        read_only=True,
    )

    class Meta:
        model = InventoryStock

        fields = [
            "id",
            "product",
            "product_name",
            "location",
            "location_name",
            "city",
            "quantity",
            "reserved_quantity",
            "available_quantity",
            "updated_at",
        ]

        read_only_fields = [
            "reserved_quantity",
            "updated_at",
        ]


class InventoryTransactionSerializer(
    serializers.ModelSerializer
):
    product_name = serializers.CharField(
        source="stock.product.name",
        read_only=True,
    )

    location_name = serializers.CharField(
        source="stock.location.name",
        read_only=True,
    )

    city = serializers.CharField(
        source="stock.location.city",
        read_only=True,
    )

    class Meta:
        model = InventoryTransaction

        fields = [
            "id",
            "stock",
            "product_name",
            "location_name",
            "city",
            "transaction_type",
            "quantity",
            "reference",
            "note",
            "created_at",
        ]