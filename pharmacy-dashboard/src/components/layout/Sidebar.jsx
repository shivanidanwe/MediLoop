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
  IconButton,
  Chip
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
import AllInclusiveIcon from '@mui/icons-material/AllInclusive';
import SmartToyIcon from '@mui/icons-material/SmartToy';
import ChevronLeftIcon from '@mui/icons-material/ChevronLeft';
import CircleIcon from '@mui/icons-material/Circle';
import { useAuth } from '../../context/AuthContext';

const drawerWidth = 264;

const Sidebar = ({ open, toggleDrawer, isMobile }) => {
  const { user, logout } = useAuth();
  const location = useLocation();

  const navSections = [
    {
      title: 'WORKSPACE',
      items: [
        { text: 'Overview', icon: <DashboardIcon fontSize="small" />, path: '/dashboard' },
        { text: 'Prescriptions', icon: <FactCheckIcon fontSize="small" />, path: '/prescriptions' },
        { text: 'Orders', icon: <LocalMallIcon fontSize="small" />, path: '/orders' },
        { text: 'Patients', icon: <PeopleIcon fontSize="small" />, path: '/customers' }
      ]
    },
    {
      title: 'PHARMACY MANAGEMENT',
      items: [
        { text: 'Medicines & Inventory', icon: <MedicationIcon fontSize="small" />, path: '/medicines' }
      ]
    },
    {
      title: 'INTELLIGENCE',
      items: [
        { text: 'AI Agents', icon: <SmartToyIcon fontSize="small" />, path: '/agents' },
        { text: 'Analytics', icon: <AssessmentIcon fontSize="small" />, path: '/reports' },
        { text: 'Notifications', icon: <NotificationsIcon fontSize="small" />, path: '/notifications' }
      ]
    },
    {
      title: 'ACCOUNT',
      items: [
        { text: 'Profile', icon: <PersonIcon fontSize="small" />, path: '/profile' },
        { text: 'Settings', icon: <SettingsIcon fontSize="small" />, path: '/settings' }
      ]
    }
  ];

  const sidebarContent = (
    <Box
      sx={{
        display: 'flex',
        flexDirection: 'column',
        height: '100%',
        bgcolor: '#07152F', // Midnight Navy
        backgroundImage: 'radial-gradient(circle at 10% 20%, rgba(39, 216, 232, 0.08) 0%, transparent 40%)',
        color: '#ffffff'
      }}
    >
      {/* Brand Header */}
      <Box
        sx={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          px: 2.8,
          py: 2.5,
          borderBottom: '1px solid rgba(255, 255, 255, 0.08)'
        }}
      >
        <Box display="flex" alignItems="center" gap={1.6}>
          <Box
            sx={{
              width: 42,
              height: 42,
              borderRadius: 3,
              background: 'linear-gradient(135deg, #477BFF 0%, #27D8E8 100%)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              color: '#ffffff',
              boxShadow: '0 4px 18px rgba(39, 216, 232, 0.35)'
            }}
          >
            <AllInclusiveIcon sx={{ fontSize: 26 }} />
          </Box>
          <Box>
            <Typography variant="h6" fontWeight={900} letterSpacing="-0.5px" sx={{ color: '#ffffff', lineHeight: 1.1 }}>
              Medi<span style={{ color: '#27D8E8' }}>Loop</span>
            </Typography>
            <Typography
              variant="caption"
              sx={{
                color: '#49E5D1',
                fontWeight: 800,
                fontSize: '0.66rem',
                letterSpacing: '1px'
              }}
            >
              AGENTIC PHARMACY
            </Typography>
          </Box>
        </Box>
        {isMobile && (
          <IconButton size="small" onClick={toggleDrawer} sx={{ color: 'rgba(255,255,255,0.7)' }}>
            <ChevronLeftIcon fontSize="small" />
          </IconButton>
        )}
      </Box>

      {/* Navigation Sections */}
      <Box sx={{ flexGrow: 1, overflowY: 'auto', px: 1.8, py: 2 }}>
        {navSections.map((section, sIdx) => (
          <Box key={section.title} sx={{ mb: 2 }}>
            <Typography
              variant="caption"
              sx={{
                px: 1.5,
                mb: 0.8,
                display: 'block',
                fontWeight: 800,
                color: 'rgba(255, 255, 255, 0.4)',
                fontSize: '0.65rem',
                letterSpacing: '0.8px'
              }}
            >
              {section.title}
            </Typography>
            <List disablePadding>
              {section.items.map((item) => {
                const isActive =
                  location.pathname === item.path ||
                  (item.path !== '/dashboard' && location.pathname.startsWith(item.path));

                return (
                  <ListItem key={item.text} disablePadding sx={{ mb: 0.4 }}>
                    <ListItemButton
                      component={NavLink}
                      to={item.path}
                      onClick={isMobile ? toggleDrawer : undefined}
                      sx={{
                        borderRadius: 2.5,
                        py: 0.85,
                        px: 1.6,
                        minHeight: 40,
                        background: isActive
                          ? 'linear-gradient(90deg, rgba(71, 123, 255, 0.28) 0%, rgba(39, 216, 232, 0.12) 100%)'
                          : 'transparent',
                        color: isActive ? '#ffffff' : 'rgba(255, 255, 255, 0.65)',
                        border: isActive ? '1px solid rgba(39, 216, 232, 0.4)' : '1px solid transparent',
                        boxShadow: isActive ? '0 4px 14px rgba(71, 123, 255, 0.18)' : 'none',
                        '&:hover': {
                          background: isActive
                            ? 'linear-gradient(90deg, rgba(71, 123, 255, 0.35) 0%, rgba(39, 216, 232, 0.18) 100%)'
                            : 'rgba(255, 255, 255, 0.05)',
                          color: '#ffffff'
                        },
                        transition: 'all 0.18s ease'
                      }}
                    >
                      <ListItemIcon
                        sx={{
                          color: isActive ? '#27D8E8' : 'rgba(255, 255, 255, 0.55)',
                          minWidth: 32
                        }}
                      >
                        {item.icon}
                      </ListItemIcon>
                      <ListItemText
                        primary={item.text}
                        primaryTypographyProps={{
                          fontSize: '0.84rem',
                          fontWeight: isActive ? 800 : 500,
                          lineHeight: 1.2
                        }}
                      />
                    </ListItemButton>
                  </ListItem>
                );
              })}
            </List>
            {sIdx < navSections.length - 1 && (
              <Divider sx={{ mt: 1.5, borderColor: 'rgba(255, 255, 255, 0.06)' }} />
            )}
          </Box>
        ))}
      </Box>

      {/* Store & Logout Footer */}
      <Box
        sx={{
          p: 1.8,
          borderTop: '1px solid rgba(255, 255, 255, 0.08)',
          bgcolor: 'rgba(0, 0, 0, 0.25)'
        }}
      >
        <Box
          sx={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            bgcolor: 'rgba(255, 255, 255, 0.05)',
            p: 1.3,
            borderRadius: 2.5,
            border: '1px solid rgba(255, 255, 255, 0.08)',
            mb: 1
          }}
        >
          <Box display="flex" alignItems="center" gap={1}>
            <CircleIcon sx={{ fontSize: 8, color: '#10b981' }} />
            <Box>
              <Typography variant="caption" sx={{ fontWeight: 800, color: '#ffffff', display: 'block', lineHeight: 1 }}>
                Store #{user?.pharmacyId || '6'}
              </Typography>
              <Typography variant="caption" sx={{ color: 'rgba(255, 255, 255, 0.55)', fontSize: '0.68rem' }}>
                PostgreSQL Live Sync
              </Typography>
            </Box>
          </Box>
          <Chip
            label="Live"
            size="small"
            sx={{
              height: 18,
              fontSize: '0.65rem',
              fontWeight: 800,
              bgcolor: 'rgba(16, 185, 129, 0.2)',
              color: '#10b981',
              border: '1px solid rgba(16, 185, 129, 0.4)'
            }}
          />
        </Box>

        <ListItemButton
          onClick={logout}
          sx={{
            borderRadius: 2,
            py: 0.8,
            px: 1.5,
            color: '#FF8C83',
            bgcolor: 'transparent',
            '&:hover': {
              bgcolor: 'rgba(255, 140, 131, 0.1)',
              color: '#ff6b6b'
            },
            transition: 'all 0.15s ease'
          }}
        >
          <ListItemIcon sx={{ color: '#FF8C83', minWidth: 32 }}>
            <ExitToAppIcon fontSize="small" />
          </ListItemIcon>
          <ListItemText
            primary="Sign Out"
            primaryTypographyProps={{
              fontSize: '0.84rem',
              fontWeight: 700
            }}
          />
        </ListItemButton>
      </Box>
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
          borderRight: '1px solid rgba(255, 255, 255, 0.08)',
          boxShadow: '4px 0 24px rgba(7, 21, 47, 0.15)'
        },
        transition: 'width 0.2s ease-in-out'
      }}
    >
      {sidebarContent}
    </Drawer>
  );
};

export default Sidebar;
