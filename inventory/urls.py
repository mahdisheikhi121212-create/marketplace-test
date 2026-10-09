from django.urls import path

from .views import (
    InventoryLocationListCreateAPIView,
    InventoryStockListCreateAPIView,
    InventoryStockUpdateAPIView,
    InventoryTransactionListAPIView,
)


urlpatterns = [

    path(
        "locations/",
        InventoryLocationListCreateAPIView
        .as_view(),
    ),

    path(
        "stocks/",
        InventoryStockListCreateAPIView
        .as_view(),
    ),

    path(
        "stocks/<int:pk>/",
        InventoryStockUpdateAPIView
        .as_view(),
    ),

    path(
        "transactions/",
        InventoryTransactionListAPIView
        .as_view(),
    ),

]