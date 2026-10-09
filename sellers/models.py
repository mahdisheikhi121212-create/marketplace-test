from django.db import models
from django.contrib.auth.models import User


class SellerProfile(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="seller_profile"
    )

    phone = models.CharField(
        max_length=20,
        blank=True
    )

    is_verified = models.BooleanField(
        default=False
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        verbose_name = "پروفایل فروشنده"
        verbose_name_plural = "پروفایل‌های فروشندگان"

    def __str__(self):
        return self.user.username