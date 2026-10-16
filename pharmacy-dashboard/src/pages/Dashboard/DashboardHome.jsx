import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Grid,
  Card,
  CardContent,
  Typography,
  Box,
  Paper,
  Button,
  Alert,
  IconButton
} from '@mui/material';
import FactCheckIcon from '@mui/icons-material/FactCheck';
import LocalMallIcon from '@mui/icons-material/LocalMall';
import AutorenewIcon from '@mui/icons-material/Autorenew';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import ArrowForwardIcon from '@mui/icons-material/ArrowForward';
import SettingsIcon from '@mui/icons-material/Settings';
import { ResponsiveContainer, LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, PieChart, Pie, Cell } from 'recharts';
import { usePrescriptionService } from '../../services/prescriptionService';
import { useOrderService } from '../../services/orderService';
import { useReportService } from '../../services/reportService';
import { useMockData } from '../../context/MockDataContext';
import LoadingSpinner from '../../components/common/LoadingSpinner';

const COLORS = ['#10b981', '#3b82f6', '#f59e0b', '#ef4444'];

const DashboardHome = () => {
  const navigate = useNavigate();
  const { mockEnabled } = useMockData();
  const { getPrescriptions } = usePrescriptionService();
  const { getOrders } = useOrderService();
  const { getReportCharts } = useReportService();

  const [loading, setLoading] = useState(true);
  const [stats, setStats] = useState({
    pendingPrescriptions: '--',
    ordersToday: '--',
    ordersReady: '--',
    completedOrders: '--'
  });
  const [chartData, setChartData] = useState({
    ordersTrend: [],
    prescriptionStatus: []
  });

  useEffect(() => {
    const loadDashboardData = async () => {
      setLoading(true);
      try {
        const [prescriptions, orders, charts] = await Promise.all([
          getPrescriptions(),
          getOrders(),
          getReportCharts()
        ]);

        if (!mockEnabled) {
          setStats({
            pendingPrescriptions: '--',
            ordersToday: '--',
            ordersReady: '--',
            completedOrders: '--'
          });
          setChartData({
            ordersTrend: [],
            prescriptionStatus: []
          });
        } else {
          // Calculate stats from mock collections
          const pendingP = prescriptions.filter(p => p.status === 'Pending').length;
          const todayO = orders.length;
          const readyO = orders.filter(o => o.status === 'Ready').length;
          const completedO = orders.filter(o => o.status === 'Delivered').length;

          setStats({
            pendingPrescriptions: String(pendingP),
            ordersToday: String(todayO),
            ordersReady: String(readyO),
            completedOrders: String(completedO)
          });

          setChartData({
            ordersTrend: charts.ordersTrend,
            prescriptionStatus: charts.prescriptionStatus
          });
        }
      } catch (err) {
        console.error('Error fetching dashboard metrics', err);
      } finally {
        setLoading(false);
      }
    };

    loadDashboardData();
  }, [mockEnabled]);

  const statCards = [
    {
      title: 'Pending Prescription Reviews',
      value: stats.pendingPrescriptions,
      icon: <FactCheckIcon sx={{ fontSize: 32 }} />,
      color: '#f59e0b',
      path: '/prescriptions'
    },
    {
      title: 'Orders Received Today',
      value: stats.ordersToday,
      icon: <LocalMallIcon sx={{ fontSize: 32 }} />,
      color: '#3b82f6',
      path: '/orders'
    },
    {
      title: 'Orders Ready for Pickup',
      value: stats.ordersReady,
      icon: <AutorenewIcon sx={{ fontSize: 32 }} />,
      color: '#10b981',
      path: '/orders'
    },
    {
      title: 'Completed Orders Today',
      value: stats.completedOrders,
      icon: <CheckCircleIcon sx={{ fontSize: 32 }} />,
      color: '#059669',
      path: '/orders'
    }
  ];

  return (
    <Box display="flex" flexDirection="column" gap={3.5}>
      {/* Welcome Title */}
      <Box display="flex" justifyContent="space-between" alignItems="center" flexWrap="wrap" gap={2}>
        <Box>
          <Typography variant="h4" fontWeight={800} color="text.primary" letterSpacing="-0.5px">
            Dashboard Overview
          </Typography>
          <Typography variant="body2" color="text.secondary" sx={{ mt: 0.5 }}>
            Real-time status of prescriptions, patient orders, and AI extraction results.
          </Typography>
        </Box>
        <Button
          variant="outlined"
          color="primary"
          startIcon={<SettingsIcon />}
          onClick={() => navigate('/settings')}
          sx={{ borderRadius: 2.5 }}
        >
          Setup Config
        </Button>
      </Box>

      {/* Info Alert about Demo Database */}
      {!mockEnabled && (
        <Alert
          severity="info"
          sx={{ borderRadius: 3, border: '1px solid', borderColor: 'info.lightBorder' }}
          action={
            <Button color="inherit" size="small" onClick={() => navigate('/settings')}>
              Enable Mock Data
            </Button>
          }
        >
          The dashboard is currently in <strong>API-Ready Mode</strong>. Metrics display empty indicators (<code>--</code>) and charts are unpopulated.
        </Alert>
      )}

      {loading ? (
        <LoadingSpinner message="Fetching live dashboard status..." height="50vh" />
      ) : (
        <>
          {/* Statistic Cards */}
          <Grid container spacing={3}>
            {statCards.map((card, index) => (
              <Grid item xs={12} sm={6} md={3} key={index}>
                <Card
                  sx={{
                    borderRadius: 4,
                    border: '1px solid',
                    borderColor: 'divider',
                    boxShadow: '0px 4px 12px rgba(0, 0, 0, 0.01)',
                    position: 'relative',
                    overflow: 'hidden',
                    height: '100%',
                    cursor: 'pointer',
                    '&:hover': {
                      boxShadow: '0px 8px 24px rgba(0, 0, 0, 0.05)',
                      transform: 'translateY(-2px)'
                    },
                    transition: 'all 0.25s ease'
                  }}
                  onClick={() => navigate(card.path)}
                >
                  <CardContent sx={{ p: 3 }}>
                    <Box display="flex" justifyContent="space-between" alignItems="flex-start" mb={2}>
                      <Box
                        sx={{
                          p: 1.5,
                          borderRadius: 3,
                          bgcolor: `${card.color}15`,
                          color: card.color,
                          display: 'flex',
                          alignItems: 'center',
                          justifyContent: 'center'
                        }}
                      >
                        {card.icon}
                      </Box>
                      <IconButton size="small" sx={{ color: 'grey.400' }}>
                        <ArrowForwardIcon fontSize="small" />
                      </IconButton>
                    </Box>
                    <Typography variant="body2" color="text.secondary" fontWeight={500} gutterBottom>
                      {card.title}
                    </Typography>
                    <Typography variant="h3" fontWeight={800} color="text.primary">
                      {card.value}
                    </Typography>
                  </CardContent>
                </Card>
              </Grid>
            ))}
          </Grid>

          {/* Charts Row */}
          <Grid container spacing={3}>
            {/* Orders Trend Chart */}
            <Grid item xs={12} md={8}>
              <Paper
                elevation={0}
                sx={{
                  p: 3,
                  borderRadius: 4,
                  border: '1px solid',
                  borderColor: 'divider',
                  height: 420,
                  display: 'flex',
                  flexDirection: 'column'
                }}
              >
                <Typography variant="h6" fontWeight={700} gutterBottom>
                  Orders Trend (Daily)
                </Typography>
                <Typography variant="caption" color="text.secondary" sx={{ mb: 3 }}>
                  Total orders received daily over the past week.
                </Typography>
                <Box sx={{ flexGrow: 1, width: '100%', minHeight: 250 }}>
                  {chartData.ordersTrend.length === 0 ? (
                    <Box
                      display="flex"
                      alignItems="center"
                      justifyContent="center"
                      height="100%"
                      sx={{ bgcolor: 'grey.50', borderRadius: 3, border: '1px dashed', borderColor: 'divider' }}
                    >
                      <Typography variant="body2" color="text.secondary">
                        No orders trend data to display (API returned empty dataset).
                      </Typography>
                    </Box>
                  ) : (
                    <ResponsiveContainer width="100%" height="100%">
                      <LineChart data={chartData.ordersTrend} margin={{ top: 5, right: 20, left: 0, bottom: 5 }}>
                        <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f0f0f0" />
                        <XAxis dataKey="name" stroke="#94a3b8" fontSize={12} tickLine={false} />
                        <YAxis stroke="#94a3b8" fontSize={12} tickLine={false} axisLine={false} />
                        <Tooltip />
                        <Legend />
                        <Line
                          type="monotone"
                          dataKey="Orders"
                          stroke="#10b981"
                          strokeWidth={3}
                          activeDot={{ r: 8 }}
                          dot={{ r: 4 }}
                        />
                      </LineChart>
                    </ResponsiveContainer>
                  )}
                </Box>
              </Paper>
            </Grid>

            {/* Prescription Status Distribution */}
            <Grid item xs={12} md={4}>
              <Paper
                elevation={0}
                sx={{
                  p: 3,
                  borderRadius: 4,
                  border: '1px solid',
                  borderColor: 'divider',
                  height: 420,
                  display: 'flex',
                  flexDirection: 'column'
                }}
              >
                <Typography variant="h6" fontWeight={700} gutterBottom>
                  Prescription Status
                </Typography>
                <Typography variant="caption" color="text.secondary" sx={{ mb: 3 }}>
                  Distribution of prescription verification classifications.
                </Typography>
                <Box sx={{ flexGrow: 1, width: '100%', minHeight: 250, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                  {chartData.prescriptionStatus.length === 0 ? (
                    <Box
                      display="flex"
                      alignItems="center"
                      justifyContent="center"
                      height="100%"
                      width="100%"
                      sx={{ bgcolor: 'grey.50', borderRadius: 3, border: '1px dashed', borderColor: 'divider' }}
                    >
                      <Typography variant="body2" color="text.secondary">
                        No distribution data available.
                      </Typography>
                    </Box>
                  ) : (
                    <ResponsiveContainer width="100%" height="100%">
                      <PieChart>
                        <Pie
                          data={chartData.prescriptionStatus}
                          cx="50%"
                          cy="50%"
                          innerRadius={60}
                          outerRadius={90}
                          paddingAngle={5}
                          dataKey="value"
                        >
                          {chartData.prescriptionStatus.map((entry, index) => (
                            <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                          ))}
                        </Pie>
                        <Tooltip />
                        <Legend layout="horizontal" align="center" verticalAlign="bottom" />
                      </PieChart>
                    </ResponsiveContainer>
                  )}
                </Box>
              </Paper>
            </Grid>
          </Grid>
        </>
      )}
    </Box>
  );
};

export default DashboardHome;
