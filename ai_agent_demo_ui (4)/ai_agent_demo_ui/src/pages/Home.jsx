import { Link } from 'react-router-dom';
import { useAppStore } from '../store/appStore';

export default function Home() {
  const { language } = useAppStore();

  const features = [
    {
      icon: '🏥',
      title: language === 'ar' ? 'منتجات موثوقة' : 'Trusted Products',
      desc: language === 'ar' ? 'منتجات طبية معتمدة' : 'Certified medical products',
    },
    {
      icon: '🚚',
      title: language === 'ar' ? 'شحن سريع' : 'Fast Shipping',
      desc: language === 'ar' ? 'توصيل في 24 ساعة' : 'Delivery in 24 hours',
    },
    {
      icon: '💬',
      title: language === 'ar' ? 'مساعد ذكي' : 'AI Assistant',
      desc: language === 'ar' ? 'مساعد متاح 24/7' : '24/7 AI support',
    },
    {
      icon: '⭐',
      title: language === 'ar' ? 'ضمان الجودة' : 'Quality Guarantee',
      desc: language === 'ar' ? 'ضمان 100% أو استرجاع' : '100% guarantee or refund',
    },
  ];

  return (
    <div className="w-full">
      {/* Hero Section */}
      <section className="bg-gradient-to-r from-blue-600 to-blue-800 text-white py-20">
        <div className="container mx-auto px-4 text-center">
          <h1 className="text-5xl font-bold mb-4">
            {language === 'ar' ? 'مرحباً بك في متجرنا الطبي' : 'Welcome to MediStore'}
          </h1>
          <p className="text-xl mb-8">
            {language === 'ar'
              ? 'أفضل المنتجات الصحية بأسعار منافسة'
              : 'Best health products at competitive prices'}
          </p>
          <div className="flex gap-4 justify-center">
            <Link
              to="/products"
              className="px-8 py-3 bg-white text-blue-600 font-bold rounded hover:bg-gray-100 transition"
            >
              {language === 'ar' ? 'تصفح المنتجات' : 'Shop Now'}
            </Link>
            <Link
              to="/chat"
              className="px-8 py-3 bg-blue-700 text-white font-bold rounded hover:bg-blue-900 transition"
            >
              {language === 'ar' ? 'تحدث مع المساعد' : 'Chat with AI'}
            </Link>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-16 bg-gray-50">
        <div className="container mx-auto px-4">
          <h2 className="text-3xl font-bold text-center mb-12">
            {language === 'ar' ? 'لماذا تختارنا؟' : 'Why Choose Us?'}
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
            {features.map((feature, idx) => (
              <div key={idx} className="bg-white p-6 rounded-lg shadow-md text-center hover:shadow-lg transition">
                <div className="text-4xl mb-4">{feature.icon}</div>
                <h3 className="text-xl font-bold mb-2">{feature.title}</h3>
                <p className="text-gray-600">{feature.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="bg-blue-600 text-white py-16">
        <div className="container mx-auto px-4 text-center">
          <h2 className="text-3xl font-bold mb-4">
            {language === 'ar' ? 'هل تحتاج مساعدة؟' : 'Need Help?'}
          </h2>
          <p className="text-lg mb-8">
            {language === 'ar'
              ? 'تحدث مع مساعدنا الذكي لاختيار المنتج المناسب'
              : 'Talk to our AI assistant to find the right product'}
          </p>
          <Link
            to="/chat"
            className="px-8 py-3 bg-white text-blue-600 font-bold rounded hover:bg-gray-100 transition inline-block"
          >
            {language === 'ar' ? 'ابدأ المحادثة' : 'Start Chat'}
          </Link>
        </div>
      </section>
    </div>
  );
}
