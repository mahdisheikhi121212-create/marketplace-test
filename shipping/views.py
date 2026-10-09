from django.db import transaction
from django.utils import timezone

from rest_framework import generics
from rest_framework.permissions import IsAdminUser
from rest_framework.exceptions import ValidationError

from .models import Shipping
from .serializers import ShippingSerializer

from order_history.services import (
    create_order_history,
)


ALLOWED_SHIPPING_TRANSITIONS = {
    "pending": {
        "processing",
        "shipped",
    },
    "processing": {
        "shipped",
    },
    "shipped": {
        "delivered",
    },
    "delivered": {
        "returned",
    },
    "returned": set(),
}


class ShippingListCreateAPIView(
    generics.ListCreateAPIView
):
    serializer_class = ShippingSerializer

    permission_classes = [
        IsAdminUser,
    ]

    queryset = (
        Shipping.objects
        .select_related(
            "order"
        )
        .all()
    )

    def perform_create(
        self,
        serializer
    ):
        order = (
            serializer
            .validated_data
            .get("order")
        )

        if order is None:
            raise ValidationError(
                "سفارش الزامی است."
            )

        if order.status not in {
            "paid",
            "processing",
        }:
            raise ValidationError(
                (
                    "ارسال فقط برای سفارش "
                    "پرداخت‌شده یا در حال پردازش "
                    "قابل ایجاد است."
                )
            )

        if Shipping.objects.filter(
            order=order
        ).exists():
            raise ValidationError(
                (
                    "برای این سفارش قبلاً "
                    "ارسال ثبت شده است."
                )
            )

        serializer.save(
            status="pending"
        )


class ShippingDetailAPIView(
    generics.RetrieveUpdateAPIView
):
    serializer_class = ShippingSerializer

    permission_classes = [
        IsAdminUser,
    ]

    queryset = (
        Shipping.objects
        .select_related(
            "order"
        )
        .all()
    )

    @transaction.atomic
    def perform_update(
        self,
        serializer
    ):
        shipping = serializer.instance

        old_status = shipping.status

        submitted_order = (
            serializer
            .validated_data
            .get(
                "order",
                shipping.order,
            )
        )

        if (
            submitted_order.pk
            != shipping.order_id
        ):
            raise ValidationError(
                (
                    "سفارش یک Shipping موجود "
                    "قابل تغییر نیست."
                )
            )

        new_status = (
            serializer
            .validated_data
            .get(
                "status",
                old_status,
            )
        )

        if new_status != old_status:

            allowed_statuses = (
                ALLOWED_SHIPPING_TRANSITIONS
                .get(
                    old_status,
                    set(),
                )
            )

            if (
                new_status
                not in allowed_statuses
            ):
                raise ValidationError(
                    (
                        "تغییر وضعیت ارسال از "
                        f"{old_status} به "
                        f"{new_status} مجاز نیست."
                    )
                )

        order = shipping.order

        if new_status == "shipped":

            if order.status not in {
                "paid",
                "processing",
                "shipped",
            }:
                raise ValidationError(
                    (
                        "وضعیت فعلی سفارش اجازه "
                        "ارسال آن را نمی‌دهد."
                    )
                )

        if new_status == "delivered":

            if order.status != "shipped":
                raise ValidationError(
                    (
                        "فقط سفارش ارسال‌شده "
                        "می‌تواند تحویل داده شود."
                    )
                )

        if new_status == "returned":

            if order.status != "delivered":
                raise ValidationError(
                    (
                        "فقط سفارش تحویل‌شده "
                        "می‌تواند مرجوع شود."
                    )
                )

        now = timezone.now()

        shipped_at = shipping.shipped_at
        delivered_at = shipping.delivered_at

        if (
            new_status == "shipped"
            and old_status != "shipped"
            and shipped_at is None
        ):
            shipped_at = now

        if (
            new_status == "delivered"
            and old_status != "delivered"
            and delivered_at is None
        ):
            delivered_at = now

        shipping = serializer.save(
            order=shipping.order,
            shipped_at=shipped_at,
            delivered_at=delivered_at,
        )

        if new_status == "shipped":

            if order.status != "shipped":

                order.status = "shipped"

                order.save(
                    update_fields=[
                        "status",
                    ]
                )

            if (
                old_status != "shipped"
                and not order.history.filter(
                    status="shipped"
                ).exists()
            ):
                create_order_history(
                    order=order,
                    status="shipped",
                    description=(
                        "سفارش ارسال شد."
                    ),
                )

        if new_status == "delivered":

            if order.status != "delivered":

                order.status = "delivered"

                order.save(
                    update_fields=[
                        "status",
                    ]
                )

            if (
                old_status != "delivered"
                and not order.history.filter(
                    status="delivered"
                ).exists()
            ):
                create_order_history(
                    order=order,
                    status="delivered",
                    description=(
                        "سفارش تحویل داده شد."
                    ),
                )