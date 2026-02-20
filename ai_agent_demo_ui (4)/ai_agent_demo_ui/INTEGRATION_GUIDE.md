# 🔗 AI Agent Platform - Integration Guide

## Overview

This guide explains how to integrate the interactive demo with real backend systems and external APIs.

## Multi-Channel Integration

### WhatsApp Business API

**Current Status**: Simulated in demo
**Real Integration Steps**:

1. Get WhatsApp Business Account
2. Configure Twilio or Meta Cloud API
3. Set up webhook endpoint
4. Add to backend router

**Backend Implementation**:
```typescript
// server/routers/whatsapp.ts
import { publicProcedure, router } from "./_core/trpc";

export const whatsappRouter = router({
  webhook: publicProcedure
    .input(z.object({
      from: z.string(),
      message: z.string(),
    }))
    .mutation(async ({ input }) => {
      // Process WhatsApp message
      // Call Manus LLM for response
      // Send back via Twilio API
    }),
});
```

### Instagram Direct Messages

**Current Status**: Simulated in demo
**Real Integration Steps**:

1. Create Instagram Business Account
2. Configure Meta Graph API
3. Set up webhook for DM events
4. Implement message handler

**Backend Implementation**:
```typescript
// server/routers/instagram.ts
export const instagramRouter = router({
  webhook: publicProcedure
    .input(z.object({
      senderId: z.string(),
      message: z.string(),
    }))
    .mutation(async ({ input }) => {
      // Process Instagram DM
      // Call Manus LLM
      // Send response via Meta API
    }),
});
```

### Facebook Messenger

**Current Status**: Simulated in demo
**Real Integration Steps**:

1. Create Facebook Page
2. Configure Messenger Platform
3. Set up webhook
4. Implement message handling

**Backend Implementation**:
```typescript
// server/routers/facebook.ts
export const facebookRouter = router({
  webhook: publicProcedure
    .input(z.object({
      senderId: z.string(),
      message: z.string(),
    }))
    .mutation(async ({ input }) => {
      // Process Facebook message
      // Call Manus LLM
      // Send via Facebook API
    }),
});
```

## Shopify Integration

### Current Status
- Simulated products in demo
- Mock Shopify IDs
- No real inventory sync

### Real Integration Steps

1. **Get Shopify API Credentials**:
   - Shop URL
   - Access Token
   - API Scopes

2. **Configure Environment Variables**:
```env
SHOPIFY_SHOP_URL=your-shop.myshopify.com
SHOPIFY_ACCESS_TOKEN=your-access-token
SHOPIFY_API_VERSION=2024-01
```

3. **Backend Implementation**:
```typescript
// server/shopify.ts
import shopify from 'shopify-api-node';

const client = new shopify({
  shopName: process.env.SHOPIFY_SHOP_URL,
  accessToken: process.env.SHOPIFY_ACCESS_TOKEN,
});

export async function getProducts() {
  return await client.product.list();
}

export async function createOrder(orderData) {
  return await client.order.create(orderData);
}

export async function updateInventory(productId, quantity) {
  return await client.inventoryLevel.adjust({
    inventoryItemId: productId,
    availableDelta: quantity,
  });
}
```

4. **tRPC Procedures**:
```typescript
// server/routers/shopify.ts
export const shopifyRouter = router({
  getProducts: publicProcedure.query(async () => {
    return await getProducts();
  }),
  
  createOrder: protectedProcedure
    .input(orderSchema)
    .mutation(async ({ input }) => {
      return await createOrder(input);
    }),
    
  updateInventory: protectedProcedure
    .input(inventorySchema)
    .mutation(async ({ input }) => {
      return await updateInventory(input.productId, input.quantity);
    }),
});
```

## Manus LLM Integration

### Current Status
- Integrated in demo
- Using Manus API
- Multi-language support

### Configuration

```typescript
// server/_core/llm.ts
import { invokeLLM } from "./llm";

export async function generateResponse(messages: Message[]) {
  return await invokeLLM({
    messages,
    model: "gpt-4",
    temperature: 0.7,
  });
}
```

### Usage in Procedures

