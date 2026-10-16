import React, { useState, useEffect } from 'react';
import { Box, Typography, Button, ButtonGroup, Chip, Tooltip } from '@mui/material';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import CheckIcon from '@mui/icons-material/Check';
import CloseIcon from '@mui/icons-material/Close';
import LocalShippingIcon from '@mui/icons-material/LocalShipping';
import StoreIcon from '@mui/icons-material/Store';
import PlayArrowIcon from '@mui/icons-material/PlayArrow';
import { useOrderService } from '../../services/orderService';
import { useMockData } from '../../context/MockDataContext';
import ReusableDataTable from '../../components/tables/ReusableDataTable';
import SnackbarNotification from '../../components/common/SnackbarNotification';

const Orders = () => {
  const { mockEnabled } = useMockData();
  const { getOrders, updateOrderStatus } = useOrderService();
  
  const [loading, setLoading] = useState(true);
  const [orders, setOrders] = useState([]);
  const [toastOpen, setToastOpen] = useState(false);
  const [toastMsg, setToastMsg] = useState('');

  const fetchOrderList = async () => {
    setLoading(true);
    try {
      const data = await getOrders();
      setOrders(data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchOrderList();
  }, [mockEnabled]);

  const handleStatusChange = async (id, newStatus) => {
    try {
      await updateOrderStatus(id, newStatus);
      setToastMsg(`Order ${id} status updated to: ${newStatus}`);
      setToastOpen(true);
      fetchOrderList(); // Reload lists to show updated values
    } catch (err) {
      console.error(err);
    }
  };

  const getOrderStatusChip = (status) => {
    switch (status) {
      case 'Pending':
        return <Chip label="Pending" size="small" sx={{ bgcolor: 'warning.lightBg', color: 'warning.main', fontWeight: 600 }} />;
      case 'Preparing':
        return <Chip label="Preparing" size="small" sx={{ bgcolor: 'info.lightBg', color: 'info.main', fontWeight: 600 }} />;
      case 'Ready':
        return <Chip label="Ready" size="small" sx={{ bgcolor: 'success.lightBg', color: 'success.main', fontWeight: 600 }} />;
      case 'Out for Delivery':
        return <Chip label="Out for Delivery" size="small" sx={{ bgcolor: 'secondary.lightBg', color: 'secondary.main', fontWeight: 600 }} />;
      case 'Delivered':
        return <Chip label="Delivered" size="small" sx={{ bgcolor: 'success.main', color: '#ffffff', fontWeight: 600 }} />;
      default:
        return <Chip label="Cancelled" size="small" sx={{ bgcolor: 'error.lightBg', color: 'error.main', fontWeight: 600 }} />;
    }
  };

  const getPrescriptionStatusChip = (prescriptionStatus) => {
    if (prescriptionStatus === 'Verified') {
      return <Chip label="Verified" size="small" color="success" variant="outlined" sx={{ fontWeight: 500 }} />;
    }
    if (prescriptionStatus === 'Rejected') {
      return <Chip label="Rejected" size="small" color="error" variant="outlined" sx={{ fontWeight: 500 }} />;
    }
    return <Chip label="Pending Review" size="small" color="warning" variant="outlined" sx={{ fontWeight: 500 }} />;
  };

  const renderActionButtons = (row) => {
    const s = row.status;
    if (s === 'Cancelled' || s === 'Delivered') return <Typography variant="caption" color="text.secondary">No Actions</Typography>;

    return (
      <Box display="flex" gap={1} justifyContent="flex-end">
        {s === 'Pending' && (
          <>
            <Tooltip title="Accept Order">
              <Button
                variant="outlined"
                color="primary"
                size="small"
                startIcon={<CheckIcon />}
                onClick={() => handleStatusChange(row.id, 'Preparing')}
                sx={{ borderRadius: 2 }}
              >
                Accept
              </Button>
            </Tooltip>
            <Tooltip title="Cancel Order">
              <Button
                variant="outlined"
                color="error"
                size="small"
                startIcon={<CloseIcon />}
                onClick={() => handleStatusChange(row.id, 'Cancelled')}
                sx={{ borderRadius: 2 }}
              >
                Cancel
              </Button>
            </Tooltip>
          </>
        )}
        {s === 'Preparing' && (
          <Tooltip title="Set Ready for Pickup">
            <Button
              variant="contained"
              color="primary"
              size="small"
              startIcon={<StoreIcon />}
              onClick={() => handleStatusChange(row.id, 'Ready')}
              sx={{ borderRadius: 2, boxShadow: 'none' }}
            >
              Ready
            </Button>
          </Tooltip>
        )}
        {s === 'Ready' && (
          <Tooltip title="Dispatch with Courier">
            <Button
              variant="contained"
              color="secondary"
              size="small"
              startIcon={<LocalShippingIcon />}
              onClick={() => handleStatusChange(row.id, 'Out for Delivery')}
              sx={{ borderRadius: 2, boxShadow: 'none' }}
            >
              Dispatch
            </Button>
          </Tooltip>
        )}
        {s === 'Out for Delivery' && (
          <Tooltip title="Mark Order Delivered">
            <Button
              variant="contained"
              color="success"
              size="small"
              startIcon={<CheckCircleIcon />}
              onClick={() => handleStatusChange(row.id, 'Delivered')}
              sx={{ borderRadius: 2, boxShadow: 'none', color: '#ffffff' }}
            >
              Delivered
            </Button>
          </Tooltip>
        )}
      </Box>
    );
  };

  const columns = [
    { id: 'id', label: 'Order ID', sortable: true },
    {
      id: 'customerName',
      label: 'Customer Name',
      sortable: true,
      render: (row) => <Typography variant="body2" fontWeight={600}>{row.customerName}</Typography>
    },
    { id: 'medicineCount', label: 'Medicine Count', sortable: true, align: 'center' },
    {
      id: 'prescriptionStatus',
      label: 'Prescription Status',
      sortable: true,
      render: (row) => getPrescriptionStatusChip(row.prescriptionStatus)
    },
    { id: 'paymentMethod', label: 'Payment Method', sortable: true },
    {
      id: 'status',
      label: 'Order Status',
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

  return (
    <Box display="flex" flexDirection="column" gap={3}>
      <Box>
        <Typography variant="h4" fontWeight={800} color="text.primary" letterSpacing="-0.5px">
          Order Operations
        </Typography>
        <Typography variant="body2" color="text.secondary" sx={{ mt: 0.5 }}>
          Monitor customer medication order statuses, dispatch details, and packaging stages.
        </Typography>
      </Box>

      <ReusableDataTable
        columns={columns}
        data={orders}
        searchKey="customerName"
        searchPlaceholder="Search customer orders..."
        filterOptions={[
          { key: 'status', label: 'Order Status', options: ['Pending', 'Preparing', 'Ready', 'Out for Delivery', 'Delivered', 'Cancelled'] }
        ]}
        loading={loading}
        emptyTitle="No Orders Found"
        emptyDescription="No orders available."
      />

      <SnackbarNotification
        open={toastOpen}
        message={toastMsg}
        onClose={() => setToastOpen(false)}
      />
    </Box>
  );
};

export default Orders;
