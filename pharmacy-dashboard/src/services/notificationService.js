import apiClient from '../api/apiClient';

export const useNotificationService = () => {
  const fetchNotifications = async (limit = 50, category = null) => {
    try {
      const url = category ? `/notifications?limit=${limit}&category=${category}` : `/notifications?limit=${limit}`;
      const response = await apiClient.get(url);
      if (Array.isArray(response.data)) {
        return response.data.map(formatNotificationFromBackend);
      }
    } catch (err) {
      console.error('Backend /notifications error:', err.message);
    }
    return [];
  };

  const fetchUnreadCount = async () => {
    try {
      const response = await apiClient.get('/notifications/unread-count');
      return response.data?.unread_count || 0;
    } catch (err) {
      return 0;
    }
  };

  const markAsRead = async (id) => {
    try {
      await apiClient.put(`/notifications/${id}/read`);
      return { success: true };
    } catch (err) {
      return { success: false, message: err.message };
    }
  };

  const markAllAsRead = async () => {
    try {
      await apiClient.post('/notifications/mark-all-read');
      return { success: true };
    } catch (err) {
      return { success: false, message: err.message };
    }
  };

  const fetchPreferences = async () => {
    try {
      const res = await apiClient.get('/notifications/preferences');
      return res.data;
    } catch (err) {
      return {
        new_prescription: true,
        new_orders: true,
        low_stock: true,
        out_of_stock: true,
        new_stock: true,
        expiry_alerts: true,
        order_updates: true,
        sound_enabled: true
      };
    }
  };

  const savePreferences = async (preferences) => {
    try {
      const res = await apiClient.put('/notifications/preferences', preferences);
      return { success: true, data: res.data };
    } catch (err) {
      return { success: false, message: err.message };
    }
  };

  return {
    getNotifications: fetchNotifications,
    getUnreadCount: fetchUnreadCount,
    markAsRead,
    markAllAsRead,
    getPreferences: fetchPreferences,
    savePreferences
  };
};

export function formatNotificationFromBackend(n) {
  const type = (n.notification_type || 'SYSTEM').toUpperCase();
  let category = 'system';
  if (type.includes('PRESCRIPTION')) category = 'prescription';
  else if (type.includes('ORDER')) category = 'order';
  else if (type.includes('STOCK') || type.includes('EXPIRY') || type.includes('CATALOGUE')) category = 'inventory';

  const d = n.created_at ? new Date(n.created_at) : new Date();
  const timeFormatted = d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  const dateFormatted = d.toLocaleDateString([], { month: 'short', day: 'numeric' });

  return {
    id: n.id,
    title: n.title || 'Dispensary Alert',
    message: n.message || n.content || '',
    type: type,
    category: category,
    read: n.is_read || false,
    isRead: n.is_read || false,
    actionUrl: n.action_url || (category === 'prescription' ? '/prescriptions' : (category === 'order' ? '/orders' : '/medicines')),
    timestamp: `${dateFormatted}, ${timeFormatted}`,
    rawDate: n.created_at
  };
}
