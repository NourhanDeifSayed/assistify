import React, { useState } from 'react';
import { Zap, Brain, MessageSquare, TrendingUp, Shield, Smartphone } from 'lucide-react';

export default function FeaturesShowcase() {
  const [selectedFeature, setSelectedFeature] = useState(0);

  const features = [
    {
      title: '🤖 AI-Powered Recommendations',
      icon: Brain,
      description: 'Intelligent product suggestions based on customer behavior and preferences',
      details: [
        'Analyzes customer browsing history',
        'Learns from purchase patterns',
        'Recommends complementary products',
        'Personalized offers based on interests',
        'Real-time recommendations',
      ],
      color: 'from-blue-500 to-cyan-500',
      technologies: ['Manus LLM', 'Machine Learning', 'Behavioral Analysis'],
    },
    {
      title: '💬 Multi-Channel Communication',
      icon: MessageSquare,
      description: 'Seamless customer support across WhatsApp, Facebook, and Instagram',
      details: [
        'WhatsApp Business API integration',
        'Facebook Messenger support',
        'Instagram Direct Messages',
        'Unified conversation history',
        'Automatic message routing',
      ],
      color: 'from-green-500 to-emerald-500',
      technologies: ['WhatsApp API', 'Facebook Graph', 'Instagram API'],
    },
    {
      title: '📊 Advanced Analytics',
      icon: TrendingUp,
      description: 'Comprehensive insights into sales, customer behavior, and funnel metrics',
      details: [
        'Real-time sales dashboard',
        'Customer behavior tracking',
        'Funnel conversion metrics',
        'Product performance analysis',
        'Revenue forecasting',
      ],
      color: 'from-purple-500 to-pink-500',
      technologies: ['Data Analytics', 'Reporting Engine', 'Visualization'],
    },
    {
      title: '🔒 Enterprise Security',
      icon: Shield,
      description: 'Bank-grade security with encryption and compliance standards',
      details: [
        'JWT token authentication',
        'SSL/TLS encryption',
        'CSRF protection',
        'XSS prevention',
        'Rate limiting & DDoS protection',
      ],
      color: 'from-red-500 to-orange-500',
      technologies: ['OAuth 2.0', 'SSL/TLS', 'Encryption'],
    },
    {
      title: '⚡ Real-Time Tracking',
      icon: Zap,
      description: 'Live order tracking with automatic delay detection and notifications',
      details: [
        'Real-time shipment tracking',
        'Automatic delay detection',
        'Customer notifications',
        'Support ticket creation',
        'Delivery confirmation',
      ],
      color: 'from-yellow-500 to-orange-500',
      technologies: ['DHL API', 'FedEx API', 'UPS API'],
    },
    {
      title: '📱 Mobile-First Design',
      icon: Smartphone,
      description: 'Fully responsive design optimized for all devices',
      details: [
        'React Native mobile app',
        'Responsive web design',
        'Touch-optimized UI',
        'Offline support',
        'App store ready',
      ],
      color: 'from-indigo-500 to-blue-500',
      technologies: ['React Native', 'Tailwind CSS', 'PWA'],
    },
  ];

  const current = features[selectedFeature];
  const CurrentIcon = current.icon;

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-gray-800 to-black p-8">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="text-center mb-12">
          <h1 className="text-5xl font-bold text-white mb-4">✨ Key Features</h1>
          <p className="text-xl text-gray-300">Comprehensive capabilities that power the platform</p>
        </div>

        {/* Feature Selector */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 mb-12">
          {features.map((feature, idx) => (
            <button
              key={idx}
              onClick={() => setSelectedFeature(idx)}
              className={`p-6 rounded-lg transition transform hover:scale-105 ${
                selectedFeature === idx
                  ? `bg-gradient-to-r ${feature.color} text-white shadow-2xl`
                  : 'bg-gray-800 text-gray-300 hover:bg-gray-700'
              }`}
            >
              <div className="text-3xl mb-2">{feature.title.split(' ')[0]}</div>
              <h3 className="font-bold text-lg">{feature.title.split(' ').slice(1).join(' ')}</h3>
            </button>
          ))}
        </div>

        {/* Feature Details */}
        <div className="bg-gray-800 rounded-lg shadow-2xl overflow-hidden">
          {/* Header */}
          <div className={`bg-gradient-to-r ${current.color} p-8 text-white`}>
            <div className="flex items-center gap-4 mb-4">
              <CurrentIcon className="w-12 h-12" />
              <h2 className="text-4xl font-bold">{current.title}</h2>
            </div>
            <p className="text-lg opacity-90">{current.description}</p>
          </div>

          {/* Content */}
          <div className="p-8 grid grid-cols-1 md:grid-cols-2 gap-8">
            {/* Details */}
            <div>
              <h3 className="text-2xl font-bold text-white mb-6">Key Capabilities</h3>
              <div className="space-y-4">
                {current.details.map((detail, idx) => (
                  <div key={idx} className="flex items-start gap-3">
                    <div className="w-2 h-2 bg-blue-400 rounded-full mt-2 flex-shrink-0"></div>
                    <p className="text-gray-300">{detail}</p>
                  </div>
                ))}
              </div>
            </div>

            {/* Technologies */}
            <div>
              <h3 className="text-2xl font-bold text-white mb-6">Technologies Used</h3>
              <div className="space-y-3">
                {current.technologies.map((tech, idx) => (
                  <div
                    key={idx}
                    className="bg-gradient-to-r from-blue-900 to-purple-900 p-4 rounded-lg border-l-4 border-blue-400"
                  >
                    <p className="text-white font-semibold">{tech}</p>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>

        {/* All Features Grid */}
        <div className="mt-12">
          <h2 className="text-3xl font-bold text-white mb-8">🎯 Complete Feature Set</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {[
              { icon: '🛒', title: 'E-Commerce', desc: 'Products, cart, checkout' },
              { icon: '💳', title: 'Paymob Payment', desc: 'Egyptian card payments' },
              { icon: '📦', title: 'Inventory', desc: 'Stock & forecasting' },
              { icon: '📊', title: 'Analytics', desc: 'Sales & metrics' },
              { icon: '🎁', title: 'Offers', desc: 'Promotions & bundles' },
              { icon: '⭐', title: 'Feedback', desc: 'Ratings & reviews' },
              { icon: '🎫', title: 'Support', desc: 'Tickets & escalation' },
              { icon: '🔔', title: 'Notifications', desc: 'Email, SMS, WhatsApp' },
              { icon: '🤖', title: 'AI Chat', desc: 'Intelligent assistant' },
              { icon: '📈', title: 'Churn Prediction', desc: 'Identify at-risk users' },
              { icon: '🎯', title: 'Personalization', desc: 'Tailored experience' },
              { icon: '🔐', title: 'Security', desc: 'Enterprise-grade' },
            ].map((item, idx) => (
              <div key={idx} className="bg-gradient-to-br from-gray-800 to-gray-900 p-6 rounded-lg border border-gray-700 hover:border-blue-400 transition">
                <div className="text-4xl mb-3">{item.icon}</div>
                <h3 className="text-xl font-bold text-white mb-2">{item.title}</h3>
                <p className="text-gray-400">{item.desc}</p>
              </div>
            ))}
          </div>
        </div>

        {/* Performance Metrics */}
        <div className="mt-12 bg-gradient-to-r from-blue-900 to-purple-900 rounded-lg p-8">
          <h2 className="text-3xl font-bold text-white mb-8">⚡ Performance Metrics</h2>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
            {[
              { metric: 'API Response', value: '< 200ms', icon: '🚀' },
              { metric: 'Uptime', value: '99.9%', icon: '✅' },
              { metric: 'Database Queries', value: '< 50ms', icon: '⚡' },
              { metric: 'Page Load', value: '< 2s', icon: '📱' },
            ].map((item, idx) => (
              <div key={idx} className="text-center">
                <div className="text-4xl mb-3">{item.icon}</div>
                <p className="text-gray-300 text-sm mb-2">{item.metric}</p>
                <p className="text-3xl font-bold text-white">{item.value}</p>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
