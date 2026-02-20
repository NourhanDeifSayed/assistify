import React from 'react';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import InteractiveDemo from './pages/InteractiveDemo';
import ChannelInteractions from './pages/ChannelInteractions';
import JourneySimulation from './pages/JourneySimulation';
import NotificationCenter from './pages/NotificationCenter';

export default function App() {
  return (
    <Router>
      <Routes>
        {/* Home - Demo Hub */}
        <Route
          path="/"
          element={
            <div className="min-h-screen bg-gradient-to-br from-gray-900 via-gray-800 to-black">
              {/* Navigation */}
              <nav className="bg-gray-900 border-b border-gray-800">
                <div className="max-w-7xl mx-auto px-4 py-4 md:py-6">
                  <h1 className="text-2xl md:text-3xl font-bold text-white">🎬 AI Agent Demo Hub</h1>
                </div>
              </nav>

              {/* Main Content */}
              <div className="max-w-7xl mx-auto px-4 py-8 md:py-12">
                <div className="text-center mb-12">
                  <h2 className="text-4xl md:text-5xl font-bold text-white mb-4">
                    Complete AI Agent Funnel Platform
                  </h2>
                  <p className="text-lg md:text-xl text-gray-300">
                    Multi-Channel Communication • Shopify Integration • Real-Time Tracking
                  </p>
                </div>

                {/* Demo Cards Grid */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6 md:gap-8">
                  {/* Interactive Demo */}
                  <Link
                    to="/demo"
                    className="group bg-gradient-to-br from-blue-900 to-purple-900 rounded-lg p-8 hover:shadow-2xl transition transform hover:scale-105"
                  >
                    <div className="text-5xl mb-4">🎬</div>
                    <h3 className="text-2xl font-bold text-white mb-2">Interactive Demo</h3>
                    <p className="text-gray-300 mb-4">
                      Experience the complete customer journey with multi-channel communication and Shopify integration
                    </p>
                    <div className="flex items-center gap-2 text-blue-400 group-hover:text-blue-300">
                      <span>Launch Demo</span>
                      <span>→</span>
                    </div>
                  </Link>

                  {/* Channel Interactions */}
                  <Link
                    to="/channels"
                    className="group bg-gradient-to-br from-green-900 to-teal-900 rounded-lg p-8 hover:shadow-2xl transition transform hover:scale-105"
                  >
                    <div className="text-5xl mb-4">🌐</div>
                    <h3 className="text-2xl font-bold text-white mb-2">Channel Interactions</h3>
                    <p className="text-gray-300 mb-4">
                      Explore authentic communication across WhatsApp, Instagram, and Facebook Messenger
                    </p>
                    <div className="flex items-center gap-2 text-green-400 group-hover:text-green-300">
                      <span>Explore Channels</span>
                      <span>→</span>
                    </div>
                  </Link>

                  {/* Journey Simulation */}
                  <Link
                    to="/journey"
                    className="group bg-gradient-to-br from-orange-900 to-red-900 rounded-lg p-8 hover:shadow-2xl transition transform hover:scale-105"
                  >
                    <div className="text-5xl mb-4">🎯</div>
                    <h3 className="text-2xl font-bold text-white mb-2">Journey Simulation</h3>
                    <p className="text-gray-300 mb-4">
                      Watch the complete customer lifecycle from pre-sale to post-sale with real-time tracking
                    </p>
                    <div className="flex items-center gap-2 text-orange-400 group-hover:text-orange-300">
                      <span>Simulate Journey</span>
                      <span>→</span>
                    </div>
                  </Link>

                  {/* Notification Center */}
                  <Link
                    to="/notifications"
                    className="group bg-gradient-to-br from-pink-900 to-rose-900 rounded-lg p-8 hover:shadow-2xl transition transform hover:scale-105"
                  >
                    <div className="text-5xl mb-4">🔔</div>
                    <h3 className="text-2xl font-bold text-white mb-2">Notification Center</h3>
                    <p className="text-gray-300 mb-4">
                      Manage real-time notifications across orders, shipping, messages, and feedback
                    </p>
                    <div className="flex items-center gap-2 text-pink-400 group-hover:text-pink-300">
                      <span>View Notifications</span>
                      <span>→</span>
                    </div>
                  </Link>
                </div>

                {/* Features Overview */}
                <div className="mt-12 md:mt-16 bg-gray-800 rounded-lg p-8 md:p-12">
                  <h2 className="text-3xl md:text-4xl font-bold text-white mb-8">✨ Key Features</h2>
                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 md:gap-8">
                    {[
                      {
                        icon: '💬',
                        title: 'Multi-Channel Support',
                        description: 'WhatsApp, Instagram, Facebook Messenger integration',
                      },
                      {
                        icon: '🛍️',
                        title: 'Shopify Integration',
                        description: 'Real-time product sync and order management',
                      },
                      {
                        icon: '🚚',
                        title: 'Real-Time Tracking',
                        description: 'Live shipping updates with delay detection',
                      },
                      {
                        icon: '🤖',
                        title: 'AI-Powered Responses',
                        description: 'Manus LLM for intelligent customer interactions',
                      },
                      {
                        icon: '📊',
                        title: 'Analytics Dashboard',
                        description: 'Track conversions and customer metrics',
                      },
                      {
                        icon: '⭐',
                        title: 'Feedback Collection',
                        description: 'Post-sale ratings and personalized offers',
                      },
                    ].map((feature, idx) => (
                      <div key={idx} className="bg-gray-700 rounded-lg p-6">
                        <div className="text-4xl mb-3">{feature.icon}</div>
                        <h3 className="text-lg font-bold text-white mb-2">{feature.title}</h3>
                        <p className="text-gray-300 text-sm">{feature.description}</p>
                      </div>
                    ))}
                  </div>
                </div>

                {/* CTA Section */}
                <div className="mt-12 md:mt-16 bg-gradient-to-r from-blue-600 to-purple-600 rounded-lg p-8 md:p-12 text-center">
                  <h2 className="text-3xl md:text-4xl font-bold text-white mb-4">Ready to Transform Your E-Commerce?</h2>
                  <p className="text-lg text-gray-100 mb-6">
                    Experience the power of AI-driven customer engagement across all channels
                  </p>
                  <button className="bg-white text-blue-600 px-8 py-3 rounded-lg font-bold hover:bg-gray-100 transition">
                    Get Started Now
                  </button>
                </div>
              </div>
            </div>
          }
        />

        {/* Demo Pages */}
        <Route path="/demo" element={<InteractiveDemo />} />
        <Route path="/channels" element={<ChannelInteractions />} />
        <Route path="/journey" element={<JourneySimulation />} />
        <Route path="/notifications" element={<NotificationCenter />} />
      </Routes>
    </Router>
  );
}
