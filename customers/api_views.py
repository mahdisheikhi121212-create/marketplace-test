from django.conf import settings

from rest_framework import generics, status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from .models import CustomerProfile
from .permissions import IsAdminOrSuperAdmin
from .serializers import (
    CustomerProfileSerializer,
    CustomerRegisterSerializer,
    SendPhoneOTPSerializer,
    VerifyPhoneOTPSerializer,
)
from .services import (
    create_phone_otp,
    verify_phone_otp,
)


def get_unique_customer_by_phone(phone):
    customers = (
        CustomerProfile.objects
        .filter(
            phone=phone
        )
        .select_related(
            "user"
        )
    )

    customer_count = customers.count()

    if customer_count == 0:
        return None, Response(
            {
                "detail":
                    "شماره تلفن یافت نشد."
            },
            status=status.HTTP_404_NOT_FOUND,
        )

    if customer_count > 1:
        return None, Response(
            {
                "detail": (
                    "این شماره تلفن به بیش از یک "
                    "حساب متصل است و باید ابتدا "
                    "اطلاعات حساب‌ها اصلاح شود."
                )
            },
            status=status.HTTP_409_CONFLICT,
        )

    return customers.first(), None


class CustomerListAPIView(
    generics.ListAPIView
):
    queryset = (
        CustomerProfile.objects
        .select_related(
            "user"
        )
        .all()
    )

    serializer_class = (
        CustomerProfileSerializer
    )

    permission_classes = [
        IsAdminOrSuperAdmin,
    ]


class CustomerRegisterAPIView(
    generics.CreateAPIView
):
    queryset = (
        CustomerProfile.objects.all()
    )

    serializer_class = (
        CustomerRegisterSerializer
    )

    permission_classes = [
        AllowAny,
    ]


class SendPhoneOTPAPIView(
    generics.GenericAPIView
):
    serializer_class = (
        SendPhoneOTPSerializer
    )

    permission_classes = [
        AllowAny,
    ]

    def post(
        self,
        request
    ):
        serializer = self.get_serializer(
            data=request.data
        )

        serializer.is_valid(
            raise_exception=True
        )

        phone = (
            serializer.validated_data[
                "phone"
            ]
        )

        customer, error_response = (
            get_unique_customer_by_phone(
                phone
            )
        )

        if error_response:
            return error_response

        if customer.phone_verified:
            return Response(
                {
                    "detail": (
                        "این شماره تلفن "
                        "قبلاً تأیید شده است."
                    )
                },
                status=(
                    status.HTTP_400_BAD_REQUEST
                ),
            )

        try:
            otp, code = create_phone_otp(
                customer
            )

        except ValueError as exc:
            return Response(
                {
                    "detail": str(exc)
                },
                status=(
                    status
                    .HTTP_429_TOO_MANY_REQUESTS
                ),
            )

        response_data = {
            "detail":
                "کد تأیید ایجاد شد.",
            "expires_at":
                otp.expires_at,
        }

        if (
            settings
            .SMS_SHOW_DEVELOPMENT_CODE
        ):
            response_data[
                "development_code"
            ] = code

        return Response(
            response_data,
            status=status.HTTP_200_OK,
        )


class VerifyPhoneOTPAPIView(
    generics.GenericAPIView
):
    serializer_class = (
        VerifyPhoneOTPSerializer
    )

    permission_classes = [
        AllowAny,
    ]

    def post(
        self,
        request
    ):
        serializer = self.get_serializer(
            data=request.data
        )

        serializer.is_valid(
            raise_exception=True
        )

        phone = (
            serializer.validated_data[
                "phone"
            ]
        )

        code = (
            serializer.validated_data[
                "code"
            ]
        )

        customer, error_response = (
            get_unique_customer_by_phone(
                phone
            )
        )

        if error_response:
            return error_response

        success, message = (
            verify_phone_otp(
                customer,
                code,
            )
        )

        if not success:
            return Response(
                {
                    "detail": message
                },
                status=(
                    status.HTTP_400_BAD_REQUEST
                ),
            )

        return Response(
            {
                "detail": message,
                "phone_verified": True,
            },
            status=status.HTTP_200_OK,
        )