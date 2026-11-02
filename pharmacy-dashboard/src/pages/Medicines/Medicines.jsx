import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Button,
  IconButton,
  Chip,
  Tooltip,
  Paper,
  Grid,
  Stack,
  LinearProgress
} from '@mui/material';
import AddIcon from '@mui/icons-material/Add';
import EditIcon from '@mui/icons-material/Edit';
import DeleteIcon from '@mui/icons-material/Delete';
import CheckCircleOutlineIcon from '@mui/icons-material/CheckCircleOutlined';
import HighlightOffIcon from '@mui/icons-material/HighlightOff';
import WarningAmberIcon from '@mui/icons-material/WarningAmber';
import MedicationIcon from '@mui/icons-material/Medication';
import RefreshIcon from '@mui/icons-material/Refresh';
import CloudUploadIcon from '@mui/icons-material/CloudUpload';
import Inventory2Icon from '@mui/icons-material/Inventory2';
import TuneIcon from '@mui/icons-material/Tune';
import { useMedicineService } from '../../services/medicineService';
import ReusableDataTable from '../../components/tables/ReusableDataTable';
import MedicineFormDialog from '../../components/dialogs/MedicineFormDialog';
import DeleteDialog from '../../components/dialogs/DeleteDialog';
import CatalogueImportDialog from '../../components/dialogs/CatalogueImportDialog';
import StockManagementDialog from '../../components/dialogs/StockManagementDialog';
import SnackbarNotification from '../../components/common/SnackbarNotification';

