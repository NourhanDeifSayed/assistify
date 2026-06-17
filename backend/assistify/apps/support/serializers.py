from rest_framework import serializers

from .models import SupportTicket


class SupportTicketCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = SupportTicket
        fields = (
            "id",
            "ticket_number",
            "order",
            "conversation",
            "issue_type",
            "description",
            "priority",
            "status",
            "created_at",
        )
        read_only_fields = (
            "id",
            "ticket_number",
            "status",
            "created_at",
        )

    def validate_description(self, value):
        value = value.strip()

        if len(value) < 10:
            raise serializers.ValidationError(
                "Please provide at least 10 characters describing the issue."
            )

        return value

    def validate(self, attrs):
        request = self.context.get("request")

        if not request or not request.user.is_authenticated:
            raise serializers.ValidationError(
                "Authentication is required to create a support ticket."
            )

        user = request.user
        order = attrs.get("order")
        conversation = attrs.get("conversation")

        if order and not user.is_staff and order.user_id != user.id:
            raise serializers.ValidationError(
                {"order": "You cannot create a ticket for this order."}
            )

        if (
            conversation
            and not user.is_staff
            and conversation.user_id != user.id
        ):
            raise serializers.ValidationError(
                {
                    "conversation":
                        "You cannot attach this conversation to the ticket."
                }
            )

        return attrs

    def create(self, validated_data):
        request = self.context["request"]

        return SupportTicket.objects.create(
            user=request.user,
            **validated_data,
        )


class SupportTicketDetailSerializer(serializers.ModelSerializer):
    user_email = serializers.EmailField(
        source="user.email",
        read_only=True,
    )
    assigned_to_email = serializers.EmailField(
        source="assigned_to.email",
        read_only=True,
    )
    order_number = serializers.CharField(
        source="order.order_number",
        read_only=True,
    )

    class Meta:
        model = SupportTicket
        fields = (
            "id",
            "ticket_number",
            "user",
            "user_email",
            "order",
            "order_number",
            "conversation",
            "issue_type",
            "description",
            "priority",
            "status",
            "assigned_to",
            "assigned_to_email",
            "admin_response",
            "created_at",
            "updated_at",
            "resolved_at",
        )
        read_only_fields = fields


class SupportTicketUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = SupportTicket
        fields = (
            "status",
            "priority",
            "assigned_to",
        )

    def validate_assigned_to(self, value):
        if value and not value.is_staff:
            raise serializers.ValidationError(
                "The assigned user must be a staff member."
            )

        return value


class SupportTicketReplySerializer(serializers.Serializer):
    response = serializers.CharField(
        min_length=2,
        max_length=5000,
    )
    status = serializers.ChoiceField(
        choices=SupportTicket.Status.choices,
        required=False,
    )

    def validate_response(self, value):
        return value.strip()