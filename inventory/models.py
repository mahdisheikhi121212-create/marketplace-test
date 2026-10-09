from django.db import models
from django.db.models import F, Q

from products.models import Product


class InventoryLocation(models.Model):
    LOCATION_TYPE_CHOICES = [
        (
            "warehouse",
            "انبار",
        ),
        (
            "store",
            "فروشگاه",
        ),
        (
            "hub",
            "مرکز توزیع",
        ),
    ]

    name = models.CharField(
        max_length=200
    )

    city = models.CharField(
        max_length=100
    )

    address = models.TextField(
        blank=True
    )

    location_type = models.CharField(
        max_length=20,
        choices=LOCATION_TYPE_CHOICES,
        default="warehouse",
    )

    is_active = models.BooleanField(
        default=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        verbose_name = "مکان موجودی"
        verbose_name_plural = "مکان‌های موجودی"

    def __str__(self):
        return (
            f"{self.name} - "
            f"{self.city}"
        )


class InventoryStock(models.Model):
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="inventory_stocks",
    )

    location = models.ForeignKey(
        InventoryLocation,
        on_delete=models.CASCADE,
        related_name="stocks",
    )

    quantity = models.PositiveIntegerField(
        default=0
    )

    reserved_quantity = models.PositiveIntegerField(
        default=0
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        verbose_name = "موجودی محصول"
        verbose_name_plural = "موجودی محصولات"

        constraints = [
            models.UniqueConstraint(
                fields=[
                    "product",
                    "location",
                ],
                name="unique_product_location_stock",
            ),
            models.CheckConstraint(
                condition=Q(
                    reserved_quantity__lte=F(
                        "quantity"
                    )
                ),
                name="inventory_reserved_lte_quantity",
            ),
        ]

    def __str__(self):
        return (
            f"{self.product.name} - "
            f"{self.location.city} - "
            f"{self.quantity}"
        )

    @property
    def available_quantity(self):
        return (
            self.quantity
            - self.reserved_quantity
        )


class InventoryTransaction(models.Model):
    TRANSACTION_TYPE_CHOICES = [
        (
            "initial",
            "موجودی اولیه",
        ),
        (
            "purchase",
            "خرید موجودی",
        ),
        (
            "reservation",
            "رزرو موجودی",
        ),
        (
            "release",
            "آزادسازی رزرو",
        ),
        (
            "sale",
            "فروش",
        ),
        (
            "return",
            "مرجوعی",
        ),
        (
            "adjustment",
            "اصلاح موجودی",
        ),
    ]

    stock = models.ForeignKey(
        InventoryStock,
        on_delete=models.PROTECT,
        related_name="transactions",
    )

    transaction_type = models.CharField(
        max_length=20,
        choices=TRANSACTION_TYPE_CHOICES,
    )

    quantity = models.IntegerField()

    reference = models.CharField(
        max_length=200,
        blank=True,
    )

    note = models.TextField(
        blank=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        verbose_name = "تراکنش موجودی"
        verbose_name_plural = "تراکنش‌های موجودی"

        ordering = [
            "-created_at"
        ]

    def __str__(self):
        return (
            f"{self.stock.product.name} - "
            f"{self.transaction_type} - "
            f"{self.quantity}"
        )