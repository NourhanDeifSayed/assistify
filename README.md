# Assistify

## AI-Powered Multi-Platform Customer Support System

Assistify is an AI-powered, multi-platform customer support system that understands customer intent, generates intelligent responses, and automates e-commerce interactions.

The system provides intelligent product recommendations, conversational order creation, order tracking, complaint management, sentiment analysis, customer support automation, and administrative management through web-based interfaces.

---

## Academic Information

**School:** School of Computational Sciences and Artificial Intelligence (CSAI)
**Document:** Graduation Project Report
**Degree:** Bachelor of Science in CSAI
**Submission Date:** June 2026

This project is submitted in partial fulfillment of the requirements for the degree of Bachelor of Science in Computational Sciences and Artificial Intelligence.

---

## Team Members

| Student Name  | Student ID | Program |
| ------------- | ---------: | ------- |
| Rahma Mourad  |  202201407 | DSAI    |
| Nourhan Deif  |  202201959 | DSAI    |
| Rahma Ibrahim |  202201689 | DSAI    |
| Jehad Mahmoud |  202201211 | DSAI    |

---

## Supervisor

**Dr. Mohamed Sami Rakha**

---

## Project Description

Assistify is designed to improve customer service and e-commerce interactions by providing a unified intelligent platform that understands customer requests and automatically directs each request to the correct workflow.

The platform combines artificial intelligence, natural language processing, web technologies, and database management to provide a complete customer support solution.

Assistify can understand user messages, detect customer intent and sentiment, recommend products, guide customers through checkout, create orders, send confirmation emails, track orders, handle complaints, and escalate conversations to human support when necessary.

The system also provides administrative interfaces for managing products, stock quantities, orders, tracking updates, users, and support tickets.

---

## Problem Statement

Customers who interact with online stores often need to use multiple pages and systems to complete simple operations.

For example, a customer may need to:

* Search manually for suitable products.
* Navigate through several checkout pages.
* Contact support separately to track an order.
* Use another form to submit a complaint.
* Wait for a human agent to answer common questions.
* Repeat personal and order information across different channels.

Traditional customer support systems may also depend heavily on human agents, which can result in slow response times, high operational costs, and inconsistent customer experiences.

In addition, many basic chatbots depend only on predefined responses and cannot properly understand customer intent, sentiment, language, or conversational context.

Assistify addresses these problems by introducing an intelligent, multi-platform customer support system that provides one conversational interface for:

* Product inquiries.
* Product recommendations.
* Order creation.
* Order tracking.
* Complaint submission.
* Customer support.
* Human-agent escalation.

The system uses AI and rule-based processing to understand customer messages and select the correct workflow. This improves response speed, reduces repetitive work, and provides customers with a more convenient and consistent experience.

---

## Project Objectives

The main objectives of Assistify are:

* Build an intelligent conversational customer support system.
* Understand different types of customer requests.
* Detect customer intent and sentiment.
* Provide relevant and context-aware responses.
* Recommend suitable products.
* Automate conversational checkout.
* Validate customer and order information.
* Create customer orders automatically.
* Send order confirmation emails.
* Track order status.
* Handle complaints and support tickets.
* Support human-agent handoff.
* Provide administrative product and order management.
* Maintain secure and organized customer data.
* Provide a scalable architecture for future integrations.

---

## Features

### AI-Powered Chat

* Natural-language customer interaction.
* Intent classification.
* Sentiment analysis.
* Automatic language detection.
* Context-aware conversation processing.
* Intelligent response generation.
* Rule-based fallback when AI parsing fails.
* Conversation-state management.
* Confidence scores for AI pipeline results.

### Product Management

* Product catalog.
* Product search.
* Product details.
* Product availability checking.
* Product stock management.
* Product pricing.
* Product activation and deactivation.
* Product recommendations.
* Inventory validation before order creation.

### Conversational Checkout

