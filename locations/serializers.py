from rest_framework import serializers

from .models import Province, City


class CitySerializer(serializers.ModelSerializer):
    class Meta:
        model = City
        fields = (
            "id",
            "name",
            "slug",
            "province",
        )


class ProvinceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Province
        fields = (
            "id",
            "name",
            "slug",
        )