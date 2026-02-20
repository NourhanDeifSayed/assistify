from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'ml_models'))

from .models import Message, Conversation, Response as ResponseModel
from .serializers import MessageSerializer, ConversationSerializer
from intent_classification.model import IntentClassifier
from sentiment_analysis.model import SentimentAnalyzer
from response_generation.model import ResponseGenerator
from product_recommendation.model import ProductRecommender

class MessageViewSet(viewsets.ModelViewSet):
    queryset = Message.objects.all()
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated]
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.intent_classifier = IntentClassifier()
        self.sentiment_analyzer = SentimentAnalyzer()
        self.response_generator = ResponseGenerator()
        self.product_recommender = ProductRecommender()
    
    @action(detail=False, methods=['post'])
    def process_message(self, request):
        content = request.data.get('content')
        conversation_id = request.data.get('conversation_id')
        
        if not content or not conversation_id:
            return Response(
                {'error': 'content and conversation_id are required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        conversation = get_object_or_404(Conversation, id=conversation_id)
        
        intent_result = self.intent_classifier.predict(content)
        sentiment_result = self.sentiment_analyzer.predict(content)
        response_result = self.response_generator.generate(
            content,
            intent=intent_result['intent'],
            sentiment=sentiment_result['sentiment']
        )
        
        message = Message.objects.create(
            conversation=conversation,
            sender='customer',
            content=content,
            intent=intent_result['intent'],
            sentiment=sentiment_result['sentiment'],
            confidence=(intent_result['confidence'] + sentiment_result['confidence']) / 2,
            metadata={
                'intent_confidence': intent_result['confidence'],
                'sentiment_confidence': sentiment_result['confidence'],
                'sentiment_intensity': sentiment_result['intensity']
            }
        )
        
        ResponseModel.objects.create(
            message=message,
            content=response_result['response'],
            model_used='T5-Base',
            confidence=0.85
        )
        
        return Response({
            'message_id': message.id,
            'intent': intent_result['intent'],
            'sentiment': sentiment_result['sentiment'],
            'response': response_result['response'],
            'confidence': message.confidence
        }, status=status.HTTP_201_CREATED)
    
    @action(detail=False, methods=['get'])
    def get_conversation_messages(self, request):
        conversation_id = request.query_params.get('conversation_id')
        
        if not conversation_id:
            return Response(
                {'error': 'conversation_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        messages = Message.objects.filter(conversation_id=conversation_id).order_by('created_at')
        serializer = self.get_serializer(messages, many=True)
        
        return Response(serializer.data)

class ConversationViewSet(viewsets.ModelViewSet):
    queryset = Conversation.objects.all()
    serializer_class = ConversationSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Conversation.objects.filter(customer__user=self.request.user)
    
    @action(detail=False, methods=['post'])
    def create_conversation(self, request):
        customer_id = request.data.get('customer_id')
        channel = request.data.get('channel', 'web')
        
        conversation = Conversation.objects.create(
            customer_id=customer_id,
            channel=channel,
            status='active'
        )
        
        serializer = self.get_serializer(conversation)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['post'])
    def close_conversation(self, request, pk=None):
        conversation = self.get_object()
        conversation.status = 'closed'
        conversation.save()
        
        serializer = self.get_serializer(conversation)
        return Response(serializer.data)
