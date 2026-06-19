import logging
import torch
import gc
from typing import Dict, Any
from transformers import AutoTokenizer, AutoModelForSequenceClassification

logger = logging.getLogger(__name__)

class SentimentAnalysisModel:
    SENTIMENT_MAP = {
        0: 'negative',
        1: 'neutral',
        2: 'positive'
    }

    def __init__(self, model_name: str = "cardiffnlp/twitter-roberta-base-sentiment"):
        self.model_name = model_name
        self.tokenizer = None
        self.model = None
        self.device = torch.device("cpu") 
        self._load_model()

    def _load_model(self):
        try:
            logger.info(f"Loading Sentiment Analysis model: {self.model_name}")
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            self.model = AutoModelForSequenceClassification.from_pretrained(
                self.model_name,
                low_cpu_mem_usage=True,
                device_map=None,
                torch_dtype=torch.float32 
            )
            self.model.to(self.device)
            self.model.eval()
        except Exception as e:
            logger.error(f"Error loading Sentiment model: {e}")
            self.model = None

    def predict(self, text: str) -> Dict[str, Any]:
        # First, check for keyword matches (especially for Arabic)
        keyword_result = self._keyword_only_predict(text)
        
        if keyword_result["sentiment"] != "neutral":
            keyword_result["confidence"] = 0.9
            return keyword_result

        if not self.model or not self.tokenizer:
            return keyword_result

        try:
            inputs = self.tokenizer(text, return_tensors="pt", truncation=True, padding=True, max_length=128).to(self.device)
            with torch.no_grad():
                outputs = self.model(**inputs)
                logits = outputs.logits.detach().cpu()
                probs = torch.nn.functional.softmax(logits, dim=-1)
                confidence, label_idx = torch.max(probs, dim=-1)

            sentiment = self.SENTIMENT_MAP.get(label_idx.item(), 'neutral')
            
            return {
                'sentiment': sentiment,
                'confidence': float(confidence.item()),
                'label_idx': int(label_idx.item())
            }
            
        except Exception as e:
            logger.error(f"Error in Sentiment prediction: {e}")
            return self._keyword_only_predict(text)

    def _keyword_only_predict(self, text: str) -> Dict[str, Any]:
        text_lower = text.lower()
        
        # Expanded Arabic and English positive words
        positive_words = [
            "good",
            "great",
            "happy",
            "excellent",
            "thanks",
            "thank",
            "love",
            "جيد",
            "جميل",
            "رائع",
            "ممتاز",
            "حلو",
            "كويس",
            "سعيد",
            "أحب",
            "احب",
            "شكرا",
            "شكرًا",
        ]
        
        # Expanded Arabic and English negative words
        negative_words = [
            "bad",
            "poor",
            "unhappy",
            "broken",
            "wrong",
            "issue",
            "terrible",
            "hate",
            "سيء",
            "سيئ",
            "وحش",
            "زعلان",
            "غاضب",
            "مكسور",
            "مشكلة",
            "خطأ",
            "رديء",
            "لا أحب",
            "مش عاجبني",
        ]
        
        # Count matches for more accurate detection
        positive_matches = sum(1 for word in positive_words if word in text_lower)
        negative_matches = sum(1 for word in negative_words if word in text_lower)
        
        if positive_matches > negative_matches:
            return {'sentiment': 'positive', 'confidence': 0.7, 'label_idx': 2}
        if negative_matches > positive_matches:
            return {'sentiment': 'negative', 'confidence': 0.7, 'label_idx': 0}
        
        # Fallback to single word detection
        if any(w in text_lower for w in positive_words):
            return {'sentiment': 'positive', 'confidence': 0.5, 'label_idx': 2}
        if any(w in text_lower for w in negative_words):
            return {'sentiment': 'negative', 'confidence': 0.5, 'label_idx': 0}
            
        return {'sentiment': 'neutral', 'confidence': 0.1, 'label_idx': 1}

    def __del__(self):
        if hasattr(self, 'model'): 
            del self.model
        if hasattr(self, 'tokenizer'): 
            del self.tokenizer
        gc.collect()