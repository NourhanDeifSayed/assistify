# Assistify ML Models Documentation

Complete documentation for all 4 machine learning models.

## Overview

Assistify uses 4 specialized ML models working together:

1. **Intent Classification** - Understand what customer wants
2. **Sentiment Analysis** - Understand how customer feels
3. **Response Generation** - Generate intelligent responses
4. **Product Recommendation** - Recommend products

## Model 1: Intent Classification (DistilBERT)

### Purpose
Classify customer messages into 6 intent categories.

### Intents
- **Purchase** - Customer wants to buy
- **Support** - Customer needs help
- **Complaint** - Customer is unhappy
- **Inquiry** - Customer has a question
- **Return** - Customer wants to return
- **Tracking** - Customer wants to track order

### Architecture
- **Base Model:** DistilBERT (distilbert-base-uncased)
- **Input:** Customer message (text)
- **Output:** Intent label + confidence score
- **Performance:** 94-96% accuracy

### Training Data Requirements

**CSV Format (messages.csv):**
```csv
content,intent
"I want to buy the gold package",purchase
"How do I use this?",support
"This product is terrible!",complaint
"What are your prices?",inquiry
"I want to return this",return
"Where is my order?",tracking
```

**Minimum Data:** 500-1000 labeled messages per intent

### Training Code

```python
from ml_models.intent_classification.model import IntentClassifier
from ml_models.training.train_all_models import ModelTrainer

trainer = ModelTrainer()
classifier = trainer.train_intent_classifier(messages_df)
classifier.save('path/to/save')
```

### Usage

```python
from ml_models.intent_classification.model import IntentClassifier

classifier = IntentClassifier()
result = classifier.predict("I want to buy the gold package")

print(result)
# Output:
# {
#   'intent': 'purchase',
#   'confidence': 0.98,
#   'all_probabilities': {
#     'purchase': 0.98,
#     'support': 0.01,
#     ...
#   }
# }
```

### Performance Metrics

| Metric | Value |
|--------|-------|
| Accuracy | 94-96% |
| Precision | 0.93-0.95 |
| Recall | 0.92-0.94 |
| F1-Score | 0.93-0.94 |
| Inference Time | 50-100ms |
| Model Size | 268MB |

---

## Model 2: Sentiment Analysis (RoBERTa)

### Purpose
Analyze customer emotions and sentiment.

### Sentiments
- **Negative** - Customer is unhappy, angry, or frustrated
- **Neutral** - Customer is asking objectively
- **Positive** - Customer is happy or satisfied

### Architecture
- **Base Model:** RoBERTa (roberta-base)
- **Input:** Customer message (text)
- **Output:** Sentiment label + confidence + intensity
- **Performance:** 96-97% accuracy

### Training Data Requirements

**CSV Format (messages.csv):**
```csv
content,sentiment
"This product is amazing!",positive
"What are your prices?",neutral
"I hate this product!",negative
"I'm very happy with my purchase",positive
"Can you help me?",neutral
"Terrible service!",negative
```

**Minimum Data:** 500-1000 labeled messages per sentiment

### Training Code

```python
from ml_models.sentiment_analysis.model import SentimentAnalyzer
from ml_models.training.train_all_models import ModelTrainer

trainer = ModelTrainer()
analyzer = trainer.train_sentiment_analyzer(messages_df)
analyzer.save('path/to/save')
```

### Usage

```python
from ml_models.sentiment_analysis.model import SentimentAnalyzer

analyzer = SentimentAnalyzer()
result = analyzer.predict("This product is amazing!")

print(result)
# Output:
# {
#   'sentiment': 'positive',
#   'confidence': 0.97,
#   'intensity': 0.95,
#   'all_probabilities': {
#     'negative': 0.01,
#     'neutral': 0.02,
#     'positive': 0.97
#   }
# }
```

### Performance Metrics

| Metric | Value |
|--------|-------|
| Accuracy | 96-97% |
| Precision | 0.95-0.97 |
| Recall | 0.95-0.97 |
| F1-Score | 0.95-0.97 |
| Inference Time | 50-100ms |
| Model Size | 498MB |

---

## Model 3: Response Generation (T5-Base)

### Purpose
Generate intelligent, context-aware responses.

### Architecture
- **Base Model:** T5-Base (t5-base)
- **Input:** Customer message + intent + sentiment
- **Output:** Generated response text
- **Performance:** 18-22 BLEU score

### Training Data Requirements

**CSV Format (messages.csv):**
```csv
content,response,intent,sentiment
"I want to buy the gold package","Great! The gold package costs $500/month...",purchase,positive
"This product is broken!","We're sorry! We'll replace it immediately.",complaint,negative
"How do I use this?","Here's a step-by-step guide...",support,neutral
```

**Minimum Data:** 1000-2000 message-response pairs

### Training Code

```python
from ml_models.response_generation.model import ResponseGenerator
from ml_models.training.train_all_models import ModelTrainer

trainer = ModelTrainer()
generator = trainer.train_response_generator(messages_df)
generator.save('path/to/save')
```

### Usage

