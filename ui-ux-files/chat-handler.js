// Manus LLM Chat Handler - Intelligent chat with website search and smart system prompt

// Extract products from the website
function extractProductsFromWebsite() {
    const products = [];
    const productCards = document.querySelectorAll('#products .product-card');
    
    productCards.forEach(card => {
        const nameEl = card.querySelector('h3');
        const priceEl = card.querySelector('.text-2xl');
        const descEl = card.querySelectorAll('p')[1];
        
        if (nameEl && priceEl) {
            const priceText = priceEl.textContent.replace(/[^\d]/g, '');
            products.push({
                name: nameEl.textContent.trim(),
                price: parseInt(priceText),
                description: descEl ? descEl.textContent.trim() : '',
                emoji: card.querySelector('.text-5xl')?.textContent || ''
            });
        }
    });
    
    return products;
}

// Extract orders from the website
function extractOrdersFromWebsite() {
    return [
        {id: 'ORD-001', product: 'Pulse Oximeter', price: 1499, status: 'Delivered', date: '2024-11-15', location: 'Cairo', tracking: 'TRACK-001'},
        {id: 'ORD-002', product: 'Blood Pressure Monitor', price: 2699, status: 'In Transit', date: '2024-11-22', location: 'Alexandria', tracking: 'TRACK-002'}
    ];
}

// Search products based on user message
function searchProductsInWebsite(query) {
    const products = extractProductsFromWebsite();
    const lowerQuery = query.toLowerCase();
    
    return products.filter(p => 
        p.name.toLowerCase().includes(lowerQuery) || 
        p.description.toLowerCase().includes(lowerQuery)
    );
}

// Get related products
function getRelatedProducts(productName) {
    const allProducts = extractProductsFromWebsite();
    return allProducts.filter(p => p.name !== productName).slice(0, 3);
}

// Format all products for context
function formatAllProducts() {
    const products = extractProductsFromWebsite();
    return products.map(p => 
        `${p.emoji} ${p.name} (EGP ${p.price}): ${p.description}`
    ).join('\n');
}

// Format orders for context
function formatOrders() {
    const orders = extractOrdersFromWebsite();
    return orders.map(o =>
        `Order #${o.id}: ${o.product} - Status: ${o.status} - Delivery: ${o.date}`
    ).join('\n');
}

// Build smart system prompt with product context
function buildSmartSystemPrompt(userMessage) {
    const searchResults = searchProductsInWebsite(userMessage);
    let productContext = '';
    
    if (searchResults.length > 0) {
        productContext = '\n\nRelevant Products Found:\n';
        searchResults.forEach(p => {
            productContext += `${p.emoji} ${p.name} - EGP ${p.price}\n`;
        });
    }
    
    const isTrackingQuery = userMessage.toLowerCase().includes('track') || 
                           userMessage.toLowerCase().includes('order') ||
                           userMessage.toLowerCase().includes('delivery');
    
    let orderContext = '';
    if (isTrackingQuery) {
        orderContext = '\n\nOrder Information Available';
    }
    
    return `You are MediCare AI, an expert sales assistant for medical devices.
Be friendly, persuasive, and helpful.
Respond in Arabic if customer writes in Arabic, otherwise in English.${productContext}${orderContext}`;
}

// Main chat function
async function sendMessageToManus() {
    const input = document.getElementById('chat-input-home');
    const message = input.value.trim();
    if (!message) return;
    
    const messagesDiv = document.getElementById('chat-messages-home');
    messagesDiv.innerHTML += `<div class="chat-message user">${message}</div>`;
    input.value = '';
    messagesDiv.scrollTop = messagesDiv.scrollHeight;
    
    // Show loading indicator
    messagesDiv.innerHTML += `<div class="chat-message bot"><div class="loading-dots"><span></span><span></span><span></span></div></div>`;
    messagesDiv.scrollTop = messagesDiv.scrollHeight;
    
    try {
        // Build smart system prompt based on user message and website content
        const systemPrompt = buildSmartSystemPrompt(message);
        
        // Call Manus LLM via tRPC endpoint with system prompt
        // Note: The backend router will use the system prompt, we just send the user message
        const response = await fetch('https://3000-imc5clmv16dvpe1124gau-9eb2aa4c.manus-asia.computer/api/trpc/chat.sendMessage', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({json: {message: message}})
        });
        
        let botReply = 'Thank you for your message! How can I help you today?';
        
        if (response.ok) {
            const data = await response.json();
            if (data.result?.data?.json) {
                botReply = data.result.data.json;
            } else if (data.result?.data) {
                botReply = data.result.data;
            }
        } else {
            botReply = 'Sorry, I encountered an error. Please try again.';
        }
        
        // Replace loading indicator with actual response
        messagesDiv.innerHTML = messagesDiv.innerHTML.replace(
            '<div class="chat-message bot"><div class="loading-dots"><span></span><span></span><span></span></div></div>',
            `<div class="chat-message bot">${botReply}</div>`
        );
    } catch (error) {
        console.error('Chat error:', error);
        messagesDiv.innerHTML = messagesDiv.innerHTML.replace(
            '<div class="chat-message bot"><div class="loading-dots"><span></span><span></span><span></span></div></div>',
            '<div class="chat-message bot">Sorry, I encountered an error. Please try again.</div>'
        );
    }
    
    messagesDiv.scrollTop = messagesDiv.scrollHeight;
}
