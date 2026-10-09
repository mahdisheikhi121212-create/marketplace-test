from decimal import Decimal
from uuid import uuid4

from django.contrib.auth.models import User

from rest_framework.test import (
    APITestCase,
)

from addresses.models import Address

from cart.models import (
    Cart,
    CartItem,
)

from customers.models import (
    CustomerProfile,
)

from inventory.models import (
    InventoryLocation,
    InventoryStock,
)

from orders.models import Order

from products.models import Product

from products.serializers import (
    SellerProductSerializer,
)

from sellers.models import (
    SellerProfile,
)

from shops.models import Shop


class MVPBusinessRulesTests(
    APITestCase
):

    def setUp(self):
        self.customer_user = (
            User.objects.create_user(
                username="mvp_customer",
                password="Test@12345",
            )
        )

        self.customer = (
            CustomerProfile.objects.create(
                user=self.customer_user,
            )
        )

        self.seller_user_a = (
            User.objects.create_user(
                username="mvp_seller_a",
                password="Test@12345",
            )
        )

        self.seller_a = (
            SellerProfile.objects.create(
                user=self.seller_user_a,
                is_verified=True,
            )
        )

        self.shop_a = (
            Shop.objects.create(
                seller=self.seller_a,
                name="MVP Shop A",
                is_active=True,
            )
        )

        self.seller_user_b = (
            User.objects.create_user(
                username="mvp_seller_b",
                password="Test@12345",
            )
        )

        self.seller_b = (
            SellerProfile.objects.create(
                user=self.seller_user_b,
                is_verified=True,
            )
        )

        self.shop_b = (
            Shop.objects.create(
                seller=self.seller_b,
                name="MVP Shop B",
                is_active=True,
            )
        )

        self.product_a1 = (
            Product.objects.create(
                shop=self.shop_a,
                name="Product A1",
                description="",
                price=Decimal(
                    "100.00"
                ),
            )
        )

        self.product_a2 = (
            Product.objects.create(
                shop=self.shop_a,
                name="Product A2",
                description="",
                price=Decimal(
                    "200.00"
                ),
            )
        )

        self.product_b = (
            Product.objects.create(
                shop=self.shop_b,
                name="Product B",
                description="",
                price=Decimal(
                    "300.00"
                ),
            )
        )

        self.location = (
            InventoryLocation.objects.create(
                name="MVP Warehouse",
                city="Test City",
                is_active=True,
            )
        )

        for product in (
            self.product_a1,
            self.product_a2,
            self.product_b,
        ):
            InventoryStock.objects.create(
                product=product,
                location=self.location,
                quantity=10,
                reserved_quantity=0,
            )

        self.client.force_authenticate(
            user=self.customer_user
        )

    def test_cart_accepts_products_from_same_shop(
        self
    ):
        first_response = self.client.post(
            "/api/cart/items/",
            {
                "product_id": (
                    self.product_a1.id
                ),
                "quantity": 1,
            },
            format="json",
        )

        second_response = self.client.post(
            "/api/cart/items/",
            {
                "product_id": (
                    self.product_a2.id
                ),
                "quantity": 1,
            },
            format="json",
        )

        self.assertEqual(
            first_response.status_code,
            201,
        )

        self.assertEqual(
            second_response.status_code,
            201,
        )

    def test_cart_rejects_product_from_second_shop(
        self
    ):
        first_response = self.client.post(
            "/api/cart/items/",
            {
                "product_id": (
                    self.product_a1.id
                ),
                "quantity": 1,
            },
            format="json",
        )

        second_response = self.client.post(
            "/api/cart/items/",
            {
                "product_id": (
                    self.product_b.id
                ),
                "quantity": 1,
            },
            format="json",
        )

        self.assertEqual(
            first_response.status_code,
            201,
        )

        self.assertEqual(
            second_response.status_code,
            400,
        )

        cart = Cart.objects.get(
            customer=self.customer
        )

        self.assertEqual(
            cart.items.count(),
            1,
        )

    def test_cart_rejects_product_from_inactive_shop(
        self
    ):
        self.shop_a.is_active = False

        self.shop_a.save(
            update_fields=[
                "is_active"
            ]
        )

        response = self.client.post(
            "/api/cart/items/",
            {
                "product_id": (
                    self.product_a1.id
                ),
                "quantity": 1,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            400,
        )

    def test_cart_rejects_product_from_unverified_seller(
        self
    ):
        self.seller_a.is_verified = False

        self.seller_a.save(
            update_fields=[
                "is_verified"
            ]
        )

        response = self.client.post(
            "/api/cart/items/",
            {
                "product_id": (
                    self.product_a1.id
                ),
                "quantity": 1,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            400,
        )

    def test_cart_rejects_quantity_above_available_stock(
        self
    ):
        response = self.client.post(
            "/api/cart/items/",
            {
                "product_id": (
                    self.product_a1.id
                ),
                "quantity": 11,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            400,
        )

    def test_seller_product_price_must_be_positive(
        self
    ):
        zero_price_serializer = (
            SellerProductSerializer(
                data={
                    "name": (
                        "Zero Price Product"
                    ),
                    "description": "",
                    "price": "0.00",
                }
            )
        )

        negative_price_serializer = (
            SellerProductSerializer(
                data={
                    "name": (
                        "Negative Price Product"
                    ),
                    "description": "",
                    "price": "-1.00",
                }
            )
        )

        self.assertFalse(
            zero_price_serializer.is_valid()
        )

        self.assertIn(
            "price",
            zero_price_serializer.errors,
        )

        self.assertFalse(
            negative_price_serializer.is_valid()
        )

        self.assertIn(
            "price",
            negative_price_serializer.errors,
        )

    def test_order_rejects_legacy_multi_shop_cart(
        self
    ):
        cart = Cart.objects.create(
            customer=self.customer
        )

        CartItem.objects.create(
            cart=cart,
            product=self.product_a1,
            quantity=1,
        )

        CartItem.objects.create(
            cart=cart,
            product=self.product_b,
            quantity=1,
        )

        address = Address.objects.create(
            customer=self.customer,
            title="Home",
            receiver_name="MVP Customer",
            phone="09121234567",
            province="Tehran",
            city="Tehran",
            address_line="Test Address",
            postal_code="1234567890",
            is_default=True,
        )

        response = self.client.post(
            "/api/orders/",
            {
                "shipping_address_id": (
                    address.id
                ),
            },
            format="json",
            HTTP_IDEMPOTENCY_KEY=(
                str(uuid4())
            ),
        )

        self.assertEqual(
            response.status_code,
            400,
        )

        self.assertEqual(
            Order.objects.count(),
            0,
        )