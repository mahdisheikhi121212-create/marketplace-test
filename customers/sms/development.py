from .base import SMSProvider


class DevelopmentSMSProvider(SMSProvider):
    def send_sms(self, phone, message):
        print(
            f"[DEVELOPMENT SMS] "
            f"To: {phone} | Message: {message}"
        )

        return {
            "success": True,
            "provider": "development",
        }