import { Link } from 'react-router-dom';
import { useAppStore } from '../store/appStore';

export default function Navbar() {
  const { language, setLanguage, cart } = useAppStore();

  return (
    <nav className="bg-white shadow-md sticky top-0 z-50">
      <div className="container mx-auto px-4 py-4">
        <div className="flex justify-between items-center">
          {/* Logo */}
          <Link to="/" className="text-2xl font-bold text-blue-600">
            🏥 MediStore
          </Link>

          {/* Navigation Links */}
          <div className="hidden md:flex gap-6">
            <Link to="/" className="hover:text-blue-600 transition">
              {language === 'ar' ? 'الرئيسية' : 'Home'}
            </Link>
            <Link to="/products" className="hover:text-blue-600 transition">
              {language === 'ar' ? 'المنتجات' : 'Products'}
            </Link>
            <Link to="/chat" className="hover:text-blue-600 transition">
              {language === 'ar' ? 'المساعد الذكي' : 'AI Chat'}
            </Link>
            <Link to="/support" className="hover:text-blue-600 transition">
              {language === 'ar' ? 'الدعم' : 'Support'}
            </Link>
            <Link to="/showcase" className="hover:text-blue-600 transition font-semibold text-purple-600">
              {language === 'ar' ? '🎨 عرض النظام' : '🎨 System'}
            </Link>
            <Link to="/demo" className="hover:text-blue-600 transition font-semibold text-green-600">
              {language === 'ar' ? '🎬 عرض توضيحي' : '🎬 Demo'}
            </Link>
          </div>

          {/* Right Side */}
          <div className="flex items-center gap-4">
            {/* Language Toggle */}
            <button
              onClick={() => setLanguage(language === 'ar' ? 'en' : 'ar')}
              className="px-3 py-2 bg-gray-200 rounded hover:bg-gray-300 transition"
            >
              {language === 'ar' ? 'EN' : 'AR'}
            </button>

            {/* Cart */}
            <Link to="/cart" className="relative">
              <span className="text-2xl">🛒</span>
              {cart.length > 0 && (
                <span className="absolute -top-2 -right-2 bg-red-500 text-white text-xs rounded-full w-5 h-5 flex items-center justify-center">
                  {cart.length}
                </span>
              )}
            </Link>

            {/* Dashboard */}
            <Link to="/dashboard" className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 transition">
              {language === 'ar' ? 'لوحة التحكم' : 'Dashboard'}
            </Link>
          </div>
        </div>
      </div>
    </nav>
  );
}
