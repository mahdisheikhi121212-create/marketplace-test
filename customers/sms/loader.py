from django.conf import settings
from django.utils.module_loading import import_string


def get_sms_provider():
    provider_class = import_string(
        settings.SMS_PROVIDER
    )

    return provider_class()