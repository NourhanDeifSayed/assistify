import React, { useState } from 'react';
import { ArrowRight, MessageCircle, ShoppingCart, Truck, Star } from 'lucide-react';

export default function FunnelVisualization() {
  const [activeStage, setActiveStage] = useState('presale');

  const stages = {
    presale: {
      title: '📋 Pre-Sale Stage',
      color: 'from-blue-500 to-blue-600',
      description: 'Customer discovers products and gets AI recommendations',
      flow: [
        { step: 1, action: 'Customer visits store', icon: '👤' },
        { step: 2, action: 'Browses products', icon: '🔍' },
        { step: 3, action: 'Asks AI questions', icon: '❓' },
        { step: 4, action: 'Gets recommendations', icon: '✨' },
        { step: 5, action: 'Decides to buy', icon: '✅' },
      ],
      aiActions: [
        'Answer FAQs about ingredients, benefits, dosage',
        'Validate medical certifications',
        'Show current offers and bundles',
        'Recommend products based on customer goals',
        'Provide personalized suggestions',
      ],
      systems: ['Manus LLM', 'Product DB', 'Recommendation Engine', 'WhatsApp/Facebook/Instagram'],
    },
    order: {
      title: '🛒 Order Placement Stage',
      color: 'from-purple-500 to-purple-600',
      description: 'Customer places order and completes payment',
      flow: [
        { step: 1, action: 'Add to cart', icon: '🛒' },
        { step: 2, action: 'Go to checkout', icon: '💳' },
        { step: 3, action: 'Enter delivery info', icon: '📍' },
        { step: 4, action: 'Select payment method', icon: '💰' },
        { step: 5, action: 'Confirm order', icon: '✅' },
      ],
      aiActions: [
        'Validate customer data',
        'Process Paymob payment gateway',
        'Generate unique order number',
        'Send order confirmation via email/WhatsApp',
        'Create order in database',
      ],
      systems: ['Paymob Payment', 'Order Management', 'Email Service', 'WhatsApp API', 'Database'],
    },
    shipping: {
      title: '🚚 Shipping & Delivery Stage',
      color: 'from-orange-500 to-orange-600',
      description: 'Order is shipped and customer tracks delivery',
      flow: [
        { step: 1, action: 'Order confirmed', icon: '✅' },
        { step: 2, action: 'Shipped from warehouse', icon: '📦' },
        { step: 3, action: 'In transit', icon: '🚚' },
        { step: 4, action: 'Out for delivery', icon: '🚗' },
        { step: 5, action: 'Delivered', icon: '🏠' },
      ],
      aiActions: [
        'Integrate with DHL/FedEx/UPS APIs',
        'Track shipment in real-time',
        'Detect shipping delays automatically',
        'Send status notifications to customer',
        'Open support ticket if delayed',
      ],
      systems: ['Shipping APIs', 'Tracking System', 'Delay Detection', 'Notification Service', 'Support System'],
    },
    postsale: {
      title: '⭐ Post-Sale Stage',
      color: 'from-pink-500 to-pink-600',
      description: 'Customer receives order and provides feedback',
      flow: [
        { step: 1, action: 'Order delivered', icon: '📦' },
        { step: 2, action: 'Request feedback', icon: '📝' },
        { step: 3, action: 'Rate order 1-5', icon: '⭐' },
        { step: 4, action: 'Analyze sentiment', icon: '🤖' },
        { step: 5, action: 'Send offers', icon: '🎁' },
      ],
      aiActions: [
        'Confirm delivery with customer',
        'Request rating and feedback',
        'Analyze sentiment of feedback',
        'Handle complaints and issues',
        'Send personalized product offers after 2-4 weeks',
      ],
      systems: ['Feedback System', 'Sentiment Analysis', 'Support Tickets', 'Analytics', 'Recommendation Engine'],
    },
  };

  const current = stages[activeStage];

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900 p-8">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="text-center mb-12">
          <h1 className="text-5xl font-bold text-white mb-4">🎯 Customer Funnel Journey</h1>
          <p className="text-xl text-gray-300">Complete flow from discovery to post-sale engagement</p>
        </div>

        {/* Stage Selector */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-12">
          {Object.entries(stages).map(([key, stage]) => (
            <button
              key={key}
              onClick={() => setActiveStage(key)}
              className={`p-4 rounded-lg font-bold text-white transition transform hover:scale-105 ${
                activeStage === key
                  ? `bg-gradient-to-r ${stage.color} shadow-lg`
                  : 'bg-gray-700 hover:bg-gray-600'
              }`}
            >
              {stage.title.split(' ')[0]} {stage.title.split(' ')[1]}
            </button>
          ))}
        </div>

        {/* Main Content */}
        <div className="bg-gray-800 rounded-lg shadow-2xl overflow-hidden">
          {/* Header */}
          <div className={`bg-gradient-to-r ${current.color} p-8 text-white`}>
            <h2 className="text-4xl font-bold mb-2">{current.title}</h2>
            <p className="text-lg opacity-90">{current.description}</p>
          </div>

          {/* Content */}
          <div className="p-8 space-y-8">
            {/* Flow Diagram */}
            <div>
              <h3 className="text-2xl font-bold text-white mb-6">Customer Journey Flow</h3>
              <div className="flex flex-wrap items-center gap-4 mb-8">
                {current.flow.map((item, idx) => (
                  <div key={idx} className="flex items-center gap-4">
                    <div className="bg-gradient-to-r from-blue-500 to-purple-500 rounded-full w-16 h-16 flex items-center justify-center">
                      <div className="text-center">
                        <div className="text-3xl">{item.icon}</div>
                        <div className="text-xs text-white font-bold">Step {item.step}</div>
                      </div>
                    </div>
                    <div className="text-white font-semibold">{item.action}</div>
                    {idx < current.flow.length - 1 && (
                      <ArrowRight className="w-6 h-6 text-gray-400" />
                    )}
                  </div>
                ))}
              </div>
            </div>

            {/* AI Actions */}
            <div>
              <h3 className="text-2xl font-bold text-white mb-6">🤖 What AI Agent Does</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {current.aiActions.map((action, idx) => (
                  <div key={idx} className="bg-gradient-to-r from-blue-900 to-purple-900 p-4 rounded-lg border-l-4 border-blue-400">
                    <div className="flex items-start gap-3">
                      <MessageCircle className="w-6 h-6 text-blue-400 flex-shrink-0 mt-1" />
                      <p className="text-gray-100">{action}</p>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Systems Involved */}
            <div>
              <h3 className="text-2xl font-bold text-white mb-6">🔌 Systems Involved</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {current.systems.map((system, idx) => (
                  <div key={idx} className="bg-gradient-to-r from-green-900 to-teal-900 p-4 rounded-lg border-l-4 border-green-400">
                    <p className="text-gray-100 font-semibold">{system}</p>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>

        {/* Full Funnel Overview */}
        <div className="mt-12 bg-gray-800 rounded-lg p-8">
          <h2 className="text-3xl font-bold text-white mb-8">📊 Complete Funnel Overview</h2>
          <div className="space-y-6">
            {[
              {
                stage: 'Pre-Sale',
                icon: '📋',
                customers: '100%',
                actions: 'Browse, Ask AI, Get Recommendations',
                conversion: '↓ 60% proceed to order',
              },
              {
                stage: 'Order Placement',
                icon: '🛒',
                customers: '60%',
                actions: 'Add to Cart, Checkout, Pay',
                conversion: '↓ 95% complete payment',
              },
              {
                stage: 'Shipping',
                icon: '🚚',
                customers: '57%',
                actions: 'Track Order, Get Updates',
                conversion: '↓ 100% delivered',
              },
              {
                stage: 'Post-Sale',
                icon: '⭐',
                customers: '57%',
                actions: 'Rate, Feedback, Get Offers',
                conversion: '↓ 40% repurchase',
              },
            ].map((item, idx) => (
              <div key={idx} className="flex items-center gap-6">
                <div className="text-4xl">{item.icon}</div>
                <div className="flex-1">
                  <div className="flex justify-between items-center mb-2">
                    <h3 className="text-xl font-bold text-white">{item.stage}</h3>
                    <span className="text-blue-400 font-bold">{item.customers}</span>
                  </div>
                  <p className="text-gray-300 mb-2">{item.actions}</p>
                  <div className="w-full bg-gray-700 rounded-full h-2">
                    <div
                      className="bg-gradient-to-r from-blue-500 to-purple-500 h-2 rounded-full"
                      style={{ width: item.customers }}
                    ></div>
                  </div>
                </div>
                <div className="text-green-400 font-semibold text-right whitespace-nowrap">{item.conversion}</div>
              </div>
            ))}
          </div>
        </div>

        {/* Key Metrics */}
        <div className="mt-12 grid grid-cols-1 md:grid-cols-4 gap-6">
          {[
            { label: 'Avg Order Value', value: '500 EGP', icon: '💰' },
            { label: 'Delivery Time', value: '2-3 Days', icon: '⏱️' },
            { label: 'Customer Satisfaction', value: '4.5/5 ⭐', icon: '😊' },
            { label: 'Repeat Rate', value: '40%', icon: '🔄' },
          ].map((metric, idx) => (
            <div key={idx} className="bg-gradient-to-br from-blue-900 to-purple-900 p-6 rounded-lg text-center">
              <div className="text-4xl mb-2">{metric.icon}</div>
              <p className="text-gray-300 text-sm mb-2">{metric.label}</p>
              <p className="text-3xl font-bold text-white">{metric.value}</p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
