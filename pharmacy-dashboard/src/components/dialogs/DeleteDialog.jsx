import React from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogContentText,
  DialogActions,
  Button
} from '@mui/material';

const DeleteDialog = ({
  open,
  title = 'Delete Item',
  message = 'Are you sure you want to delete this item? This action cannot be undone.',
  deleteLabel = 'Delete',
  cancelLabel = 'Cancel',
  onDelete,
  onCancel,
  loading = false
}) => {
  return (
    <Dialog open={open} onClose={loading ? undefined : onCancel} maxWidth="xs" fullWidth>
      <DialogTitle sx={{ fontWeight: 600, color: 'error.main' }}>{title}</DialogTitle>
      <DialogContent>
        <DialogContentText variant="body2">{message}</DialogContentText>
      </DialogContent>
      <DialogActions sx={{ px: 3, pb: 2 }}>
        <Button onClick={onCancel} disabled={loading} color="inherit">
          {cancelLabel}
        </Button>
        <Button onClick={onDelete} disabled={loading} variant="contained" color="error">
          {loading ? 'Deleting...' : deleteLabel}
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default DeleteDialog;
