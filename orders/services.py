from decimal import Decimal

from django.db import transaction

from rest_framework.exceptions import ValidationError

from cart.models import Cart

from cart.services import (
    validate_cart_for_checkout,
)

from inventory.services import (
    release_reserved_stock,
    reserve_stock,
)

from order_history.services import (
    create_order_history,
)

from orders.models import (
    Order,
    OrderItem,
)

from orders.order_utils import (
    generate_order_number,
)


@transaction.atomic
def create_order_from_cart(
    customer,
    shipping_address,
    idempotency_key,
):
    existing_order = (
        Order.objects
        .select_for_update()
        .filter(
            customer=customer,
            idempotency_key=idempotency_key,
        )
        .first()
    )

    if existing_order:
        return existing_order

    cart, _ = (
        Cart.objects
        .select_for_update()
        .get_or_create(
            customer=customer
        )
    )

    validate_cart_for_checkout(
        cart
    )

    cart_items = list(
        cart.items
        .select_related(
            "product__shop__seller"
        )
        .all()
    )

    shop = (
        cart_items[0]
        .product
        .shop
    )

    total_price = Decimal("0")

    for cart_item in cart_items:
        total_price += (
            cart_item.product.price
            * cart_item.quantity
        )

    order = Order.objects.create(
        customer=customer,
        shop=shop,
        shipping_address=shipping_address,
        order_number=generate_order_number(),
        idempotency_key=idempotency_key,
        status="pending",
        total_price=total_price,
    )

    create_order_history(
        order=order,
        status="created",
        description="سفارش ایجاد شد.",
    )

    for cart_item in cart_items:
        product = cart_item.product
        quantity = cart_item.quantity

        OrderItem.objects.create(
            order=order,
            product=product,
            quantity=quantity,
            price_at_purchase=product.price,
        )

        reserve_stock(
            product=product,
            quantity=quantity,
            reference=order.order_number,
        )

    cart.items.all().delete()

    return order


@transaction.atomic
def cancel_order(order):
    if order.status != "pending":
        raise ValidationError(
            "این سفارش قابل لغو نیست."
        )

    release_reserved_stock(
        order
    )

    order.status = "cancelled"

    order.save(
        update_fields=[
            "status",
        ]
    )

    create_order_history(
        order=order,
        status="cancelled",
        description="سفارش لغو شد.",
    )

    return order