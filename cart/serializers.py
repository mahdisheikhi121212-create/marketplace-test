from rest_framework import serializers

from .models import Cart, CartItem
from products.models import Product


class ProductInCartSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = (
            "id",
            "name",
            "price",
        )


class CartItemSerializer(serializers.ModelSerializer):
    product = ProductInCartSerializer(
        read_only=True
    )

    product_id = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all(),
        source="product",
        write_only=True
    )

    subtotal = serializers.SerializerMethodField()

    class Meta:
        model = CartItem
        fields = (
            "id",
            "product",
            "product_id",
            "quantity",
            "subtotal",
            "created_at",
        )

        read_only_fields = (
            "id",
            "product",
            "subtotal",
            "created_at",
        )

    def get_subtotal(self, obj):
        return obj.product.price * obj.quantity


class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(
        many=True,
        read_only=True
    )

    total_price = serializers.SerializerMethodField()

    class Meta:
        model = Cart
        fields = (
            "id",
            "items",
            "total_price",
            "created_at",
            "updated_at",
        )

        read_only_fields = (
            "id",
            "items",
            "total_price",
            "created_at",
            "updated_at",
        )

    def get_total_price(self, obj):
        return sum(
            item.product.price * item.quantity
            for item in obj.items.all()
        )
