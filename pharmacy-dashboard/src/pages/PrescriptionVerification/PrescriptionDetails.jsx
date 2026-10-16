import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  Box,
  Typography,
  Grid,
  Paper,
  Divider,
  Button,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TextField,
  Card,
  CardContent,
  IconButton,
  Tooltip
} from '@mui/material';
import ArrowBackIcon from '@mui/icons-material/ArrowBack';
import CheckIcon from '@mui/icons-material/Check';
import CloseIcon from '@mui/icons-material/Close';
import ReplayIcon from '@mui/icons-material/Replay';
import SaveIcon from '@mui/icons-material/Save';
import DeleteIcon from '@mui/icons-material/Delete';
import AddIcon from '@mui/icons-material/Add';
import { usePrescriptionService } from '../../services/prescriptionService';
import ImageViewer from '../../components/common/ImageViewer';
import LoadingSpinner from '../../components/common/LoadingSpinner';
import EmptyState from '../../components/common/EmptyState';
import ConfirmationDialog from '../../components/dialogs/ConfirmationDialog';
import SnackbarNotification from '../../components/common/SnackbarNotification';

const PrescriptionDetails = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const { getPrescriptionById, savePrescriptionChanges, verifyPrescription } = usePrescriptionService();

  const [loading, setLoading] = useState(true);
  const [prescription, setPrescription] = useState(null);
  const [editedMedicines, setEditedMedicines] = useState([]);
  
  // Dialog States
  const [confirmOpen, setConfirmOpen] = useState(false);
  const [actionType, setActionType] = useState(''); // 'Approve' | 'Reject' | 'RequestNew'
  const [dialogLoading, setDialogLoading] = useState(false);

  // Toast States
  const [toastOpen, setToastOpen] = useState(false);
  const [toastMsg, setToastMsg] = useState('');
  const [toastSeverity, setToastSeverity] = useState('success');

  useEffect(() => {
    const fetchDetails = async () => {
      setLoading(true);
      const data = await getPrescriptionById(id);
      if (data) {
        setPrescription(data);
        setEditedMedicines(data.medicines ? [...data.medicines] : []);
      }
      setLoading(false);
    };
    fetchDetails();
  }, [id]);

  const handleFieldChange = (index, field, value) => {
    const updated = [...editedMedicines];
    updated[index] = {
      ...updated[index],
      [field]: field === 'quantity' || field === 'confidence' ? Number(value) || 0 : value
    };
    setEditedMedicines(updated);
  };

  const handleAddMedicine = () => {
    setEditedMedicines([
      ...editedMedicines,
      {
        id: Date.now(),
        name: 'Medicine Name',
        strength: 'Strength',
        dosage: 'Dosage',
        duration: 'Duration',
        quantity: 1,
        confidence: 100
      }
    ]);
  };

  const handleDeleteMedicine = (index) => {
    setEditedMedicines(editedMedicines.filter((_, idx) => idx !== index));
  };

  const triggerToast = (msg, severity = 'success') => {
    setToastMsg(msg);
    setToastSeverity(severity);
    setToastOpen(true);
  };

  const handleSaveChanges = async () => {
    try {
      await savePrescriptionChanges(id, editedMedicines);
      triggerToast('Prescription medicines saved locally.');
    } catch (err) {
      triggerToast('Error saving changes.', 'error');
    }
  };

  const handleOpenConfirm = (type) => {
    setActionType(type);
    setConfirmOpen(true);
  };

  const handleConfirmAction = async () => {
    setDialogLoading(true);
    try {
      let statusResult = '';
      let msg = '';
      
      if (actionType === 'Approve') {
        statusResult = 'Approved';
        msg = 'Prescription approved successfully.';
      } else if (actionType === 'Reject') {
        statusResult = 'Rejected';
        msg = 'Prescription rejected successfully.';
      } else {
        statusResult = 'Pending';
        msg = 'New prescription document requested from customer.';
      }

      await verifyPrescription(id, statusResult);
      setConfirmOpen(false);
      triggerToast(msg);
      
      // Delay navigation slightly so they can read the toast success
      setTimeout(() => {
        navigate('/prescriptions');
      }, 1000);

    } catch (err) {
      triggerToast('Operation failed.', 'error');
    } finally {
      setDialogLoading(false);
    }
  };

  if (loading) {
    return <LoadingSpinner message="Retrieving prescription details..." height="60vh" />;
  }

  if (!prescription) {
    return <EmptyState title="Prescription Not Found" description="The requested prescription record could not be loaded." />;
  }

  return (
    <Box display="flex" flexDirection="column" gap={3}>
      {/* Header action bar */}
      <Box display="flex" alignItems="center" gap={2}>
        <IconButton onClick={() => navigate('/prescriptions')} color="primary">
          <ArrowBackIcon />
        </IconButton>
        <Box>
          <Typography variant="h5" fontWeight={800} color="text.primary">
            Prescription Verification / {prescription.id}
          </Typography>
          <Typography variant="body2" color="text.secondary">
            AI confidence, details review, and verification workflows.
          </Typography>
        </Box>
      </Box>

      {/* Main Layout Grid */}
      <Grid container spacing={4}>
        {/* Left Side: ImageViewer */}
        <Grid item xs={12} lg={5} sx={{ display: 'flex', flexDirection: 'column' }}>
          <Typography variant="subtitle1" fontWeight={700} color="text.primary" sx={{ mb: 1.5 }}>
            Original Uploaded Prescription File
          </Typography>
          <Box sx={{ height: 500, width: '100%' }}>
            <ImageViewer imageUrl={prescription.imageUrl} alt={`Prescription ${prescription.id}`} />
          </Box>
        </Grid>

        {/* Right Side: Customer Info & Editable Medicine list */}
        <Grid item xs={12} lg={7} display="flex" flexDirection="column" gap={3}>
          {/* Customer Info Card */}
          <Card variant="outlined" sx={{ borderRadius: 3, borderColor: 'divider' }}>
            <CardContent sx={{ p: 3 }}>
              <Typography variant="subtitle1" fontWeight={700} color="text.primary" sx={{ mb: 2 }}>
                Customer Information
              </Typography>
              <Grid container spacing={2}>
                <Grid item xs={12} sm={6}>
                  <Typography variant="caption" color="text.secondary" display="block">Full Name</Typography>
                  <Typography variant="body2" fontWeight={600}>{prescription.customerName}</Typography>
                </Grid>
                <Grid item xs={12} sm={6}>
                  <Typography variant="caption" color="text.secondary" display="block">Phone Number</Typography>
                  <Typography variant="body2" fontWeight={600}>{prescription.patientDetails.phone}</Typography>
                </Grid>
                <Grid item xs={12} sm={6}>
                  <Typography variant="caption" color="text.secondary" display="block">Email Address</Typography>
                  <Typography variant="body2" fontWeight={600}>{prescription.patientDetails.email}</Typography>
                </Grid>
                <Grid item xs={12} sm={3}>
                  <Typography variant="caption" color="text.secondary" display="block">Age / Gender</Typography>
                  <Typography variant="body2" fontWeight={600}>
                    {prescription.patientDetails.age} yrs / {prescription.patientDetails.gender}
                  </Typography>
                </Grid>
                <Grid item xs={12}>
                  <Typography variant="caption" color="text.secondary" display="block">Delivery Address</Typography>
                  <Typography variant="body2" fontWeight={600}>{prescription.patientDetails.address}</Typography>
                </Grid>
              </Grid>
            </CardContent>
          </Card>

          {/* AI Extracted Medicines Table */}
          <Paper elevation={0} sx={{ border: '1px solid', borderColor: 'divider', borderRadius: 3, p: 3 }}>
            <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
              <Box>
                <Typography variant="subtitle1" fontWeight={700} color="text.primary">
                  AI Extracted Medicines
                </Typography>
                <Typography variant="caption" color="text.secondary">
                  Pharmacists must review and correct any mismatches from the scan.
                </Typography>
              </Box>
              <Button
                variant="outlined"
                color="primary"
                size="small"
                startIcon={<AddIcon />}
                onClick={handleAddMedicine}
                sx={{ borderRadius: 2 }}
              >
                Add Row
              </Button>
            </Box>

            <TableContainer sx={{ border: '1px solid', borderColor: 'grey.200', borderRadius: 2, mb: 3 }}>
              <Table size="small">
                <TableHead sx={{ bgcolor: 'grey.50' }}>
                  <TableRow>
                    <TableCell sx={{ fontWeight: 600 }}>Medicine Name</TableCell>
                    <TableCell sx={{ fontWeight: 600 }}>Strength</TableCell>
                    <TableCell sx={{ fontWeight: 600 }}>Dosage</TableCell>
                    <TableCell sx={{ fontWeight: 600 }}>Duration</TableCell>
                    <TableCell sx={{ fontWeight: 600, width: 80 }}>Qty</TableCell>
                    <TableCell sx={{ fontWeight: 600, width: 80 }}>Conf %</TableCell>
                    <TableCell sx={{ fontWeight: 600, width: 50 }}></TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {editedMedicines.length === 0 ? (
                    <TableRow>
                      <TableCell colSpan={7} align="center" sx={{ py: 3, color: 'text.secondary' }}>
                        No medicines extracted. Click "Add Row" to build prescription.
                      </TableCell>
                    </TableRow>
                  ) : (
                    editedMedicines.map((med, index) => (
                      <TableRow key={med.id || index}>
                        <TableCell sx={{ py: 1 }}>
                          <TextField
                            size="small"
                            value={med.name}
                            onChange={(e) => handleFieldChange(index, 'name', e.target.value)}
                            fullWidth
                            InputProps={{ style: { fontSize: '0.875rem' } }}
                          />
                        </TableCell>
                        <TableCell sx={{ py: 1 }}>
                          <TextField
                            size="small"
                            value={med.strength}
                            onChange={(e) => handleFieldChange(index, 'strength', e.target.value)}
                            fullWidth
                            InputProps={{ style: { fontSize: '0.875rem' } }}
                          />
                        </TableCell>
                        <TableCell sx={{ py: 1 }}>
                          <TextField
                            size="small"
                            value={med.dosage}
                            onChange={(e) => handleFieldChange(index, 'dosage', e.target.value)}
                            fullWidth
                            InputProps={{ style: { fontSize: '0.875rem' } }}
                          />
                        </TableCell>
                        <TableCell sx={{ py: 1 }}>
                          <TextField
                            size="small"
                            value={med.duration}
                            onChange={(e) => handleFieldChange(index, 'duration', e.target.value)}
                            fullWidth
                            InputProps={{ style: { fontSize: '0.875rem' } }}
                          />
                        </TableCell>
                        <TableCell sx={{ py: 1 }}>
                          <TextField
                            size="small"
                            type="number"
                            value={med.quantity}
                            onChange={(e) => handleFieldChange(index, 'quantity', e.target.value)}
                            InputProps={{ style: { fontSize: '0.875rem' } }}
                          />
                        </TableCell>
                        <TableCell sx={{ py: 1 }}>
                          <TextField
                            size="small"
                            type="number"
                            value={med.confidence}
                            onChange={(e) => handleFieldChange(index, 'confidence', e.target.value)}
                            InputProps={{ style: { fontSize: '0.875rem' } }}
                          />
                        </TableCell>
                        <TableCell sx={{ py: 1, px: 0.5 }} align="center">
                          <Tooltip title="Remove Row">
                            <IconButton color="error" size="small" onClick={() => handleDeleteMedicine(index)}>
                              <DeleteIcon fontSize="small" />
                            </IconButton>
                          </Tooltip>
                        </TableCell>
                      </TableRow>
                    ))
                  )}
                </TableBody>
              </Table>
            </TableContainer>

            {/* Action Buttons Row */}
            <Box display="flex" justifyContent="space-between" flexWrap="wrap" gap={2}>
              <Button
                variant="outlined"
                color="secondary"
                startIcon={<SaveIcon />}
                onClick={handleSaveChanges}
                sx={{ borderRadius: 2 }}
              >
                Save Changes
              </Button>

              <Box display="flex" gap={1.5} flexWrap="wrap">
                <Button
                  variant="outlined"
                  color="warning"
                  startIcon={<ReplayIcon />}
                  onClick={() => handleOpenConfirm('RequestNew')}
                  sx={{ borderRadius: 2 }}
                >
                  Request New Prescription
                </Button>
                <Button
                  variant="outlined"
                  color="error"
                  startIcon={<CloseIcon />}
                  onClick={() => handleOpenConfirm('Reject')}
                  sx={{ borderRadius: 2 }}
                >
                  Reject
                </Button>
                <Button
                  variant="contained"
                  color="primary"
                  startIcon={<CheckIcon />}
                  onClick={() => handleOpenConfirm('Approve')}
                  sx={{ borderRadius: 2, boxShadow: 'none' }}
                >
                  Approve
                </Button>
              </Box>
            </Box>
          </Paper>
        </Grid>
      </Grid>

      {/* Confirmation Dialog */}
      <ConfirmationDialog
        open={confirmOpen}
        title={
          actionType === 'Approve'
            ? 'Approve Prescription'
            : actionType === 'Reject'
            ? 'Reject Prescription'
            : 'Request New Upload'
        }
        message={
          actionType === 'Approve'
            ? 'Are you sure you want to approve this prescription and trigger the packaging order workflow?'
            : actionType === 'Reject'
            ? 'Are you sure you want to reject this prescription? This will notify the customer of the failure.'
            : 'Are you sure you want to request a new scan? This prompts the customer to take a clearer image.'
        }
        confirmLabel={
          actionType === 'Approve' ? 'Approve' : actionType === 'Reject' ? 'Reject' : 'Request'
        }
        onConfirm={handleConfirmAction}
        onCancel={() => setConfirmOpen(false)}
        loading={dialogLoading}
      />

      {/* Snackbar Notification Toast */}
      <SnackbarNotification
        open={toastOpen}
        message={toastMsg}
        severity={toastSeverity}
        onClose={() => setToastOpen(false)}
      />
    </Box>
  );
};

export default PrescriptionDetails;