* Product selection through chat.
* Guided checkout steps.
* Customer full-name collection.
* Customer email collection.
* Phone-number collection.
* Delivery-address collection.
* Quantity collection.
* Email validation.
* Phone-number validation.
* Quantity validation.
* Stock validation.
* Order confirmation step.
* Cash-on-delivery support.
* Guest checkout support.
* Automatic order creation.
* Automatic stock reduction after successful checkout.
* Transaction-safe order creation.
* Order confirmation email.

### Order Management

* Unique order-number generation.
* Order-item creation.
* Customer information storage.
* Order-status management.
* Order tracking.
* Tracking history.
* Secure tracking token.
* Administrative order updates.
* Order details in Django Admin.
* Custom administrative order pages.

### Complaint and Support Management

* Complaint detection.
* Complaint workflow.
* Support-ticket creation.
* Ticket-number generation.
* Ticket-status management.
* Order-related complaint support.
* Human-agent escalation.
* Human-handoff status.
* Customer issue tracking.

### Administration

* Product administration.
* Inventory administration.
* Order administration.
* Order-item administration.
* Tracking-update administration.
* User administration.
* Support-ticket administration.
* Django Admin dashboard.
* Custom React administrative pages.
* Product creation and editing.
* Order-status updates.
* Stock monitoring.

### Email Notifications

* Gmail SMTP integration.
* Automatic confirmation email after successful order creation.
* Customer name and order information in confirmation emails.
* Email delivery-status metadata.
* Email error handling.
* Configurable sender address.

### Integration Support

* RESTful API.
* Gmail SMTP.
* Optional Shopify draft-order integration.
* Configurable Shopify synchronization status.
* Frontend and backend API communication.
* Docker-based database support.

### Testing and Reliability

* Automated Django tests.
* Chat workflow tests.
* Order workflow tests.
* Product tests.
* User tests.
* Support tests.
* AI/ML pipeline tests.
* Checkout validation tests.
* Email confirmation tests.
* State-machine tests.
* API response tests.

---

## System Architecture

Assistify follows a layered client-server architecture.

```text
┌──────────────────────────────────┐
│          React Frontend          │
│                                  │
│ - Customer Chat Interface        │
│ - Product Pages                  │
│ - Admin Product Pages            │
│ - Admin Order Pages              │
└────────────────┬─────────────────┘
                 │
                 │ HTTP / REST / JSON
                 ▼
┌──────────────────────────────────┐
│     Django REST Framework API    │
│                                  │
│ - Request Routing                │
│ - Serializers                    │
│ - Input Validation               │
│ - Authentication                 │
│ - API Responses                  │
└────────────────┬─────────────────┘
                 │
                 ▼
┌──────────────────────────────────┐
│     AI and Business Orchestrator │
│                                  │
│ - Language Detection             │
│ - Safety Layer                   │
│ - Intent Classification          │
│ - Sentiment Analysis             │
│ - Product Recommendations        │
│ - Complaint Processing           │
│ - Order Tracking                 │
│ - Checkout Processing            │
│ - Response Generation            │
└────────────────┬─────────────────┘
                 │
                 ▼
┌──────────────────────────────────┐
│   Conversational State Machines  │
│                                  │
│ - Checkout State                 │
│ - Complaint State                │
│ - Customer Data Collection       │
│ - Validation                     │
│ - Order Confirmation             │
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
        ┌────────┴────────┐
        ▼                 ▼
┌───────────────┐  ┌─────────────────┐
│  Gmail SMTP   │  │ Optional Shopify│
│ Email Service │  │   Integration   │
└───────────────┘  └─────────────────┘
```

---

## Main System Components

### Frontend

The frontend is implemented using React and provides the user interface for both customers and administrators.

It includes:

* Customer chat interface.
* Product display.
* Product-management pages.
* Order-management pages.
* Administrative dashboards.
* API communication with the backend.
* Form handling.
* Error and loading states.

### Backend

The backend is implemented using Django and Django REST Framework.

It is responsible for:

* API endpoints.
* Database operations.
* Request validation.
* Business rules.
* Order creation.
* Product management.
* User management.
* Complaint handling.
* Email delivery.
* AI pipeline orchestration.
* Administrative functionality.