```typescript
export const chatRouter = router({
  sendMessage: protectedProcedure
    .input(z.object({
      message: z.string(),
      channel: z.enum(['whatsapp', 'instagram', 'facebook']),
    }))
    .mutation(async ({ input, ctx }) => {
      // Get product context
      const products = await getProducts();
      
      // Build system prompt
      const systemPrompt = buildSystemPrompt(products);
      
      // Call Manus LLM
      const response = await generateResponse([
        { role: 'system', content: systemPrompt },
        { role: 'user', content: input.message },
      ]);
      
      // Save to database
      await saveMessage({
        userId: ctx.user.id,
        channel: input.channel,
        userMessage: input.message,
        aiResponse: response,
      });
      
      return response;
    }),
});
```

## Database Schema

### Chat Messages Table

```sql
CREATE TABLE chatMessages (
  id INT PRIMARY KEY AUTO_INCREMENT,
  userId INT NOT NULL,
  channel ENUM('whatsapp', 'instagram', 'facebook', 'web'),
  userMessage TEXT NOT NULL,
  aiResponse TEXT NOT NULL,
  metadata JSON,
  createdAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (userId) REFERENCES users(id)
);
```

### Orders Table

```sql
CREATE TABLE orders (
  id INT PRIMARY KEY AUTO_INCREMENT,
  customerId INT NOT NULL,
  shopifyOrderId VARCHAR(255),
  channel VARCHAR(50),
  totalAmount DECIMAL(10, 2),
  status ENUM('pending', 'confirmed', 'shipped', 'delivered'),
  trackingNumber VARCHAR(255),
  createdAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (customerId) REFERENCES customers(id)
);
```

### Notifications Table

```sql
CREATE TABLE notifications (
  id INT PRIMARY KEY AUTO_INCREMENT,
  userId INT NOT NULL,
  type ENUM('order', 'shipping', 'message', 'feedback', 'offer'),
  title VARCHAR(255),
  message TEXT,
  read BOOLEAN DEFAULT FALSE,
  createdAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (userId) REFERENCES users(id)
);
```

## Shipping Integration

### DHL Integration

```typescript
// server/shipping/dhl.ts
import axios from 'axios';

const DHL_API = 'https://api.dhl.com';

export async function trackShipment(trackingNumber: string) {
  const response = await axios.get(
    `${DHL_API}/tracking/${trackingNumber}`,
    {
      headers: {
        'Authorization': `Bearer ${process.env.DHL_API_KEY}`,
      },
    }
  );
  return response.data;
}

export async function createShipment(shipmentData) {
  const response = await axios.post(
    `${DHL_API}/shipments`,
    shipmentData,
    {
      headers: {
        'Authorization': `Bearer ${process.env.DHL_API_KEY}`,
      },
    }
  );
  return response.data;
}
```

### FedEx Integration

```typescript
// server/shipping/fedex.ts
export async function trackShipment(trackingNumber: string) {
  // Similar implementation for FedEx
}
```

### UPS Integration

```typescript
// server/shipping/ups.ts
export async function trackShipment(trackingNumber: string) {
  // Similar implementation for UPS
}
```

## Real-Time Notifications

### WebSocket Setup

```typescript
// server/_core/websocket.ts
import { WebSocketServer } from 'ws';

const wss = new WebSocketServer({ port: 8080 });

wss.on('connection', (ws) => {
  ws.on('message', (message) => {
    // Handle incoming messages
  });
  
  ws.on('close', () => {
    // Clean up
  });
});

export function notifyUser(userId: string, notification: Notification) {
  wss.clients.forEach((client) => {
    if (client.userId === userId) {
      client.send(JSON.stringify(notification));
    }
  });
}
```

### Frontend Integration

```typescript
// client/src/hooks/useNotifications.ts
import { useEffect, useState } from 'react';

export function useNotifications() {
  const [notifications, setNotifications] = useState([]);
  
  useEffect(() => {
    const ws = new WebSocket('ws://localhost:8080');
    
    ws.onmessage = (event) => {
      const notification = JSON.parse(event.data);
      setNotifications((prev) => [notification, ...prev]);
    };
    
    return () => ws.close();
  }, []);
  
  return notifications;
}
```

## Analytics Integration

### Event Tracking

