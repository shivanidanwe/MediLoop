import React, { useState, useEffect } from 'react';
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
  Tooltip
} from '@mui/material';
import FactCheckIcon from '@mui/icons-material/FactCheck';
import LocalMallIcon from '@mui/icons-material/LocalMall';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import WarningAmberIcon from '@mui/icons-material/WarningAmber';
import DraftsIcon from '@mui/icons-material/Drafts';
import MarkEmailReadIcon from '@mui/icons-material/MarkEmailRead';
import { useNotificationService } from '../../services/notificationService';
import { useMockData } from '../../context/MockDataContext';
import LoadingSpinner from '../../components/common/LoadingSpinner';
import EmptyState from '../../components/common/EmptyState';

const Notifications = () => {
  const { mockEnabled } = useMockData();
  const { getNotifications, markAsRead } = useNotificationService();
  
  const [loading, setLoading] = useState(true);
  const [notifications, setNotifications] = useState([]);

  const fetchNotificationList = async () => {
    setLoading(true);
    try {
      const data = await getNotifications();
      setNotifications(data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchNotificationList();
  }, [mockEnabled]);

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
      const unread = notifications.filter(n => !n.read);
      await Promise.all(unread.map(n => markAsRead(n.id)));
      fetchNotificationList();
    } catch (err) {
      console.error(err);
    }
  };

  const getAlertConfig = (type) => {
    switch (type) {
      case 'New Prescription':
        return {
          icon: <FactCheckIcon />,
          color: '#f59e0b',
          bg: '#fef3c7'
        };
      case 'Order Received':
        return {
          icon: <LocalMallIcon />,
          color: '#3b82f6',
          bg: '#dbeafe'
        };
      case 'Verification Complete':
        return {
          icon: <CheckCircleIcon />,
          color: '#10b981',
          bg: '#d1fae5'
        };
      default:
        return {
          icon: <WarningAmberIcon />,
          color: '#ef4444',
          bg: '#fee2e2'
        };
    }
  };

  return (
    <Box display="flex" flexDirection="column" gap={3.5}>
      {/* Header bar */}
      <Box display="flex" justifyContent="space-between" alignItems="center" flexWrap="wrap" gap={2}>
        <Box>
          <Typography variant="h4" fontWeight={800} color="text.primary" letterSpacing="-0.5px">
            Notifications
          </Typography>
          <Typography variant="body2" color="text.secondary" sx={{ mt: 0.5 }}>
            Real-time feed of prescription scanning events, patient orders, and system checks.
          </Typography>
        </Box>
        {mockEnabled && notifications.some((n) => !n.read) && (
          <Button
            variant="outlined"
            color="primary"
            startIcon={<MarkEmailReadIcon />}
            onClick={handleMarkAllRead}
            sx={{ borderRadius: 2.5 }}
          >
            Mark All Read
          </Button>
        )}
      </Box>

      {loading ? (
        <LoadingSpinner message="Querying incoming alerts..." height="40vh" />
      ) : notifications.length === 0 ? (
        <EmptyState title="No notifications available." description="Your inbox is clear! Any alerts will appear here." />
      ) : (
        <Grid container spacing={2}>
          {notifications.map((notif) => {
            const config = getAlertConfig(notif.type);
            return (
              <Grid item xs={12} key={notif.id}>
                <Card
                  variant="outlined"
                  sx={{
                    borderRadius: 3.5,
                    borderColor: notif.read ? 'divider' : 'primary.lightBorder',
                    bgcolor: notif.read ? '#ffffff' : 'primary.lightBg',
                    borderLeft: '5px solid',
                    borderLeftColor: config.color,
                    transition: 'all 0.2s',
                    position: 'relative'
                  }}
                >
                  <CardContent sx={{ p: 2.5, '&:last-child': { pb: 2.5 } }}>
                    <Box display="flex" alignItems="flex-start" gap={2}>
                      {/* Icon */}
                      <Box
                        sx={{
                          p: 1.5,
                          borderRadius: 3,
                          bgcolor: config.bg,
                          color: config.color,
                          display: 'flex',
                          alignItems: 'center',
                          justifyContent: 'center'
                        }}
                      >
                        {config.icon}
                      </Box>

                      {/* Content */}
                      <Box flexGrow={1} sx={{ pr: 6 }}>
                        <Box display="flex" alignItems="center" gap={1.5} flexWrap="wrap" mb={0.5}>
                          <Typography variant="subtitle2" fontWeight={700} color="text.primary">
                            {notif.type}
                          </Typography>
                          <Chip label={notif.time} size="small" variant="outlined" sx={{ fontSize: '0.75rem', height: 20 }} />
                        </Box>
                        <Typography variant="body2" color="text.secondary">
                          {notif.message}
                        </Typography>
                      </Box>

                      {/* Actions */}
                      {!notif.read && (
                        <Box sx={{ position: 'absolute', right: 16, top: '50%', transform: 'translateY(-50%)' }}>
                          <Tooltip title="Mark as Read">
                            <IconButton color="primary" onClick={() => handleMarkAsRead(notif.id)}>
                              <DraftsIcon />
                            </IconButton>
                          </Tooltip>
                        </Box>
                      )}
                    </Box>
                  </CardContent>
                </Card>
              </Grid>
            );
          })}
        </Grid>
      )}
    </Box>
  );
};

export default Notifications;
