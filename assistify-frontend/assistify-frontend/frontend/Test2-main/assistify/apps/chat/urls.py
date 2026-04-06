from django.urls import path
from .views import ChatView, ConversationHistoryView

urlpatterns = [
    path("", ChatView.as_view(), name="chat"),
    path("history/<int:conversation_id>/", ConversationHistoryView.as_view(), name="chat-history"),
]
