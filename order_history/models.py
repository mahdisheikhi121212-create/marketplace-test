from django.db import models

from orders.models import Order


class OrderHistory(models.Model):
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="history"
    )

    STATUS_CHOICES = [
        ("created", "Created"),
        ("paid", "Paid"),
        ("processing", "Processing"),
        ("shipped", "Shipped"),
        ("delivered", "Delivered"),
        ("cancelled", "Cancelled"),
    ]

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES
    )

    description = models.TextField(
        blank=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        verbose_name = "تاریخچه سفارش"
        verbose_name_plural = "تاریخچه سفارش‌ها"

    def __str__(self):
        return f"{self.order.order_number} - {self.status}"