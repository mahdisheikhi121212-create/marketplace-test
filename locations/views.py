from rest_framework import generics
from rest_framework.permissions import AllowAny

from .models import Province, City
from .serializers import ProvinceSerializer, CitySerializer


class ProvinceListAPIView(generics.ListAPIView):
    permission_classes = [AllowAny]

    queryset = Province.objects.filter(
        is_active=True
    )
    serializer_class = ProvinceSerializer


class CityListAPIView(generics.ListAPIView):
    permission_classes = [AllowAny]

    serializer_class = CitySerializer

    def get_queryset(self):
        province_id = self.request.query_params.get("province")

        queryset = City.objects.filter(
            is_active=True
        )

        if province_id:
            queryset = queryset.filter(
                province_id=province_id
            )

        return queryset