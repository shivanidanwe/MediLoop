import React, { useState, useEffect } from 'react';
import { Box, Typography, Button, IconButton, Chip, Tooltip } from '@mui/material';
import AddIcon from '@mui/icons-material/Add';
import EditIcon from '@mui/icons-material/Edit';
import DeleteIcon from '@mui/icons-material/Delete';
import CheckCircleOutlineIcon from '@mui/icons-material/CheckCircleOutlined';
import HighlightOffIcon from '@mui/icons-material/HighlightOff';
import { useMedicineService } from '../../services/medicineService';
import { useMockData } from '../../context/MockDataContext';
import ReusableDataTable from '../../components/tables/ReusableDataTable';
import MedicineFormDialog from '../../components/dialogs/MedicineFormDialog';
import DeleteDialog from '../../components/dialogs/DeleteDialog';
import SnackbarNotification from '../../components/common/SnackbarNotification';

const Medicines = () => {
  const { mockEnabled } = useMockData();
  const { getMedicines, addMedicine, updateMedicine, deleteMedicine } = useMedicineService();

  const [loading, setLoading] = useState(true);
  const [medicines, setMedicines] = useState([]);
  
  // Modal/Dialog states
  const [formOpen, setFormOpen] = useState(false);
  const [deleteOpen, setDeleteOpen] = useState(false);
  const [selectedMed, setSelectedMed] = useState(null);
  const [actionLoading, setActionLoading] = useState(false);

  // Toast notifications
  const [toastOpen, setToastOpen] = useState(false);
  const [toastMsg, setToastMsg] = useState('');

  const fetchMedicineList = async () => {
    setLoading(true);
    try {
      const data = await getMedicines();
      setMedicines(data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchMedicineList();
  }, [mockEnabled]);

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

  const handleFormSubmit = async (formData) => {
    setActionLoading(true);
    try {
      if (selectedMed) {
        // Edit flow
        await updateMedicine(selectedMed.id, formData);
        setToastMsg(`Medicine "${formData.name}" updated successfully.`);
      } else {
        // Add flow
        await addMedicine(formData);
        setToastMsg(`Medicine "${formData.name}" added to catalog.`);
      }
      setFormOpen(false);
      setToastOpen(true);
      fetchMedicineList();
    } catch (err) {
      console.error(err);
    } finally {
      setActionLoading(false);
    }
  };

  const handleDeleteConfirm = async () => {
    if (!selectedMed) return;
    setActionLoading(true);
    try {
      await deleteMedicine(selectedMed.id);
      setToastMsg(`Medicine "${selectedMed.name}" removed from catalog.`);
      setDeleteOpen(false);
      setToastOpen(true);
      fetchMedicineList();
    } catch (err) {
      console.error(err);
    } finally {
      setActionLoading(false);
    }
  };

  const getPrescriptionReqChip = (req) => {
    return req ? (
      <Chip label="Required" size="small" color="error" variant="outlined" sx={{ fontWeight: 600 }} />
    ) : (
      <Chip label="OTC (Over the Counter)" size="small" color="success" variant="outlined" sx={{ fontWeight: 500 }} />
    );
  };

  const getAvailabilityChip = (availability) => {
    return availability === 'In Stock' ? (
      <Chip
        icon={<CheckCircleOutlineIcon style={{ color: '#10b981' }} />}
        label="In Stock"
        size="small"
        sx={{ bgcolor: 'success.lightBg', color: 'success.main', fontWeight: 600 }}
      />
    ) : (
      <Chip
        icon={<HighlightOffIcon style={{ color: '#ef4444' }} />}
        label="Out of Stock"
        size="small"
        sx={{ bgcolor: 'error.lightBg', color: 'error.main', fontWeight: 600 }}
      />
    );
  };

  const columns = [
    {
      id: 'name',
      label: 'Medicine Name',
      sortable: true,
      render: (row) => <Typography variant="body2" fontWeight={600}>{row.name}</Typography>
    },
    { id: 'strength', label: 'Strength', sortable: true },
    { id: 'category', label: 'Category', sortable: true },
    { id: 'manufacturer', label: 'Manufacturer', sortable: true },
    {
      id: 'prescriptionRequired',
      label: 'Prescription Required',
      sortable: true,
      render: (row) => getPrescriptionReqChip(row.prescriptionRequired)
    },
    {
      id: 'availability',
      label: 'Availability',
      sortable: true,
      render: (row) => getAvailabilityChip(row.availability)
    },
    {
      id: 'actions',
      label: 'Actions',
      align: 'right',
      render: (row) => (
        <Box display="flex" gap={0.5} justifyContent="flex-end">
          <Tooltip title="Edit Medicine">
            <IconButton color="primary" onClick={() => handleOpenEdit(row)}>
              <EditIcon fontSize="small" />
            </IconButton>
          </Tooltip>
          <Tooltip title="Delete Medicine">
            <IconButton color="error" onClick={() => handleOpenDelete(row)}>
              <DeleteIcon fontSize="small" />
            </IconButton>
          </Tooltip>
        </Box>
      )
    }
  ];

  return (
    <Box display="flex" flexDirection="column" gap={3}>
      {/* Header operations */}
      <Box display="flex" justifyContent="space-between" alignItems="center" flexWrap="wrap" gap={2}>
        <Box>
          <Typography variant="h4" fontWeight={800} color="text.primary" letterSpacing="-0.5px">
            Medicine Catalog
          </Typography>
          <Typography variant="body2" color="text.secondary" sx={{ mt: 0.5 }}>
            Manage inventory status, prescription requirements, and active medication catalogs.
          </Typography>
        </Box>
        {mockEnabled && (
          <Button
            variant="contained"
            color="primary"
            startIcon={<AddIcon />}
            onClick={handleOpenAdd}
            sx={{ borderRadius: 2.5, boxShadow: 'none' }}
          >
            Add Medicine
          </Button>
        )}
      </Box>

      <ReusableDataTable
        columns={columns}
        data={medicines}
        searchKey="name"
        searchPlaceholder="Search medicines catalog..."
        filterOptions={[
          { key: 'availability', label: 'Availability', options: ['In Stock', 'Out of Stock'] }
        ]}
        loading={loading}
        emptyTitle="No medicines found"
        emptyDescription="There are no medications configured in the database catalog."
      />

      {/* Form Dialog */}
      <MedicineFormDialog
        open={formOpen}
        onClose={() => setFormOpen(false)}
        onSubmit={handleFormSubmit}
        initialData={selectedMed}
        loading={actionLoading}
      />

      {/* Delete Confirmation */}
      <DeleteDialog
        open={deleteOpen}
        title="Remove Catalog Medicine"
        message={`Are you sure you want to delete "${selectedMed?.name}"? Patients will no longer be able to request this medicine via orders.`}
        onDelete={handleDeleteConfirm}
        onCancel={() => setDeleteOpen(false)}
        loading={actionLoading}
      />

      <SnackbarNotification
        open={toastOpen}
        message={toastMsg}
        onClose={() => setToastOpen(false)}
      />
    </Box>
  );
};

export default Medicines;
