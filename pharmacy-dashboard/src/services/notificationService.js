import apiClient from '../api/apiClient';
import { useMockData } from '../context/MockDataContext';

export const useNotificationService = () => {
  const { getNotifications: getMockNotifications, markNotificationRead: markMockRead } = useMockData();

  const fetchNotifications = async () => {
    try {
      const response = await apiClient.get('/notifications');
      if (Array.isArray(response.data) && response.data.length > 0) {
        return response.data.map((n, idx) => ({
          id: n.id || idx + 1,
          title: n.title || 'System Notification',
          message: n.message || n.content || 'New update available.',
          timestamp: n.created_at ? new Date(n.created_at).toLocaleTimeString() : 'Just now',
          read: n.is_read || false,
          type: n.type || 'info'
        }));
      }
    } catch (err) {
      console.warn('Backend /notifications endpoint check:', err.message);
    }
    return getMockNotifications();
  };

  const markAsRead = async (id) => {
    try {
      await apiClient.put(`/notifications/${id}/read`);
      return { success: true };
    } catch (err) {
      markMockRead(id);
      return { success: true };
    }
  };

  return {
    getNotifications: fetchNotifications,
    markAsRead
  };
};
