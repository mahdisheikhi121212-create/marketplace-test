import hashlib
import secrets
from datetime import timedelta

from django.utils import timezone

from .models import PhoneVerificationOTP
from .sms.loader import get_sms_provider


OTP_LENGTH = 6
OTP_EXPIRY_MINUTES = 5
MAX_VERIFY_ATTEMPTS = 5
RESEND_COOLDOWN_SECONDS = 60


def hash_otp(code):
    return hashlib.sha256(
        code.encode("utf-8")
    ).hexdigest()


def generate_otp():
    return "".join(
        str(secrets.randbelow(10))
        for _ in range(OTP_LENGTH)
    )


def create_phone_otp(customer):
    now = timezone.now()

    recent_otp = (
        PhoneVerificationOTP.objects
        .filter(
            customer=customer,
            created_at__gte=now - timedelta(
                seconds=RESEND_COOLDOWN_SECONDS
            ),
            is_used=False,
        )
        .first()
    )

    if recent_otp:
        raise ValueError(
            "لطفاً قبل از درخواست کد جدید کمی صبر کنید."
        )

    code = generate_otp()

    PhoneVerificationOTP.objects.filter(
        customer=customer,
        is_used=False,
    ).update(
        is_used=True
    )

    otp = PhoneVerificationOTP.objects.create(
        customer=customer,
        code_hash=hash_otp(code),
        expires_at=now + timedelta(
            minutes=OTP_EXPIRY_MINUTES
        ),
    )

    message = (
        f"کد تأیید شما: {code}"
    )

    sms_provider = get_sms_provider()

    sms_provider.send_sms(
        customer.phone,
        message,
    )

    return otp, code


def verify_phone_otp(customer, code):
    otp = (
        PhoneVerificationOTP.objects
        .filter(
            customer=customer,
            is_used=False,
        )
        .first()
    )

    if not otp:
        return False, "کد تأیید معتبر نیست."

    if timezone.now() >= otp.expires_at:
        otp.is_used = True
        otp.save(update_fields=["is_used"])
        return False, "کد تأیید منقضی شده است."

    if otp.attempts >= MAX_VERIFY_ATTEMPTS:
        otp.is_used = True
        otp.save(update_fields=["is_used"])
        return False, "تعداد تلاش‌های مجاز تمام شده است."

    otp.attempts += 1

    if not secrets.compare_digest(
        otp.code_hash,
        hash_otp(code),
    ):
        otp.save(update_fields=["attempts"])
        return False, "کد تأیید اشتباه است."

    otp.is_used = True
    otp.save(update_fields=["attempts", "is_used"])

    customer.phone_verified = True
    customer.save(update_fields=["phone_verified"])

    return True, "شماره تلفن با موفقیت تأیید شد."