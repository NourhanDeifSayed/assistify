# Assistify - AI-Powered Medical E-commerce Platform

Assistify is a full-stack medical e-commerce platform enhanced with AI capabilities, including an intelligent chatbot and a recommendation system. The platform supports English and Arabic and integrates with Shopify for product and order management.

---

## Features

* AI chatbot for customer support with semantic understanding
* Product recommendations based on user queries and intent
* Complete e-commerce flow: browsing, cart, and order placement
* Multilingual support (Arabic and English)
* Shopify integration for products and orders
* Guided checkout flow using a state machine
* Content safety layer for filtering sensitive or harmful inputs

---

## Tech Stack

### Backend

* Django
* Django REST Framework
* PostgreSQL

### Frontend

* React.js

### AI / Machine Learning

* Ollama (Qwen2.5:7b)
* Sentence Transformers (MiniLM)
* Scikit-learn

### E-commerce

* Shopify Admin API

### DevOps

* Docker
* Docker Compose

---

## ML Models Setup

This project uses Git LFS to manage large model files.

After cloning:

```bash
git lfs install
git lfs pull
```

If Git LFS is not installed:
https://git-lfs.com/

---

## Quick Start

```bash
git clone https://github.com/NourhanDeifSayed/assistify.git
cd assistify
git lfs install
git lfs pull
```

---

## Running with Docker

### Prerequisites

* Docker
* Docker Compose

### Run

```bash
docker-compose up --build
```

### Access

* Frontend: http://localhost:3000
* Backend API: http://localhost:8000/api/v1/
* Django Admin: http://localhost:8000/admin/

---

## Local Development

### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

pip install -r requirements.txt
pip install psutil sentence-transformers scikit-learn transformers torch ollama

cp .env.example .env

python manage.py migrate
python manage.py train_minilm
python manage.py runserver
```

---

### Frontend

```bash
cd frontend
npm install
cp .env.example .env
npm start
```

---

## AI Components

* Intent classification (e.g. purchase, tracking, complaint)
* Sentiment analysis
* Semantic product recommendation using MiniLM
* Response generation using Qwen2.5 via Ollama
* Safety filtering for restricted content
* Checkout assistant for collecting order data

---

## Shopify Integration

* Product listing and search
* Draft order creation
* Payment link generation
* Order tracking

---

## Updating Product Embeddings

```bash
docker-compose exec backend python manage.py train_minilm
```

---

## Notes

* ML models must be downloaded via Git LFS
* Ollama must be installed and running
* Shopify credentials are required
* The system uses rule-based routing before falling back to the language model

---

## Environment Variables

### Shopify

* SHOPIFY_STORE_DOMAIN
* SHOPIFY_ACCESS_TOKEN
* SHOPIFY_API_VERSION

### Database

* POSTGRES_DB
* POSTGRES_USER
* POSTGRES_PASSWORD

### Django

* SECRET_KEY
* DEBUG
* ALLOWED_HOSTS

---
