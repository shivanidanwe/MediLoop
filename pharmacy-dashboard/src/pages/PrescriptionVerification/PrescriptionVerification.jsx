import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Chip,
  Button,
  IconButton,
  Tooltip,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TablePagination,
  TextField,
  InputAdornment,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Grid,
  Stack,
  Avatar,
  Alert,
  AlertTitle,
  CircularProgress
} from '@mui/material';
import SearchIcon from '@mui/icons-material/Search';
import VisibilityIcon from '@mui/icons-material/Visibility';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import HighlightOffIcon from '@mui/icons-material/HighlightOff';
import HourglassEmptyIcon from '@mui/icons-material/HourglassEmpty';
import HelpOutlineIcon from '@mui/icons-material/HelpOutlineOutlined';
import CheckIcon from '@mui/icons-material/Check';
import CloseIcon from '@mui/icons-material/Close';
import ZoomInIcon from '@mui/icons-material/ZoomIn';
import RefreshIcon from '@mui/icons-material/Refresh';
import FactCheckIcon from '@mui/icons-material/FactCheck';
import MedicationIcon from '@mui/icons-material/Medication';
import LockIcon from '@mui/icons-material/Lock';
import ChatBubbleOutlineIcon from '@mui/icons-material/ChatBubbleOutlineOutlined';
import { usePrescriptionService } from '../../services/prescriptionService';
import ImageViewer from '../../components/common/ImageViewer';
import SnackbarNotification from '../../components/common/SnackbarNotification';

