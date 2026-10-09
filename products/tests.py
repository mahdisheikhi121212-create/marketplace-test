from django.contrib.auth.models import User
from django.test import TestCase

from rest_framework.test import APIClient

from sellers.models import SellerProfile
from shops.models import Shop


class SellerVerificationTests(TestCase):

    def setUp(self):
        self.client = APIClient()

        self.normal_user = User.objects.create_user(
            username="normal_user",
            password="testpass123",
        )

        self.unverified_user = User.objects.create_user(
            username="unverified_seller",
            password="testpass123",
        )

        self.unverified_seller = SellerProfile.objects.create(
            user=self.unverified_user,
            is_verified=False,
        )

        Shop.objects.create(
            seller=self.unverified_seller,
            name="Unverified Shop",
        )

        self.verified_user = User.objects.create_user(
            username="verified_seller",
            password="testpass123",
        )

        self.verified_seller = SellerProfile.objects.create(
            user=self.verified_user,
            is_verified=True,
        )

        Shop.objects.create(
            seller=self.verified_seller,
            name="Verified Shop",
        )

    def test_normal_user_cannot_access_seller_products(self):
        self.client.force_authenticate(
            user=self.normal_user,
        )

        response = self.client.get(
            "/api/products/seller/",
        )

        self.assertEqual(
            response.status_code,
            403,
        )

    def test_unverified_seller_cannot_access_seller_products(self):
        self.client.force_authenticate(
            user=self.unverified_user,
        )

        response = self.client.get(
            "/api/products/seller/",
        )

        self.assertEqual(
            response.status_code,
            403,
        )

    def test_verified_seller_can_access_seller_products(self):
        self.client.force_authenticate(
            user=self.verified_user,
        )

        response = self.client.get(
            "/api/products/seller/",
        )

        self.assertEqual(
            response.status_code,
            200,
        )

    def test_unauthenticated_user_cannot_access_seller_products(self):
        response = self.client.get(
            "/api/products/seller/",
        )

        self.assertEqual(
            response.status_code,
            401,
        )

