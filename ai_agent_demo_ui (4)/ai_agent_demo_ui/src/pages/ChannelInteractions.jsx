import React, { useState } from 'react';
import { MessageCircle, Send, Heart, Share2, Copy, Download, AlertCircle, CheckCircle, Clock } from 'lucide-react';

export default function ChannelInteractions() {
  const [selectedChannel, setSelectedChannel] = useState('whatsapp');
  const [conversationHistory, setConversationHistory] = useState([]);
  const [inputValue, setInputValue] = useState('');

  const channels = {
    whatsapp: {
      name: 'WhatsApp Business',
      color: 'from-green-500 to-green-600',
      icon: '💬',
      features: ['Real-time messaging', 'Media sharing', 'Group chats', 'Status updates'],
      example: 'مرحباً، هل يمكنك مساعدتي في اختيار منتج؟',
      responses: [
        'بالتأكيد! ما نوع المنتج الذي تبحث عنه؟',
        'لدينا عدة خيارات رائعة. هل تريد منتج للمناعة أم للطاقة؟',
        'ممتاز! سأرسل لك الخيارات المتاحة الآن.',
      ],
    },
    instagram: {
      name: 'Instagram Direct Messages',
      color: 'from-pink-500 to-purple-600',
      icon: '📸',
      features: ['Visual catalog', 'Story replies', 'Quick replies', 'Carousel posts'],
      example: 'Hey! I saw your products, are they available?',
      responses: [
        'Hey! 👋 Yes, all our products are in stock!',
        'Which product interests you the most? 😊',
        'Perfect! Let me send you the details and pricing.',
      ],
    },
    facebook: {
      name: 'Facebook Messenger',
      color: 'from-blue-500 to-blue-600',
      icon: '👥',
      features: ['Customer support', 'Order updates', 'Quick replies', 'Bot automation'],
      example: 'Hello, I have a question about my order',
      responses: [
        'Hello! How can I help you today? 😊',
        'I can help you track your order or answer any questions.',
        'Your order is on the way! Expected delivery tomorrow.',
      ],
    },
  };

  const currentChannel = channels[selectedChannel];

  const handleSendMessage = (message) => {
    if (!message.trim()) return;

    setConversationHistory((prev) => [
      ...prev,
      { role: 'user', text: message, timestamp: new Date() },
    ]);
    setInputValue('');

    setTimeout(() => {
      const randomResponse = currentChannel.responses[
        Math.floor(Math.random() * currentChannel.responses.length)
      ];
      setConversationHistory((prev) => [
        ...prev,
        { role: 'ai', text: randomResponse, timestamp: new Date() },
      ]);
    }, 1000);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-gray-800 to-black p-4 md:p-8">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-4xl md:text-5xl font-bold text-white mb-2">🌐 Channel-Specific Interactions</h1>
          <p className="text-lg text-gray-300">Experience authentic communication across different platforms</p>
        </div>

        {/* Channel Selector */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
          {Object.entries(channels).map(([key, channel]) => (
            <button
              key={key}
              onClick={() => {
                setSelectedChannel(key);
                setConversationHistory([]);
              }}
              className={`p-6 rounded-lg transition transform hover:scale-105 ${
                selectedChannel === key
                  ? `bg-gradient-to-r ${channel.color} text-white shadow-2xl`
                  : 'bg-gray-800 text-gray-300 hover:bg-gray-700'
              }`}
            >
              <div className="text-4xl mb-2">{channel.icon}</div>
              <h3 className="font-bold text-lg mb-2">{channel.name}</h3>
              <div className="text-xs space-y-1">
                {channel.features.map((feature, idx) => (
                  <div key={idx} className="flex items-center gap-2">
                    <span className="text-blue-400">✓</span>
                    <span>{feature}</span>
                  </div>
                ))}
              </div>
            </button>
          ))}
        </div>

        {/* Main Chat Area */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Chat Interface */}
          <div className="lg:col-span-2 bg-gray-800 rounded-lg shadow-2xl overflow-hidden flex flex-col h-[600px]">
            {/* Header */}
            <div className={`bg-gradient-to-r ${currentChannel.color} p-6 text-white`}>
              <h2 className="text-2xl font-bold">{currentChannel.name}</h2>
              <p className="text-sm opacity-90">Authentic platform experience</p>
            </div>

            {/* Messages */}
            <div className="flex-1 overflow-y-auto p-6 space-y-4">
              {conversationHistory.length === 0 ? (
                <div className="h-full flex items-center justify-center text-gray-400">
                  <div className="text-center">
                    <MessageCircle className="w-16 h-16 mx-auto mb-4 opacity-50" />
                    <p>Start a conversation...</p>
                  </div>
                </div>
              ) : (
                conversationHistory.map((msg, idx) => (
                  <div key={idx} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                    <div
                      className={`max-w-xs px-4 py-3 rounded-lg ${
                        msg.role === 'user'
                          ? 'bg-blue-600 text-white rounded-br-none'
                          : 'bg-gray-700 text-gray-100 rounded-bl-none'
                      }`}
                    >
                      <p>{msg.text}</p>
                      <p className="text-xs opacity-70 mt-1">{msg.timestamp.toLocaleTimeString()}</p>
                    </div>
                  </div>
                ))
              )}
            </div>

            {/* Input Area */}
            <div className="border-t border-gray-700 p-4 bg-gray-900">
              <div className="flex gap-2">
                <input
                  type="text"
                  placeholder="Type message..."
                  value={inputValue}
                  onChange={(e) => setInputValue(e.target.value)}
                  className="flex-1 bg-gray-700 text-white px-4 py-2 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  onKeyPress={(e) => {
                    if (e.key === 'Enter') {
                      handleSendMessage(inputValue);
                    }
                  }}
                />
                <button
                  onClick={() => handleSendMessage(inputValue)}
                  className="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 transition"
                >
                  <Send className="w-5 h-5" />
                </button>
              </div>
            </div>
          </div>

          {/* Info Panel */}
          <div className="space-y-4">
            {/* Platform Features */}
            <div className="bg-gradient-to-br from-purple-900 to-purple-800 rounded-lg p-6">
              <h3 className="text-xl font-bold text-white mb-4">🎯 Platform Features</h3>
              <div className="space-y-3">
                {currentChannel.features.map((feature, idx) => (
                  <div key={idx} className="flex items-center gap-3">
                    <CheckCircle className="w-5 h-5 text-green-400" />
                    <span className="text-gray-200">{feature}</span>
                  </div>
                ))}
              </div>
            </div>

            {/* Quick Templates */}
            <div className="bg-gray-800 rounded-lg p-6">
              <h3 className="text-lg font-bold text-white mb-4">📋 Quick Templates</h3>
              <div className="space-y-2">
                {currentChannel.responses.map((response, idx) => (
                  <button
                    key={idx}
                    onClick={() => handleSendMessage(response)}
                    className="w-full text-left bg-gray-700 hover:bg-gray-600 text-gray-200 p-3 rounded-lg transition text-sm"
                  >
                    {response.substring(0, 50)}...
                  </button>
                ))}
              </div>
            </div>

            {/* Stats */}
            <div className="bg-gradient-to-br from-green-900 to-green-800 rounded-lg p-6">
              <h3 className="text-lg font-bold text-white mb-4">📊 Conversation Stats</h3>
              <div className="space-y-2 text-sm text-gray-200">
                <div className="flex justify-between">
                  <span>Messages:</span>
                  <span className="font-bold text-green-400">{conversationHistory.length}</span>
                </div>
                <div className="flex justify-between">
                  <span>Response Time:</span>
                  <span className="font-bold text-green-400">~1s</span>
                </div>
                <div className="flex justify-between">
                  <span>Satisfaction:</span>
                  <span className="font-bold text-green-400">98%</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Channel Comparison */}
        <div className="mt-12 bg-gray-800 rounded-lg p-8">
          <h2 className="text-3xl font-bold text-white mb-8">📊 Channel Comparison</h2>
          <div className="overflow-x-auto">
            <table className="w-full text-sm md:text-base">
              <thead>
                <tr className="border-b border-gray-700">
                  <th className="text-left py-3 px-4 text-gray-300">Feature</th>
                  <th className="text-center py-3 px-4 text-gray-300">WhatsApp</th>
                  <th className="text-center py-3 px-4 text-gray-300">Instagram</th>
                  <th className="text-center py-3 px-4 text-gray-300">Facebook</th>
                </tr>
              </thead>
              <tbody>
                {[
                  { feature: 'Real-time Messaging', whatsapp: true, instagram: true, facebook: true },
                  { feature: 'Media Sharing', whatsapp: true, instagram: true, facebook: true },
                  { feature: 'Group Support', whatsapp: true, instagram: false, facebook: true },
                  { feature: 'Status Updates', whatsapp: true, instagram: true, facebook: false },
                  { feature: 'Quick Replies', whatsapp: true, instagram: true, facebook: true },
                  { feature: 'Automation', whatsapp: true, instagram: false, facebook: true },
                ].map((row, idx) => (
                  <tr key={idx} className="border-b border-gray-700 hover:bg-gray-700">
                    <td className="py-3 px-4 text-gray-300">{row.feature}</td>
                    <td className="text-center py-3 px-4">
                      {row.whatsapp ? <CheckCircle className="w-5 h-5 text-green-400 mx-auto" /> : <AlertCircle className="w-5 h-5 text-gray-500 mx-auto" />}
                    </td>
                    <td className="text-center py-3 px-4">
                      {row.instagram ? <CheckCircle className="w-5 h-5 text-green-400 mx-auto" /> : <AlertCircle className="w-5 h-5 text-gray-500 mx-auto" />}
                    </td>
                    <td className="text-center py-3 px-4">
                      {row.facebook ? <CheckCircle className="w-5 h-5 text-green-400 mx-auto" /> : <AlertCircle className="w-5 h-5 text-gray-500 mx-auto" />}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
}
