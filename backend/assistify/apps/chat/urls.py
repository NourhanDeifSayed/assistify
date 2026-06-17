from django.urls import path
from .feedback_views import ConversationFeedbackView

from .analytics_views import AnalyticsOverviewView

from .ml_views import (
    IntentClassificationView,
    MLPipelineView,
    ModelStatusView,
    RecommendationView,
    SentimentAnalysisView,
)
from .views import (
    ChatView,
    ConversationHistoryView,
    WhatsAppWebhookView,
)

urlpatterns = [
    path(
        "",
        ChatView.as_view(),
        name="chat",
    ),
    path(
        "feedback/",
        ConversationFeedbackView.as_view(),
        name="conversation-feedback",
    ),
    path(
        "whatsapp/webhook/",
        WhatsAppWebhookView.as_view(),
        name="whatsapp-webhook",
    ),
    path(
        "history/<int:conversation_id>/",
        ConversationHistoryView.as_view(),
        name="chat-history",
    ),
    path(
        "ml/pipeline/",
        MLPipelineView.as_view(),
        name="ml-pipeline",
    ),
    path(
        "ml/intent/",
        IntentClassificationView.as_view(),
        name="intent-classification",
    ),
    path(
        "ml/sentiment/",
        SentimentAnalysisView.as_view(),
        name="sentiment-analysis",
    ),
    path(
        "ml/recommendations/",
        RecommendationView.as_view(),
        name="recommendations",
    ),
    path(
        "ml/status/",
        ModelStatusView.as_view(),
        name="model-status",
    ),
    
   path(
    "analytics/",
    AnalyticsOverviewView.as_view(),
    name="analytics-overview",
   ),


]