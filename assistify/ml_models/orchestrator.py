import logging
import torch
import gc
import os
import psutil
from typing import Dict, Any, List, Optional

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ModelOrchestrator:
    _instance = None
    _models = {}
    
    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(ModelOrchestrator, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if hasattr(self, '_initialized') and self._initialized:
            return
        
        logger.info("Initializing Stable Hybrid Model Orchestrator...")
        self._initialized = True
        # Initialize recommendation model during orchestrator init.
        self._get_model("recommendation")

    def _get_model(self, model_type: str):
        """Lazy load models with absolute imports and memory safety."""
        if model_type in self._models and self._models[model_type] is not None:
            return self._models[model_type]

        try:
            # Check memory
            available_ram_gb = psutil.virtual_memory().available / (1024**3)
            
            # Recommendation model is lightweight for inference
            if model_type == 'recommendation':
                from assistify.ml_models.product_recommendation.model import ProductRecommendationModel
                if 'recommendation' not in self._models or self._models['recommendation'] is None:
                    self._models['recommendation'] = ProductRecommendationModel()
                return self._models['recommendation']

            # Threshold for heavy models (T5, MARBERT, RoBERTa)
            # Reduced threshold for testing environments if FORCE_ML is set
            force_ml = os.environ.get('FORCE_ML', 'False').lower() == 'true'
            threshold = 0.5 if force_ml else 1.5
            
            if available_ram_gb < threshold:
                logger.warning(f"Low memory ({available_ram_gb:.2f}GB). Skipping heavy model {model_type}. Threshold: {threshold}GB")
                return None

            if model_type == 'intent':
                from assistify.ml_models.intent_classification.model import IntentClassificationModel
                self._models['intent'] = IntentClassificationModel()
            elif model_type == 'sentiment':
                from assistify.ml_models.sentiment_analysis.model import SentimentAnalysisModel
                self._models['sentiment'] = SentimentAnalysisModel()
            elif model_type == 'response':
                from assistify.ml_models.response_generation.model import ResponseGenerationModel
                self._models['response'] = ResponseGenerationModel()
            
            return self._models.get(model_type)
        except Exception as e:
            logger.error(f"Failed to load {model_type} model: {e}", exc_info=True)
            return None

    def process_message(self, message: str = "", user_id: Optional[int] = None, **kwargs) -> Dict[str, Any]:
        """Main pipeline optimized for maximum stability and zero-crash."""
        text = message or kwargs.get('text', '')
        if not text:
            return {'success': False, 'error': 'Empty message'}
            
        logger.info(f"Processing message: {text}")
        
        # 1. Intent Classification
        intent_data = self._classify_intent_safe(text)
        
        # 2. Sentiment Analysis
        sentiment_data = self._analyze_sentiment_safe(text)
        
        # 3. Recommendations
        recommendations, rec_method = self._get_recommendations_stable(
            user_id=user_id, 
            intent=intent_data['intent'],
            query=text
        )
        
        # 4. Response Generation
        context = {
            'intent': intent_data['intent'],
            'sentiment': sentiment_data['sentiment'],
            'recommendations': recommendations
        }
        response_data = self._generate_response_safe(text, context)
        
        # Final cleanup
        gc.collect()
        if torch.cuda.is_available():
            torch.cuda.empty_cache()

        return {
            'success': True,
            'response': response_data['response'],
            'intent': intent_data['intent'],
            'sentiment': sentiment_data['sentiment'],
            'recommendations': recommendations,
            'intent_confidence': intent_data['confidence'],
            'sentiment_confidence': sentiment_data['confidence'],
            'metadata': {
                'intent_label_idx': intent_data.get('label_idx'),
                'sentiment_label_idx': sentiment_data.get('label_idx'),
                'response_confidence': response_data.get('confidence', 0.0),
                'recommendation_method': rec_method
            }
        }

    def _classify_intent_safe(self, message: str) -> Dict[str, Any]:
        try:
            model = self._get_model('intent')
            if model:
                return model.predict(message)
        except Exception as e:
            logger.error(f"Intent prediction error: {e}")
        return self._fallback_intent(message)

    def _analyze_sentiment_safe(self, message: str) -> Dict[str, Any]:
        try:
            model = self._get_model('sentiment')
            if model:
                return model.predict(message)
        except Exception as e:
            logger.error(f"Sentiment prediction error: {e}")
        return self._fallback_sentiment(message)

    def _get_recommendations_stable(self, user_id: Optional[int], intent: str, query: str):
        """Stable recommendation system that avoids memory-heavy training on-the-fly."""
        method = "fallback_database_search"
        recs = []
        
        # Try ML Recommendation Model
        try:
            model = self._get_model('recommendation')
            if model:
                rec_result = model.predict(user_id=user_id, query=query, intent=intent)
                recs = rec_result.get('recommendations', [])
                method = rec_result.get('method', 'ml_recommendation')
        except Exception as e:
            logger.error(f"Recommendation prediction failed: {e}")
        
        # If ML failed or returned nothing, use high-quality DB search
        if not recs:
            try:
                from django.apps import apps
                Product = apps.get_model('products', 'Product')
                from django.db.models import Q
                
                # Smart search in DB
                recs_objs = Product.objects.filter(
                    Q(is_active=True) & (
                        Q(name__icontains=query) | 
                        Q(description__icontains=query) |
                        Q(name__icontains=intent) | 
                        Q(description__icontains=intent)
                    )
                ).distinct()
                
                if not recs_objs.exists():
                    recs_objs = Product.objects.filter(is_active=True)[:5]
                
                recs = [{
                    'product_id': p.id,
                    'name': p.name,
                    'price': float(p.price),
                    'currency': p.currency,
                    'description': p.description,
                    'emoji': p.emoji or '📦',
                    'score': 0.5
                } for p in recs_objs[:5]]
                
                method = "database_fallback"
            except Exception as e:
                logger.error(f"DB Search failed: {e}")
                recs = []
            
        return recs, method

    def _generate_response_safe(self, message: str, context: Dict[str, Any]) -> Dict[str, Any]:
        try:
            model = self._get_model('response')
            if model:
                return model.generate(message, context)
        except Exception as e:
            logger.error(f"Response generation error: {e}")
        return {'response': self._fallback_response(context), 'confidence': 0.0}

    def _fallback_intent(self, text: str) -> Dict[str, Any]:
        text = text.lower()
        if any(w in text for w in ['buy', 'purchase', 'order', 'شراء', 'طلب']):
            return {'intent': 'purchase', 'confidence': 0.5, 'label_idx': 7}
        if any(w in text for w in ['hello', 'hi', 'hey', 'أهلا', 'مرحبا']):
            return {'intent': 'greeting', 'confidence': 0.5, 'label_idx': 0}
        return {'intent': 'inquiry', 'confidence': 0.1, 'label_idx': 1}

    def _fallback_sentiment(self, text: str) -> Dict[str, Any]:
        text = text.lower()
        if any(w in text for w in ['good', 'great', 'thanks', 'جيد', 'شكرا']):
            return {'sentiment': 'positive', 'confidence': 0.5, 'label_idx': 2}
        if any(w in text for w in ['bad', 'poor', 'issue', 'سيء', 'مشكلة']):
            return {'sentiment': 'negative', 'confidence': 0.5, 'label_idx': 0}
        return {'sentiment': 'neutral', 'confidence': 0.1, 'label_idx': 1}

    def _fallback_response(self, context: Dict[str, Any]) -> str:
        intent = context.get('intent', 'inquiry')
        recs = context.get('recommendations', [])
        
        responses = {
            'greeting': "Hello! How can I assist you with our medical products today?",
            'purchase': "I can certainly help you with your purchase. Here are some products you might like.",
            'inquiry': "I'm here to answer any questions you have about our medical equipment.",
            'fallback': "I understand. Please let me know how I can help you further."
        }
        res = responses.get(intent, responses['fallback'])
        if recs:
            res += f" I recommend checking out the {recs[0]['name']}."
        return res

    def get_model_status(self) -> Dict[str, Any]:
        import psutil
        available_ram_gb = psutil.virtual_memory().available / (1024**3)
        return {
            'status': 'operational',
            'memory_available_gb': round(available_ram_gb, 2),
            'models_loaded': list(self._models.keys())
        }
