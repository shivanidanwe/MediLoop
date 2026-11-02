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
  Card,
  CardContent,
  IconButton,
  Tooltip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Chip,
  Alert,
  AlertTitle,
  TextField,
  Stack
} from '@mui/material';
import ArrowBackIcon from '@mui/icons-material/ArrowBack';
import CheckIcon from '@mui/icons-material/Check';
import CloseIcon from '@mui/icons-material/Close';
import QuestionAnswerIcon from '@mui/icons-material/QuestionAnswer';
import SendIcon from '@mui/icons-material/Send';
import LockIcon from '@mui/icons-material/Lock';
import WarningAmberIcon from '@mui/icons-material/WarningAmber';
import CheckCircleOutlineIcon from '@mui/icons-material/CheckCircleOutlined';
import VerifiedIcon from '@mui/icons-material/Verified';
import DescriptionIcon from '@mui/icons-material/Description';
import { usePrescriptionService } from '../../services/prescriptionService';
import apiClient from '../../api/apiClient';
import ImageViewer from '../../components/common/ImageViewer';
import LoadingSpinner from '../../components/common/LoadingSpinner';
import EmptyState from '../../components/common/EmptyState';
import ConfirmationDialog from '../../components/dialogs/ConfirmationDialog';
import SnackbarNotification from '../../components/common/SnackbarNotification';

