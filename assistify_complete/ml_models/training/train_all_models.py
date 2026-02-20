import os
import sys
import torch
import pandas as pd
from pathlib import Path
from sklearn.model_selection import train_test_split
from datasets import Dataset
from transformers import Trainer, TrainingArguments

sys.path.insert(0, str(Path(__file__).parent.parent))

from intent_classification.model import IntentClassifier
from sentiment_analysis.model import SentimentAnalyzer
from response_generation.model import ResponseGenerator
from product_recommendation.model import ProductRecommender

class ModelTrainer:
    def __init__(self, data_path='data/'):
        self.data_path = Path(data_path)
        self.models_path = Path(__file__).parent.parent / 'trained_models'
        self.models_path.mkdir(exist_ok=True)
    
    def load_training_data(self):
        messages_df = pd.read_csv(self.data_path / 'messages.csv')
        interactions_df = pd.read_csv(self.data_path / 'interactions.csv')
        products_df = pd.read_csv(self.data_path / 'products.csv')
        
        return messages_df, interactions_df, products_df
    
    def train_intent_classifier(self, messages_df):
        print("Training Intent Classifier...")
        
        classifier = IntentClassifier()
        
        if 'intent' not in messages_df.columns:
            print("Warning: No intent labels found. Using pre-trained model.")
            classifier.save(self.models_path / 'intent_classifier')
            return classifier
        
        train_df, eval_df = train_test_split(messages_df, test_size=0.2, random_state=42)
        
        train_dataset = Dataset.from_pandas(train_df[['content', 'intent']])
        eval_dataset = Dataset.from_pandas(eval_df[['content', 'intent']])
        
        training_args = TrainingArguments(
            output_dir=str(self.models_path / 'intent_classifier'),
            num_train_epochs=3,
            per_device_train_batch_size=32,
            per_device_eval_batch_size=32,
            warmup_steps=100,
            weight_decay=0.01,
            logging_dir='./logs',
            logging_steps=100,
        )
        
        trainer = Trainer(
            model=classifier.model,
            args=training_args,
            train_dataset=train_dataset,
            eval_dataset=eval_dataset,
        )
        
        trainer.train()
        classifier.save(self.models_path / 'intent_classifier')
        
        print("Intent Classifier trained successfully!")
        return classifier
    
    def train_sentiment_analyzer(self, messages_df):
        print("Training Sentiment Analyzer...")
        
        analyzer = SentimentAnalyzer()
        
        if 'sentiment' not in messages_df.columns:
            print("Warning: No sentiment labels found. Using pre-trained model.")
            analyzer.save(self.models_path / 'sentiment_analyzer')
            return analyzer
        
        train_df, eval_df = train_test_split(messages_df, test_size=0.2, random_state=42)
        
        train_dataset = Dataset.from_pandas(train_df[['content', 'sentiment']])
        eval_dataset = Dataset.from_pandas(eval_df[['content', 'sentiment']])
        
        training_args = TrainingArguments(
            output_dir=str(self.models_path / 'sentiment_analyzer'),
            num_train_epochs=3,
            per_device_train_batch_size=32,
            per_device_eval_batch_size=32,
            warmup_steps=100,
            weight_decay=0.01,
            logging_dir='./logs',
            logging_steps=100,
        )
        
        trainer = Trainer(
            model=analyzer.model,
            args=training_args,
            train_dataset=train_dataset,
            eval_dataset=eval_dataset,
        )
        
        trainer.train()
        analyzer.save(self.models_path / 'sentiment_analyzer')
        
        print("Sentiment Analyzer trained successfully!")
        return analyzer
    
    def train_response_generator(self, messages_df):
        print("Training Response Generator...")
        
        generator = ResponseGenerator()
        
        if 'response' not in messages_df.columns:
            print("Warning: No response data found. Using pre-trained model.")
            generator.save(self.models_path / 'response_generator')
            return generator
        
        train_df, eval_df = train_test_split(messages_df, test_size=0.2, random_state=42)
        
        train_dataset = Dataset.from_pandas(train_df[['content', 'response']])
        eval_dataset = Dataset.from_pandas(eval_df[['content', 'response']])
        
        training_args = TrainingArguments(
            output_dir=str(self.models_path / 'response_generator'),
            num_train_epochs=3,
            per_device_train_batch_size=16,
            per_device_eval_batch_size=16,
            warmup_steps=100,
            weight_decay=0.01,
            logging_dir='./logs',
            logging_steps=100,
        )
        
        trainer = Trainer(
            model=generator.model,
            args=training_args,
            train_dataset=train_dataset,
            eval_dataset=eval_dataset,
        )
        
        trainer.train()
        generator.save(self.models_path / 'response_generator')
        
        print("Response Generator trained successfully!")
        return generator
    
    def train_product_recommender(self, interactions_df, products_df):
        print("Training Product Recommender...")
        
        recommender = ProductRecommender()
        recommender.prepare_data(interactions_df, products_df)
        recommender.train(epochs=30)
        recommender.save(str(self.models_path / 'product_recommender'))
        
        print("Product Recommender trained successfully!")
        return recommender
    
    def train_all(self):
        try:
            messages_df, interactions_df, products_df = self.load_training_data()
        except FileNotFoundError:
            print("Training data not found. Using pre-trained models.")
            print("To train custom models, provide data in:")
            print(f"  - {self.data_path / 'messages.csv'}")
            print(f"  - {self.data_path / 'interactions.csv'}")
            print(f"  - {self.data_path / 'products.csv'}")
            return
        
        self.train_intent_classifier(messages_df)
        self.train_sentiment_analyzer(messages_df)
        self.train_response_generator(messages_df)
        self.train_product_recommender(interactions_df, products_df)
        
        print("\nAll models trained successfully!")
        print(f"Models saved to: {self.models_path}")

if __name__ == '__main__':
    trainer = ModelTrainer()
    trainer.train_all()
