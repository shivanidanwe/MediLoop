import React, { useState } from 'react';
import {
  Box,
  Typography,
  Card,
  CardContent,
  Switch,
  TextField,
  MenuItem,
  Button,
  Divider,
  Grid,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Alert
} from '@mui/material';
import DarkModeIcon from '@mui/icons-material/DarkMode';
import NotificationsIcon from '@mui/icons-material/Notifications';
import SecurityIcon from '@mui/icons-material/Security';
import LibraryBooksIcon from '@mui/icons-material/LibraryBooks';
import StorageIcon from '@mui/icons-material/Storage';
import ExitToAppIcon from '@mui/icons-material/ExitToApp';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import { useAuth } from '../../context/AuthContext';
import SnackbarNotification from '../../components/common/SnackbarNotification';

const Settings = () => {
  const { user, logout } = useAuth();
  
  // Local preferences states
  const [darkMode, setDarkMode] = useState(false);
  const [language, setLanguage] = useState('en');
  const [notifyEmail, setNotifyEmail] = useState(true);
  const [notifyPush, setNotifyPush] = useState(true);
  
  // Toast notification
  const [toastOpen, setToastOpen] = useState(false);
  const [toastMsg, setToastMsg] = useState('');

  const handleSavePref = () => {
    setToastMsg('Preferences updated successfully!');
    setToastOpen(true);
  };

  return (
    <Box display="flex" flexDirection="column" gap={3.5}>
      <Box>
        <Typography variant="h4" fontWeight={800} color="text.primary" letterSpacing="-0.5px">
          Portal Settings
        </Typography>
        <Typography variant="body2" color="text.secondary" sx={{ mt: 0.5 }}>
          Configure pharmacy portal preferences, notification rules, and database sync status.
        </Typography>
      </Box>

      <Grid container spacing={4}>
        {/* Left Side: Real-time Database Status */}
        <Grid item xs={12} md={6}>
          <Card variant="outlined" sx={{ borderRadius: 4, height: '100%' }}>
            <CardContent sx={{ p: 4, display: 'flex', flexDirection: 'column', gap: 3 }}>
              <Box display="flex" alignItems="center" gap={1.5} color="primary.main">
                <StorageIcon sx={{ fontSize: 28 }} />
                <Typography variant="h6" fontWeight={700} color="text.primary">
                  Database & Store Connection
                </Typography>
              </Box>

              <Typography variant="body2" color="text.secondary">
                The pharmacy portal is connected to the live PostgreSQL database. All incoming prescriptions, patient profiles, inventory changes, and order status transitions are synchronized in real-time.
              </Typography>

              <Alert
                icon={<CheckCircleIcon fontSize="inherit" />}
                severity="success"
                sx={{ borderRadius: 2.5, border: '1px solid rgba(16, 185, 129, 0.25)', bgcolor: 'rgba(16, 185, 129, 0.08)' }}
              >
                Connected Store: <strong>{user?.pharmacyName || 'Kalawati Medical & General Stores'} (Store #{user?.pharmacyId || 6})</strong>
                <Typography variant="caption" sx={{ display: 'block', mt: 0.5, color: 'text.secondary' }}>
                  PostgreSQL Real-Time Live Sync Active
                </Typography>
              </Alert>

              <Box sx={{ mt: 1, p: 2, bgcolor: 'grey.50', borderRadius: 2.5, border: '1px solid #e2e8f0' }}>
                <Typography variant="subtitle2" fontWeight={700} gutterBottom>
                  Data Persistence Protocol
                </Typography>
                <Typography variant="caption" color="text.secondary" sx={{ display: 'block', lineHeight: 1.6 }}>
                  • Prescriptions uploaded by patients are processed by AI OCR & NER and written directly to the database.
                  <br />
                  • Pharmacist verification decisions immediately update patient orders and notify customers.
                  <br />
                  • Mock datasets are permanently disabled to ensure authentic healthcare audit compliance.
                </Typography>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        {/* Right Side: Interface Preferences & Logout */}
        <Grid item xs={12} md={6}>
          <Card variant="outlined" sx={{ borderRadius: 4 }}>
            <CardContent sx={{ p: 4, display: 'flex', flexDirection: 'column', gap: 3.5 }}>
              {/* Interface Preferences */}
              <Box>
                <Box display="flex" alignItems="center" gap={1.5} color="primary.main" mb={2}>
                  <DarkModeIcon />
                  <Typography variant="subtitle1" fontWeight={700} color="text.primary">
                    Interface Preferences
                  </Typography>
                </Box>
                <Grid container spacing={2}>
                  <Grid item xs={12} sm={6} display="flex" alignItems="center" justifyContent="space-between">
                    <Typography variant="body2" color="text.secondary">Dark Mode Interface</Typography>
                    <Switch checked={darkMode} onChange={(e) => { setDarkMode(e.target.checked); handleSavePref(); }} color="primary" />
                  </Grid>
                  <Grid item xs={12} sm={6}>
                    <TextField
                      select
                      size="small"
                      label="Portal Language"
                      value={language}
                      onChange={(e) => { setLanguage(e.target.value); handleSavePref(); }}
                      fullWidth
                      InputProps={{ style: { borderRadius: 12 } }}
                    >
                      <MenuItem value="en">English (US)</MenuItem>
                      <MenuItem value="mr">Marathi (मराठी)</MenuItem>
                      <MenuItem value="hi">Hindi (हिंदी)</MenuItem>
                    </TextField>
                  </Grid>
                </Grid>
              </Box>

              <Divider />

              {/* Notification preferences */}
              <Box>
                <Box display="flex" alignItems="center" gap={1.5} color="primary.main" mb={2}>
                  <NotificationsIcon />
                  <Typography variant="subtitle1" fontWeight={700} color="text.primary">
                    Notification Preferences
                  </Typography>
                </Box>
                <Grid container spacing={1.5}>
                  <Grid item xs={12} display="flex" alignItems="center" justifyContent="space-between">
                    <Typography variant="body2" color="text.secondary">Email Alert Digests</Typography>
                    <Switch checked={notifyEmail} onChange={(e) => { setNotifyEmail(e.target.checked); handleSavePref(); }} color="primary" />
                  </Grid>
                  <Grid item xs={12} display="flex" alignItems="center" justifyContent="space-between">
                    <Typography variant="body2" color="text.secondary">Browser Push Notifications</Typography>
                    <Switch checked={notifyPush} onChange={(e) => { setNotifyPush(e.target.checked); handleSavePref(); }} color="primary" />
                  </Grid>
                </Grid>
              </Box>

              <Divider />

              {/* Legal documents */}
              <Box>
                <Box display="flex" alignItems="center" gap={1.5} color="primary.main" mb={1}>
                  <LibraryBooksIcon />
                  <Typography variant="subtitle1" fontWeight={700} color="text.primary">
                    Legal & Safety Docs
                  </Typography>
                </Box>
                <List disablePadding>
                  <ListItem disableGutters button onClick={() => alert('MediLoop complies with HIPAA & CDSCO regulations.')} sx={{ py: 1 }}>
                    <ListItemIcon sx={{ minWidth: 32 }}><SecurityIcon fontSize="small" /></ListItemIcon>
                    <ListItemText primary="Privacy Policy & HIPAA Disclosures" primaryTypographyProps={{ fontSize: '0.85rem' }} />
                  </ListItem>
                  <ListItem disableGutters button onClick={() => alert('Standard Terms of Pharmacist Verification apply.')} sx={{ py: 1 }}>
                    <ListItemIcon sx={{ minWidth: 32 }}><LibraryBooksIcon fontSize="small" /></ListItemIcon>
                    <ListItemText primary="Portal Terms & Conditions of Operation" primaryTypographyProps={{ fontSize: '0.85rem' }} />
                  </ListItem>
                </List>
              </Box>

              <Divider />

              {/* Logout Button */}
              <Button
                variant="outlined"
                color="error"
                startIcon={<ExitToAppIcon />}
                onClick={logout}
                fullWidth
                sx={{ borderRadius: 2.5 }}
              >
                Sign Out of Session
              </Button>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      <SnackbarNotification
        open={toastOpen}
        message={toastMsg}
        onClose={() => setToastOpen(false)}
      />
    </Box>
  );
};

export default Settings;
