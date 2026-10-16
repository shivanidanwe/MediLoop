import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  IconButton,
  Tooltip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  Grid,
  Divider,
  Paper
} from '@mui/material';
import VisibilityIcon from '@mui/icons-material/Visibility';
import LocalMallIcon from '@mui/icons-material/LocalMall';
import DescriptionIcon from '@mui/icons-material/Description';
import { useCustomerService } from '../../services/customerService';
import { useMockData } from '../../context/MockDataContext';
import ReusableDataTable from '../../components/tables/ReusableDataTable';

const Customers = () => {
  const { mockEnabled } = useMockData();
  const { getCustomers } = useCustomerService();
  const [loading, setLoading] = useState(true);
  const [customers, setCustomers] = useState([]);
  
  // Dialog state
  const [detailsOpen, setDetailsOpen] = useState(false);
  const [selectedCust, setSelectedCust] = useState(null);

  useEffect(() => {
    const loadCustomers = async () => {
      setLoading(true);
      try {
        const data = await getCustomers();
        setCustomers(data);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    };
    loadCustomers();
  }, [mockEnabled]);

  const handleOpenDetails = (cust) => {
    setSelectedCust(cust);
    setDetailsOpen(true);
  };

  const columns = [
    {
      id: 'name',
      label: 'Customer Name',
      sortable: true,
      render: (row) => <Typography variant="body2" fontWeight={600}>{row.name}</Typography>
    },
    { id: 'phone', label: 'Phone Number', sortable: true },
    { id: 'email', label: 'Email Address', sortable: true },
    { id: 'orders', label: 'Total Orders', sortable: true, align: 'center' },
    { id: 'lastOrder', label: 'Last Order Date', sortable: true },
    {
      id: 'actions',
      label: 'Actions',
      align: 'right',
      render: (row) => (
        <Box display="flex" gap={0.5} justifyContent="flex-end">
          <Tooltip title="View Profile Detail">
            <IconButton color="primary" onClick={() => handleOpenDetails(row)}>
              <VisibilityIcon fontSize="small" />
            </IconButton>
          </Tooltip>
        </Box>
      )
    }
  ];

  return (
    <Box display="flex" flexDirection="column" gap={3}>
      <Box>
        <Typography variant="h4" fontWeight={800} color="text.primary" letterSpacing="-0.5px">
          Customer Directory
        </Typography>
        <Typography variant="body2" color="text.secondary" sx={{ mt: 0.5 }}>
          Browse patient directories, order frequencies, contact profiles, and upload logs.
        </Typography>
      </Box>

      <ReusableDataTable
        columns={columns}
        data={customers}
        searchKey="name"
        searchPlaceholder="Search customer profiles..."
        loading={loading}
        emptyTitle="No customer records"
        emptyDescription="There are no patient/customer files currently indexed in the system."
        onRowClick={handleOpenDetails}
      />

      {/* Customer Profile Details Dialog */}
      <Dialog open={detailsOpen} onClose={() => setDetailsOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle sx={{ fontWeight: 600 }}>Customer Summary Profile</DialogTitle>
        <DialogContent dividers>
          {selectedCust && (
            <Grid container spacing={3}>
              {/* Demographics */}
              <Grid item xs={12}>
                <Typography variant="subtitle2" color="primary" fontWeight={700} gutterBottom>
                  Personal Demographics
                </Typography>
                <Grid container spacing={1}>
                  <Grid item xs={12} sm={6}>
                    <Typography variant="caption" color="text.secondary" display="block">Full Name</Typography>
                    <Typography variant="body2" fontWeight={600}>{selectedCust.name}</Typography>
                  </Grid>
                  <Grid item xs={12} sm={6}>
                    <Typography variant="caption" color="text.secondary" display="block">Customer ID</Typography>
                    <Typography variant="body2" fontWeight={600}>{selectedCust.id}</Typography>
                  </Grid>
                  <Grid item xs={12} sm={6}>
                    <Typography variant="caption" color="text.secondary" display="block">Primary Phone</Typography>
                    <Typography variant="body2" fontWeight={600}>{selectedCust.phone}</Typography>
                  </Grid>
                  <Grid item xs={12} sm={6}>
                    <Typography variant="caption" color="text.secondary" display="block">Email Address</Typography>
                    <Typography variant="body2" fontWeight={600}>{selectedCust.email}</Typography>
                  </Grid>
                </Grid>
              </Grid>

              <Grid item xs={12}>
                <Divider />
              </Grid>

              {/* History summaries */}
              <Grid item xs={12}>
                <Typography variant="subtitle2" color="primary" fontWeight={700} gutterBottom>
                  Purchase & Prescription Logs
                </Typography>
                <Grid container spacing={2} sx={{ mt: 0.5 }}>
                  <Grid item xs={6}>
                    <Paper variant="outlined" sx={{ p: 2, textAlign: 'center', borderRadius: 2 }}>
                      <LocalMallIcon color="action" sx={{ mb: 1 }} />
                      <Typography variant="body2" color="text.secondary">Total Orders</Typography>
                      <Typography variant="h6" fontWeight={700}>{selectedCust.orders}</Typography>
                    </Paper>
                  </Grid>
                  <Grid item xs={6}>
                    <Paper variant="outlined" sx={{ p: 2, textAlign: 'center', borderRadius: 2 }}>
                      <DescriptionIcon color="action" sx={{ mb: 1 }} />
                      <Typography variant="body2" color="text.secondary">Last Ordered</Typography>
                      <Typography variant="body2" fontWeight={700} sx={{ py: 0.3 }}>
                        {selectedCust.lastOrder}
                      </Typography>
                    </Paper>
                  </Grid>
                </Grid>
              </Grid>
            </Grid>
          )}
        </DialogContent>
        <DialogActions sx={{ px: 3, py: 1.5 }}>
          <Button onClick={() => setDetailsOpen(false)} color="primary" variant="contained">
            Close Profile
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default Customers;
