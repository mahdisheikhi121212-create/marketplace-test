from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from payments.models import Payment
from payments.views import fail_payment_and_release


class Command(BaseCommand):
    help = "Expire pending payments and release reserved stock."

    def handle(self, *args, **options):
        now = timezone.now()

        payment_ids = (
            Payment.objects
            .filter(
                status="pending",
                expires_at__isnull=False,
                expires_at__lte=now,
            )
            .values_list(
                "id",
                flat=True,
            )
        )

        expired_count = 0

        for payment_id in payment_ids:
            with transaction.atomic():
                payment = (
                    Payment.objects
                    .select_for_update()
                    .select_related("order")
                    .get(id=payment_id)
                )

                if (
                    payment.status != "pending"
                    or payment.expires_at is None
                    or payment.expires_at > timezone.now()
                ):
                    continue

                fail_payment_and_release(payment)

                expired_count += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"{expired_count} payment(s) expired."
            )
        )