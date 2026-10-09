from rest_framework import generics
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated

from .models import Shop
from .serializers import ShopSerializer


class SellerShopAPIView(
    generics.RetrieveUpdateAPIView
):
    serializer_class = ShopSerializer
    permission_classes = [
        IsAuthenticated,
    ]

    def get_object(self):
        seller = getattr(
            self.request.user,
            "seller_profile",
            None,
        )

        if seller is None:
            raise PermissionDenied(
                "این بخش فقط برای فروشندگان قابل دسترسی است."
            )

        try:
            return Shop.objects.get(
                seller=seller
            )

        except Shop.DoesNotExist:
            raise PermissionDenied(
                "فروشگاهی برای این فروشنده وجود ندارد."
            )