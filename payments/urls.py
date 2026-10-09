from django.urls import path

from .views import (
    PaymentCallbackAPIView,
    PaymentCreateAPIView,
    PaymentRedirectAPIView,
)


urlpatterns = [
    path(
        "",
        PaymentCreateAPIView.as_view(),
        name="payment-create",
    ),

    path(
        "<int:pk>/redirect/",
        PaymentRedirectAPIView.as_view(),
        name="payment-redirect",
    ),

    path(
        "callback/",
        PaymentCallbackAPIView.as_view(),
        name="payment-callback",
    ),
]