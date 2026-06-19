# Assistify

Assistify is an AI-powered, multi-platform customer support system that understands customer intent, generates intelligent responses, recommends suitable products, automates e-commerce interactions, creates and tracks orders, manages complaints, and supports human-agent escalation.

---

## Team Members

| Name          |        ID | Program |
| ------------- | --------: | ------- |
| Rahma Mourad  | 202201407 | DSAI    |
| Nourhan Deif  | 202201959 | DSAI    |
| Rahma Ibrahim | 202201689 | DSAI    |
| Jehad Mahmoud | 202201211 | DSAI    |

---

## Supervisor

**Dr. Mohamed Sami Rakha**

---

## Problem Statement

Online customers often need to use multiple systems to search for products, receive recommendations, place orders, track deliveries, and communicate with customer support.

Traditional customer support systems usually depend heavily on human agents. This may result in slow response times, repetitive work, increased operational costs, and inconsistent customer experiences.

Basic rule-based chatbots also have limited capabilities because they may not understand customer intent, sentiment, language, or the context of a multi-step conversation.

Assistify addresses these problems by providing a unified intelligent customer support platform that can:

* Understand natural-language customer messages.
* Detect customer intent and sentiment.
* Identify the language used by the customer.
* Recommend relevant products.
* Guide the customer through a conversational checkout process.
* Validate customer and order information.
* Create orders automatically.
* Send order confirmation emails.
* Track existing orders.
* Handle complaints and support tickets.
* Escalate conversations to human support when necessary.

The system improves the customer experience by providing faster responses, reducing repetitive manual operations, and combining multiple e-commerce and support services into one conversational interface.

---

## Features

### AI-Powered Customer Support

* Natural-language customer interaction.
* Customer intent classification.
* Sentiment analysis.
* Automatic language detection.
* Context-aware response generation.
* Confidence-based AI routing.
* Rule-based fallback when AI parsing fails.
* Conversation-state management.

### Product Services

* Product catalog.
* Product search.
* Product recommendations.
* Product availability checking.
* Product price display.
* Inventory and stock management.
* Product activation and deactivation.

### Conversational Checkout

* Product selection through chat.
* Guided multi-step checkout.
* Customer full-name collection.
* Customer email collection and validation.
* Customer phone-number collection and validation.
* Delivery-address collection.
* Quantity collection and validation.
* Product stock validation.
* Order confirmation step.
* Guest checkout support.
* Cash-on-delivery support.
* Automatic order creation.
* Automatic product stock reduction.
* Unique order-number generation.

### Order Management

* Order creation.
* Order-item creation.
* Order-status management.
* Secure order tracking.
* Tracking-token generation.
* Tracking-update history.
* Administrative order management.
* Automatic order confirmation emails.

### Complaint and Support Management

* Complaint-intent detection.
* Support-ticket creation.
* Ticket-number generation.
* Ticket-status management.
* Order-related complaint processing.
* Human-agent handoff.
* Support escalation when automation is insufficient.

### Administration

* Django Admin dashboard.
* Product administration.
* Inventory administration.
* Order administration.
* Order-item administration.
* Tracking-update administration.
* User administration.
* Support-ticket administration.
* Custom React admin product page.
* Custom React admin order page.

### Testing and Reliability

* Automated backend tests.
* User-management tests.
* Product-management tests.
* Support-workflow tests.
* AI/ML pipeline tests.
* Checkout state-machine tests.
* Order-creation tests.
* Input-validation tests.
* Confirmation-email tests.
* Chat API tests.

---

## System Architecture

Assistify follows a layered client-server architecture.

```text
┌──────────────────────────────────┐
│          React Frontend          │
│                                  │
│ - Customer Chat Interface        │
│ - Product Interface              │
│ - Admin Products Page            │
│ - Admin Orders Page              │
└────────────────┬─────────────────┘
                 │
                 │ HTTP / JSON
                 ▼
┌──────────────────────────────────┐
│     Django REST Framework API    │
│                                  │
│ - API Routing                    │
│ - Serializers                    │
│ - Request Validation             │
│ - Authentication                 │
│ - Response Handling              │
└────────────────┬─────────────────┘
                 │
                 ▼
┌──────────────────────────────────┐
│      AI and ML Orchestrator      │
│                                  │
│ - Language Detection             │
│ - Safety Processing              │
│ - Intent Classification          │
│ - Sentiment Analysis             │
│ - Product Recommendation         │
│ - Response Generation            │
│ - Workflow Routing               │
└────────────────┬─────────────────┘
                 │
                 ▼
┌──────────────────────────────────┐
│   Conversational State Machines  │
│                                  │
│ - Checkout Workflow              │
│ - Complaint Workflow             │
│ - Order Tracking Workflow        │
│ - Customer Input Validation      │
└────────────────┬─────────────────┘
                 │
                 ▼
┌──────────────────────────────────┐
│       PostgreSQL Database        │
│                                  │
│ - Users                          │
│ - Products                       │
│ - Conversations                  │
│ - Orders                         │
│ - Order Items                    │
│ - Tracking Updates               │
│ - Support Tickets                │
└────────────────┬─────────────────┘
                 │
        ┌────────┴─────────┐
        ▼                  ▼
┌───────────────┐   ┌─────────────────┐
│  Gmail SMTP   │   │ Optional Shopify│
│ Email Service │   │   Integration   │
└───────────────┘   └─────────────────┘
```

