from rest_framework import serializers

from .models import Shipping


class ShippingSerializer(
    serializers.ModelSerializer
):

    order_number = serializers.CharField(
        source="order.order_number",
        read_only=True
    )

    class Meta:
        model = Shipping

        fields = (
            "id",
            "order",
            "order_number",
            "status",
            "carrier",
            "tracking_number",
            "shipped_at",
            "delivered_at",
            "created_at",
        )

        read_only_fields = (
            "id",
            "order_number",
            "shipped_at",
            "delivered_at",
            "created_at",
        )