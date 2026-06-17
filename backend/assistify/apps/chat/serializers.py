from rest_framework import serializers
from assistify.apps.chat.models import (
    Conversation,
    ConversationFeedback,
)

class ConversationFeedbackSerializer(serializers.ModelSerializer):
    conversation = serializers.PrimaryKeyRelatedField(
        read_only=True,
    )

    conversation_id = serializers.IntegerField(
        write_only=True,
    )

    rating_label = serializers.CharField(
        source="get_rating_display",
        read_only=True,
    )

    class Meta:
        model = ConversationFeedback
        fields = [
            "id",
            "conversation",
            "conversation_id",
            "rating",
            "rating_label",
            "comment",
            "created_at",
            "updated_at",
        ]

        read_only_fields = [
            "id",
            "conversation",
            "rating_label",
            "created_at",
            "updated_at",
        ]

    def validate_comment(self, value):
        value = value.strip()
        if len(value) > 1000:
            raise serializers.ValidationError(
                "Comment cannot exceed 1000 characters."
            )
        return value

    def validate(self, attrs):
        request = self.context.get("request")
        conversation_id = attrs.get("conversation_id")

        if not request or not request.user.is_authenticated:
            raise serializers.ValidationError(
                "Authentication is required to submit feedback."
            )

        try:
            conversation = Conversation.objects.get(
                id=conversation_id,
            )
        except Conversation.DoesNotExist:
            raise serializers.ValidationError(
                {
                    "conversation_id": (
                        "Conversation was not found."
                    )
                }
            )

        if (
            conversation.user_id != request.user.id
            and not request.user.is_staff
        ):
            raise serializers.ValidationError(
                {
                    "conversation_id": (
                        "You cannot rate this conversation."
                    )
                }
            )

        if ConversationFeedback.objects.filter(
            conversation=conversation,
        ).exists():
            raise serializers.ValidationError(
                {
                    "conversation_id": (
                        "Feedback already exists for this conversation."
                    )
                }
            )

        attrs["conversation"] = conversation
        attrs.pop("conversation_id", None)

        return attrs