### Architecture Overview

The React frontend provides the customer and administrative user interfaces.

The frontend communicates with the Django REST Framework backend through REST API requests using JSON.

The backend validates each request and sends customer messages to the AI and ML orchestration layer.

The orchestration layer performs language detection, intent classification, sentiment analysis, recommendation generation, and workflow routing.

Multi-step operations such as checkout and complaint creation are managed using conversational state machines.

PostgreSQL stores products, users, conversations, orders, order items, tracking updates, and support tickets.

Gmail SMTP is used to send order confirmation emails. The system also includes optional support for Shopify integration.

---

## Technologies Used

### Frontend

* React
* JavaScript
* HTML5
* CSS3
* Fetch API
* Create React App
* Webpack
* npm

### Backend

* Python 3.11
* Django
* Django REST Framework
* Django CORS Headers

### Database

* PostgreSQL

### AI/ML Frameworks and Techniques

* Python-based AI and NLP pipeline.
* Intent classification.
* Sentiment analysis.
* Automatic language detection.
* Product recommendation engine.
* Confidence-based request routing.
* Rule-based fallback processing.
* Conversational state machines.

### Cloud Services and External Integrations

* Gmail SMTP for email notifications.
* Optional Shopify API integration.
* The system can be deployed to cloud platforms that support Docker, Python, Node.js, and PostgreSQL.

### DevOps Tools

* Docker
* Docker Compose
* Git
* GitHub
* Python virtual environments
* npm
* PowerShell

---

## Setup Instructions

### Prerequisites

Install the following software before running the project:

* Python 3.11
* Node.js
* npm
* Docker Desktop
* Git

### 1. Clone the Repository

```bash
git clone <repository-url>
cd assistify
```

Replace `<repository-url>` with the actual GitHub repository URL.

### 2. Create the Environment File

Create a file named `.env` in the project root.

```env
SECRET_KEY=replace-with-a-secure-secret-key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1,backend

DB_NAME=assistify_db
DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=127.0.0.1
DB_PORT=5433

CORS_ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000,http://localhost:3001,http://127.0.0.1:3001

EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-google-app-password
DEFAULT_FROM_EMAIL=your-email@gmail.com
```

Do not add real passwords or secret values to the repository.

Make sure `.env` is listed inside `.gitignore`.

```gitignore
.env
```

### 3. Start the PostgreSQL Database

Run the following command from the directory containing `docker-compose.yml`:

```bash
docker compose up -d
```

Check that the database container is running:

```bash
docker ps
```

The local database configuration is:

```text
Database name: assistify_db
Database user: postgres
Database host: 127.0.0.1
Database port: 5433
```

### 4. Create the Python Virtual Environment

From the project root:

```powershell
python -m venv .venv
```

Activate the environment on Windows:

```powershell
.\.venv\Scripts\Activate.ps1
```

### 5. Install Backend Dependencies

Open the backend directory:

```powershell
cd backend
```

Install the required Python packages:

```powershell
pip install -r requirements.txt
```

### 6. Apply Database Migrations

```powershell
python manage.py migrate
```

### 7. Create an Administrator Account

```powershell
python manage.py createsuperuser
```

Enter the required username, email address, and password.

### 8. Start the Backend Server

```powershell
python manage.py runserver 127.0.0.1:8000
```

The backend will be available at:

```text
http://127.0.0.1:8000
```

The Django Admin dashboard will be available at:

```text
http://127.0.0.1:8000/admin/
```

The chat API endpoint is:

```text
http://127.0.0.1:8000/api/v1/chat/
```

### 9. Install Frontend Dependencies

Keep the backend terminal running.

Open another terminal and run:

```powershell
cd frontend
npm install
```

### 10. Start the Frontend

```powershell
npm start
```

The frontend URL will be displayed in the terminal.

It will commonly be one of the following:

```text
http://localhost:3000
```

or:

```text
http://localhost:3001
```

### 11. Run the Tests

Open the backend directory:

```powershell
cd backend
```

Run the complete backend test suite:

```powershell
python manage.py test
```

Run the chat and order tests:

```powershell
python manage.py test assistify.apps.orders assistify.apps.chat
```

Run the AI/ML tests:

```powershell
python manage.py test assistify.apps.ml
```

