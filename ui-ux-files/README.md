# MediCare AI - Manus LLM Chat Integration

## Files Included

1. **complete-platform.html** - Main UI/UX with chat widget
2. **chat-handler.js** - Chat handler that connects to Manus LLM
3. **routers.ts** - Backend router with Manus LLM integration
4. **chatData.ts** - Product and order data
5. **llm.ts** - LLM integration helper

## Setup Instructions

### For Local Server

1. Copy `complete-platform.html` and `chat-handler.js` to your public/static folder
2. Update the API URL in `chat-handler.js`:
   ```javascript
   // Change from:
   https://3000-imc5clmv16dvpe1124gau-9eb2aa4c.manus-asia.computer/api/trpc/chat.sendMessage
   
   // To your local server:
   http://localhost:3000/api/trpc/chat.sendMessage
   ```

3. Copy the backend files (routers.ts, chatData.ts, llm.ts) to your server

4. Make sure your server has CORS enabled:
   ```javascript
   app.use((req, res, next) => {
     res.header('Access-Control-Allow-Origin', '*');
     res.header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');
     res.header('Access-Control-Allow-Headers', 'Content-Type');
     next();
   });
   ```

5. Access the UI at: `http://localhost:8080/complete-platform.html`

## Features

✅ Floating chat widget with Manus LLM
✅ Product search and recommendations
✅ Order tracking support
✅ Multi-language support (Arabic/English)
✅ Intelligent responses from Manus LLM
✅ Shopping cart integration
✅ Payment processing
✅ Order confirmation and tracking

## Chat Features

The chat widget now:
- Searches the website for relevant products
- Sends context to Manus LLM
- Receives intelligent, persuasive responses
- Suggests complementary products
- Helps with order tracking
- Supports both Arabic and English

## Customization

To customize the chat:
1. Edit the system prompt in `chat-handler.js` (buildSmartSystemPrompt function)
2. Update product data in `chatData.ts`
3. Modify the chat widget styling in `complete-platform.html`

## Support

For issues or questions, contact support@medicareai.com
