from datetime import timedelta
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.test import override_settings
from django.utils import timezone
from rest_framework.test import APITestCase

from customers.models import CustomerProfile
from inventory.models import (
    InventoryLocation,
    InventoryStock,
    InventoryTransaction,
)
from inventory.services import reserve_stock
from orders.models import Order, OrderItem
from payments.models import Payment
from products.models import Product
from sellers.models import SellerProfile
from shops.models import Shop


User = get_user_model()


class PaymentFlowTests(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="payment_test_user",
            password="testpass123",
        )

        self.customer = CustomerProfile.objects.create(
            user=self.user,
        )

        self.seller_user = User.objects.create_user(
            username="payment_test_seller",
            password="testpass123",
        )

        self.seller = SellerProfile.objects.create(
            user=self.seller_user,
            is_verified=True,
        )

        self.shop = Shop.objects.create(
            seller=self.seller,
            name="Payment Test Shop",
            is_active=True,
        )

        self.order = Order.objects.create(
            customer=self.customer,
            shop=self.shop,
            order_number="PAYMENT-TEST-001",
            total_price=1500,
            status="pending",
        )

    def create_product(
        self,
        name,
        price=1500,
    ):
        return Product.objects.create(
            shop=self.shop,
            name=name,
            description="",
            price=price,
        )

    def authenticate(self):
        response = self.client.post(
            "/api/auth/login/",
            {
                "username": "payment_test_user",
                "password": "testpass123",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        token = response.data["access"]

        self.client.credentials(
            HTTP_AUTHORIZATION=(
                f"Bearer {token}"
            )
        )

    @patch(
        "payments.views.ZarinPalService.request_payment"
    )
    def test_payment_create_success(
        self,
        mock_request_payment,
    ):
        self.authenticate()

        mock_request_payment.return_value = {
            "data": {
                "authority":
                    "TEST-AUTHORITY-123",
            }
        }

        response = self.client.post(
            "/api/payments/",
            {
                "order": self.order.id,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            201,
        )

        payment = Payment.objects.get(
            order=self.order
        )

        self.assertEqual(
            payment.status,
            "pending",
        )

        self.assertEqual(
            payment.amount,
            self.order.total_price,
        )

        self.assertEqual(
            payment.authority,
            "TEST-AUTHORITY-123",
        )

        self.assertEqual(
            payment.order,
            self.order,
        )

    @patch(
        "payments.views.ZarinPalService.request_payment"
    )
    def test_payment_create_sets_expiration(
        self,
        mock_request_payment,
    ):
        self.authenticate()

        mock_request_payment.return_value = {
            "data": {
                "authority":
                    "TEST-EXPIRATION-AUTHORITY",
            }
        }

        response = self.client.post(
            "/api/payments/",
            {
                "order": self.order.id,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            201,
        )

        payment = Payment.objects.get(
            order=self.order
        )

        self.assertIsNotNone(
            payment.expires_at
        )

        expiration_duration = (
            payment.expires_at
            - payment.created_at
        )

        self.assertAlmostEqual(
            expiration_duration.total_seconds(),
            15 * 60,
            delta=5,
        )

    @patch(
        "payments.views.ZarinPalService.request_payment"
    )
    def test_payment_create_gateway_failure(
        self,
        mock_request_payment,
    ):
        self.authenticate()

        product = self.create_product(
            "Test Product"
        )

        location = (
            InventoryLocation.objects.create(
                name="Test Location",
                is_active=True,
            )
        )

        stock = InventoryStock.objects.create(
            product=product,
            location=location,
            quantity=10,
            reserved_quantity=0,
        )

        OrderItem.objects.create(
            order=self.order,
            product=product,
            quantity=1,
            price_at_purchase=1500,
        )

        reserve_stock(
            product,
            1,
            reference=self.order.order_number,
        )

        mock_request_payment.side_effect = (
            Exception(
                "Gateway unavailable"
            )
        )

        response = self.client.post(
            "/api/payments/",
            {
                "order": self.order.id,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            400,
        )

        payment = Payment.objects.get(
            order=self.order
        )

        self.assertEqual(
            payment.status,
            "failed",
        )

        stock.refresh_from_db()

        self.assertEqual(
            stock.reserved_quantity,
            0,
        )

        self.assertTrue(
            InventoryTransaction.objects.filter(
                stock=stock,
                transaction_type="release",
                reference=(
                    self.order.order_number
                ),
            ).exists()
        )

    def test_payment_create_for_other_customer_order(
        self
    ):
        self.authenticate()

        other_user = User.objects.create_user(
            username="other_payment_user",
            password="testpass123",
        )

        other_customer = (
            CustomerProfile.objects.create(
                user=other_user,
            )
        )

        other_order = Order.objects.create(
            customer=other_customer,
            shop=self.shop,
            order_number="PAYMENT-OTHER-001",
            total_price=2000,
            status="pending",
        )

        response = self.client.post(
            "/api/payments/",
            {
                "order": other_order.id,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            400,
        )

        self.assertFalse(
            Payment.objects.filter(
                order=other_order
            ).exists()
        )

    @patch(
        "payments.views.ZarinPalService.verify_payment"
    )
    def test_payment_callback_completes_sale(
        self,
        mock_verify_payment,
    ):
        product = self.create_product(
            "Callback Product"
        )

        location = (
            InventoryLocation.objects.create(
                name="Callback Location",
                is_active=True,
            )
        )

        stock = InventoryStock.objects.create(
            product=product,
            location=location,
            quantity=10,
            reserved_quantity=0,
        )

        OrderItem.objects.create(
            order=self.order,
            product=product,
            quantity=1,
            price_at_purchase=1500,
        )

        reserve_stock(
            product,
            1,
            reference=self.order.order_number,
        )

        payment = Payment.objects.create(
            order=self.order,
            amount=self.order.total_price,
            status="pending",
            authority="CALLBACK-AUTHORITY",
        )

        mock_verify_payment.return_value = {
            "data": {
                "code": 100,
                "ref_id": "REF-123",
            }
        }

        response = self.client.get(
            "/api/payments/callback/",
            {
                "Authority":
                    "CALLBACK-AUTHORITY",
                "Status": "OK",
            },
        )

        self.assertEqual(
            response.status_code,
            302,
        )

        payment.refresh_from_db()
        self.order.refresh_from_db()
        stock.refresh_from_db()

        self.assertEqual(
            payment.status,
            "paid",
        )

        self.assertEqual(
            payment.transaction_id,
            "REF-123",
        )

        self.assertEqual(
            self.order.status,
            "paid",
        )

        self.assertEqual(
            stock.quantity,
            9,
        )

        self.assertEqual(
            stock.reserved_quantity,
            0,
        )

        self.assertTrue(
            InventoryTransaction.objects.filter(
                stock=stock,
                transaction_type="sale",
                reference=(
                    self.order.order_number
                ),
            ).exists()
        )

    def test_payment_callback_failed_status(
        self
    ):
        product = self.create_product(
            "Failed Callback Product"
        )

        location = (
            InventoryLocation.objects.create(
                name=(
                    "Failed Callback Location"
                ),
                is_active=True,
            )
        )

        stock = InventoryStock.objects.create(
            product=product,
            location=location,
            quantity=10,
            reserved_quantity=0,
        )

        OrderItem.objects.create(
            order=self.order,
            product=product,
            quantity=1,
            price_at_purchase=1500,
        )

        reserve_stock(
            product,
            1,
            reference=self.order.order_number,
        )

        Payment.objects.create(
            order=self.order,
            amount=self.order.total_price,
            status="pending",
            authority=(
                "FAILED-CALLBACK-AUTHORITY"
            ),
        )

        with patch(
            "payments.views.complete_sale"
        ) as mock_complete_sale:

            response = self.client.get(
                "/api/payments/callback/",
                {
                    "Authority": (
                        "FAILED-CALLBACK-AUTHORITY"
                    ),
                    "Status": "NOK",
                },
            )

        self.assertEqual(
            response.status_code,
            400,
        )

        payment = Payment.objects.get(
            order=self.order
        )

        self.assertEqual(
            payment.status,
            "failed",
        )

        self.order.refresh_from_db()

        self.assertEqual(
            self.order.status,
            "pending",
        )

        stock.refresh_from_db()

        self.assertEqual(
            stock.reserved_quantity,
            0,
        )

        self.assertTrue(
            InventoryTransaction.objects.filter(
                stock=stock,
                transaction_type="release",
                reference=(
                    self.order.order_number
                ),
            ).exists()
        )

        mock_complete_sale.assert_not_called()

    @override_settings(
        PAYMENT_EXPIRATION_MINUTES=15
    )
    def test_expire_payments_marks_expired_payment_failed(
        self,
    ):
        payment = Payment.objects.create(
            order=self.order,
            amount=self.order.total_price,
            status="pending",
            authority=(
                "EXPIRED-TEST-AUTHORITY"
            ),
            expires_at=(
                timezone.now()
                - timedelta(minutes=1)
            ),
        )

        call_command(
            "expire_payments"
        )

        payment.refresh_from_db()

        self.assertEqual(
            payment.status,
            "failed",
        )

    @override_settings(
        PAYMENT_EXPIRATION_MINUTES=15
    )
    def test_expire_payment_releases_reserved_stock(
        self,
    ):
        product = self.create_product(
            "Expiration Product"
        )

        location = (
            InventoryLocation.objects.create(
                name="Expiration Location",
                is_active=True,
            )
        )

        stock = InventoryStock.objects.create(
            product=product,
            location=location,
            quantity=10,
            reserved_quantity=0,
        )

        OrderItem.objects.create(
            order=self.order,
            product=product,
            quantity=1,
            price_at_purchase=1500,
        )

        reserve_stock(
            product,
            1,
            reference=self.order.order_number,
        )

        stock.refresh_from_db()

        self.assertEqual(
            stock.reserved_quantity,
            1,
        )

        Payment.objects.create(
            order=self.order,
            amount=self.order.total_price,
            status="pending",
            authority=(
                "EXPIRATION-RELEASE-AUTHORITY"
            ),
            expires_at=(
                timezone.now()
                - timedelta(minutes=1)
            ),
        )

        call_command(
            "expire_payments"
        )

        payment = Payment.objects.get(
            order=self.order
        )

        stock.refresh_from_db()
        self.order.refresh_from_db()

        self.assertEqual(
            payment.status,
            "failed",
        )

        self.assertEqual(
            self.order.status,
            "pending",
        )

        self.assertEqual(
            stock.reserved_quantity,
            0,
        )

        release_transactions = (
            InventoryTransaction.objects.filter(
                stock=stock,
                transaction_type="release",
                reference=(
                    self.order.order_number
                ),
            )
        )

        self.assertEqual(
            release_transactions.count(),
            1,
        )

        call_command(
            "expire_payments"
        )

        stock.refresh_from_db()

        self.assertEqual(
            stock.reserved_quantity,
            0,
        )

        self.assertEqual(
            InventoryTransaction.objects.filter(
                stock=stock,
                transaction_type="release",
                reference=(
                    self.order.order_number
                ),
            ).count(),
            1,
        )

    @patch(
        "payments.views.ZarinPalService.verify_payment",
        return_value={
            "data": {
                "code": 100,
                "ref_id":
                    "EXPIRED-SHOULD-NOT-BE-USED",
            }
        },
    )
    def test_expired_payment_callback_cannot_be_paid(
        self,
        mock_verify_payment,
    ):
        payment = Payment.objects.create(
            order=self.order,
            amount=self.order.total_price,
            status="pending",
            authority=(
                "EXPIRED-CALLBACK-AUTHORITY"
            ),
            expires_at=(
                timezone.now()
                - timedelta(minutes=1)
            ),
        )

        response = self.client.get(
            "/api/payments/callback/",
            {
                "Authority":
                    "EXPIRED-CALLBACK-AUTHORITY",
                "Status": "OK",
            },
        )

        self.assertEqual(
            response.status_code,
            400,
        )

        payment.refresh_from_db()
        self.order.refresh_from_db()

        self.assertEqual(
            payment.status,
            "failed",
        )

        self.assertEqual(
            self.order.status,
            "pending",
        )

        mock_verify_payment.assert_not_called()

    @patch(
        "payments.views.ZarinPalService.verify_payment",
        return_value={
            "data": {
                "code": 100,
                "ref_id":
                    "NON-PENDING-SHOULD-NOT-BE-USED",
            }
        },
    )
    def test_non_pending_payment_callback_cannot_be_paid(
        self,
        mock_verify_payment,
    ):
        payment = Payment.objects.create(
            order=self.order,
            amount=self.order.total_price,
            status="failed",
            authority="NON-PENDING-AUTHORITY",
        )

        response = self.client.get(
            "/api/payments/callback/",
            {
                "Authority":
                    "NON-PENDING-AUTHORITY",
                "Status": "OK",
            },
        )

        self.assertEqual(
            response.status_code,
            400,
        )

        payment.refresh_from_db()
        self.order.refresh_from_db()

        self.assertEqual(
            payment.status,
            "failed",
        )

        self.assertEqual(
            self.order.status,
            "pending",
        )

        mock_verify_payment.assert_not_called()