from django.contrib.auth.models import User

from rest_framework import serializers

from .models import CustomerProfile


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            "id",
            "username",
            "first_name",
            "last_name",
            "email",
        )


class CustomerProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = CustomerProfile
        fields = (
            "id",
            "user",
            "phone",
            "phone_verified",
            "created_at",
        )


class CustomerRegisterSerializer(serializers.ModelSerializer):
    username = serializers.CharField(
        write_only=True,
        min_length=3,
        max_length=30,
    )

    password = serializers.CharField(
        write_only=True,
        min_length=12,
    )

    email = serializers.EmailField(
        required=False,
        allow_blank=True,
    )

    def validate_username(self, value):
        if (
            not value[0].isalpha()
            or not value[0].isascii()
        ):
            raise serializers.ValidationError(
                "نام کاربری باید با یک حرف انگلیسی شروع شود."
            )

        for character in value:
            if not (
                character.isascii()
                and (
                    character.isalnum()
                    or character in "_-"
                )
            ):
                raise serializers.ValidationError(
                    (
                        "نام کاربری فقط می‌تواند شامل "
                        "حروف انگلیسی، اعداد، _ و - باشد."
                    )
                )

        if User.objects.filter(
            username=value
        ).exists():
            raise serializers.ValidationError(
                "این نام کاربری قبلاً ثبت شده است."
            )

        return value

    def validate_password(self, value):
        if len(value) < 12:
            raise serializers.ValidationError(
                "رمز عبور باید حداقل ۱۲ کاراکتر باشد."
            )

        if not any(
            char.isupper()
            for char in value
        ):
            raise serializers.ValidationError(
                (
                    "رمز عبور باید حداقل یک "
                    "حرف انگلیسی بزرگ داشته باشد."
                )
            )

        if not any(
            char.islower()
            for char in value
        ):
            raise serializers.ValidationError(
                (
                    "رمز عبور باید حداقل یک "
                    "حرف انگلیسی کوچک داشته باشد."
                )
            )

        if not any(
            char.isdigit()
            for char in value
        ):
            raise serializers.ValidationError(
                "رمز عبور باید حداقل یک عدد داشته باشد."
            )

        special_characters = (
            "!@#$%^&*()_+-=[]{}|;:',.<>?/`~\\\""
        )

        if not any(
            char in special_characters
            for char in value
        ):
            raise serializers.ValidationError(
                (
                    "رمز عبور باید حداقل یک "
                    "کاراکتر ویژه داشته باشد."
                )
            )

        return value

    def validate_phone(self, value):
        value = value.strip()

        if not value:
            return value

        if CustomerProfile.objects.filter(
            phone=value
        ).exists():
            raise serializers.ValidationError(
                "این شماره تلفن قبلاً ثبت شده است."
            )

        return value

    class Meta:
        model = CustomerProfile
        fields = (
            "username",
            "password",
            "email",
            "phone",
        )

    def create(self, validated_data):
        username = validated_data.pop(
            "username"
        )

        password = validated_data.pop(
            "password"
        )

        email = validated_data.pop(
            "email",
            "",
        )

        user = User.objects.create_user(
            username=username,
            password=password,
            email=email,
        )

        customer = CustomerProfile.objects.create(
            user=user,
            **validated_data,
        )

        return customer


class SendPhoneOTPSerializer(serializers.Serializer):
    phone = serializers.CharField(
        min_length=10,
        max_length=20,
    )

    def validate_phone(self, value):
        return value.strip()


class VerifyPhoneOTPSerializer(serializers.Serializer):
    phone = serializers.CharField(
        min_length=10,
        max_length=20,
    )

    code = serializers.CharField(
        min_length=6,
        max_length=6,
    )

    def validate_phone(self, value):
        return value.strip()

    def validate_code(self, value):
        if not value.isdigit():
            raise serializers.ValidationError(
                "کد تأیید باید فقط شامل اعداد باشد."
            )

        return value