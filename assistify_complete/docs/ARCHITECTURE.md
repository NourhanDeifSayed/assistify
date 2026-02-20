# Assistify Architecture Documentation

Complete technical architecture overview.

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     CLIENT LAYER                             │
├─────────────────────────────────────────────────────────────┤
│  React Frontend │ Web Chat │ Admin Dashboard │ Analytics     │
└────────────────────────┬────────────────────────────────────┘
                         │ HTTP/REST
┌────────────────────────▼────────────────────────────────────┐
│                   API GATEWAY LAYER                          │
├─────────────────────────────────────────────────────────────┤
│  Django REST Framework │ Authentication │ Rate Limiting     │
└────────────────────────┬────────────────────────────────────┘
                         │
        ┌────────────────┼────────────────┐
        │                │                │
        ▼                ▼                ▼
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│  Chatbot     │  │  Channels    │  │  Analytics   │
│  Service     │  │  Service     │  │  Service     │
└──────────────┘  └──────────────┘  └──────────────┘
        │                │                │
        └────────────────┼────────────────┘
                         │
        ┌────────────────┼────────────────┐
        │                │                │
        ▼                ▼                ▼
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│  ML Models   │  │  Task Queue  │  │  Cache       │
│  (4 Models)  │  │  (Celery)    │  │  (Redis)     │
└──────────────┘  └──────────────┘  └──────────────┘
        │                │                │
        └────────────────┼────────────────┘
                         │
        ┌────────────────┼────────────────┐
        │                │                │
        ▼                ▼                ▼
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│  PostgreSQL  │  │  Redis       │  │  File        │
│  Database    │  │  Cache       │  │  Storage     │
└──────────────┘  └──────────────┘  └──────────────┘
```

## Component Details

### Frontend (React)

**Location:** `frontend/`

**Components:**
- Chat Interface
- Admin Dashboard
- Analytics Dashboard
- Settings Panel
- Real-time Notifications

**Technologies:**
- React 19
- Tailwind CSS
- Axios (HTTP client)
- Zustand (State management)
- React Router (Navigation)

### Backend (Django)

**Location:** `backend/`

**Apps:**
- `chatbot` - Core chatbot functionality
- `channels` - Multi-channel integration
- `models` - ML model integration
- `analytics` - Analytics and reporting

**Technologies:**
- Django 4.2
- Django REST Framework
- PostgreSQL
- Redis
- Celery

### ML Models

**Location:** `ml_models/`

**Models:**
1. Intent Classification (DistilBERT)
2. Sentiment Analysis (RoBERTa)
3. Response Generation (T5-Base)
4. Product Recommendation (LightFM)

**Technologies:**
- Transformers (Hugging Face)
- PyTorch
- Scikit-learn
- LightFM

### Channel Integrations

**Supported Channels:**
- WhatsApp (Twilio)
- Instagram (Meta Graph API)
- Facebook Messenger (Meta Graph API)
- Shopify Chat

**Architecture:**
```
Incoming Message
      │
      ▼
Channel Webhook Handler
      │
      ├─ Validate signature
      ├─ Extract message
      ├─ Create/Update customer
      └─ Create conversation
      │
      ▼
Message Processing Pipeline
      │
      ├─ Intent Classification
      ├─ Sentiment Analysis
      ├─ Response Generation
      └─ Product Recommendation
      │
      ▼
Response Delivery
      │
      ├─ Format response
      ├─ Add recommendations
      └─ Send via channel
```

## Data Flow

### Message Processing Flow

```
1. Customer sends message via channel
   ↓
2. Webhook handler receives and validates
   ↓
3. Extract message content and customer info
   ↓
4. Create/Update customer record
   ↓
5. Create conversation (if new)
   ↓
6. Create message record
   ↓
7. Queue async processing task (Celery)
   ↓
8. Process through ML pipeline:
   - Intent Classification
   - Sentiment Analysis
   - Response Generation
   - Product Recommendation
   ↓
9. Store results in database
   ↓
10. Format response with recommendations
    ↓
11. Send response via channel
    ↓