### AI and ML Layer

The AI and ML layer processes customer messages and extracts meaningful information.

It performs:

* Intent classification.
* Sentiment analysis.
* Language detection.
* Product recommendation.
* Request routing.
* Response generation.
* Confidence calculation.
* Fallback processing.

### Checkout State Machine

The checkout state machine maintains the current checkout stage for every conversation.

Example checkout flow:

```text
Idle
  ↓
Awaiting Product
  ↓
Awaiting Name
  ↓
Awaiting Email
  ↓
Awaiting Phone
  ↓
Awaiting Address
  ↓
Awaiting Quantity
  ↓
Awaiting Confirmation
  ↓
Order Created
```

The state machine ensures that required information is collected in the correct order before creating the order.

### Database

The PostgreSQL database stores the system's structured data.

Main database entities include:

* Users.
* Products.
* Conversations.
* Orders.
* Order items.
* Tracking updates.
* Support tickets.
* Complaint data.
* Customer information.

### Email Service

The system uses Gmail SMTP to send order confirmation messages.

The email service is triggered after successful order creation and database transaction completion.

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

### AI and Machine Learning

* Python-based NLP pipeline
* Intent classification
* Sentiment analysis
* Language detection
* Recommendation engine
* Rule-based fallback engine
* Conversational state machine
* Confidence-based routing

### External Services

* Gmail SMTP
* Optional Shopify API

### DevOps and Development Tools

* Docker
* Docker Compose
* Git
* GitHub
* Python virtual environment
* PowerShell
* npm
* Django test framework

---

## Project Structure

```text
assistify/
│
├── backend/
│   ├── assistify/
│   │   ├── apps/
│   │   │   ├── chat/
│   │   │   │   ├── models.py
│   │   │   │   ├── serializers.py
│   │   │   │   ├── views.py
│   │   │   │   ├── urls.py
│   │   │   │   └── tests/
│   │   │   │
│   │   │   ├── ml/
│   │   │   │   ├── orchestrator.py
│   │   │   │   ├── models.py
│   │   │   │   └── tests/
│   │   │   │
│   │   │   ├── orders/
│   │   │   │   ├── models.py
│   │   │   │   ├── serializers.py
│   │   │   │   ├── services.py
│   │   │   │   ├── admin.py
│   │   │   │   └── tests/
│   │   │   │
│   │   │   ├── products/
│   │   │   ├── support/
│   │   │   └── users/
│   │   │
│   │   ├── settings/
│   │   ├── urls.py
│   │   └── wsgi.py
│   │
│   ├── manage.py
│   └── requirements.txt
│
├── frontend/
│   ├── public/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   │   ├── AdminProducts.js
│   │   │   ├── AdminOrders.js
│   │   │   └── ...
│   │   ├── services/
│   │   ├── App.js
│   │   └── index.js
│   │
│   ├── package.json
│   └── package-lock.json
│
├── docs/
│   └── screenshots/
│
├── .env
├── .gitignore
├── docker-compose.yml
└── README.md
```

The exact folder structure may vary depending on the current version of the project.

---

## Setup Instructions

## Prerequisites

Before running the project, install:

* Python 3.11
* Node.js
* npm
* Docker Desktop
* Git

Recommended tools:

* Visual Studio Code
* PostgreSQL client
* Postman

---

## 1. Clone the Repository

```bash
git clone <repository-url>
cd assistify
```

Replace `<repository-url>` with the actual GitHub repository URL.

---

## 2. Create the Environment File

Create a `.env` file in the project root:

```env
SECRET_KEY=replace-with-a-secure-secret-key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1,backend

DB_NAME=assistify_db
DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=127.0.0.1
DB_PORT=5433

CORS_ALLOWED_ORIGINS=http://localhost:3001,http://127.0.0.1:3001

EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-google-app-password
DEFAULT_FROM_EMAIL=your-email@gmail.com
```

Important:

* Never publish the `.env` file.
* Never use a normal Gmail password for SMTP.
* Use a Google App Password.
* Never include real credentials in the repository.

