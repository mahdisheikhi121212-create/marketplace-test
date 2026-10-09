from decimal import Decimal

from rest_framework.exceptions import ValidationError


def validate_product_for_purchase(product):
    shop = product.shop

    if shop is None:
        raise ValidationError(
            "این محصول به فروشگاه معتبری متصل نیست."
        )

    if not shop.is_active:
        raise ValidationError(
            "فروشگاه این محصول غیرفعال است."
        )

    seller = shop.seller

    if seller is None or not seller.is_verified:
        raise ValidationError(
            "فروشنده این محصول تأیید نشده است."
        )

    if (
        product.price is None
        or product.price <= Decimal("0")
    ):
        raise ValidationError(
            "قیمت محصول باید بیشتر از صفر باشد."
        )

    return shop


def get_available_quantity(product):
    stocks = (
        product.inventory_stocks
        .select_related("location")
        .filter(
            location__is_active=True
        )
    )

    return sum(
        max(
            stock.available_quantity,
            0,
        )
        for stock in stocks
    )


def validate_cart_item_for_purchase(
    cart,
    product,
    quantity,
    current_item=None,
    additive=False,
):
    shop = validate_product_for_purchase(
        product
    )

    if (
        current_item is not None
        and product.id != current_item.product_id
    ):
        raise ValidationError(
            (
                "محصول یک آیتم سبد قابل تغییر نیست؛ "
                "آیتم را حذف و محصول جدید را اضافه کنید."
            )
        )

    other_items = cart.items.all()

    if current_item is not None:
        other_items = other_items.exclude(
            pk=current_item.pk
        )

    if other_items.exclude(
        product__shop_id=shop.id
    ).exists():
        raise ValidationError(
            (
                "در نسخه فعلی، همه محصولات یک سبد خرید "
                "باید متعلق به یک فروشگاه باشند."
            )
        )

    desired_quantity = quantity

    if additive:
        existing_item = (
            cart.items
            .filter(
                product=product
            )
            .first()
        )

        if existing_item is not None:
            desired_quantity += (
                existing_item.quantity
            )

    available_quantity = (
        get_available_quantity(
            product
        )
    )

    if desired_quantity > available_quantity:
        raise ValidationError(
            (
                "موجودی کافی برای این تعداد "
                "از محصول وجود ندارد."
            )
        )


def validate_cart_for_checkout(cart):
    items = list(
        cart.items
        .select_related(
            "product__shop__seller"
        )
        .all()
    )

    if not items:
        raise ValidationError(
            "سبد خرید شما خالی است."
        )

    shop_id = None

    for item in items:
        shop = validate_product_for_purchase(
            item.product
        )

        if shop_id is None:
            shop_id = shop.id

        elif shop.id != shop_id:
            raise ValidationError(
                (
                    "در نسخه فعلی، هر سفارش فقط "
                    "می‌تواند شامل محصولات یک فروشگاه باشد."
                )
            )

    return shop_id