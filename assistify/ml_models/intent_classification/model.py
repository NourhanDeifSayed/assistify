import logging
import torch
import numpy as np
import gc
from typing import Dict, Any
from transformers import AutoTokenizer, AutoModelForSequenceClassification

logger = logging.getLogger(__name__)

class IntentClassificationModel:
    
    INTENT_MAP = {
        0: 'inquiry',
        1: 'greeting',
        2: 'offer',
        3: 'order_tracking',
        4: 'payment',
        5: 'return',
        6: 'product_search',
        7: 'purchase',
        8: 'complaint',
        9: 'support',
        10: 'feedback',
        11: 'goodbye'
    }

    def __init__(self, model_name: str = "UBC-NLP/MARBERTv2"):
        self.model_name = model_name
        self.tokenizer = None
        self.model = None
        self.device = torch.device("cpu") # Force CPU for stability on Windows
        self._load_model()

    def _load_model(self):
        try:
            logger.info(f"Loading Intent Classification model: {self.model_name}")
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            
            # Use aggressive memory saving for loading
            self.model = AutoModelForSequenceClassification.from_pretrained(
                self.model_name, 
                num_labels=12,
                low_cpu_mem_usage=True, # Enable this but handle meta device if it occurs
                device_map=None,
                torch_dtype=torch.float32 # Ensure standard float32 for CPU
            )
            self.model.to(self.device)
            self.model.eval()
        except Exception as e:
            logger.error(f"Error loading Intent model: {e}")
            # Fallback to a very basic initialization if it fails
            self.model = None

    def predict(self, text: str) -> Dict[str, Any]:
        if not self.model or not self.tokenizer:
            return self._keyword_only_predict(text)

        try:
            inputs = self.tokenizer(text, return_tensors="pt", truncation=True, padding=True, max_length=128).to(self.device)
            with torch.no_grad():
                outputs = self.model(**inputs)
                logits = outputs.logits.detach().cpu()
                probs = torch.nn.functional.softmax(logits, dim=-1).numpy()[0]
                
            # Keyword-based boosting
            text_lower = text.lower()
            boosted_probs = probs.copy()
            
            keywords = {
                'greeting': ['hello', 'hi', 'hey', 'مرحبا', 'اهلا'],
                'purchase': ['buy', 'order', 'purchase', 'get', 'price', 'cost', 'شراء', 'سعر'],
                'order_tracking': ['track', 'where', 'status', 'delivery', 'shipping', 'تتبع', 'شحن'],
                'return': ['return', 'refund', 'exchange', 'back', 'استرجاع', 'استبدال'],
                'product_search': ['find', 'search', 'look', 'device', 'monitor', 'oximeter', 'بحث', 'جهاز'],
                'payment': ['pay', 'card', 'cash', 'visa', 'دفع', 'كارت'],
                'complaint': ['broken', 'bad', 'unhappy', 'wrong', 'issue', 'مشكلة', 'سيء'],
                'goodbye': ['bye', 'thanks', 'thank', 'شكرا', 'مع السلامة']
            }
            
            inv_map = {v: k for k, v in self.INTENT_MAP.items()}
            for intent_name, words in keywords.items():
                if any(word in text_lower for word in words):
                    idx = inv_map.get(intent_name)
                    if idx is not None:
                        boosted_probs[idx] += 0.4
            
            boosted_probs = boosted_probs / boosted_probs.sum()
            label_idx = np.argmax(boosted_probs)
            confidence = boosted_probs[label_idx]
            intent = self.INTENT_MAP.get(label_idx, 'inquiry')
            
            return {
                'intent': intent,
                'confidence': float(confidence),
                'label_idx': int(label_idx)
            }
        except Exception as e:
            logger.error(f"Error in Intent prediction: {e}")
            return self._keyword_only_predict(text)

    def _keyword_only_predict(self, text: str) -> Dict[str, Any]:
        """Ultra-lightweight fallback if model fails to load."""
        text_lower = text.lower()
        mapping = {
            'greeting': ['hello', 'hi', 'hey', 'مرحبا', 'اهلا'],
            'purchase': ['buy', 'order', 'purchase', 'get', 'price', 'cost', 'شراء', 'سعر'],
            'order_tracking': ['track', 'where', 'status', 'delivery', 'shipping', 'تتبع', 'شحن'],
            'return': ['return', 'refund', 'exchange', 'back', 'استرجاع', 'استبدال'],
            'product_search': ['find', 'search', 'look', 'device', 'monitor', 'oximeter', 'بحث', 'جهاز'],
            'payment': ['pay', 'card', 'cash', 'visa', 'دفع', 'كارت'],
            'complaint': ['broken', 'bad', 'unhappy', 'wrong', 'issue', 'مشكلة', 'سيء'],
            'goodbye': ['bye', 'thanks', 'thank', 'شكرا', 'مع السلامة']
        }
        for intent, words in mapping.items():
            if any(w in text_lower for w in words):
                return {'intent': intent, 'confidence': 0.5, 'label_idx': None}
        return {'intent': 'inquiry', 'confidence': 0.1, 'label_idx': None}

    def __del__(self):
        """Ensure memory is cleared when object is deleted."""
        if hasattr(self, 'model'): del self.model
        if hasattr(self, 'tokenizer'): del self.tokenizer
        gc.collect()
