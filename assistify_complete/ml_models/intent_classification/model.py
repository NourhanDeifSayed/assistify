import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import numpy as np

class IntentClassifier:
    def __init__(self, model_name='distilbert-base-uncased', num_labels=6):
        self.model_name = model_name
        self.num_labels = num_labels
        self.intents = ['purchase', 'support', 'complaint', 'inquiry', 'return', 'tracking']
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForSequenceClassification.from_pretrained(model_name, num_labels=num_labels)
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.model.to(self.device)
    
    def predict(self, text):
        inputs = self.tokenizer(text, return_tensors='pt', truncation=True, max_length=512)
        inputs = {k: v.to(self.device) for k, v in inputs.items()}
        
        with torch.no_grad():
            outputs = self.model(**inputs)
        
        logits = outputs.logits
        probabilities = torch.softmax(logits, dim=1)
        predicted_class = torch.argmax(logits, dim=1).item()
        confidence = probabilities[0][predicted_class].item()
        
        return {
            'intent': self.intents[predicted_class],
            'confidence': float(confidence),
            'all_probabilities': {intent: float(prob) for intent, prob in zip(self.intents, probabilities[0].cpu().numpy())}
        }
    
    def save(self, path):
        self.model.save_pretrained(path)
        self.tokenizer.save_pretrained(path)
    
    def load(self, path):
        self.model = AutoModelForSequenceClassification.from_pretrained(path)
        self.tokenizer = AutoTokenizer.from_pretrained(path)
        self.model.to(self.device)
