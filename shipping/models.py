from django.db import models

from orders.models import Order


class Shipping(models.Model):
    order = models.OneToOneField(
        Order,
        on_delete=models.CASCADE,
        related_name="shipping"
    )

    SHIPPING_STATUS = [
    ("pending", "در انتظار ارسال"),
    ("processing", "در حال آماده‌سازی"),
    ("shipped", "ارسال شده"),
    ("delivered", "تحویل شده"),
    ("returned", "مرجوع شده"),
]

    status = models.CharField(
        max_length=20,
        choices=SHIPPING_STATUS,
        default="pending"
    )

    carrier = models.CharField(
        max_length=100,
        blank=True
    )

    tracking_number = models.CharField(
        max_length=100,
        blank=True
    )

    shipped_at = models.DateTimeField(
        null=True,
        blank=True
    )

    delivered_at = models.DateTimeField(
        null=True,
        blank=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        verbose_name = "ارسال سفارش"
        verbose_name_plural = "ارسال سفارش‌ها"

    def __str__(self):
        return f"Shipping - {self.order.order_number}"