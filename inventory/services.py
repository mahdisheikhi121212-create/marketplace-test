from django.db import models, transaction

from rest_framework.exceptions import ValidationError

from .models import (
    InventoryStock,
    InventoryTransaction,
)


@transaction.atomic
def reserve_stock(
    product,
    quantity,
    reference=""
):
    stocks = (
        InventoryStock.objects
        .select_for_update()
        .filter(
            product=product,
            location__is_active=True,
        )
        .order_by(
            "location_id"
        )
    )

    remaining_quantity = quantity

    for stock in stocks:

        available_quantity = (
            stock.available_quantity
        )

        if available_quantity <= 0:
            continue

        reserve_quantity = min(
            available_quantity,
            remaining_quantity,
        )

        stock.reserved_quantity += (
            reserve_quantity
        )

        stock.save(
            update_fields=[
                "reserved_quantity",
                "updated_at",
            ]
        )

        InventoryTransaction.objects.create(
            stock=stock,
            transaction_type="reservation",
            quantity=reserve_quantity,
            reference=reference,
            note="رزرو موجودی برای سفارش",
        )

        remaining_quantity -= (
            reserve_quantity
        )

        if remaining_quantity == 0:
            break

    if remaining_quantity > 0:
        raise ValidationError(
            "موجودی کافی برای این محصول وجود ندارد."
        )


@transaction.atomic
def complete_sale(
    order
):
    """
    تبدیل فقط Reservationهای متعلق به همین سفارش
    به فروش قطعی، حتی اگر رزرو بین چند Location
    تقسیم شده باشد.
    """

    for item in order.items.all():

        remaining_to_sell = item.quantity

        reservation_stock_ids = (
            InventoryTransaction.objects
            .filter(
                stock__product=item.product,
                transaction_type="reservation",
                reference=order.order_number,
            )
            .values_list(
                "stock_id",
                flat=True,
            )
            .distinct()
        )

        stocks = (
            InventoryStock.objects
            .select_for_update()
            .filter(
                id__in=reservation_stock_ids,
            )
            .order_by(
                "location_id"
            )
        )

        for stock in stocks:

            if remaining_to_sell <= 0:
                break

            reserved_quantity = (
                InventoryTransaction.objects
                .filter(
                    stock=stock,
                    transaction_type="reservation",
                    reference=order.order_number,
                )
                .aggregate(
                    total=models.Sum("quantity")
                )["total"]
                or 0
            )

            sold_quantity = (
                InventoryTransaction.objects
                .filter(
                    stock=stock,
                    transaction_type="sale",
                    reference=order.order_number,
                )
                .aggregate(
                    total=models.Sum("quantity")
                )["total"]
                or 0
            )

            released_quantity = (
                InventoryTransaction.objects
                .filter(
                    stock=stock,
                    transaction_type="release",
                    reference=order.order_number,
                )
                .aggregate(
                    total=models.Sum("quantity")
                )["total"]
                or 0
            )

            own_remaining_reservation = (
                reserved_quantity
                - sold_quantity
                - released_quantity
            )

            if own_remaining_reservation <= 0:
                continue

            sale_quantity = min(
                own_remaining_reservation,
                remaining_to_sell,
            )

            if (
                stock.reserved_quantity
                < sale_quantity
            ):
                raise ValidationError(
                    "مقدار رزرو شده موجودی کافی نیست."
                )

            if stock.quantity < sale_quantity:
                raise ValidationError(
                    "موجودی واقعی محصول کافی نیست."
                )

            stock.quantity -= sale_quantity
            stock.reserved_quantity -= sale_quantity

            stock.save(
                update_fields=[
                    "quantity",
                    "reserved_quantity",
                    "updated_at",
                ]
            )

            InventoryTransaction.objects.create(
                stock=stock,
                transaction_type="sale",
                quantity=sale_quantity,
                reference=order.order_number,
                note=(
                    "تبدیل رزرو موجودی "
                    "به فروش قطعی"
                ),
            )

            remaining_to_sell -= (
                sale_quantity
            )

        if remaining_to_sell > 0:
            raise ValidationError(
                "موجودی رزرو شده کافی نیست."
            )