```typescript
// server/routers/analytics.ts
export const analyticsRouter = router({
  trackEvent: publicProcedure
    .input(z.object({
      event: z.string(),
      channel: z.string(),
      metadata: z.record(z.any()).optional(),
    }))
    .mutation(async ({ input }) => {
      // Save event to database
      await saveAnalyticsEvent({
        event: input.event,
        channel: input.channel,
        metadata: input.metadata,
        timestamp: new Date(),
      });
    }),
});
```

### Frontend Tracking

```typescript
// client/src/lib/analytics.ts
export function trackEvent(event: string, data?: Record<string, any>) {
  trpc.analytics.trackEvent.mutate({
    event,
    channel: getCurrentChannel(),
    metadata: data,
  });
}
```

## Environment Variables

Create `.env.local` in the project root:

```env
# Manus LLM
BUILT_IN_FORGE_API_URL=https://api.manus.im
BUILT_IN_FORGE_API_KEY=your-api-key

# Shopify
SHOPIFY_SHOP_URL=your-shop.myshopify.com
SHOPIFY_ACCESS_TOKEN=your-access-token

# Shipping APIs
DHL_API_KEY=your-dhl-key
FEDEX_API_KEY=your-fedex-key
UPS_API_KEY=your-ups-key

# WhatsApp
TWILIO_ACCOUNT_SID=your-account-sid
TWILIO_AUTH_TOKEN=your-auth-token
TWILIO_WHATSAPP_NUMBER=+1234567890

# Instagram/Facebook
META_APP_ID=your-app-id
META_APP_SECRET=your-app-secret
META_PAGE_ACCESS_TOKEN=your-page-token

# Database
DATABASE_URL=mysql://user:password@localhost:3306/ai_agent_db

# JWT
JWT_SECRET=your-jwt-secret
```

## Testing Integration

### Unit Tests

```typescript
// server/routers/__tests__/shopify.test.ts
import { describe, it, expect } from 'vitest';
import { shopifyRouter } from '../shopify';

describe('Shopify Router', () => {
  it('should fetch products', async () => {
    const products = await shopifyRouter.getProducts();
    expect(products).toHaveLength(3);
  });
  
  it('should create order', async () => {
    const order = await shopifyRouter.createOrder({
      customerId: 1,
      items: [{ productId: 1, quantity: 2 }],
    });
    expect(order.id).toBeDefined();
  });
});
```

### Integration Tests

```typescript
// e2e/demo.test.ts
import { test, expect } from '@playwright/test';

test('complete customer journey', async ({ page }) => {
  await page.goto('http://localhost:5173/demo');
  
  // Select WhatsApp channel
  await page.click('button:has-text("WhatsApp")');
  
  // Start pre-sale stage
  await page.click('button:has-text("💬")');
  
  // Send message
  await page.fill('input[placeholder="Type message..."]', 'Hello');
  await page.click('button:has-text("Send")');
  
  // Verify response
  expect(await page.locator('text=مرحباً')).toBeDefined();
});
```

## Deployment

### Production Checklist

- [ ] All environment variables configured
- [ ] Database migrations run
- [ ] API keys secured in environment
- [ ] CORS configured for production domain
- [ ] SSL/TLS certificates installed
- [ ] Rate limiting enabled
- [ ] Error logging configured
- [ ] Monitoring and alerts set up
- [ ] Backup strategy implemented
- [ ] Load testing completed

### Docker Deployment

```dockerfile
FROM node:18-alpine

WORKDIR /app

COPY package*.json ./
RUN npm ci

COPY . .
RUN npm run build

EXPOSE 3000

CMD ["npm", "start"]
```

## Support & Troubleshooting

### Common Issues

**Shopify API Connection Failed**
- Verify API credentials
- Check API scopes
- Ensure shop URL is correct

**Manus LLM Not Responding**
- Check API key validity
- Verify network connectivity
- Check rate limits

**WhatsApp Messages Not Received**
- Verify webhook URL
- Check webhook signature
- Ensure Twilio credentials are correct

## Next Steps

1. Set up Shopify API credentials
2. Configure WhatsApp Business Account
3. Set up Instagram/Facebook apps
4. Configure Manus LLM API
5. Set up shipping provider APIs
6. Deploy to production
7. Monitor and optimize

---

**Last Updated**: November 2024
**Version**: 1.0.0
