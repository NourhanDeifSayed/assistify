import { useState, useEffect } from 'react';
import { useAppStore } from '../store/appStore';
import { orderService, feedbackService, supportTicketService } from '../api/services';

export default function Dashboard() {
  const { language, setLoading, loading } = useAppStore();
  const [stats, setStats] = useState({
    totalOrders: 0,
    totalRevenue: 0,
    avgRating: 0,
    openTickets: 0,
  });
  const [recentOrders, setRecentOrders] = useState([]);

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      setLoading(true);
      
      const [ordersRes, feedbackRes, ticketsRes] = await Promise.all([
        orderService.getRecent(),
        feedbackService.getAverageRating(),
        supportTicketService.getOpen(),
      ]);

      setRecentOrders(ordersRes.data);
      
      setStats({
        totalOrders: ordersRes.data.length,
        totalRevenue: ordersRes.data.reduce((sum, order) => sum + parseFloat(order.final_price), 0),
        avgRating: feedbackRes.data.average_rating || 0,
        openTickets: ticketsRes.data.length,
      });
    } catch (error) {
      console.error('Error fetching dashboard data:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-4xl font-bold mb-8">
        {language === 'ar' ? 'لوحة التحكم' : 'Dashboard'}
      </h1>

      {loading ? (
        <div className="text-center py-12">
          {language === 'ar' ? 'جاري التحميل...' : 'Loading...'}
        </div>
      ) : (
        <>
          {/* Stats Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-12">
            {/* Total Orders */}
            <div className="bg-white rounded-lg shadow-md p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-gray-600 text-sm">
                    {language === 'ar' ? 'إجمالي الطلبات' : 'Total Orders'}
                  </p>
                  <p className="text-3xl font-bold text-blue-600">{stats.totalOrders}</p>
                </div>
                <span className="text-4xl">📦</span>
              </div>
            </div>

            {/* Total Revenue */}
            <div className="bg-white rounded-lg shadow-md p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-gray-600 text-sm">
                    {language === 'ar' ? 'إجمالي الإيرادات' : 'Total Revenue'}
                  </p>
                  <p className="text-3xl font-bold text-green-600">{stats.totalRevenue.toFixed(2)} ر.س</p>
                </div>
                <span className="text-4xl">💰</span>
              </div>
            </div>

            {/* Average Rating */}
            <div className="bg-white rounded-lg shadow-md p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-gray-600 text-sm">
                    {language === 'ar' ? 'متوسط التقييم' : 'Avg Rating'}
                  </p>
                  <p className="text-3xl font-bold text-yellow-600">
                    {stats.avgRating.toFixed(1)} ⭐
                  </p>
                </div>
                <span className="text-4xl">⭐</span>
              </div>
            </div>

            {/* Open Tickets */}
            <div className="bg-white rounded-lg shadow-md p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-gray-600 text-sm">
                    {language === 'ar' ? 'التذاكر المفتوحة' : 'Open Tickets'}
                  </p>
                  <p className="text-3xl font-bold text-red-600">{stats.openTickets}</p>
                </div>
                <span className="text-4xl">🎫</span>
              </div>
            </div>
          </div>

          {/* Recent Orders */}
          <div className="bg-white rounded-lg shadow-md overflow-hidden">
            <div className="p-6 border-b">
              <h2 className="text-2xl font-bold">
                {language === 'ar' ? 'الطلبات الأخيرة' : 'Recent Orders'}
              </h2>
            </div>

            {recentOrders.length === 0 ? (
              <div className="p-6 text-center text-gray-600">
                {language === 'ar' ? 'لا توجد طلبات' : 'No orders yet'}
              </div>
            ) : (
              <table className="w-full">
                <thead className="bg-gray-100">
                  <tr>
                    <th className="px-6 py-3 text-left text-sm font-semibold">
                      {language === 'ar' ? 'رقم الطلب' : 'Order #'}
                    </th>
                    <th className="px-6 py-3 text-left text-sm font-semibold">
                      {language === 'ar' ? 'العميل' : 'Customer'}
                    </th>
                    <th className="px-6 py-3 text-left text-sm font-semibold">
                      {language === 'ar' ? 'المبلغ' : 'Amount'}
                    </th>
                    <th className="px-6 py-3 text-left text-sm font-semibold">
                      {language === 'ar' ? 'الحالة' : 'Status'}
                    </th>
                    <th className="px-6 py-3 text-left text-sm font-semibold">
                      {language === 'ar' ? 'التاريخ' : 'Date'}
                    </th>
                  </tr>
                </thead>
                <tbody>
                  {recentOrders.map((order) => (
                    <tr key={order.id} className="border-b hover:bg-gray-50">
                      <td className="px-6 py-4 font-mono text-sm">{order.order_number}</td>
                      <td className="px-6 py-4">{order.customer_name}</td>
                      <td className="px-6 py-4 font-bold text-green-600">{order.final_price} ر.س</td>
                      <td className="px-6 py-4">
                        <span className={`px-3 py-1 rounded text-sm font-semibold ${
                          order.status === 'delivered'
                            ? 'bg-green-100 text-green-800'
                            : order.status === 'shipped'
                            ? 'bg-blue-100 text-blue-800'
                            : order.status === 'confirmed'
                            ? 'bg-yellow-100 text-yellow-800'
                            : 'bg-gray-100 text-gray-800'
                        }`}>
                          {order.status_display}
                        </span>
                      </td>
                      <td className="px-6 py-4 text-sm">
                        {new Date(order.created_at).toLocaleDateString()}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </div>
        </>
      )}
    </div>
  );
}