@transaction.atomic
def release_reserved_stock(
    order
):
    """
    آزادسازی فقط Reservationهای متعلق
    به همین سفارش.

    Location می‌تواند بعد از ایجاد رزرو
    غیرفعال شده باشد؛ غیرفعال بودن Location
    نباید مانع آزادسازی یک رزرو موجود شود.
    """

    for item in order.items.all():

        remaining_to_release = item.quantity

        reservation_stock_ids = (
            InventoryTransaction.objects
            .filter(
                stock__product=item.product,
                transaction_type="reservation",
                reference=order.order_number,
            )
            .values_list(
                "stock_id",
                flat=True,
            )
            .distinct()
        )

        stocks = (
            InventoryStock.objects
            .select_for_update()
            .filter(
                id__in=reservation_stock_ids,
            )
            .order_by(
                "location_id"
            )
        )

        for stock in stocks:

            if remaining_to_release <= 0:
                break

            reserved_quantity = (
                InventoryTransaction.objects
                .filter(
                    stock=stock,
                    transaction_type="reservation",
                    reference=order.order_number,
                )
                .aggregate(
                    total=models.Sum("quantity")
                )["total"]
                or 0
            )

            released_quantity = (
                InventoryTransaction.objects
                .filter(
                    stock=stock,
                    transaction_type="release",
                    reference=order.order_number,
                )
                .aggregate(
                    total=models.Sum("quantity")
                )["total"]
                or 0
            )

            sold_quantity = (
                InventoryTransaction.objects
                .filter(
                    stock=stock,
                    transaction_type="sale",
                    reference=order.order_number,
                )
                .aggregate(
                    total=models.Sum("quantity")
                )["total"]
                or 0
            )

            own_remaining_reservation = (
                reserved_quantity
                - released_quantity
                - sold_quantity
            )

            if own_remaining_reservation <= 0:
                continue

            release_quantity = min(
                own_remaining_reservation,
                remaining_to_release,
            )

            if (
                stock.reserved_quantity
                < release_quantity
            ):
                raise ValidationError(
                    "مقدار رزرو شده موجودی کافی نیست."
                )

            stock.reserved_quantity -= (
                release_quantity
            )

            stock.save(
                update_fields=[
                    "reserved_quantity",
                    "updated_at",
                ]
            )

            InventoryTransaction.objects.create(
                stock=stock,
                transaction_type="release",
                quantity=release_quantity,
                reference=order.order_number,
                note="آزادسازی رزرو سفارش",
            )

            remaining_to_release -= (
                release_quantity
            )


@transaction.atomic
def ensure_order_reserved(
    order
):
    """
    اطمینان از اینکه موجودی موردنیاز سفارش
    در حال حاضر واقعاً رزرو شده است.

    در Retry پرداخت، اگر Reservation قبلی
    به دلیل failed یا expired آزاد شده باشد،
    فقط مقدار کسری دوباره رزرو می‌شود.
    """

    for item in order.items.all():

        reserved_quantity = (
            InventoryTransaction.objects
            .filter(
                stock__product=item.product,
                transaction_type="reservation",
                reference=order.order_number,
            )
            .aggregate(
                total=models.Sum("quantity")
            )["total"]
            or 0
        )

        released_quantity = (
            InventoryTransaction.objects
            .filter(
                stock__product=item.product,
                transaction_type="release",
                reference=order.order_number,
            )
            .aggregate(
                total=models.Sum("quantity")
            )["total"]
            or 0
        )

        sold_quantity = (
            InventoryTransaction.objects
            .filter(
                stock__product=item.product,
                transaction_type="sale",
                reference=order.order_number,
            )
            .aggregate(
                total=models.Sum("quantity")
            )["total"]
            or 0
        )

        remaining_reservation = (
            reserved_quantity
            - released_quantity
            - sold_quantity
        )

        if remaining_reservation < 0:
            raise ValidationError(
                "وضعیت رزرو موجودی سفارش ناسازگار است."
            )

        if remaining_reservation > item.quantity:
            raise ValidationError(
                (
                    "مقدار رزرو موجودی سفارش "
                    "بیش از مقدار موردنیاز است."
                )
            )

        missing_quantity = (
            item.quantity
            - remaining_reservation
        )

        if missing_quantity <= 0:
            continue

        reserve_stock(
            product=item.product,
            quantity=missing_quantity,
            reference=order.order_number,
        )