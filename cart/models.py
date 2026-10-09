from django.db import models

from customers.models import CustomerProfile
from products.models import Product


class Cart(models.Model):
    customer = models.OneToOneField(
        CustomerProfile,
        on_delete=models.CASCADE,
        related_name="cart",
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        verbose_name = "سبد خرید"
        verbose_name_plural = "سبدهای خرید"

    def __str__(self):
        return (
            f"Cart - "
            f"{self.customer.user.username}"
        )


class CartItem(models.Model):
    cart = models.ForeignKey(
        Cart,
        on_delete=models.CASCADE,
        related_name="items",
    )

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="cart_items",
    )

    quantity = models.PositiveIntegerField(
        default=1
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        verbose_name = "آیتم سبد خرید"
        verbose_name_plural = "آیتم‌های سبد خرید"

        constraints = [
            models.UniqueConstraint(
                fields=[
                    "cart",
                    "product",
                ],
                name="unique_cart_product",
            ),
            models.CheckConstraint(
                condition=models.Q(
                    quantity__gt=0
                ),
                name="cart_item_quantity_gt_zero",
            ),
        ]

    def __str__(self):
        return (
            f"{self.product.name} "
            f"({self.quantity})"
        )