Add the following entry to `.gitignore`:

```gitignore
.env
```

---

## 3. Start the PostgreSQL Database

From the directory containing `docker-compose.yml`, run:

```bash
docker compose up -d
```

Check that the database container is running:

```bash
docker ps
```

The development database configuration is:

```text
Database name: assistify_db
Database user: postgres
Database host: 127.0.0.1
Database port: 5433
```

---

## 4. Backend Setup

Open PowerShell in the project directory:

```powershell
cd D:\Assistify_V3\assistify
```

Create a virtual environment:

```powershell
python -m venv .venv
```

Activate the environment:

```powershell
.\.venv\Scripts\Activate.ps1
```

Open the backend directory:

```powershell
cd backend
```

Install Python dependencies:

```powershell
pip install -r requirements.txt
```

Apply migrations:

```powershell
python manage.py migrate
```

Create an administrator account:

```powershell
python manage.py createsuperuser
```

Start the backend server:

```powershell
python manage.py runserver 127.0.0.1:8000
```

The backend is available at:

```text
http://127.0.0.1:8000
```

Django Admin is available at:

```text
http://127.0.0.1:8000/admin/
```

The chat API endpoint is:

```text
POST http://127.0.0.1:8000/api/v1/chat/
```

---

## 5. Frontend Setup

Keep the backend terminal running.

Open another PowerShell terminal:

```powershell
cd D:\Assistify_V3\assistify\frontend
```

Install frontend dependencies:

```powershell
npm install
```

Start the frontend development server:

```powershell
npm start
```

The application URL will be displayed in the terminal.

Common development URLs include:

```text
http://localhost:3000
```

or:

```text
http://localhost:3001
```

---

## 6. Run Backend Tests

Open the backend directory:

```powershell
cd D:\Assistify_V3\assistify\backend
```

Run the complete test suite:

```powershell
python manage.py test
```

Run the chat and order tests:

```powershell
python manage.py test assistify.apps.orders assistify.apps.chat
```

Run AI/ML tests:

```powershell
python manage.py test assistify.apps.ml
```

Run product, user, and support tests:

```powershell
python manage.py test assistify.apps.products assistify.apps.users assistify.apps.support
```

---

## Email Configuration

Assistify sends an email after successful order creation.

### Configure Gmail

1. Open the Google Account settings.
2. Enable 2-Step Verification.
3. Open the App Passwords page.
4. Create a new App Password.
5. Name it:

```text
Assistify Django
```

6. Add the generated password to `.env`:

```env
EMAIL_HOST_PASSWORD=your-new-google-app-password
```

Do not include spaces around the password.

Do not share the password or commit it to GitHub.

### Test Email Delivery

Run:

```powershell
python manage.py shell -c "from django.core.mail import send_mail; print(send_mail('Assistify Test','Email is working',None,['recipient@example.com'],fail_silently=False))"
```

The expected result is:

```text
1
```

A result of `1` means that Django successfully sent the message to the configured SMTP service.

Check the recipient's:

* Inbox.
* Spam folder.
* Promotions folder.

---

## Usage Guide

## Customer Chat

1. Open the Assistify frontend.
2. Open the chat interface.
3. Enter a product question or request.
4. The system analyzes the message.
5. The system detects the intent, language, and sentiment.
6. The appropriate response or workflow is selected.

Example:

```text
Customer: What products are available?

Assistify: Here are some available products.
```

---

## Product Recommendation

The customer can ask for a recommendation:

```text
Customer: Can you recommend a health monitoring device?
```

Assistify analyzes the request and returns relevant products based on the available product data and recommendation logic.

---

## Conversational Checkout

To create an order, the customer starts by selecting a product.

Example:

```text
Customer: I want to buy a Blood Pressure Monitor.

Assistify: Please share your full name.

Customer: Hossam Amir

Assistify: Please share your email address.

Customer: customer@example.com

Assistify: Please share your phone number.

Customer: 01011223344

Assistify: Please share your delivery address.

Customer: Nasr City, Cairo, Egypt

Assistify: Please enter the required quantity.

Customer: 2

Assistify: Please confirm your order.

Customer: Confirm order
```

