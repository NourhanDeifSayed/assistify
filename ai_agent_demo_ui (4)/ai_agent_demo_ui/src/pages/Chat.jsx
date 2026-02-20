import { useState, useRef, useEffect } from 'react';
import { useAppStore } from '../store/appStore';
import { conversationService } from '../api/services';

export default function Chat() {
  const { language } = useAppStore();
  const [messages, setMessages] = useState([
    {
      id: 1,
      role: 'assistant',
      content: language === 'ar'
        ? 'مرحباً! أنا مساعدك الذكي. كيف يمكنني مساعدتك اليوم؟'
        : 'Hello! I\'m your AI assistant. How can I help you today?',
    },
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSendMessage = async (e) => {
    e.preventDefault();
    if (!input.trim()) return;

    // Add user message
    const userMessage = {
      id: messages.length + 1,
      role: 'user',
      content: input,
    };
    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setLoading(true);

    try {
      // Simulate AI response
      setTimeout(() => {
        const responses = {
          ar: [
            'هذا سؤال رائع! دعني أساعدك بمزيد من المعلومات.',
            'أنا هنا لمساعدتك في اختيار المنتج المناسب.',
            'هل تريد معرفة المزيد عن منتجاتنا؟',
            'يمكنني أن أوصيك بمنتجات مناسبة لاحتياجاتك.',
          ],
          en: [
            'That\'s a great question! Let me help you with more information.',
            'I\'m here to help you choose the right product.',
            'Would you like to know more about our products?',
            'I can recommend products suitable for your needs.',
          ],
        };

        const randomResponse = responses[language][Math.floor(Math.random() * responses[language].length)];
        
        setMessages(prev => [...prev, {
          id: prev.length + 1,
          role: 'assistant',
          content: randomResponse,
        }]);
        setLoading(false);
      }, 1000);
    } catch (error) {
      console.error('Error sending message:', error);
      setLoading(false);
    }
  };

  const quickActions = [
    {
      label: language === 'ar' ? 'المنتجات المشهورة' : 'Popular Products',
      message: language === 'ar' ? 'أريد أن أرى المنتجات المشهورة' : 'Show me popular products',
    },
    {
      label: language === 'ar' ? 'العروض الخاصة' : 'Special Offers',
      message: language === 'ar' ? 'ما هي العروض الخاصة المتاحة؟' : 'What special offers do you have?',
    },
    {
      label: language === 'ar' ? 'تتبع الطلب' : 'Track Order',
      message: language === 'ar' ? 'أريد تتبع طلبي' : 'I want to track my order',
    },
    {
      label: language === 'ar' ? 'الدعم' : 'Support',
      message: language === 'ar' ? 'أحتاج إلى مساعدة' : 'I need support',
    },
  ];

  return (
    <div className="container mx-auto px-4 py-8 h-screen flex flex-col">
      <h1 className="text-4xl font-bold mb-8">
        {language === 'ar' ? 'المساعد الذكي' : 'AI Assistant'}
      </h1>

      <div className="flex-1 grid grid-cols-1 lg:grid-cols-4 gap-8">
        {/* Chat Area */}
        <div className="lg:col-span-3 flex flex-col bg-white rounded-lg shadow-md overflow-hidden">
          {/* Messages */}
          <div className="flex-1 overflow-y-auto p-6 space-y-4">
            {messages.map((msg) => (
              <div
                key={msg.id}
                className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                <div
                  className={`max-w-xs lg:max-w-md px-4 py-2 rounded-lg ${
                    msg.role === 'user'
                      ? 'bg-blue-600 text-white'
                      : 'bg-gray-200 text-gray-800'
                  }`}
                >
                  {msg.content}
                </div>
              </div>
            ))}
            {loading && (
              <div className="flex justify-start">
                <div className="bg-gray-200 text-gray-800 px-4 py-2 rounded-lg">
                  <div className="flex gap-1">
                    <div className="w-2 h-2 bg-gray-600 rounded-full animate-bounce"></div>
                    <div className="w-2 h-2 bg-gray-600 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                    <div className="w-2 h-2 bg-gray-600 rounded-full animate-bounce" style={{ animationDelay: '0.4s' }}></div>
                  </div>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>

          {/* Input */}
          <form onSubmit={handleSendMessage} className="border-t p-4 flex gap-2">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder={language === 'ar' ? 'اكتب رسالتك...' : 'Type your message...'}
              className="flex-1 px-4 py-2 border rounded focus:outline-none focus:border-blue-600"
              disabled={loading}
            />
            <button
              type="submit"
              disabled={loading || !input.trim()}
              className="px-6 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 transition disabled:bg-gray-400"
            >
              {language === 'ar' ? 'إرسال' : 'Send'}
            </button>
          </form>
        </div>

        {/* Quick Actions */}
        <div className="lg:col-span-1">
          <div className="bg-white rounded-lg shadow-md p-6 sticky top-20">
            <h2 className="text-xl font-bold mb-4">
              {language === 'ar' ? 'إجراءات سريعة' : 'Quick Actions'}
            </h2>
            <div className="space-y-2">
              {quickActions.map((action, idx) => (
                <button
                  key={idx}
                  onClick={() => {
                    setInput(action.message);
                    setTimeout(() => {
                      document.querySelector('form')?.dispatchEvent(new Event('submit', { bubbles: true }));
                    }, 0);
                  }}
                  className="w-full px-4 py-2 bg-gray-100 text-gray-800 rounded hover:bg-blue-100 transition text-sm text-left"
                >
                  {action.label}
                </button>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
