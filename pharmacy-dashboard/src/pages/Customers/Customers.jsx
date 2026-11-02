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
  Paper,
  Card,
  CardContent,
  Avatar,
  Chip,
  Stack
} from '@mui/material';
import VisibilityIcon from '@mui/icons-material/Visibility';
import LocalMallIcon from '@mui/icons-material/LocalMall';
import DescriptionIcon from '@mui/icons-material/Description';
import PeopleAltIcon from '@mui/icons-material/PeopleAlt';
import RepeatIcon from '@mui/icons-material/Repeat';
import PersonAddAlt1Icon from '@mui/icons-material/PersonAddAlt1';
import PhoneIcon from '@mui/icons-material/Phone';
import EmailIcon from '@mui/icons-material/Email';
import LocationOnIcon from '@mui/icons-material/LocationOn';
import CloseIcon from '@mui/icons-material/Close';
import { useCustomerService } from '../../services/customerService';
import { useMockData } from '../../context/MockDataContext';
import ReusableDataTable from '../../components/tables/ReusableDataTable';

const getInitials = (name) => {
  if (!name) return 'PT';
  const parts = name.trim().split(' ');
  if (parts.length === 1) return parts[0].substring(0, 2).toUpperCase();
  return (parts[0][0] + parts[parts.length - 1][0]).toUpperCase();
};

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
        setCustomers(Array.isArray(data) ? data : []);
      } catch (err) {
        console.error('Failed to load customers:', err);
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

  // Compute directory metrics
  const totalCount = customers.length;
  const activeCount = customers.filter(c => (c.orders ?? c.totalOrders ?? 0) > 1).length;
  const newCount = customers.filter(c => (c.orders ?? c.totalOrders ?? 0) <= 1).length;
  const totalOrdersSum = customers.reduce((acc, c) => acc + (c.orders ?? c.totalOrders ?? 0), 0);

  const kpis = [
    {
      title: 'Total Patients',
      value: totalCount,
      icon: <PeopleAltIcon sx={{ fontSize: 24 }} />,
      color: '#3b82f6',
      bg: 'rgba(59, 130, 246, 0.1)',
      subtext: 'Registered mobile accounts'
    },
    {
      title: 'Active Re-orderers',
      value: activeCount,
      icon: <RepeatIcon sx={{ fontSize: 24 }} />,
      color: '#10b981',
      bg: 'rgba(16, 185, 129, 0.1)',
      subtext: 'Multiple orders placed'
    },
    {
      title: 'New Patients',
      value: newCount,
      icon: <PersonAddAlt1Icon sx={{ fontSize: 24 }} />,
      color: '#f59e0b',
      bg: 'rgba(245, 158, 11, 0.1)',
      subtext: 'First-time customers'
    },
    {
      title: 'Cumulative Orders',
      value: totalOrdersSum,
      icon: <LocalMallIcon sx={{ fontSize: 24 }} />,
      color: '#8b5cf6',
      bg: 'rgba(139, 92, 246, 0.1)',
      subtext: 'Dispensary sales volume'
    }
  ];

  const columns = [
    {
      id: 'name',
      label: 'Patient Name',
      sortable: true,
      render: (row) => (
        <Box display="flex" alignItems="center" gap={1.5}>
          <Avatar
            sx={{
              bgcolor: 'rgba(16, 185, 129, 0.15)',
              color: '#059669',
              fontWeight: 700,
              fontSize: '0.82rem',
              width: 36,
              height: 36,
              border: '1.5px solid rgba(16, 185, 129, 0.3)'
            }}
          >
            {getInitials(row.name)}
          </Avatar>
          <Box>
            <Typography variant="body2" fontWeight={700} color="text.primary">
              {row.name}
            </Typography>
            <Typography variant="caption" color="text.secondary" sx={{ display: 'block', fontSize: '0.72rem' }}>
              ID: #{row.id || 'N/A'}
            </Typography>
          </Box>
        </Box>
      )
    },
    { 
      id: 'phone', 
      label: 'Phone Contact', 
      sortable: true,
      render: (row) => (
        <Box display="flex" alignItems="center" gap={0.8}>
          <PhoneIcon sx={{ fontSize: 16, color: 'text.secondary' }} />
          <Typography variant="body2" sx={{ fontFamily: 'monospace', fontSize: '0.8rem' }}>
            {row.phone || 'N/A'}
          </Typography>
        </Box>
      )
    },
    { 
      id: 'email', 
      label: 'Email Address', 
      sortable: true,
      render: (row) => (
        <Box display="flex" alignItems="center" gap={0.8}>
          <EmailIcon sx={{ fontSize: 16, color: 'text.secondary' }} />
          <Typography variant="body2" color="text.secondary" sx={{ fontSize: '0.8rem' }}>
            {row.email || 'N/A'}
          </Typography>
        </Box>
      )
    },
    { 
      id: 'orders', 
      label: 'Total Orders', 
      sortable: true, 
      align: 'center',
      render: (row) => {
        const count = row.orders ?? row.totalOrders ?? 0;
        return (
          <Chip
            label={`${count} ${count === 1 ? 'order' : 'orders'}`}
            size="small"
            sx={{
              fontWeight: 700,
              fontSize: '0.75rem',
              bgcolor: count > 2 ? 'rgba(16, 185, 129, 0.12)' : 'rgba(59, 130, 246, 0.1)',
              color: count > 2 ? '#059669' : '#2563eb',
              border: '1px solid',
              borderColor: count > 2 ? 'rgba(16, 185, 129, 0.3)' : 'rgba(59, 130, 246, 0.25)'
            }}
          />
        );
      }
    },
    { 
      id: 'lastOrder', 
      label: 'Last Order Date', 
      sortable: true,
      render: (row) => (
        <Typography variant="body2" color="text.secondary" sx={{ fontSize: '0.8rem' }}>
          {row.lastOrder || row.lastOrderDate || 'No recent orders'}
        </Typography>
      )
    },
    {
      id: 'actions',
      label: 'Actions',
      align: 'right',
      render: (row) => (
        <Box display="flex" gap={1} justifyContent="flex-end">
          <Button
            variant="outlined"
            size="small"
            startIcon={<VisibilityIcon sx={{ fontSize: '1rem !important' }} />}
            onClick={(e) => {
              e.stopPropagation();
              handleOpenDetails(row);
            }}
            sx={{
              borderRadius: 2,
              py: 0.4,
              px: 1.4,
              fontSize: '0.78rem',
              fontWeight: 700,
              textTransform: 'none',
              borderColor: 'rgba(59, 130, 246, 0.4)',
              color: '#2563eb',
              '&:hover': {
                borderColor: '#2563eb',
                bgcolor: 'rgba(59, 130, 246, 0.04)'
              }
            }}
          >
            View Profile
          </Button>
        </Box>
      )
    }
  ];

  return (
    <Box display="flex" flexDirection="column" gap={3}>
      {/* Header bar */}
      <Box display="flex" justifyContent="space-between" alignItems="flex-start" flexWrap="wrap" gap={2}>
        <Box>
          <Typography variant="h4" fontWeight={800} color="text.primary" letterSpacing="-0.5px">
            Patient Directory
          </Typography>
          <Typography variant="body2" color="text.secondary" sx={{ mt: 0.5 }}>
            Browse registered patient profiles, purchase frequencies, contact information, and delivery locations.
          </Typography>
        </Box>
        <Chip
          icon={<PeopleAltIcon sx={{ fontSize: 16 }} />}
          label={`${totalCount} Total Patients`}
          sx={{
            fontWeight: 700,
            fontSize: '0.8rem',
            bgcolor: 'rgba(59, 130, 246, 0.1)',
            color: '#2563eb',
            border: '1px solid rgba(59, 130, 246, 0.25)',
            py: 0.5
          }}
        />
      </Box>

      {/* KPI Cards */}
      <Grid container spacing={2}>
        {kpis.map((kpi, idx) => (
          <Grid item xs={12} sm={6} md={3} key={idx}>
            <Card
              variant="outlined"
              sx={{
                borderRadius: 3,
                border: '1px solid #e2e8f0',
                boxShadow: '0 1px 3px rgba(0,0,0,0.02)',
                transition: 'all 0.2s ease',
                '&:hover': {
                  transform: 'translateY(-2px)',
                  boxShadow: '0 4px 12px rgba(0,0,0,0.06)'
                }
              }}
            >
              <CardContent sx={{ p: 2.2, '&:last-child': { pb: 2.2 } }}>
                <Box display="flex" justifyContent="space-between" alignItems="flex-start" mb={1.2}>
                  <Box
                    sx={{
                      p: 1.1,
                      borderRadius: 2.5,
                      bgcolor: kpi.bg,
                      color: kpi.color,
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center'
                    }}
                  >
                    {kpi.icon}
                  </Box>
                  <Typography variant="h5" fontWeight={800} color="text.primary">
                    {kpi.value}
                  </Typography>
                </Box>
                <Typography variant="body2" fontWeight={700} color="text.primary">
                  {kpi.title}
                </Typography>
                <Typography variant="caption" color="text.secondary">
                  {kpi.subtext}
                </Typography>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>

      {/* Customer Directory Table */}
      <ReusableDataTable
        columns={columns}
        data={customers}
        searchKey="name"
        searchPlaceholder="Search patients by name, phone or email..."
        loading={loading}
        emptyTitle="No patient records found"
        emptyDescription="There are no patient files currently indexed in the dispensary database."
        onRowClick={handleOpenDetails}
      />

      {/* Customer Profile Details Dialog */}
      <Dialog
        open={detailsOpen}
        onClose={() => setDetailsOpen(false)}
        maxWidth="sm"
        fullWidth
        PaperProps={{
          sx: { borderRadius: 3.5, overflow: 'hidden' }
        }}
      >
        <DialogTitle sx={{ px: 3, py: 2, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <Box display="flex" alignItems="center" gap={1.5}>
            <Avatar
              sx={{
                bgcolor: 'rgba(16, 185, 129, 0.15)',
                color: '#059669',
                fontWeight: 800,
                width: 44,
                height: 44,
                border: '2px solid rgba(16, 185, 129, 0.3)'
              }}
            >
              {selectedCust ? getInitials(selectedCust.name) : 'PT'}
            </Avatar>
            <Box>
              <Typography variant="subtitle1" fontWeight={800} color="text.primary">
                {selectedCust?.name || 'Patient Summary'}
              </Typography>
              <Typography variant="caption" color="text.secondary">
                Customer Record #{selectedCust?.id || 'N/A'}
              </Typography>
            </Box>
          </Box>
          <IconButton size="small" onClick={() => setDetailsOpen(false)} sx={{ color: 'text.secondary' }}>
            <CloseIcon fontSize="small" />
          </IconButton>
        </DialogTitle>

        <Divider />

        <DialogContent sx={{ p: 3 }}>
          {selectedCust && (
            <Stack spacing={2.5}>
              {/* Contact Information Cards */}
              <Box>
                <Typography variant="caption" fontWeight={700} color="text.secondary" sx={{ textTransform: 'uppercase', letterSpacing: '0.5px', mb: 1, display: 'block' }}>
                  Contact Demographics
                </Typography>
                <Grid container spacing={1.5}>
                  <Grid item xs={12} sm={6}>
                    <Paper variant="outlined" sx={{ p: 1.5, borderRadius: 2, bgcolor: '#f8fafc', borderColor: '#e2e8f0' }}>
                      <Box display="flex" alignItems="center" gap={1} mb={0.5}>
                        <PhoneIcon sx={{ fontSize: 16, color: '#3b82f6' }} />
                        <Typography variant="caption" color="text.secondary" fontWeight={600}>Mobile Phone</Typography>
                      </Box>
                      <Typography variant="body2" fontWeight={700} sx={{ fontFamily: 'monospace' }}>
                        {selectedCust.phone || 'Not provided'}
                      </Typography>
                    </Paper>
                  </Grid>

                  <Grid item xs={12} sm={6}>
                    <Paper variant="outlined" sx={{ p: 1.5, borderRadius: 2, bgcolor: '#f8fafc', borderColor: '#e2e8f0' }}>
                      <Box display="flex" alignItems="center" gap={1} mb={0.5}>
                        <EmailIcon sx={{ fontSize: 16, color: '#8b5cf6' }} />
                        <Typography variant="caption" color="text.secondary" fontWeight={600}>Email Address</Typography>
                      </Box>
                      <Typography variant="body2" fontWeight={700} noWrap>
                        {selectedCust.email || 'Not provided'}
                      </Typography>
                    </Paper>
                  </Grid>

                  <Grid item xs={12}>
                    <Paper variant="outlined" sx={{ p: 1.5, borderRadius: 2, bgcolor: '#f8fafc', borderColor: '#e2e8f0' }}>
                      <Box display="flex" alignItems="center" gap={1} mb={0.5}>
                        <LocationOnIcon sx={{ fontSize: 16, color: '#ef4444' }} />
                        <Typography variant="caption" color="text.secondary" fontWeight={600}>Saved Delivery Address</Typography>
                      </Box>
                      <Typography variant="body2" fontWeight={600}>
                        {selectedCust.address || 'Pandharpur, Maharashtra, India'}
                      </Typography>
                    </Paper>
                  </Grid>
                </Grid>
              </Box>

              {/* Order History Metrics */}
              <Box>
                <Typography variant="caption" fontWeight={700} color="text.secondary" sx={{ textTransform: 'uppercase', letterSpacing: '0.5px', mb: 1, display: 'block' }}>
                  Dispensary History
                </Typography>
                <Grid container spacing={2}>
                  <Grid item xs={6}>
                    <Paper
                      variant="outlined"
                      sx={{
                        p: 2,
                        textAlign: 'center',
                        borderRadius: 2.5,
                        bgcolor: 'rgba(59, 130, 246, 0.04)',
                        borderColor: 'rgba(59, 130, 246, 0.2)'
                      }}
                    >
                      <LocalMallIcon sx={{ color: '#2563eb', fontSize: 26, mb: 0.5 }} />
                      <Typography variant="caption" color="text.secondary" display="block">Cumulative Orders</Typography>
                      <Typography variant="h5" fontWeight={800} color="#1e40af">
                        {selectedCust.orders ?? selectedCust.totalOrders ?? 0}
                      </Typography>
                    </Paper>
                  </Grid>

                  <Grid item xs={6}>
                    <Paper
                      variant="outlined"
                      sx={{
                        p: 2,
                        textAlign: 'center',
                        borderRadius: 2.5,
                        bgcolor: 'rgba(16, 185, 129, 0.04)',
                        borderColor: 'rgba(16, 185, 129, 0.2)'
                      }}
                    >
                      <DescriptionIcon sx={{ color: '#059669', fontSize: 26, mb: 0.5 }} />
                      <Typography variant="caption" color="text.secondary" display="block">Most Recent Order</Typography>
                      <Typography variant="body2" fontWeight={700} color="#065f46" sx={{ mt: 0.5 }}>
                        {selectedCust.lastOrder || selectedCust.lastOrderDate || 'None logged'}
                      </Typography>
                    </Paper>
                  </Grid>
                </Grid>
              </Box>
            </Stack>
          )}
        </DialogContent>

        <Divider />

        <DialogActions sx={{ px: 3, py: 1.5 }}>
          <Button
            onClick={() => setDetailsOpen(false)}
            variant="contained"
            size="small"
            sx={{
              borderRadius: 2,
              px: 2.5,
              py: 0.6,
              fontWeight: 700,
              fontSize: '0.8rem',
              textTransform: 'none',
              bgcolor: 'primary.main',
              boxShadow: 'none'
            }}
          >
            Close Directory Card
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default Customers;