const Medicines = () => {
  const { getMedicines, addMedicine, updateMedicine, deleteMedicine } = useMedicineService();

  const [loading, setLoading] = useState(true);
  const [medicines, setMedicines] = useState([]);
  const [categoryFilter, setCategoryFilter] = useState('All');

  // Modal/Dialog states
  const [formOpen, setFormOpen] = useState(false);
  const [deleteOpen, setDeleteOpen] = useState(false);
  const [selectedMed, setSelectedMed] = useState(null);
  const [actionLoading, setActionLoading] = useState(false);

  // Import Wizard & Stock Management States
  const [importWizardOpen, setImportWizardOpen] = useState(false);
  const [stockDialogOpen, setStockDialogOpen] = useState(false);
  const [adjustingMed, setAdjustingMed] = useState(null);

  // Toast notifications
  const [toastOpen, setToastOpen] = useState(false);
  const [toastMsg, setToastMsg] = useState('');
  const [toastSeverity, setToastSeverity] = useState('success');

  const fetchMedicineList = async () => {
    setLoading(true);
    try {
      const data = await getMedicines();
      setMedicines(Array.isArray(data) ? data : []);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchMedicineList();
  }, []);

  const triggerToast = (msg, severity = 'success') => {
    setToastMsg(msg);
    setToastSeverity(severity);
    setToastOpen(true);
  };

  const handleOpenAdd = () => {
    setSelectedMed(null);
    setFormOpen(true);
  };

  const handleOpenEdit = (med) => {
    setSelectedMed(med);
    setFormOpen(true);
  };

  const handleOpenDelete = (med) => {
    setSelectedMed(med);
    setDeleteOpen(true);
  };

  const handleOpenStockAdjust = (med = null) => {
    setAdjustingMed(med);
    setStockDialogOpen(true);
  };

  const handleFormSubmit = async (formData) => {
    setActionLoading(true);
    try {
      if (selectedMed) {
        await updateMedicine(selectedMed.id, formData);
        triggerToast(`Medicine "${formData.name}" updated successfully.`);
      } else {
        await addMedicine(formData);
        triggerToast(`Medicine "${formData.name}" added to catalog.`);
      }
      setFormOpen(false);
      fetchMedicineList();
    } catch (err) {
      triggerToast('Operation failed: ' + err.message, 'error');
    } finally {
      setActionLoading(false);
    }
  };

  const handleDeleteConfirm = async () => {
    if (!selectedMed) return;
    setActionLoading(true);
    try {
      await deleteMedicine(selectedMed.id);
      triggerToast(`Medicine "${selectedMed.name}" removed from catalog.`, 'info');
      setDeleteOpen(false);
      fetchMedicineList();
    } catch (err) {
      triggerToast('Failed to delete medicine: ' + err.message, 'error');
    } finally {
      setActionLoading(false);
    }
  };

  // Accurate Metrics calculation from database stock counts
  const totalMeds = medicines.length;
  const inStockMeds = medicines.filter(m => (m.stockQuantity ?? m.stock ?? 0) > 25).length;
  const lowStockMeds = medicines.filter(m => {
    const q = m.stockQuantity ?? m.stock ?? 0;
    return q > 0 && q <= 25;
  }).length;
  const outOfStockMeds = medicines.filter(m => (m.stockQuantity ?? m.stock ?? 0) <= 0).length;
  const rxRequiredMeds = medicines.filter(m => m.prescriptionRequired).length;

  const stockHealthRate = totalMeds > 0 ? Math.round((inStockMeds / totalMeds) * 100) : 100;

  // Filtered by category tab
  const filteredMedicines = categoryFilter === 'All'
    ? medicines
    : medicines.filter(m => (m.category || '').toLowerCase().includes(categoryFilter.toLowerCase()));

  // Extract top categories
  const categoriesList = ['All', 'Analgesics', 'Antibiotics', 'Cardiovascular', 'Vitamins', 'Respiratory', 'Gastrointestinal'];

  const getPrescriptionReqChip = (req) => {
    return req ? (
      <Chip
        label="Rx Required"
        size="small"
        sx={{
          bgcolor: 'rgba(239, 68, 68, 0.08)',
          color: '#dc2626',
          fontWeight: 700,
          fontSize: '0.7rem',
          border: '1px solid rgba(239, 68, 68, 0.2)'
        }}
      />
    ) : (
      <Chip
        label="OTC Non-Rx"
        size="small"
        sx={{
          bgcolor: 'rgba(16, 185, 129, 0.08)',
          color: '#059669',
          fontWeight: 700,
          fontSize: '0.7rem',
          border: '1px solid rgba(16, 185, 129, 0.2)'
        }}
      />
    );
  };

  const getAvailabilityChip = (med) => {
    const q = med.stockQuantity ?? med.stock ?? 0;
    if (q <= 0) {
      return (
        <Chip
          icon={<HighlightOffIcon sx={{ fontSize: '14px !important', color: '#dc2626 !important' }} />}
          label="Out of Stock (0)"
          size="small"
          sx={{
            bgcolor: 'rgba(239, 68, 68, 0.1)',
            color: '#dc2626',
            fontWeight: 700,
            fontSize: '0.72rem',
            border: '1px solid rgba(239, 68, 68, 0.25)'
          }}
        />
      );
    }
    if (q <= 25) {
      return (
        <Chip
          icon={<WarningAmberIcon sx={{ fontSize: '14px !important', color: '#d97706 !important' }} />}
          label={`Low Stock (${q})`}
          size="small"
          sx={{
            bgcolor: 'rgba(245, 158, 11, 0.1)',
            color: '#d97706',
            fontWeight: 700,
            fontSize: '0.72rem',
            border: '1px solid rgba(245, 158, 11, 0.25)'
          }}
        />
      );
    }
    return (
      <Chip
        icon={<CheckCircleOutlineIcon sx={{ fontSize: '14px !important', color: '#059669 !important' }} />}
        label={`In Stock (${q})`}
        size="small"
        sx={{
          bgcolor: 'rgba(16, 185, 129, 0.1)',
          color: '#059669',
          fontWeight: 700,
          fontSize: '0.72rem',
          border: '1px solid rgba(16, 185, 129, 0.25)'
        }}
      />
    );
  };

  const columns = [
    {
      id: 'name',
      label: 'Medicine & Formulation',
      sortable: true,
      render: (row) => (
        <Box>
          <Typography variant="body2" fontWeight={700} color="#0f172a" sx={{ fontSize: '0.84rem' }}>
            {row.name}
          </Typography>
          <Typography variant="caption" color="text.secondary" sx={{ fontSize: '0.72rem' }}>
            {row.dosageForm || 'Oral Solid'} • {row.strength || 'Standard'}
          </Typography>
        </Box>
      )
    },
    {
      id: 'category',
      label: 'Therapeutic Category',
      sortable: true,
      render: (row) => (
        <Chip
          label={row.category || 'General'}
          size="small"
          sx={{
            height: 22,
            fontSize: '0.7rem',
            fontWeight: 600,
            bgcolor: '#f1f5f9',
            border: '1px solid #e2e8f0',
            color: '#334155'
          }}
        />
      )
    },
    {
      id: 'price',
      label: 'Selling Price',
      sortable: true,
      render: (row) => (
        <Typography variant="body2" fontWeight={700} color="#0f172a" sx={{ fontSize: '0.82rem' }}>
          ₹{(Number(row.sellingPrice || row.price || row.mrp || 35)).toFixed(2)}
        </Typography>
      )
    },
    {
      id: 'manufacturer',
      label: 'Manufacturer',
      sortable: true,
      render: (row) => (
        <Typography variant="caption" color="text.secondary" fontWeight={500} sx={{ fontSize: '0.78rem' }}>
          {row.manufacturer || 'Cipla / Sun Pharma'}
        </Typography>
      )
    },
    {
      id: 'prescriptionRequired',
      label: 'Rx Classification',
      sortable: true,
      render: (row) => getPrescriptionReqChip(row.prescriptionRequired)
    },
    {
      id: 'availability',
      label: 'Dispensary Stock',
      sortable: true,
      render: (row) => getAvailabilityChip(row)
    },
    {
      id: 'actions',
      label: 'Actions',
      align: 'right',
      render: (row) => (
        <Box display="flex" gap={0.5} justifyContent="flex-end">
          <Tooltip title="Stock Adjustment / Movement">
            <IconButton
              size="small"
              onClick={() => handleOpenStockAdjust(row)}
              sx={{
                p: 0.6,
                border: '1px solid #e2e8f0',
                borderRadius: 2,
                color: '#10b981',
                '&:hover': { bgcolor: 'rgba(16, 185, 129, 0.08)' }
              }}
            >
              <TuneIcon fontSize="small" />
            </IconButton>
          </Tooltip>
          <Tooltip title="Edit Details">
            <IconButton
              size="small"
              onClick={() => handleOpenEdit(row)}
              sx={{
                p: 0.6,
                border: '1px solid #e2e8f0',
                borderRadius: 2,
                color: '#3b82f6',
                '&:hover': { bgcolor: '#f0f9ff' }
              }}
            >
              <EditIcon fontSize="small" />
            </IconButton>
          </Tooltip>
          <Tooltip title="Delete Medicine">
            <IconButton
              size="small"
              onClick={() => handleOpenDelete(row)}
              sx={{
                p: 0.6,
                border: '1px solid #e2e8f0',
                borderRadius: 2,
                color: '#ef4444',
                '&:hover': { bgcolor: '#fef2f2' }
              }}
            >
              <DeleteIcon fontSize="small" />
            </IconButton>
          </Tooltip>
        </Box>
      )
    }
  ];

  const inventoryCards = [
    { title: 'Total Catalog SKUs', count: totalMeds, color: '#0f172a', bg: '#f8fafc', border: '#e2e8f0' },
    { title: 'In Stock SKUs (>25)', count: inStockMeds, color: '#10b981', bg: 'rgba(16, 185, 129, 0.05)', border: '#a7f3d0' },
    { title: 'Low Stock SKUs (1-25)', count: lowStockMeds, color: '#f59e0b', bg: 'rgba(245, 158, 11, 0.05)', border: '#fde68a' },
    { title: 'Out of Stock (0 units)', count: outOfStockMeds, color: '#ef4444', bg: 'rgba(239, 68, 68, 0.05)', border: '#fecaca' }
  ];

  return (
    <Box display="flex" flexDirection="column" gap={2.5}>
      {/* Header Banner */}
      <Box display="flex" justifyContent="space-between" alignItems="center" flexWrap="wrap" gap={2}>
        <Box>
          <Stack direction="row" spacing={1.2} alignItems="center">
            <MedicationIcon sx={{ fontSize: 28, color: '#10b981' }} />
            <Typography variant="h5" fontWeight={800} color="#0f172a" letterSpacing="-0.5px">
              Medicine Catalog & Inventory
            </Typography>
            <Chip
              label={`${totalMeds} Active SKUs`}
              size="small"
              sx={{ fontWeight: 700, fontSize: '0.7rem', bgcolor: '#f1f5f9' }}
            />
          </Stack>
          <Typography variant="body2" color="text.secondary" sx={{ mt: 0.3, fontSize: '0.84rem' }}>
            Maintain pharmaceutical formulations, live dispensary stock counts, bulk Excel catalogue ingestion, and batch movements.
          </Typography>
        </Box>

        <Stack direction="row" spacing={1.2} flexWrap="wrap">
          <Button
            variant="outlined"
            size="small"
            startIcon={<RefreshIcon fontSize="small" />}
            onClick={fetchMedicineList}
            sx={{
              borderRadius: 2,
              fontWeight: 700,
              textTransform: 'none',
              fontSize: '0.8rem',
              py: 0.6,
              px: 1.5
            }}
          >
            Refresh
          </Button>

          {/* Import Catalogue Wizard Button */}
          <Button
            variant="outlined"
            size="small"
            color="secondary"
            startIcon={<CloudUploadIcon fontSize="small" />}
            onClick={() => setImportWizardOpen(true)}
            sx={{
              borderRadius: 2,
              fontWeight: 700,
              textTransform: 'none',
              fontSize: '0.8rem',
              py: 0.6,
              px: 1.5,
              borderColor: '#8b5cf6',
              color: '#7c3aed',
              '&:hover': { bgcolor: 'rgba(139, 92, 246, 0.08)' }
            }}
          >
            Import Catalogue (Excel/CSV)
          </Button>

          {/* Manage Stock / Adjustments Button */}
          <Button
            variant="outlined"
            size="small"
            color="primary"
            startIcon={<Inventory2Icon fontSize="small" />}
            onClick={() => handleOpenStockAdjust(null)}
            sx={{
              borderRadius: 2,
              fontWeight: 700,
              textTransform: 'none',
              fontSize: '0.8rem',
              py: 0.6,
              px: 1.5
            }}
          >
            Manage Stock
          </Button>

          {/* Add New SKU Button */}
          <Button
            variant="contained"
            size="small"
            startIcon={<AddIcon fontSize="small" />}
            onClick={handleOpenAdd}
            sx={{
              borderRadius: 2,
              fontWeight: 700,
              textTransform: 'none',
              fontSize: '0.8rem',
              py: 0.6,
              px: 1.8,
              bgcolor: '#10b981',
              '&:hover': { bgcolor: '#059669' }
            }}
          >
            Add Medicine
          </Button>
        </Stack>
      </Box>

      {/* Visual Inventory Metrics Cards */}
      <Paper elevation={0} sx={{ p: 2.2, borderRadius: 3, border: '1px solid #e2e8f0', bgcolor: '#ffffff' }}>
        <Grid container spacing={1.5}>
          {inventoryCards.map((c) => (
            <Grid item xs={6} sm={3} key={c.title}>
              <Box
                sx={{
                  p: 1.5,
                  borderRadius: 2.5,
                  bgcolor: c.bg,
                  border: `1px solid ${c.border}`
                }}
              >
                <Typography variant="caption" sx={{ color: '#64748b', fontWeight: 700, textTransform: 'uppercase', fontSize: '0.66rem', display: 'block' }}>
                  {c.title}
                </Typography>
                <Typography variant="h5" fontWeight={800} sx={{ color: c.color, mt: 0.2 }}>
                  {c.count}
                </Typography>
              </Box>
            </Grid>
          ))}
        </Grid>
      </Paper>

      {/* Category Tabs */}
      <Paper elevation={0} sx={{ p: 1.5, borderRadius: 3, border: '1px solid #e2e8f0', bgcolor: '#ffffff' }}>
        <Stack direction="row" spacing={1} flexWrap="wrap">
          {categoriesList.map((cat) => {
            const isSelected = categoryFilter === cat;
            return (
              <Chip
                key={cat}
                label={cat}
                size="small"
                onClick={() => setCategoryFilter(cat)}
                sx={{
                  fontWeight: 700,
                  fontSize: '0.78rem',
                  cursor: 'pointer',
                  py: 1.8,
                  px: 0.5,
                  borderRadius: 2,
                  bgcolor: isSelected ? '#10b981' : '#f8fafc',
                  color: isSelected ? '#ffffff' : '#64748b',
                  border: isSelected ? '1px solid #10b981' : '1px solid #e2e8f0',
                  '&:hover': { bgcolor: isSelected ? '#059669' : '#f1f5f9' }
                }}
              />
            );
          })}
        </Stack>
      </Paper>

      {/* Reusable Data Table */}
      <ReusableDataTable
        columns={columns}
        data={filteredMedicines}
        searchKey="name"
        searchPlaceholder="Search by medicine name, generic molecule..."
        loading={loading}
        emptyTitle="No Medicines Found"
        emptyDescription="There are no medications matching your filter."
      />

      {/* Add / Edit Medicine Modal */}
      <MedicineFormDialog
        open={formOpen}
        onClose={() => setFormOpen(false)}
        onSubmit={handleFormSubmit}
        initialData={selectedMed}
        loading={actionLoading}
      />

      {/* Delete Confirmation Modal */}
      <DeleteDialog
        open={deleteOpen}
        onClose={() => setDeleteOpen(false)}
        onConfirm={handleDeleteConfirm}
        title="Remove Medicine from Catalog"
        message={`Are you sure you want to remove "${selectedMed?.name}"? Existing order references will be maintained.`}
        loading={actionLoading}
      />

      {/* Bulk Excel/CSV Import Wizard Modal */}
      <CatalogueImportDialog
        open={importWizardOpen}
        onClose={() => setImportWizardOpen(false)}
        onImportSuccess={() => {
          fetchMedicineList();
          triggerToast('Medicine catalogue imported successfully into PostgreSQL!');
        }}
      />

      {/* Stock Management & Movements Dialog */}
      <StockManagementDialog
        open={stockDialogOpen}
        onClose={() => setStockDialogOpen(false)}
        selectedMedicine={adjustingMed}
        medicinesList={medicines}
        onStockUpdated={() => {
          fetchMedicineList();
          triggerToast('Inventory stock updated!');
        }}
      />

      <SnackbarNotification
        open={toastOpen}
        message={toastMsg}
        severity={toastSeverity}
        onClose={() => setToastOpen(false)}
      />
    </Box>
  );
};

export default Medicines;