12. Log interaction for analytics
```

### Database Schema

**Core Tables:**
- `users` - System users
- `customers` - Customer profiles
- `conversations` - Chat conversations
- `messages` - Individual messages
- `responses` - Generated responses
- `products` - Product catalog
- `interactions` - Customer-product interactions
- `recommendations` - Product recommendations
- `model_metrics` - Model performance metrics
- `webhook_logs` - Webhook event logs

**Relationships:**
```
users (1) ──── (N) customers
customers (1) ──── (N) conversations
conversations (1) ──── (N) messages
messages (1) ──── (1) responses
customers (N) ──── (N) products (through interactions)
messages (1) ──── (N) recommendations
```

## API Flow

### REST API Structure

```
/api/
├── messages/
│   ├── process_message/ (POST)
│   └── get_conversation_messages/ (GET)
├── conversations/
│   ├── create_conversation/ (POST)
│   ├── list/ (GET)
│   └── {id}/close_conversation/ (POST)
├── webhooks/
│   ├── whatsapp/ (POST)
│   ├── instagram/ (POST)
│   ├── facebook/ (POST)
│   └── shopify/ (POST)
└── analytics/
    ├── intent_stats/ (GET)
    ├── sentiment_stats/ (GET)
    └── channel_stats/ (GET)
```

## Deployment Architecture

### Development Environment
```
Local Machine
├── Django Dev Server (8000)
├── React Dev Server (3000)
├── PostgreSQL (5432)
├── Redis (6379)
└── Celery Worker
```

### Production Environment
```
Cloud Server (AWS/GCP/Azure)
├── Load Balancer
├── Django App Servers (Gunicorn)
├── React Static Files (CDN)
├── PostgreSQL (Managed)
├── Redis (Managed)
├── Celery Workers
└── Monitoring (Prometheus/Grafana)
```

## Security Architecture

### Authentication
- JWT tokens for API
- Session-based for web
- OAuth 2.0 for third-party

### Authorization
- Role-based access control (RBAC)
- Permission-based endpoints
- Customer data isolation

### Data Protection
- HTTPS/TLS encryption
- Database encryption at rest
- API rate limiting
- CORS policy enforcement
- CSRF protection

### Secrets Management
- Environment variables
- Secure credential storage
- API key rotation
- Webhook signature validation

## Scalability Considerations

### Horizontal Scaling
- Stateless Django servers
- Load balancer for distribution
- Database replication
- Redis cluster for caching

### Vertical Scaling
- Increase server resources
- Optimize database queries
- Model quantization for inference
- Batch processing for heavy tasks

### Async Processing
- Celery for long-running tasks
- Redis as message broker
- Task queuing and retry logic
- Worker pool management

## Performance Optimization

### Caching Strategy
- Redis for frequent queries
- Model output caching
- API response caching
- Database query optimization

### Database Optimization
- Proper indexing
- Connection pooling
- Query optimization
- Regular maintenance

### ML Model Optimization
- Model quantization
- Batch inference
- GPU acceleration
- Model caching

## Monitoring and Logging

### Metrics to Track
- API response times
- Model inference latency
- Database query performance
- Cache hit rates
- Error rates

### Logging Strategy
- Application logs
- API request/response logs
- ML model predictions
- Webhook events
- User actions

### Alerting
- High error rates
- Slow response times
- Model accuracy degradation
- Database issues
- Service downtime

## Disaster Recovery

### Backup Strategy
- Daily database backups
- Model checkpoints
- Configuration backups
- Code repository backups

### Recovery Procedures
- Database restore process
- Model rollback procedure
- Configuration recovery
- Service restart procedure

## Future Enhancements

1. **Multi-language Support**
   - Translate messages
   - Multilingual models

2. **Advanced Analytics**
   - Customer lifetime value
   - Churn prediction
   - Sentiment trends

3. **Integration Expansion**
   - Telegram
   - WeChat
   - Slack
   - Custom webhooks

4. **AI Improvements**
   - Fine-tuned models
   - Custom training
   - Ensemble methods
   - Reinforcement learning

5. **Infrastructure**
   - Kubernetes deployment
   - Microservices architecture
   - GraphQL API
   - Real-time streaming
