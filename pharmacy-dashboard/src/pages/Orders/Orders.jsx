import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Button,
  Chip,
  Tooltip,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Divider,
  TextField,
  Grid,
  Stack,
  Avatar,
  LinearProgress,
  Menu,
  MenuItem
} from '@mui/material';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import CheckIcon from '@mui/icons-material/Check';
import CloseIcon from '@mui/icons-material/Close';
import LocalShippingIcon from '@mui/icons-material/LocalShipping';
import StoreIcon from '@mui/icons-material/Store';
import VisibilityIcon from '@mui/icons-material/Visibility';
import MedicationIcon from '@mui/icons-material/Medication';
import DescriptionIcon from '@mui/icons-material/Description';
import RefreshIcon from '@mui/icons-material/Refresh';
import LocalMallIcon from '@mui/icons-material/LocalMall';
import TrendingUpIcon from '@mui/icons-material/TrendingUp';
import CurrencyRupeeIcon from '@mui/icons-material/CurrencyRupee';
import AccessTimeIcon from '@mui/icons-material/AccessTime';
import ReceiptLongIcon from '@mui/icons-material/ReceiptLong';
import ArrowDropDownIcon from '@mui/icons-material/ArrowDropDown';
import { useOrderService } from '../../services/orderService';
import ReusableDataTable from '../../components/tables/ReusableDataTable';
import SnackbarNotification from '../../components/common/SnackbarNotification';
import ImageViewer from '../../components/common/ImageViewer';

