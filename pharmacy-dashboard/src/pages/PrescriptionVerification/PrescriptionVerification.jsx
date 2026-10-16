import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Box, Typography, Chip, Button, IconButton, Tooltip } from '@mui/material';
import VisibilityIcon from '@mui/icons-material/Visibility';
import CheckCircleOutlineIcon from '@mui/icons-material/CheckCircleOutlined';
import HighlightOffIcon from '@mui/icons-material/HighlightOff';
import HourglassEmptyIcon from '@mui/icons-material/HourglassEmpty';
import { usePrescriptionService } from '../../services/prescriptionService';
import { useMockData } from '../../context/MockDataContext';
import ReusableDataTable from '../../components/tables/ReusableDataTable';

const PrescriptionVerification = () => {
  const navigate = useNavigate();
  const { mockEnabled } = useMockData();
  const { getPrescriptions } = usePrescriptionService();
  const [loading, setLoading] = useState(true);
  const [prescriptions, setPrescriptions] = useState([]);

  useEffect(() => {
    const loadPrescriptions = async () => {
      setLoading(true);
      try {
        const data = await getPrescriptions();
        setPrescriptions(data);
      } catch (err) {
        console.error('Error fetching prescriptions', err);
      } finally {
        setLoading(false);
      }
    };
    loadPrescriptions();
  }, [mockEnabled]);

  const getStatusChip = (status) => {
    switch (status) {
      case 'Approved':
        return (
          <Chip
            icon={<CheckCircleOutlineIcon style={{ color: '#10b981' }} />}
            label="Approved"
            size="small"
            sx={{ bgcolor: 'success.lightBg', color: 'success.main', fontWeight: 600, border: '1px solid', borderColor: 'success.lightBorder' }}
          />
        );
      case 'Rejected':
        return (
          <Chip
            icon={<HighlightOffIcon style={{ color: '#ef4444' }} />}
            label="Rejected"
            size="small"
            sx={{ bgcolor: 'error.lightBg', color: 'error.main', fontWeight: 600, border: '1px solid', borderColor: 'error.lightBorder' }}
          />
        );
      default:
        return (
          <Chip
            icon={<HourglassEmptyIcon style={{ color: '#f59e0b' }} />}
            label="Pending"
            size="small"
            sx={{ bgcolor: 'warning.lightBg', color: 'warning.main', fontWeight: 600, border: '1px solid', borderColor: 'warning.lightBorder' }}
          />
        );
    }
  };

  const getAIStatusChip = (aiStatus) => {
    if (aiStatus === 'Success') {
      return (
        <Chip
          label="AI Extracted"
          size="small"
          color="success"
          variant="outlined"
          sx={{ fontWeight: 500 }}
        />
      );
    }
    if (aiStatus === 'Failed') {
      return (
        <Chip
          label="AI Failed"
          size="small"
          color="error"
          variant="outlined"
          sx={{ fontWeight: 500 }}
        />
      );
    }
    return (
      <Chip
        label="Pending AI"
        size="small"
        color="warning"
        variant="outlined"
        sx={{ fontWeight: 500 }}
      />
    );
  };

  const columns = [
    {
      id: 'id',
      label: 'Prescription ID',
      sortable: true
    },
    {
      id: 'customerName',
      label: 'Customer Name',
      sortable: true,
      render: (row) => <Typography variant="body2" fontWeight={600}>{row.customerName}</Typography>
    },
    {
      id: 'uploadTime',
      label: 'Upload Time',
      sortable: true,
      render: (row) => new Date(row.uploadTime).toLocaleString()
    },
    {
      id: 'aiStatus',
      label: 'AI Status',
      sortable: true,
      render: (row) => getAIStatusChip(row.aiStatus)
    },
    {
      id: 'status',
      label: 'Verification Status',
      sortable: true,
      render: (row) => getStatusChip(row.status)
    },
    {
      id: 'actions',
      label: 'Actions',
      align: 'right',
      render: (row) => (
        <Tooltip title="View Prescription Details">
          <IconButton
            color="primary"
            onClick={(e) => {
              e.stopPropagation(); // Avoid triggering row click twice if applicable
              navigate(`/prescriptions/${row.id}`);
            }}
          >
            <VisibilityIcon />
          </IconButton>
        </Tooltip>
      )
    }
  ];

  return (
    <Box display="flex" flexDirection="column" gap={3}>
      <Box>
        <Typography variant="h4" fontWeight={800} color="text.primary" letterSpacing="-0.5px">
          Prescription Verification
        </Typography>
        <Typography variant="body2" color="text.secondary" sx={{ mt: 0.5 }}>
          Verify scanned/uploaded patient prescriptions assisted by OCR AI translation.
        </Typography>
      </Box>

      <ReusableDataTable
        columns={columns}
        data={prescriptions}
        searchKey="customerName"
        searchPlaceholder="Search customer name..."
        filterOptions={[
          { key: 'status', label: 'Verification Status', options: ['Pending', 'Approved', 'Rejected'] }
        ]}
        dateFilterKey="uploadTime"
        loading={loading}
        emptyTitle="No prescriptions available"
        emptyDescription="There are no prescriptions requiring validation at this time."
        onRowClick={(row) => navigate(`/prescriptions/${row.id}`)}
      />
    </Box>
  );
};

export default PrescriptionVerification;
