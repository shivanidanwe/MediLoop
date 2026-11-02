import apiClient from '../api/apiClient';

export const useCustomerService = () => {
  const fetchCustomers = async () => {
    // 1. Dedicated customer endpoint
    try {
      const response = await apiClient.get('/pharmacies/customers');
      if (Array.isArray(response.data) && response.data.length > 0) {
        return response.data.map(c => ({
          id: c.id,
          name: c.name || c.full_name || 'Customer',
          email: c.email || '',
          phone: c.phone || c.mobile_number || '+91 9876543210',
          address: c.address || 'Pandharpur, Maharashtra',
          orders: c.orders != null ? c.orders : (c.total_orders || 0),
          totalOrders: c.total_orders != null ? c.total_orders : (c.orders || 0),
          lastOrder: c.last_order || (c.last_order_date ? new Date(c.last_order_date).toISOString().split('T')[0] : 'N/A'),
          lastOrderDate: c.last_order || (c.last_order_date ? new Date(c.last_order_date).toISOString().split('T')[0] : 'N/A')
        }));
      }
    } catch (err) {
      // Aggregate from real orders
    }

    // 2. Real-time aggregation directly from database orders
    try {
      const response = await apiClient.get('/orders');
      if (Array.isArray(response.data) && response.data.length > 0) {
        const customerMap = new Map();
        response.data.forEach(order => {
          const cId = order.customer_id;
          const orderDate = order.placed_at || order.created_at;
          const formattedDate = orderDate ? new Date(orderDate).toISOString().split('T')[0] : 'N/A';
          const orderTimestamp = orderDate ? new Date(orderDate).getTime() : 0;

          if (!customerMap.has(cId)) {
            customerMap.set(cId, {
              id: cId,
              name: order.customer_name || 'Customer',
              email: order.customer_email || `customer${cId}@example.com`,
              phone: order.customer_phone || '+91 9876543210',
              address: order.delivery_address || 'Pandharpur, Maharashtra',
              orders: 1,
              totalOrders: 1,
              lastOrder: formattedDate,
              lastOrderDate: formattedDate,
              _latestTimestamp: orderTimestamp
            });
          } else {
            const existing = customerMap.get(cId);
            existing.orders += 1;
            existing.totalOrders += 1;
            if (order.customer_name && (!existing.name || existing.name === 'Customer')) {
              existing.name = order.customer_name;
            }
            if (order.customer_phone) existing.phone = order.customer_phone;
            if (order.customer_email) existing.email = order.customer_email;
            if (order.delivery_address) existing.address = order.delivery_address;
            if (orderTimestamp > existing._latestTimestamp) {
              existing._latestTimestamp = orderTimestamp;
              existing.lastOrder = formattedDate;
              existing.lastOrderDate = formattedDate;
            }
          }
        });
        return Array.from(customerMap.values());
      }
    } catch (err) {
      console.error('Backend orders for customers check:', err.message);
    }
    return [];
  };

  return {
    getCustomers: fetchCustomers
  };
};