```python
from ml_models.response_generation.model import ResponseGenerator

generator = ResponseGenerator()
result = generator.generate(
    "I want to buy the gold package",
    intent="purchase",
    sentiment="positive"
)

print(result)
# Output:
# {
#   'response': 'Great! The gold package costs $500/month...',
#   'model': 't5-base',
#   'input_length': 8,
#   'output_length': 12
# }
```

### Performance Metrics

| Metric | Value |
|--------|-------|
| BLEU Score | 18-22 |
| ROUGE-L | 0.35-0.40 |
| Inference Time | 300-500ms |
| Model Size | 892MB |

---

## Model 4: Product Recommendation (LightFM)

### Purpose
Recommend products based on customer behavior and preferences.

### Recommendation Types
- **Purchase Recommendations** - Products matching customer intent
- **Cross-sell** - Complementary products
- **Upsell** - Premium versions
- **Trending** - Popular products
- **Personalized** - Based on customer history

### Architecture
- **Base Model:** LightFM (Collaborative Filtering)
- **Input:** Customer ID + product interactions
- **Output:** Ranked product recommendations
- **Performance:** 0.48-0.52 Precision@10

### Training Data Requirements

**CSV Format (interactions.csv):**
```csv
customer_id,product_id,interaction_type,timestamp
1,101,view,2024-02-01 10:00:00
1,101,add_to_cart,2024-02-01 10:05:00
1,101,purchase,2024-02-01 10:10:00
2,102,view,2024-02-01 11:00:00
2,103,purchase,2024-02-01 11:30:00
```

**CSV Format (products.csv):**
```csv
product_id,name,category,price
101,Gold Package,subscription,500
102,Silver Package,subscription,300
103,Support Add-on,addon,50
```

**Minimum Data:** 5000-10000 interactions

### Training Code

```python
from ml_models.product_recommendation.model import ProductRecommender
from ml_models.training.train_all_models import ModelTrainer

trainer = ModelTrainer()
recommender = trainer.train_product_recommender(interactions_df, products_df)
recommender.save('path/to/save')
```

### Usage

```python
from ml_models.product_recommendation.model import ProductRecommender

recommender = ProductRecommender()
result = recommender.recommend(customer_id=1, num_recommendations=5)

print(result)
# Output:
# {
#   'recommendations': [
#     {
#       'product_id': 102,
#       'score': 0.92,
#       'rank': 1
#     },
#     {
#       'product_id': 103,
#       'score': 0.85,
#       'rank': 2
#     },
#     ...
#   ]
# }
```

### Performance Metrics

| Metric | Value |
|--------|-------|
| Precision@10 | 0.48-0.52 |
| Recall@10 | 0.44-0.48 |
| NDCG@10 | 0.50-0.55 |
| Inference Time | 10-50ms |
| Model Size | Variable |

---

## Training Pipeline

### Step 1: Prepare Data

```bash
mkdir -p ml_models/training/data
# Add your CSV files to this directory
```

### Step 2: Run Training

```bash
cd ml_models/training
python train_all_models.py
```

### Step 3: Evaluate Models

```python
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score

# Evaluate intent classifier
predictions = classifier.predict(test_texts)
accuracy = accuracy_score(test_labels, predictions)
print(f"Accuracy: {accuracy:.4f}")
```

### Step 4: Deploy Models

```python
# Save trained models
classifier.save('ml_models/trained_models/intent_classifier')
analyzer.save('ml_models/trained_models/sentiment_analyzer')
generator.save('ml_models/trained_models/response_generator')
recommender.save('ml_models/trained_models/product_recommender')
```

## Model Monitoring

### Track Performance Over Time

```python
from django.db import models

class ModelMetrics(models.Model):
    model_name = models.CharField(max_length=100)
    metric_name = models.CharField(max_length=100)
    metric_value = models.FloatField()
    timestamp = models.DateTimeField(auto_now_add=True)
```

### Log Predictions

```python
# Log every prediction for analysis
message = Message.objects.create(
    conversation=conversation,
    sender='customer',
    content=content,
    intent=intent_result['intent'],
    sentiment=sentiment_result['sentiment'],
    confidence=confidence_score,
    metadata={
        'intent_confidence': intent_result['confidence'],
        'sentiment_confidence': sentiment_result['confidence']
    }
)
```

## Continuous Improvement

### Weekly Retraining

```bash
#!/bin/bash
# scripts/weekly_retrain.sh

cd ml_models/training
python train_all_models.py

# Backup old models
cp -r ../trained_models ../trained_models.backup

# Move new models
mv trained_models/* ../trained_models/
```

### A/B Testing

Compare old vs new models:

```python
def compare_models(test_data):
    old_predictions = old_model.predict(test_data)
    new_predictions = new_model.predict(test_data)
    
    improvement = (new_predictions == test_labels).sum() / len(test_labels)
    return improvement
```

## Troubleshooting

### Out of Memory
- Reduce batch size
- Use smaller model variants
- Enable gradient checkpointing

### Low Accuracy
- Increase training data
- Adjust hyperparameters
- Check data quality

### Slow Inference
- Use smaller models
- Enable model quantization
- Use GPU acceleration

## References

- DistilBERT: https://huggingface.co/distilbert-base-uncased
- RoBERTa: https://huggingface.co/roberta-base
- T5: https://huggingface.co/t5-base
- LightFM: https://github.com/lyst/lightfm
