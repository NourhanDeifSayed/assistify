import React, { useState, useEffect } from 'react';
import { MessageCircle, ShoppingCart, Truck, Star, CheckCircle, AlertCircle, Send, Phone, MessageSquare, Instagram, Facebook } from 'lucide-react';

export default function InteractiveDemo() {
  const [stage, setStage] = useState(0);
  const [channel, setChannel] = useState('whatsapp');
  const [messages, setMessages] = useState([]);
  const [isTyping, setIsTyping] = useState(false);
  const [selectedProduct, setSelectedProduct] = useState(null);
  const [cartItems, setCartItems] = useState([]);
  const [orderStatus, setOrderStatus] = useState(null);
  const [shopifyIntegration, setShopifyIntegration] = useState(false);
  const [inputValue, setInputValue] = useState('');

  const stages = [
    {
      title: '💬 Pre-Sale: Customer Inquiry',
      description: 'Customer asks questions about products',
      icon: MessageCircle,
      color: 'from-blue-500 to-cyan-500',
    },
    {
      title: '🛒 Order Placement',
      description: 'Customer selects product and checks out',
      icon: ShoppingCart,
      color: 'from-green-500 to-emerald-500',
    },
    {
      title: '🚚 Shipping & Delivery',
      description: 'Order is shipped and tracked',
      icon: Truck,
      color: 'from-orange-500 to-yellow-500',
    },
    {
      title: '⭐ Post-Sale: Feedback',
      description: 'Customer rates and receives offers',
      icon: Star,
      color: 'from-purple-500 to-pink-500',
    },
  ];

  const channels = [
    { id: 'whatsapp', name: 'WhatsApp', icon: Phone, color: 'from-green-400 to-green-600', badge: '💬' },
    { id: 'instagram', name: 'Instagram DM', icon: Instagram, color: 'from-pink-400 to-purple-600', badge: '📸' },
    { id: 'facebook', name: 'Facebook', icon: Facebook, color: 'from-blue-400 to-blue-600', badge: '👥' },
  ];

  const shopifyProducts = [
    {
      id: 1,
      name: 'Vitamin C Supplement',
      price: 150,
      shopifyId: 'gid://shopify/Product/1',
      image: '💊',
      description: 'Boost immunity with premium Vitamin C',
      benefits: ['Immune boost', 'Antioxidant', 'Energy'],
      stock: 45,
    },
    {
      id: 2,
      name: 'Omega-3 Fish Oil',
      price: 200,
      shopifyId: 'gid://shopify/Product/2',
      image: '🐟',
      description: 'Heart and brain health support',
      benefits: ['Heart health', 'Brain function', 'Anti-inflammatory'],
      stock: 32,
    },
    {
      id: 3,
      name: 'Multivitamin Complex',
      price: 250,
      shopifyId: 'gid://shopify/Product/3',
      image: '🌈',
      description: 'Complete daily nutrition',
      benefits: ['Complete nutrition', 'Energy', 'Overall wellness'],
      stock: 28,
    },
  ];

  const channelResponses = {
    whatsapp: {
      greeting: "مرحباً! 👋 أهلاً وسهلاً في متجرنا الطبي. كيف يمكنني مساعدتك؟",
      inquiry: "سؤال رائع! لدينا عدة منتجات قد تساعدك. دعني أعرض عليك أفضل التوصيات.",
      recommendation: "بناءً على احتياجاتك، أوصيك بمكمل فيتامين C. إنه منتج عالي الجودة وممتاز للمناعة!",
      orderConfirm: "ممتاز! تم تأكيد طلبك. رقم الطلب: #ORD-2024-001 سيتم الشحن خلال 24 ساعة.",
      shipping: "طلبك في الطريق! 📦 الحالة الحالية: قيد الشحن. التسليم المتوقع: غداً",
      delivery: "رائع! 🎉 تم تسليم طلبك. نود سماع رأيك!",
    },
    instagram: {
      greeting: "Hey! 👋 Welcome to our medical store! How can we help? 💊",
      inquiry: "Great question! We have some amazing products. Let me show you our top picks! 🌟",
      recommendation: "Based on your needs, I recommend our Vitamin C Supplement! It's perfect for immunity! 💪",
      orderConfirm: "Perfect! Your order is confirmed. Order #ORD-2024-001 will ship within 24 hours! 📦",
      shipping: "Your order is on the way! 🚚 Status: In Transit. Expected delivery: Tomorrow!",
      delivery: "Amazing! 🎉 Your order has been delivered! Please share your feedback! ⭐",
    },
    facebook: {
      greeting: "Hello! 👋 Welcome to MediStore. How can we assist you today?",
      inquiry: "That's a great question! We have several products that might help. Let me show you our recommendations.",
      recommendation: "I recommend our Vitamin C Supplement. It's highly rated and perfect for boosting immunity!",
      orderConfirm: "Great! Your order has been confirmed. Order #ORD-2024-001 will be shipped within 24 hours.",
      shipping: "Your order is on its way! 📦 Current status: In Transit. Expected delivery: Tomorrow",
      delivery: "Excellent! 🎉 Your order has been delivered. We'd love to hear your feedback!",
    },
  };

  const addMessage = (text, sender = 'ai') => {
    setMessages((prev) => [...prev, { text, sender, timestamp: new Date(), channel }]);
  };

  const simulateAIResponse = (response, delay = 1500) => {
    setIsTyping(true);
    setTimeout(() => {
      addMessage(response, 'ai');
      setIsTyping(false);
    }, delay);
  };

  const handleStageStart = (stageIndex) => {
    setMessages([]);
    setStage(stageIndex);

    const responses = channelResponses[channel];

    switch (stageIndex) {
      case 0:
        const inquiry = channel === 'whatsapp' ? "أبحث عن شيء لتقوية المناعة" : "I'm looking for something to boost my immunity";
        addMessage(inquiry, 'user');
        setTimeout(() => {
          simulateAIResponse(responses.greeting);
        }, 500);
        break;
      case 1:
        const order = channel === 'whatsapp' ? "أريد طلب مكمل فيتامين C" : "I'd like to order the Vitamin C Supplement";
        addMessage(order, 'user');
        setSelectedProduct(shopifyProducts[0]);
        setShopifyIntegration(true);
        setTimeout(() => {
          simulateAIResponse(responses.orderConfirm);
        }, 500);
        setCartItems([shopifyProducts[0]]);
        break;
      case 2:
        const track = channel === 'whatsapp' ? "أين طلبي؟" : "Where is my order?";
        addMessage(track, 'user');
        setOrderStatus('in-transit');
        setTimeout(() => {
          simulateAIResponse(responses.shipping);
        }, 500);
        break;
      case 3:
        const feedback = channel === 'whatsapp' ? "استقبلت طلبي، رائع جداً!" : "I received my order, it's amazing!";
        addMessage(feedback, 'user');
        setOrderStatus('delivered');
        setTimeout(() => {
          simulateAIResponse(responses.delivery);
        }, 500);
        break;
      default:
        break;
    }
  };

  const handleUserMessage = (text) => {
    if (!text.trim()) return;
    
    addMessage(text, 'user');
    setInputValue('');
    
    const responses = channelResponses[channel];

    switch (stage) {
      case 0:
        if (text.toLowerCase().includes('yes') || text.toLowerCase().includes('show') || text.includes('نعم')) {
          simulateAIResponse(responses.recommendation);
        } else {
          simulateAIResponse("I can help you find the perfect product for your needs. What are your main health concerns?");
        }
        break;
      case 1:
        if (text.toLowerCase().includes('yes') || text.toLowerCase().includes('checkout') || text.includes('نعم')) {
          simulateAIResponse("Great! Your order has been placed successfully. Order #ORD-2024-001");
          setOrderStatus('confirmed');
        }
        break;
      case 2:
        if (text.toLowerCase().includes('track') || text.toLowerCase().includes('status') || text.includes('تتبع')) {
          simulateAIResponse(responses.shipping);
        }
        break;
      case 3:
        if (text.toLowerCase().includes('rate') || text.toLowerCase().includes('feedback') || text.includes('تقييم')) {
          simulateAIResponse(responses.delivery);
        }
        break;
      default:
        break;
    }
  };

  const CurrentIcon = stages[stage].icon;
  const currentChannel = channels.find(c => c.id === channel);
  const ChannelIcon = currentChannel.icon;

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-gray-800 to-black p-4 md:p-8">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-4xl md:text-5xl font-bold text-white mb-2">🎬 Complete AI Agent Demo</h1>
          <p className="text-lg md:text-xl text-gray-300">Multi-Channel Communication + Shopify Integration</p>
        </div>

        {/* Channel Selector */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
          {channels.map((ch) => {
            const Icon = ch.icon;
            return (
              <button
                key={ch.id}
                onClick={() => {
                  setChannel(ch.id);
                  setMessages([]);
                }}
                className={`p-4 md:p-6 rounded-lg transition transform hover:scale-105 ${
                  channel === ch.id
                    ? `bg-gradient-to-r ${ch.color} text-white shadow-2xl`
                    : 'bg-gray-800 text-gray-300 hover:bg-gray-700'
                }`}
              >
                <Icon className="w-6 h-6 md:w-8 md:h-8 mb-2 mx-auto" />
                <h3 className="font-bold text-sm md:text-base">{ch.name}</h3>
              </button>
            );
          })}
        </div>

        {/* Stage Selector */}
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-2 md:gap-4 mb-8">
          {stages.map((s, idx) => {
            const Icon = s.icon;
            return (
              <button
                key={idx}
                onClick={() => handleStageStart(idx)}
                className={`p-3 md:p-6 rounded-lg transition transform hover:scale-105 text-xs md:text-sm ${
                  stage === idx
                    ? `bg-gradient-to-r ${s.color} text-white shadow-2xl`
                    : 'bg-gray-800 text-gray-300 hover:bg-gray-700'
                }`}
              >
                <Icon className="w-5 h-5 md:w-8 md:h-8 mb-1 md:mb-2 mx-auto" />
                <h3 className="font-bold">{s.title.split(':')[0]}</h3>
              </button>
            );
          })}
        </div>

        {/* Main Demo Area */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 md:gap-8">
          {/* Chat Area */}
          <div className="lg:col-span-2 bg-gray-800 rounded-lg shadow-2xl overflow-hidden flex flex-col h-[500px] md:h-[600px]">
            {/* Header */}
            <div className={`bg-gradient-to-r ${stages[stage].color} p-4 md:p-6 text-white`}>
              <div className="flex items-center gap-3">
                <CurrentIcon className="w-6 h-6 md:w-8 md:h-8" />
                <div className="flex-1">
                  <h2 className="text-lg md:text-2xl font-bold">{stages[stage].title}</h2>
                  <div className="flex items-center gap-2 text-xs md:text-sm opacity-90">
                    <ChannelIcon className="w-4 h-4" />
                    <span>via {currentChannel.name}</span>
                  </div>
                </div>
              </div>
            </div>

            {/* Messages */}
            <div className="flex-1 overflow-y-auto p-4 md:p-6 space-y-3 md:space-y-4">
              {messages.map((msg, idx) => (
                <div
                  key={idx}
                  className={`flex ${msg.sender === 'user' ? 'justify-end' : 'justify-start'}`}
                >
                  <div
                    className={`max-w-xs md:max-w-sm px-3 md:px-4 py-2 md:py-3 rounded-lg text-sm md:text-base ${
                      msg.sender === 'user'
                        ? 'bg-blue-600 text-white'
                        : 'bg-gray-700 text-gray-100'
                    }`}
                  >
                    {msg.text}
                  </div>
                </div>
              ))}
              {isTyping && (
                <div className="flex justify-start">
                  <div className="bg-gray-700 text-gray-100 px-4 py-2 rounded-lg">
                    <div className="flex gap-1">
                      <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                      <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                      <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.4s' }}></div>
                    </div>
                  </div>
                </div>
              )}
            </div>

            {/* Input Area */}
            <div className="border-t border-gray-700 p-3 md:p-4 bg-gray-900">
              <div className="flex gap-2">
                <input
                  type="text"
                  placeholder="Type message..."
                  value={inputValue}
                  onChange={(e) => setInputValue(e.target.value)}
                  className="flex-1 bg-gray-700 text-white px-3 md:px-4 py-2 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm md:text-base"
                  onKeyPress={(e) => {
                    if (e.key === 'Enter') {
                      handleUserMessage(inputValue);
                    }
                  }}
                />
                <button
                  onClick={() => handleUserMessage(inputValue)}
                  className="bg-blue-600 text-white px-4 md:px-6 py-2 rounded-lg hover:bg-blue-700 transition"
                >
                  <Send className="w-4 h-4 md:w-5 md:h-5" />
                </button>
              </div>
            </div>
          </div>

          {/* Info Panel */}
          <div className="space-y-4">
            {/* Shopify Integration */}
            {shopifyIntegration && selectedProduct && (
              <div className="bg-gradient-to-br from-green-900 to-green-800 rounded-lg p-4 md:p-6 border-2 border-green-500">
                <h3 className="text-lg md:text-xl font-bold text-white mb-4">🛍️ Shopify Integration</h3>
                <div className="space-y-3">
                  <div className="bg-green-800 p-3 rounded-lg">
                    <p className="text-xs md:text-sm text-gray-200 mb-2">
                      <strong>Shopify ID:</strong> {selectedProduct.shopifyId}
                    </p>
                    <p className="text-2xl md:text-3xl mb-2">{selectedProduct.image}</p>
                    <h4 className="font-bold text-white mb-1">{selectedProduct.name}</h4>
                    <p className="text-green-300 font-bold mb-2">EGP {selectedProduct.price}</p>
                    <p className="text-xs md:text-sm text-gray-200 mb-2">Stock: {selectedProduct.stock} units</p>
                    <div className="bg-green-700 p-2 rounded text-xs text-gray-100">
                      ✅ Synced with Shopify Store
                    </div>
                  </div>
                </div>
              </div>
            )}

            {/* Order Status */}
            {stage >= 2 && orderStatus && (
              <div className="bg-gray-800 rounded-lg p-4 md:p-6">
                <h3 className="text-lg md:text-xl font-bold text-white mb-4">📦 Order Status</h3>
                <div className="space-y-3">
                  <div className="flex items-center gap-3">
                    <CheckCircle className="w-5 h-5 md:w-6 md:h-6 text-green-400" />
                    <span className="text-sm md:text-base text-gray-300">Order Confirmed</span>
                  </div>
                  <div className={`flex items-center gap-3 ${orderStatus === 'in-transit' || orderStatus === 'delivered' ? 'text-gray-300' : 'text-gray-500'}`}>
                    <Truck className="w-5 h-5 md:w-6 md:h-6" />
                    <span className="text-sm md:text-base">In Transit</span>
                  </div>
                  <div className={`flex items-center gap-3 ${orderStatus === 'delivered' ? 'text-green-400' : 'text-gray-500'}`}>
                    <CheckCircle className="w-5 h-5 md:w-6 md:h-6" />
                    <span className="text-sm md:text-base">Delivered</span>
                  </div>
                </div>
              </div>
            )}

            {/* AI Features */}
            <div className="bg-gradient-to-br from-blue-900 to-purple-900 rounded-lg p-4 md:p-6">
              <h3 className="text-lg md:text-xl font-bold text-white mb-4">🤖 AI Capabilities</h3>
              <div className="space-y-2 text-xs md:text-sm text-gray-200">
                <div className="flex items-start gap-2">
                  <span className="text-blue-400">✓</span>
                  <span>Multi-channel support</span>
                </div>
                <div className="flex items-start gap-2">
                  <span className="text-blue-400">✓</span>
                  <span>Shopify integration</span>
                </div>
                <div className="flex items-start gap-2">
                  <span className="text-blue-400">✓</span>
                  <span>Real-time tracking</span>
                </div>
                <div className="flex items-start gap-2">
                  <span className="text-blue-400">✓</span>
                  <span>Auto recommendations</span>
                </div>
                <div className="flex items-start gap-2">
                  <span className="text-blue-400">✓</span>
                  <span>Feedback collection</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Quick Actions */}
        <div className="mt-8 md:mt-12 bg-gray-800 rounded-lg p-4 md:p-6">
          <h3 className="text-xl md:text-2xl font-bold text-white mb-4 md:mb-6">🎯 Quick Actions</h3>
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-2 md:gap-4">
            {[
              { label: 'Ask Question', action: () => handleUserMessage(channel === 'whatsapp' ? 'ما هي التوصية؟' : 'What do you recommend?') },
              { label: 'Place Order', action: () => handleUserMessage(channel === 'whatsapp' ? 'أريد طلب هذا' : 'I want to order this') },
              { label: 'Track Order', action: () => handleUserMessage(channel === 'whatsapp' ? 'أين طلبي؟' : 'Where is my order?') },
              { label: 'Give Feedback', action: () => handleUserMessage(channel === 'whatsapp' ? 'منتج رائع! 5 نجوم' : 'Great product! 5 stars') },
            ].map((action, idx) => (
              <button
                key={idx}
                onClick={action.action}
                className="bg-gradient-to-r from-blue-600 to-purple-600 text-white px-3 md:px-6 py-2 md:py-3 rounded-lg hover:from-blue-700 hover:to-purple-700 transition font-semibold text-xs md:text-base"
              >
                {action.label}
              </button>
            ))}
          </div>
        </div>

        {/* Integration Info */}
        <div className="mt-8 md:mt-12 grid grid-cols-1 md:grid-cols-3 gap-4 md:gap-6">
          <div className="bg-gradient-to-br from-green-900 to-green-800 rounded-lg p-4 md:p-6 border-2 border-green-500">
            <h4 className="text-lg font-bold text-white mb-2">✅ WhatsApp Integration</h4>
            <p className="text-sm text-gray-200">Direct messaging via WhatsApp Business API with real-time notifications</p>
          </div>
          <div className="bg-gradient-to-br from-pink-900 to-purple-900 rounded-lg p-4 md:p-6 border-2 border-pink-500">
            <h4 className="text-lg font-bold text-white mb-2">📸 Instagram Integration</h4>
            <p className="text-sm text-gray-200">Instagram DM support with visual product catalog and quick replies</p>
          </div>
          <div className="bg-gradient-to-br from-blue-900 to-blue-800 rounded-lg p-4 md:p-6 border-2 border-blue-500">
            <h4 className="text-lg font-bold text-white mb-2">👥 Facebook Integration</h4>
            <p className="text-sm text-gray-200">Facebook Messenger with customer support and order updates</p>
          </div>
        </div>
      </div>
    </div>
  );
}
