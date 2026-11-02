import React, { useState, useEffect } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Box,
  Typography,
  Button,
  Tabs,
  Tab,
  Paper,
  Grid,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Chip,
  IconButton,
  Alert,
  CircularProgress,
  Stack
} from '@mui/material';
import CloseIcon from '@mui/icons-material/Close';
import InventoryIcon from '@mui/icons-material/Inventory';
import HistoryIcon from '@mui/icons-material/History';
import ArrowUpwardIcon from '@mui/icons-material/ArrowUpward';
import ArrowDownwardIcon from '@mui/icons-material/ArrowDownward';
import { useMedicineService } from '../../services/medicineService';

const ADJUSTMENT_REASONS = [
  { value: 'RESTOCK', label: 'Supplier Restock / Received Shipment (+)', isPositive: true },
  { value: 'PURCHASE', label: 'Direct Wholesale Purchase (+)', isPositive: true },
  { value: 'DAMAGED', label: 'Damaged / Broken Packaging (-)', isPositive: false },
  { value: 'EXPIRED', label: 'Expired Formulation Discard (-)', isPositive: false },
  { value: 'RETURNED', label: 'Patient Return to Shelf (+)', isPositive: true },
  { value: 'AUDIT_CORRECTION', label: 'Physical Audit Cycle Count Correction (+/-)', isPositive: null }
];

