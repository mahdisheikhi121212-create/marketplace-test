from decimal import Decimal

from django.contrib.auth.models import User
from rest_framework.test import APITestCase

from addresses.models import Address
from customers.models import CustomerProfile
from inventory.models import (
    InventoryLocation,
    InventoryStock,
)
from order_history.models import OrderHistory
from orders.models import Order
from products.models import Product
from sellers.models import SellerProfile
from shipping.models import Shipping
from shops.models import Shop


class ShippingFlowTests(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="shipping_test_user",
            password="Test@12345",
        )

        self.customer = (
            CustomerProfile.objects.create(
                user=self.user,
            )
        )

        self.seller_user = (
            User.objects.create_user(
                username=(
                    "shipping_test_seller"
                ),
                password="Test@12345",
            )
        )

        self.seller = (
            SellerProfile.objects.create(
                user=self.seller_user,
                is_verified=True,
            )
        )

        self.shop = Shop.objects.create(
            seller=self.seller,
            name="Shipping Test Shop",
            is_active=True,
        )

        self.address = Address.objects.create(
            customer=self.customer,
            title="Home",
            receiver_name="Test Receiver",
            phone="09121234567",
            province="Tehran",
            city="Tehran",
            address_line="Test Address 123",
            postal_code="1234567890",
            is_default=True,
        )

        self.product = Product.objects.create(
            shop=self.shop,
            name="Shipping Test Product",
            description=(
                "Product for shipping test."
            ),
            price=Decimal("1500.00"),
        )

        self.location = (
            InventoryLocation.objects.create(
                name=(
                    "Shipping Test Location"
                ),
            )
        )

        self.stock = (
            InventoryStock.objects.create(
                product=self.product,
                location=self.location,
                quantity=10,
                reserved_quantity=0,
            )
        )

        self.order = Order.objects.create(
            customer=self.customer,
            shop=self.shop,
            order_number=(
                "SHIPPING-TEST-001"
            ),
            shipping_address=self.address,
            status="pending",
            total_price=Decimal(
                "3000.00"
            ),
        )

    def test_shipping_created_for_order(self):
        shipping = Shipping.objects.create(
            order=self.order,
            status="pending",
            carrier="Test Carrier",
            tracking_number="TEST-TRACK-001",
        )

        self.assertEqual(
            shipping.order,
            self.order,
        )

        self.assertEqual(
            shipping.status,
            "pending",
        )

        self.assertEqual(
            shipping.carrier,
            "Test Carrier",
        )

        self.assertEqual(
            shipping.tracking_number,
            "TEST-TRACK-001",
        )

    def test_shipping_status_can_be_updated(
        self
    ):
        shipping = Shipping.objects.create(
            order=self.order,
            status="pending",
            carrier="Test Carrier",
            tracking_number="TEST-TRACK-002",
        )

        shipping.status = "shipped"
        shipping.save()

        shipping.refresh_from_db()

        self.assertEqual(
            shipping.status,
            "shipped",
        )

        shipping.status = "delivered"
        shipping.save()

        shipping.refresh_from_db()

        self.assertEqual(
            shipping.status,
            "delivered",
        )


class ShippingStatusRegressionTests(
    APITestCase
):

    def setUp(self):
        self.customer_user = (
            User.objects.create_user(
                username="shipping_customer",
                password="Test@12345",
            )
        )

        self.customer = (
            CustomerProfile.objects.create(
                user=self.customer_user,
            )
        )

        self.seller_user = (
            User.objects.create_user(
                username=(
                    "shipping_status_seller"
                ),
                password="Test@12345",
            )
        )

        self.seller = (
            SellerProfile.objects.create(
                user=self.seller_user,
                is_verified=True,
            )
        )

        self.shop = Shop.objects.create(
            seller=self.seller,
            name="Shipping Status Shop",
            is_active=True,
        )

        self.admin_user = (
            User.objects.create_user(
                username="shipping_admin",
                password="Test@12345",
                is_staff=True,
            )
        )

        self.order = Order.objects.create(
            customer=self.customer,
            shop=self.shop,
            order_number=(
                "SHIPPING-STATUS-001"
            ),
            status="paid",
            total_price=Decimal(
                "1000.00"
            ),
        )

        self.shipping = (
            Shipping.objects.create(
                order=self.order,
                status="pending",
                carrier="Test Carrier",
                tracking_number=(
                    "STATUS-TRACK-001"
                ),
            )
        )

        self.client.force_authenticate(
            user=self.admin_user
        )

    def test_shipping_shipped_status_updates_order_and_history(
        self
    ):
        response = self.client.patch(
            (
                f"/api/shipping/"
                f"{self.shipping.id}/"
            ),
            {
                "status": "shipped",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        self.shipping.refresh_from_db()
        self.order.refresh_from_db()

        self.assertEqual(
            self.shipping.status,
            "shipped",
        )

        self.assertIsNotNone(
            self.shipping.shipped_at,
        )

        self.assertEqual(
            self.order.status,
            "shipped",
        )

        self.assertTrue(
            OrderHistory.objects.filter(
                order=self.order,
                status="shipped",
            ).exists()
        )

    def test_shipping_delivered_status_updates_order_and_history(
        self
    ):
        self.shipping.status = "shipped"
        self.shipping.save()

        self.order.status = "shipped"
        self.order.save(
            update_fields=[
                "status",
            ]
        )

        response = self.client.patch(
            (
                f"/api/shipping/"
                f"{self.shipping.id}/"
            ),
            {
                "status": "delivered",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        self.shipping.refresh_from_db()
        self.order.refresh_from_db()

        self.assertEqual(
            self.shipping.status,
            "delivered",
        )

        self.assertIsNotNone(
            self.shipping.delivered_at,
        )

        self.assertEqual(
            self.order.status,
            "delivered",
        )

        self.assertTrue(
            OrderHistory.objects.filter(
                order=self.order,
                status="delivered",
            ).exists()
        )