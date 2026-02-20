import { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { useAppStore } from '../store/appStore';
import { orderService } from '../api/services';

export default function OrderTracking() {
  const { orderNumber } = useParams();
  const { language, setLoading, loading } = useAppStore();
  const [order, setOrder] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchOrder();
  }, [orderNumber]);

  const fetchOrder = async () => {
    try {
      setLoading(true);
      // In real app, you'd fetch by order number
      const response = await orderService.getAll({ order_number: orderNumber });
      if (response.data.results.length > 0) {
        setOrder(response.data.results[0]);
      } else {
        setError(language === 'ar' ? 'الطلب غير موجود' : 'Order not found');
      }
    } catch (err) {
      setError(language === 'ar' ? 'خطأ في جلب الطلب' : 'Error fetching order');
    } finally {
      setLoading(false);
    }
  };

  const getStatusColor = (status) => {
    const colors = {
      pending: 'bg-yellow-100 text-yellow-800',
      confirmed: 'bg-blue-100 text-blue-800',
      shipped: 'bg-purple-100 text-purple-800',
      delivered: 'bg-green-100 text-green-800',
      cancelled: 'bg-red-100 text-red-800',
    };
    return colors[status] || 'bg-gray-100 text-gray-800';
  };

  const statusSteps = ['pending', 'confirmed', 'shipped', 'delivered'];
  const currentStepIndex = order ? statusSteps.indexOf(order.status) : -1;

  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-4xl font-bold mb-8">
        {language === 'ar' ? 'تتبع الطلب' : 'Order Tracking'}
      </h1>

      {loading ? (
        <div className="text-center py-12">
          {language === 'ar' ? 'جاري التحميل...' : 'Loading...'}
        </div>
      ) : error ? (
        <div className="bg-red-100 text-red-800 p-4 rounded mb-8">
          {error}
        </div>
      ) : order ? (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Order Status */}
          <div className="lg:col-span-2">
            {/* Status Timeline */}
            <div className="bg-white rounded-lg shadow-md p-8 mb-8">
              <h2 className="text-2xl font-bold mb-8">
                {language === 'ar' ? 'حالة الطلب' : 'Order Status'}
              </h2>

              <div className="relative">
                <div className="flex justify-between mb-8">
                  {statusSteps.map((step, idx) => (
                    <div key={step} className="flex flex-col items-center flex-1">
                      <div
                        className={`w-12 h-12 rounded-full flex items-center justify-center font-bold text-white ${
                          idx <= currentStepIndex ? 'bg-green-600' : 'bg-gray-300'
                        }`}
                      >
                        {idx + 1}
                      </div>
                      <p className="text-sm mt-2 text-center">
                        {language === 'ar'
                          ? {
                              pending: 'قيد الانتظار',
                              confirmed: 'مؤكد',
                              shipped: 'مشحون',
                              delivered: 'مسلم',
                            }[step]
                          : {
                              pending: 'Pending',
                              confirmed: 'Confirmed',
                              shipped: 'Shipped',
                              delivered: 'Delivered',
                            }[step]}
                      </p>
                    </div>
                  ))}
                </div>

                {/* Progress Bar */}
                <div className="h-2 bg-gray-300 rounded-full mb-8">
                  <div
                    className="h-full bg-green-600 rounded-full transition-all duration-300"
                    style={{
                      width: `${((currentStepIndex + 1) / statusSteps.length) * 100}%`,
                    }}
                  />
                </div>
              </div>

              {/* Current Status */}
              <div className={`p-4 rounded ${getStatusColor(order.status)}`}>
                <p className="font-bold">
                  {language === 'ar' ? 'الحالة الحالية:' : 'Current Status:'}{' '}
                  {order.status_display}
                </p>
              </div>
            </div>

            {/* Tracking Details */}
            {order.tracking_number && (
              <div className="bg-white rounded-lg shadow-md p-8">
                <h2 className="text-2xl font-bold mb-6">
                  {language === 'ar' ? 'تفاصيل الشحن' : 'Shipping Details'}
                </h2>

                <div className="space-y-4">
                  <div className="flex justify-between border-b pb-4">
                    <span className="font-semibold">
                      {language === 'ar' ? 'رقم التتبع' : 'Tracking Number'}
                    </span>
                    <span className="font-mono">{order.tracking_number}</span>
                  </div>

                  <div className="flex justify-between border-b pb-4">
                    <span className="font-semibold">
                      {language === 'ar' ? 'شركة الشحن' : 'Shipping Company'}
                    </span>
                    <span>{order.shipping_company || '-'}</span>
                  </div>

                  {order.shipped_at && (
                    <div className="flex justify-between border-b pb-4">
                      <span className="font-semibold">
                        {language === 'ar' ? 'تاريخ الشحن' : 'Shipped Date'}
                      </span>
                      <span>{new Date(order.shipped_at).toLocaleDateString()}</span>
                    </div>
                  )}

                  {order.delivered_at && (
                    <div className="flex justify-between">
                      <span className="font-semibold">
                        {language === 'ar' ? 'تاريخ التسليم' : 'Delivery Date'}
                      </span>
                      <span>{new Date(order.delivered_at).toLocaleDateString()}</span>
                    </div>
                  )}
                </div>
              </div>
            )}
          </div>

          {/* Order Summary */}
          <div className="lg:col-span-1">
            <div className="bg-white rounded-lg shadow-md p-6 sticky top-20">
              <h2 className="text-2xl font-bold mb-6">
                {language === 'ar' ? 'ملخص الطلب' : 'Order Summary'}
              </h2>

              <div className="space-y-4 mb-6">
                <div className="flex justify-between">
                  <span>{language === 'ar' ? 'رقم الطلب' : 'Order #'}</span>
                  <span className="font-bold">{order.order_number}</span>
                </div>

                <div className="flex justify-between">
                  <span>{language === 'ar' ? 'التاريخ' : 'Date'}</span>
                  <span>{new Date(order.created_at).toLocaleDateString()}</span>
                </div>

                <div className="flex justify-between">
                  <span>{language === 'ar' ? 'عدد المنتجات' : 'Items'}</span>
                  <span className="font-bold">{order.items?.length || 0}</span>
                </div>

                <div className="border-t pt-4 flex justify-between text-lg font-bold">
                  <span>{language === 'ar' ? 'الإجمالي' : 'Total'}</span>
                  <span className="text-green-600">{order.final_price} ر.س</span>
                </div>
              </div>

              {/* Delivery Address */}
              <div className="bg-gray-50 p-4 rounded">
                <h3 className="font-bold mb-2">
                  {language === 'ar' ? 'عنوان التسليم' : 'Delivery Address'}
                </h3>
                <p className="text-sm text-gray-700">
                  {order.delivery_name}<br />
                  {order.delivery_address}<br />
                  {order.delivery_city} {order.delivery_postal_code}
                </p>
              </div>
            </div>
          </div>
        </div>
      ) : null}
    </div>
  );
}
