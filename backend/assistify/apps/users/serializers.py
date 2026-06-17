from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


User = get_user_model()


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True,
        min_length=8,
        style={"input_type": "password"},
    )

    password2 = serializers.CharField(
        write_only=True,
        min_length=8,
        label="Confirm password",
        style={"input_type": "password"},
    )

    class Meta:
        model = User
        fields = (
            "id",
            "username",
            "email",
            "password",
            "password2",
            "phone",
            "address",
        )

        read_only_fields = ("id",)

    def validate_email(self, value):
        email = value.strip().lower()

        if User.objects.filter(email__iexact=email).exists():
            raise serializers.ValidationError(
                "A user with this email already exists."
            )

        return email

    def validate(self, attrs):
        password = attrs.get("password")
        password2 = attrs.pop("password2", None)

        if password != password2:
            raise serializers.ValidationError(
                {"password2": "Passwords do not match."}
            )

        return attrs

    def create(self, validated_data):
        return User.objects.create_user(
            **validated_data,
            role=User.Role.CUSTOMER,
        )


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User

        fields = (
            "id",
            "username",
            "email",
            "role",
            "phone",
            "address",
            "date_joined",
        )

        read_only_fields = (
            "id",
            "email",
            "role",
            "date_joined",
        )


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        data["user"] = UserProfileSerializer(self.user).data
        return data