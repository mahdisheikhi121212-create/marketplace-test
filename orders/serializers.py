from rest_framework import serializers

from .models import (
    Order,
    OrderItem,
)

from order_history.models import (
    OrderHistory,
)

from addresses.serializers import (
    AddressSerializer,
)

from shipping.serializers import (
    ShippingSerializer,
)


class OrderItemSerializer(
    serializers.ModelSerializer
):
    product_name = serializers.CharField(
        source="product.name",
        read_only=True
    )

    class Meta:
        model = OrderItem

        fields = (
            "id",
            "product",
            "product_name",
            "quantity",
            "price_at_purchase",
        )

        read_only_fields = (
            "id",
            "product_name",
            "price_at_purchase",
        )


class OrderHistorySerializer(
    serializers.ModelSerializer
):
    class Meta:
        model = OrderHistory

        fields = (
            "id",
            "status",
            "description",
            "created_at",
        )

        read_only_fields = (
            "id",
            "status",
            "description",
            "created_at",
        )


class OrderSerializer(
    serializers.ModelSerializer
):
    customer_name = serializers.CharField(
        source="customer.user.username",
        read_only=True
    )

    items = OrderItemSerializer(
        many=True,
        read_only=True
    )

    history = OrderHistorySerializer(
        many=True,
        read_only=True
    )

    shipping_address = AddressSerializer(
        read_only=True
    )

    shipping = ShippingSerializer(
        read_only=True
    )

    shipping_address_id = serializers.PrimaryKeyRelatedField(
        source="shipping_address",
        queryset=__import__(
            "addresses.models",
            fromlist=["Address"]
        ).Address.objects.all(),
        write_only=True,
        required=False,
        allow_null=True,
    )

    class Meta:
        model = Order

        fields = (
            "id",
            "order_number",
            "customer_name",
            "shipping_address",
            "shipping_address_id",
            "status",
            "total_price",
            "items",
            "history",
            "shipping",
            "created_at",
        )

        read_only_fields = (
            "id",
            "order_number",
            "customer_name",
            "shipping_address",
            "status",
            "total_price",
            "items",
            "history",
            "shipping",
            "created_at",
        )


class OrderStatusUpdateSerializer(
    serializers.ModelSerializer
):
    class Meta:
        model = Order

        fields = (
            "status",
        )
