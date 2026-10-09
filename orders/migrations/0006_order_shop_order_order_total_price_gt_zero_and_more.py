import django.db.models.deletion

from django.db import migrations, models


def backfill_order_shop(apps, schema_editor):
    Order = apps.get_model(
        "orders",
        "Order",
    )

    OrderItem = apps.get_model(
        "orders",
        "OrderItem",
    )

    for order in Order.objects.all():
        shop_ids = list(
            OrderItem.objects
            .filter(order_id=order.id)
            .values_list(
                "product__shop_id",
                flat=True,
            )
            .distinct()
        )

        shop_ids = [
            shop_id
            for shop_id in shop_ids
            if shop_id is not None
        ]

        if len(shop_ids) != 1:
            raise RuntimeError(
                (
                    f"Order {order.id} cannot be "
                    f"safely assigned to one shop. "
                    f"Detected shops: {shop_ids}"
                )
            )

        order.shop_id = shop_ids[0]

        order.save(
            update_fields=[
                "shop",
            ]
        )


def reverse_order_shop(apps, schema_editor):
    Order = apps.get_model(
        "orders",
        "Order",
    )

    Order.objects.update(
        shop=None
    )


class Migration(migrations.Migration):

    dependencies = [
        (
            "addresses",
            "0003_address_province_address_updated_at",
        ),
        (
            "customers",
            "0004_phoneverificationotp",
        ),
        (
            "orders",
            "0005_order_idempotency_key",
        ),
        (
            "products",
            "0004_product_category",
        ),
        (
            "shops",
            "0004_alter_shop_options",
        ),
    ]

    operations = [
        migrations.AddField(
            model_name="order",
            name="shop",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=(
                    django.db.models.deletion.PROTECT
                ),
                related_name="orders",
                to="shops.shop",
            ),
        ),

        migrations.RunPython(
            backfill_order_shop,
            reverse_order_shop,
        ),

        migrations.AddConstraint(
            model_name="order",
            constraint=models.CheckConstraint(
                condition=models.Q(
                    ("total_price__gt", 0)
                ),
                name=(
                    "order_total_price_gt_zero"
                ),
            ),
        ),

        migrations.AddConstraint(
            model_name="orderitem",
            constraint=models.UniqueConstraint(
                fields=(
                    "order",
                    "product",
                ),
                name="unique_order_product",
            ),
        ),

        migrations.AddConstraint(
            model_name="orderitem",
            constraint=models.CheckConstraint(
                condition=models.Q(
                    ("quantity__gt", 0)
                ),
                name=(
                    "order_item_quantity_gt_zero"
                ),
            ),
        ),

        migrations.AddConstraint(
            model_name="orderitem",
            constraint=models.CheckConstraint(
                condition=models.Q(
                    (
                        "price_at_purchase__gt",
                        0,
                    )
                ),
                name=(
                    "order_item_price_gt_zero"
                ),
            ),
        ),
    ]