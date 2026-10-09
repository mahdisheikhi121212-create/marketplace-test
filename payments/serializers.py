from rest_framework import serializers

from .models import Payment


class PaymentSerializer(
    serializers.ModelSerializer
):
    class Meta:
        model = Payment

        fields = [
            "id",
            "order",
            "status",
            "amount",
            "transaction_id",
            "authority",
            "created_at",
            "paid_at",
        ]

        read_only_fields = [
            "id",
            "status",
            "amount",
            "transaction_id",
            "authority",
            "created_at",
            "paid_at",
        ]