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
        # Prevent privilege escalation: check raw initial data for admin fields
        forbidden_fields = {"role", "is_staff", "is_superuser", "is_admin"}
        if self.initial_data:
            sent_forbidden = forbidden_fields.intersection(self.initial_data.keys())
            if sent_forbidden:
                raise serializers.ValidationError(
                    "You cannot specify admin roles or flags during registration."
                )

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
            "is_staff",
            "is_superuser",
            "phone",
            "address",
            "date_joined",
        )
        read_only_fields = (
            "id",
            "email",
            "role",
            "is_staff",
            "is_superuser",
            "date_joined",
        )

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        data["user"] = UserProfileSerializer(self.user).data
        return data


class AdminUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            "id",
            "username",
            "email",
            "role",
            "is_staff",
            "is_superuser",
            "is_active",
            "phone",
            "address",
            "date_joined",
        )
        read_only_fields = ("id", "email", "date_joined")


class AdminUserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            "role",
            "is_staff",
            "is_superuser",
            "is_active",
            "phone",
            "address",
        )

    def validate(self, attrs):
        request = self.context.get("request")
        if not request or not request.user.is_authenticated:
            raise serializers.ValidationError("Authentication required.")

        request_user = request.user
        instance = self.instance

        if instance and instance.is_superuser and not request_user.is_superuser:
            raise serializers.ValidationError("Only superusers can modify other superusers.")

        is_staff_val = attrs.get("is_staff")
        is_superuser_val = attrs.get("is_superuser")
        role_val = attrs.get("role")

        if not request_user.is_superuser:
            if is_superuser_val is True and (instance is None or not instance.is_superuser):
                raise serializers.ValidationError("Only superusers can grant superuser status.")
            if is_staff_val is True and (instance is None or not instance.is_staff):
                raise serializers.ValidationError("Only superusers can grant staff status.")
            if role_val == User.Role.ADMIN and (instance is None or instance.role != User.Role.ADMIN):
                raise serializers.ValidationError("Only superusers can assign the Admin role.")

        return attrs