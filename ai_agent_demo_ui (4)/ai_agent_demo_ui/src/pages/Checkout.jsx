import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAppStore } from '../store/appStore';
import { orderService } from '../api/services';

export default function Checkout() {
  const navigate = useNavigate();
  const { language, cart, clearCart, setLoading, loading, setError } = useAppStore();
  const [formData, setFormData] = useState({
    customer: 1, 
    delivery_name: '',
    delivery_phone: '',
    delivery_address: '',
    delivery_city: '',
    delivery_postal_code: '',
    payment_method: 'cash',
  });

  const total = cart.reduce((sum, item) => sum + (item.discount_price || item.price), 0);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (cart.length === 0) {
      setError(language === 'ar' ? 'السلة فارغة' : 'Cart is empty');
      return;
    }

    try {
      setLoading(true);
      
      const orderData = {
        ...formData,
        products: cart.map(item => ({
          product_id: item.id,
          quantity: 1,
          price: item.discount_price || item.price,
        })),
        total_price: total,
        discount_amount: 0,
        final_price: total,
        payment_status: 'pending',
      };

      const response = await orderService.create(orderData);
      
      // Clear cart 
      clearCart();
      navigate(`/orders/${response.data.order_number}`);
      
    } catch (error) {
      console.error('Error creating order:', error);
      setError(error.response?.data?.detail || 'Error creating order');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-4xl font-bold mb-8">
        {language === 'ar' ? 'إتمام الشراء' : 'Checkout'}
      </h1>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Form */}
        <div className="lg:col-span-2">
          <form onSubmit={handleSubmit} className="bg-white rounded-lg shadow-md p-8">
            <h2 className="text-2xl font-bold mb-6">
              {language === 'ar' ? 'بيانات التسليم' : 'Delivery Information'}
            </h2>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
              <div>
                <label className="block text-sm font-semibold mb-2">
                  {language === 'ar' ? 'الاسم الكامل' : 'Full Name'}
                </label>
                <input
                  type="text"
                  name="delivery_name"
                  value={formData.delivery_name}
                  onChange={handleChange}
                  required
                  className="w-full px-4 py-2 border rounded focus:outline-none focus:border-blue-600"
                />
              </div>

              <div>
                <label className="block text-sm font-semibold mb-2">
                  {language === 'ar' ? 'رقم الهاتف' : 'Phone Number'}
                </label>
                <input
                  type="tel"
                  name="delivery_phone"
                  value={formData.delivery_phone}
                  onChange={handleChange}
                  required
                  className="w-full px-4 py-2 border rounded focus:outline-none focus:border-blue-600"
                />
              </div>
            </div>

            <div className="mb-6">
              <label className="block text-sm font-semibold mb-2">
                {language === 'ar' ? 'العنوان' : 'Address'}
              </label>
              <input
                type="text"
                name="delivery_address"
                value={formData.delivery_address}
                onChange={handleChange}
                required
                className="w-full px-4 py-2 border rounded focus:outline-none focus:border-blue-600"
              />
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
              <div>
                <label className="block text-sm font-semibold mb-2">
                  {language === 'ar' ? 'المدينة' : 'City'}
                </label>
                <input
                  type="text"
                  name="delivery_city"
                  value={formData.delivery_city}
                  onChange={handleChange}
                  required
                  className="w-full px-4 py-2 border rounded focus:outline-none focus:border-blue-600"
                />
              </div>

              <div>
                <label className="block text-sm font-semibold mb-2">
                  {language === 'ar' ? 'الرمز البريدي' : 'Postal Code'}
                </label>
                <input
                  type="text"
                  name="delivery_postal_code"
                  value={formData.delivery_postal_code}
                  onChange={handleChange}
                  className="w-full px-4 py-2 border rounded focus:outline-none focus:border-blue-600"
                />
              </div>
            </div>

            <div className="mb-6">
              <label className="block text-sm font-semibold mb-2">
                {language === 'ar' ? 'طريقة الدفع' : 'Payment Method'}
              </label>
              <select
                name="payment_method"
                value={formData.payment_method}
                onChange={handleChange}
                className="w-full px-4 py-2 border rounded focus:outline-none focus:border-blue-600"
              >
                <option value="cash">{language === 'ar' ? 'دفع عند الاستلام' : 'Cash on Delivery'}</option>
                <option value="online">{language === 'ar' ? 'دفع أونلاين' : 'Online Payment'}</option>
                <option value="card">{language === 'ar' ? 'بطاقة ائتمان' : 'Credit Card'}</option>
              </select>
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full px-6 py-3 bg-blue-600 text-white rounded hover:bg-blue-700 transition font-bold disabled:bg-gray-400"
            >
              {loading ? (language === 'ar' ? 'جاري المعالجة...' : 'Processing...') : (language === 'ar' ? 'إتمام الطلب' : 'Complete Order')}
            </button>
          </form>
        </div>

        {/* Order Summary */}
        <div className="lg:col-span-1">
          <div className="bg-white rounded-lg shadow-md p-6 sticky top-20">
            <h2 className="text-2xl font-bold mb-6">
              {language === 'ar' ? 'ملخص الطلب' : 'Order Summary'}
            </h2>

            <div className="space-y-4 mb-6">
              {cart.map((item, idx) => (
                <div key={idx} className="flex justify-between text-sm">
                  <span>{item.name}</span>
                  <span>{item.discount_price || item.price} ر.س</span>
                </div>
              ))}
            </div>

            <div className="border-t pt-4">
              <div className="flex justify-between text-lg font-bold">
                <span>{language === 'ar' ? 'الإجمالي' : 'Total'}</span>
                <span className="text-green-600">{total} ر.س</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
