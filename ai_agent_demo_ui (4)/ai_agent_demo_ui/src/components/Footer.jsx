import { useAppStore } from '../store/appStore';

export default function Footer() {
  const { language } = useAppStore();

  return (
    <footer className="bg-gray-800 text-white py-8 mt-12">
      <div className="container mx-auto px-4">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          {/* About */}
          <div>
            <h3 className="text-xl font-bold mb-4">
              {language === 'ar' ? 'عن المتجر' : 'About Store'}
            </h3>
            <p className="text-gray-400">
              {language === 'ar'
                ? 'متجر طبي موثوق يقدم منتجات صحية عالية الجودة'
                : 'Trusted medical store offering high-quality health products'}
            </p>
          </div>

          {/* Quick Links */}
          <div>
            <h3 className="text-xl font-bold mb-4">
              {language === 'ar' ? 'روابط سريعة' : 'Quick Links'}
            </h3>
            <ul className="space-y-2 text-gray-400">
              <li><a href="/products" className="hover:text-white transition">
                {language === 'ar' ? 'المنتجات' : 'Products'}
              </a></li>
              <li><a href="/support" className="hover:text-white transition">
                {language === 'ar' ? 'الدعم' : 'Support'}
              </a></li>
              <li><a href="/chat" className="hover:text-white transition">
                {language === 'ar' ? 'المساعد الذكي' : 'AI Chat'}
              </a></li>
            </ul>
          </div>

          {/* Contact */}
          <div>
            <h3 className="text-xl font-bold mb-4">
              {language === 'ar' ? 'اتصل بنا' : 'Contact Us'}
            </h3>
            <p className="text-gray-400">
              📧 support@medistore.com<br />
              📱 +966 50 123 4567<br />
              🕐 {language === 'ar' ? '24/7 متاح' : '24/7 Available'}
            </p>
          </div>
        </div>

        <div className="border-t border-gray-700 mt-8 pt-8 text-center text-gray-400">
          <p>&copy; 2024 MediStore. {language === 'ar' ? 'جميع الحقوق محفوظة' : 'All rights reserved'}</p>
        </div>
      </div>
    </footer>
  );
}
