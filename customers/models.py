from django.db import models
from django.contrib.auth.models import User


class CustomerProfile(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="customer_profile",
    )

    phone = models.CharField(
        max_length=20,
        blank=True,
    )

    phone_verified = models.BooleanField(
        default=False,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    class Meta:
        verbose_name = "پروفایل مشتری"
        verbose_name_plural = "پروفایل‌های مشتریان"

        constraints = [
            models.UniqueConstraint(
                fields=[
                    "phone",
                ],
                condition=~models.Q(
                    phone=""
                ),
                name=(
                    "unique_nonempty_customer_phone"
                ),
            ),
        ]

    def __str__(self):
        return self.user.username


class PhoneVerificationOTP(models.Model):
    customer = models.ForeignKey(
        CustomerProfile,
        on_delete=models.CASCADE,
        related_name="phone_otps",
    )

    code_hash = models.CharField(
        max_length=128,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    expires_at = models.DateTimeField()

    attempts = models.PositiveSmallIntegerField(
        default=0,
    )

    is_used = models.BooleanField(
        default=False,
    )

    class Meta:
        ordering = [
            "-created_at",
        ]

    def __str__(self):
        return (
            f"OTP - "
            f"{self.customer.user.username}"
        )