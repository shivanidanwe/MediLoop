import React, { useState, useEffect } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Box,
  Typography,
  Button,
  Switch,
  FormControlLabel,
  Paper,
  Divider,
  IconButton,
  Alert,
  CircularProgress,
  Stack
} from '@mui/material';
import CloseIcon from '@mui/icons-material/Close';
import NotificationsIcon from '@mui/icons-material/Notifications';
import FactCheckIcon from '@mui/icons-material/FactCheck';
import LocalMallIcon from '@mui/icons-material/LocalMall';
import InventoryIcon from '@mui/icons-material/Inventory';
import WarningAmberIcon from '@mui/icons-material/WarningAmber';
import VolumeUpIcon from '@mui/icons-material/VolumeUp';
import { useNotificationService } from '../../services/notificationService';

const NotificationPreferencesDialog = ({ open, onClose }) => {
  const { getPreferences, savePreferences } = useNotificationService();

  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [successMsg, setSuccessMsg] = useState('');
  const [prefs, setPrefs] = useState({
    new_prescription: true,
    new_orders: true,
    low_stock: true,
    out_of_stock: true,
    new_stock: true,
    expiry_alerts: true,
    order_updates: true,
    sound_enabled: true
  });

  useEffect(() => {
    if (open) {
      loadPrefs();
    }
  }, [open]);

  const loadPrefs = async () => {
    setLoading(true);
    setSuccessMsg('');
    const data = await getPreferences();
    if (data) {
      setPrefs({
        new_prescription: data.new_prescription ?? true,
        new_orders: data.new_orders ?? true,
        low_stock: data.low_stock ?? true,
        out_of_stock: data.out_of_stock ?? true,
        new_stock: data.new_stock ?? true,
        expiry_alerts: data.expiry_alerts ?? true,
        order_updates: data.order_updates ?? true,
        sound_enabled: data.sound_enabled ?? true
      });
    }
    setLoading(false);
  };

  const handleToggle = (key) => {
    setPrefs(prev => ({ ...prev, [key]: !prev[key] }));
  };

  const handleSave = async () => {
    setSaving(true);
    const res = await savePreferences(prefs);
    setSaving(false);
    if (res.success) {
      setSuccessMsg('Notification preferences updated!');
      setTimeout(() => {
        onClose();
      }, 700);
    }
  };

  return (
    <Dialog
      open={open}
      onClose={onClose}
      maxWidth="sm"
      fullWidth
      PaperProps={{ sx: { borderRadius: 3.5 } }}
    >
      <DialogTitle sx={{ px: 3, py: 2, borderBottom: '1px solid #e2e8f0', bgcolor: '#f8fafc', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <Stack direction="row" spacing={1.2} alignItems="center">
          <NotificationsIcon sx={{ color: '#3b82f6' }} />
          <Typography variant="h6" fontWeight={800} color="#0f172a">
            Notification Alert Preferences
          </Typography>
        </Stack>
        <IconButton size="small" onClick={onClose}>
          <CloseIcon fontSize="small" />
        </IconButton>
      </DialogTitle>

      <DialogContent sx={{ p: 3 }}>
        {successMsg && (
          <Alert severity="success" sx={{ mb: 2, borderRadius: 2 }}>
            {successMsg}
          </Alert>
        )}

        {loading ? (
          <Box display="flex" justifyContent="center" alignItems="center" py={4}>
            <CircularProgress size={24} />
          </Box>
        ) : (
          <Stack spacing={2}>
            <Typography variant="caption" color="text.secondary" fontWeight={700} sx={{ textTransform: 'uppercase' }}>
              Dispensary Real-time Triggers
            </Typography>

            <Paper elevation={0} sx={{ p: 2, border: '1px solid #e2e8f0', borderRadius: 2.5, bgcolor: '#f8fafc' }}>
              <Stack spacing={1.5}>
                <Box display="flex" justifyContent="space-between" alignItems="center">
                  <Box display="flex" alignItems="center" gap={1.2}>
                    <FactCheckIcon sx={{ color: '#f59e0b', fontSize: 20 }} />
                    <Box>
                      <Typography variant="body2" fontWeight={700} color="#0f172a">
                        New Prescription Uploads
                      </Typography>
                      <Typography variant="caption" color="text.secondary">
                        Alert immediately when patient submits prescription for review
                      </Typography>
                    </Box>
                  </Box>
                  <Switch
                    checked={prefs.new_prescription}
                    onChange={() => handleToggle('new_prescription')}
                    color="primary"
                  />
                </Box>

                <Divider />

                <Box display="flex" justifyContent="space-between" alignItems="center">
                  <Box display="flex" alignItems="center" gap={1.2}>
                    <LocalMallIcon sx={{ color: '#3b82f6', fontSize: 20 }} />
                    <Box>
                      <Typography variant="body2" fontWeight={700} color="#0f172a">
                        New Customer Orders
                      </Typography>
                      <Typography variant="caption" color="text.secondary">
                        Alert when checkout is completed and packaging is required
                      </Typography>
                    </Box>
                  </Box>
                  <Switch
                    checked={prefs.new_orders}
                    onChange={() => handleToggle('new_orders')}
                    color="primary"
                  />
                </Box>

                <Divider />

                <Box display="flex" justifyContent="space-between" alignItems="center">
                  <Box display="flex" alignItems="center" gap={1.2}>
                    <WarningAmberIcon sx={{ color: '#ef4444', fontSize: 20 }} />
                    <Box>
                      <Typography variant="body2" fontWeight={700} color="#0f172a">
                        Low & Out of Stock Alerts
                      </Typography>
                      <Typography variant="caption" color="text.secondary">
                        Notify when SKU falls below reorder threshold (≤ 25 units)
                      </Typography>
                    </Box>
                  </Box>
                  <Switch
                    checked={prefs.low_stock}
                    onChange={() => handleToggle('low_stock')}
                    color="primary"
                  />
                </Box>

                <Divider />

                <Box display="flex" justifyContent="space-between" alignItems="center">
                  <Box display="flex" alignItems="center" gap={1.2}>
                    <InventoryIcon sx={{ color: '#10b981', fontSize: 20 }} />
                    <Box>
                      <Typography variant="body2" fontWeight={700} color="#0f172a">
                        Batch Expiry & Inventory Movements
                      </Typography>
                      <Typography variant="caption" color="text.secondary">
                        Alerts for batches expiring within 180 days
                      </Typography>
                    </Box>
                  </Box>
                  <Switch
                    checked={prefs.expiry_alerts}
                    onChange={() => handleToggle('expiry_alerts')}
                    color="primary"
                  />
                </Box>

                <Divider />

                <Box display="flex" justifyContent="space-between" alignItems="center">
                  <Box display="flex" alignItems="center" gap={1.2}>
                    <VolumeUpIcon sx={{ color: '#8b5cf6', fontSize: 20 }} />
                    <Box>
                      <Typography variant="body2" fontWeight={700} color="#0f172a">
                        Dispensary Audio Chime
                      </Typography>
                      <Typography variant="caption" color="text.secondary">
                        Play subtle chime sound on incoming urgent notifications
                      </Typography>
                    </Box>
                  </Box>
                  <Switch
                    checked={prefs.sound_enabled}
                    onChange={() => handleToggle('sound_enabled')}
                    color="primary"
                  />
                </Box>
              </Stack>
            </Paper>
          </Stack>
        )}
      </DialogContent>

      <DialogActions sx={{ px: 3, py: 2, borderTop: '1px solid #e2e8f0', bgcolor: '#f8fafc', justifyContent: 'space-between' }}>
        <Button size="small" onClick={onClose} sx={{ fontWeight: 600 }}>
          Cancel
        </Button>
        <Button
          variant="contained"
          size="small"
          onClick={handleSave}
          disabled={saving}
          sx={{ borderRadius: 2, fontWeight: 700, px: 2.5, bgcolor: '#10b981', '&:hover': { bgcolor: '#059669' } }}
        >
          {saving ? <CircularProgress size={18} color="inherit" /> : 'Save Preferences'}
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default NotificationPreferencesDialog;

