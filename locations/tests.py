from django.test import TestCase
from rest_framework.test import APIClient

from .models import Province, City


class LocationAPITestCase(TestCase):

    def setUp(self):
        self.client = APIClient()

        self.province = Province.objects.create(
            name="تهران",
            slug="tehran",
            is_active=True,
        )

        self.city = City.objects.create(
            province=self.province,
            name="تهران",
            slug="tehran",
            is_active=True,
        )

    def test_province_list_api(self):
        response = self.client.get(
            "/api/locations/provinces/"
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        self.assertIsInstance(
            response.data,
            list,
        )

        self.assertEqual(
            response.data[0]["name"],
            "تهران",
        )

    def test_city_list_api(self):
        response = self.client.get(
            (
                "/api/locations/cities/"
                f"?province={self.province.id}"
            )
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        self.assertIsInstance(
            response.data,
            list,
        )

        self.assertEqual(
            response.data[0]["name"],
            "تهران",
        )

    def test_city_filter_by_province(self):
        other_province = Province.objects.create(
            name="اصفهان",
            slug="isfahan",
            is_active=True,
        )

        City.objects.create(
            province=other_province,
            name="اصفهان",
            slug="isfahan",
            is_active=True,
        )

        response = self.client.get(
            (
                "/api/locations/cities/"
                f"?province={self.province.id}"
            )
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        self.assertEqual(
            len(response.data),
            1,
        )

        self.assertEqual(
            response.data[0]["name"],
            "تهران",
        )

    def test_inactive_province_not_returned(self):
        Province.objects.create(
            name="استان غیرفعال",
            slug="inactive-province",
            is_active=False,
        )

        response = self.client.get(
            "/api/locations/provinces/"
        )

        names = [
            item["name"]
            for item in response.data
        ]

        self.assertNotIn(
            "استان غیرفعال",
            names,
        )

    def test_inactive_city_not_returned(self):
        City.objects.create(
            province=self.province,
            name="شهر غیرفعال",
            slug="inactive-city",
            is_active=False,
        )

        response = self.client.get(
            (
                "/api/locations/cities/"
                f"?province={self.province.id}"
            )
        )

        names = [
            item["name"]
            for item in response.data
        ]

        self.assertNotIn(
            "شهر غیرفعال",
            names,
        )