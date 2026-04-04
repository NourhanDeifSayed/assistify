import logging
import torch
import gc
from typing import Dict, Any, Optional
from transformers import T5Tokenizer, T5ForConditionalGeneration

logger = logging.getLogger(__name__)

class ResponseGenerationModel:
    
    def __init__(self, model_name: str = "t5-small"):
        self.model_name = model_name
        self.tokenizer = None
        self.model = None
        self.device = torch.device("cpu") # Force CPU for stability on Windows
        self._load_model()

    def _load_model(self):
        try:
            logger.info(f"Loading Response Generation model: {self.model_name}")
            self.tokenizer = T5Tokenizer.from_pretrained(self.model_name)
            
            # Use aggressive memory saving for loading
            self.model = T5ForConditionalGeneration.from_pretrained(
                self.model_name,
                low_cpu_mem_usage=True,
                device_map=None,
                torch_dtype=torch.float32 # Ensure standard float32 for CPU
            )
            self.model.to(self.device)
            self.model.eval()
        except Exception as e:
            logger.error(f"Error loading Response model: {e}")
            self.model = None

    def generate(self, query: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        if not self.model or not self.tokenizer:
            return {'response': self._generate_fallback_response(context), 'confidence': 0.0}

        if context is None:
            context = {}
        
        intent = context.get('intent', 'inquiry')
        sentiment = context.get('sentiment', 'neutral')
        recommendations = context.get('recommendations', [])
        
        # Guide T5 with a prompt
        prompt = f"Refine this response for a {sentiment} customer who said '{query}': {self._generate_fallback_response(context)}"
        
        try:
            input_ids = self.tokenizer(prompt, return_tensors="pt", truncation=True, padding=True, max_length=256).input_ids.to(self.device)
            
            with torch.no_grad():
                outputs = self.model.generate(
                    input_ids, 
                    max_length=150, 
                    num_beams=2, # Reduced beams for memory
                    no_repeat_ngram_size=2,
                    early_stopping=True
                )
                
                response_text = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
                
                # If T5 output is too short or weird, fallback
                if len(response_text) < 10:
                    response_text = self._generate_fallback_response(context)

            return {
                'response': response_text,
                'confidence': 0.9,
                'intent': intent,
                'sentiment': sentiment
            }
        except Exception as e:
            logger.error(f"Error in Response generation: {e}")
            return {'response': self._generate_fallback_response(context), 'confidence': 0.0}

    def _generate_fallback_response(self, context: Optional[Dict[str, Any]]) -> str:
        """Rule-based response generator for low-memory situations."""
        if context is None: context = {}
        intent = context.get('intent', 'inquiry')
        sentiment = context.get('sentiment', 'neutral')
        recommendations = context.get('recommendations', [])
        
        templates = {
            'greeting': "Hello! I'm your MediCare AI assistant. How can I help you today?",
            'purchase': "I see you're interested in making a purchase. I've found some great medical devices for you.",
            'inquiry': "I'd be happy to help with your inquiry about our medical products.",
            'product_search': "I'm searching our catalog for the best medical devices matching your request.",
            'complaint': "I'm sorry to hear you're having trouble. Let me help you resolve this issue.",
            'support': "Our support team is here to help. What seems to be the problem?",
            'fallback': "I understand. I've found some medical products that might be helpful for you."
        }
        
        base = templates.get(intent, templates['fallback'])
        if recommendations:
            base += f" I recommend checking out the {recommendations[0]['name']}."
            
        if sentiment == 'positive':
            base = "Great! " + base
        elif sentiment == 'negative':
            base = "I apologize for any inconvenience. " + base
            
        return base

    def __del__(self):
        """Ensure memory is cleared when object is deleted."""
        if hasattr(self, 'model'): del self.model
        if hasattr(self, 'tokenizer'): del self.tokenizer
        gc.collect()
