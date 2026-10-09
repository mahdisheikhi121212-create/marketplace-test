from datetime import timedelta

from django.conf import settings
from django.db import transaction
from django.shortcuts import redirect
from django.utils import timezone

from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import (
    PermissionDenied,
    ValidationError,
)
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Payment
from .serializers import PaymentSerializer
from .services import ZarinPalService

from inventory.services import (
    complete_sale,
    ensure_order_reserved,
    release_reserved_stock,
)

from order_history.services import (
    create_order_history,
)

from orders.models import Order

from shipping.models import Shipping


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


@transaction.atomic
def fail_payment_and_release(payment):
    if payment.status != "pending":
        return

    payment.status = "failed"

    payment.save(
        update_fields=[
            "status",
        ]
    )

    release_reserved_stock(
        payment.order
    )


class PaymentCreateAPIView(
    generics.CreateAPIView
):
    serializer_class = PaymentSerializer

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

        submitted_order = (
            serializer.validated_data.get(
                "order"
            )
        )

        if not submitted_order:
            raise ValidationError(
                "سفارش الزامی است."
            )

        with transaction.atomic():

            order = (
                Order.objects
                .select_for_update()
                .get(
                    pk=submitted_order.pk
                )
            )

            if order.customer != customer:
                raise ValidationError(
                    "این سفارش متعلق به شما نیست."
                )

            if order.status != "pending":
                raise ValidationError(
                    "این سفارش قابل پرداخت نیست."
                )

            paid_payment_exists = (
                Payment.objects
                .filter(
                    order=order,
                    status="paid",
                )
                .exists()
            )

            if paid_payment_exists:
                raise ValidationError(
                    "این سفارش قبلاً پرداخت شده است."
                )

            pending_payment = (
                Payment.objects
                .filter(
                    order=order,
                    status="pending",
                )
                .order_by(
                    "-created_at"
                )
                .first()
            )

            if pending_payment:

                is_expired = (
                    pending_payment.expires_at
                    is not None
                    and pending_payment.expires_at
                    <= timezone.now()
                )

                if is_expired:
                    fail_payment_and_release(
                        pending_payment
                    )

                elif pending_payment.authority:
                    serializer.instance = (
                        pending_payment
                    )
                    return

                else:
                    raise ValidationError(
                        (
                            "درخواست پرداخت این سفارش "
                            "در حال پردازش است."
                        )
                    )

            ensure_order_reserved(
                order
            )

            payment = Payment.objects.create(
                order=order,
                amount=order.total_price,
                status="pending",
                expires_at=(
                    timezone.now()
                    + timedelta(
                        minutes=(
                            settings
                            .PAYMENT_EXPIRATION_MINUTES
                        )
                    )
                ),
            )

        zarinpal = ZarinPalService()

        try:
            response_data = (
                zarinpal.request_payment(
                    payment
                )
            )

        except Exception:
            fail_payment_and_release(
                payment
            )

            raise ValidationError(
                (
                    "اتصال به درگاه پرداخت "
                    "انجام نشد."
                )
            )

        data = response_data.get(
            "data",
            {},
        )

        authority = data.get(
            "authority"
        )

        if not authority:
            fail_payment_and_release(
                payment
            )

            raise ValidationError(
                (
                    "شناسه پرداخت از درگاه "
                    "دریافت نشد."
                )
            )

        payment.authority = authority

        payment.save(
            update_fields=[
                "authority",
            ]
        )

        serializer.instance = payment


