import apiClient from '../api/apiClient';
import { useMockData } from '../context/MockDataContext';

export const useOrderService = () => {
  const { getOrders: getMockOrders, updateOrderStatus: updateMockOrderStatus } = useMockData();

  const fetchOrders = async () => {
    try {
      const response = await apiClient.get('/orders');
      if (Array.isArray(response.data)) {
        return response.data.map(order => ({
          id: order.id,
          orderId: `#ORD-${order.id.toString().padStart(4, '0')}`,
          customerName: order.customer_name || `Customer #${order.customer_id}`,
          customerPhone: order.customer_phone || '+91 9876543210',
          customerAddress: order.delivery_address || 'Pune, Maharashtra',
          itemsCount: order.items ? order.items.length : 1,
          totalAmount: order.total_amount ? `₹${order.total_amount}` : '₹450',
          numericTotal: order.total_amount || 450,
          status: mapBackendStatus(order.status),
          backendStatus: order.status,
          date: order.created_at ? new Date(order.created_at).toLocaleDateString() : 'Today',
          rawDate: order.created_at,
          paymentMethod: order.payment_method || 'COD',
          items: (order.items || []).map(i => ({
            name: i.medicine_name || `Medicine #${i.medicine_id}`,
            quantity: i.quantity || 1,
            price: i.unit_price ? `₹${i.unit_price}` : '₹100'
          }))
        }));
      }
    } catch (err) {
      console.warn('Backend /orders offline or empty, using mock orders fallback:', err.message);
    }
    return getMockOrders();
  };

  const approveOrder = async (id) => {
    return changeOrderStatus(id, 'Preparing');
  };

  const changeOrderStatus = async (id, status) => {
    try {
      const backendStatus = mapFrontendStatusToBackend(status);
      await apiClient.put(`/orders/${id}/status`, { order_status: backendStatus });
      return { success: true };
    } catch (err) {
      console.warn('Backend order status update failed, updating local state:', err.message);
      updateMockOrderStatus(id, status);
      return { success: true };
    }
  };

  return {
    getOrders: fetchOrders,
    approveOrder,
    updateOrderStatus: changeOrderStatus
  };
};

function mapBackendStatus(status) {
  if (!status) return 'Pending';
  const upper = status.toString().toUpperCase();
  if (upper === 'PENDING' || upper === 'CREATED') return 'Pending';
  if (upper === 'PROCESSING' || upper === 'CONFIRMED' || upper === 'PREPARING') return 'Preparing';
  if (upper === 'DISPATCHED' || upper === 'SHIPPED' || upper === 'OUT_FOR_DELIVERY') return 'Out for Delivery';
  if (upper === 'DELIVERED' || upper === 'COMPLETED') return 'Delivered';
  if (upper === 'CANCELLED' || upper === 'REJECTED') return 'Cancelled';
  return status;
}

function mapFrontendStatusToBackend(status) {
  if (status === 'Pending') return 'PENDING';
  if (status === 'Preparing') return 'PREPARING';
  if (status === 'Out for Delivery') return 'SHIPPED';
  if (status === 'Delivered') return 'DELIVERED';
  if (status === 'Cancelled') return 'CANCELLED';
  return status.toUpperCase();
}
