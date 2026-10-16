import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Grid,
  Card,
  CardContent,
  Paper
} from '@mui/material';
import LocalMallIcon from '@mui/icons-material/LocalMall';
import FactCheckIcon from '@mui/icons-material/FactCheck';
import CancelPresentationIcon from '@mui/icons-material/CancelPresentation';
import TimerIcon from '@mui/icons-material/Timer';
import { ResponsiveContainer, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, AreaChart, Area } from 'recharts';
import { useReportService } from '../../services/reportService';
import { useMockData } from '../../context/MockDataContext';
import LoadingSpinner from '../../components/common/LoadingSpinner';

const Reports = () => {
  const { mockEnabled } = useMockData();
  const { getReportStats, getReportCharts } = useReportService();

  const [loading, setLoading] = useState(true);
  const [stats, setStats] = useState({
    totalOrders: '--',
    verifiedPrescriptions: '--',
    rejectedPrescriptions: '--',
    avgVerificationTime: '--'
  });
  
  const [charts, setCharts] = useState({
    monthlyOrders: [],
    approvalRates: []
  });

  useEffect(() => {
    const loadReports = async () => {
      setLoading(true);
      try {
        const [statsData, chartsData] = await Promise.all([
          getReportStats(),
          getReportCharts()
        ]);
        setStats(statsData);
        setCharts(chartsData);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    };
    loadReports();
  }, [mockEnabled]);

  const statConfig = [
    { title: 'Total Orders', value: stats.totalOrders, icon: <LocalMallIcon sx={{ fontSize: 28 }} />, color: '#3b82f6' },
    { title: 'Verified Prescriptions', value: stats.verifiedPrescriptions, icon: <FactCheckIcon sx={{ fontSize: 28 }} />, color: '#10b981' },
    { title: 'Rejected Prescriptions', value: stats.rejectedPrescriptions, icon: <CancelPresentationIcon sx={{ fontSize: 28 }} />, color: '#ef4444' },
    { title: 'Average Verification Time', value: stats.avgVerificationTime, icon: <TimerIcon sx={{ fontSize: 28 }} />, color: '#8b5cf6' }
  ];

  return (
    <Box display="flex" flexDirection="column" gap={3.5}>
      <Box>
        <Typography variant="h4" fontWeight={800} color="text.primary" letterSpacing="-0.5px">
          Performance Reports
        </Typography>
        <Typography variant="body2" color="text.secondary" sx={{ mt: 0.5 }}>
          Pharmacy throughput analytics, prescription validation percentages, and response timelines.
        </Typography>
      </Box>

      {loading ? (
        <LoadingSpinner message="Generating analytics compilation..." height="50vh" />
      ) : (
        <>
          {/* Summary stats */}
          <Grid container spacing={3}>
            {statConfig.map((item, index) => (
              <Grid item xs={12} sm={6} md={3} key={index}>
                <Card
                  variant="outlined"
                  sx={{
                    borderRadius: 4,
                    borderColor: 'divider',
                    boxShadow: '0px 4px 12px rgba(0, 0, 0, 0.01)'
                  }}
                >
                  <CardContent sx={{ p: 3, display: 'flex', alignItems: 'center', gap: 2.5 }}>
                    <Box
                      sx={{
                        p: 1.5,
                        borderRadius: 3,
                        bgcolor: `${item.color}15`,
                        color: item.color,
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center'
                      }}
                    >
                      {item.icon}
                    </Box>
                    <Box>
                      <Typography variant="caption" color="text.secondary" fontWeight={500} display="block">
                        {item.title}
                      </Typography>
                      <Typography variant="h5" fontWeight={800} color="text.primary" sx={{ mt: 0.2 }}>
                        {item.value}
                      </Typography>
                    </Box>
                  </CardContent>
                </Card>
              </Grid>
            ))}
          </Grid>

          {/* Charts Rows */}
          <Grid container spacing={3}>
            {/* Monthly Orders Bar Chart */}
            <Grid item xs={12} md={6}>
              <Paper
                elevation={0}
                sx={{
                  p: 3,
                  borderRadius: 4,
                  border: '1px solid',
                  borderColor: 'divider',
                  height: 380,
                  display: 'flex',
                  flexDirection: 'column'
                }}
              >
                <Typography variant="subtitle1" fontWeight={700} gutterBottom>
                  Monthly Orders Volume
                </Typography>
                <Typography variant="caption" color="text.secondary" sx={{ mb: 3 }}>
                  Total medicine packaging orders fulfilled over the last 6 months.
                </Typography>
                <Box sx={{ flexGrow: 1, width: '100%', minHeight: 200 }}>
                  {charts.monthlyOrders.length === 0 ? (
                    <Box
                      display="flex"
                      alignItems="center"
                      justifyContent="center"
                      height="100%"
                      sx={{ bgcolor: 'grey.50', borderRadius: 3, border: '1px dashed', borderColor: 'divider' }}
                    >
                      <Typography variant="body2" color="text.secondary">
                        No monthly orders dataset available.
                      </Typography>
                    </Box>
                  ) : (
                    <ResponsiveContainer width="100%" height="100%">
                      <BarChart data={charts.monthlyOrders} margin={{ top: 5, right: 10, left: -20, bottom: 5 }}>
                        <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f0f0f0" />
                        <XAxis dataKey="name" fontSize={11} stroke="#94a3b8" tickLine={false} />
                        <YAxis fontSize={11} stroke="#94a3b8" tickLine={false} axisLine={false} />
                        <Tooltip />
                        <Legend />
                        <Bar dataKey="Orders" fill="#3b82f6" radius={[4, 4, 0, 0]} barSize={36} />
                      </BarChart>
                    </ResponsiveContainer>
                  )}
                </Box>
              </Paper>
            </Grid>

            {/* Prescription Approval Rate Area Chart */}
            <Grid item xs={12} md={6}>
              <Paper
                elevation={0}
                sx={{
                  p: 3,
                  borderRadius: 4,
                  border: '1px solid',
                  borderColor: 'divider',
                  height: 380,
                  display: 'flex',
                  flexDirection: 'column'
                }}
              >
                <Typography variant="subtitle1" fontWeight={700} gutterBottom>
                  Prescription Validation Rate (%)
                </Typography>
                <Typography variant="caption" color="text.secondary" sx={{ mb: 3 }}>
                  Percentage of successfully verified medical prescription uploads.
                </Typography>
                <Box sx={{ flexGrow: 1, width: '100%', minHeight: 200 }}>
                  {charts.approvalRates.length === 0 ? (
                    <Box
                      display="flex"
                      alignItems="center"
                      justifyContent="center"
                      height="100%"
                      sx={{ bgcolor: 'grey.50', borderRadius: 3, border: '1px dashed', borderColor: 'divider' }}
                    >
                      <Typography variant="body2" color="text.secondary">
                        No validation metrics available.
                      </Typography>
                    </Box>
                  ) : (
                    <ResponsiveContainer width="100%" height="100%">
                      <AreaChart data={charts.approvalRates} margin={{ top: 5, right: 10, left: -20, bottom: 5 }}>
                        <defs>
                          <linearGradient id="colorRate" x1="0" y1="0" x2="0" y2="1">
                            <stop offset="5%" stopColor="#10b981" stopOpacity={0.3} />
                            <stop offset="95%" stopColor="#10b981" stopOpacity={0} />
                          </linearGradient>
                        </defs>
                        <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f0f0f0" />
                        <XAxis dataKey="name" fontSize={11} stroke="#94a3b8" tickLine={false} />
                        <YAxis fontSize={11} stroke="#94a3b8" tickLine={false} axisLine={false} domain={[80, 100]} />
                        <Tooltip />
                        <Legend />
                        <Area type="monotone" dataKey="Rate" stroke="#10b981" strokeWidth={2.5} fillOpacity={1} fill="url(#colorRate)" />
                      </AreaChart>
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

export default Reports;
