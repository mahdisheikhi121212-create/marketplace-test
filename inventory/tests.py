from django.contrib.auth.models import User
from django.test import TestCase
from rest_framework.test import APITestCase

from customers.models import CustomerProfile
from inventory.models import (
    InventoryLocation,
    InventoryStock,
    InventoryTransaction,
)
from inventory.services import (
    complete_sale,
    release_reserved_stock,
    reserve_stock,
)
from orders.models import Order, OrderItem
from products.models import Product
from sellers.models import SellerProfile
from shops.models import Shop


class InventoryAPISecurityTests(APITestCase):

    def setUp(self):
        self.normal_user = User.objects.create_user(
            username="inventory_normal_user",
            password="testpass123",
        )

        self.admin_user = User.objects.create_user(
            username="inventory_admin_user",
            password="testpass123",
            is_staff=True,
        )

        self.seller_user = User.objects.create_user(
            username="inventory_security_seller",
            password="testpass123",
        )

        self.seller = SellerProfile.objects.create(
            user=self.seller_user,
            is_verified=True,
        )

        self.shop = Shop.objects.create(
            seller=self.seller,
            name="Inventory Security Shop",
            is_active=True,
        )

        self.location = InventoryLocation.objects.create(
            name="Security Test Location",
            city="Test City",
            is_active=True,
        )

        self.product = Product.objects.create(
            shop=self.shop,
            name="Security Test Product",
            description="",
            price=100,
        )

        self.stock = InventoryStock.objects.create(
            product=self.product,
            location=self.location,
            quantity=10,
            reserved_quantity=2,
        )

        self.transaction = InventoryTransaction.objects.create(
            stock=self.stock,
            transaction_type="initial",
            quantity=10,
            reference="SECURITY-TEST",
        )

    def test_normal_user_cannot_access_inventory_stock_api(self):
        self.client.force_authenticate(
            user=self.normal_user
        )

        response = self.client.get(
            "/api/inventory/stocks/"
        )

        self.assertEqual(
            response.status_code,
            403,
        )

    def test_admin_user_can_access_inventory_stock_api(self):
        self.client.force_authenticate(
            user=self.admin_user
        )

        response = self.client.get(
            "/api/inventory/stocks/"
        )

        self.assertEqual(
            response.status_code,
            200,
        )

    def test_reserved_quantity_cannot_be_changed_through_api(self):
        self.client.force_authenticate(
            user=self.admin_user
        )

        response = self.client.patch(
            f"/api/inventory/stocks/{self.stock.id}/",
            {
                "reserved_quantity": 99,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        self.stock.refresh_from_db()

        self.assertEqual(
            self.stock.reserved_quantity,
            2,
        )

    def test_normal_user_cannot_access_inventory_transactions(self):
        self.client.force_authenticate(
            user=self.normal_user
        )

        response = self.client.get(
            "/api/inventory/transactions/"
        )

        self.assertEqual(
            response.status_code,
            403,
        )

    def test_admin_user_can_access_inventory_transactions(self):
        self.client.force_authenticate(
            user=self.admin_user
        )

        response = self.client.get(
            "/api/inventory/transactions/"
        )

        self.assertEqual(
            response.status_code,
            200,
        )


class ReservationReleaseOwnershipTests(TestCase):

    def setUp(self):
        user = User.objects.create_user(
            username="release_test_user",
            password="testpass123",
        )

        self.customer = CustomerProfile.objects.create(
            user=user,
        )

        self.seller_user = User.objects.create_user(
            username="release_test_seller",
            password="testpass123",
        )

        self.seller = SellerProfile.objects.create(
            user=self.seller_user,
            is_verified=True,
        )

        self.shop = Shop.objects.create(
            seller=self.seller,
            name="Release Test Shop",
            is_active=True,
        )

        self.location = InventoryLocation.objects.create(
            name="Test Location",
            city="Test City",
            is_active=True,
        )

        self.product = Product.objects.create(
            shop=self.shop,
            name="Test Product",
            description="",
            price=100,
        )

        self.stock = InventoryStock.objects.create(
            product=self.product,
            location=self.location,
            quantity=10,
            reserved_quantity=0,
        )

        self.order_a = Order.objects.create(
            customer=self.customer,
            shop=self.shop,
            order_number="TEST-ORDER-A",
            total_price=100,
            status="pending",
        )

        self.order_b = Order.objects.create(
            customer=self.customer,
            shop=self.shop,
            order_number="TEST-ORDER-B",
            total_price=100,
            status="pending",
        )

        OrderItem.objects.create(
            order=self.order_a,
            product=self.product,
            quantity=1,
            price_at_purchase=100,
        )

        OrderItem.objects.create(
            order=self.order_b,
            product=self.product,
            quantity=1,
            price_at_purchase=100,
        )

        reserve_stock(
            self.product,
            1,
            reference=self.order_a.order_number,
        )

        reserve_stock(
            self.product,
            1,
            reference=self.order_b.order_number,
        )

    def test_release_only_affects_same_order_reservation(self):
        self.stock.refresh_from_db()

        self.assertEqual(
            self.stock.reserved_quantity,
            2,
        )

        release_reserved_stock(self.order_a)

        self.stock.refresh_from_db()

        self.assertEqual(
            self.stock.reserved_quantity,
            1,
        )

        self.assertEqual(
            InventoryTransaction.objects.filter(
                stock=self.stock,
                transaction_type="release",
                reference=self.order_a.order_number,
            ).count(),
            1,
        )

        release_reserved_stock(self.order_a)

        self.stock.refresh_from_db()

        self.assertEqual(
            self.stock.reserved_quantity,
            1,
        )

        self.assertEqual(
            InventoryTransaction.objects.filter(
                stock=self.stock,
                transaction_type="release",
                reference=self.order_a.order_number,
            ).count(),
            1,
        )

        self.assertEqual(
            InventoryTransaction.objects.filter(
                stock=self.stock,
                transaction_type="reservation",
                reference=self.order_b.order_number,
            ).count(),
            1,
        )


class MultiLocationSaleTests(TestCase):

    def setUp(self):
        user = User.objects.create_user(
            username="stage6_multilocation_user",
            password="testpass123",
        )

        self.customer = CustomerProfile.objects.create(
            user=user,
        )

        self.seller_user = User.objects.create_user(
            username="stage6_multilocation_seller",
            password="testpass123",
        )

        self.seller = SellerProfile.objects.create(
            user=self.seller_user,
            is_verified=True,
        )

        self.shop = Shop.objects.create(
            seller=self.seller,
            name="Stage 6 Shop",
            is_active=True,
        )

        self.product = Product.objects.create(
            shop=self.shop,
            name="Stage 6 Product",
            description="Stage 6 multi-location sale test",
            price=100,
        )

        self.location_a = InventoryLocation.objects.create(
            name="Stage 6 Location A",
            city="Test City A",
            is_active=True,
        )

        self.location_b = InventoryLocation.objects.create(
            name="Stage 6 Location B",
            city="Test City B",
            is_active=True,
        )

        self.stock_a = InventoryStock.objects.create(
            product=self.product,
            location=self.location_a,
            quantity=1,
            reserved_quantity=0,
        )

        self.stock_b = InventoryStock.objects.create(
            product=self.product,
            location=self.location_b,
            quantity=2,
            reserved_quantity=0,
        )

        self.order = Order.objects.create(
            customer=self.customer,
            shop=self.shop,
            order_number="STAGE6-MULTI-LOCATION-ORDER",
            total_price=200,
            status="pending",
        )

        OrderItem.objects.create(
            order=self.order,
            product=self.product,
            quantity=2,
            price_at_purchase=100,
        )

        reserve_stock(
            self.product,
            2,
            reference=self.order.order_number,
        )

    def test_complete_sale_uses_all_locations_reserved_for_order(self):
        self.stock_a.refresh_from_db()
        self.stock_b.refresh_from_db()

        self.assertEqual(
            self.stock_a.reserved_quantity,
            1,
        )

        self.assertEqual(
            self.stock_b.reserved_quantity,
            1,
        )

        complete_sale(self.order)

        self.stock_a.refresh_from_db()
        self.stock_b.refresh_from_db()

        self.assertEqual(
            self.stock_a.quantity,
            0,
        )

        self.assertEqual(
            self.stock_a.reserved_quantity,
            0,
        )

        self.assertEqual(
            self.stock_b.quantity,
            1,
        )

        self.assertEqual(
            self.stock_b.reserved_quantity,
            0,
        )

        sale_transactions = (
            InventoryTransaction.objects.filter(
                transaction_type="sale",
                reference=self.order.order_number,
            )
        )

        self.assertEqual(
            sale_transactions.count(),
            2,
        )

        self.assertEqual(
            sum(
                sale_transactions.values_list(
                    "quantity",
                    flat=True,
                )
            ),
            2,
        )