const PrescriptionDetails = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const { getPrescriptionById, verifyPrescription, requestClarification } = usePrescriptionService();

  const [loading, setLoading] = useState(true);
  const [prescription, setPrescription] = useState(null);

  // Dialog States
  const [confirmOpen, setConfirmOpen] = useState(false);
  const [dialogLoading, setDialogLoading] = useState(false);
  const [rejectionReason, setRejectionReason] = useState('');
  const [rejectDialogOpen, setRejectDialogOpen] = useState(false);
  const [clarifyDialogOpen, setClarifyDialogOpen] = useState(false);
  const [clarificationNotes, setClarificationNotes] = useState('');

  // Procurement & Low Stock States
  const [procurementDialogOpen, setProcurementDialogOpen] = useState(false);
  const [procurementData, setProcurementData] = useState(null);
  const [sendingPo, setSendingPo] = useState(false);

  // Toast States
  const [toastOpen, setToastOpen] = useState(false);
  const [toastMsg, setToastMsg] = useState('');
  const [toastSeverity, setToastSeverity] = useState('success');

  const fetchDetails = async () => {
    setLoading(true);
    const data = await getPrescriptionById(id);
    if (data) {
      setPrescription(data);
    }
    setLoading(false);
  };

  useEffect(() => {
    fetchDetails();
  }, [id]);

  const triggerToast = (msg, severity = 'success') => {
    setToastMsg(msg);
    setToastSeverity(severity);
    setToastOpen(true);
  };

  const isFinalized = Boolean(
    prescription?.isFinalized ||
    ['Approved', 'Rejected', 'Verified'].includes(prescription?.status)
  );

  const handleConfirmReject = async () => {
    if (!rejectionReason.trim()) return;
    setDialogLoading(true);
    try {
      await verifyPrescription(id, 'Rejected', rejectionReason.trim());
      setRejectDialogOpen(false);
      triggerToast('Prescription rejected. Customer notified with the reason.', 'warning');
      fetchDetails();
    } catch (err) {
      triggerToast('Rejection failed: ' + (err.response?.data?.detail || err.message), 'error');
    } finally {
      setDialogLoading(false);
    }
  };

  const handleConfirmClarification = async () => {
    if (!clarificationNotes.trim()) return;
    setDialogLoading(true);
    try {
      await requestClarification(id, clarificationNotes.trim());
      setClarifyDialogOpen(false);
      triggerToast('Clarification request dispatched to customer.', 'info');
      fetchDetails();
    } catch (err) {
      triggerToast('Failed to request clarification: ' + (err.response?.data?.detail || err.message), 'error');
    } finally {
      setDialogLoading(false);
    }
  };

  const handleConfirmApprove = async () => {
    setDialogLoading(true);
    try {
      await verifyPrescription(id, 'Approved');
      setConfirmOpen(false);

      // Check for newly generated Procurement Invoice
      try {
        const poRes = await apiClient.get('/inventory/supplier-invoices');
        if (poRes.data && poRes.data.length > 0) {
          setProcurementData(poRes.data[0]);
          setProcurementDialogOpen(true);
          return;
        }
      } catch (_) {}

      triggerToast('Prescription approved successfully. Customer and order status updated.', 'success');
      fetchDetails();
    } catch (err) {
      triggerToast('Approval failed: ' + (err.response?.data?.detail || err.message), 'error');
    } finally {
      setDialogLoading(false);
    }
  };

  const handleSendSupplierInvoice = async () => {
    if (!procurementData) return;
    setSendingPo(true);
    try {
      await apiClient.post(`/inventory/supplier-invoices/${procurementData.id}/send`);
      triggerToast(`Purchase Order ${procurementData.po_number} sent to supplier!`, 'success');
      setProcurementDialogOpen(false);
      fetchDetails();
    } catch (err) {
      triggerToast('Failed to dispatch PO to supplier.', 'error');
    } finally {
      setSendingPo(false);
    }
  };

  if (loading) {
    return <LoadingSpinner message="Retrieving prescription verification records..." height="60vh" />;
  }

  if (!prescription) {
    return <EmptyState title="Prescription Not Found" description="The requested prescription record could not be loaded." />;
  }

  const medicinesList = Array.isArray(prescription.medicines) ? prescription.medicines : [];

  return (
    <Box display="flex" flexDirection="column" gap={3}>
      {/* Header action bar */}
      <Box display="flex" justifyContent="space-between" alignItems="center" flexWrap="wrap" gap={2}>
        <Box display="flex" alignItems="center" gap={2}>
          <IconButton onClick={() => navigate('/prescriptions')} color="primary" sx={{ border: '1px solid #e2e8f0', borderRadius: 2 }}>
            <ArrowBackIcon />
          </IconButton>
          <Box>
            <Stack direction="row" spacing={1.5} alignItems="center">
              <Typography variant="h5" fontWeight={800} color="#0f172a">
                Prescription Review #{prescription.id}
              </Typography>
              <Chip
                label={prescription.status || 'Pending'}
                size="small"
                sx={{
                  fontWeight: 800,
                  fontSize: '0.75rem',
                  bgcolor: isFinalized
                    ? (prescription.status === 'Approved' ? 'rgba(16, 185, 129, 0.12)' : 'rgba(239, 68, 68, 0.12)')
                    : 'rgba(245, 158, 11, 0.12)',
                  color: isFinalized
                    ? (prescription.status === 'Approved' ? '#059669' : '#dc2626')
                    : '#d97706',
                  border: '1px solid',
                  borderColor: isFinalized
                    ? (prescription.status === 'Approved' ? 'rgba(16, 185, 129, 0.3)' : 'rgba(239, 68, 68, 0.3)')
                    : 'rgba(245, 158, 11, 0.3)'
                }}
              />
              {isFinalized && (
                <Chip
                  icon={<LockIcon sx={{ fontSize: '13px !important' }} />}
                  label="Decision Finalized"
                  size="small"
                  variant="outlined"
                  sx={{ fontSize: '0.7rem', fontWeight: 700 }}
                />
              )}
            </Stack>
            <Typography variant="body2" color="text.secondary" sx={{ mt: 0.3 }}>
              Uploaded on {prescription.date || 'Today'} • Secure Medical Verification Workflow
            </Typography>
          </Box>
        </Box>

        {/* Top Actions */}
        <Stack direction="row" spacing={1.5}>
          <Button
            variant="outlined"
            color="warning"
            disabled={isFinalized}
            startIcon={<QuestionAnswerIcon />}
            onClick={() => {
              setClarificationNotes('');
              setClarifyDialogOpen(true);
            }}
            sx={{ borderRadius: 2, textTransform: 'none', fontWeight: 700 }}
          >
            Request Clarification
          </Button>

          <Button
            variant="outlined"
            color="error"
            disabled={isFinalized}
            startIcon={<CloseIcon />}
            onClick={() => {
              setRejectionReason('');
              setRejectDialogOpen(true);
            }}
            sx={{ borderRadius: 2, textTransform: 'none', fontWeight: 700 }}
          >
            Reject Prescription
          </Button>

          <Button
            variant="contained"
            color="primary"
            disabled={isFinalized}
            startIcon={<CheckIcon />}
            onClick={() => setConfirmOpen(true)}
            sx={{
              borderRadius: 2,
              textTransform: 'none',
              fontWeight: 700,
              bgcolor: '#10b981',
              '&:hover': { bgcolor: '#059669' }
            }}
          >
            Approve Prescription
          </Button>
        </Stack>
      </Box>

      {/* Audit Banner if Finalized */}
      {isFinalized && (
        <Alert severity={prescription.status === 'Approved' ? 'success' : 'error'} sx={{ borderRadius: 2.5 }}>
          <AlertTitle sx={{ fontWeight: 800 }}>
            Prescription Audit Status: {prescription.status}
          </AlertTitle>
          This prescription record has already been reviewed and finalized by the licensed pharmacist.
          In accordance with pharmacy compliance, approved and rejected decisions cannot be overwritten.
        </Alert>
      )}

      {/* Main Layout Grid */}
      <Grid container spacing={3.5}>
        {/* Left Side: ImageViewer (Zoom, Pan, Rotate, Download, PDF) */}
        <Grid item xs={12} lg={5} sx={{ display: 'flex', flexDirection: 'column' }}>
          <Typography variant="subtitle2" fontWeight={800} color="#0f172a" sx={{ mb: 1 }}>
            Original Uploaded Document Evidence
          </Typography>
          <Box sx={{ height: 520, width: '100%' }}>
            <ImageViewer
              imageUrl={prescription.imageUrl}
              prescriptionId={prescription.id}
              alt={`Prescription Document #${prescription.id}`}
            />
          </Box>

          {/* OCR Extracted Text Preview */}
          {prescription.extractedText && (
            <Card variant="outlined" sx={{ mt: 2.5, borderRadius: 3, bgcolor: '#f8fafc', borderColor: '#e2e8f0' }}>
              <CardContent sx={{ p: 2.5 }}>
                <Typography variant="caption" fontWeight={800} color="#64748b" sx={{ textTransform: 'uppercase', letterSpacing: 0.5, display: 'block', mb: 1 }}>
                  OCR Raw Extracted Text Output
                </Typography>
                <Typography
                  variant="body2"
                  sx={{
                    fontFamily: 'monospace',
                    whiteSpace: 'pre-wrap',
                    color: '#334155',
                    fontSize: '0.82rem',
                    lineHeight: 1.6,
                    p: 1.8,
                    bgcolor: '#ffffff',
                    borderRadius: 2,
                    border: '1px solid #e2e8f0',
                    maxHeight: 220,
                    overflowY: 'auto'
                  }}
                >
                  {prescription.extractedText}
                </Typography>
              </CardContent>
            </Card>
          )}
        </Grid>

        {/* Right Side: Patient Info & READ-ONLY Extracted Medicines */}
        <Grid item xs={12} lg={7} display="flex" flexDirection="column" gap={3}>
          {/* Patient Card */}
          <Paper elevation={0} sx={{ p: 3, border: '1px solid #e2e8f0', borderRadius: 3, bgcolor: '#ffffff' }}>
            <Typography variant="subtitle1" fontWeight={800} color="#0f172a" sx={{ mb: 2 }}>
              Patient & Clinical Attribution
            </Typography>
            <Grid container spacing={2}>
              <Grid item xs={12} sm={6}>
                <Typography variant="caption" color="text.secondary" display="block">Patient / Customer Name</Typography>
                <Typography variant="body2" fontWeight={700} color="#0f172a">
                  {prescription.customerName || prescription.patientName || 'Registered Patient'}
                </Typography>
              </Grid>
              <Grid item xs={12} sm={6}>
                <Typography variant="caption" color="text.secondary" display="block">Prescribing Doctor</Typography>
                <Typography variant="body2" fontWeight={700} color="#0f172a">
                  {prescription.doctorName || 'Licensed Medical Practitioner'}
                </Typography>
              </Grid>
              <Grid item xs={12} sm={6}>
                <Typography variant="caption" color="text.secondary" display="block">Contact Phone</Typography>
                <Typography variant="body2" fontWeight={600} color="#334155">
                  {prescription.patientDetails?.phone || '+91 98450 00000'}
                </Typography>
              </Grid>
              <Grid item xs={12} sm={6}>
                <Typography variant="caption" color="text.secondary" display="block">Age / Gender</Typography>
                <Typography variant="body2" fontWeight={600} color="#334155">
                  {prescription.patientDetails?.age || '42'} yrs • {prescription.patientDetails?.gender || 'Male'}
                </Typography>
              </Grid>
              <Grid item xs={12}>
                <Typography variant="caption" color="text.secondary" display="block">Delivery / Residence Address</Typography>
                <Typography variant="body2" fontWeight={600} color="#334155">
                  {prescription.patientDetails?.address || 'Pandharpur, Maharashtra, India'}
                </Typography>
              </Grid>
            </Grid>
          </Paper>

          {/* Strictly Read-Only Extracted Medicines Manifest */}
          <Paper elevation={0} sx={{ p: 3, border: '1px solid #e2e8f0', borderRadius: 3, bgcolor: '#ffffff' }}>
            <Box display="flex" justifyContent="space-between" alignItems="center" mb={1.5} flexWrap="wrap" gap={1}>
              <Box>
                <Stack direction="row" spacing={1} alignItems="center">
                  <LockIcon sx={{ fontSize: 18, color: '#64748b' }} />
                  <Typography variant="subtitle1" fontWeight={800} color="#0f172a">
                    AI Extracted Medicine Details (Read-Only)
                  </Typography>
                </Stack>
                <Typography variant="caption" color="text.secondary">
                  Legally protected extracted clinical data. Modifications are prohibited to ensure audit trail integrity.
                </Typography>
              </Box>
              <Chip
                label="Protected Clinical Record"
                size="small"
                sx={{ bgcolor: '#f1f5f9', color: '#475569', fontWeight: 700, fontSize: '0.7rem' }}
              />
            </Box>

            <Alert severity="info" sx={{ mb: 2.5, py: 0.5, borderRadius: 2, fontSize: '0.82rem' }}>
              Extracted prescription items cannot be silently modified. If items differ from the physician's handwritten note, click <strong>"Request Clarification"</strong> or <strong>"Reject"</strong> with an explanation.
            </Alert>

            <TableContainer sx={{ border: '1px solid #e2e8f0', borderRadius: 2.5, overflow: 'hidden' }}>
              <Table size="small">
                <TableHead sx={{ bgcolor: '#f8fafc' }}>
                  <TableRow>
                    <TableCell sx={{ fontWeight: 700, fontSize: '0.75rem', py: 1.2 }}>Medicine Name</TableCell>
                    <TableCell sx={{ fontWeight: 700, fontSize: '0.75rem', py: 1.2 }}>Strength</TableCell>
                    <TableCell sx={{ fontWeight: 700, fontSize: '0.75rem', py: 1.2 }}>Dosage Pattern</TableCell>
                    <TableCell sx={{ fontWeight: 700, fontSize: '0.75rem', py: 1.2 }}>Duration</TableCell>
                    <TableCell sx={{ fontWeight: 700, fontSize: '0.75rem', py: 1.2, textAlign: 'center' }}>Prescribed Qty</TableCell>
                    <TableCell sx={{ fontWeight: 700, fontSize: '0.75rem', py: 1.2, textAlign: 'right' }}>Confidence</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {medicinesList.length === 0 ? (
                    <TableRow>
                      <TableCell colSpan={6} align="center" sx={{ py: 3, color: 'text.secondary', fontSize: '0.85rem' }}>
                        No medicines extracted automatically from this prescription scan.
                      </TableCell>
                    </TableRow>
                  ) : (
                    medicinesList.map((med, index) => {
                      const conf = Number(med.confidence || 85);
                      const isLowConf = conf < 70;
                      return (
                        <TableRow key={med.id || index} sx={{ '&:hover': { bgcolor: '#f8fafc' } }}>
                          <TableCell sx={{ py: 1.2 }}>
                            <Typography variant="body2" fontWeight={700} color="#0f172a">
                              {med.name || med.medicine_name || 'Prescribed Drug'}
                            </Typography>
                            {med.instructions && (
                              <Typography variant="caption" color="text.secondary" display="block">
                                Inst: {med.instructions}
                              </Typography>
                            )}
                            {isLowConf && (
                              <Chip
                                label="Low OCR Confidence"
                                size="small"
                                sx={{ height: 18, fontSize: '0.62rem', bgcolor: 'rgba(245, 158, 11, 0.1)', color: '#d97706', fontWeight: 700, mt: 0.3 }}
                              />
                            )}
                          </TableCell>
                          <TableCell sx={{ py: 1.2, fontSize: '0.82rem', color: '#475569' }}>
                            {med.strength || 'Standard'}
                          </TableCell>
                          <TableCell sx={{ py: 1.2, fontSize: '0.82rem', color: '#475569' }}>
                            {med.dosage || med.frequency || 'As directed'}
                          </TableCell>
                          <TableCell sx={{ py: 1.2, fontSize: '0.82rem', color: '#475569' }}>
                            {med.duration || '5 days'}
                          </TableCell>
                          <TableCell sx={{ py: 1.2, textAlign: 'center' }}>
                            <Chip
                              label={`${med.quantity || 1} units`}
                              size="small"
                              sx={{ height: 22, fontSize: '0.72rem', fontWeight: 800, bgcolor: '#f1f5f9' }}
                            />
                          </TableCell>
                          <TableCell sx={{ py: 1.2, textAlign: 'right' }}>
                            <Chip
                              label={`${conf}%`}
                              size="small"
                              sx={{
                                height: 22,
                                fontSize: '0.72rem',
                                fontWeight: 800,
                                bgcolor: isLowConf ? 'rgba(245, 158, 11, 0.1)' : 'rgba(16, 185, 129, 0.1)',
                                color: isLowConf ? '#d97706' : '#059669',
                                border: `1px solid ${isLowConf ? 'rgba(245, 158, 11, 0.3)' : 'rgba(16, 185, 129, 0.3)'}`
                              }}
                            />
                          </TableCell>
                        </TableRow>
                      );
                    })
                  )}
                </TableBody>
              </Table>
            </TableContainer>

            {/* Bottom Actions Row */}
            <Box display="flex" justifyContent="flex-end" alignItems="center" gap={1.5} mt={3} flexWrap="wrap">
              <Button
                variant="outlined"
                color="warning"
                disabled={isFinalized}
                startIcon={<QuestionAnswerIcon />}
                onClick={() => {
                  setClarificationNotes('');
                  setClarifyDialogOpen(true);
                }}
                sx={{ borderRadius: 2, textTransform: 'none', fontWeight: 700, fontSize: '0.82rem' }}
              >
                Request Clarification
              </Button>
              <Button
                variant="outlined"
                color="error"
                disabled={isFinalized}
                startIcon={<CloseIcon />}
                onClick={() => {
                  setRejectionReason('');
                  setRejectDialogOpen(true);
                }}
                sx={{ borderRadius: 2, textTransform: 'none', fontWeight: 700, fontSize: '0.82rem' }}
              >
                Reject
              </Button>
              <Button
                variant="contained"
                disabled={isFinalized}
                startIcon={<CheckIcon />}
                onClick={() => setConfirmOpen(true)}
                sx={{
                  borderRadius: 2,
                  textTransform: 'none',
                  fontWeight: 700,
                  fontSize: '0.82rem',
                  bgcolor: '#10b981',
                  '&:hover': { bgcolor: '#059669' }
                }}
              >
                Approve Prescription
              </Button>
            </Box>
          </Paper>
        </Grid>
      </Grid>

      {/* Confirmation Dialog for Approval */}
      <ConfirmationDialog
        open={confirmOpen}
        title="Approve Prescription"
        message="Are you sure you want to approve this prescription? The customer will be notified, the prescription will be locked as Approved, and inventory availability will be verified."
        confirmLabel="Confirm Approval"
        onConfirm={handleConfirmApprove}
        onCancel={() => setConfirmOpen(false)}
        loading={dialogLoading}
      />

      {/* Mandatory Prescription Rejection Dialog */}
      <Dialog
        open={rejectDialogOpen}
        onClose={() => setRejectDialogOpen(false)}
        maxWidth="xs"
        fullWidth
        PaperProps={{ sx: { borderRadius: 3 } }}
      >
        <DialogTitle sx={{ fontWeight: 800, color: '#dc2626', pb: 1 }}>
          Reject Prescription #{id}
        </DialogTitle>
        <DialogContent>
          <Typography variant="body2" color="text.secondary" mb={2}>
            Please specify the clinical or administrative reason for rejecting this prescription (e.g. illegible signature, expired date, missing doctor license). The customer will be informed.
          </Typography>
          <TextField
            autoFocus
            label="Rejection Reason (Required)"
            fullWidth
            multiline
            rows={3}
            value={rejectionReason}
            onChange={(e) => setRejectionReason(e.target.value)}
            placeholder="e.g. The prescription image is blurry and the doctor's seal is unreadable."
            error={!rejectionReason.trim()}
            helperText={!rejectionReason.trim() ? "Rejection reason is required" : ""}
          />
        </DialogContent>
        <DialogActions sx={{ p: 2.5, pt: 0 }}>
          <Button onClick={() => setRejectDialogOpen(false)} color="inherit" sx={{ fontWeight: 600 }}>
            Cancel
          </Button>
          <Button
            variant="contained"
            color="error"
            disabled={!rejectionReason.trim() || dialogLoading}
            onClick={handleConfirmReject}
            sx={{ borderRadius: 2, fontWeight: 700 }}
          >
            Confirm Rejection
          </Button>
        </DialogActions>
      </Dialog>

      {/* Customer Clarification Dialog */}
      <Dialog
        open={clarifyDialogOpen}
        onClose={() => setClarifyDialogOpen(false)}
        maxWidth="sm"
        fullWidth
        PaperProps={{ sx: { borderRadius: 3 } }}
      >
        <DialogTitle sx={{ fontWeight: 800, color: '#d97706', pb: 1 }}>
          Request Clarification from Patient
        </DialogTitle>
        <DialogContent>
          <Typography variant="body2" color="text.secondary" mb={2}>
            Ask the patient or physician to clarify dosage, strength, or re-upload a clearer picture without outright rejecting the order.
          </Typography>
          <TextField
            autoFocus
            label="Clarification Message / Query (Required)"
            fullWidth
            multiline
            rows={3}
            value={clarificationNotes}
            onChange={(e) => setClarificationNotes(e.target.value)}
            placeholder="e.g. Please clarify the dosage for Tab Azithromycin or upload an uncropped image showing the doctor's full signature."
            error={!clarificationNotes.trim()}
            helperText={!clarificationNotes.trim() ? "Notes are required" : ""}
          />
        </DialogContent>
        <DialogActions sx={{ p: 2.5, pt: 0 }}>
          <Button onClick={() => setClarifyDialogOpen(false)} color="inherit" sx={{ fontWeight: 600 }}>
            Cancel
          </Button>
          <Button
            variant="contained"
            color="warning"
            disabled={!clarificationNotes.trim() || dialogLoading}
            onClick={handleConfirmClarification}
            sx={{ borderRadius: 2, fontWeight: 700 }}
          >
            Send Clarification Request
          </Button>
        </DialogActions>
      </Dialog>

      {/* AI Stock Orchestration Dialog */}
      <Dialog
        open={procurementDialogOpen}
        onClose={() => {
          setProcurementDialogOpen(false);
          fetchDetails();
        }}
        maxWidth="md"
        fullWidth
        PaperProps={{ sx: { borderRadius: 3, p: 1 } }}
      >
        <DialogTitle sx={{ display: 'flex', alignItems: 'center', gap: 1.5, pb: 1 }}>
          <WarningAmberIcon color="warning" sx={{ fontSize: 32 }} />
          <Box>
            <Typography variant="h6" fontWeight={800} color="#0f172a">
              Stock Replenishment Alert
            </Typography>
            <Typography variant="caption" color="text.secondary">
              Automated stock verification completed post-approval
            </Typography>
          </Box>
        </DialogTitle>

        <DialogContent dividers sx={{ display: 'flex', flexDirection: 'column', gap: 2.5, py: 2.5 }}>
          <Alert severity="warning" sx={{ borderRadius: 2 }}>
            <AlertTitle sx={{ fontWeight: 700 }}>Depleted Stock Detected</AlertTitle>
            Prescribed medicines are in high demand and current inventory is below threshold.
            A replenishment Purchase Order draft has been prepared.
          </Alert>

          {procurementData && (
            <Paper variant="outlined" sx={{ p: 2, borderRadius: 2, bgcolor: '#f9fafb' }}>
              <Box display="flex" justifyContent="space-between" alignItems="center" mb={1.5}>
                <Box>
                  <Typography variant="subtitle2" fontWeight={700}>
                    Purchase Order: {procurementData.po_number}
                  </Typography>
                  <Typography variant="caption" color="text.secondary">
                    Supplier: {procurementData.supplier_name}
                  </Typography>
                </Box>
                <Chip label={procurementData.status || 'READY_FOR_SUPPLIER'} color="warning" size="small" sx={{ fontWeight: 700 }} />
              </Box>

              <TableContainer component={Paper} variant="outlined" sx={{ borderRadius: 1.5, my: 1.5 }}>
                <Table size="small">
                  <TableHead sx={{ bgcolor: '#f1f5f9' }}>
                    <TableRow>
                      <TableCell sx={{ fontWeight: 700 }}>Medicine</TableCell>
                      <TableCell align="center" sx={{ fontWeight: 700 }}>Current Stock</TableCell>
                      <TableCell align="center" sx={{ fontWeight: 700 }}>Order Qty</TableCell>
                      <TableCell align="right" sx={{ fontWeight: 700 }}>Unit Price</TableCell>
                      <TableCell align="right" sx={{ fontWeight: 700 }}>Line Total</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {(procurementData.items_json || []).map((line, idx) => (
                      <TableRow key={idx}>
                        <TableCell sx={{ fontWeight: 600 }}>{line.medicine_name}</TableCell>
                        <TableCell align="center">
                          <Chip
                            label={`${line.current_stock} left`}
                            size="small"
                            color={line.current_stock <= 0 ? 'error' : 'warning'}
                            sx={{ height: 20, fontSize: '0.7rem' }}
                          />
                        </TableCell>
                        <TableCell align="center" sx={{ fontWeight: 700, color: 'primary.main' }}>
                          +{line.reorder_quantity} units
                        </TableCell>
                        <TableCell align="right">₹{line.unit_wholesale_price}</TableCell>
                        <TableCell align="right" sx={{ fontWeight: 700 }}>₹{line.line_total}</TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </TableContainer>

              <Box display="flex" justifyContent="flex-end" gap={3} mt={1}>
                <Typography variant="subtitle1" fontWeight={800} color="primary.main">
                  Total PO Value: ₹{procurementData.total_amount}
                </Typography>
              </Box>
            </Paper>
          )}
        </DialogContent>

        <DialogActions sx={{ px: 3, py: 2, justifyContent: 'space-between' }}>
          <Button
            onClick={() => {
              setProcurementDialogOpen(false);
              fetchDetails();
            }}
            color="inherit"
          >
            Acknowledge & Close
          </Button>

          <Button
            variant="contained"
            color="primary"
            startIcon={<SendIcon />}
            loading={sendingPo}
            onClick={handleSendSupplierInvoice}
            sx={{ borderRadius: 2 }}
          >
            Dispatch PO to Supplier
          </Button>
        </DialogActions>
      </Dialog>

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
