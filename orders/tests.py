from decimal import Decimal
from uuid import uuid4

from django.contrib.auth.models import User
from rest_framework.test import APITestCase

from addresses.models import Address
from cart.models import Cart, CartItem
from customers.models import CustomerProfile
from inventory.models import (
    InventoryLocation,
    InventoryStock,
)
from inventory.services import reserve_stock
from order_history.models import OrderHistory
from orders.models import Order, OrderItem
from products.models import Product
from sellers.models import SellerProfile
from shops.models import Shop


class OrderInventoryFlowTests(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="order_flow_test",
            password="Test@12345",
        )

        self.customer = CustomerProfile.objects.create(
            user=self.user,
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

        self.seller_user = User.objects.create_user(
            username="order_flow_seller",
            password="Test@12345",
        )

        self.seller = SellerProfile.objects.create(
            user=self.seller_user,
            is_verified=True,
        )

        self.shop = Shop.objects.create(
            seller=self.seller,
            name="Order Flow Test Shop",
            is_active=True,
        )

        self.product = Product.objects.create(
            shop=self.shop,
            name="Order Flow Test Product",
            description="Product for order flow test.",
            price=Decimal("1500.00"),
        )

        self.location = InventoryLocation.objects.create(
            name="Order Flow Test Location",
            is_active=True,
        )

        self.stock = InventoryStock.objects.create(
            product=self.product,
            location=self.location,
            quantity=10,
            reserved_quantity=0,
        )

        self.cart = Cart.objects.create(
            customer=self.customer,
        )

        CartItem.objects.create(
            cart=self.cart,
            product=self.product,
            quantity=2,
        )

    def authenticate(self):
        response = self.client.post(
            "/api/auth/login/",
            {
                "username": "order_flow_test",
                "password": "Test@12345",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        self.client.credentials(
            HTTP_AUTHORIZATION=(
                f"Bearer {response.data['access']}"
            )
        )

    def test_order_creation_and_inventory_reservation(self):
        self.authenticate()

        response = self.client.post(
            "/api/orders/",
            {
                "shipping_address_id": self.address.id,
            },
            format="json",
            HTTP_IDEMPOTENCY_KEY=str(uuid4()),
        )

        self.assertEqual(
            response.status_code,
            201,
        )

        order = Order.objects.get(
            id=response.data["id"]
        )

        self.assertEqual(
            order.customer,
            self.customer,
        )

        self.assertEqual(
            order.shop,
            self.shop,
        )

        self.assertEqual(
            order.shipping_address_id,
            self.address.id,
        )

        self.assertEqual(
            order.total_price,
            Decimal("3000.00"),
        )

        self.assertTrue(
            OrderItem.objects.filter(
                order=order,
                product=self.product,
                quantity=2,
            ).exists()
        )

        self.stock.refresh_from_db()

        self.assertEqual(
            self.stock.quantity,
            10,
        )

        self.assertEqual(
            self.stock.reserved_quantity,
            2,
        )


class OrderStatusRegressionTests(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="order_status_user",
            password="Test@12345",
        )

        self.customer = CustomerProfile.objects.create(
            user=self.user,
        )

        self.admin_user = User.objects.create_user(
            username="order_status_admin",
            password="Test@12345",
            is_staff=True,
        )

        self.seller_user = User.objects.create_user(
            username="order_status_seller",
            password="Test@12345",
        )

        self.seller = SellerProfile.objects.create(
            user=self.seller_user,
            is_verified=True,
        )

        self.shop = Shop.objects.create(
            seller=self.seller,
            name="Order Status Shop",
            is_active=True,
        )

        self.product = Product.objects.create(
            shop=self.shop,
            name="Order Status Product",
            description="",
            price=Decimal("1000.00"),
        )

        self.location = InventoryLocation.objects.create(
            name="Order Status Location",
            is_active=True,
        )

        self.stock = InventoryStock.objects.create(
            product=self.product,
            location=self.location,
            quantity=10,
            reserved_quantity=0,
        )

        self.order = Order.objects.create(
            customer=self.customer,
            shop=self.shop,
            order_number="ORDER-STATUS-001",
            status="pending",
            total_price=Decimal("1000.00"),
        )

        OrderItem.objects.create(
            order=self.order,
            product=self.product,
            quantity=1,
            price_at_purchase=Decimal("1000.00"),
        )

        reserve_stock(
            self.product,
            1,
            reference=self.order.order_number,
        )

        self.client.force_authenticate(
            user=self.user
        )

    def test_customer_cannot_mark_pending_order_as_paid(self):
        response = self.client.patch(
            f"/api/orders/{self.order.id}/status/",
            {
                "status": "paid",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            400,
        )

        self.order.refresh_from_db()

        self.assertEqual(
            self.order.status,
            "pending",
        )

    def test_customer_cancellation_releases_stock_and_creates_history(self):
        response = self.client.patch(
            f"/api/orders/{self.order.id}/status/",
            {
                "status": "cancelled",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        self.order.refresh_from_db()
        self.stock.refresh_from_db()

        self.assertEqual(
            self.order.status,
            "cancelled",
        )

        self.assertEqual(
            self.stock.reserved_quantity,
            0,
        )

        self.assertTrue(
            OrderHistory.objects.filter(
                order=self.order,
                status="cancelled",
            ).exists()
        )

    def test_admin_cannot_mark_pending_order_as_paid(self):
        self.client.force_authenticate(
            user=self.admin_user
        )

        response = self.client.patch(
            f"/api/orders/admin/{self.order.id}/status/",
            {
                "status": "paid",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            400,
        )

        self.order.refresh_from_db()

        self.assertEqual(
            self.order.status,
            "pending",
        )

    def test_admin_cannot_mark_order_as_shipped_directly(self):
        self.order.status = "processing"

        self.order.save(
            update_fields=[
                "status",
            ]
        )

        self.client.force_authenticate(
            user=self.admin_user
        )

        response = self.client.patch(
            f"/api/orders/admin/{self.order.id}/status/",
            {
                "status": "shipped",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            400,
        )

        self.order.refresh_from_db()

        self.assertEqual(
            self.order.status,
            "processing",
        )

    def test_admin_cannot_mark_order_as_delivered_directly(self):
        self.order.status = "shipped"

        self.order.save(
            update_fields=[
                "status",
            ]
        )

        self.client.force_authenticate(
            user=self.admin_user
        )

        response = self.client.patch(
            f"/api/orders/admin/{self.order.id}/status/",
            {
                "status": "delivered",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            400,
        )

        self.order.refresh_from_db()

        self.assertEqual(
            self.order.status,
            "shipped",
        )

    def test_admin_can_move_paid_order_to_processing(self):
        self.order.status = "paid"

        self.order.save(
            update_fields=[
                "status",
            ]
        )

        self.client.force_authenticate(
            user=self.admin_user
        )

        response = self.client.patch(
            f"/api/orders/admin/{self.order.id}/status/",
            {
                "status": "processing",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        self.order.refresh_from_db()

        self.assertEqual(
            self.order.status,
            "processing",
        )

        self.assertTrue(
            OrderHistory.objects.filter(
                order=self.order,
                status="processing",
            ).exists()
        )