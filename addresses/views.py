from rest_framework import generics
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated

from .models import Address
from .serializers import AddressSerializer


def get_customer(user):
    customer = getattr(
        user,
        "customer_profile",
        None,
    )

    if customer is None:
        raise PermissionDenied(
            "این بخش فقط برای مشتریان قابل دسترسی است."
        )

    return customer


class AddressListCreateAPIView(
    generics.ListCreateAPIView
):
    serializer_class = AddressSerializer
    permission_classes = [
        IsAuthenticated,
    ]

    def get_queryset(self):
        customer = get_customer(
            self.request.user
        )

        return Address.objects.filter(
            customer=customer
        )

    def perform_create(
        self,
        serializer
    ):
        customer = get_customer(
            self.request.user
        )

        address = serializer.save(
            customer=customer
        )

        if address.is_default:
            (
                Address.objects
                .filter(
                    customer=customer
                )
                .exclude(
                    id=address.id
                )
                .update(
                    is_default=False
                )
            )


class AddressDetailAPIView(
    generics.RetrieveUpdateDestroyAPIView
):
    serializer_class = AddressSerializer
    permission_classes = [
        IsAuthenticated,
    ]

    def get_queryset(self):
        customer = get_customer(
            self.request.user
        )

        return Address.objects.filter(
            customer=customer
        )

    def perform_update(
        self,
        serializer
    ):
        customer = get_customer(
            self.request.user
        )

        address = serializer.save()

        if address.is_default:
            (
                Address.objects
                .filter(
                    customer=customer
                )
                .exclude(
                    id=address.id
                )
                .update(
                    is_default=False
                )
            )