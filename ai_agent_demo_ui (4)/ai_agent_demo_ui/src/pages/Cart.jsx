import { Link } from 'react-router-dom';
import { useAppStore } from '../store/appStore';

export default function Cart() {
  const { language, cart, removeFromCart, clearCart } = useAppStore();

  const total = cart.reduce((sum, item) => sum + (item.discount_price || item.price), 0);

  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-4xl font-bold mb-8">
        {language === 'ar' ? 'سلة التسوق' : 'Shopping Cart'}
      </h1>

      {cart.length === 0 ? (
        <div className="text-center py-12">
          <p className="text-xl mb-4">
            {language === 'ar' ? 'السلة فارغة' : 'Your cart is empty'}
          </p>
          <Link
            to="/products"
            className="px-6 py-3 bg-blue-600 text-white rounded hover:bg-blue-700 transition inline-block"
          >
            {language === 'ar' ? 'تصفح المنتجات' : 'Shop Now'}
          </Link>
        </div>
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Cart Items */}
          <div className="lg:col-span-2">
            <div className="bg-white rounded-lg shadow-md overflow-hidden">
              <table className="w-full">
                <thead className="bg-gray-100">
                  <tr>
                    <th className="px-6 py-3 text-left">{language === 'ar' ? 'المنتج' : 'Product'}</th>
                    <th className="px-6 py-3 text-left">{language === 'ar' ? 'السعر' : 'Price'}</th>
                    <th className="px-6 py-3 text-left">{language === 'ar' ? 'إجراء' : 'Action'}</th>
                  </tr>
                </thead>
                <tbody>
                  {cart.map((item) => (
                    <tr key={item.cartId} className="border-b hover:bg-gray-50">
                      <td className="px-6 py-4">
                        <div>
                          <p className="font-semibold">{item.name}</p>
                          <p className="text-sm text-gray-600">{item.description}</p>
                        </div>
                      </td>
                      <td className="px-6 py-4">
                        <p className="font-bold text-green-600">
                          {item.discount_price || item.price} ر.س
                        </p>
                      </td>
                      <td className="px-6 py-4">
                        <button
                          onClick={() => removeFromCart(item.cartId)}
                          className="px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700 transition text-sm"
                        >
                          {language === 'ar' ? 'حذف' : 'Remove'}
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            {/* Clear Cart */}
            <button
              onClick={clearCart}
              className="mt-4 px-6 py-2 bg-red-600 text-white rounded hover:bg-red-700 transition"
            >
              {language === 'ar' ? 'مسح السلة' : 'Clear Cart'}
            </button>
          </div>

          {/* Order Summary */}
          <div className="lg:col-span-1">
            <div className="bg-white rounded-lg shadow-md p-6 sticky top-20">
              <h2 className="text-2xl font-bold mb-6">
                {language === 'ar' ? 'ملخص الطلب' : 'Order Summary'}
              </h2>

              <div className="space-y-4 mb-6">
                <div className="flex justify-between">
                  <span>{language === 'ar' ? 'عدد المنتجات' : 'Items'}</span>
                  <span className="font-bold">{cart.length}</span>
                </div>
                <div className="flex justify-between text-lg font-bold border-t pt-4">
                  <span>{language === 'ar' ? 'الإجمالي' : 'Total'}</span>
                  <span className="text-green-600">{total} ر.س</span>
                </div>
              </div>

              <Link
                to="/checkout"
                className="w-full px-6 py-3 bg-blue-600 text-white rounded hover:bg-blue-700 transition font-bold text-center block"
              >
                {language === 'ar' ? 'متابعة الشراء' : 'Proceed to Checkout'}
              </Link>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
