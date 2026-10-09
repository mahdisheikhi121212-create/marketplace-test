from django.urls import path

from .views import (
    OrderCreateAPIView,
    OrderListAPIView,
    OrderDetailAPIView,
    OrderStatusUpdateAPIView,
    AdminOrderListAPIView,
    AdminOrderDetailAPIView,
    AdminOrderStatusUpdateAPIView,
)


urlpatterns = [
    path(
        "",
        OrderCreateAPIView.as_view(),
        name="order-create"
    ),

    path(
        "list/",
        OrderListAPIView.as_view(),
        name="order-list"
    ),

    path(
        "admin/",
        AdminOrderListAPIView.as_view(),
        name="admin-order-list"
    ),

    path(
        "admin/<int:pk>/",
        AdminOrderDetailAPIView.as_view(),
        name="admin-order-detail"
    ),

    path(
        "admin/<int:pk>/status/",
        AdminOrderStatusUpdateAPIView.as_view(),
        name="admin-order-status-update"
    ),

    path(
        "<int:pk>/",
        OrderDetailAPIView.as_view(),
        name="order-detail"
    ),

    path(
        "<int:pk>/status/",
        OrderStatusUpdateAPIView.as_view(),
        name="order-status-update"
    ),
]
