from django.db import models


class Order(models.Model):
    STATUS_CHOICES = [
        (
            "pending",
            "در انتظار پرداخت",
        ),
        (
            "paid",
            "پرداخت شده",
        ),
        (
            "processing",
            "در حال پردازش",
        ),
        (
            "shipped",
            "ارسال شده",
        ),
        (
            "delivered",
            "تحویل شده",
        ),
        (
            "cancelled",
            "لغو شده",
        ),
    ]

    customer = models.ForeignKey(
        "customers.CustomerProfile",
        on_delete=models.PROTECT,
        related_name="orders",
    )

    shop = models.ForeignKey(
        "shops.Shop",
        on_delete=models.PROTECT,
        related_name="orders",
    )

    shipping_address = models.ForeignKey(
        "addresses.Address",
        on_delete=models.PROTECT,
        related_name="orders",
        null=True,
        blank=True,
    )

    order_number = models.CharField(
        max_length=50,
        unique=True,
    )

    idempotency_key = models.UUIDField(
        unique=True,
        null=True,
        blank=True,
        editable=False,
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="pending",
    )

    total_price = models.DecimalField(
        max_digits=14,
        decimal_places=2,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=models.Q(
                    total_price__gt=0
                ),
                name="order_total_price_gt_zero",
            ),
        ]

    def __str__(self):
        return self.order_number


class OrderItem(models.Model):
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="items",
    )

    product = models.ForeignKey(
        "products.Product",
        on_delete=models.PROTECT,
        related_name="order_items",
    )

    quantity = models.PositiveIntegerField()

    price_at_purchase = models.DecimalField(
        max_digits=14,
        decimal_places=2,
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=[
                    "order",
                    "product",
                ],
                name="unique_order_product",
            ),
            models.CheckConstraint(
                condition=models.Q(
                    quantity__gt=0
                ),
                name="order_item_quantity_gt_zero",
            ),
            models.CheckConstraint(
                condition=models.Q(
                    price_at_purchase__gt=0
                ),
                name="order_item_price_gt_zero",
            ),
        ]

    def __str__(self):
        return (
            f"{self.order.order_number} - "
            f"{self.product.name}"
        )