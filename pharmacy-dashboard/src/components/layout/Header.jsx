import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
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
  Tooltip,
  Divider,
  Paper
} from '@mui/material';
import MenuIcon from '@mui/icons-material/Menu';
import NotificationsNoneIcon from '@mui/icons-material/NotificationsNone';
import PersonOutlineIcon from '@mui/icons-material/PersonOutlined';
import SettingsOutlinedIcon from '@mui/icons-material/SettingsOutlined';
import LogoutOutlinedIcon from '@mui/icons-material/LogoutOutlined';
import CircleIcon from '@mui/icons-material/Circle';
import { useAuth } from '../../context/AuthContext';
import { useMockData } from '../../context/MockDataContext';

const Header = ({ toggleSidebar }) => {
  const { user, logout } = useAuth();
  const { mockEnabled } = useMockData();
  const navigate = useNavigate();
  const [anchorEl, setAnchorEl] = useState(null);

  const handleOpenUserMenu = (event) => {
    setAnchorEl(event.currentTarget);
  };

  const handleCloseUserMenu = () => {
    setAnchorEl(null);
  };

  const handleNavigate = (path) => {
    navigate(path);
    handleCloseUserMenu();
  };

  // Simulate notification count
  const unreadCount = mockEnabled ? 2 : 0;

  return (
    <AppBar
      position="sticky"
      elevation={0}
      sx={{
        bgcolor: '#ffffff',
        borderBottom: '1px solid',
        borderColor: 'divider',
        zIndex: (theme) => theme.zIndex.drawer + 1
      }}
    >
      <Toolbar sx={{ justifyContent: 'space-between', px: { xs: 2, sm: 3 } }}>
        {/* Left Elements: Toggle Drawer & Pharmacy details */}
        <Box display="flex" alignItems="center" gap={1.5}>
          <IconButton
            color="inherit"
            aria-label="open drawer"
            edge="start"
            onClick={toggleSidebar}
            sx={{ color: 'text.secondary', mr: 0.5 }}
          >
            <MenuIcon />
          </IconButton>
          <Box>
            <Typography variant="body2" color="text.secondary" fontWeight={500} sx={{ display: { xs: 'none', sm: 'block' } }}>
              Pharmacy Dashboard
            </Typography>
            <Typography variant="subtitle1" color="text.primary" fontWeight={700} lineHeight={1.2}>
              {user?.pharmacyName || 'Pharmacy Name'}
            </Typography>
          </Box>
        </Box>

        {/* Right Elements: Notifications & Profile Avatar */}
        <Box display="flex" alignItems="center" gap={2}>
          {mockEnabled && (
            <Paper
              elevation={0}
              sx={{
                px: 1.5,
                py: 0.5,
                borderRadius: 2.5,
                bgcolor: 'success.lightBg',
                color: 'success.main',
                border: '1px solid',
                borderColor: 'success.lightBorder',
                display: 'inline-flex',
                alignItems: 'center',
                gap: 1
              }}
            >
              <CircleIcon sx={{ fontSize: 8, color: 'success.main' }} />
              <Typography variant="caption" fontWeight={600}>
                Mock Data Active
              </Typography>
            </Paper>
          )}

          <Tooltip title="Notifications">
            <IconButton onClick={() => navigate('/notifications')} sx={{ color: 'text.secondary' }}>
              <Badge badgeContent={unreadCount} color="error" overlap="rectangular">
                <NotificationsNoneIcon />
              </Badge>
            </IconButton>
          </Tooltip>

          {/* User Profile */}
          <Box display="flex" alignItems="center" gap={1.5}>
            <Box sx={{ textAlign: 'right', display: { xs: 'none', md: 'block' } }}>
              <Typography variant="subtitle2" color="text.primary" fontWeight={600}>
                {user?.name || 'Pharmacist Name'}
              </Typography>
              <Typography variant="caption" color="text.secondary" fontWeight={500}>
                {user?.email || 'pharmacist@mediloop.com'}
              </Typography>
            </Box>
            <Tooltip title="Account menu">
              <IconButton onClick={handleOpenUserMenu} sx={{ p: 0 }}>
                <Avatar
                  alt={user?.name}
                  src={user?.photoUrl}
                  sx={{
                    width: 40,
                    height: 40,
                    border: '2px solid',
                    borderColor: 'primary.lightBorder',
                    bgcolor: 'primary.main',
                    color: '#ffffff',
                    fontWeight: 700,
                    fontSize: '1rem'
                  }}
                >
                  {user?.name ? user.name.charAt(0) : 'P'}
                </Avatar>
              </IconButton>
            </Tooltip>

            {/* Profile Dropdown */}
            <Menu
              anchorEl={anchorEl}
              open={Boolean(anchorEl)}
              onClose={handleCloseUserMenu}
              PaperProps={{
                elevation: 0,
                sx: {
                  overflow: 'visible',
                  filter: 'drop-shadow(0px 2px 10px rgba(0,0,0,0.08))',
                  mt: 1.5,
                  borderRadius: 3,
                  width: 200,
                  '& .MuiAvatar-root': {
                    width: 32,
                    height: 32,
                    ml: -0.5,
                    mr: 1
                  }
                }
              }}
              transformOrigin={{ horizontal: 'right', vertical: 'top' }}
              anchorOrigin={{ horizontal: 'right', vertical: 'bottom' }}
            >
              <MenuItem onClick={() => handleNavigate('/profile')} sx={{ py: 1.2 }}>
                <PersonOutlineIcon sx={{ mr: 1.5, color: 'text.secondary' }} /> My Profile
              </MenuItem>
              <MenuItem onClick={() => handleNavigate('/settings')} sx={{ py: 1.2 }}>
                <SettingsOutlinedIcon sx={{ mr: 1.5, color: 'text.secondary' }} /> Settings
              </MenuItem>
              <Divider sx={{ my: 1 }} />
              <MenuItem onClick={logout} sx={{ py: 1.2, color: 'error.main' }}>
                <LogoutOutlinedIcon sx={{ mr: 1.5, color: 'error.main' }} /> Logout
              </MenuItem>
            </Menu>
          </Box>
        </Box>
      </Toolbar>
    </AppBar>
  );
};

export default Header;
