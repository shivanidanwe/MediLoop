import apiClient from '../api/apiClient';
import { useMockData } from '../context/MockDataContext';

export const useCustomerService = () => {
  const { getCustomers: getMockCustomers } = useMockData();

  const fetchCustomers = async () => {
    try {
      const response = await apiClient.get('/orders');
      if (Array.isArray(response.data) && response.data.length > 0) {
        const customerMap = new Map();
        response.data.forEach(order => {
          const cId = order.customer_id;
          if (!customerMap.has(cId)) {
            customerMap.set(cId, {
              id: cId,
              name: order.customer_name || `Customer #${cId}`,
              email: `customer${cId}@example.com`,
              phone: order.customer_phone || '+91 9876543210',
              address: order.delivery_address || 'Pune, Maharashtra',
              totalOrders: 1,
              lastOrderDate: order.created_at ? new Date(order.created_at).toLocaleDateString() : 'Today'
            });
          } else {
            const existing = customerMap.get(cId);
            existing.totalOrders += 1;
          }
        });
        return Array.from(customerMap.values());
      }
    } catch (err) {
      console.warn('Backend orders for customers check:', err.message);
    }
    return getMockCustomers();
  };

  return {
    getCustomers: fetchCustomers
  };
};