const Orders = () => {
  const { getOrders, updateOrderStatus } = useOrderService();

  const [loading, setLoading] = useState(true);
  const [orders, setOrders] = useState([]);
  const [toastOpen, setToastOpen] = useState(false);
  const [toastMsg, setToastMsg] = useState('');
  const [selectedOrder, setSelectedOrder] = useState(null);
  const [rejectDialogOpen, setRejectDialogOpen] = useState(false);
  const [rejectOrderId, setRejectOrderId] = useState(null);
  const [rejectionReason, setRejectionReason] = useState('');
  const [statusFilter, setStatusFilter] = useState('All');

  // Prescription Scan Viewer Dialog
  const [rxViewerOpen, setRxViewerOpen] = useState(false);
  const [viewingRxUrl, setViewingRxUrl] = useState('');
  const [viewingRxId, setViewingRxId] = useState(null);

  const fetchOrderList = async () => {
    try {
      const data = await getOrders();
      setOrders(Array.isArray(data) ? data : []);
      // If modal is open, refresh selectedOrder reference
      if (selectedOrder) {
        const found = data.find(o => o.id === selectedOrder.id);
        if (found) setSelectedOrder(found);
      }
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchOrderList();
    const interval = setInterval(() => {
      getOrders().then(data => setOrders(Array.isArray(data) ? data : [])).catch(() => {});
    }, 6000); // 6s periodic polling
    const onFocus = () => fetchOrderList();
    window.addEventListener('focus', onFocus);
    return () => {
      clearInterval(interval);
      window.removeEventListener('focus', onFocus);
    };
  }, []);

  const handleStatusChange = async (id, newStatus, reason = '') => {
    try {
      await updateOrderStatus(id, newStatus, reason);
      setToastMsg(`Order #${id} status updated to: ${newStatus}`);
      setToastOpen(true);
      fetchOrderList();
    } catch (err) {
      console.error(err);
    }
  };

  // Metrics Calculation
  const totalOrders = orders.length;
  const pendingOrders = orders.filter(o => o.status === 'Pending').length;
  const preparingOrders = orders.filter(o => o.status === 'Preparing').length;
  const readyOrders = orders.filter(o => o.status === 'Ready' || o.status === 'Ready for Pickup').length;
  const outOrders = orders.filter(o => o.status === 'Out for Delivery').length;
  const deliveredOrders = orders.filter(o => o.status === 'Delivered').length;

  const fulfillmentRate = totalOrders > 0
    ? Math.round((deliveredOrders / totalOrders) * 100)
    : 100;

  // Filtered dataset by status filter chip
  const filteredOrders = statusFilter === 'All'
    ? orders
    : orders.filter(o => {
        if (statusFilter === 'Ready') return o.status === 'Ready' || o.status === 'Ready for Pickup';
        return o.status === statusFilter;
      });

  const getOrderStatusChip = (status) => {
    switch (status) {
      case 'Pending':
        return (
          <Chip
            label="Pending"
            size="small"
            sx={{
              bgcolor: 'rgba(245, 158, 11, 0.1)',
              color: '#d97706',
              fontWeight: 700,
              fontSize: '0.72rem',
              border: '1px solid rgba(245, 158, 11, 0.25)'
            }}
          />
        );
      case 'Preparing':
        return (
          <Chip
            label="Preparing"
            size="small"
            sx={{
              bgcolor: 'rgba(59, 130, 246, 0.1)',
              color: '#2563eb',
              fontWeight: 700,
              fontSize: '0.72rem',
              border: '1px solid rgba(59, 130, 246, 0.25)'
            }}
          />
        );
      case 'Ready':
      case 'Ready for Pickup':
        return (
          <Chip
            label="Ready for Pickup"
            size="small"
            sx={{
              bgcolor: 'rgba(139, 92, 246, 0.1)',
              color: '#7c3aed',
              fontWeight: 700,
              fontSize: '0.72rem',
              border: '1px solid rgba(139, 92, 246, 0.25)'
            }}
          />
        );
      case 'Out for Delivery':
        return (
          <Chip
            label="Out for Delivery"
            size="small"
            sx={{
              bgcolor: 'rgba(14, 165, 233, 0.1)',
              color: '#0284c7',
              fontWeight: 700,
              fontSize: '0.72rem',
              border: '1px solid rgba(14, 165, 233, 0.25)'
            }}
          />
        );
      case 'Delivered':
        return (
          <Chip
            label="Delivered"
            size="small"
            sx={{
              bgcolor: 'rgba(16, 185, 129, 0.1)',
              color: '#059669',
              fontWeight: 700,
              fontSize: '0.72rem',
              border: '1px solid rgba(16, 185, 129, 0.25)'
            }}
          />
        );
      default:
        return (
          <Chip
            label={status || 'Cancelled'}
            size="small"
            sx={{
              bgcolor: 'rgba(239, 68, 68, 0.1)',
              color: '#dc2626',
              fontWeight: 700,
              fontSize: '0.72rem',
              border: '1px solid rgba(239, 68, 68, 0.25)'
            }}
          />
        );
    }
  };

  const getPrescriptionStatusChip = (prescriptionStatus) => {
    if (prescriptionStatus === 'Verified' || prescriptionStatus === 'Approved') {
      return (
        <Chip
          label="Rx Verified"
          size="small"
          sx={{
            bgcolor: 'rgba(16, 185, 129, 0.08)',
            color: '#059669',
            fontWeight: 700,
            fontSize: '0.7rem',
            border: '1px solid rgba(16, 185, 129, 0.2)'
          }}
        />
      );
    }
    if (prescriptionStatus === 'Rejected') {
      return (
        <Chip
          label="Rx Rejected"
          size="small"
          sx={{
            bgcolor: 'rgba(239, 68, 68, 0.08)',
            color: '#dc2626',
            fontWeight: 700,
            fontSize: '0.7rem',
            border: '1px solid rgba(239, 68, 68, 0.2)'
          }}
        />
      );
    }
    return (
      <Chip
        label="Pending Review"
        size="small"
        sx={{
          bgcolor: 'rgba(245, 158, 11, 0.08)',
          color: '#d97706',
          fontWeight: 700,
          fontSize: '0.7rem',
          border: '1px solid rgba(245, 158, 11, 0.2)'
        }}
      />
    );
  };

  // Precise Button Sizing for Actions
  const renderActionButtons = (row) => {
    const s = row.status;

    return (
      <Box display="flex" gap={1} justifyContent="flex-end" alignItems="center">
        <Tooltip title="View Order Details & Prescribed Items">
          <IconButton
            size="small"
            color="primary"
            onClick={() => setSelectedOrder(row)}
            sx={{
              p: 0.6,
              border: '1px solid #e2e8f0',
              borderRadius: 2,
              '&:hover': { bgcolor: '#f8fafc' }
            }}
          >
            <VisibilityIcon fontSize="small" />
          </IconButton>
        </Tooltip>

        {s === 'Pending' && (
          <>
            <Button
              variant="contained"
              size="small"
              startIcon={<CheckIcon sx={{ fontSize: '14px !important' }} />}
              onClick={() => handleStatusChange(row.id, 'Preparing')}
              sx={{
                borderRadius: 2,
                fontSize: '0.76rem',
                fontWeight: 700,
                py: 0.45,
                px: 1.3,
                textTransform: 'none',
                bgcolor: '#10b981',
                '&:hover': { bgcolor: '#059669' }
              }}
            >
              Accept
            </Button>
            <Button
              variant="outlined"
              color="error"
              size="small"
              startIcon={<CloseIcon sx={{ fontSize: '14px !important' }} />}
              onClick={() => {
                setRejectOrderId(row.id);
                setRejectionReason('');
                setRejectDialogOpen(true);
              }}
              sx={{
                borderRadius: 2,
                fontSize: '0.76rem',
                fontWeight: 700,
                py: 0.45,
                px: 1.3,
                textTransform: 'none'
              }}
            >
              Reject
            </Button>
          </>
        )}
        {s === 'Preparing' && (
          <Button
            variant="contained"
            size="small"
            startIcon={<StoreIcon sx={{ fontSize: '14px !important' }} />}
            onClick={() => handleStatusChange(row.id, 'Ready')}
            sx={{
              borderRadius: 2,
              fontSize: '0.76rem',
              fontWeight: 700,
              py: 0.45,
              px: 1.4,
              textTransform: 'none',
              bgcolor: '#3b82f6',
              '&:hover': { bgcolor: '#2563eb' }
            }}
          >
            Ready
          </Button>
        )}
        {(s === 'Ready' || s === 'Ready for Pickup') && (
          <Box display="flex" gap={0.8}>
            <Button
              variant="contained"
              size="small"
              startIcon={<LocalShippingIcon sx={{ fontSize: '14px !important' }} />}
              onClick={() => handleStatusChange(row.id, 'Out for Delivery')}
              sx={{
                borderRadius: 2,
                fontSize: '0.76rem',
                fontWeight: 700,
                py: 0.45,
                px: 1.2,
                textTransform: 'none',
                bgcolor: '#8b5cf6',
                '&:hover': { bgcolor: '#7c3aed' }
              }}
            >
              Dispatch
            </Button>
            <Button
              variant="outlined"
              size="small"
              startIcon={<CheckCircleIcon sx={{ fontSize: '14px !important' }} />}
              onClick={() => handleStatusChange(row.id, 'Delivered')}
              sx={{
                borderRadius: 2,
                fontSize: '0.76rem',
                fontWeight: 700,
                py: 0.45,
                px: 1.2,
                textTransform: 'none',
                borderColor: '#10b981',
                color: '#059669',
                '&:hover': { bgcolor: 'rgba(16, 185, 129, 0.08)' }
              }}
            >
              Deliver
            </Button>
          </Box>
        )}
        {s === 'Out for Delivery' && (
          <Button
            variant="contained"
            size="small"
            startIcon={<CheckCircleIcon sx={{ fontSize: '14px !important' }} />}
            onClick={() => handleStatusChange(row.id, 'Delivered')}
            sx={{
              borderRadius: 2,
              fontSize: '0.76rem',
              fontWeight: 700,
              py: 0.45,
              px: 1.4,
              textTransform: 'none',
              bgcolor: '#10b981',
              color: '#ffffff',
              '&:hover': { bgcolor: '#059669' }
            }}
          >
            Delivered
          </Button>
        )}
      </Box>
    );
  };

  const columns = [
    {
      id: 'id',
      label: 'Order ID',
      sortable: true,
      render: (row) => (
        <Typography variant="body2" fontWeight={800} color="#059669" sx={{ fontSize: '0.82rem' }}>
          {row.orderId || `#ORD-${row.id}`}
        </Typography>
      )
    },
    {
      id: 'customerName',
      label: 'Customer Details',
      sortable: true,
      render: (row) => {
        const initials = (row.customerName || 'Customer')
          .split(' ')
          .map((n) => n[0])
          .join('')
          .toUpperCase()
          .slice(0, 2);

        return (
          <Stack direction="row" spacing={1.2} alignItems="center">
            <Avatar sx={{ width: 28, height: 28, bgcolor: 'rgba(59, 130, 246, 0.15)', color: '#2563eb', fontSize: '0.75rem', fontWeight: 700 }}>
              {initials}
            </Avatar>
            <Box>
              <Typography variant="body2" fontWeight={700} color="#0f172a" sx={{ fontSize: '0.82rem', lineHeight: 1.1 }}>
                {row.customerName || 'Patient'}
              </Typography>
              <Typography variant="caption" color="text.secondary" sx={{ fontSize: '0.7rem' }}>
                {row.phone || 'Standard Delivery'}
              </Typography>
            </Box>
          </Stack>
        );
      }
    },
    {
      id: 'total',
      label: 'Order Value',
      sortable: true,
      render: (row) => (
        <Typography variant="body2" fontWeight={800} color="#0f172a" sx={{ fontSize: '0.82rem' }}>
          ₹{(Number(row.total || row.total_amount || 0)).toFixed(2)}
        </Typography>
      )
    },
    {
      id: 'medicineCount',
      label: 'Medicines',
      sortable: true,
      align: 'center',
      render: (row) => (
        <Chip
          label={`${row.medicineCount || (row.items ? row.items.length : 1)} items`}
          size="small"
          sx={{ height: 22, fontSize: '0.7rem', fontWeight: 600, bgcolor: '#f1f5f9' }}
        />
      )
    },
    {
      id: 'prescriptionStatus',
      label: 'Rx Verification',
      sortable: true,
      render: (row) => getPrescriptionStatusChip(row.prescriptionStatus)
    },
    {
      id: 'paymentMethod',
      label: 'Payment',
      sortable: true,
      render: (row) => (
        <Chip
          label={row.paymentMethod || 'COD'}
          size="small"
          sx={{ height: 22, fontSize: '0.7rem', fontWeight: 700, bgcolor: '#f8fafc', border: '1px solid #e2e8f0' }}
        />
      )
    },
    {
      id: 'status',
      label: 'Fulfillment Stage',
      sortable: true,
      render: (row) => getOrderStatusChip(row.status)
    },
    {
      id: 'actions',
      label: 'Actions',
      align: 'right',
      render: (row) => renderActionButtons(row)
    }
  ];

  const pipelineCards = [
    { title: 'Total Orders', count: totalOrders, color: '#0f172a', bg: '#f8fafc', border: '#e2e8f0' },
    { title: 'Pending Approval', count: pendingOrders, color: '#f59e0b', bg: 'rgba(245, 158, 11, 0.05)', border: '#fde68a' },
    { title: 'In Preparation', count: preparingOrders, color: '#3b82f6', bg: 'rgba(59, 130, 246, 0.05)', border: '#bfdbfe' },
    { title: 'Ready for Dispatch', count: readyOrders, color: '#8b5cf6', bg: 'rgba(139, 92, 246, 0.05)', border: '#ddd6fe' },
    { title: 'Delivered', count: deliveredOrders, color: '#10b981', bg: 'rgba(16, 185, 129, 0.05)', border: '#a7f3d0' }
  ];

  // Calculate order item breakdown finances
  const calculateFinancials = (order) => {
    if (!order) return { subtotal: 0, discount: 0, delivery: 0, tax: 0, total: 0 };
    const items = order.items || [];
    let itemsSubtotal = 0;
    items.forEach(it => {
      const q = Number(it.quantity) || 1;
      const p = Number(it.unitPrice ?? it.unit_price ?? it.price_per_unit ?? it.price ?? 0);
      const lineTot = Number(it.totalPrice ?? it.total_price ?? (q * p));
      itemsSubtotal += lineTot;
    });

    const finalTotal = Number(order.total || order.total_amount || itemsSubtotal);
    const subtotal = itemsSubtotal > 0 ? itemsSubtotal : finalTotal;
    const discount = order.discount_amount ? Number(order.discount_amount) : 0;
    const delivery = order.delivery_charges ? Number(order.delivery_charges) : 0;
    const tax = Math.max(0, finalTotal - (subtotal - discount + delivery));

    return {
      subtotal: subtotal.toFixed(2),
      discount: discount.toFixed(2),
      delivery: delivery.toFixed(2),
      tax: tax.toFixed(2),
      total: finalTotal.toFixed(2)
    };
  };

  const financials = calculateFinancials(selectedOrder);

  return (
    <Box display="flex" flexDirection="column" gap={2.5}>
      {/* Header Banner */}
      <Box display="flex" justifyContent="space-between" alignItems="center" flexWrap="wrap" gap={2}>
        <Box>
          <Stack direction="row" spacing={1.2} alignItems="center">
            <LocalMallIcon sx={{ fontSize: 28, color: '#3b82f6' }} />
            <Typography variant="h5" fontWeight={800} color="#0f172a" letterSpacing="-0.5px">
              Order Operations
            </Typography>
            <Chip
              label={`${pendingOrders} Action Required`}
              size="small"
              color={pendingOrders > 0 ? 'warning' : 'default'}
              sx={{ fontWeight: 700, fontSize: '0.7rem' }}
            />
          </Stack>
          <Typography variant="body2" color="text.secondary" sx={{ mt: 0.3, fontSize: '0.84rem' }}>
            Fulfill patient orders, verify itemized billing, manage packaging stages, coordinate dispatch, and track live status.
          </Typography>
        </Box>

        <Button
          variant="contained"
          size="small"
          startIcon={<RefreshIcon fontSize="small" />}
          onClick={fetchOrderList}
          sx={{
            borderRadius: 2,
            fontWeight: 700,
            textTransform: 'none',
            fontSize: '0.8rem',
            py: 0.6,
            px: 1.6,
            bgcolor: '#10b981',
            '&:hover': { bgcolor: '#059669' }
          }}
        >
          Refresh Orders
        </Button>
      </Box>

      {/* Visual Order Pipeline Cards & Fulfillment Progress Meter */}
      <Paper elevation={0} sx={{ p: 2.2, borderRadius: 3, border: '1px solid #e2e8f0', bgcolor: '#ffffff' }}>
        <Grid container spacing={1.5} alignItems="center">
          {pipelineCards.map((c) => (
            <Grid item xs={6} sm={2.4} key={c.title}>
              <Box
                sx={{
                  p: 1.5,
                  borderRadius: 2.5,
                  bgcolor: c.bg,
                  border: `1px solid ${c.border}`
                }}
              >
                <Typography variant="caption" sx={{ color: '#64748b', fontWeight: 700, textTransform: 'uppercase', fontSize: '0.66rem', display: 'block' }}>
                  {c.title}
                </Typography>
                <Typography variant="h5" fontWeight={800} sx={{ color: c.color, mt: 0.2 }}>
                  {c.count}
                </Typography>
              </Box>
            </Grid>
          ))}
        </Grid>

        {/* Fulfillment Progress Bar */}
        <Box sx={{ mt: 2, pt: 1.5, borderTop: '1px solid #f1f5f9' }}>
          <Box display="flex" justifyContent="space-between" alignItems="center" mb={0.6}>
            <Stack direction="row" spacing={0.8} alignItems="center">
              <TrendingUpIcon sx={{ fontSize: 16, color: '#3b82f6' }} />
              <Typography variant="caption" fontWeight={700} color="#475569">
                Order Fulfillment Progress
              </Typography>
            </Stack>
            <Typography variant="caption" fontWeight={800} color="#059669">
              {fulfillmentRate}% Completed ({deliveredOrders}/{totalOrders || 1})
            </Typography>
          </Box>
          <LinearProgress
            variant="determinate"
            value={fulfillmentRate}
            sx={{
              height: 7,
              borderRadius: 3.5,
              bgcolor: '#e2e8f0',
              '& .MuiLinearProgress-bar': {
                bgcolor: '#10b981',
                borderRadius: 3.5
              }
            }}
          />
        </Box>
      </Paper>

      {/* Interactive Status Filter Tabs */}
      <Paper elevation={0} sx={{ p: 1.5, borderRadius: 3, border: '1px solid #e2e8f0', bgcolor: '#ffffff' }}>
        <Stack direction="row" spacing={1} flexWrap="wrap">
          {[
            { id: 'All', label: 'All Orders', count: totalOrders },
            { id: 'Pending', label: 'Pending', count: pendingOrders, color: '#f59e0b' },
            { id: 'Preparing', label: 'Preparing', count: preparingOrders, color: '#3b82f6' },
            { id: 'Ready', label: 'Ready for Pickup', count: readyOrders, color: '#8b5cf6' },
            { id: 'Out for Delivery', label: 'Out for Delivery', count: outOrders, color: '#0ea5e9' },
            { id: 'Delivered', label: 'Delivered', count: deliveredOrders, color: '#10b981' }
          ].map((f) => {
            const selected = statusFilter === f.id;
            return (
              <Chip
                key={f.id}
                label={`${f.label} (${f.count})`}
                size="small"
                onClick={() => setStatusFilter(f.id)}
                sx={{
                  fontWeight: 700,
                  fontSize: '0.78rem',
                  cursor: 'pointer',
                  py: 1.8,
                  px: 0.5,
                  borderRadius: 2,
                  bgcolor: selected ? (f.color ? `${f.color}20` : '#0f172a') : '#f8fafc',
                  color: selected ? (f.color || '#ffffff') : '#64748b',
                  border: selected ? `1px solid ${f.color || '#0f172a'}` : '1px solid #e2e8f0',
                  '&:hover': { bgcolor: selected ? undefined : '#f1f5f9' }
                }}
              />
            );
          })}
        </Stack>
      </Paper>

      {/* Structured Reusable Data Table */}
      <ReusableDataTable
        columns={columns}
        data={filteredOrders}
        searchKey="customerName"
        searchPlaceholder="Search customer orders, medicines..."
        loading={loading}
        emptyTitle="No Orders Found"
        emptyDescription="There are no active orders matching this filter."
      />

      {/* Complete Itemized Order Details & Workflow Modal */}
      <Dialog
        open={Boolean(selectedOrder)}
        onClose={() => setSelectedOrder(null)}
        maxWidth="md"
        fullWidth
        PaperProps={{ sx: { borderRadius: 3.5 } }}
      >
        <DialogTitle sx={{ px: 3, py: 2.2, borderBottom: '1px solid #e2e8f0', bgcolor: '#f8fafc' }}>
          <Box display="flex" justifyContent="space-between" alignItems="center">
            <Stack direction="row" spacing={1.5} alignItems="center">
              <ReceiptLongIcon sx={{ color: '#3b82f6', fontSize: 26 }} />
              <Box>
                <Typography variant="h6" fontWeight={800} color="#0f172a">
                  Order {selectedOrder?.orderId || `#ORD-${selectedOrder?.id}`} Manifest
                </Typography>
                <Typography variant="caption" color="text.secondary">
                  Placed on {selectedOrder?.placed_at ? new Date(selectedOrder.placed_at).toLocaleString() : 'Today'}
                </Typography>
              </Box>
              {selectedOrder && getOrderStatusChip(selectedOrder.status)}
            </Stack>
            <IconButton size="small" onClick={() => setSelectedOrder(null)}>
              <CloseIcon fontSize="small" />
            </IconButton>
          </Box>
        </DialogTitle>

        <DialogContent sx={{ p: 3 }}>
          {selectedOrder && (
            <Grid container spacing={3}>
              {/* Customer & Address Card */}
              <Grid item xs={12} sm={6}>
                <Typography variant="caption" fontWeight={800} color="#64748b" sx={{ textTransform: 'uppercase', letterSpacing: 0.5, display: 'block', mb: 1 }}>
                  Customer & Delivery Profile
                </Typography>
                <Paper elevation={0} sx={{ p: 2.2, border: '1px solid #e2e8f0', borderRadius: 2.5, bgcolor: '#f8fafc' }}>
                  <Typography variant="body1" fontWeight={700} color="#0f172a">
                    {selectedOrder.customerName || 'Registered Patient'}
                  </Typography>
                  <Typography variant="body2" color="text.secondary" sx={{ mt: 0.5 }}>
                    Phone: <strong>{selectedOrder.phone || '+91 98450 00000'}</strong>
                  </Typography>
                  <Typography variant="body2" color="text.secondary" sx={{ mt: 0.5 }}>
                    Delivery Address: {selectedOrder.address || selectedOrder.deliveryAddress || 'Pandharpur, Maharashtra'}
                  </Typography>
                  <Divider sx={{ my: 1.5 }} />
                  <Box display="flex" justifyContent="space-between" alignItems="center">
                    <Typography variant="caption" color="text.secondary">
                      Payment Mode:
                    </Typography>
                    <Chip
                      label={selectedOrder.paymentMethod || 'Cash on Delivery (COD)'}
                      size="small"
                      sx={{ fontWeight: 700, fontSize: '0.72rem', bgcolor: 'rgba(16, 185, 129, 0.1)', color: '#059669' }}
                    />
                  </Box>
                </Paper>
              </Grid>

              {/* Prescription Scan & Verification Summary Card */}
              <Grid item xs={12} sm={6}>
                <Typography variant="caption" fontWeight={800} color="#64748b" sx={{ textTransform: 'uppercase', letterSpacing: 0.5, display: 'block', mb: 1 }}>
                  Prescription Evidence & Audit
                </Typography>
                <Paper elevation={0} sx={{ p: 2.2, border: '1px solid #e2e8f0', borderRadius: 2.5, bgcolor: '#f8fafc' }}>
                  <Box display="flex" justifyContent="space-between" alignItems="center" mb={1}>
                    <Typography variant="caption" color="text.secondary">
                      Verification Status:
                    </Typography>
                    {getPrescriptionStatusChip(selectedOrder.prescriptionStatus)}
                  </Box>

                  <Box display="flex" justifyContent="space-between" alignItems="center" mb={1.5}>
                    <Typography variant="caption" color="text.secondary">
                      Prescription Link ID:
                    </Typography>
                    <Typography variant="caption" fontWeight={800} color="#0f172a">
                      #{selectedOrder.prescriptionId || selectedOrder.id || 'N/A'}
                    </Typography>
                  </Box>

                  {/* Button to preview prescription scan */}
                  <Button
                    variant="outlined"
                    size="small"
                    fullWidth
                    startIcon={<DescriptionIcon />}
                    onClick={() => {
                      const imgUrl = selectedOrder.prescription_image_url || `http://localhost:8000/api/v1/prescriptions/${selectedOrder.prescriptionId || selectedOrder.id}/image`;
                      setViewingRxUrl(imgUrl);
                      setViewingRxId(selectedOrder.prescriptionId || selectedOrder.id);
                      setRxViewerOpen(true);
                    }}
                    sx={{
                      borderRadius: 2,
                      textTransform: 'none',
                      fontWeight: 700,
                      borderColor: '#3b82f6',
                      color: '#2563eb',
                      '&:hover': { bgcolor: 'rgba(59, 130, 246, 0.08)' }
                    }}
                  >
                    View Prescription Scan
                  </Button>
                </Paper>
              </Grid>

              {/* Complete Itemized Ordered Medicines Table */}
              <Grid item xs={12}>
                <Typography variant="caption" fontWeight={800} color="#64748b" sx={{ textTransform: 'uppercase', letterSpacing: 0.5, display: 'block', mb: 1 }}>
                  Itemized Medicine Dispensing Table
                </Typography>
                <Paper elevation={0} sx={{ border: '1px solid #e2e8f0', borderRadius: 2.5, overflow: 'hidden' }}>
                  <Table size="small">
                    <TableHead sx={{ bgcolor: '#f8fafc' }}>
                      <TableRow>
                        <TableCell sx={{ fontWeight: 700, fontSize: '0.75rem', py: 1.2 }}>Medicine</TableCell>
                        <TableCell sx={{ fontWeight: 700, fontSize: '0.75rem', py: 1.2 }}>Manufacturer / Brand</TableCell>
                        <TableCell sx={{ fontWeight: 700, fontSize: '0.75rem', py: 1.2 }}>Strength / Form</TableCell>
                        <TableCell sx={{ fontWeight: 700, fontSize: '0.75rem', py: 1.2, textAlign: 'center' }}>Quantity</TableCell>
                        <TableCell sx={{ fontWeight: 700, fontSize: '0.75rem', py: 1.2, textAlign: 'right' }}>Unit Price</TableCell>
                        <TableCell sx={{ fontWeight: 700, fontSize: '0.75rem', py: 1.2, textAlign: 'right' }}>Item Total</TableCell>
                      </TableRow>
                    </TableHead>
                    <TableBody>
                      {selectedOrder.items && selectedOrder.items.length > 0 ? (
                        selectedOrder.items.map((it, idx) => {
                          const qty = Number(it.quantity) || 1;
                          const unitPrice = Number(it.unitPrice ?? it.unit_price ?? it.price_per_unit ?? it.price ?? 0);
                          const lineTotal = Number(it.totalPrice ?? it.total_price ?? (qty * unitPrice)).toFixed(2);

                          return (
                            <TableRow key={idx} sx={{ '&:hover': { bgcolor: '#f8fafc' } }}>
                              <TableCell sx={{ py: 1.2 }}>
                                <Stack direction="row" spacing={1.2} alignItems="center">
                                  <Avatar
                                    src={it.image_url}
                                    sx={{
                                      width: 28,
                                      height: 28,
                                      bgcolor: 'rgba(71, 123, 255, 0.1)',
                                      color: '#477BFF',
                                      fontSize: '0.75rem',
                                      fontWeight: 700
                                    }}
                                  >
                                    <MedicationIcon sx={{ fontSize: 16 }} />
                                  </Avatar>
                                  <Typography variant="body2" fontWeight={700} color="#0f172a">
                                    {it.medicine_name || it.name || 'Prescribed Medicine'}
                                  </Typography>
                                </Stack>
                              </TableCell>
                              <TableCell sx={{ py: 1.2, fontSize: '0.8rem', color: '#475569' }}>
                                {it.manufacturer || it.brand_name || 'Standard Pharma'}
                              </TableCell>
                              <TableCell sx={{ py: 1.2, fontSize: '0.8rem', color: '#475569' }}>
                                {it.strength || it.dosage_form || 'Standard'}
                              </TableCell>
                              <TableCell sx={{ py: 1.2, textAlign: 'center' }}>
                                <Chip
                                  label={`${qty} units`}
                                  size="small"
                                  sx={{ height: 22, fontSize: '0.72rem', fontWeight: 700, bgcolor: '#f1f5f9' }}
                                />
                              </TableCell>
                              <TableCell sx={{ py: 1.2, textAlign: 'right', fontWeight: 600, fontSize: '0.82rem' }}>
                                ₹{unitPrice.toFixed(2)}
                              </TableCell>
                              <TableCell sx={{ py: 1.2, textAlign: 'right', fontWeight: 800, fontSize: '0.84rem', color: '#0f172a' }}>
                                ₹{lineTotal}
                              </TableCell>
                            </TableRow>
                          );
                        })
                      ) : (
                        <TableRow>
                          <TableCell colSpan={6} align="center" sx={{ py: 2.5, color: 'text.secondary' }}>
                            Standard Clinical Package (1 unit) — ₹{(Number(selectedOrder.total || 0)).toFixed(2)}
                          </TableCell>
                        </TableRow>
                      )}
                    </TableBody>
                  </Table>
                </Paper>
              </Grid>

              {/* Financial Calculation Breakdown Table */}
              <Grid item xs={12}>
                <Paper elevation={0} sx={{ p: 2.2, border: '1px solid #e2e8f0', borderRadius: 2.5, bgcolor: '#f8fafc' }}>
                  <Grid container spacing={2}>
                    <Grid item xs={12} sm={7}>
                      <Typography variant="caption" fontWeight={800} color="#64748b" sx={{ textTransform: 'uppercase', display: 'block', mb: 0.5 }}>
                        Fulfillment Stage Transition
                      </Typography>
                      <Typography variant="body2" color="text.secondary" sx={{ fontSize: '0.82rem' }}>
                        Advance order stages according to pharmacy workflow. Transitions are audited in PostgreSQL.
                      </Typography>
                    </Grid>
                    <Grid item xs={12} sm={5}>
                      <Stack spacing={0.8}>
                        <Box display="flex" justifyContent="space-between">
                          <Typography variant="caption" color="text.secondary">Items Subtotal:</Typography>
                          <Typography variant="caption" fontWeight={700}>₹{financials.subtotal}</Typography>
                        </Box>
                        <Box display="flex" justifyContent="space-between">
                          <Typography variant="caption" color="text.secondary">Applied Discount:</Typography>
                          <Typography variant="caption" fontWeight={700} color="#059669">-₹{financials.discount}</Typography>
                        </Box>
                        <Box display="flex" justifyContent="space-between">
                          <Typography variant="caption" color="text.secondary">Delivery Charges:</Typography>
                          <Typography variant="caption" fontWeight={700}>₹{financials.delivery}</Typography>
                        </Box>
                        <Box display="flex" justifyContent="space-between">
                          <Typography variant="caption" color="text.secondary">Estimated Taxes / GST:</Typography>
                          <Typography variant="caption" fontWeight={700}>₹{financials.tax}</Typography>
                        </Box>
                        <Divider sx={{ my: 0.5 }} />
                        <Box display="flex" justifyContent="space-between" alignItems="center">
                          <Typography variant="subtitle2" fontWeight={800} color="#0f172a">
                            Final Total Order Amount:
                          </Typography>
                          <Typography variant="h6" fontWeight={800} color="#059669">
                            ₹{financials.total}
                          </Typography>
                        </Box>
                      </Stack>
                    </Grid>
                  </Grid>
                </Paper>
              </Grid>
            </Grid>
          )}
        </DialogContent>

        <DialogActions sx={{ px: 3, py: 2, borderTop: '1px solid #e2e8f0', bgcolor: '#f8fafc', justifyContent: 'space-between' }}>
          <Button size="small" onClick={() => setSelectedOrder(null)} sx={{ fontWeight: 600, fontSize: '0.8rem' }}>
            Close
          </Button>

          {/* Quick status transition actions inside modal */}
          {selectedOrder && (
            <Box display="flex" gap={1.2}>
              {selectedOrder.status === 'Pending' && (
                <>
                  <Button
                    variant="outlined"
                    color="error"
                    size="small"
                    onClick={() => {
                      setRejectOrderId(selectedOrder.id);
                      setRejectionReason('');
                      setRejectDialogOpen(true);
                    }}
                    sx={{ borderRadius: 2, textTransform: 'none', fontWeight: 700 }}
                  >
                    Reject Order
                  </Button>
                  <Button
                    variant="contained"
                    size="small"
                    onClick={() => handleStatusChange(selectedOrder.id, 'Preparing')}
                    sx={{ borderRadius: 2, textTransform: 'none', fontWeight: 700, bgcolor: '#10b981', '&:hover': { bgcolor: '#059669' } }}
                  >
                    Accept & Prepare
                  </Button>
                </>
              )}
              {selectedOrder.status === 'Preparing' && (
                <Button
                  variant="contained"
                  size="small"
                  onClick={() => handleStatusChange(selectedOrder.id, 'Ready')}
                  sx={{ borderRadius: 2, textTransform: 'none', fontWeight: 700, bgcolor: '#3b82f6', '&:hover': { bgcolor: '#2563eb' } }}
                >
                  Mark Ready for Pickup
                </Button>
              )}
              {(selectedOrder.status === 'Ready' || selectedOrder.status === 'Ready for Pickup') && (
                <>
                  <Button
                    variant="contained"
                    size="small"
                    onClick={() => handleStatusChange(selectedOrder.id, 'Out for Delivery')}
                    sx={{ borderRadius: 2, textTransform: 'none', fontWeight: 700, bgcolor: '#8b5cf6', '&:hover': { bgcolor: '#7c3aed' } }}
                  >
                    Dispatch for Delivery
                  </Button>
                  <Button
                    variant="outlined"
                    size="small"
                    onClick={() => handleStatusChange(selectedOrder.id, 'Delivered')}
                    sx={{ borderRadius: 2, textTransform: 'none', fontWeight: 700, borderColor: '#10b981', color: '#059669' }}
                  >
                    Deliver to Customer
                  </Button>
                </>
              )}
              {selectedOrder.status === 'Out for Delivery' && (
                <Button
                  variant="contained"
                  size="small"
                  onClick={() => handleStatusChange(selectedOrder.id, 'Delivered')}
                  sx={{ borderRadius: 2, textTransform: 'none', fontWeight: 700, bgcolor: '#10b981', '&:hover': { bgcolor: '#059669' } }}
                >
                  Confirm Delivery
                </Button>
              )}
              {selectedOrder.status === 'Delivered' && (
                <Chip label="Order Fully Delivered" color="success" sx={{ fontWeight: 700 }} />
              )}
            </Box>
          )}
        </DialogActions>
      </Dialog>

      {/* Linked Prescription Preview Dialog */}
      <Dialog
        open={rxViewerOpen}
        onClose={() => setRxViewerOpen(false)}
        maxWidth="md"
        fullWidth
        PaperProps={{ sx: { borderRadius: 3 } }}
      >
        <DialogTitle sx={{ px: 3, py: 1.8, borderBottom: '1px solid #e2e8f0', bgcolor: '#f8fafc', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <Typography variant="subtitle1" fontWeight={800} color="#0f172a">
            Prescription Document Scan #{viewingRxId}
          </Typography>
          <IconButton size="small" onClick={() => setRxViewerOpen(false)}>
            <CloseIcon fontSize="small" />
          </IconButton>
        </DialogTitle>
        <DialogContent sx={{ p: 2 }}>
          <Box sx={{ height: 500, width: '100%' }}>
            <ImageViewer
              imageUrl={viewingRxUrl}
              prescriptionId={viewingRxId}
              alt={`Prescription Scan #${viewingRxId}`}
            />
          </Box>
        </DialogContent>
      </Dialog>

      {/* Reject Order Dialog */}
      <Dialog
        open={rejectDialogOpen}
        onClose={() => setRejectDialogOpen(false)}
        maxWidth="xs"
        fullWidth
        PaperProps={{ sx: { borderRadius: 3 } }}
      >
        <DialogTitle sx={{ fontWeight: 800, color: '#dc2626' }}>
          Reject Order #{rejectOrderId}
        </DialogTitle>
        <DialogContent>
          <Typography variant="body2" color="text.secondary" mb={2}>
            Mandatory rejection explanation recorded in the audit trail:
          </Typography>
          <TextField
            fullWidth
            multiline
            rows={3}
            size="small"
            label="Rejection Reason"
            placeholder="e.g. Out of stock, invalid delivery address, or physician clarification required..."
            value={rejectionReason}
            onChange={(e) => setRejectionReason(e.target.value)}
            InputProps={{ style: { borderRadius: 8, fontSize: '0.82rem' } }}
          />
        </DialogContent>
        <DialogActions sx={{ px: 3, py: 1.8 }}>
          <Button size="small" onClick={() => setRejectDialogOpen(false)} sx={{ fontWeight: 600 }}>
            Cancel
          </Button>
          <Button
            variant="contained"
            color="error"
            size="small"
            disabled={!rejectionReason.trim()}
            onClick={() => {
              handleStatusChange(rejectOrderId, 'Cancelled', rejectionReason);
              setRejectDialogOpen(false);
            }}
            sx={{ borderRadius: 2, fontWeight: 700, px: 2 }}
          >
            Confirm Rejection
          </Button>
        </DialogActions>
      </Dialog>

      <SnackbarNotification
        open={toastOpen}
        message={toastMsg}
        severity="success"
        onClose={() => setToastOpen(false)}
      />
    </Box>
  );
};

export default Orders;
