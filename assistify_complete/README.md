# Assistify - Multi-Channel AI Chatbot Platform

Complete implementation of Assistify with 4 ML models, Django backend, React frontend, and multi-channel integration.

## Project Structure

```
assistify_complete/
├── backend/                 # Django backend
│   ├── assistify/          # Main Django project
│   ├── chatbot/            # Chatbot app
│   ├── channels/           # Channel integrations
│   ├── models/             # ML models integration
│   ├── requirements.txt    # Python dependencies
│   └── manage.py          # Django management
├── frontend/              # React frontend
│   ├── src/              # React source code
│   ├── public/           # Static assets
│   ├── package.json      # Node dependencies
│   └── README.md         # Frontend documentation
├── ml_models/            # Machine learning models
│   ├── intent_classification/    # Model 1
│   ├── sentiment_analysis/       # Model 2
│   ├── response_generation/      # Model 3
│   ├── product_recommendation/   # Model 4
│   └── training/                 # Training scripts
├── config/               # Configuration files
│   ├── settings.py      # Django settings
│   ├── database.sql     # Database schema
│   └── .env.example     # Environment variables
├── scripts/             # Utility scripts
│   ├── setup.sh         # Setup script
│   ├── train_models.py  # Training runner
│   └── deploy.sh        # Deployment script
└── docs/               # Documentation
    ├── ARCHITECTURE.md
    ├── API.md
    ├── MODELS.md
    ├── SETUP.md
    └── DEPLOYMENT.md
```

## Features

- **4 ML Models:**
  - Intent Classification (DistilBERT)
  - Sentiment Analysis (RoBERTa)
  - Response Generation (T5-Base)
  - Product Recommendation (LightFM)

- **Multi-Channel Integration:**
  - WhatsApp (Twilio)
  - Instagram (Meta Graph API)
  - Facebook Messenger (Meta Graph API)
  - Shopify Chat

- **Backend:**
  - Django REST Framework
  - PostgreSQL Database
  - Celery for async tasks
  - Redis for caching

- **Frontend:**
  - React 19
  - Real-time chat interface
  - Admin dashboard
  - Analytics

## Quick Start

### Prerequisites
- Python 3.9+
- Node.js 18+
- PostgreSQL 12+
- Redis 6+

### Installation

1. **Clone and setup:**
```bash
cd assistify_complete
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r backend/requirements.txt
```

2. **Setup database:**
```bash
cd backend
python manage.py migrate
```

3. **Setup frontend:**
```bash
cd frontend
npm install
npm run dev
```

4. **Train models (optional):**
```bash
cd ml_models/training
python train_all_models.py
```

## Configuration

Copy `.env.example` to `.env` and update:
```
DATABASE_URL=postgresql://user:password@localhost/assistify
REDIS_URL=redis://localhost:6379
TWILIO_ACCOUNT_SID=your_sid
TWILIO_AUTH_TOKEN=your_token
META_ACCESS_TOKEN=your_token
SHOPIFY_API_KEY=your_key
```

## API Documentation

See `docs/API.md` for complete API documentation.

## Model Training

See `docs/MODELS.md` for training instructions.

## Deployment

See `docs/DEPLOYMENT.md` for production deployment.

## Support

For issues and questions, refer to the documentation in the `docs/` folder.
