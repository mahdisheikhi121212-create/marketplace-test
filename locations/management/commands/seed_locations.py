import json
from pathlib import Path

from django.core.management.base import BaseCommand
from locations.models import Province, City


class Command(BaseCommand):
    help = "Seed Iran provinces and cities"

    def handle(self, *args, **options):
        base_dir = Path(__file__).resolve().parents[2]
        data_dir = base_dir / "data"

        provinces_file = data_dir / "provinces.json"
        cities_file = data_dir / "cities.json"

        if not provinces_file.exists():
            self.stdout.write(
                self.style.ERROR(
                    f"Province file not found: {provinces_file}"
                )
            )
            return

        if not cities_file.exists():
            self.stdout.write(
                self.style.ERROR(
                    f"City file not found: {cities_file}"
                )
            )
            return

        with open(provinces_file, "r", encoding="utf-8-sig") as file:
            provinces_data = json.load(file)

        with open(cities_file, "r", encoding="utf-8-sig") as file:
            cities_data = json.load(file)

        province_map = {}

        self.stdout.write("Importing provinces...")

        for item in provinces_data:
            province, created = Province.objects.update_or_create(
                slug=item["slug"],
                defaults={
                    "name": item["name"],
                    "is_active": True,
                },
            )

            province_map[item["id"]] = province

        self.stdout.write(
            self.style.SUCCESS(
                f"Provinces imported: {len(province_map)}"
            )
        )

        self.stdout.write("Importing cities...")

        created_count = 0
        updated_count = 0
        skipped_count = 0

        for item in cities_data:
            province = province_map.get(item["province_id"])

            if not province:
                skipped_count += 1
                continue

            city, created = City.objects.update_or_create(
                province=province,
                name=item["name"],
                defaults={
                    "slug": item["slug"],
                    "is_active": True,
                },
            )

            if created:
                created_count += 1
            else:
                updated_count += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Cities created: {created_count}"
            )
        )

        self.stdout.write(
            self.style.SUCCESS(
                f"Cities updated: {updated_count}"
            )
        )

        if skipped_count:
            self.stdout.write(
                self.style.WARNING(
                    f"Cities skipped: {skipped_count}"
                )
            )

        self.stdout.write(
            self.style.SUCCESS(
                "Iran locations imported successfully."
            )
        )