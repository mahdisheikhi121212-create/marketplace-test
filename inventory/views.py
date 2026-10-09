from rest_framework import generics

from rest_framework.permissions import (
    IsAdminUser,
)

from .models import (
    InventoryLocation,
    InventoryStock,
    InventoryTransaction,
)

from .serializers import (
    InventoryLocationSerializer,
    InventoryStockSerializer,
    InventoryTransactionSerializer,
)


class InventoryLocationListCreateAPIView(
    generics.ListCreateAPIView
):
    queryset = (
        InventoryLocation.objects
        .all()
        .order_by(
            "-created_at"
        )
    )

    serializer_class = (
        InventoryLocationSerializer
    )

    permission_classes = [
        IsAdminUser,
    ]


class InventoryStockListCreateAPIView(
    generics.ListCreateAPIView
):
    queryset = (
        InventoryStock.objects
        .select_related(
            "product",
            "location",
        )
        .order_by(
            "-updated_at"
        )
    )

    serializer_class = (
        InventoryStockSerializer
    )

    permission_classes = [
        IsAdminUser,
    ]


class InventoryStockUpdateAPIView(
    generics.UpdateAPIView
):
    queryset = (
        InventoryStock.objects
        .select_related(
            "product",
            "location",
        )
    )

    serializer_class = (
        InventoryStockSerializer
    )

    permission_classes = [
        IsAdminUser,
    ]


class InventoryTransactionListAPIView(
    generics.ListAPIView
):
    queryset = (
        InventoryTransaction.objects
        .select_related(
            "stock__product",
            "stock__location",
        )
        .order_by(
            "-created_at"
        )
    )

    serializer_class = (
        InventoryTransactionSerializer
    )

    permission_classes = [
        IsAdminUser,
    ]