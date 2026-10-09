from uuid import UUID

from rest_framework import generics

from rest_framework.exceptions import (
    PermissionDenied,
    ValidationError,
)

from rest_framework.permissions import (
    BasePermission,
    IsAuthenticated,
)

from .models import Order

from .serializers import (
    OrderSerializer,
    OrderStatusUpdateSerializer,
)

from .services import (
    cancel_order,
    create_order_from_cart,
)

from order_history.services import (
    create_order_history,
)


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


class OrderCreateAPIView(
    generics.CreateAPIView
):
    serializer_class = OrderSerializer

    permission_classes = [
        IsAuthenticated,
    ]

    def perform_create(
        self,
        serializer
    ):
        customer = get_customer(
            self.request.user
        )

        shipping_address = (
            serializer.validated_data.get(
                "shipping_address"
            )
        )

        if not shipping_address:
            raise ValidationError(
                "آدرس ارسال الزامی است."
            )

        if (
            shipping_address.customer
            != customer
        ):
            raise ValidationError(
                "این آدرس متعلق به شما نیست."
            )

        raw_key = (
            self.request.headers.get(
                "Idempotency-Key"
            )
        )

        if not raw_key:
            raise ValidationError(
                (
                    "شناسه یکتای درخواست سفارش "
                    "ارسال نشده است."
                )
            )

        try:
            idempotency_key = UUID(
                raw_key
            )

        except (
            ValueError,
            TypeError,
        ):
            raise ValidationError(
                (
                    "شناسه یکتای درخواست سفارش "
                    "معتبر نیست."
                )
            )

        order = create_order_from_cart(
            customer=customer,
            shipping_address=shipping_address,
            idempotency_key=idempotency_key,
        )

        serializer.instance = order


class OrderListAPIView(
    generics.ListAPIView
):
    serializer_class = OrderSerializer

    permission_classes = [
        IsAuthenticated,
    ]

    def get_queryset(self):
        customer = get_customer(
            self.request.user
        )

        return (
            Order.objects
            .filter(
                customer=customer
            )
            .prefetch_related(
                "items",
                "history",
            )
            .select_related(
                "shipping_address",
                "shop",
            )
            .order_by(
                "-created_at"
            )
        )


class OrderDetailAPIView(
    generics.RetrieveAPIView
):
    serializer_class = OrderSerializer

    permission_classes = [
        IsAuthenticated,
    ]

    def get_queryset(self):
        customer = get_customer(
            self.request.user
        )

        return (
            Order.objects
            .filter(
                customer=customer
            )
            .prefetch_related(
                "items",
                "history",
            )
            .select_related(
                "shipping_address",
                "shop",
            )
        )


class OrderStatusUpdateAPIView(
    generics.UpdateAPIView
):
    serializer_class = (
        OrderStatusUpdateSerializer
    )

    permission_classes = [
        IsAuthenticated,
    ]

    def get_queryset(self):
        customer = get_customer(
            self.request.user
        )

        return Order.objects.filter(
            customer=customer
        )

    def perform_update(
        self,
        serializer
    ):
        order = serializer.instance

        new_status = (
            serializer.validated_data.get(
                "status"
            )
        )

        if new_status != "cancelled":
            raise ValidationError(
                (
                    "مشتری فقط می‌تواند سفارش "
                    "در انتظار پرداخت را لغو کند."
                )
            )

        cancel_order(
            order
        )

        serializer.instance = order


class IsStaffUser(
    BasePermission
):
    def has_permission(
        self,
        request,
        view
    ):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.is_staff
        )


class AdminOrderListAPIView(
    generics.ListAPIView
):
    serializer_class = OrderSerializer

    permission_classes = [
        IsStaffUser,
    ]

    def get_queryset(self):
        return (
            Order.objects
            .all()
            .prefetch_related(
                "items",
                "history",
            )
            .select_related(
                "customer",
                "shipping_address",
                "shop",
            )
            .order_by(
                "-created_at"
            )
        )


class AdminOrderDetailAPIView(
    generics.RetrieveAPIView
):
    serializer_class = OrderSerializer

    permission_classes = [
        IsStaffUser,
    ]

    queryset = (
        Order.objects.all()
    )


class AdminOrderStatusUpdateAPIView(
    generics.UpdateAPIView
):
    serializer_class = (
        OrderStatusUpdateSerializer
    )

    permission_classes = [
        IsStaffUser,
    ]

    queryset = (
        Order.objects.all()
    )

    def perform_update(
        self,
        serializer
    ):
        order = serializer.instance

        new_status = (
            serializer.validated_data.get(
                "status"
            )
        )

        if new_status == "cancelled":
            cancel_order(
                order
            )

            serializer.instance = order
            return

        if new_status == "processing":

            if order.status != "paid":
                raise ValidationError(
                    (
                        "فقط سفارش پرداخت‌شده "
                        "می‌تواند وارد مرحله پردازش شود."
                    )
                )

            order.status = "processing"

            order.save(
                update_fields=[
                    "status",
                ]
            )

            create_order_history(
                order=order,
                status="processing",
                description=(
                    "سفارش وارد مرحله پردازش شد."
                ),
            )

            serializer.instance = order
            return

        raise ValidationError(
            (
                "این تغییر وضعیت از مسیر مدیریت "
                "سفارش مجاز نیست. وضعیت paid فقط "
                "از مسیر پرداخت و وضعیت‌های shipped "
                "و delivered فقط از مسیر ارسال "
                "تغییر می‌کنند."
            )
        )