from django.db import models
from customers.models import CustomerProfile


class Address(models.Model):
    customer = models.ForeignKey(
        CustomerProfile,
        on_delete=models.CASCADE,
        related_name="addresses"
    )

    title = models.CharField(
        max_length=100,
        default="Home"
    )

    receiver_name = models.CharField(
        max_length=100
    )

    phone = models.CharField(
        max_length=20
    )

    province = models.CharField(
        max_length=100,
        blank=True,
        default=""
    )

    city = models.CharField(
        max_length=100
    )

    address_line = models.TextField()

    postal_code = models.CharField(
        max_length=20
    )

    is_default = models.BooleanField(
        default=False
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        verbose_name = "آدرس"
        verbose_name_plural = "آدرس‌ها"

    def __str__(self):
        return f"{self.customer.user.username} - {self.city}"