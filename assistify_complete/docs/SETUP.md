# Assistify Setup Guide

Complete setup instructions for Windows, Linux, and macOS.

## Prerequisites

### Windows
- Python 3.9+ (https://www.python.org/downloads/)
- Node.js 18+ (https://nodejs.org/)
- PostgreSQL 12+ (https://www.postgresql.org/download/windows/)
- Redis 6+ (https://github.com/microsoftarchive/redis/releases)
- Git (https://git-scm.com/download/win)

### Linux
```bash
sudo apt-get update
sudo apt-get install python3.9 python3-pip nodejs postgresql postgresql-contrib redis-server
```

### macOS
```bash
brew install python@3.9 node postgresql redis
```

## Installation Steps

### 1. Clone Repository
```bash
git clone https://github.com/yourusername/assistify.git
cd assistify_complete
```

### 2. Setup Python Environment

#### Windows
```powershell
python -m venv venv
.\venv\Scripts\activate
pip install -r backend/requirements.txt
```

#### Linux/macOS
```bash
python3.9 -m venv venv
source venv/bin/activate
pip install -r backend/requirements.txt
```

### 3. Setup PostgreSQL Database

#### Windows
```bash
psql -U postgres
```

Then run:
```sql
\i config/database.sql
```

#### Linux/macOS
```bash
sudo -u postgres psql
```

Then run:
```sql
\i config/database.sql
```

### 4. Setup Django Backend

```bash
cd backend
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

### 5. Setup React Frontend

```bash
cd frontend
npm install
npm run dev
```

### 6. Setup Redis (for Celery)

#### Windows
```bash
redis-server
```

#### Linux/macOS
```bash
redis-server
```

### 7. Setup Celery Worker (optional)

```bash
cd backend
celery -A assistify worker -l info
```

## Environment Variables

Create `.env` file in the root directory:

```
# Database
DATABASE_URL=postgresql://postgres:password@localhost:5432/assistify
REDIS_URL=redis://localhost:6379

# Django
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# WhatsApp (Twilio)
TWILIO_ACCOUNT_SID=your_account_sid
TWILIO_AUTH_TOKEN=your_auth_token
TWILIO_PHONE_NUMBER=+1234567890

# Instagram/Facebook (Meta)
META_ACCESS_TOKEN=your_access_token
META_BUSINESS_ACCOUNT_ID=your_business_account_id
META_VERIFY_TOKEN=your_verify_token

# Shopify
SHOPIFY_API_KEY=your_api_key
SHOPIFY_API_PASSWORD=your_api_password
SHOPIFY_SHOP_NAME=your_shop_name

# CORS
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8000
```

## Training ML Models

### Download Training Data

Create `ml_models/training/data/` directory with:
- `messages.csv` - Customer messages with intent and sentiment labels
- `interactions.csv` - Customer-product interactions
- `products.csv` - Product catalog

### Train Models

```bash
cd ml_models/training
python train_all_models.py
```

Models will be saved to `ml_models/trained_models/`

## Running the Application

### Terminal 1: Django Backend
```bash
cd backend
python manage.py runserver
```

### Terminal 2: React Frontend
```bash
cd frontend
npm run dev
```

### Terminal 3: Celery Worker (optional)
```bash
cd backend
celery -A assistify worker -l info
```

### Terminal 4: Redis Server
```bash
redis-server
```

## Access Points

- **Frontend:** http://localhost:5173
- **Backend API:** http://localhost:8000
- **Admin Panel:** http://localhost:8000/admin
- **API Docs:** http://localhost:8000/api/docs

## Troubleshooting

### Port Already in Use
```bash
# Find process using port
lsof -i :8000  # macOS/Linux
netstat -ano | findstr :8000  # Windows

# Kill process
kill -9 <PID>  # macOS/Linux
taskkill /PID <PID> /F  # Windows
```

### Database Connection Error
```bash
# Check PostgreSQL is running
psql -U postgres -c "SELECT 1"

# Reset database
python manage.py migrate --reset
```

### Module Not Found
```bash
# Reinstall dependencies
pip install -r backend/requirements.txt --force-reinstall
npm install --force
```

## Next Steps

1. Configure channel integrations (WhatsApp, Instagram, Facebook, Shopify)
2. Train ML models with your data
3. Deploy to production
4. Monitor performance and analytics

See `DEPLOYMENT.md` for production setup.