After confirmation, the system:

* Validates the provided information.
* Checks the available product stock.
* Creates the order.
* Creates the order item.
* Reduces the product stock.
* Generates an order number.
* Sends a confirmation email.
* Returns a tracking token.

---

## Order Tracking

The customer should keep the order number returned after order creation.

Example:

```text
Track order ORD-2026-XXXXXXXXXXXX
```

The system returns the current order status and the latest tracking updates.

Possible statuses may include:

* Placed.
* Processing.
* Warehouse.
* Shipped.
* Delivered.
* Cancelled.

---

## Complaint Submission

The customer can submit a complaint through the chat.

Example:

```text
Customer: I have a problem with my order.
```

The system collects the required information and may create a support ticket.

The response can include:

* Ticket number.
* Ticket status.
* Related order.
* Human-handoff status.

---

## Human Support

If the system detects that the request requires human assistance, it can mark the conversation for human handoff.

Examples include:

* Complex complaints.
* Repeated failed responses.
* Sensitive customer issues.
* Requests that cannot be completed automatically.

---

## Administration Guide

Open Django Admin:

```text
http://127.0.0.1:8000/admin/
```

Sign in using the superuser account.

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

The React frontend also contains administrative pages for products and orders.

---

## API Documentation

## Chat Endpoint

```http
POST /api/v1/chat/
Content-Type: application/json
```

### Create a New Conversation

```json
{
  "message": "I want to buy a Blood Pressure Monitor"
}
```

Example response:

```json
{
  "success": true,
  "response": "Please share your full name.",
  "intent": "purchase_intent",
  "conversation_id": 43,
  "metadata": {
    "purchase_state": "awaiting_name",
    "checkout_completed": false
  }
}
```

### Continue an Existing Conversation

Use the returned `conversation_id`:

```json
{
  "message": "Hossam Amir",
  "conversation_id": 43
}
```

The same conversation ID should be included in all following requests.

### Successful Order Response

```json
{
  "success": true,
  "response": "Your order was created successfully.",
  "intent": "order_created",
  "metadata": {
    "purchase_state": "idle",
    "order_id": 14,
    "order_number": "ORD-2026-XXXXXXXXXXXX",
    "checkout_completed": true,
    "confirmation_email_sent": true,
    "confirmation_email_error": null
  },
  "conversation_id": 43
}
```

---

## Screenshots and Demo

Create the following folder:

```text
docs/screenshots/
```

Recommended screenshots:

* Home page.
* Customer chat interface.
* Product catalog.
* Product recommendations.
* Checkout conversation.
* Successful order response.
* Confirmation email.
* Order-tracking response.
* Complaint workflow.
* Support-ticket response.
* Admin products page.
* Admin orders page.
* Django Admin dashboard.

Example:

```markdown
![Home Page](docs/screenshots/home-page.png)

![AI Chat](docs/screenshots/chat.png)

![Product Recommendation](docs/screenshots/recommendation.png)

![Checkout](docs/screenshots/checkout.png)

![Order Confirmation](docs/screenshots/order-confirmation.png)

![Confirmation Email](docs/screenshots/email.png)

![Order Tracking](docs/screenshots/tracking.png)

![Admin Products](docs/screenshots/admin-products.png)

![Admin Orders](docs/screenshots/admin-orders.png)
```

### Demo Video

```text
Add the project demonstration video link here.
```

### Live Demo

```text
Add the deployed application link here.
```

---

## Repository Professionalism Requirements

The repository should demonstrate:

* Clean and maintainable code.
* Logical folder organization.
* Proper documentation.
* Well-commented implementation.
* Consistent naming conventions.
* Meaningful commit messages.
* Proper branching strategy.
* Clear separation of frontend and backend.
* Clear separation of AI logic and business logic.
* Secure credential management.
* No secrets committed to version control.
* Proper input validation.
* Proper error handling.
* Reproducible installation instructions.
* Clear deployment instructions.
* Automated tests.
* Professional README documentation.
* Organized API endpoints.
* Reusable components and services.

