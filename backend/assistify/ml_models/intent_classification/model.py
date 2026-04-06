import logging
import torch
import numpy as np
import gc
import re
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
        11: 'goodbye',
        12: 'recommendation_request',
        13: 'introduce_name',
        14: 'memory_check',
        15: 'product_details',
        16: 'recommendation_reasoning'
    }

    GREETING_WORDS = [
        'مرحبا', 'مرحباً', 'اهلا', 'أهلاً', 'أهلا', 'اهلاً', 'اهلين',
        'السلام عليكم', 'سلام عليكم', 'وعليكم السلام',
        'صباح الخير', 'صباح النور', 'مساء الخير', 'مساء النور',
        'يسعد صباحك', 'يسعد مساك',
        'ازيك', 'ازيكم', 'إزيك', 'إزيكم', 'عامل ايه', 'عاملة ايه',
        'ايه الاخبار', 'إيه الأخبار', 'كيفك', 'كيف حالك', 'عامل إيه',
        'ازيك يا', 'اهلا وسهلا', 'حياك', 'حياك الله',
        'hello', 'hi', 'hey', 'howdy', 'greetings', 'good morning',
        'good afternoon', 'good evening', 'good day', "what's up", 'sup',
        'how are you', 'how r u', 'how are u',
    ]

    PRODUCT_KEYWORDS = [
        'monitor', 'thermometer', 'oximeter', 'nebulizer', 'glucose',
        'pulse', 'blood pressure', 'heart rate', 'heating pad', 'mask',
        'جهاز', 'ترمومتر', 'كمامة', 'بخاخ', 'سكر', 'ضغط', 'قياس',
    ]

    def __init__(self, model_name: str = "UBC-NLP/MARBERTv2"):
        self.model_name = model_name
        self.tokenizer = None
        self.model = None
        self.device = torch.device("cpu") 
        self._load_model()

    def _load_model(self):
        try:
            logger.info(f"Loading Intent Classification model: {self.model_name}")
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            self.model = AutoModelForSequenceClassification.from_pretrained(
                self.model_name, 
                num_labels=17,
                low_cpu_mem_usage=True,
                device_map=None,
                torch_dtype=torch.float32,
                ignore_mismatched_sizes=True 
            )
            self.model.to(self.device)
            self.model.eval()
        except Exception as e:
            logger.error(f"Error loading Intent model: {e}")
            self.model = None

    def predict(self, text: str, last_intent: str = None) -> Dict[str, Any]:
        text_lower = text.lower().strip()


        AFFIRMATIVES = {'yes', 'yeah', 'yep', 'sure', 'ok', 'okay', 'اه', 'أيوه', 'ايوه', 'تمام', 'اكيد', 'أكيد', 'طيب', 'يلا'}
        if text_lower in AFFIRMATIVES:
            if last_intent in ('recommendation_request', 'product_search', 'inquiry'):
                return {'intent': 'product_details', 'confidence': 1.0, 'label_idx': 15}
            if last_intent == 'product_details':
                return {'intent': 'purchase', 'confidence': 1.0, 'label_idx': 7}
            return {'intent': 'product_details', 'confidence': 0.9, 'label_idx': 15}

        PLACE_ORDER_PHRASES = [
            'place order', 'place an order', 'order it', 'order now', 'buy it', 'buy now',
            'i want to order', 'i want to buy', 'proceed', 'checkout',
            'اطلبه', 'اشتريه', 'اشتري', 'عايز اشتري', 'عايزة اشتري',
            'هشتريه', 'هطلبه', 'كمّل', 'كمل',
        ]
        if any(p in text_lower for p in PLACE_ORDER_PHRASES):
            return {'intent': 'purchase', 'confidence': 1.0, 'label_idx': 7}

        is_greeting = any(word in text_lower for word in self.GREETING_WORDS)
        has_product = any(kw in text_lower for kw in self.PRODUCT_KEYWORDS)

        if is_greeting and not has_product:
            return {'intent': 'greeting', 'confidence': 1.0, 'label_idx': 1}

        order_pattern = r'ord-\d{4}-\d{1,5}'
        if re.search(order_pattern, text_lower) or any(w in text_lower for w in [
            'تتبع', 'فين طلبي', 'حالة الطلب', 'track my order', 'order status', 'where is my order'
        ]):
            return {'intent': 'order_tracking', 'confidence': 1.0, 'label_idx': 3}

        if any(w in text_lower for w in ['ليه', 'اشمعنى', 'بناء على ايه', 'سبب', 'why', 'reason', 'why this', 'why recommended']):
            return {'intent': 'recommendation_reasoning', 'confidence': 1.0, 'label_idx': 16}

        if any(w in text_lower for w in ['اسمي إيه', 'اسمي ايه', 'مين أنا', 'مين انا', 'تعرفني', 'who am i', 'my name', 'what is my name']):
            return {'intent': 'memory_check', 'confidence': 1.0, 'label_idx': 14}

        if any(w in text_lower for w in [
            'هشتري', 'هطلبه', 'اشتري', 'اطلبه',
            'عايز اشتري', 'عايزة اشتري', 'عاوز اشتري', 'عاوزة اشتري',
            'buy', 'i want to buy', 'i want to order', 'purchase', 'want to buy'
        ]):
            return {'intent': 'purchase', 'confidence': 1.0, 'label_idx': 7}

        name_pattern_ar = r'(?:اسمي|أنا|انا|اسمي هو|معاك)\s+([آ-ي]{2,})'
        name_pattern_en = r"(?:my name is|i'm|i am|this is)\s+([a-zA-Z]{2,})"
        match_ar = re.search(name_pattern_ar, text_lower)
        match_en = re.search(name_pattern_en, text_lower)
        if match_ar or match_en:
            extracted = match_ar.group(1) if match_ar else match_en.group(1)
            blacklist = ['اسمي', 'ايه', 'إيه', 'أنا', 'انا', 'مين', 'هو', 'هي', 'ده', 'دي',
                         'بكام', 'سعره', 'معلومات', 'تفاصيل', 'عاوزة', 'عايزة', 'عايز', 'فين',
                         'مواصفات', 'what', 'who', 'is', 'am', 'the', 'want', 'need', 'name', 'this']
            if extracted.lower() not in blacklist and '؟' not in text_lower and '?' not in text_lower:
                return {'intent': 'introduce_name', 'confidence': 0.98, 'label_idx': 13}

        if any(w in text_lower for w in [
            'تفاصيل', 'معلومات', 'عنه', 'سعره', 'كام ده', 'مواصفات',
            'details', 'more info', 'about it', 'price', 'specs', 'tell me more'
        ]):
            return {'intent': 'product_details', 'confidence': 0.95, 'label_idx': 15}

        if has_product and len(text_lower.split()) <= 5:
            return {'intent': 'product_search', 'confidence': 0.9, 'label_idx': 6}

        if not self.model or not self.tokenizer:
            return self._keyword_only_predict(text_lower)

        try:
            inputs = self.tokenizer(text, return_tensors="pt", truncation=True, padding=True, max_length=128).to(self.device)
            with torch.no_grad():
                outputs = self.model(**inputs)
                logits = outputs.logits.detach().cpu()
                probs = torch.nn.functional.softmax(logits, dim=-1).numpy()[0]

            boosted_probs = probs.copy()

            keywords = {
                'greeting': self.GREETING_WORDS,
                'recommendation_request': [
                    'recommend', 'suggest', 'best', 'better', 'أرشح', 'توصية',
                    'ترشيح', 'أفضل', 'احسن', 'تنصحني', 'عايز جهاز', 'عايزة جهاز',
                    'رشحلي', 'اقترح'
                ],
                'product_search': [
                    'find', 'search', 'look', 'device', 'monitor', 'oximeter',
                    'thermometer', 'mask', 'glucose', 'pulse', 'nebulizer',
                    'بحث', 'جهاز', 'عندكم', 'عايز', 'heating pad'
                ],
                'goodbye': ['bye', 'thanks', 'thank', 'شكرا', 'مع السلامة', 'سلام', 'تسلم'],
                'order_tracking': ['track', 'order', 'status', 'تتبع', 'طلبي', 'فين']
            }

            inv_map = {v: k for k, v in self.INTENT_MAP.items()}
            for intent_name, words in keywords.items():
                if any(word in text_lower for word in words):
                    idx = inv_map.get(intent_name)
                    if idx is not None:
                        boosted_probs[idx] += 0.7

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
            return self._keyword_only_predict(text_lower)

    def _keyword_only_predict(self, text: str) -> Dict[str, Any]:
        text_lower = text.lower()

        if any(word in text_lower for word in self.GREETING_WORDS):
            has_product = any(kw in text_lower for kw in self.PRODUCT_KEYWORDS)
            if not has_product:
                return {'intent': 'greeting', 'confidence': 0.95, 'label_idx': 1}

        mapping = {
            'order_tracking':          ['track', 'order', 'status', 'تتبع', 'طلبي', 'فين'],
            'recommendation_reasoning':['ليه', 'اشمعنى', 'why', 'reason'],
            'memory_check':            ['اسمي إيه', 'اسمي ايه', 'مين أنا', 'who am i', 'my name'],
            'introduce_name':          ['اسمي', 'أنا', 'انا', 'i am', "i'm", 'my name'],
            'product_details':         ['تفاصيل', 'معلومات', 'عنه', 'سعره', 'مواصفات', 'details', 'about it'],
            'purchase':                ['buy', 'purchase', 'شراء', 'اشتري', 'هشتري', 'عايز اشتري', 'عايزة اشتري'],
            'product_search':          ['find', 'search', 'جهاز', 'عندكم', 'عايز', 'nebulizer', 'monitor', 'thermometer'],
            'recommendation_request':  ['recommend', 'suggest', 'أرشح', 'توصية', 'ترشيح', 'رشحلي', 'اقترح'],
            'goodbye':                 ['bye', 'thanks', 'شكرا', 'سلام'],
        }
        for intent, words in mapping.items():
            if any(w in text_lower for w in words):
                return {'intent': intent, 'confidence': 0.9, 'label_idx': None}
        return {'intent': 'inquiry', 'confidence': 0.1, 'label_idx': None}

    def __del__(self):
        if hasattr(self, 'model'): del self.model
        if hasattr(self, 'tokenizer'): del self.tokenizer
        gc.collect()