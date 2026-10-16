import React, { useState } from 'react';
import {
  Box,
  Typography,
  Card,
  CardContent,
  FormControlLabel,
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
import LanguageIcon from '@mui/icons-material/Language';
import SecurityIcon from '@mui/icons-material/Security';
import LibraryBooksIcon from '@mui/icons-material/LibraryBooks';
import DatabaseIcon from '@mui/icons-material/Storage';
import ExitToAppIcon from '@mui/icons-material/ExitToApp';
import { useMockData } from '../../context/MockDataContext';
import { useAuth } from '../../context/AuthContext';
import SnackbarNotification from '../../components/common/SnackbarNotification';

const Settings = () => {
  const { mockEnabled, setMockEnabled } = useMockData();
  const { logout } = useAuth();
  
  // Local preferences states
  const [darkMode, setDarkMode] = useState(false);
  const [language, setLanguage] = useState('en');
  const [notifyEmail, setNotifyEmail] = useState(true);
  const [notifyPush, setNotifyPush] = useState(true);
  
  // Toast notification
  const [toastOpen, setToastOpen] = useState(false);
  const [toastMsg, setToastMsg] = useState('');

  const handleMockToggle = (checked) => {
    setMockEnabled(checked);
    const msg = checked
      ? 'Mock Database Enabled. Tables, cards, and charts now render with placeholder datasets.'
      : 'Mock Database Disabled. App is now in API-Ready Mode (empty/pending states).';
    setToastMsg(msg);
    setToastOpen(true);
  };

  return (
    <Box display="flex" flexDirection="column" gap={3.5}>
      <Box>
        <Typography variant="h4" fontWeight={800} color="text.primary" letterSpacing="-0.5px">
          Portal Settings
        </Typography>
        <Typography variant="body2" color="text.secondary" sx={{ mt: 0.5 }}>
          Configure system behaviors, dark mode settings, notification frequencies, and developer mock databases.
        </Typography>
      </Box>

      <Grid container spacing={4}>
        {/* Left Side: Mock Database Controller & Status */}
        <Grid item xs={12} md={6}>
          <Card variant="outlined" sx={{ borderRadius: 4, height: '100%' }}>
            <CardContent sx={{ p: 4, display: 'flex', flexDirection: 'column', gap: 3 }}>
              <Box display="flex" alignItems="center" gap={1.5} color="primary.main">
                <DatabaseIcon sx={{ fontSize: 28 }} />
                <Typography variant="h6" fontWeight={700} color="text.primary">
                  Mock Integration Controls
                </Typography>
              </Box>

              <Typography variant="body2" color="text.secondary">
                To test how the pharmacy dashboard consumes API data, toggle the switch below. When disabled, the dashboard simulates empty records. When enabled, it returns placeholder lists.
              </Typography>

              <Alert
                severity={mockEnabled ? 'success' : 'info'}
                sx={{ borderRadius: 2.5, border: '1px solid', borderColor: mockEnabled ? 'success.lightBorder' : 'info.lightBorder' }}
              >
                Current State: <strong>{mockEnabled ? 'MOCK DATABASE CONNECTED' : 'API-READY (EMPTY STATE)'}</strong>
              </Alert>

              <Box display="flex" alignItems="center" justifyContent="space-between" sx={{ mt: 1 }}>
                <Typography variant="subtitle2" fontWeight={600}>
                  Enable Mock Database Mode
                </Typography>
                <Switch
                  checked={mockEnabled}
                  onChange={(e) => handleMockToggle(e.target.checked)}
                  color="primary"
                />
              </Box>

              <Divider sx={{ my: 1 }} />

              <Typography variant="caption" color="text.secondary">
                Note: In-memory updates (like verifying prescription statuses or adding medicines) persist only while the browser tab remains open.
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        {/* Right Side: Interface Preference fields */}
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
                    <Switch checked={darkMode} onChange={(e) => setDarkMode(e.target.checked)} color="primary" />
                  </Grid>
                  <Grid item xs={12} sm={6}>
                    <TextField
                      select
                      size="small"
                      label="Portal Language"
                      value={language}
                      onChange={(e) => setLanguage(e.target.value)}
                      fullWidth
                      InputProps={{ style: { borderRadius: 12 } }}
                    >
                      <MenuItem value="en">English (US)</MenuItem>
                      <MenuItem value="es">Español</MenuItem>
                      <MenuItem value="fr">Français</MenuItem>
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
                    <Switch checked={notifyEmail} onChange={(e) => setNotifyEmail(e.target.checked)} color="primary" />
                  </Grid>
                  <Grid item xs={12} display="flex" alignItems="center" justifyContent="space-between">
                    <Typography variant="body2" color="text.secondary">Browser Push Notifications</Typography>
                    <Switch checked={notifyPush} onChange={(e) => setNotifyPush(e.target.checked)} color="primary" />
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
                  <ListItem disableGutters button onClick={() => alert('Displaying Privacy Policy (Placeholder)')} sx={{ py: 1 }}>
                    <ListItemIcon sx={{ minWidth: 32 }}><SecurityIcon fontSize="small" /></ListItemIcon>
                    <ListItemText primary="Privacy Policy & HIPAA Disclosures" primaryTypographyProps={{ fontSize: '0.85rem' }} />
                  </ListItem>
                  <ListItem disableGutters button onClick={() => alert('Displaying Terms of Service (Placeholder)')} sx={{ py: 1 }}>
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
