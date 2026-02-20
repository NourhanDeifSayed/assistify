import React, { useState, useEffect } from 'react';
import { Bell, X, CheckCircle, AlertCircle, Info, Truck, MessageSquare, ShoppingCart, Star, TrendingUp, Settings, Trash2 } from 'lucide-react';

export default function NotificationCenter() {
  const [notifications, setNotifications] = useState([
    {
      id: 1,
      type: 'order',
      title: 'Order Confirmed',
      message: 'Your order #ORD-2024-001 has been confirmed',
      timestamp: new Date(Date.now() - 5 * 60000),
      read: false,
      icon: ShoppingCart,
      color: 'from-green-500 to-green-600',
    },
    {
      id: 2,
      type: 'shipping',
      title: 'Package Shipped',
      message: 'Your order is on the way! Tracking: DHL-2024-001',
      timestamp: new Date(Date.now() - 15 * 60000),
      read: false,
      icon: Truck,
      color: 'from-blue-500 to-blue-600',
    },
    {
      id: 3,
      type: 'message',
      title: 'New Message',
      message: 'AI Agent: Your order will arrive tomorrow!',
      timestamp: new Date(Date.now() - 30 * 60000),
      read: true,
      icon: MessageSquare,
      color: 'from-purple-500 to-purple-600',
    },
    {
      id: 4,
      type: 'feedback',
      title: 'Feedback Request',
      message: 'Please rate your recent purchase',
      timestamp: new Date(Date.now() - 2 * 60 * 60000),
      read: true,
      icon: Star,
      color: 'from-yellow-500 to-yellow-600',
    },
    {
      id: 5,
      type: 'offer',
      title: 'Special Offer',
      message: '15% discount on your next purchase!',
      timestamp: new Date(Date.now() - 4 * 60 * 60000),
      read: true,
      icon: TrendingUp,
      color: 'from-pink-500 to-pink-600',
    },
  ]);

  const [filter, setFilter] = useState('all');
  const [showSettings, setShowSettings] = useState(false);

  const unreadCount = notifications.filter((n) => !n.read).length;

  const filteredNotifications =
    filter === 'all'
      ? notifications
      : notifications.filter((n) => n.type === filter);

  const handleMarkAsRead = (id) => {
    setNotifications((prev) =>
      prev.map((n) => (n.id === id ? { ...n, read: true } : n))
    );
  };

  const handleDelete = (id) => {
    setNotifications((prev) => prev.filter((n) => n.id !== id));
  };

  const handleMarkAllAsRead = () => {
    setNotifications((prev) => prev.map((n) => ({ ...n, read: true })));
  };

  const handleClearAll = () => {
    setNotifications([]);
  };

  const formatTime = (date) => {
    const now = new Date();
    const diff = now - date;
    const minutes = Math.floor(diff / 60000);
    const hours = Math.floor(diff / 3600000);
    const days = Math.floor(diff / 86400000);

    if (minutes < 1) return 'Just now';
    if (minutes < 60) return `${minutes}m ago`;
    if (hours < 24) return `${hours}h ago`;
    if (days < 7) return `${days}d ago`;
    return date.toLocaleDateString();
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-gray-800 to-black p-4 md:p-8">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-4xl md:text-5xl font-bold text-white mb-2">🔔 Notification Center</h1>
            <p className="text-lg text-gray-300">
              {unreadCount} unread notification{unreadCount !== 1 ? 's' : ''}
            </p>
          </div>
          <button
            onClick={() => setShowSettings(!showSettings)}
            className="p-3 bg-gray-800 text-white rounded-lg hover:bg-gray-700 transition"
          >
            <Settings className="w-6 h-6" />
          </button>
        </div>

        {/* Settings Panel */}
        {showSettings && (
          <div className="bg-gray-800 rounded-lg p-6 mb-8">
            <h2 className="text-xl font-bold text-white mb-4">⚙️ Notification Settings</h2>
            <div className="space-y-4">
              {[
                { label: 'Order Updates', enabled: true },
                { label: 'Shipping Alerts', enabled: true },
                { label: 'Messages', enabled: true },
                { label: 'Feedback Requests', enabled: true },
                { label: 'Special Offers', enabled: false },
              ].map((setting, idx) => (
                <div key={idx} className="flex items-center justify-between p-3 bg-gray-700 rounded-lg">
                  <span className="text-gray-200">{setting.label}</span>
                  <input
                    type="checkbox"
                    defaultChecked={setting.enabled}
                    className="w-5 h-5 rounded cursor-pointer"
                  />
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Filter Tabs */}
        <div className="flex gap-2 md:gap-4 mb-8 overflow-x-auto pb-2">
          {['all', 'order', 'shipping', 'message', 'feedback', 'offer'].map((f) => (
            <button
              key={f}
              onClick={() => setFilter(f)}
              className={`px-4 md:px-6 py-2 rounded-lg transition whitespace-nowrap font-semibold ${
                filter === f
                  ? 'bg-gradient-to-r from-blue-500 to-purple-500 text-white'
                  : 'bg-gray-800 text-gray-300 hover:bg-gray-700'
              }`}
            >
              {f.charAt(0).toUpperCase() + f.slice(1)}
            </button>
          ))}
        </div>

        {/* Action Buttons */}
        <div className="flex gap-3 md:gap-4 mb-8">
          <button
            onClick={handleMarkAllAsRead}
            className="flex-1 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition font-semibold"
          >
            ✓ Mark All as Read
          </button>
          <button
            onClick={handleClearAll}
            className="flex-1 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition font-semibold"
          >
            🗑 Clear All
          </button>
        </div>

        {/* Notifications List */}
        <div className="space-y-4">
          {filteredNotifications.length === 0 ? (
            <div className="text-center py-12 bg-gray-800 rounded-lg">
              <Bell className="w-16 h-16 mx-auto mb-4 text-gray-600" />
              <p className="text-gray-400 text-lg">No notifications</p>
            </div>
          ) : (
            filteredNotifications.map((notification) => {
              const Icon = notification.icon;
              return (
                <div
                  key={notification.id}
                  className={`p-4 md:p-6 rounded-lg transition transform hover:scale-102 ${
                    notification.read
                      ? 'bg-gray-800 opacity-75'
                      : 'bg-gradient-to-r from-gray-800 to-gray-700 border-l-4 border-blue-500'
                  }`}
                  onClick={() => handleMarkAsRead(notification.id)}
                >
                  <div className="flex items-start gap-4">
                    {/* Icon */}
                    <div className={`bg-gradient-to-br ${notification.color} p-3 rounded-lg flex-shrink-0`}>
                      <Icon className="w-6 h-6 text-white" />
                    </div>

                    {/* Content */}
                    <div className="flex-1 min-w-0">
                      <div className="flex items-start justify-between gap-2">
                        <div className="flex-1">
                          <h3 className="text-lg font-bold text-white">{notification.title}</h3>
                          <p className="text-gray-300 text-sm md:text-base mt-1">{notification.message}</p>
                        </div>
                        {!notification.read && (
                          <div className="w-3 h-3 bg-blue-500 rounded-full flex-shrink-0 mt-2"></div>
                        )}
                      </div>

                      {/* Timestamp */}
                      <p className="text-gray-500 text-xs md:text-sm mt-3">{formatTime(notification.timestamp)}</p>
                    </div>

                    {/* Actions */}
                    <div className="flex gap-2 flex-shrink-0">
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          handleMarkAsRead(notification.id);
                        }}
                        className="p-2 bg-gray-700 text-gray-300 rounded-lg hover:bg-gray-600 transition"
                        title="Mark as read"
                      >
                        <CheckCircle className="w-5 h-5" />
                      </button>
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          handleDelete(notification.id);
                        }}
                        className="p-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition"
                        title="Delete"
                      >
                        <Trash2 className="w-5 h-5" />
                      </button>
                    </div>
                  </div>
                </div>
              );
            })
          )}
        </div>

        {/* Stats */}
        <div className="mt-12 grid grid-cols-1 md:grid-cols-3 gap-4 md:gap-6">
          <div className="bg-gradient-to-br from-blue-900 to-blue-800 rounded-lg p-6">
            <p className="text-gray-300 text-sm mb-2">Total Notifications</p>
            <p className="text-4xl font-bold text-blue-300">{notifications.length}</p>
          </div>
          <div className="bg-gradient-to-br from-green-900 to-green-800 rounded-lg p-6">
            <p className="text-gray-300 text-sm mb-2">Read</p>
            <p className="text-4xl font-bold text-green-300">{notifications.filter((n) => n.read).length}</p>
          </div>
          <div className="bg-gradient-to-br from-purple-900 to-purple-800 rounded-lg p-6">
            <p className="text-gray-300 text-sm mb-2">Unread</p>
            <p className="text-4xl font-bold text-purple-300">{unreadCount}</p>
          </div>
        </div>
      </div>
    </div>
  );
}
