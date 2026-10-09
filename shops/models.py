from django.db import models

from sellers.models import SellerProfile


class Shop(models.Model):
    seller = models.OneToOneField(
        SellerProfile,
        on_delete=models.CASCADE,
        related_name="shop",
    )

    name = models.CharField(
        max_length=200
    )

    description = models.TextField(
        blank=True
    )

    city = models.CharField(
        max_length=100,
        blank=True
    )

    address = models.TextField(
        blank=True
    )

    phone = models.CharField(
        max_length=20,
        blank=True
    )

    is_active = models.BooleanField(
        default=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        verbose_name = "فروشگاه"
        verbose_name_plural = "فروشگاه‌ها"

    def __str__(self):
        return self.name