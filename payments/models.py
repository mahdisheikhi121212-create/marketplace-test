from django.db import models

from orders.models import Order


class Payment(models.Model):
    PAYMENT_STATUS = [
        ("pending", "در انتظار پرداخت"),
        ("paid", "پرداخت موفق"),
        ("failed", "پرداخت ناموفق"),
        ("cancelled", "لغو شده"),
    ]

    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="payments",
    )

    status = models.CharField(
        max_length=20,
        choices=PAYMENT_STATUS,
        default="pending",
    )

    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
    )

    transaction_id = models.CharField(
        max_length=100,
        blank=True,
    )

    authority = models.CharField(
        max_length=100,
        blank=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    expires_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    paid_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    class Meta:
        verbose_name = "پرداخت"
        verbose_name_plural = "پرداخت‌ها"

        constraints = [
            models.UniqueConstraint(
                fields=[
                    "order",
                ],
                condition=models.Q(
                    status="pending"
                ),
                name="unique_pending_payment_per_order",
            ),
            models.UniqueConstraint(
                fields=[
                    "order",
                ],
                condition=models.Q(
                    status="paid"
                ),
                name="unique_paid_payment_per_order",
            ),
        ]

    def __str__(self):
        return (
            f"Payment #{self.id} - "
            f"{self.order.order_number}"
        )