import React, { useState, useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import {
  AppBar,
  Toolbar,
  IconButton,
  Typography,
  Box,
  Badge,
  Avatar,
  Menu,
  MenuItem,
  Popover,
  Tooltip,
  Divider,
  Chip,
  Stack,
  TextField,
  InputAdornment,
  Breadcrumbs,
  Link,
  Button
} from '@mui/material';
import MenuIcon from '@mui/icons-material/Menu';
import NotificationsNoneIcon from '@mui/icons-material/NotificationsNone';
import PersonOutlineIcon from '@mui/icons-material/PersonOutlined';
import SettingsOutlinedIcon from '@mui/icons-material/SettingsOutlined';
import LogoutOutlinedIcon from '@mui/icons-material/LogoutOutlined';
import StorefrontIcon from '@mui/icons-material/Storefront';
import StorageIcon from '@mui/icons-material/Storage';
import SmartToyIcon from '@mui/icons-material/SmartToy';
import SearchIcon from '@mui/icons-material/Search';
import NavigateNextIcon from '@mui/icons-material/NavigateNext';
import FactCheckIcon from '@mui/icons-material/FactCheck';
import LocalMallIcon from '@mui/icons-material/LocalMall';
import InventoryIcon from '@mui/icons-material/Inventory';
import WarningAmberIcon from '@mui/icons-material/WarningAmber';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import TuneIcon from '@mui/icons-material/Tune';
import CircleIcon from '@mui/icons-material/Circle';
import { useAuth } from '../../context/AuthContext';
import { useNotificationService } from '../../services/notificationService';
import NotificationPreferencesDialog from '../dialogs/NotificationPreferencesDialog';

const getPageMeta = (pathname) => {
  if (pathname.includes('/prescriptions/')) {
    return { title: 'Prescription Review', section: 'Workspace', path: '/prescriptions' };
  }
  switch (pathname) {
    case '/dashboard':
      return { title: 'Operational Overview', section: 'Workspace', path: '/dashboard' };
    case '/prescriptions':
      return { title: 'Prescription Verification', section: 'Workspace', path: '/prescriptions' };
    case '/orders':
      return { title: 'Order Fulfillment Pipeline', section: 'Workspace', path: '/orders' };
    case '/customers':
      return { title: 'Patient Directory', section: 'Workspace', path: '/customers' };
    case '/medicines':
      return { title: 'Medicine Catalog & Inventory', section: 'Pharmacy Management', path: '/medicines' };
    case '/agents':
      return { title: 'AI Agent Architecture', section: 'Intelligence', path: '/agents' };
    case '/reports':
      return { title: 'Performance Analytics', section: 'Intelligence', path: '/reports' };
    case '/notifications':
      return { title: 'Dispatch & Safety Alerts', section: 'Intelligence', path: '/notifications' };
    case '/profile':
      return { title: 'Pharmacist Profile', section: 'Account', path: '/profile' };
    case '/settings':
      return { title: 'Dispensary Settings', section: 'Account', path: '/settings' };
    default:
      return { title: 'Pharmacist Portal', section: 'Workspace', path: '/dashboard' };
  }
};

const Header = ({ toggleSidebar }) => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const { getNotifications, getUnreadCount, markAsRead, markAllAsRead } = useNotificationService();

  const [anchorEl, setAnchorEl] = useState(null);
  const [notifAnchorEl, setNotifAnchorEl] = useState(null);
  const [unreadCount, setUnreadCount] = useState(0);
  const [notificationsList, setNotificationsList] = useState([]);
  const [prefsOpen, setPrefsOpen] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');

  const meta = getPageMeta(location.pathname);

  const fetchNotifs = async () => {
    try {
      const [list, count] = await Promise.all([
        getNotifications(10),
        getUnreadCount()
      ]);
      if (Array.isArray(list)) setNotificationsList(list);
      setUnreadCount(typeof count === 'number' ? count : 0);
    } catch (_) {}
  };

  useEffect(() => {
    fetchNotifs();
    const interval = setInterval(fetchNotifs, 8000); // Poll every 8s for live notifications
    return () => clearInterval(interval);
  }, [location.pathname]);

  const handleOpenUserMenu = (event) => setAnchorEl(event.currentTarget);
  const handleCloseUserMenu = () => setAnchorEl(null);

  const handleOpenNotifPopover = (event) => {
    setNotifAnchorEl(event.currentTarget);
    fetchNotifs();
  };
  const handleCloseNotifPopover = () => setNotifAnchorEl(null);

  const handleNavigate = (path) => {
    navigate(path);
    handleCloseUserMenu();
  };

  const handleLogout = () => {
    handleCloseUserMenu();
    logout();
    navigate('/login', { replace: true });
  };

  const handleSearchSubmit = (e) => {
    e.preventDefault();
    const query = searchQuery.trim().toLowerCase();
    if (!query) return;

    if (query.includes('rx') || query.includes('presc')) {
      navigate('/prescriptions');
    } else if (query.includes('ord')) {
      navigate('/orders');
    } else if (query.includes('patient') || query.includes('cust')) {
      navigate('/customers');
    } else if (query.includes('agent') || query.includes('ai')) {
      navigate('/agents');
    } else {
      navigate('/medicines');
    }
    setSearchQuery('');
  };

  const handleNotificationClick = async (notif) => {
    if (!notif.read) {
      await markAsRead(notif.id);
      fetchNotifs();
    }
    handleCloseNotifPopover();
    if (notif.actionUrl) {
      navigate(notif.actionUrl);
    } else if (notif.category === 'prescription') {
      navigate('/prescriptions');
    } else if (notif.category === 'order') {
      navigate('/orders');
    } else {
      navigate('/notifications');
    }
  };

  const handleMarkAll = async () => {
    await markAllAsRead();
    fetchNotifs();
  };

  const getNotifCategoryIcon = (category) => {
    switch (category) {
      case 'prescription':
        return <FactCheckIcon sx={{ fontSize: 18, color: '#f59e0b' }} />;
      case 'order':
        return <LocalMallIcon sx={{ fontSize: 18, color: '#3b82f6' }} />;
      case 'inventory':
        return <InventoryIcon sx={{ fontSize: 18, color: '#10b981' }} />;
      default:
        return <WarningAmberIcon sx={{ fontSize: 18, color: '#8b5cf6' }} />;
    }
  };

  const userInitials = user?.name
    ? user.name
        .split(' ')
        .map((n) => n[0])
        .join('')
        .toUpperCase()
        .slice(0, 2)
    : 'DR';

  return (
    <AppBar
      position="sticky"
      elevation={0}
      sx={{
        backgroundColor: 'rgba(255, 255, 255, 0.85)',
        backdropFilter: 'blur(24px) saturate(190%)',
        borderBottom: '1px solid rgba(226, 232, 240, 0.85)',
        color: '#07152F',
        zIndex: (theme) => theme.zIndex.drawer + 1,
        transition: 'all 0.25s cubic-bezier(0.4, 0, 0.2, 1)'
      }}
    >
      <Toolbar sx={{ justifyContent: 'space-between', px: { xs: 2, sm: 3 }, minHeight: 64 }}>
        {/* Left Side: Mobile toggle + Breadcrumb Hierarchy */}
        <Stack direction="row" spacing={1.5} alignItems="center">
          <IconButton
            color="inherit"
            edge="start"
            onClick={toggleSidebar}
            sx={{
              display: { md: 'none' },
              border: '1px solid #E2E8F0',
              borderRadius: 2.5,
              p: 0.8
            }}
          >
            <MenuIcon fontSize="small" />
          </IconButton>

          <Box>
            <Breadcrumbs
              separator={<NavigateNextIcon sx={{ fontSize: 13, color: '#94A3B8' }} />}
              sx={{ fontSize: '0.72rem', '& a': { color: '#64748B', textDecoration: 'none' } }}
            >
              <Link
                onClick={() => navigate('/dashboard')}
                sx={{ cursor: 'pointer', fontWeight: 600, '&:hover': { color: '#477BFF' } }}
              >
                MediLoop
              </Link>
              <Typography sx={{ fontSize: '0.72rem', fontWeight: 600, color: '#94A3B8' }}>
                {meta.section}
              </Typography>
            </Breadcrumbs>
            <Typography
              variant="h6"
              fontWeight={800}
              sx={{
                fontSize: { xs: '0.95rem', sm: '1.08rem' },
                letterSpacing: '-0.3px',
                lineHeight: 1.2,
                color: '#07152F'
              }}
            >
              {meta.title}
            </Typography>
          </Box>
        </Stack>

        {/* Center: Omni Search Bar */}
        <Box
          component="form"
          onSubmit={handleSearchSubmit}
          sx={{
            display: { xs: 'none', lg: 'block' },
            width: '320px',
            maxWidth: '400px'
          }}
        >
          <TextField
            size="small"
            fullWidth
            placeholder="Quick search medicines, orders, patients..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            InputProps={{
              startAdornment: (
                <InputAdornment position="start">
                  <SearchIcon sx={{ color: '#94A3B8', fontSize: 18 }} />
                </InputAdornment>
              ),
              sx: {
                borderRadius: 3,
                bgcolor: '#F8FAFC',
                fontSize: '0.82rem',
                border: '1px solid #E2E8F0',
                '& fieldset': { border: 'none' },
                '&:hover': { bgcolor: '#ffffff' }
              }
            }}
          />
        </Box>

        {/* Right Elements: Store badge, AI Monitor, Alerts & Profile */}
        <Stack direction="row" spacing={1.5} alignItems="center">
          {/* Store Info Pill */}
          <Box
            sx={{
              display: { xs: 'none', sm: 'flex' },
              alignItems: 'center',
              gap: 1.2,
              bgcolor: 'rgba(71, 123, 255, 0.06)',
              border: '1.2px solid rgba(71, 123, 255, 0.2)',
              borderRadius: 2.5,
              px: 1.5,
              py: 0.6
            }}
          >
            <StorefrontIcon sx={{ color: '#477BFF', fontSize: 18 }} />
            <Box>
              <Typography
                variant="caption"
                sx={{
                  color: '#477BFF',
                  fontWeight: 800,
                  textTransform: 'uppercase',
                  letterSpacing: '0.5px',
                  display: 'block',
                  fontSize: '0.64rem',
                  lineHeight: 1
                }}
              >
                STORE #{user?.pharmacyId || '6'}
              </Typography>
              <Typography
                variant="subtitle2"
                sx={{
                  color: '#07152F',
                  fontWeight: 800,
                  fontSize: '0.78rem',
                  lineHeight: 1.1
                }}
              >
                {user?.pharmacyName ? user.pharmacyName.split(' ')[0] : 'Pandharpur'}
              </Typography>
            </Box>
          </Box>

          <Chip
            icon={<SmartToyIcon sx={{ fontSize: '14px !important', color: '#27D8E8 !important' }} />}
            label="9 AI Agents"
            size="small"
            onClick={() => navigate('/agents')}
            sx={{
              bgcolor: 'rgba(39, 216, 232, 0.1)',
              color: '#0891b2',
              fontWeight: 800,
              fontSize: '0.72rem',
              height: 28,
              border: '1px solid rgba(39, 216, 232, 0.3)',
              cursor: 'pointer',
              display: { xs: 'none', md: 'inline-flex' },
              '&:hover': { bgcolor: 'rgba(39, 216, 232, 0.18)' }
            }}
          />

          <Chip
            icon={<StorageIcon sx={{ fontSize: '13px !important', color: '#10b981 !important' }} />}
            label="Live PostgreSQL"
            size="small"
            sx={{
              bgcolor: 'rgba(16, 185, 129, 0.08)',
              color: '#059669',
              fontWeight: 800,
              fontSize: '0.7rem',
              height: 28,
              border: '1px solid rgba(16, 185, 129, 0.25)',
              display: { xs: 'none', xl: 'inline-flex' }
            }}
          />

          {/* Interactive Notification Bell */}
          <Tooltip title="Dispensary Notifications & Live Alerts">
            <IconButton
              size="small"
              onClick={handleOpenNotifPopover}
              sx={{
                p: 0.9,
                border: '1.2px solid rgba(226, 232, 240, 0.9)',
                borderRadius: 2.5,
                color: '#07152F',
                bgcolor: 'rgba(255, 255, 255, 0.7)',
                '&:hover': { bgcolor: '#ffffff', borderColor: '#477BFF' }
              }}
            >
              <Badge badgeContent={unreadCount} color="error" max={99}>
                <NotificationsNoneIcon fontSize="small" />
              </Badge>
            </IconButton>
          </Tooltip>

          {/* User Profile Pill */}
          <Box
            onClick={handleOpenUserMenu}
            sx={{
              display: 'flex',
              alignItems: 'center',
              gap: 1.2,
              pl: 0.8,
              pr: 1.6,
              py: 0.45,
              border: '1.2px solid rgba(226, 232, 240, 0.9)',
              borderRadius: 3,
              cursor: 'pointer',
              bgcolor: 'rgba(255, 255, 255, 0.7)',
              transition: 'all 0.18s ease',
              '&:hover': {
                bgcolor: '#ffffff',
                borderColor: '#477BFF',
                boxShadow: '0 4px 12px rgba(71, 123, 255, 0.12)'
              }
            }}
          >
            <Avatar
              sx={{
                width: 34,
                height: 34,
                background: 'linear-gradient(135deg, #477BFF 0%, #27D8E8 100%)',
                color: '#ffffff',
                fontWeight: 800,
                fontSize: '0.82rem'
              }}
            >
              {userInitials}
            </Avatar>
            <Box sx={{ display: { xs: 'none', md: 'block' } }}>
              <Typography variant="body2" fontWeight={800} color="#07152F" sx={{ fontSize: '0.82rem', lineHeight: 1.1 }}>
                {user?.name || 'Dr. Pharmacist'}
              </Typography>
              <Typography variant="caption" sx={{ color: '#64748B', fontSize: '0.68rem', fontWeight: 600 }}>
                Licensed Dispenser
              </Typography>
            </Box>
          </Box>

          {/* Profile Dropdown Menu */}
          <Menu
            anchorEl={anchorEl}
            open={Boolean(anchorEl)}
            onClose={handleCloseUserMenu}
            PaperProps={{
              sx: {
                borderRadius: 3,
                minWidth: 220,
                mt: 1.2,
                boxShadow: '0 12px 32px rgba(7, 21, 47, 0.12)',
                border: '1px solid #E2E8F0',
                p: 0.5
              }
            }}
          >
            <Box sx={{ px: 2, py: 1.5 }}>
              <Typography variant="subtitle2" fontWeight={800} color="#07152F">
                {user?.name || 'Dr. Pharmacist'}
              </Typography>
              <Typography variant="caption" color="text.secondary">
                {user?.email || 'pharmacist@mediloop.com'}
              </Typography>
            </Box>
            <Divider sx={{ my: 0.5 }} />
            <MenuItem onClick={() => handleNavigate('/profile')} sx={{ py: 1, borderRadius: 2, fontSize: '0.85rem' }}>
              <PersonOutlineIcon fontSize="small" sx={{ mr: 1.5, color: '#477BFF' }} />
              Profile Settings
            </MenuItem>
            <MenuItem onClick={() => handleNavigate('/agents')} sx={{ py: 1, borderRadius: 2, fontSize: '0.85rem' }}>
              <SmartToyIcon fontSize="small" sx={{ mr: 1.5, color: '#27D8E8' }} />
              AI Agent Console
            </MenuItem>
            <MenuItem onClick={() => handleNavigate('/settings')} sx={{ py: 1, borderRadius: 2, fontSize: '0.85rem' }}>
              <SettingsOutlinedIcon fontSize="small" sx={{ mr: 1.5, color: '#8865F7' }} />
              Dispensary Config
            </MenuItem>
            <Divider sx={{ my: 0.5 }} />
            <MenuItem onClick={handleLogout} sx={{ py: 1, borderRadius: 2, fontSize: '0.85rem', color: '#FF8C83' }}>
              <LogoutOutlinedIcon fontSize="small" sx={{ mr: 1.5, color: '#FF8C83' }} />
              Sign Out
            </MenuItem>
          </Menu>

          {/* Interactive Notifications Popover */}
          <Popover
            open={Boolean(notifAnchorEl)}
            anchorEl={notifAnchorEl}
            onClose={handleCloseNotifPopover}
            anchorOrigin={{ vertical: 'bottom', horizontal: 'right' }}
            transformOrigin={{ vertical: 'top', horizontal: 'right' }}
            PaperProps={{
              sx: {
                width: 380,
                maxHeight: 520,
                borderRadius: 3.5,
                mt: 1.2,
                boxShadow: '0 16px 40px rgba(7, 21, 47, 0.16)',
                border: '1px solid #E2E8F0',
                display: 'flex',
                flexDirection: 'column'
              }
            }}
          >
            {/* Popover Header */}
            <Box sx={{ p: 2, borderBottom: '1px solid #e2e8f0', bgcolor: '#f8fafc', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <Stack direction="row" spacing={1} alignItems="center">
                <Typography variant="subtitle1" fontWeight={800} color="#07152F">
                  Notifications
                </Typography>
                {unreadCount > 0 && (
                  <Chip label={`${unreadCount} New`} size="small" color="error" sx={{ height: 20, fontSize: '0.65rem', fontWeight: 800 }} />
                )}
              </Stack>
              <Stack direction="row" spacing={0.5}>
                {unreadCount > 0 && (
                  <Button size="small" onClick={handleMarkAll} sx={{ fontSize: '0.72rem', fontWeight: 700, textTransform: 'none' }}>
                    Mark all read
                  </Button>
                )}
                <Tooltip title="Alert Preferences">
                  <IconButton size="small" onClick={() => { handleCloseNotifPopover(); setPrefsOpen(true); }}>
                    <TuneIcon fontSize="small" />
                  </IconButton>
                </Tooltip>
              </Stack>
            </Box>

            {/* Notifications List */}
            <Box sx={{ overflowY: 'auto', p: 1, flex: 1 }}>
              {notificationsList.length === 0 ? (
                <Box py={4} textAlign="center">
                  <Typography variant="body2" color="text.secondary">
                    No active notifications for this pharmacy.
                  </Typography>
                </Box>
              ) : (
                notificationsList.map((notif) => (
                  <Box
                    key={notif.id}
                    onClick={() => handleNotificationClick(notif)}
                    sx={{
                      p: 1.5,
                      borderRadius: 2,
                      cursor: 'pointer',
                      mb: 0.5,
                      bgcolor: notif.read ? 'transparent' : 'rgba(59, 130, 246, 0.05)',
                      border: notif.read ? '1px solid transparent' : '1px solid rgba(59, 130, 246, 0.2)',
                      '&:hover': { bgcolor: '#f8fafc' }
                    }}
                  >
                    <Box display="flex" gap={1.2} alignItems="flex-start">
                      <Box sx={{ mt: 0.3 }}>
                        {getNotifCategoryIcon(notif.category)}
                      </Box>
                      <Box flex={1}>
                        <Box display="flex" justifyContent="space-between" alignItems="center">
                          <Typography variant="body2" fontWeight={notif.read ? 600 : 800} color="#07152F" sx={{ fontSize: '0.82rem' }}>
                            {notif.title}
                          </Typography>
                          {!notif.read && (
                            <CircleIcon sx={{ fontSize: 8, color: '#3b82f6' }} />
                          )}
                        </Box>
                        <Typography variant="caption" color="text.secondary" sx={{ display: 'block', fontSize: '0.74rem', mt: 0.3 }}>
                          {notif.message}
                        </Typography>
                        <Typography variant="caption" color="#94a3b8" sx={{ fontSize: '0.68rem', mt: 0.5, display: 'block' }}>
                          {notif.timeAgo || notif.time || 'Just now'}
                        </Typography>
                      </Box>
                    </Box>
                  </Box>
                ))
              )}
            </Box>

            {/* Popover Footer */}
            <Box sx={{ p: 1.5, borderTop: '1px solid #e2e8f0', bgcolor: '#f8fafc', display: 'flex', justifyContent: 'center' }}>
              <Button
                size="small"
                fullWidth
                onClick={() => {
                  handleCloseNotifPopover();
                  navigate('/notifications');
                }}
                sx={{ textTransform: 'none', fontWeight: 700, fontSize: '0.8rem' }}
              >
                View All Activity & Safety Alerts
              </Button>
            </Box>
          </Popover>

          {/* Preferences Dialog */}
          <NotificationPreferencesDialog
            open={prefsOpen}
            onClose={() => setPrefsOpen(false)}
          />
        </Stack>
      </Toolbar>
    </AppBar>
  );
};

export default Header;