const StockManagementDialog = ({ open, onClose, selectedMedicine, medicinesList = [], onStockUpdated }) => {
  const { adjustStock, getStockMovements } = useMedicineService();

  const [currentTab, setCurrentTab] = useState(0);
  const [targetMedicineId, setTargetMedicineId] = useState('');
  const [movementType, setMovementType] = useState('RESTOCK');
  const [quantity, setQuantity] = useState('');
  const [batchNumber, setBatchNumber] = useState('');
  const [expiryDate, setExpiryDate] = useState('');
  const [notes, setNotes] = useState('');
  const [loading, setLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState('');
  const [successMsg, setSuccessMsg] = useState('');

  // History Tab
  const [movements, setMovements] = useState([]);
  const [loadingHistory, setLoadingHistory] = useState(false);

  useEffect(() => {
    if (selectedMedicine) {
      setTargetMedicineId(selectedMedicine.id);
      setBatchNumber(selectedMedicine.batchNumber || '');
      setExpiryDate(selectedMedicine.expiryDate || '');
    } else if (medicinesList.length > 0) {
      setTargetMedicineId(medicinesList[0].id);
    }
  }, [selectedMedicine, medicinesList, open]);

  useEffect(() => {
    if (open && currentTab === 1) {
      fetchMovements();
    }
  }, [open, currentTab]);

  const fetchMovements = async () => {
    setLoadingHistory(true);
    const data = await getStockMovements();
    setMovements(data);
    setLoadingHistory(false);
  };

  const handleClose = () => {
    setErrorMsg('');
    setSuccessMsg('');
    setQuantity('');
    setNotes('');
    onClose();
  };

  const handleSubmitAdjustment = async (e) => {
    e.preventDefault();
    const qtyNum = parseInt(quantity, 10);
    if (!targetMedicineId || isNaN(qtyNum) || qtyNum === 0) {
      setErrorMsg('Please enter a valid non-zero quantity.');
      return;
    }

    setLoading(true);
    setErrorMsg('');
    setSuccessMsg('');

    // Determine sign based on adjustment type if user entered positive number
    let finalQty = qtyNum;
    const selectedReason = ADJUSTMENT_REASONS.find(r => r.value === movementType);
    if (selectedReason && selectedReason.isPositive === false && finalQty > 0) {
      finalQty = -finalQty;
    }

    const payload = {
      movement_type: movementType,
      quantity_change: finalQty,
      batch_number: batchNumber.trim() || undefined,
      expiry_date: expiryDate || undefined,
      reference_notes: notes.trim() || undefined
    };

    const res = await adjustStock(targetMedicineId, payload);
    setLoading(false);

    if (res.success) {
      setSuccessMsg(`Stock updated successfully! New Balance: ${res.data?.new_stock_quantity || 'Updated'} units.`);
      setQuantity('');
      setNotes('');
      if (typeof onStockUpdated === 'function') {
        onStockUpdated();
      }
      setTimeout(() => {
        fetchMovements();
      }, 500);
    } else {
      setErrorMsg(res.message || 'Failed to apply stock adjustment.');
    }
  };

  return (
    <Dialog
      open={open}
      onClose={handleClose}
      maxWidth="md"
      fullWidth
      PaperProps={{ sx: { borderRadius: 3.5 } }}
    >
      <DialogTitle sx={{ px: 3, py: 2, borderBottom: '1px solid #e2e8f0', bgcolor: '#f8fafc', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <Box>
          <Typography variant="h6" fontWeight={800} color="#0f172a">
            Dispensary Stock & Inventory Management
          </Typography>
          <Typography variant="caption" color="text.secondary">
            Post stock adjustments, record batch receipts, write off expired meds, and view audit trail
          </Typography>
        </Box>
        <IconButton size="small" onClick={handleClose}>
          <CloseIcon fontSize="small" />
        </IconButton>
      </DialogTitle>

      <Box sx={{ borderBottom: 1, borderColor: 'divider', px: 3, bgcolor: '#ffffff' }}>
        <Tabs value={currentTab} onChange={(_, val) => setCurrentTab(val)}>
          <Tab icon={<InventoryIcon sx={{ fontSize: 18 }} />} iconPosition="start" label="Record Stock Adjustment" sx={{ fontWeight: 700, fontSize: '0.82rem', textTransform: 'none' }} />
          <Tab icon={<HistoryIcon sx={{ fontSize: 18 }} />} iconPosition="start" label="Stock Movement Audit Trail" sx={{ fontWeight: 700, fontSize: '0.82rem', textTransform: 'none' }} />
        </Tabs>
      </Box>

      <DialogContent sx={{ p: 3, minHeight: 380 }}>
        {errorMsg && (
          <Alert severity="error" sx={{ mb: 2.5, borderRadius: 2 }} onClose={() => setErrorMsg('')}>
            {errorMsg}
          </Alert>
        )}
        {successMsg && (
          <Alert severity="success" sx={{ mb: 2.5, borderRadius: 2 }} onClose={() => setSuccessMsg('')}>
            {successMsg}
          </Alert>
        )}

        {/* TAB 0: Record Adjustment */}
        {currentTab === 0 && (
          <Box component="form" onSubmit={handleSubmitAdjustment} display="flex" flexDirection="column" gap={2.5}>
            <Grid container spacing={2.5}>
              <Grid item xs={12} sm={6}>
                <FormControl fullWidth size="small">
                  <InputLabel id="med-select-label">Select Medicine SKU</InputLabel>
                  <Select
                    labelId="med-select-label"
                    value={targetMedicineId}
                    label="Select Medicine SKU"
                    onChange={(e) => setTargetMedicineId(e.target.value)}
                    sx={{ borderRadius: 2, fontSize: '0.85rem' }}
                  >
                    {medicinesList.map((m) => (
                      <MenuItem key={m.id} value={m.id} sx={{ fontSize: '0.82rem' }}>
                        {m.name} — Current: <strong>{m.stockQuantity ?? m.stock ?? 0} units</strong>
                      </MenuItem>
                    ))}
                  </Select>
                </FormControl>
              </Grid>

              <Grid item xs={12} sm={6}>
                <FormControl fullWidth size="small">
                  <InputLabel id="type-select-label">Movement / Reason</InputLabel>
                  <Select
                    labelId="type-select-label"
                    value={movementType}
                    label="Movement / Reason"
                    onChange={(e) => setMovementType(e.target.value)}
                    sx={{ borderRadius: 2, fontSize: '0.85rem' }}
                  >
                    {ADJUSTMENT_REASONS.map((r) => (
                      <MenuItem key={r.value} value={r.value} sx={{ fontSize: '0.82rem' }}>
                        {r.label}
                      </MenuItem>
                    ))}
                  </Select>
                </FormControl>
              </Grid>

              <Grid item xs={12} sm={4}>
                <TextField
                  fullWidth
                  size="small"
                  type="number"
                  label="Quantity Change"
                  value={quantity}
                  onChange={(e) => setQuantity(e.target.value)}
                  placeholder="e.g. 50 or -10"
                  required
                  InputProps={{ style: { borderRadius: 8, fontSize: '0.85rem' } }}
                  helperText="Units to add (+) or subtract (-)"
                />
              </Grid>

              <Grid item xs={12} sm={4}>
                <TextField
                  fullWidth
                  size="small"
                  label="Batch Number"
                  value={batchNumber}
                  onChange={(e) => setBatchNumber(e.target.value)}
                  placeholder="e.g. BAT-2026-08"
                  InputProps={{ style: { borderRadius: 8, fontSize: '0.85rem' } }}
                />
              </Grid>

              <Grid item xs={12} sm={4}>
                <TextField
                  fullWidth
                  size="small"
                  type="date"
                  label="Batch Expiry Date"
                  value={expiryDate}
                  onChange={(e) => setExpiryDate(e.target.value)}
                  InputLabelProps={{ shrink: true }}
                  InputProps={{ style: { borderRadius: 8, fontSize: '0.85rem' } }}
                />
              </Grid>

              <Grid item xs={12}>
                <TextField
                  fullWidth
                  size="small"
                  multiline
                  rows={2}
                  label="Audit Notes & Reference"
                  value={notes}
                  onChange={(e) => setNotes(e.target.value)}
                  placeholder="e.g. Received shipment from Sun Pharma under PO #2049"
                  InputProps={{ style: { borderRadius: 8, fontSize: '0.85rem' } }}
                />
              </Grid>
            </Grid>

            <Box display="flex" justifyContent="flex-end" mt={1}>
              <Button
                type="submit"
                variant="contained"
                disabled={loading}
                sx={{
                  borderRadius: 2,
                  fontWeight: 700,
                  px: 3,
                  py: 1,
                  bgcolor: '#10b981',
                  '&:hover': { bgcolor: '#059669' }
                }}
              >
                {loading ? <CircularProgress size={20} color="inherit" /> : 'Confirm Stock Adjustment'}
              </Button>
            </Box>
          </Box>
        )}

        {/* TAB 1: Movement History Audit Trail */}
        {currentTab === 1 && (
          <Box display="flex" flexDirection="column" gap={2}>
            {loadingHistory ? (
              <Stack direction="row" spacing={1.5} alignItems="center" justifyContent="center" py={4}>
                <CircularProgress size={24} />
                <Typography variant="body2" color="text.secondary">Fetching live inventory movements...</Typography>
              </Stack>
            ) : movements.length === 0 ? (
              <Paper elevation={0} sx={{ p: 4, textAlign: 'center', border: '1px solid #e2e8f0', borderRadius: 2.5, bgcolor: '#f8fafc' }}>
                <Typography variant="body2" color="text.secondary">
                  No inventory movements recorded yet. Movements appear when orders are dispensed or stock is adjusted.
                </Typography>
              </Paper>
            ) : (
              <TableContainer component={Paper} elevation={0} sx={{ border: '1px solid #e2e8f0', borderRadius: 2.5, maxHeight: 360 }}>
                <Table size="small" stickyHeader>
                  <TableHead>
                    <TableRow sx={{ bgcolor: '#f8fafc' }}>
                      <TableCell sx={{ fontWeight: 700, fontSize: '0.74rem' }}>Timestamp</TableCell>
                      <TableCell sx={{ fontWeight: 700, fontSize: '0.74rem' }}>Medicine SKU</TableCell>
                      <TableCell sx={{ fontWeight: 700, fontSize: '0.74rem' }}>Type</TableCell>
                      <TableCell sx={{ fontWeight: 700, fontSize: '0.74rem', textAlign: 'center' }}>Change</TableCell>
                      <TableCell sx={{ fontWeight: 700, fontSize: '0.74rem', textAlign: 'center' }}>Balance</TableCell>
                      <TableCell sx={{ fontWeight: 700, fontSize: '0.74rem' }}>Batch / Reference</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {movements.map((m) => {
                      const isPos = m.quantity_change > 0;
                      return (
                        <TableRow key={m.id} sx={{ '&:hover': { bgcolor: '#f8fafc' } }}>
                          <TableCell sx={{ fontSize: '0.78rem', py: 1 }}>
                            {new Date(m.created_at).toLocaleString()}
                          </TableCell>
                          <TableCell sx={{ fontSize: '0.82rem', fontWeight: 700, py: 1 }}>
                            {m.medicine_name || `Medicine #${m.medicine_id}`}
                          </TableCell>
                          <TableCell sx={{ py: 1 }}>
                            <Chip label={m.movement_type} size="small" sx={{ height: 20, fontSize: '0.66rem', fontWeight: 700 }} />
                          </TableCell>
                          <TableCell sx={{ py: 1, textAlign: 'center' }}>
                            <Stack direction="row" spacing={0.5} alignItems="center" justifyContent="center">
                              {isPos ? (
                                <ArrowUpwardIcon sx={{ fontSize: 14, color: '#10b981' }} />
                              ) : (
                                <ArrowDownwardIcon sx={{ fontSize: 14, color: '#ef4444' }} />
                              )}
                              <Typography variant="caption" fontWeight={800} color={isPos ? '#10b981' : '#ef4444'}>
                                {isPos ? `+${m.quantity_change}` : m.quantity_change}
                              </Typography>
                            </Stack>
                          </TableCell>
                          <TableCell sx={{ py: 1, textAlign: 'center', fontWeight: 700, fontSize: '0.8rem' }}>
                            {m.balance_after}
                          </TableCell>
                          <TableCell sx={{ py: 1, fontSize: '0.75rem', color: '#64748b' }}>
                            {m.batch_number || m.reference_notes || '—'}
                          </TableCell>
                        </TableRow>
                      );
                    })}
                  </TableBody>
                </Table>
              </TableContainer>
            )}
          </Box>
        )}
      </DialogContent>

      <DialogActions sx={{ px: 3, py: 2, borderTop: '1px solid #e2e8f0', bgcolor: '#f8fafc' }}>
        <Button size="small" onClick={handleClose} sx={{ fontWeight: 600 }}>
          Close
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default StockManagementDialog;

