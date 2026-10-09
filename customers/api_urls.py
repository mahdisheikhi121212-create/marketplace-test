from django.urls import path

from .api_views import (
    CustomerListAPIView,
    CustomerRegisterAPIView,
    SendPhoneOTPAPIView,
    VerifyPhoneOTPAPIView,
)


urlpatterns = [
    path(
        "",
        CustomerListAPIView.as_view(),
        name="customer-list-api",
    ),

    path(
        "register/",
        CustomerRegisterAPIView.as_view(),
        name="customer-register-api",
    ),

    path(
        "phone/send-otp/",
        SendPhoneOTPAPIView.as_view(),
        name="phone-send-otp",
    ),

    path(
        "phone/verify-otp/",
        VerifyPhoneOTPAPIView.as_view(),
        name="phone-verify-otp",
    ),
]