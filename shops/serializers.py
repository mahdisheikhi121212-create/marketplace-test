from rest_framework import serializers

from .models import Shop


class ShopSerializer(serializers.ModelSerializer):

    class Meta:
        model = Shop

        fields = (
            "id",
            "name",
            "description",
            "city",
            "address",
            "phone",
            "is_active",
            "created_at",
        )

        read_only_fields = (
            "id",
            "is_active",
            "created_at",
        )