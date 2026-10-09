from django.db import models

from categories.models import Category
from shops.models import Shop


class Product(models.Model):
    shop = models.ForeignKey(
        Shop,
        on_delete=models.CASCADE,
        related_name="products",
    )

    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name="products",
        null=True,
        blank=True,
    )

    name = models.CharField(
        max_length=200
    )

    description = models.TextField()

    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        verbose_name = "محصول"
        verbose_name_plural = "محصولات"

        constraints = [
            models.CheckConstraint(
                condition=models.Q(
                    price__gt=0
                ),
                name="product_price_gt_zero",
            ),
        ]

    def __str__(self):
        return self.name