Run the product, user, and support tests:

```powershell
python manage.py test assistify.apps.products assistify.apps.users assistify.apps.support
```

---

## Deployment Instructions

### Local Deployment

Start PostgreSQL:

```bash
docker compose up -d
```

Start the backend:

```powershell
cd backend
python manage.py runserver 127.0.0.1:8000
```

Start the frontend in another terminal:

```powershell
cd frontend
npm start
```

### Docker Deployment

Build the Docker images:

```bash
docker compose build
```

Start the configured services:

```bash
docker compose up -d
```

Check the running services:

```bash
docker compose ps
```

Apply database migrations:

```bash
docker compose exec backend python manage.py migrate
```

Create an administrator account:

```bash
docker compose exec backend python manage.py createsuperuser
```

View service logs:

```bash
docker compose logs -f
```

Stop the services:

```bash
docker compose down
```

### Frontend Production Build

Open the frontend directory:

```bash
cd frontend
```

Install the dependencies:

```bash
npm install
```

Create the production build:

```bash
npm run build
```

The production frontend files will be generated inside:

```text
frontend/build/
```

### Production Requirements

Before deploying the system to production:

* Set `DEBUG=False`.
* Generate a secure Django `SECRET_KEY`.
* Configure production `ALLOWED_HOSTS`.
* Restrict CORS origins.
* Use secure database credentials.
* Store credentials using environment variables or a secret manager.
* Enable HTTPS.
* Configure static-file hosting.
* Configure media-file hosting.
* Use a production WSGI server.
* Configure database backups.
* Configure logging and monitoring.
* Do not expose PostgreSQL publicly.
* Do not commit `.env` or secret values.

---

## Usage Guide

### Customer Chat

1. Open the Assistify frontend.
2. Open the customer chat interface.
3. Enter a product inquiry, purchase request, tracking request, or complaint.
4. The system analyzes the message.
5. The customer's intent, sentiment, and language are detected.
6. The appropriate response or workflow is selected.

### Product Inquiry

Example:

```text
What products are available?
```

Assistify displays the available products.

### Product Recommendation

Example:

```text
Can you recommend a health monitoring device?
```

Assistify analyzes the request and returns relevant product recommendations.

### Conversational Checkout

Example checkout conversation:

```text
Customer: I want to buy a Blood Pressure Monitor.

Assistify: Please share your full name.

Customer: Rahma

Assistify: Please share your email address.

Customer: customer@example.com

Assistify: Please share your phone number.

Customer: 01011223344

Assistify: Please share your delivery address.

Customer: Nasr City, Cairo, Egypt

Assistify: Please enter the required quantity.

Customer: 2

Assistify: Please confirm your order.

Customer: Confirm order.
```

After confirmation, the system:

* Validates the customer information.
* Validates the requested quantity.
* Checks product availability.
* Creates the order.
* Creates the order item.
* Reduces product stock.
* Generates a unique order number.
* Generates a tracking token.
* Sends a confirmation email.

### Order Tracking

The customer can track an order using its order number.

Example:

```text
Track order ORD-2026-XXXXXXXXXXXX
```

The system returns the current order status and available tracking updates.

### Complaint Submission

Example:

```text
I have a problem with my order.
```

The system identifies the complaint, collects the required information, and creates a support ticket when necessary.

### Administration

Open the Django Admin dashboard:

```text
http://127.0.0.1:8000/admin/
```

Administrators can manage:

* Users.
* Products.
* Product prices.
* Product stock.
* Product availability.
* Orders.
* Order items.
* Tracking updates.
* Conversations.
* Support tickets.

---

## Screenshots / Demo
### Home Page

![Home Page](docs/screenshots/home-page.png)

### Customer Chat Interface

![Customer Chat](docs/screenshots/customer-chat.png)

### Product Catalog

![Product Catalog](docs/screenshots/product-catalog.png)

### Product Recommendation

![Product Recommendation](docs/screenshots/product-recommendation.png)

### Conversational Checkout

![Conversational Checkout](docs/screenshots/checkout.png)

### Successful Order

![Successful Order](docs/screenshots/successful-order.png)

### Confirmation Email

![Confirmation Email](docs/screenshots/confirmation-email.png)

### Order Tracking

![Order Tracking](docs/screenshots/order-tracking.png)

### Complaint Workflow

![Complaint Workflow](docs/screenshots/complaint-workflow.png)

### Admin Products Page

![Admin Products](docs/screenshots/admin-products.png)

### Admin Orders Page

![Admin Orders](docs/screenshots/admin-orders.png)

### Django Admin Dashboard

![Django Admin](docs/screenshots/django-admin.png)


### Demo Video

![Assistify Demo](docs/screenshots/assistify-demo.gif)

```text
Demo Video: https://drive.google.com/file/d/your-video-id/view

---
