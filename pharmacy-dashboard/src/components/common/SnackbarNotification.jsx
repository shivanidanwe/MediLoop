import React from 'react';
import { Snackbar, Alert } from '@mui/material';

const SnackbarNotification = ({
  open,
  message,
  severity = 'success', // 'success' | 'error' | 'warning' | 'info'
  onClose,
  duration = 4000
}) => {
  return (
    <Snackbar
      open={open}
      autoHideDuration={duration}
      onClose={onClose}
      anchorOrigin={{ vertical: 'bottom', horizontal: 'right' }}
    >
      <Alert onClose={onClose} severity={severity} variant="filled" sx={{ width: '100%' }}>
        {message}
      </Alert>
    </Snackbar>
  );
};

export default SnackbarNotification;
