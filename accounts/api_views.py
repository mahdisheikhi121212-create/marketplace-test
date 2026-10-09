from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated

from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError

from .serializers import (
    LoginSerializer,
    ProfileSerializer,
    ChangePasswordSerializer,
)

from .models import Profile


class LoginAPIView(APIView):

    permission_classes = [
        AllowAny
    ]

    def post(self, request):

        serializer = LoginSerializer(
            data=request.data
        )

        serializer.is_valid(
            raise_exception=True
        )

        user = serializer.validated_data["user"]

        refresh = RefreshToken.for_user(
            user
        )

        return Response(
            {
                "refresh": str(refresh),
                "access": str(
                    refresh.access_token
                ),
            },
            status=status.HTTP_200_OK
        )


class LogoutAPIView(APIView):

    permission_classes = [
        IsAuthenticated
    ]

    def post(self, request):

        refresh_token = request.data.get(
            "refresh"
        )

        if not refresh_token:

            return Response(
                {
                    "error": (
                        "Refresh token "
                        "ارسال نشده است."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        try:

            token = RefreshToken(
                refresh_token
            )

            token.blacklist()

            return Response(
                {
                    "message": (
                        "با موفقیت خارج شدید."
                    )
                },
                status=status.HTTP_205_RESET_CONTENT
            )

        except TokenError as error:

            return Response(
                {
                    "error": (
                        "Refresh token "
                        "نامعتبر یا منقضی است."
                    ),
                    "detail": str(error),
                },
                status=status.HTTP_400_BAD_REQUEST
            )


class MeAPIView(APIView):

    permission_classes = [
        IsAuthenticated
    ]

    def get(self, request):

        user = request.user

        return Response(
            {
                "id": user.id,
                "username": user.username,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "email": user.email,
                "is_staff": user.is_staff,
            },
            status=status.HTTP_200_OK
        )


class ProfileAPIView(APIView):

    permission_classes = [
        IsAuthenticated
    ]

    def get(self, request):

        profile, created = (
            Profile.objects.get_or_create(
                user=request.user
            )
        )

        serializer = ProfileSerializer(
            profile
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )

    def patch(self, request):

        profile, created = (
            Profile.objects.get_or_create(
                user=request.user
            )
        )

        serializer = ProfileSerializer(
            profile,
            data=request.data,
            partial=True
        )

        serializer.is_valid(
            raise_exception=True
        )

        serializer.save()

        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )


class ChangePasswordAPIView(APIView):

    permission_classes = [
        IsAuthenticated
    ]

    def post(self, request):

        serializer = ChangePasswordSerializer(
            data=request.data,
            context={
                "request": request
            }
        )

        serializer.is_valid(
            raise_exception=True
        )

        user = request.user

        user.set_password(
            serializer.validated_data[
                "new_password"
            ]
        )

        user.save()

        return Response(
            {
                "message": (
                    "رمز عبور "
                    "با موفقیت تغییر کرد."
                )
            },
            status=status.HTTP_200_OK
        )
