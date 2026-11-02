import apiClient from '../api/apiClient';

export const useOrderService = () => {
  const fetchOrders = async () => {
    try {
      const response = await apiClient.get('/orders');
      if (Array.isArray(response.data)) {
        return response.data.map(order => formatOrderFromBackend(order)).filter(Boolean);
      }
    } catch (err) {
      console.error('Backend /orders error:', err.message);
    }
    return [];
  };

  const fetchOrderById = async (id) => {
    try {
      const response = await apiClient.get(`/orders/${id}`);
      if (response.data) {
        return formatOrderFromBackend(response.data);
      }
    } catch (err) {
      console.error(`Backend /orders/${id} failed:`, err.message);
    }
    return null;
  };

  const approveOrder = async (id) => {
    return changeOrderStatus(id, 'Preparing');
  };

  const changeOrderStatus = async (id, status, reason = '', notes = '') => {
    try {
      const backendStatus = mapFrontendStatusToBackend(status);
      const payload = {
        order_status: backendStatus,
        rejection_reason: reason || notes,
        notes: notes || reason
      };
      const response = await apiClient.put(`/orders/${id}/status`, payload);
      return { success: true, data: formatOrderFromBackend(response.data) };
    } catch (err) {
      console.error('Backend order status update failed:', err.message);
      return { success: false, message: err.response?.data?.detail || err.message };
    }
  };

  return {
    getOrders: fetchOrders,
    getOrderById: fetchOrderById,
    approveOrder,
    changeOrderStatus,
    updateOrderStatus: changeOrderStatus
  };
};

export function formatOrderFromBackend(order) {
  if (!order || typeof order !== 'object') return null;

  const rawStatus = (order.order_status || order.status || 'PENDING').toUpperCase();
  const safeId = order.id != null ? order.id : Math.floor(Math.random() * 1000);

  const itemsMapped = (order.items || []).map((i, idx) => {
    const medName = i.medicine_name || i.medicine?.brand_name || i.medicine?.generic_name || `Medicine #${i.medicine_id || idx + 1}`;
    const strength = i.strength || i.medicine?.strength || '';
    const unitP = Number(i.unit_price != null ? i.unit_price : (i.price != null ? i.price : 45.0));
    const qty = Number(i.quantity || 1);
    const totalP = Number(i.total_price != null ? i.total_price : (unitP * qty));

    return {
      id: i.id || idx + 1,
      medicineId: i.medicine_id,
      name: strength ? `${medName} (${strength})` : medName,
      medicineName: medName,
      manufacturer: i.manufacturer || i.medicine?.manufacturer || 'Cipla / Sun Pharma',
      strength: strength || 'Standard',
      dosage: i.dosage_form || i.medicine?.dosage_form || 'Tablet',
      quantity: qty,
      unitPrice: unitP,
      unit_price: unitP,
      price: unitP,
      price_per_unit: unitP,
      totalPrice: totalP,
      total_price: totalP,
      priceFormatted: `₹${unitP.toFixed(2)}`,
      totalFormatted: `₹${totalP.toFixed(2)}`,
      imageUrl: i.image_url || i.medicine?.image_url || ''
    };
  });

  const numTotal = Number(order.total_amount != null ? order.total_amount : itemsMapped.reduce((s, it) => s + it.totalPrice, 0));
  const subtotalVal = Number(order.subtotal != null ? order.subtotal : itemsMapped.reduce((s, it) => s + it.totalPrice, numTotal));
  const discountVal = Number(order.discount || 0);
  const deliveryVal = Number(order.delivery_charges || (numTotal > 500 ? 0 : 40));
  const taxVal = Number(order.taxes || Math.round(numTotal * 0.05));

  const pId = order.prescription_id;
  const pImgUrl = order.prescription_image_url || (pId ? `http://localhost:8000/api/v1/prescriptions/${pId}/image` : null);

  return {
    id: safeId,
    orderId: order.order_number || `#ORD-${safeId.toString().padStart(4, '0')}`,
    orderNumber: order.order_number || `#ORD-${safeId.toString().padStart(4, '0')}`,
    customerName: order.customer_name || 'Patient',
    customerPhone: order.customer_phone || '+91 9876543210',
    customerEmail: order.customer_email || 'patient@mediloop.com',
    customerAddress: order.delivery_address || 'Pandharpur, Solapur, Maharashtra - 413304',
    deliveryAddress: order.delivery_address || 'Pandharpur, Solapur, Maharashtra - 413304',
    itemsCount: itemsMapped.length,
    medicineCount: itemsMapped.length,
    total: numTotal,
    total_amount: numTotal,
    numericTotal: numTotal,
    totalAmount: `₹${numTotal.toFixed(2)}`,
    subtotal: subtotalVal,
    discount: discountVal,
    deliveryCharges: deliveryVal,
    taxes: taxVal,
    status: mapBackendStatus(rawStatus),
    backendStatus: rawStatus,
    paymentStatus: order.payment_status || 'PAID',
    paymentMethod: order.payment_method || 'COD',
    date: (order.placed_at || order.created_at) ? new Date(order.placed_at || order.created_at).toLocaleDateString() : 'Today',
    rawDate: order.placed_at || order.created_at,
    prescriptionId: pId,
    prescriptionImageUrl: pImgUrl,
    hasPrescription: Boolean(pId),
    items: itemsMapped,
    medicines: itemsMapped,
    auditEvents: order.audit_events || [],
    rejectionReason: order.rejection_reason || ''
  };
}

export function mapBackendStatus(rawStatus) {
  const upper = (rawStatus || '').toUpperCase();
  if (upper.includes('DELIVER')) return 'Delivered';
  if (upper.includes('OUT_FOR') || upper.includes('DISPATCH')) return 'Out for Delivery';
  if (upper.includes('READY')) return 'Ready for Pickup';
  if (upper.includes('PREPAR') || upper.includes('PACK') || upper.includes('APPROV') || upper.includes('PROCESS')) return 'Preparing';
  if (upper.includes('CANCEL') || upper.includes('REJECT')) return 'Cancelled';
  return 'Pending';
}

export function mapFrontendStatusToBackend(status) {
  const s = (status || '').toLowerCase();
  if (s.includes('deliver')) return 'DELIVERED';
  if (s.includes('out') || s.includes('dispatch')) return 'OUT_FOR_DELIVERY';
  if (s.includes('ready') || s.includes('pickup')) return 'READY';
  if (s.includes('prepar') || s.includes('process') || s.includes('accept')) return 'PREPARING';
  if (s.includes('cancel')) return 'CANCELLED';
  if (s.includes('reject')) return 'REJECTED';
  return 'PENDING_VERIFICATION';
}