---

## Recommended Branching Strategy

```text
main
├── develop
├── feature/ai-chat
├── feature/product-recommendation
├── feature/chat-checkout
├── feature/order-tracking
├── feature/complaint-workflow
├── feature/email-confirmation
├── feature/admin-dashboard
├── fix/frontend-build
└── fix/api-validation
```

### Branch Descriptions

* `main`: Stable production-ready version.
* `develop`: Integrated development version.
* `feature/*`: New system features.
* `fix/*`: Bug fixes.
* `test/*`: Test-related changes.
* `docs/*`: Documentation changes.

---

## Commit Message Examples

```text
feat: add conversational checkout workflow
```

```text
feat: add product recommendation service
```

```text
feat: send confirmation email after order creation
```

```text
feat: add order tracking workflow
```

```text
fix: validate quantity before creating order
```

```text
fix: resolve duplicate variable declaration in admin products page
```

```text
fix: improve complaint intent routing
```

```text
test: add checkout state machine tests
```

```text
test: add order confirmation email tests
```

```text
docs: update project README
```

```text
refactor: improve AI orchestration pipeline
```

---

## Security Notes

* Never commit `.env`.
* Never expose the Django `SECRET_KEY`.
* Never share Google App Passwords.
* Revoke exposed credentials immediately.
* Use strong database passwords.
* Use HTTPS in production.
* Validate all customer inputs.
* Restrict administrative pages.
* Restrict production CORS origins.
* Do not expose the database publicly.
* Store production credentials in a secret manager.
* Disable Django debug mode in production.
* Regularly update project dependencies.
* Back up the production database.
* Review logs for suspicious activity.

---

## Testing

The project includes automated tests for major system components.

Tested areas include:

* User operations.
* Product operations.
* Support workflows.
* AI orchestration.
* Intent classification.
* Sentiment analysis.
* Language detection.
* Recommendation processing.
* Chat API responses.
* Checkout states.
* Email validation.
* Phone validation.
* Quantity validation.
* Order creation.
* Stock reduction.
* Confirmation emails.
* Order tracking.
* Complaint handling.

Run all tests:

```powershell
python manage.py test
```

Successful tests help ensure that changes do not break existing functionality.

---

## Known Limitations

Current limitations may include:

* Recommendation quality depends on the available product data.
* Some AI requests may require fallback processing.
* Gmail SMTP requires valid account configuration.
* Shopify integration may be disabled when credentials are unavailable.
* Human-agent communication is not fully real-time.
* Deployment settings require additional production configuration.
* Some customer languages may have limited NLP support.
* Online payment integration is not currently included.

---

## Future Enhancements

Potential future improvements include:

* Online payment gateway integration.
* Real-time human support chat.
* Advanced multilingual support.
* Voice-based customer interaction.
* Mobile application.
* WhatsApp integration.
* Facebook Messenger integration.
* SMS order notifications.
* Advanced recommendation models.
* Customer authentication and profiles.
* Order cancellation workflow.
* Return and refund management.
* Product reviews and ratings.
* AI response-quality monitoring.
* Customer-service analytics.
* Sales analytics dashboard.
* Advanced Shopify synchronization.
* Cloud deployment.
* CI/CD pipeline.
* Containerized frontend and backend.
* Redis caching.
* Asynchronous email processing.
* Real-time notifications.
* Improved security monitoring.

---

## Contribution Guidelines

When contributing to the project:

1. Create a new branch.
2. Use a clear branch name.
3. Follow the existing code style.
4. Write meaningful comments when necessary.
5. Add or update tests.
6. Run the test suite.
7. Use meaningful commit messages.
8. Create a pull request.
9. Request code review.
10. Do not include credentials or environment files.

Example:

```bash
git checkout -b feature/new-feature
```

After completing the changes:

```bash
git add .
git commit -m "feat: add new feature"
git push origin feature/new-feature
```

