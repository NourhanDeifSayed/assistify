import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import numpy as np

class SentimentAnalyzer:
    def __init__(self, model_name='roberta-base', num_labels=3):
        self.model_name = model_name
        self.num_labels = num_labels
        self.sentiments = ['negative', 'neutral', 'positive']
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
        
        intensity = self._calculate_intensity(probabilities[0].cpu().numpy())
        
        return {
            'sentiment': self.sentiments[predicted_class],
            'confidence': float(confidence),
            'intensity': float(intensity),
            'all_probabilities': {sent: float(prob) for sent, prob in zip(self.sentiments, probabilities[0].cpu().numpy())}
        }
    
    def _calculate_intensity(self, probabilities):
        if probabilities[0] > 0.7:
            return probabilities[0]
        elif probabilities[2] > 0.7:
            return probabilities[2]
        else:
            return 0.5
    
    def save(self, path):
        self.model.save_pretrained(path)
        self.tokenizer.save_pretrained(path)
    
    def load(self, path):
        self.model = AutoModelForSequenceClassification.from_pretrained(path)
        self.tokenizer = AutoTokenizer.from_pretrained(path)
        self.model.to(self.device)
