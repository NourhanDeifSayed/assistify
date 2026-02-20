# Assistify Quick Start Guide

Get up and running with Assistify in 5 minutes.

## For Windows Users

### Step 1: Extract ZIP
```
Right-click assistify_complete.zip
Select "Extract All"
Choose destination folder
```

### Step 2: Install Python & Node.js
```
Download Python 3.9+: https://www.python.org/downloads/
Download Node.js 18+: https://nodejs.org/
Run installers with default settings
```

### Step 3: Setup Backend
```powershell
cd assistify_complete\backend
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
```

### Step 4: Setup Frontend
```powershell
cd ..\frontend
npm install
```

### Step 5: Run Application

**Terminal 1 - Backend:**
```powershell
cd assistify_complete\backend
.\venv\Scripts\activate
python manage.py runserver
```

**Terminal 2 - Frontend:**
```powershell
cd assistify_complete\frontend
npm run dev
```

### Step 6: Access Application
- **Frontend:** http://localhost:5173
- **Backend API:** http://localhost:8000
- **Admin:** http://localhost:8000/admin

---

## For Linux/Mac Users

### Step 1: Extract ZIP
```bash
unzip assistify_complete.zip
cd assistify_complete
```

### Step 2: Setup Backend
```bash
python3.9 -m venv venv
source venv/bin/activate
pip install -r backend/requirements.txt
```

### Step 3: Setup Frontend
```bash
cd frontend
npm install
cd ..
```

### Step 4: Setup Database
```bash
# Install PostgreSQL if not already installed
# macOS: brew install postgresql
# Linux: sudo apt-get install postgresql

# Create database
createdb assistify

# Run migrations
cd backend
python manage.py migrate
```

### Step 5: Run Application

**Terminal 1 - Backend:**
```bash
cd backend
source ../venv/bin/activate
python manage.py runserver
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```

### Step 6: Access Application
- **Frontend:** http://localhost:5173
- **Backend API:** http://localhost:8000
- **Admin:** http://localhost:8000/admin

---

## Project Structure

```
assistify_complete/
├── backend/              # Django backend
│   ├── assistify/       # Main Django project
│   ├── chatbot/         # Chatbot app
│   ├── channels/        # Channel integrations
│   └── requirements.txt # Python dependencies
├── frontend/            # React frontend
│   ├── src/            # React source code
│   ├── package.json    # Node dependencies
│   └── public/         # Static assets
├── ml_models/          # Machine learning models
│   ├── intent_classification/
│   ├── sentiment_analysis/
│   ├── response_generation/
│   ├── product_recommendation/
│   └── training/       # Training scripts
├── docs/               # Documentation
│   ├── SETUP.md       # Detailed setup guide
│   ├── API.md         # API documentation
│   ├── MODELS.md      # ML models documentation
│   ├── ARCHITECTURE.md # System architecture
│   └── DEPLOYMENT.md  # Deployment guide
└── config/            # Configuration files
    ├── database.sql   # Database schema
    └── .env.example   # Environment variables
```

---

## Key Features

### 4 ML Models
1. **Intent Classification** - Understand customer intent
2. **Sentiment Analysis** - Analyze customer emotions
3. **Response Generation** - Generate intelligent responses
4. **Product Recommendation** - Recommend products

### Multi-Channel Support
- WhatsApp (Twilio)
- Instagram (Meta)
- Facebook Messenger (Meta)
- Shopify Chat

### Admin Dashboard
- Real-time chat monitoring
- Customer analytics
- Model performance metrics
- Channel statistics

---

## Common Commands

### Backend
```bash
# Run development server
python manage.py runserver

# Create admin user
python manage.py createsuperuser

# Run migrations
python manage.py migrate

# Create new app
python manage.py startapp app_name

# Run tests
python manage.py test
```

### Frontend
```bash
# Run development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview

# Run linter
npm run lint

# Format code
npm run format
```

### ML Models
```bash
# Train all models
cd ml_models/training
python train_all_models.py

# Train specific model
python train_intent_classifier.py
```

---

## Environment Configuration

Create `.env` file in root directory:

```
# Database
DATABASE_URL=postgresql://postgres:password@localhost:5432/assistify

# Django
SECRET_KEY=your-secret-key-here
DEBUG=True

# WhatsApp (Twilio)
TWILIO_ACCOUNT_SID=your_account_sid
TWILIO_AUTH_TOKEN=your_auth_token

# Instagram/Facebook (Meta)
META_ACCESS_TOKEN=your_access_token

# Shopify
SHOPIFY_API_KEY=your_api_key
```

See `config/.env.example` for all available options.

---

## Troubleshooting

### Port Already in Use
```bash
# Windows
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# macOS/Linux
lsof -i :8000
kill -9 <PID>
```

### Database Connection Error
```bash
# Check PostgreSQL is running
psql -U postgres -c "SELECT 1"

# Create database if missing
createdb assistify
```

### Module Not Found
```bash
# Reinstall dependencies
pip install -r backend/requirements.txt --force-reinstall
npm install --force
```

### Port 3000 Already in Use
```bash
# Use different port
npm run dev -- --port 3001
```

---

## Next Steps

1. **Configure Channels**
   - Set up WhatsApp integration
   - Configure Instagram/Facebook
   - Connect Shopify store

2. **Train Models**
   - Prepare training data
   - Run `python train_all_models.py`
   - Monitor model performance

3. **Deploy to Production**
   - Follow `docs/DEPLOYMENT.md`
   - Set up monitoring
   - Configure backups

4. **Monitor & Optimize**
   - Check analytics dashboard
   - Monitor API performance
   - Retrain models regularly

---

## Documentation

- **Setup Guide:** `docs/SETUP.md`
- **API Documentation:** `docs/API.md`
- **ML Models Guide:** `docs/MODELS.md`
- **Architecture:** `docs/ARCHITECTURE.md`
- **Deployment:** `docs/DEPLOYMENT.md`

---

## Support

For issues and questions:
1. Check the documentation
2. Review error logs
3. Check GitHub issues
4. Contact support team

---

## License

This project is licensed under the MIT License.

---

**Happy coding! 🚀**
