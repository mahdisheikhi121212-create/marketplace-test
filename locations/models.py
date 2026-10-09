from django.db import models


class Province(models.Model):
    name = models.CharField(
        max_length=100,
        unique=True,
        verbose_name="استان"
    )

    slug = models.SlugField(
        max_length=100,
        unique=True,
        verbose_name="شناسه"
    )

    is_active = models.BooleanField(
        default=True,
        verbose_name="فعال"
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        verbose_name = "استان"
        verbose_name_plural = "استان‌ها"
        ordering = ["name"]

    def __str__(self):
        return self.name


class City(models.Model):
    province = models.ForeignKey(
        Province,
        on_delete=models.CASCADE,
        related_name="cities",
        verbose_name="استان"
    )

    name = models.CharField(
        max_length=100,
        verbose_name="شهر"
    )

    slug = models.SlugField(
        max_length=100,
        verbose_name="شناسه"
    )

    is_active = models.BooleanField(
        default=True,
        verbose_name="فعال"
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        verbose_name = "شهر"
        verbose_name_plural = "شهرها"
        ordering = ["name"]

        constraints = [
            models.UniqueConstraint(
                fields=["province", "name"],
                name="unique_city_per_province"
            )
        ]

    def __str__(self):
        return f"{self.name} - {self.province.name}"