class PaymentRedirectAPIView(
    APIView
):
    permission_classes = [
        IsAuthenticated,
    ]

    def get(
        self,
        request,
        pk
    ):
        customer = get_customer(
            request.user
        )

        payment = (
            Payment.objects
            .filter(
                id=pk,
                order__customer=customer,
                status="pending",
            )
            .first()
        )

        if not payment:
            raise ValidationError(
                "پرداخت موردنظر پیدا نشد."
            )

        if (
            payment.expires_at is not None
            and payment.expires_at
            <= timezone.now()
        ):
            fail_payment_and_release(
                payment
            )

            raise ValidationError(
                "مهلت پرداخت به پایان رسیده است."
            )

        if not payment.authority:
            raise ValidationError(
                (
                    "شناسه پرداخت درگاه "
                    "وجود ندارد."
                )
            )

        zarinpal = ZarinPalService()

        payment_url = (
            zarinpal.get_payment_url(
                payment.authority
            )
        )

        return Response(
            {
                "payment_id": payment.id,
                "authority": payment.authority,
                "payment_url": payment_url,
            }
        )


class PaymentCallbackAPIView(
    APIView
):
    permission_classes = []

    @transaction.atomic
    def get(
        self,
        request
    ):
        authority = (
            request.query_params.get(
                "Authority"
            )
        )

        status = (
            request.query_params.get(
                "Status"
            )
        )

        if not authority:
            return Response(
                {
                    "detail":
                        "شناسه پرداخت وجود ندارد."
                },
                status=400,
            )

        payment = (
            Payment.objects
            .select_for_update()
            .select_related(
                "order"
            )
            .filter(
                authority=authority
            )
            .first()
        )

        if not payment:
            return Response(
                {
                    "detail":
                        "پرداخت پیدا نشد."
                },
                status=404,
            )

        if payment.status == "paid":
            return redirect(
                f"{settings.FRONTEND_URL}/orders"
            )

        if payment.status != "pending":
            return Response(
                {
                    "detail":
                        (
                            "این پرداخت دیگر "
                            "قابل پردازش نیست."
                        )
                },
                status=400,
            )

        if (
            payment.expires_at is not None
            and payment.expires_at
            <= timezone.now()
        ):
            fail_payment_and_release(
                payment
            )

            return Response(
                {
                    "detail":
                        (
                            "مهلت پرداخت "
                            "به پایان رسیده است."
                        )
                },
                status=400,
            )

        if status != "OK":
            fail_payment_and_release(
                payment
            )

            return Response(
                {
                    "detail":
                        "پرداخت ناموفق بود."
                },
                status=400,
            )

        zarinpal = ZarinPalService()

        try:
            verify_data = (
                zarinpal.verify_payment(
                    payment,
                    authority,
                )
            )

        except Exception:
            fail_payment_and_release(
                payment
            )

            return Response(
                {
                    "detail":
                        (
                            "تأیید پرداخت "
                            "انجام نشد."
                        )
                },
                status=502,
            )

        data = verify_data.get(
            "data",
            {}
        )

        code = data.get(
            "code"
        )

        if code not in [
            100,
            101,
        ]:
            fail_payment_and_release(
                payment
            )

            return Response(
                {
                    "detail":
                        "پرداخت تأیید نشد.",
                    "gateway_code":
                        code,
                },
                status=400,
            )

        order = (
            Order.objects
            .select_for_update()
            .get(
                pk=payment.order_id
            )
        )

        if order.status != "pending":
            return Response(
                {
                    "detail":
                        (
                            "وضعیت سفارش برای "
                            "تکمیل پرداخت معتبر نیست."
                        )
                },
                status=400,
            )

        payment.status = "paid"
        payment.paid_at = timezone.now()

        payment.transaction_id = str(
            data.get(
                "ref_id",
                ""
            )
        )

        payment.save(
            update_fields=[
                "status",
                "paid_at",
                "transaction_id",
            ]
        )

        order.status = "paid"

        order.save(
            update_fields=[
                "status",
            ]
        )

        create_order_history(
            order=order,
            status="paid",
            description=(
                "پرداخت سفارش انجام شد."
            ),
        )

        Shipping.objects.get_or_create(
            order=order,
            defaults={
                "status": "pending"
            },
        )

        complete_sale(
            order
        )

        return redirect(
            f"{settings.FRONTEND_URL}/orders"
        )