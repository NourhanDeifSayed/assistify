import React, { useState } from 'react';
import { ChevronDown, ChevronUp, Database, Server, Smartphone, BarChart3, Zap, Shield } from 'lucide-react';

export default function SystemShowcase() {
  const [expandedSection, setExpandedSection] = useState('architecture');

  const toggleSection = (section) => {
    setExpandedSection(expandedSection === section ? null : section);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-purple-50 to-pink-50 p-8">
      {/* Header */}
      <div className="max-w-7xl mx-auto mb-12">
        <h1 className="text-5xl font-bold text-gray-900 mb-4">
          🚀 AI Agent E-Commerce Platform
        </h1>
        <p className="text-xl text-gray-600">
          Complete funnel system with AI-powered recommendations, multi-channel support, and advanced analytics
        </p>
      </div>

      {/* System Architecture */}
      <div className="max-w-7xl mx-auto mb-8">
        <div className="bg-white rounded-lg shadow-lg overflow-hidden">
          <button
            onClick={() => toggleSection('architecture')}
            className="w-full p-6 bg-gradient-to-r from-blue-600 to-blue-700 text-white flex items-center justify-between hover:from-blue-700 hover:to-blue-800 transition"
          >
            <div className="flex items-center gap-3">
              <Server className="w-6 h-6" />
              <h2 className="text-2xl font-bold">System Architecture</h2>
            </div>
            {expandedSection === 'architecture' ? <ChevronUp /> : <ChevronDown />}
          </button>

          {expandedSection === 'architecture' && (
            <div className="p-8 bg-gray-50">
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
                {/* Frontend */}
                <div className="bg-white p-6 rounded-lg border-2 border-blue-200">
                  <div className="flex items-center gap-2 mb-4">
                    <Smartphone className="w-6 h-6 text-blue-600" />
                    <h3 className="text-xl font-bold text-gray-900">Frontend</h3>
                  </div>
                  <ul className="space-y-2 text-gray-700">
                    <li>✅ React 19 + Vite</li>
                    <li>✅ Tailwind CSS</li>
                    <li>✅ Zustand State Management</li>
                    <li>✅ 10 Complete Pages</li>
                    <li>✅ Multi-language (AR/EN)</li>
                    <li>✅ Responsive Design</li>
                  </ul>
                </div>

                {/* Backend */}
                <div className="bg-white p-6 rounded-lg border-2 border-purple-200">
                  <div className="flex items-center gap-2 mb-4">
                    <Server className="w-6 h-6 text-purple-600" />
                    <h3 className="text-xl font-bold text-gray-900">Backend</h3>
                  </div>
                  <ul className="space-y-2 text-gray-700">
                    <li>✅ Django 4.2</li>
                    <li>✅ Django REST Framework</li>
                    <li>✅ 50+ API Endpoints</li>
                    <li>✅ Celery Task Queue</li>
                    <li>✅ JWT Authentication</li>
                    <li>✅ Paymob Integration</li>
                  </ul>
                </div>

                {/* Database */}
                <div className="bg-white p-6 rounded-lg border-2 border-pink-200">
                  <div className="flex items-center gap-2 mb-4">
                    <Database className="w-6 h-6 text-pink-600" />
                    <h3 className="text-xl font-bold text-gray-900">Database</h3>
                  </div>
                  <ul className="space-y-2 text-gray-700">
                    <li>✅ MySQL 8.0</li>
                    <li>✅ 13 Models</li>
                    <li>✅ Redis Cache</li>
                    <li>✅ Optimized Queries</li>
                    <li>✅ Automated Backups</li>
                    <li>✅ Full Indexing</li>
                  </ul>
                </div>
              </div>

              {/* Integration Services */}
              <div className="bg-gradient-to-r from-blue-100 to-purple-100 p-6 rounded-lg">
                <h3 className="text-xl font-bold text-gray-900 mb-4">🔌 Integration Services</h3>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                  {[
                    'Manus LLM',
                    'Paymob Payment',
                    'WhatsApp API',
                    'Facebook Messenger',
                    'Instagram DM',
                    'Email Service',
                    'SMS/Twilio',
                    'Shipping APIs'
                  ].map((service, idx) => (
                    <div key={idx} className="bg-white p-4 rounded-lg text-center font-semibold text-gray-700">
                      {service}
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Funnel Visualization */}
      <div className="max-w-7xl mx-auto mb-8">
        <div className="bg-white rounded-lg shadow-lg overflow-hidden">
          <button
            onClick={() => toggleSection('funnel')}
            className="w-full p-6 bg-gradient-to-r from-green-600 to-green-700 text-white flex items-center justify-between hover:from-green-700 hover:to-green-800 transition"
          >
            <div className="flex items-center gap-3">
              <Zap className="w-6 h-6" />
              <h2 className="text-2xl font-bold">Customer Funnel Journey</h2>
            </div>
            {expandedSection === 'funnel' ? <ChevronUp /> : <ChevronDown />}
          </button>

          {expandedSection === 'funnel' && (
            <div className="p-8 bg-gray-50">
              <div className="space-y-6">
                {/* Stage 1: Pre-Sale */}
                <div className="bg-gradient-to-r from-blue-50 to-blue-100 p-6 rounded-lg border-l-4 border-blue-600">
                  <h3 className="text-2xl font-bold text-blue-900 mb-4">📋 Stage 1: Pre-Sale</h3>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <h4 className="font-semibold text-gray-800 mb-2">Customer Actions:</h4>
                      <ul className="space-y-1 text-gray-700">
                        <li>✓ Browse products</li>
                        <li>✓ Ask AI questions</li>
                        <li>✓ View recommendations</li>
                        <li>✓ Check certifications</li>
                      </ul>
                    </div>
                    <div>
                      <h4 className="font-semibold text-gray-800 mb-2">AI Agent Does:</h4>
                      <ul className="space-y-1 text-gray-700">
                        <li>✓ Answers FAQs</li>
                        <li>✓ Recommends products</li>
                        <li>✓ Shows offers</li>
                        <li>✓ Validates medical info</li>
                      </ul>
                    </div>
                  </div>
                </div>

                {/* Stage 2: Order Placement */}
                <div className="bg-gradient-to-r from-purple-50 to-purple-100 p-6 rounded-lg border-l-4 border-purple-600">
                  <h3 className="text-2xl font-bold text-purple-900 mb-4">🛒 Stage 2: Order Placement</h3>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <h4 className="font-semibold text-gray-800 mb-2">Customer Actions:</h4>
                      <ul className="space-y-1 text-gray-700">
                        <li>✓ Enter delivery info</li>
                        <li>✓ Select payment method</li>
                        <li>✓ Enter card details</li>
                        <li>✓ Confirm order</li>
                      </ul>
                    </div>
                    <div>
                      <h4 className="font-semibold text-gray-800 mb-2">System Does:</h4>
                      <ul className="space-y-1 text-gray-700">
                        <li>✓ Validates data</li>
                        <li>✓ Processes Paymob payment</li>
                        <li>✓ Generates order number</li>
                        <li>✓ Sends confirmation</li>
                      </ul>
                    </div>
                  </div>
                </div>

                {/* Stage 3: Shipping & Delivery */}
                <div className="bg-gradient-to-r from-orange-50 to-orange-100 p-6 rounded-lg border-l-4 border-orange-600">
                  <h3 className="text-2xl font-bold text-orange-900 mb-4">🚚 Stage 3: Shipping & Delivery</h3>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <h4 className="font-semibold text-gray-800 mb-2">Customer Actions:</h4>
                      <ul className="space-y-1 text-gray-700">
                        <li>✓ Tracks order</li>
                        <li>✓ Receives updates</li>
                        <li>✓ Gets notifications</li>
                        <li>✓ Receives package</li>
                      </ul>
                    </div>
                    <div>
                      <h4 className="font-semibold text-gray-800 mb-2">System Does:</h4>
                      <ul className="space-y-1 text-gray-700">
                        <li>✓ Tracks shipment</li>
                        <li>✓ Detects delays</li>
                        <li>✓ Sends notifications</li>
                        <li>✓ Confirms delivery</li>
                      </ul>
                    </div>
                  </div>
                </div>

                {/* Stage 4: Post-Sale */}
                <div className="bg-gradient-to-r from-pink-50 to-pink-100 p-6 rounded-lg border-l-4 border-pink-600">
                  <h3 className="text-2xl font-bold text-pink-900 mb-4">⭐ Stage 4: Post-Sale</h3>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <h4 className="font-semibold text-gray-800 mb-2">Customer Actions:</h4>
                      <ul className="space-y-1 text-gray-700">
                        <li>✓ Rates order (1-5)</li>
                        <li>✓ Leaves feedback</li>
                        <li>✓ Reports issues</li>
                        <li>✓ Receives offers</li>
                      </ul>
                    </div>
                    <div>
                      <h4 className="font-semibold text-gray-800 mb-2">System Does:</h4>
                      <ul className="space-y-1 text-gray-700">
                        <li>✓ Requests feedback</li>
                        <li>✓ Analyzes sentiment</li>
                        <li>✓ Creates support tickets</li>
                        <li>✓ Sends personalized offers</li>
                      </ul>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Features Overview */}
      <div className="max-w-7xl mx-auto mb-8">
        <div className="bg-white rounded-lg shadow-lg overflow-hidden">
          <button
            onClick={() => toggleSection('features')}
            className="w-full p-6 bg-gradient-to-r from-indigo-600 to-indigo-700 text-white flex items-center justify-between hover:from-indigo-700 hover:to-indigo-800 transition"
          >
            <div className="flex items-center gap-3">
              <BarChart3 className="w-6 h-6" />
              <h2 className="text-2xl font-bold">Key Features</h2>
            </div>
            {expandedSection === 'features' ? <ChevronUp /> : <ChevronDown />}
          </button>

          {expandedSection === 'features' && (
            <div className="p-8 bg-gray-50">
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {[
                  { title: 'AI Recommendations', desc: 'Smart product suggestions based on customer behavior' },
                  { title: 'Multi-Channel Support', desc: 'WhatsApp, Facebook, Instagram integration' },
                  { title: 'Real-time Tracking', desc: 'Live order status updates' },
                  { title: 'Payment Processing', desc: 'Paymob Egyptian card payments' },
                  { title: 'Sentiment Analysis', desc: 'AI analyzes customer feedback' },
                  { title: 'Inventory Management', desc: 'Stock tracking & forecasting' },
                  { title: 'Analytics Dashboard', desc: 'Sales & customer metrics' },
                  { title: 'Churn Prediction', desc: 'Identify at-risk customers' },
                  { title: 'Notifications', desc: 'Email, SMS, WhatsApp alerts' },
                ].map((feature, idx) => (
                  <div key={idx} className="bg-white p-6 rounded-lg border-2 border-gray-200 hover:border-indigo-400 transition">
                    <h3 className="text-lg font-bold text-gray-900 mb-2">{feature.title}</h3>
                    <p className="text-gray-600">{feature.desc}</p>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Security & Performance */}
      <div className="max-w-7xl mx-auto mb-8">
        <div className="bg-white rounded-lg shadow-lg overflow-hidden">
          <button
            onClick={() => toggleSection('security')}
            className="w-full p-6 bg-gradient-to-r from-red-600 to-red-700 text-white flex items-center justify-between hover:from-red-700 hover:to-red-800 transition"
          >
            <div className="flex items-center gap-3">
              <Shield className="w-6 h-6" />
              <h2 className="text-2xl font-bold">Security & Performance</h2>
            </div>
            {expandedSection === 'security' ? <ChevronUp /> : <ChevronDown />}
          </button>

          {expandedSection === 'security' && (
            <div className="p-8 bg-gray-50">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                <div>
                  <h3 className="text-xl font-bold text-gray-900 mb-4">🔒 Security</h3>
                  <ul className="space-y-2 text-gray-700">
                    <li>✅ JWT Authentication</li>
                    <li>✅ SSL/TLS Encryption</li>
                    <li>✅ CSRF Protection</li>
                    <li>✅ XSS Prevention</li>
                    <li>✅ SQL Injection Protection</li>
                    <li>✅ Rate Limiting</li>
                    <li>✅ Secure Password Hashing</li>
                    <li>✅ OTP Verification</li>
                  </ul>
                </div>
                <div>
                  <h3 className="text-xl font-bold text-gray-900 mb-4">⚡ Performance</h3>
                  <ul className="space-y-2 text-gray-700">
                    <li>✅ Redis Caching</li>
                    <li>✅ Database Indexing</li>
                    <li>✅ Query Optimization</li>
                    <li>✅ CDN Ready</li>
                    <li>✅ Gzip Compression</li>
                    <li>✅ Image Optimization</li>
                    <li>✅ Code Splitting</li>
                    <li>✅ Lazy Loading</li>
                  </ul>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Statistics */}
      <div className="max-w-7xl mx-auto">
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {[
            { label: 'Database Models', value: '13' },
            { label: 'API Endpoints', value: '50+' },
            { label: 'Frontend Pages', value: '10' },
            { label: 'Integration Services', value: '8' },
          ].map((stat, idx) => (
            <div key={idx} className="bg-gradient-to-br from-blue-600 to-purple-600 text-white p-6 rounded-lg text-center">
              <div className="text-3xl font-bold mb-2">{stat.value}</div>
              <div className="text-sm opacity-90">{stat.label}</div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
