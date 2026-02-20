import torch
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

class ResponseGenerator:
    def __init__(self, model_name='t5-base'):
        self.model_name = model_name
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForSeq2SeqLM.from_pretrained(model_name)
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.model.to(self.device)
    
    def generate(self, text, intent=None, sentiment=None, max_length=100):
        prefix = f"intent: {intent} sentiment: {sentiment} " if intent and sentiment else ""
        input_text = prefix + text
        
        inputs = self.tokenizer(input_text, return_tensors='pt', truncation=True, max_length=512)
        inputs = {k: v.to(self.device) for k, v in inputs.items()}
        
        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                max_length=max_length,
                num_beams=4,
                early_stopping=True,
                temperature=0.7,
                top_p=0.9
            )
        
        response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        
        return {
            'response': response,
            'model': self.model_name,
            'input_length': len(input_text.split()),
            'output_length': len(response.split())
        }
    
    def save(self, path):
        self.model.save_pretrained(path)
        self.tokenizer.save_pretrained(path)
    
    def load(self, path):
        self.model = AutoModelForSeq2SeqLM.from_pretrained(path)
        self.tokenizer = AutoTokenizer.from_pretrained(path)
        self.model.to(self.device)
