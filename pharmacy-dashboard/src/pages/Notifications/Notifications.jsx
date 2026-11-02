import React, { useState, useEffect, useMemo } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Box,
  Typography,
  Card,
  CardContent,
  IconButton,
  Button,
  Grid,
  Chip,
  Paper,
  Tooltip,
  Stack
} from '@mui/material';
import FactCheckIcon from '@mui/icons-material/FactCheck';
import LocalMallIcon from '@mui/icons-material/LocalMall';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import WarningAmberIcon from '@mui/icons-material/WarningAmber';
import InventoryIcon from '@mui/icons-material/Inventory';
import DraftsIcon from '@mui/icons-material/Drafts';
import MarkEmailReadIcon from '@mui/icons-material/MarkEmailRead';
import NotificationsActiveIcon from '@mui/icons-material/NotificationsActive';
import AccessTimeIcon from '@mui/icons-material/AccessTime';
import TuneIcon from '@mui/icons-material/Tune';
import ArrowForwardIcon from '@mui/icons-material/ArrowForward';
import { useNotificationService } from '../../services/notificationService';
import LoadingSpinner from '../../components/common/LoadingSpinner';
import EmptyState from '../../components/common/EmptyState';
import NotificationPreferencesDialog from '../../components/dialogs/NotificationPreferencesDialog';

