import React from 'react';
import { NavLink, useLocation } from 'react-router-dom';
import {
  Box,
  Drawer,
  List,
  ListItem,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  Typography,
  Divider,
  IconButton
} from '@mui/material';
import DashboardIcon from '@mui/icons-material/Dashboard';
import FactCheckIcon from '@mui/icons-material/FactCheck';
import LocalMallIcon from '@mui/icons-material/LocalMall';
import MedicationIcon from '@mui/icons-material/Medication';
import PeopleIcon from '@mui/icons-material/People';
import NotificationsIcon from '@mui/icons-material/Notifications';
import AssessmentIcon from '@mui/icons-material/Assessment';
import PersonIcon from '@mui/icons-material/Person';
import SettingsIcon from '@mui/icons-material/Settings';
import ExitToAppIcon from '@mui/icons-material/ExitToApp';
import LocalHospitalIcon from '@mui/icons-material/LocalHospital';
import ChevronLeftIcon from '@mui/icons-material/ChevronLeft';
import { useAuth } from '../../context/AuthContext';

const drawerWidth = 260;

const Sidebar = ({ open, toggleDrawer, isMobile }) => {
  const { logout } = useAuth();
  const location = useLocation();

  const menuItems = [
    { text: 'Dashboard', icon: <DashboardIcon />, path: '/dashboard' },
    { text: 'Prescription Verification', icon: <FactCheckIcon />, path: '/prescriptions' },
    { text: 'Orders', icon: <LocalMallIcon />, path: '/orders' },
    { text: 'Medicines', icon: <MedicationIcon />, path: '/medicines' },
    { text: 'Customers', icon: <PeopleIcon />, path: '/customers' },
    { text: 'Notifications', icon: <NotificationsIcon />, path: '/notifications' },
    { text: 'Reports', icon: <AssessmentIcon />, path: '/reports' },
    { text: 'Profile', icon: <PersonIcon />, path: '/profile' },
    { text: 'Settings', icon: <SettingsIcon />, path: '/settings' }
  ];

  const sidebarContent = (
    <Box sx={{ display: 'flex', flexDirection: 'column', height: '100%', bgcolor: '#ffffff' }}>
      {/* Brand Header */}
      <Box
        sx={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          px: 2.5,
          py: 3,
          color: 'primary.main'
        }}
      >
        <Box display="flex" alignItems="center" gap={1.5}>
          <LocalHospitalIcon sx={{ fontSize: 32 }} />
          <Typography variant="h5" fontWeight={800} letterSpacing="-0.5px">
            MediLoop
          </Typography>
        </Box>
        {isMobile && (
          <IconButton onClick={toggleDrawer}>
            <ChevronLeftIcon />
          </IconButton>
        )}
      </Box>

      <Divider sx={{ opacity: 0.6 }} />

      {/* Nav List */}
      <List sx={{ px: 1.5, py: 2, flexGrow: 1 }} disablePadding>
        {menuItems.map((item) => {
          const isActive = location.pathname === item.path || (item.path !== '/dashboard' && location.pathname.startsWith(item.path));
          return (
            <ListItem key={item.text} disablePadding sx={{ mb: 0.6 }}>
              <ListItemButton
                component={NavLink}
                to={item.path}
                onClick={isMobile ? toggleDrawer : undefined}
                sx={{
                  borderRadius: 3,
                  py: 1.2,
                  px: 2,
                  bgcolor: isActive ? 'primary.lightBg' : 'transparent',
                  color: isActive ? 'primary.main' : 'text.secondary',
                  '&:hover': {
                    bgcolor: isActive ? 'primary.lightBg' : 'grey.50',
                    color: isActive ? 'primary.main' : 'text.primary'
                  },
                  transition: 'all 0.2s ease'
                }}
              >
                <ListItemIcon
                  sx={{
                    color: isActive ? 'primary.main' : 'text.secondary',
                    minWidth: 40
                  }}
                >
                  {item.icon}
                </ListItemIcon>
                <ListItemText
                  primary={item.text}
                  primaryTypographyProps={{
                    fontSize: '0.9rem',
                    fontWeight: isActive ? 600 : 500
                  }}
                />
              </ListItemButton>
            </ListItem>
          );
        })}
      </List>

      <Divider sx={{ opacity: 0.6 }} />

      {/* Logout Action */}
      <List sx={{ px: 1.5, py: 2 }} disablePadding>
        <ListItem disablePadding>
          <ListItemButton
            onClick={logout}
            sx={{
              borderRadius: 3,
              py: 1.2,
              px: 2,
              color: 'error.main',
              '&:hover': {
                bgcolor: 'error.lighterBg',
                color: 'error.dark'
              },
              transition: 'all 0.2s ease'
            }}
          >
            <ListItemIcon sx={{ color: 'error.main', minWidth: 40 }}>
              <ExitToAppIcon />
            </ListItemIcon>
            <ListItemText
              primary="Logout"
              primaryTypographyProps={{
                fontSize: '0.9rem',
                fontWeight: 600
              }}
            />
          </ListItemButton>
        </ListItem>
      </List>
    </Box>
  );

  if (isMobile) {
    return (
      <Drawer
        variant="temporary"
        open={open}
        onClose={toggleDrawer}
        ModalProps={{ keepMounted: true }}
        sx={{
          '& .MuiDrawer-paper': { boxSizing: 'border-box', width: drawerWidth }
        }}
      >
        {sidebarContent}
      </Drawer>
    );
  }

  return (
    <Drawer
      variant="persistent"
      open={open}
      sx={{
        width: open ? drawerWidth : 0,
        flexShrink: 0,
        '& .MuiDrawer-paper': {
          boxSizing: 'border-box',
          width: drawerWidth,
          borderRight: '1px solid',
          borderColor: 'divider',
          boxShadow: '0px 4px 20px rgba(0, 0, 0, 0.02)'
        },
        transition: 'width 0.22s ease-in-out'
      }}
    >
      {sidebarContent}
    </Drawer>
  );
};

export default Sidebar;
