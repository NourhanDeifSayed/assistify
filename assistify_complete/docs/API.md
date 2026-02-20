# Assistify API Documentation

Complete REST API documentation for Assistify chatbot platform.

## Base URL
```
http://localhost:8000/api
```

## Authentication
All endpoints require Bearer token authentication:
```
Authorization: Bearer <token>
```

## Endpoints

### Messages

#### Process Message
**POST** `/messages/process_message/`

Process a customer message through all ML models.

**Request:**
```json
{
  "content": "I want to buy the gold package",
  "conversation_id": 1
}
```

**Response:**
```json
{
  "message_id": 1,
  "intent": "purchase",
  "sentiment": "positive",
  "response": "Great! The gold package costs $500/month...",
  "confidence": 0.95
}
```

#### Get Conversation Messages
**GET** `/messages/get_conversation_messages/?conversation_id=1`

Retrieve all messages in a conversation.

**Response:**
```json
[
  {
    "id": 1,
    "conversation_id": 1,
    "sender": "customer",
    "content": "I want to buy the gold package",
    "intent": "purchase",
    "sentiment": "positive",
    "confidence": 0.95,
    "created_at": "2024-02-12T10:30:00Z"
  }
]
```

### Conversations

#### Create Conversation
**POST** `/conversations/create_conversation/`

Create a new conversation.

**Request:**
```json
{
  "customer_id": 1,
  "channel": "whatsapp"
}
```

**Response:**
```json
{
  "id": 1,
  "customer_id": 1,
  "channel": "whatsapp",
  "status": "active",
  "created_at": "2024-02-12T10:30:00Z"
}
```

#### Get Conversations
**GET** `/conversations/`

List all conversations for the authenticated user.

**Response:**
```json
[
  {
    "id": 1,
    "customer_id": 1,
    "channel": "whatsapp",
    "status": "active",
    "created_at": "2024-02-12T10:30:00Z"
  }
]
```

#### Close Conversation
**POST** `/conversations/{id}/close_conversation/`

Close a conversation.

**Response:**
```json
{
  "id": 1,
  "customer_id": 1,
  "channel": "whatsapp",
  "status": "closed",
  "created_at": "2024-02-12T10:30:00Z"
}
```

### Webhooks

#### WhatsApp Webhook
**POST** `/webhooks/whatsapp/`

Receive incoming WhatsApp messages.

**Request (from Twilio):**
```json
{
  "From": "whatsapp:+1234567890",
  "Body": "I want to buy the gold package",
  "MessageSid": "SM1234567890"
}
```

#### Instagram Webhook
**POST** `/webhooks/instagram/`

Receive incoming Instagram messages.

**Request (from Meta):**
```json
{
  "entry": [
    {
      "messaging": [
        {
          "sender": {"id": "123456"},
          "message": {"text": "I want to buy the gold package"}
        }
      ]
    }
  ]
}
```

### Analytics

#### Get Intent Statistics
**GET** `/analytics/intent_stats/`

Get statistics about customer intents.

**Response:**
```json
{
  "purchase": 45,
  "support": 30,
  "complaint": 10,
  "inquiry": 25,
  "return": 5,
  "tracking": 15
}
```

#### Get Sentiment Statistics
**GET** `/analytics/sentiment_stats/`

Get statistics about customer sentiments.

**Response:**
```json
{
  "positive": 60,
  "neutral": 25,
  "negative": 15
}
```

#### Get Channel Statistics
**GET** `/analytics/channel_stats/`

Get statistics about channel usage.

**Response:**
```json
{
  "whatsapp": 100,
  "instagram": 50,
  "facebook": 30,
  "shopify": 20
}
```

## Error Responses

### 400 Bad Request
```json
{
  "error": "content and conversation_id are required"
}
```

### 401 Unauthorized
```json
{
  "detail": "Authentication credentials were not provided."
}
```

### 404 Not Found
```json
{
  "detail": "Not found."
}
```

### 500 Internal Server Error
```json
{
  "error": "Internal server error"
}
```

## Rate Limiting

- 100 requests per minute per user
- 1000 requests per hour per user

## Pagination

List endpoints support pagination:
```
GET /conversations/?page=1&page_size=10
```

**Response:**
```json
{
  "count": 100,
  "next": "http://localhost:8000/api/conversations/?page=2",
  "previous": null,
  "results": [...]
}
```

## Filtering

Filter by status:
```
GET /conversations/?status=active
```

Filter by channel:
```
GET /conversations/?channel=whatsapp
```

Filter by date range:
```
GET /messages/?created_at__gte=2024-02-01&created_at__lte=2024-02-28
```

## Sorting

Sort by field:
```
GET /conversations/?ordering=-created_at
```

## Examples

### Example 1: Process a Message
```bash
curl -X POST http://localhost:8000/api/messages/process_message/ \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "I want to buy the gold package",
    "conversation_id": 1
  }'
```

### Example 2: Get Conversation Messages
```bash
curl -X GET "http://localhost:8000/api/messages/get_conversation_messages/?conversation_id=1" \
  -H "Authorization: Bearer <token>"
```

### Example 3: Create Conversation
```bash
curl -X POST http://localhost:8000/api/conversations/create_conversation/ \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "customer_id": 1,
    "channel": "whatsapp"
  }'
```

## WebSocket (Real-time)

For real-time chat, use WebSocket:

```javascript
const ws = new WebSocket('ws://localhost:8000/ws/chat/1/');

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log('New message:', data);
};

ws.send(JSON.stringify({
  'message': 'Hello!'
}));
```