const Notifications = () => {
  const navigate = useNavigate();
  const { getNotifications, markAsRead, markAllAsRead } = useNotificationService();

  const [loading, setLoading] = useState(true);
  const [notifications, setNotifications] = useState([]);
  const [activeFilter, setActiveFilter] = useState('ALL');
  const [prefsOpen, setPrefsOpen] = useState(false);

  const fetchNotificationList = async () => {
    setLoading(true);
    try {
      const data = await getNotifications(50);
      setNotifications(Array.isArray(data) ? data : []);
    } catch (err) {
      console.error('Failed to load notifications:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchNotificationList();
    const interval = setInterval(fetchNotificationList, 8000);
    return () => clearInterval(interval);
  }, []);

  const handleMarkAsRead = async (id) => {
    try {
      await markAsRead(id);
      fetchNotificationList();
    } catch (err) {
      console.error(err);
    }
  };

  const handleMarkAllRead = async () => {
    try {
      await markAllAsRead();
      fetchNotificationList();
    } catch (err) {
      console.error(err);
    }
  };

  const getAlertConfig = (notif) => {
    const cat = notif.category || '';
    const type = notif.type || '';

    if (cat === 'prescription' || type.includes('PRESCRIPTION')) {
      return {
        icon: <FactCheckIcon sx={{ fontSize: 20 }} />,
        color: '#f59e0b',
        bg: 'rgba(245, 158, 11, 0.1)',
        tag: 'Prescription Scan',
        actionLabel: 'Verify Prescription',
        actionPath: '/prescriptions'
      };
    }
    if (cat === 'order' || type.includes('ORDER')) {
      return {
        icon: <LocalMallIcon sx={{ fontSize: 20 }} />,
        color: '#3b82f6',
        bg: 'rgba(59, 130, 246, 0.1)',
        tag: 'Order Dispatch',
        actionLabel: 'Fulfill Order',
        actionPath: '/orders'
      };
    }
    if (cat === 'inventory' || type.includes('STOCK') || type.includes('EXPIRY') || type.includes('CATALOGUE')) {
      return {
        icon: <InventoryIcon sx={{ fontSize: 20 }} />,
        color: '#10b981',
        bg: 'rgba(16, 185, 129, 0.1)',
        tag: 'Stock Telemetry',
        actionLabel: 'Manage Stock',
        actionPath: '/medicines'
      };
    }
    return {
      icon: <WarningAmberIcon sx={{ fontSize: 20 }} />,
      color: '#8b5cf6',
      bg: 'rgba(139, 92, 246, 0.1)',
      tag: 'System Event',
      actionLabel: 'View Details',
      actionPath: '/dashboard'
    };
  };

  // KPI Computations
  const totalCount = notifications.length;
  const unreadCount = notifications.filter(n => !n.read).length;
  const rxAlertsCount = notifications.filter(n => (n.category === 'prescription' || n.type?.includes('PRESCRIPTION'))).length;
  const orderAlertsCount = notifications.filter(n => (n.category === 'order' || n.type?.includes('ORDER'))).length;
  const stockAlertsCount = notifications.filter(n => (n.category === 'inventory' || n.type?.includes('STOCK') || n.type?.includes('EXPIRY'))).length;

  const kpis = [
    {
      title: 'Total Stream Alerts',
      value: totalCount,
      icon: <NotificationsActiveIcon sx={{ fontSize: 24 }} />,
      color: '#3b82f6',
      bg: 'rgba(59, 130, 246, 0.1)',
      subtext: 'Real-time telemetry stream'
    },
    {
      title: 'Action Required',
      value: unreadCount,
      icon: <DraftsIcon sx={{ fontSize: 24 }} />,
      color: unreadCount > 0 ? '#ef4444' : '#10b981',
      bg: unreadCount > 0 ? 'rgba(239, 68, 68, 0.1)' : 'rgba(16, 185, 129, 0.1)',
      subtext: unreadCount > 0 ? 'Unread messages' : 'All alerts cleared'
    },
    {
      title: 'Prescription Activity',
      value: rxAlertsCount,
      icon: <FactCheckIcon sx={{ fontSize: 24 }} />,
      color: '#f59e0b',
      bg: 'rgba(245, 158, 11, 0.1)',
      subtext: 'Scans & approvals'
    },
    {
      title: 'Order Dispatch Events',
      value: orderAlertsCount,
      icon: <LocalMallIcon sx={{ fontSize: 24 }} />,
      color: '#8b5cf6',
      bg: 'rgba(139, 92, 246, 0.1)',
      subtext: 'Cart checkouts'
    }
  ];

  // Filtered Notifications
  const filteredNotifications = useMemo(() => {
    return notifications.filter((notif) => {
      if (activeFilter === 'UNREAD') return !notif.read;
      if (activeFilter === 'PRESCRIPTION') return notif.category === 'prescription' || notif.type?.toLowerCase().includes('prescription');
      if (activeFilter === 'ORDER') return notif.category === 'order' || notif.type?.toLowerCase().includes('order');
      if (activeFilter === 'INVENTORY') return notif.category === 'inventory' || notif.type?.toLowerCase().includes('stock') || notif.type?.toLowerCase().includes('expiry');
      return true;
    });
  }, [notifications, activeFilter]);

  return (
    <Box display="flex" flexDirection="column" gap={3}>
      {/* Header bar */}
      <Box display="flex" justifyContent="space-between" alignItems="center" flexWrap="wrap" gap={2}>
        <Box>
          <Typography variant="h5" fontWeight={800} color="#0f172a" letterSpacing="-0.5px">
            Notifications & Dispatch Alerts
          </Typography>
          <Typography variant="body2" color="text.secondary" sx={{ mt: 0.3 }}>
            Real-time feed of patient prescription submissions, order packaging, low stock warnings, and dispensary events.
          </Typography>
        </Box>

        <Stack direction="row" spacing={1.2}>
          <Button
            variant="outlined"
            size="small"
            startIcon={<TuneIcon />}
            onClick={() => setPrefsOpen(true)}
            sx={{
              borderRadius: 2,
              py: 0.6,
              px: 1.8,
              fontSize: '0.8rem',
              fontWeight: 700,
              textTransform: 'none'
            }}
          >
            Preferences
          </Button>

          {unreadCount > 0 && (
            <Button
              variant="contained"
              size="small"
              color="primary"
              startIcon={<MarkEmailReadIcon sx={{ fontSize: '1rem !important' }} />}
              onClick={handleMarkAllRead}
              sx={{
                borderRadius: 2,
                py: 0.6,
                px: 1.8,
                fontSize: '0.8rem',
                fontWeight: 700,
                textTransform: 'none',
                bgcolor: '#10b981',
                '&:hover': { bgcolor: '#059669' }
              }}
            >
              Mark All Read ({unreadCount})
            </Button>
          )}
        </Stack>
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
                bgcolor: '#ffffff',
                boxShadow: '0 1px 3px rgba(0,0,0,0.02)'
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
                  <Typography variant="h5" fontWeight={800} color="#0f172a">
                    {kpi.value}
                  </Typography>
                </Box>
                <Typography variant="body2" fontWeight={700} color="#0f172a">
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

      {/* Filter Chips Bar */}
      <Paper elevation={0} sx={{ p: 1.5, borderRadius: 3, border: '1px solid #e2e8f0', bgcolor: '#ffffff' }}>
        <Stack direction="row" spacing={1} flexWrap="wrap" alignItems="center">
          <Typography variant="caption" fontWeight={700} color="#64748b" sx={{ mr: 1, textTransform: 'uppercase' }}>
            Filter Category:
          </Typography>
          {[
            { key: 'ALL', label: 'All Alerts', count: totalCount },
            { key: 'UNREAD', label: 'Unread Only', count: unreadCount, color: '#ef4444' },
            { key: 'PRESCRIPTION', label: 'Prescriptions', count: rxAlertsCount, color: '#f59e0b' },
            { key: 'ORDER', label: 'Orders', count: orderAlertsCount, color: '#3b82f6' },
            { key: 'INVENTORY', label: 'Inventory & Stock', count: stockAlertsCount, color: '#10b981' }
          ].map((tab) => {
            const isSelected = activeFilter === tab.key;
            return (
              <Chip
                key={tab.key}
                label={`${tab.label} (${tab.count})`}
                size="small"
                onClick={() => setActiveFilter(tab.key)}
                sx={{
                  fontWeight: 700,
                  fontSize: '0.78rem',
                  borderRadius: 2,
                  py: 1.6,
                  px: 0.5,
                  cursor: 'pointer',
                  bgcolor: isSelected ? (tab.color ? `${tab.color}20` : '#0f172a') : '#f8fafc',
                  color: isSelected ? (tab.color || '#ffffff') : '#64748b',
                  border: isSelected ? `1px solid ${tab.color || '#0f172a'}` : '1px solid #e2e8f0',
                  '&:hover': { bgcolor: isSelected ? undefined : '#f1f5f9' }
                }}
              />
            );
          })}
        </Stack>
      </Paper>

      {/* Content Stream */}
      {loading ? (
        <LoadingSpinner message="Querying incoming alerts..." height="30vh" />
      ) : filteredNotifications.length === 0 ? (
        <EmptyState
          title="No alerts in this category."
          description="Your dispensary inbox has no messages under the selected filter."
        />
      ) : (
        <Grid container spacing={1.5}>
          {filteredNotifications.map((notif) => {
            const config = getAlertConfig(notif);
            return (
              <Grid item xs={12} key={notif.id}>
                <Card
                  variant="outlined"
                  sx={{
                    borderRadius: 2.5,
                    borderColor: notif.read ? '#e2e8f0' : 'rgba(59, 130, 246, 0.4)',
                    bgcolor: notif.read ? '#ffffff' : 'rgba(59, 130, 246, 0.02)',
                    borderLeft: '4px solid',
                    borderLeftColor: config.color,
                    boxShadow: notif.read ? 'none' : '0 2px 8px rgba(59, 130, 246, 0.06)',
                    transition: 'all 0.2s ease',
                    position: 'relative'
                  }}
                >
                  <CardContent sx={{ p: 2, '&:last-child': { pb: 2 } }}>
                    <Box display="flex" alignItems="center" justifyContent="space-between" flexWrap="wrap" gap={2}>
                      <Box display="flex" alignItems="center" gap={2} flex={1}>
                        {/* Icon */}
                        <Box
                          sx={{
                            p: 1.2,
                            borderRadius: 2,
                            bgcolor: config.bg,
                            color: config.color,
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center',
                            flexShrink: 0
                          }}
                        >
                          {config.icon}
                        </Box>

                        {/* Content */}
                        <Box flexGrow={1}>
                          <Box display="flex" alignItems="center" gap={1.2} flexWrap="wrap" mb={0.4}>
                            <Typography variant="subtitle2" fontWeight={800} color="#0f172a">
                              {notif.title || notif.type}
                            </Typography>
                            <Chip
                              label={config.tag}
                              size="small"
                              sx={{
                                fontSize: '0.7rem',
                                height: 18,
                                bgcolor: '#f1f5f9',
                                fontWeight: 700,
                                color: '#475569'
                              }}
                            />
                            <Box display="flex" alignItems="center" gap={0.4} color="text.secondary">
                              <AccessTimeIcon sx={{ fontSize: 13 }} />
                              <Typography variant="caption" sx={{ fontSize: '0.72rem' }}>
                                {notif.time || 'Recently'}
                              </Typography>
                            </Box>
                            {!notif.read && (
                              <Chip
                                label="NEW"
                                size="small"
                                sx={{
                                  fontSize: '0.65rem',
                                  height: 16,
                                  bgcolor: '#3b82f6',
                                  color: '#ffffff',
                                  fontWeight: 800
                                }}
                              />
                            )}
                          </Box>
                          <Typography variant="body2" color="#475569" sx={{ fontSize: '0.85rem' }}>
                            {notif.message}
                          </Typography>
                        </Box>
                      </Box>

                      {/* Action buttons */}
                      <Stack direction="row" spacing={1} alignItems="center">
                        <Button
                          variant="outlined"
                          size="small"
                          endIcon={<ArrowForwardIcon sx={{ fontSize: 14 }} />}
                          onClick={() => {
                            if (!notif.read) handleMarkAsRead(notif.id);
                            navigate(notif.actionUrl || config.actionPath);
                          }}
                          sx={{
                            borderRadius: 2,
                            fontSize: '0.76rem',
                            fontWeight: 700,
                            textTransform: 'none',
                            borderColor: config.color,
                            color: config.color
                          }}
                        >
                          {config.actionLabel}
                        </Button>

                        {!notif.read && (
                          <Tooltip title="Mark as Read">
                            <IconButton
                              size="small"
                              color="primary"
                              onClick={() => handleMarkAsRead(notif.id)}
                              sx={{
                                bgcolor: 'rgba(59, 130, 246, 0.08)',
                                '&:hover': { bgcolor: 'rgba(59, 130, 246, 0.16)' }
                              }}
                            >
                              <DraftsIcon fontSize="small" />
                            </IconButton>
                          </Tooltip>
                        )}
                      </Stack>
                    </Box>
                  </CardContent>
                </Card>
              </Grid>
            );
          })}
        </Grid>
      )}

      {/* Preferences Dialog */}
      <NotificationPreferencesDialog
        open={prefsOpen}
        onClose={() => setPrefsOpen(false)}
      />
    </Box>
  );
};

export default Notifications;
