from django.contrib.auth import authenticate
from django.contrib.auth.models import User

from rest_framework import serializers

from .models import Profile


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True
    )

    class Meta:
        model = User
        fields = [
            "username",
            "email",
            "password",
        ]

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data["username"],
            email=validated_data.get(
                "email",
                ""
            ),
            password=validated_data["password"],
        )

        return user


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()

    password = serializers.CharField(
        write_only=True
    )

    def validate(self, data):
        username = data.get(
            "username"
        )

        password = data.get(
            "password"
        )

        user = authenticate(
            username=username,
            password=password,
        )

        if not user:
            raise serializers.ValidationError(
                "نام کاربری یا رمز عبور اشتباه است."
            )

        data["user"] = user

        return data


class ProfileSerializer(serializers.ModelSerializer):
    username = serializers.CharField(
        source="user.username",
        read_only=True,
    )

    email = serializers.EmailField(
        source="user.email",
        read_only=True,
    )

    role = serializers.SerializerMethodField()

    class Meta:
        model = Profile

        fields = [
            "username",
            "email",
            "phone",
            "avatar",
            "role",
        ]

    def get_role(self, obj):
        user = obj.user

        if user.is_staff:
            return "admin"

        if hasattr(
            user,
            "seller_profile",
        ):
            return "seller"

        if hasattr(
            user,
            "customer_profile",
        ):
            return "customer"

        return "user"


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(
        write_only=True
    )

    new_password = serializers.CharField(
        write_only=True
    )

    def validate(self, data):
        user = self.context["request"].user

        if not user.check_password(
            data["old_password"]
        ):
            raise serializers.ValidationError(
                "رمز عبور فعلی اشتباه است."
            )

        return data