const PrescriptionVerification = () => {
  const { getPrescriptions, verifyPrescription, requestClarification } = usePrescriptionService();

  const [loading, setLoading] = useState(true);
  const [isSyncing, setIsSyncing] = useState(false);
  const [lastSynced, setLastSynced] = useState(null);
  const [secondsAgo, setSecondsAgo] = useState(0);
  const [prescriptions, setPrescriptions] = useState([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('All');

  // Pagination
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(10);

  // View & Verify Modal State
  const [selectedRx, setSelectedRx] = useState(null);
  const [modalOpen, setModalOpen] = useState(false);
  const [pharmacistNote, setPharmacistNote] = useState('');
  const [actionLoading, setActionLoading] = useState(false);

  // Clarification Dialog
  const [clarifyDialogOpen, setClarifyDialogOpen] = useState(false);
  const [clarificationNotes, setClarificationNotes] = useState('');

  // Reject Confirmation Dialog
  const [rejectDialogOpen, setRejectDialogOpen] = useState(false);
  const [rejectReason, setRejectReason] = useState('');

  // Toast
  const [toastOpen, setToastOpen] = useState(false);
  const [toastMsg, setToastMsg] = useState('');
  const [toastSeverity, setToastSeverity] = useState('success');

  const loadPrescriptions = async (isInitial = false) => {
    if (isInitial && prescriptions.length === 0) {
      setLoading(true);
    }
    setIsSyncing(true);
    try {
      const data = await getPrescriptions();
      if (Array.isArray(data)) {
        setPrescriptions(data);
        setLastSynced(new Date());
        setSecondsAgo(0);
      }
    } catch (err) {
      console.error('Error fetching prescriptions from real-time database:', err);
    } finally {
      setLoading(false);
      setIsSyncing(false);
    }
  };

  // Real-time automatic polling every 5 seconds
  useEffect(() => {
    loadPrescriptions(true);

    const pollTimer = setInterval(() => {
      // Pause silent polling if pharmacist has opened an interactive modal
      if (!modalOpen && !rejectDialogOpen && !clarifyDialogOpen) {
        loadPrescriptions(false);
      }
    }, 5000);

    return () => clearInterval(pollTimer);
  }, [modalOpen, rejectDialogOpen, clarifyDialogOpen]);

  // Second ticker for last synced indicator
  useEffect(() => {
    const ticker = setInterval(() => {
      if (lastSynced) {
        setSecondsAgo(Math.floor((Date.now() - lastSynced.getTime()) / 1000));
      }
    }, 1000);
    return () => clearInterval(ticker);
  }, [lastSynced]);

  const getSyncLabel = () => {
    if (!lastSynced) return 'Connecting...';
    if (secondsAgo < 5) return 'Just now';
    if (secondsAgo < 60) return `${secondsAgo}s ago`;
    return `${Math.floor(secondsAgo / 60)}m ago`;
  };

  const showToast = (msg, severity = 'success') => {
    setToastMsg(msg);
    setToastSeverity(severity);
    setToastOpen(true);
  };

  const handleOpenModal = (rx) => {
    setSelectedRx(rx);
    setPharmacistNote(rx.pharmacistNotes || '');
    setModalOpen(true);
  };

  const handleCloseModal = () => {
    setModalOpen(false);
    setSelectedRx(null);
    setPharmacistNote('');
  };

  const handleApprove = async () => {
    if (!selectedRx || selectedRx.isFinalized) return;
    setActionLoading(true);
    try {
      const res = await verifyPrescription(selectedRx.id, 'Approved', pharmacistNote);
      if (res.success) {
        showToast(`Prescription #${selectedRx.id} successfully APPROVED.`);
        handleCloseModal();
        await loadPrescriptions(false);
      } else {
        showToast('Approval failed: ' + res.message, 'error');
      }
    } catch (err) {
      showToast('Approval failed: ' + (err.message || 'Error'), 'error');
    } finally {
      setActionLoading(false);
    }
  };

  const handleOpenReject = () => {
    setRejectReason('');
    setRejectDialogOpen(true);
  };

  const handleCloseReject = () => {
    setRejectDialogOpen(false);
    setRejectReason('');
  };

  const handleConfirmReject = async () => {
    if (!selectedRx || !rejectReason.trim()) {
      showToast('A mandatory rejection reason is required.', 'error');
      return;
    }
    setActionLoading(true);
    try {
      const res = await verifyPrescription(selectedRx.id, 'Rejected', rejectReason.trim());
      if (res.success) {
        showToast(`Prescription #${selectedRx.id} REJECTED with reason recorded.`);
        handleCloseReject();
        handleCloseModal();
        await loadPrescriptions(false);
      } else {
        showToast('Rejection failed: ' + res.message, 'error');
      }
    } catch (err) {
      showToast('Rejection failed: ' + (err.message || 'Error'), 'error');
    } finally {
      setActionLoading(false);
    }
  };

  const handleOpenClarify = () => {
    setClarificationNotes('');
    setClarifyDialogOpen(true);
  };

  const handleCloseClarify = () => {
    setClarifyDialogOpen(false);
    setClarificationNotes('');
  };

  const handleConfirmClarify = async () => {
    if (!selectedRx || !clarificationNotes.trim()) {
      showToast('Clarification instructions are required for the patient.', 'error');
      return;
    }
    setActionLoading(true);
    try {
      const res = await requestClarification(selectedRx.id, clarificationNotes.trim());
      if (res.success) {
        showToast(`Prescription #${selectedRx.id} marked as Requires Clarification. Patient notified.`);
        handleCloseClarify();
        handleCloseModal();
        await loadPrescriptions(false);
      } else {
        showToast('Clarification request failed: ' + res.message, 'error');
      }
    } catch (err) {
      showToast('Failed to request clarification: ' + (err.message || 'Error'), 'error');
    } finally {
      setActionLoading(false);
    }
  };

  // Real-Time Metrics Calculation directly from database records
  const totalCount = prescriptions.length;
  const pendingCount = prescriptions.filter(p => p.status === 'Pending' || p.status === 'Under Review').length;
  const approvedCount = prescriptions.filter(p => p.status === 'Approved').length;
  const rejectedCount = prescriptions.filter(p => p.status === 'Rejected').length;
  const clarifyCount = prescriptions.filter(p => p.status === 'Requires Clarification').length;

  // Filtered dataset with live search
  const filteredData = prescriptions.filter((item) => {
    const sTerm = searchTerm.toLowerCase();
    const matchesSearch =
      (item.patientName || '').toLowerCase().includes(sTerm) ||
      (item.customerName || '').toLowerCase().includes(sTerm) ||
      (item.doctorName || '').toLowerCase().includes(sTerm) ||
      (item.id || '').toString().includes(sTerm) ||
      (item.rxId || '').toLowerCase().includes(sTerm);

    const matchesStatus =
      statusFilter === 'All' ||
      (statusFilter === 'Pending' && (item.status === 'Pending' || item.status === 'Under Review')) ||
      (statusFilter === 'Approved' && item.status === 'Approved') ||
      (statusFilter === 'Rejected' && item.status === 'Rejected') ||
      (statusFilter === 'Requires Clarification' && item.status === 'Requires Clarification') ||
      (statusFilter === 'Under Review' && item.status === 'Under Review');

    return matchesSearch && matchesStatus;
  });

  const paginatedData = filteredData.slice(page * rowsPerPage, page * rowsPerPage + rowsPerPage);

  const getStatusChip = (status) => {
    switch (status) {
      case 'Approved':
        return (
          <Chip
            icon={<CheckCircleIcon sx={{ fontSize: '13px !important' }} />}
            label="Approved"
            size="small"
            sx={{
              bgcolor: 'rgba(16, 185, 129, 0.12)',
              color: '#059669',
              fontWeight: 800,
              fontSize: '0.72rem',
              border: '1px solid rgba(16, 185, 129, 0.3)'
            }}
          />
        );
      case 'Rejected':
        return (
          <Chip
            icon={<HighlightOffIcon sx={{ fontSize: '13px !important' }} />}
            label="Rejected"
            size="small"
            sx={{
              bgcolor: 'rgba(239, 68, 68, 0.12)',
              color: '#dc2626',
              fontWeight: 800,
              fontSize: '0.72rem',
              border: '1px solid rgba(239, 68, 68, 0.3)'
            }}
          />
        );
      case 'Requires Clarification':
        return (
          <Chip
            icon={<HelpOutlineIcon sx={{ fontSize: '13px !important' }} />}
            label="Requires Clarification"
            size="small"
            sx={{
              bgcolor: 'rgba(139, 92, 246, 0.12)',
              color: '#7c3aed',
              fontWeight: 800,
              fontSize: '0.72rem',
              border: '1px solid rgba(139, 92, 246, 0.3)'
            }}
          />
        );
      case 'Under Review':
        return (
          <Chip
            icon={<HourglassEmptyIcon sx={{ fontSize: '13px !important' }} />}
            label="Under Review"
            size="small"
            sx={{
              bgcolor: 'rgba(59, 130, 246, 0.12)',
              color: '#2563eb',
              fontWeight: 800,
              fontSize: '0.72rem',
              border: '1px solid rgba(59, 130, 246, 0.3)'
            }}
          />
        );
      default:
        return (
          <Chip
            icon={<HourglassEmptyIcon sx={{ fontSize: '13px !important' }} />}
            label="Pending Verification"
            size="small"
            sx={{
              bgcolor: 'rgba(245, 158, 11, 0.12)',
              color: '#d97706',
              fontWeight: 800,
              fontSize: '0.72rem',
              border: '1px solid rgba(245, 158, 11, 0.3)'
            }}
          />
        );
    }
  };

  return (
    <Box display="flex" flexDirection="column" gap={2.5}>
      {/* Header Banner */}
      <Box display="flex" justifyContent="space-between" alignItems="center" flexWrap="wrap" gap={2}>
        <Box>
          <Stack direction="row" spacing={1.2} alignItems="center">
            <FactCheckIcon sx={{ fontSize: 28, color: '#10b981' }} />
            <Typography variant="h5" fontWeight={800} color="#0f172a" letterSpacing="-0.5px">
              Prescription Verification
            </Typography>
            <Chip
              label={`${pendingCount} Pending`}
              size="small"
              color={pendingCount > 0 ? 'warning' : 'default'}
              sx={{ fontWeight: 800, fontSize: '0.72rem' }}
            />
          </Stack>
          <Typography variant="body2" color="text.secondary" sx={{ mt: 0.3, fontSize: '0.84rem' }}>
            Live clinical verification queue. Review scanned medical prescriptions from database, inspect read-only extracted medicines, and record decisions.
          </Typography>
        </Box>

        <Stack direction="row" spacing={1.5} alignItems="center" flexWrap="wrap">
          {/* Live DB Sync Pulse Badge */}
          <Chip
            icon={
              <Box
                sx={{
                  width: 8,
                  height: 8,
                  borderRadius: '50%',
                  bgcolor: isSyncing ? '#38bdf8' : '#10b981',
                  boxShadow: isSyncing
                    ? '0 0 0 2px rgba(56, 189, 248, 0.4)'
                    : '0 0 0 2px rgba(16, 185, 129, 0.4)',
                  animation: 'pulse 1.8s infinite',
                  '@keyframes pulse': {
                    '0%': { transform: 'scale(0.95)', opacity: 0.8 },
                    '50%': { transform: 'scale(1.15)', opacity: 1 },
                    '100%': { transform: 'scale(0.95)', opacity: 0.8 }
                  }
                }}
              />
            }
            label={`Live DB Sync Active • ${prescriptions.length} Records • ${getSyncLabel()}`}
            size="small"
            sx={{
              bgcolor: 'rgba(16, 185, 129, 0.08)',
              color: '#059669',
              fontWeight: 700,
              fontSize: '0.74rem',
              border: '1px solid rgba(16, 185, 129, 0.25)',
              px: 0.5
            }}
          />

          <Button
            variant="contained"
            size="small"
            startIcon={
              <RefreshIcon
                fontSize="small"
                sx={{
                  animation: isSyncing ? 'spin 0.8s linear infinite' : 'none',
                  '@keyframes spin': { '100%': { transform: 'rotate(360deg)' } }
                }}
              />
            }
            onClick={() => loadPrescriptions(false)}
            disabled={isSyncing}
            sx={{
              borderRadius: 2,
              fontWeight: 700,
              textTransform: 'none',
              fontSize: '0.82rem',
              py: 0.7,
              px: 1.8,
              bgcolor: '#10b981',
              '&:hover': { bgcolor: '#059669' }
            }}
          >
            {isSyncing ? 'Syncing DB...' : 'Sync Now'}
          </Button>
        </Stack>
      </Box>

      {/* Metric Cards */}
      <Grid container spacing={2}>
        {[
          { title: 'Total Scans', count: totalCount, color: '#3b82f6', bg: 'rgba(59, 130, 246, 0.06)' },
          { title: 'Pending Verification', count: pendingCount, color: '#f59e0b', bg: 'rgba(245, 158, 11, 0.06)' },
          { title: 'Approved & Verified', count: approvedCount, color: '#10b981', bg: 'rgba(16, 185, 129, 0.06)' },
          { title: 'Rejected', count: rejectedCount, color: '#ef4444', bg: 'rgba(239, 68, 68, 0.06)' },
          { title: 'Clarification Needed', count: clarifyCount, color: '#8b5cf6', bg: 'rgba(139, 92, 246, 0.06)' }
        ].map((card, idx) => (
          <Grid item xs={12} sm={6} md={2.4} key={idx}>
            <Paper
              elevation={0}
              sx={{
                p: 2,
                borderRadius: 3,
                border: '1px solid',
                borderColor: `${card.color}30`,
                bgcolor: card.bg
              }}
            >
              <Typography variant="caption" fontWeight={700} color="text.secondary" textTransform="uppercase" sx={{ fontSize: '0.7rem' }}>
                {card.title}
              </Typography>
              <Typography variant="h4" fontWeight={800} color={card.color} sx={{ my: 0.2 }}>
                {card.count}
              </Typography>
            </Paper>
          </Grid>
        ))}
      </Grid>

      {/* Filter and Search Bar */}
      <Paper elevation={0} sx={{ p: 2, borderRadius: 3, border: '1px solid #e2e8f0', bgcolor: '#ffffff' }}>
        <Box display="flex" justifyContent="space-between" alignItems="center" flexWrap="wrap" gap={2}>
          <Stack direction="row" spacing={1} flexWrap="wrap" useFlexGap>
            {['All', 'Pending', 'Approved', 'Rejected', 'Requires Clarification'].map((st) => {
              const count = st === 'All'
                ? totalCount
                : (st === 'Pending'
                    ? pendingCount
                    : (st === 'Approved'
                        ? approvedCount
                        : (st === 'Rejected'
                            ? rejectedCount
                            : clarifyCount)));

              return (
                <Chip
                  key={st}
                  label={`${st} (${count})`}
                  onClick={() => { setStatusFilter(st); setPage(0); }}
                  variant={statusFilter === st ? 'filled' : 'outlined'}
                  color={statusFilter === st ? 'primary' : 'default'}
                  sx={{ fontWeight: 700, fontSize: '0.75rem', cursor: 'pointer' }}
                />
              );
            })}
          </Stack>

          <TextField
            size="small"
            placeholder="Search by Patient Name or Rx ID..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            InputProps={{
              startAdornment: (
                <InputAdornment position="start">
                  <SearchIcon fontSize="small" sx={{ color: '#94a3b8' }} />
                </InputAdornment>
              ),
              style: { borderRadius: 8, fontSize: '0.82rem', width: 280 }
            }}
          />
        </Box>
      </Paper>

      {/* Main Prescriptions Table */}
      <Paper elevation={0} sx={{ borderRadius: 3, border: '1px solid #e2e8f0', overflow: 'hidden' }}>
        <TableContainer>
          <Table size="small">
            <TableHead sx={{ bgcolor: '#f8fafc' }}>
              <TableRow>
                <TableCell sx={{ fontWeight: 800, fontSize: '0.78rem' }}>Rx ID</TableCell>
                <TableCell sx={{ fontWeight: 800, fontSize: '0.78rem' }}>Patient Details</TableCell>
                <TableCell sx={{ fontWeight: 800, fontSize: '0.78rem' }}>Prescription Image</TableCell>
                <TableCell sx={{ fontWeight: 800, fontSize: '0.78rem' }}>Extracted Medicines</TableCell>
                <TableCell sx={{ fontWeight: 800, fontSize: '0.78rem' }}>OCR Confidence</TableCell>
                <TableCell sx={{ fontWeight: 800, fontSize: '0.78rem' }}>Status</TableCell>
                <TableCell sx={{ fontWeight: 800, fontSize: '0.78rem' }}>Date</TableCell>
                <TableCell sx={{ fontWeight: 800, fontSize: '0.78rem', textAlign: 'right' }}>Action</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {loading && prescriptions.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={8} align="center" sx={{ py: 6 }}>
                    <Stack alignItems="center" spacing={1.5}>
                      <CircularProgress size={32} sx={{ color: '#10b981' }} />
                      <Typography variant="body2" color="text.secondary" fontWeight={600}>
                        Connecting to MediLoop PostgreSQL database...
                      </Typography>
                    </Stack>
                  </TableCell>
                </TableRow>
              ) : paginatedData.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={8} align="center" sx={{ py: 6 }}>
                    <Typography variant="body2" fontWeight={700} color="#64748b">
                      No prescriptions found matching "{statusFilter}" criteria.
                    </Typography>
                    <Typography variant="caption" color="#94a3b8" display="block" sx={{ mt: 0.5 }}>
                      New customer prescription uploads will appear here in real time automatically.
                    </Typography>
                  </TableCell>
                </TableRow>
              ) : (
                paginatedData.map((rx) => {
                  const initials = (rx.patientName || 'Patient').split(' ').map((n) => n[0]).join('').slice(0, 2).toUpperCase();

                  return (
                    <TableRow key={rx.id} hover sx={{ '&:last-child td': { border: 0 } }}>
                      <TableCell sx={{ py: 1.5 }}>
                        <Typography variant="body2" fontWeight={800} color="#059669" sx={{ fontSize: '0.82rem' }}>
                          {rx.rxId || `#RX-${rx.id}`}
                        </Typography>
                      </TableCell>

                      <TableCell sx={{ py: 1.5 }}>
                        <Stack direction="row" spacing={1.2} alignItems="center">
                          <Avatar sx={{ width: 28, height: 28, bgcolor: 'rgba(16, 185, 129, 0.15)', color: '#059669', fontSize: '0.75rem', fontWeight: 800 }}>
                            {initials}
                          </Avatar>
                          <Box>
                            <Typography variant="body2" fontWeight={700} color="#0f172a" sx={{ fontSize: '0.82rem' }}>
                              {rx.patientName}
                            </Typography>
                            <Typography variant="caption" color="text.secondary" sx={{ fontSize: '0.7rem' }}>
                              {rx.doctorName || 'Practitioner Rx'}
                            </Typography>
                          </Box>
                        </Stack>
                      </TableCell>

                      <TableCell sx={{ py: 1.5 }}>
                        <Box
                          onClick={() => handleOpenModal(rx)}
                          sx={{
                            width: 64,
                            height: 44,
                            borderRadius: 1.5,
                            overflow: 'hidden',
                            border: '1px solid #cbd5e1',
                            cursor: 'pointer',
                            bgcolor: '#0f172a',
                            position: 'relative',
                            '&:hover .zoom-pill': { opacity: 1 }
                          }}
                        >
                          <img
                            src={rx.imageUrl}
                            alt="Scan"
                            style={{ width: '100%', height: '100%', objectFit: 'cover' }}
                            onError={(e) => {
                              e.target.style.display = 'none';
                              if (e.target.nextElementSibling) {
                                e.target.nextElementSibling.style.display = 'flex';
                              }
                            }}
                          />
                          <Box
                            sx={{
                              display: 'none',
                              width: '100%',
                              height: '100%',
                              alignItems: 'center',
                              justifyContent: 'center',
                              bgcolor: '#f1f5f9',
                              color: '#94a3b8',
                              fontSize: '0.65rem',
                              fontWeight: 700
                            }}
                          >
                            Doc Rx
                          </Box>
                          <Box
                            className="zoom-pill"
                            sx={{
                              position: 'absolute',
                              inset: 0,
                              bgcolor: 'rgba(0,0,0,0.5)',
                              color: '#ffffff',
                              display: 'flex',
                              alignItems: 'center',
                              justifyContent: 'center',
                              opacity: 0,
                              transition: 'opacity 0.2s ease'
                            }}
                          >
                            <ZoomInIcon fontSize="small" />
                          </Box>
                        </Box>
                      </TableCell>

                      <TableCell sx={{ py: 1.5 }}>
                        {rx.medicines && rx.medicines.length > 0 ? (
                          <Stack direction="row" spacing={0.5} flexWrap="wrap" useFlexGap>
                            {rx.medicines.slice(0, 2).map((m, idx) => (
                              <Chip
                                key={idx}
                                label={`${m.name} (${m.quantity})`}
                                size="small"
                                sx={{ height: 22, fontSize: '0.7rem', fontWeight: 600, bgcolor: '#f1f5f9', color: '#334155' }}
                              />
                            ))}
                            {rx.medicines.length > 2 && (
                              <Chip
                                label={`+${rx.medicines.length - 2} more`}
                                size="small"
                                sx={{ height: 22, fontSize: '0.68rem', bgcolor: '#e2e8f0', fontWeight: 700 }}
                              />
                            )}
                          </Stack>
                        ) : (
                          <Typography variant="caption" color="text.secondary">
                            Manual verification needed
                          </Typography>
                        )}
                      </TableCell>

                      <TableCell sx={{ py: 1.5 }}>
                        <Chip
                          label={rx.ocrConfidence || '95%'}
                          size="small"
                          sx={{ height: 22, fontSize: '0.7rem', fontWeight: 700, bgcolor: 'rgba(59, 130, 246, 0.1)', color: '#2563eb' }}
                        />
                      </TableCell>

                      <TableCell sx={{ py: 1.5 }}>
                        {getStatusChip(rx.status)}
                      </TableCell>

                      <TableCell sx={{ py: 1.5, color: '#64748b', fontSize: '0.8rem' }}>
                        {rx.date || 'Today'}
                      </TableCell>

                      <TableCell sx={{ py: 1.5, textAlign: 'right' }}>
                        <Button
                          variant="contained"
                          size="small"
                          startIcon={<VisibilityIcon sx={{ fontSize: '14px !important' }} />}
                          onClick={() => handleOpenModal(rx)}
                          sx={{
                            borderRadius: 2,
                            fontSize: '0.76rem',
                            fontWeight: 700,
                            py: 0.45,
                            px: 1.4,
                            textTransform: 'none',
                            bgcolor: rx.status === 'Pending' ? '#f59e0b' : '#3b82f6',
                            '&:hover': { bgcolor: rx.status === 'Pending' ? '#d97706' : '#2563eb' }
                          }}
                        >
                          {rx.status === 'Pending' ? 'Verify' : 'Inspect'}
                        </Button>
                      </TableCell>
                    </TableRow>
                  );
                })
              )}
            </TableBody>
          </Table>
        </TableContainer>

        <TablePagination
          rowsPerPageOptions={[5, 10, 25]}
          component="div"
          count={filteredData.length}
          rowsPerPage={rowsPerPage}
          page={page}
          onPageChange={(e, newPage) => setPage(newPage)}
          onRowsPerPageChange={(e) => {
            setRowsPerPage(parseInt(e.target.value, 10));
            setPage(0);
          }}
        />
      </Paper>

      {/* Interactive Verification Modal */}
      <Dialog
        open={modalOpen}
        onClose={handleCloseModal}
        maxWidth="lg"
        fullWidth
        PaperProps={{ sx: { borderRadius: 3.5, maxHeight: '92vh' } }}
      >
        <DialogTitle sx={{ px: 3, py: 2, borderBottom: '1px solid #e2e8f0', bgcolor: '#f8fafc' }}>
          <Box display="flex" justifyContent="space-between" alignItems="center">
            <Stack direction="row" spacing={1.5} alignItems="center">
              <FactCheckIcon sx={{ color: '#10b981' }} />
              <Typography variant="h6" fontWeight={800} color="#0f172a">
                Prescription #{selectedRx?.id} Clinical Verification
              </Typography>
              {selectedRx && getStatusChip(selectedRx.status)}
            </Stack>
            <IconButton size="small" onClick={handleCloseModal} sx={{ color: '#64748b' }}>
              <CloseIcon fontSize="small" />
            </IconButton>
          </Box>
        </DialogTitle>

        <DialogContent sx={{ p: 3 }}>
          {selectedRx && (
            <Grid container spacing={3}>
              {/* Left Column: Original Scanned Image with Zoom & Download */}
              <Grid item xs={12} md={6}>
                <Typography variant="subtitle2" fontWeight={800} color="#0f172a" gutterBottom>
                  Original Uploaded Prescription
                </Typography>
                <Typography variant="caption" color="text.secondary" display="block" mb={1.5}>
                  Clinical source of truth. Zoom in to review doctor's handwritten notes, dosage instructions, and signature.
                </Typography>
                <Box sx={{ border: '1px solid #cbd5e1', borderRadius: 3, overflow: 'hidden', height: 460 }}>
                  <ImageViewer
                    imageUrl={selectedRx.imageUrl}
                    fileName={selectedRx.fileName}
                    alt={`Prescription #${selectedRx.id}`}
                  />
                </Box>
              </Grid>

              {/* Right Column: Read-Only Extracted Medicines & Decision Area */}
              <Grid item xs={12} md={6}>
                {selectedRx.isFinalized && (
                  <Alert
                    severity={selectedRx.status === 'Approved' ? 'success' : 'error'}
                    sx={{ mb: 2, borderRadius: 2.5, fontWeight: 600 }}
                  >
                    <AlertTitle sx={{ fontWeight: 800 }}>Decision Finalized</AlertTitle>
                    This prescription has already been <strong>{selectedRx.status.toUpperCase()}</strong>. Final decisions cannot be modified through the dispensary dashboard.
                    {selectedRx.pharmacistNotes && (
                      <Typography variant="caption" display="block" mt={0.5}>
                        Pharmacist remarks: {selectedRx.pharmacistNotes}
                      </Typography>
                    )}
                  </Alert>
                )}

                <Box display="flex" justifyContent="space-between" alignItems="center" mb={1}>
                  <Box>
                    <Stack direction="row" spacing={1} alignItems="center">
                      <LockIcon sx={{ fontSize: 16, color: '#64748b' }} />
                      <Typography variant="subtitle2" fontWeight={800} color="#0f172a">
                        Extracted Prescription Information (Read-Only)
                      </Typography>
                    </Stack>
                    <Typography variant="caption" color="text.secondary">
                      Extracted clinical data is immutable for patient safety and regulatory audit.
                    </Typography>
                  </Box>
                  <Chip label="Audit Locked" size="small" variant="outlined" sx={{ fontWeight: 700, fontSize: '0.68rem' }} />
                </Box>

                {/* Read-Only Extracted Items Table */}
                <Paper elevation={0} sx={{ border: '1px solid #e2e8f0', borderRadius: 2.5, maxHeight: 260, overflowY: 'auto', mb: 2 }}>
                  <Table size="small">
                    <TableHead sx={{ bgcolor: '#f8fafc' }}>
                      <TableRow>
                        <TableCell sx={{ fontWeight: 700, fontSize: '0.72rem', py: 1 }}>Medicine Name</TableCell>
                        <TableCell sx={{ fontWeight: 700, fontSize: '0.72rem', py: 1 }}>Strength</TableCell>
                        <TableCell sx={{ fontWeight: 700, fontSize: '0.72rem', py: 1 }}>Dosage / Frequency</TableCell>
                        <TableCell sx={{ fontWeight: 700, fontSize: '0.72rem', py: 1, textAlign: 'center' }}>Qty</TableCell>
                        <TableCell sx={{ fontWeight: 700, fontSize: '0.72rem', py: 1 }}>Instructions</TableCell>
                      </TableRow>
                    </TableHead>
                    <TableBody>
                      {selectedRx.medicines.length === 0 ? (
                        <TableRow>
                          <TableCell colSpan={5} align="center" sx={{ py: 3, color: 'text.secondary' }}>
                            No extracted medicines found on record.
                          </TableCell>
                        </TableRow>
                      ) : (
                        selectedRx.medicines.map((m, idx) => (
                          <TableRow key={idx}>
                            <TableCell sx={{ py: 1 }}>
                              <Typography variant="body2" fontWeight={700} color="#0f172a" sx={{ fontSize: '0.8rem' }}>
                                {m.name}
                              </Typography>
                            </TableCell>
                            <TableCell sx={{ py: 1, fontSize: '0.75rem', color: '#475569' }}>
                              {m.strength}
                            </TableCell>
                            <TableCell sx={{ py: 1 }}>
                              <Chip label={m.frequency} size="small" sx={{ height: 20, fontSize: '0.68rem', bgcolor: '#f1f5f9' }} />
                            </TableCell>
                            <TableCell sx={{ py: 1, textAlign: 'center', fontWeight: 800 }}>
                              {m.quantity}
                            </TableCell>
                            <TableCell sx={{ py: 1, fontSize: '0.72rem', color: '#64748b' }}>
                              {m.instructions || 'Standard'}
                            </TableCell>
                          </TableRow>
                        ))
                      )}
                    </TableBody>
                  </Table>
                </Paper>

                {/* Patient Information Summary */}
                <Paper elevation={0} sx={{ p: 1.8, borderRadius: 2.5, bgcolor: '#f8fafc', border: '1px solid #e2e8f0', mb: 2 }}>
                  <Typography variant="caption" fontWeight={800} color="text.secondary" textTransform="uppercase">
                    Patient & Clinical Context
                  </Typography>
                  <Grid container spacing={1.5} mt={0.2}>
                    <Grid item xs={6}>
                      <Typography variant="caption" color="text.secondary" display="block">Patient Name</Typography>
                      <Typography variant="body2" fontWeight={700}>{selectedRx.patientName}</Typography>
                    </Grid>
                    <Grid item xs={6}>
                      <Typography variant="caption" color="text.secondary" display="block">Doctor / Practitioner</Typography>
                      <Typography variant="body2" fontWeight={700}>{selectedRx.doctorName || 'Medical Officer'}</Typography>
                    </Grid>
                    <Grid item xs={6}>
                      <Typography variant="caption" color="text.secondary" display="block">Contact Number</Typography>
                      <Typography variant="body2">{selectedRx.patientDetails?.phone || '+91 9876543210'}</Typography>
                    </Grid>
                    <Grid item xs={6}>
                      <Typography variant="caption" color="text.secondary" display="block">Delivery Address</Typography>
                      <Typography variant="body2" noWrap>{selectedRx.patientDetails?.address || 'Pandharpur, Maharashtra'}</Typography>
                    </Grid>
                  </Grid>
                </Paper>

                {/* Pharmacist Remarks */}
                <Typography variant="subtitle2" fontWeight={800} color="#0f172a" gutterBottom sx={{ fontSize: '0.82rem' }}>
                  Pharmacist Clinical Notes & Verification Remarks
                </Typography>
                <TextField
                  fullWidth
                  multiline
                  rows={2}
                  size="small"
                  disabled={selectedRx.isFinalized}
                  placeholder="Enter comments or special instructions for the customer..."
                  value={pharmacistNote}
                  onChange={(e) => setPharmacistNote(e.target.value)}
                  InputProps={{ style: { borderRadius: 8, fontSize: '0.82rem' } }}
                />
              </Grid>
            </Grid>
          )}
        </DialogContent>

        <DialogActions sx={{ px: 3, py: 2, borderTop: '1px solid #e2e8f0', bgcolor: '#f8fafc', justifyContent: 'space-between' }}>
          <Button color="inherit" size="small" onClick={handleCloseModal} sx={{ fontWeight: 600 }}>
            Close
          </Button>

          <Stack direction="row" spacing={1.5}>
            {!selectedRx?.isFinalized && (
              <>
                <Button
                  variant="outlined"
                  color="secondary"
                  size="small"
                  startIcon={<ChatBubbleOutlineIcon fontSize="small" />}
                  onClick={handleOpenClarify}
                  disabled={actionLoading}
                  sx={{ borderRadius: 2, fontSize: '0.8rem', py: 0.6, px: 1.5, fontWeight: 700 }}
                >
                  Request Clarification
                </Button>
                <Button
                  variant="outlined"
                  color="error"
                  size="small"
                  startIcon={<CloseIcon fontSize="small" />}
                  onClick={handleOpenReject}
                  disabled={actionLoading}
                  sx={{ borderRadius: 2, fontSize: '0.8rem', py: 0.6, px: 1.5, fontWeight: 700 }}
                >
                  Reject
                </Button>
                <Button
                  variant="contained"
                  size="small"
                  startIcon={<CheckIcon fontSize="small" />}
                  onClick={handleApprove}
                  disabled={actionLoading}
                  sx={{
                    borderRadius: 2,
                    fontSize: '0.8rem',
                    py: 0.6,
                    px: 1.8,
                    fontWeight: 700,
                    bgcolor: '#10b981',
                    '&:hover': { bgcolor: '#059669' }
                  }}
                >
                  {actionLoading ? 'Processing...' : 'Approve & Verify'}
                </Button>
              </>
            )}
          </Stack>
        </DialogActions>
      </Dialog>

      {/* Reject Confirmation Dialog */}
      <Dialog open={rejectDialogOpen} onClose={handleCloseReject} maxWidth="xs" fullWidth PaperProps={{ sx: { borderRadius: 3 } }}>
        <DialogTitle sx={{ fontWeight: 800, color: '#dc2626' }}>
          Reject Prescription #{selectedRx?.id}
        </DialogTitle>
        <DialogContent>
          <Typography variant="body2" color="text.secondary" mb={2}>
            A mandatory clinical rejection reason must be recorded and sent to the patient:
          </Typography>
          <TextField
            fullWidth
            multiline
            rows={3}
            size="small"
            label="Rejection Reason"
            value={rejectReason}
            onChange={(e) => setRejectReason(e.target.value)}
            placeholder="e.g., Incomplete doctor signature, illegible dosage, expired prescription validity..."
            InputProps={{ style: { borderRadius: 8, fontSize: '0.82rem' } }}
          />
        </DialogContent>
        <DialogActions sx={{ px: 3, py: 1.8 }}>
          <Button size="small" onClick={handleCloseReject}>Cancel</Button>
          <Button variant="contained" color="error" size="small" onClick={handleConfirmReject} disabled={actionLoading} sx={{ borderRadius: 2, fontWeight: 700 }}>
            Confirm Rejection
          </Button>
        </DialogActions>
      </Dialog>

      {/* Clarification Dialog */}
      <Dialog open={clarifyDialogOpen} onClose={handleCloseClarify} maxWidth="sm" fullWidth PaperProps={{ sx: { borderRadius: 3 } }}>
        <DialogTitle sx={{ fontWeight: 800, color: '#7c3aed' }}>
          Request Clarification on Prescription #{selectedRx?.id}
        </DialogTitle>
        <DialogContent>
          <Typography variant="body2" color="text.secondary" mb={2}>
            Explain clearly to the customer what needs clarification or ask them to upload a clearer copy:
          </Typography>
          <TextField
            fullWidth
            multiline
            rows={3}
            size="small"
            label="Clarification Instructions for Customer"
            value={clarificationNotes}
            onChange={(e) => setClarificationNotes(e.target.value)}
            placeholder="e.g. Please upload a clear photo showing the doctor's registration stamp and full dosage duration..."
            InputProps={{ style: { borderRadius: 8, fontSize: '0.82rem' } }}
          />
        </DialogContent>
        <DialogActions sx={{ px: 3, py: 1.8 }}>
          <Button size="small" onClick={handleCloseClarify}>Cancel</Button>
          <Button variant="contained" color="secondary" size="small" onClick={handleConfirmClarify} disabled={actionLoading} sx={{ borderRadius: 2, fontWeight: 700 }}>
            Send Clarification Request
          </Button>
        </DialogActions>
      </Dialog>

      <SnackbarNotification open={toastOpen} message={toastMsg} severity={toastSeverity} onClose={() => setToastOpen(false)} />
    </Box>
  );
};

export default PrescriptionVerification;
