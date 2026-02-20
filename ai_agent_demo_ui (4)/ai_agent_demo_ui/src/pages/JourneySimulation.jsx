import React, { useState, useEffect } from 'react';
import { ChevronRight, CheckCircle, Clock, AlertCircle, TrendingUp, Users, ShoppingCart, Truck, Star, MessageCircle } from 'lucide-react';

export default function JourneySimulation() {
  const [currentStage, setCurrentStage] = useState(0);
  const [isAutoPlay, setIsAutoPlay] = useState(false);
  const [journeyData, setJourneyData] = useState({
    customerId: 'CUST-2024-001',
    customerName: 'أحمد محمد',
    email: 'ahmed@example.com',
    phone: '+20 100 123 4567',
    channel: 'WhatsApp',
    totalSpent: 0,
    satisfaction: 0,
  });

  const stages = [
    {
      id: 'pre-sale',
      title: '💬 Pre-Sale: Customer Inquiry',
      description: 'Customer discovers product and asks questions',
      duration: '5-10 minutes',
      actions: [
        'Customer sends inquiry via WhatsApp',
        'AI Agent searches product catalog',
        'Sends personalized recommendations',
        'Customer asks about benefits and pricing',
        'AI provides detailed information',
      ],
      metrics: {
        responseTime: '< 2 seconds',
        engagementRate: '95%',
        conversionRate: '45%',
      },
      data: {
        productsViewed: 3,
        questionsAsked: 5,
        recommendationsShown: 2,
      },
    },
    {
      id: 'order',
      title: '🛒 Order Placement',
      description: 'Customer selects product and completes purchase',
      duration: '3-5 minutes',
      actions: [
        'Customer decides to purchase',
        'AI confirms product details',
        'Collects delivery address',
        'Processes payment securely',
        'Order confirmation sent',
      ],
      metrics: {
        conversionRate: '78%',
        avgOrderValue: 'EGP 450',
        paymentSuccess: '99.2%',
      },
      data: {
        itemsOrdered: 2,
        totalAmount: 450,
        paymentMethod: 'Credit Card',
      },
    },
    {
      id: 'shipping',
      title: '🚚 Shipping & Delivery',
      description: 'Order is shipped and delivered with real-time tracking',
      duration: '24-48 hours',
      actions: [
        'Order packed and labeled',
        'Handed to shipping partner',
        'Real-time tracking updates',
        'Delay detection activated',
        'Delivery confirmation',
      ],
      metrics: {
        onTimeDelivery: '96%',
        avgDeliveryTime: '36 hours',
        delayDetection: '100%',
      },
      data: {
        trackingNumber: 'DHL-2024-001',
        carrier: 'DHL',
        estimatedDelivery: 'Tomorrow',
      },
    },
    {
      id: 'post-sale',
      title: '⭐ Post-Sale: Feedback & Offers',
      description: 'Collect feedback and send personalized offers',
      duration: '1-2 days',
      actions: [
        'Delivery confirmation sent',
        'Request product feedback',
        'Customer rates experience',
        'AI analyzes satisfaction',
        'Personalized offers sent',
      ],
      metrics: {
        feedbackRate: '87%',
        avgRating: '4.8/5',
        repeatPurchaseRate: '62%',
      },
      data: {
        rating: 5,
        feedback: 'Excellent product and fast delivery!',
        nextOfferDiscount: '15%',
      },
    },
  ];

  useEffect(() => {
    if (!isAutoPlay) return;

    const timer = setTimeout(() => {
      if (currentStage < stages.length - 1) {
        setCurrentStage(currentStage + 1);
      } else {
        setIsAutoPlay(false);
      }
    }, 5000);

    return () => clearTimeout(timer);
  }, [isAutoPlay, currentStage]);

  const stage = stages[currentStage];
  const progress = ((currentStage + 1) / stages.length) * 100;

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-gray-800 to-black p-4 md:p-8">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-4xl md:text-5xl font-bold text-white mb-2">🎯 Complete Customer Journey</h1>
          <p className="text-lg text-gray-300">End-to-end simulation of the AI Agent Funnel</p>
        </div>

        {/* Customer Info Card */}
        <div className="bg-gradient-to-r from-blue-900 to-purple-900 rounded-lg p-6 md:p-8 mb-8">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 md:gap-6">
            <div>
              <p className="text-gray-300 text-sm mb-1">Customer ID</p>
              <p className="text-white font-bold text-lg">{journeyData.customerId}</p>
            </div>
            <div>
              <p className="text-gray-300 text-sm mb-1">Customer Name</p>
              <p className="text-white font-bold text-lg">{journeyData.customerName}</p>
            </div>
            <div>
              <p className="text-gray-300 text-sm mb-1">Channel</p>
              <p className="text-white font-bold text-lg">💬 {journeyData.channel}</p>
            </div>
            <div>
              <p className="text-gray-300 text-sm mb-1">Total Spent</p>
              <p className="text-green-400 font-bold text-lg">EGP {journeyData.totalSpent}</p>
            </div>
          </div>
        </div>

        {/* Progress Bar */}
        <div className="mb-8">
          <div className="flex justify-between items-center mb-2">
            <p className="text-white font-bold">Journey Progress</p>
            <p className="text-gray-400 text-sm">{currentStage + 1} of {stages.length}</p>
          </div>
          <div className="w-full bg-gray-700 rounded-full h-3 overflow-hidden">
            <div
              className="bg-gradient-to-r from-blue-500 to-purple-500 h-full transition-all duration-500"
              style={{ width: `${progress}%` }}
            ></div>
          </div>
        </div>

        {/* Main Content */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 md:gap-8 mb-8">
          {/* Stage Timeline */}
          <div className="lg:col-span-2 bg-gray-800 rounded-lg p-6 md:p-8">
            <h2 className="text-2xl md:text-3xl font-bold text-white mb-6">{stage.title}</h2>
            <p className="text-gray-300 mb-6">{stage.description}</p>

            {/* Actions */}
            <div className="space-y-3 mb-8">
              <h3 className="text-lg font-bold text-white">📋 Actions in this stage:</h3>
              {stage.actions.map((action, idx) => (
                <div key={idx} className="flex items-start gap-3 p-3 bg-gray-700 rounded-lg">
                  <CheckCircle className="w-5 h-5 text-green-400 flex-shrink-0 mt-1" />
                  <span className="text-gray-200">{action}</span>
                </div>
              ))}
            </div>

            {/* Stage Data */}
            <div className="bg-gray-700 rounded-lg p-4 md:p-6">
              <h3 className="text-lg font-bold text-white mb-4">📊 Stage Data:</h3>
              <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
                {Object.entries(stage.data).map(([key, value]) => (
                  <div key={key} className="bg-gray-800 p-3 rounded-lg">
                    <p className="text-gray-400 text-xs uppercase">{key.replace(/([A-Z])/g, ' $1')}</p>
                    <p className="text-white font-bold text-lg">{value}</p>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Metrics & Info */}
          <div className="space-y-4">
            {/* Duration */}
            <div className="bg-gradient-to-br from-orange-900 to-orange-800 rounded-lg p-6">
              <div className="flex items-center gap-2 mb-2">
                <Clock className="w-5 h-5 text-orange-400" />
                <h3 className="font-bold text-white">Duration</h3>
              </div>
              <p className="text-2xl font-bold text-orange-300">{stage.duration}</p>
            </div>

            {/* Metrics */}
            <div className="bg-gradient-to-br from-green-900 to-green-800 rounded-lg p-6">
              <h3 className="font-bold text-white mb-4">📈 Key Metrics</h3>
              <div className="space-y-3">
                {Object.entries(stage.metrics).map(([key, value]) => (
                  <div key={key} className="flex justify-between items-center">
                    <p className="text-gray-200 text-sm">{key.replace(/([A-Z])/g, ' $1')}</p>
                    <p className="text-green-300 font-bold">{value}</p>
                  </div>
                ))}
              </div>
            </div>

            {/* AI Capabilities */}
            <div className="bg-gradient-to-br from-purple-900 to-purple-800 rounded-lg p-6">
              <h3 className="font-bold text-white mb-4">🤖 AI Capabilities</h3>
              <div className="space-y-2 text-sm text-gray-200">
                <div className="flex items-center gap-2">
                  <span className="text-purple-400">✓</span>
                  <span>Natural language understanding</span>
                </div>
                <div className="flex items-center gap-2">
                  <span className="text-purple-400">✓</span>
                  <span>Product recommendations</span>
                </div>
                <div className="flex items-center gap-2">
                  <span className="text-purple-400">✓</span>
                  <span>Real-time tracking</span>
                </div>
                <div className="flex items-center gap-2">
                  <span className="text-purple-400">✓</span>
                  <span>Sentiment analysis</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Stage Navigation */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3 md:gap-4 mb-8">
          {stages.map((s, idx) => (
            <button
              key={idx}
              onClick={() => {
                setCurrentStage(idx);
                setIsAutoPlay(false);
              }}
              className={`p-3 md:p-4 rounded-lg transition transform hover:scale-105 ${
                currentStage === idx
                  ? 'bg-gradient-to-r from-blue-500 to-purple-500 text-white shadow-lg'
                  : idx < currentStage
                  ? 'bg-green-600 text-white'
                  : 'bg-gray-700 text-gray-300'
              }`}
            >
              <div className="text-2xl mb-2">{s.title.split(':')[0]}</div>
              <div className="text-xs font-bold">{s.id}</div>
            </button>
          ))}
        </div>

        {/* Controls */}
        <div className="flex flex-col md:flex-row gap-4 md:gap-6 justify-center mb-8">
          <button
            onClick={() => setCurrentStage(Math.max(0, currentStage - 1))}
            disabled={currentStage === 0}
            className="px-6 md:px-8 py-3 bg-gray-700 text-white rounded-lg hover:bg-gray-600 transition disabled:opacity-50 disabled:cursor-not-allowed"
          >
            ← Previous
          </button>
          <button
            onClick={() => setIsAutoPlay(!isAutoPlay)}
            className={`px-6 md:px-8 py-3 rounded-lg transition font-bold ${
              isAutoPlay
                ? 'bg-red-600 hover:bg-red-700 text-white'
                : 'bg-green-600 hover:bg-green-700 text-white'
            }`}
          >
            {isAutoPlay ? '⏸ Pause' : '▶ Auto Play'}
          </button>
          <button
            onClick={() => setCurrentStage(Math.min(stages.length - 1, currentStage + 1))}
            disabled={currentStage === stages.length - 1}
            className="px-6 md:px-8 py-3 bg-gray-700 text-white rounded-lg hover:bg-gray-600 transition disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2 justify-center"
          >
            Next <ChevronRight className="w-4 h-4" />
          </button>
        </div>

        {/* Summary Stats */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 md:gap-6">
          {[
            { icon: Users, label: 'Total Customers', value: '15,234', color: 'from-blue-500 to-blue-600' },
            { icon: ShoppingCart, label: 'Total Orders', value: '8,456', color: 'from-green-500 to-green-600' },
            { icon: TrendingUp, label: 'Conversion Rate', value: '34.2%', color: 'from-purple-500 to-purple-600' },
            { icon: Star, label: 'Avg Rating', value: '4.7/5', color: 'from-yellow-500 to-yellow-600' },
          ].map((stat, idx) => {
            const Icon = stat.icon;
            return (
              <div key={idx} className={`bg-gradient-to-br ${stat.color} rounded-lg p-6 text-white`}>
                <Icon className="w-8 h-8 mb-2 opacity-80" />
                <p className="text-gray-200 text-sm mb-1">{stat.label}</p>
                <p className="text-2xl md:text-3xl font-bold">{stat.value}</p>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
