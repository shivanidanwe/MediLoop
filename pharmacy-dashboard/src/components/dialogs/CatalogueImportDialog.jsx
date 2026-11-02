import React, { useState } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Box,
  Typography,
  Button,
  Stepper,
  Step,
  StepLabel,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Chip,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  RadioGroup,
  FormControlLabel,
  Radio,
  Alert,
  CircularProgress,
  IconButton,
  Stack,
  Divider
} from '@mui/material';
import CloseIcon from '@mui/icons-material/Close';
import CloudUploadIcon from '@mui/icons-material/CloudUpload';
import FileDownloadIcon from '@mui/icons-material/FileDownload';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import ErrorOutlineIcon from '@mui/icons-material/ErrorOutlineOutlined';
import ArrowBackIcon from '@mui/icons-material/ArrowBack';
import ArrowForwardIcon from '@mui/icons-material/ArrowForward';
import { useMedicineService } from '../../services/medicineService';

const STEPS = [
  'Upload File',
  'Column Mapping',
  'Data Preview',
  'Validation',
  'Import Mode',
  'Execution & Report'
];

const TARGET_FIELDS = [
  { key: 'brand_name', label: 'Medicine / Brand Name', required: true },
  { key: 'generic_name', label: 'Generic Molecule Name', required: false },
  { key: 'category', label: 'Therapeutic Category', required: false },
  { key: 'strength', label: 'Strength (e.g. 500mg)', required: false },
  { key: 'dosage_form', label: 'Dosage Form (e.g. Tablet, Syrup)', required: false },
  { key: 'mrp', label: 'MRP (₹)', required: false },
  { key: 'selling_price', label: 'Selling Price (₹)', required: false },
  { key: 'stock_quantity', label: 'Stock Quantity', required: false },
  { key: 'prescription_required', label: 'Prescription Required (Yes/No)', required: false },
  { key: 'manufacturer', label: 'Manufacturer / Brand', required: false }
];

const CatalogueImportDialog = ({ open, onClose, onImportSuccess }) => {
  const { previewCatalogueUpload, executeCatalogueImport } = useMedicineService();

  const [activeStep, setActiveStep] = useState(0);
  const [selectedFile, setSelectedFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState('');

  // Preview & Mapping data from backend
  const [previewData, setPreviewData] = useState(null);
  const [columnMapping, setColumnMapping] = useState({});
  const [importMode, setImportMode] = useState('update'); // 'add' or 'update'
  const [importResult, setImportResult] = useState(null);

  const resetState = () => {
    setActiveStep(0);
    setSelectedFile(null);
    setLoading(false);
    setErrorMsg('');
    setPreviewData(null);
    setColumnMapping({});
    setImportMode('update');
    setImportResult(null);
  };

  const handleClose = () => {
    resetState();
    onClose();
  };

  const handleDownloadSample = () => {
    const csvContent = "data:text/csv;charset=utf-8," +
      "Brand Name,Generic Name,Category,Strength,Dosage Form,Selling Price,MRP,Stock Quantity,Prescription Required,Manufacturer\n" +
      "Amoxicillin 500mg,Amoxicillin,Antibiotics,500mg,Capsule,85.00,105.00,120,Yes,Cipla Ltd\n" +
      "Paracetamol 650mg,Paracetamol,Analgesics,650mg,Tablet,32.00,40.00,250,No,Micro Labs\n" +
      "Cetirizine 10mg,Cetirizine,Antihistamines,10mg,Tablet,22.00,28.00,90,No,Dr Reddys\n" +
      "Azithromycin 500mg,Azithromycin,Antibiotics,500mg,Tablet,115.00,140.00,60,Yes,Sun Pharma\n";
    const encodedUri = encodeURI(csvContent);
    const link = document.createElement("a");
    link.setAttribute("href", encodedUri);
    link.setAttribute("download", "mediloop_catalogue_sample.csv");
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  const handleFileSelect = async (e) => {
    const file = e.target.files?.[0];
    if (!file) return;

    const ext = file.name.split('.').pop().toLowerCase();
    if (!['csv', 'xlsx', 'xls'].includes(ext)) {
      setErrorMsg('Please select a valid .csv, .xlsx, or .xls file.');
      return;
    }

    setSelectedFile(file);
    setErrorMsg('');
    setLoading(true);

    const res = await previewCatalogueUpload(file);
    setLoading(false);

    if (res.success && res.data) {
      setPreviewData(res.data);
      // Auto map detected columns
      const headers = res.data.headers || [];
      const autoMap = {};
      headers.forEach(h => {
        const lower = h.toLowerCase().replace(/[^a-z0-9]/g, '_');
        TARGET_FIELDS.forEach(tf => {
          if (lower.includes(tf.key) || lower.includes(tf.label.toLowerCase().slice(0, 5))) {
            autoMap[tf.key] = h;
          }
        });
      });
      // Ensure default fallback
      if (!autoMap['brand_name'] && headers.length > 0) autoMap['brand_name'] = headers[0];
      setColumnMapping(autoMap);
      setActiveStep(1); // Proceed to Step 2
    } else {
      setErrorMsg(res.message || 'Failed to inspect file structure.');
    }
  };

  const handleExecute = async () => {
    if (!selectedFile) return;
    setLoading(true);
    setErrorMsg('');

    const res = await executeCatalogueImport(selectedFile, importMode, columnMapping);
    setLoading(false);

    if (res.success && res.data) {
      setImportResult(res.data);
      setActiveStep(5); // Step 6: Execution & Report
      if (typeof onImportSuccess === 'function') {
        onImportSuccess();
      }
    } else {
      setErrorMsg(res.message || 'Import failed to complete on server.');
    }
  };

  const downloadFailedRecords = () => {
    if (!importResult || !importResult.errors || importResult.errors.length === 0) return;
    const header = "Row,Identifier,Error Description\n";
    const rows = importResult.errors.map(e => `"${e.row}","${e.identifier || ''}","${e.error}"`).join("\n");
    const blob = new Blob([header + rows], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.setAttribute("href", url);
    link.setAttribute("download", `mediloop_import_errors_${Date.now()}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
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
            Medicine Catalogue Import Wizard
          </Typography>
          <Typography variant="caption" color="text.secondary">
            Bulk ingest pharmaceutical catalogue via Excel or CSV with schema mapping & validation
          </Typography>
        </Box>
        <IconButton size="small" onClick={handleClose}>
          <CloseIcon fontSize="small" />
        </IconButton>
      </DialogTitle>

      <Box sx={{ px: 3, pt: 2.5, pb: 1, bgcolor: '#ffffff' }}>
        <Stepper activeStep={activeStep} alternativeLabel>
          {STEPS.map((label, idx) => (
            <Step key={label} completed={activeStep > idx}>
              <StepLabel
                StepIconProps={{
                  sx: {
                    '&.Mui-active': { color: '#3b82f6' },
                    '&.Mui-completed': { color: '#10b981' }
                  }
                }}
              >
                <Typography variant="caption" sx={{ fontSize: '0.72rem', fontWeight: activeStep === idx ? 700 : 500 }}>
                  {label}
                </Typography>
              </StepLabel>
            </Step>
          ))}
        </Stepper>
      </Box>

      <DialogContent sx={{ p: 3, minHeight: 340 }}>
        {errorMsg && (
          <Alert severity="error" sx={{ mb: 2.5, borderRadius: 2 }} onClose={() => setErrorMsg('')}>
            {errorMsg}
          </Alert>
        )}

        {/* STEP 1: Upload File */}
        {activeStep === 0 && (
          <Box display="flex" flexDirection="column" alignItems="center" justifyContent="center" gap={2.5} py={3}>
            <Box
              sx={{
                width: '100%',
                border: '2px dashed #93c5fd',
                borderRadius: 3,
                p: 4,
                textAlign: 'center',
                bgcolor: 'rgba(59, 130, 246, 0.03)',
                cursor: 'pointer',
                transition: 'all 0.2s ease',
                '&:hover': { bgcolor: 'rgba(59, 130, 246, 0.07)', borderColor: '#3b82f6' }
              }}
              component="label"
            >
              <input
                type="file"
                hidden
                accept=".csv, .xlsx, .xls"
                onChange={handleFileSelect}
              />
              <CloudUploadIcon sx={{ fontSize: 52, color: '#3b82f6', mb: 1 }} />
              <Typography variant="h6" fontWeight={700} color="#0f172a">
                Choose Excel or CSV Catalogue File
              </Typography>
              <Typography variant="body2" color="text.secondary" sx={{ mt: 0.5 }}>
                Drag and drop your spreadsheet here or click to browse files
              </Typography>
              <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mt: 1 }}>
                Supported Formats: .xlsx, .xls, .csv (Max 10 MB)
              </Typography>
            </Box>

            {loading && (
              <Stack direction="row" spacing={1.5} alignItems="center">
                <CircularProgress size={20} />
                <Typography variant="body2" color="text.secondary">
                  Parsing workbook columns & preview rows...
                </Typography>
              </Stack>
            )}

            <Button
              variant="text"
              size="small"
              startIcon={<FileDownloadIcon />}
              onClick={handleDownloadSample}
              sx={{ textTransform: 'none', fontWeight: 700, color: '#059669' }}
            >
              Download Sample MediLoop CSV Template
            </Button>
          </Box>
        )}

        {/* STEP 2: Column Mapping */}
        {activeStep === 1 && previewData && (
          <Box display="flex" flexDirection="column" gap={2}>
            <Typography variant="body2" color="text.secondary">
              Map the columns from your uploaded file (<strong>{previewData.filename}</strong>) to MediLoop catalog fields.
            </Typography>

            <Paper elevation={0} sx={{ border: '1px solid #e2e8f0', borderRadius: 2.5, overflow: 'hidden' }}>
              <Table size="small">
                <TableHead sx={{ bgcolor: '#f8fafc' }}>
                  <TableRow>
                    <TableCell sx={{ fontWeight: 700, fontSize: '0.75rem' }}>MediLoop Catalog Field</TableCell>
                    <TableCell sx={{ fontWeight: 700, fontSize: '0.75rem' }}>Status</TableCell>
                    <TableCell sx={{ fontWeight: 700, fontSize: '0.75rem' }}>Uploaded File Column</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {TARGET_FIELDS.map((field) => {
                    const currentMapping = columnMapping[field.key] || '';
                    return (
                      <TableRow key={field.key}>
                        <TableCell sx={{ py: 1 }}>
                          <Typography variant="body2" fontWeight={700} color="#0f172a" sx={{ fontSize: '0.82rem' }}>
                            {field.label}
                          </Typography>
                        </TableCell>
                        <TableCell sx={{ py: 1 }}>
                          {field.required ? (
                            <Chip label="Required" size="small" color="error" sx={{ height: 20, fontSize: '0.65rem', fontWeight: 700 }} />
                          ) : (
                            <Chip label="Optional" size="small" sx={{ height: 20, fontSize: '0.65rem' }} />
                          )}
                        </TableCell>
                        <TableCell sx={{ py: 1 }}>
                          <FormControl size="small" fullWidth>
                            <Select
                              value={currentMapping}
                              onChange={(e) => setColumnMapping({ ...columnMapping, [field.key]: e.target.value })}
                              displayEmpty
                              sx={{ fontSize: '0.82rem', borderRadius: 2 }}
                            >
                              <MenuItem value="">
                                <em>-- Do Not Map --</em>
                              </MenuItem>
                              {(previewData.headers || []).map((h) => (
                                <MenuItem key={h} value={h} sx={{ fontSize: '0.82rem' }}>
                                  {h}
                                </MenuItem>
                              ))}
                            </Select>
                          </FormControl>
                        </TableCell>
                      </TableRow>
                    );
                  })}
                </TableBody>
              </Table>
            </Paper>
          </Box>
        )}

        {/* STEP 3: Data Preview */}
        {activeStep === 2 && previewData && (
          <Box display="flex" flexDirection="column" gap={2}>
            <Stack direction="row" spacing={1.5} alignItems="center">
              <Chip label={`Total Rows: ${previewData.total_rows}`} size="small" sx={{ fontWeight: 700 }} />
              <Chip label={`Showing First ${previewData.preview_rows?.length || 0} Sample Rows`} size="small" color="primary" sx={{ fontWeight: 700 }} />
            </Stack>

            <TableContainer component={Paper} elevation={0} sx={{ border: '1px solid #e2e8f0', borderRadius: 2.5, maxHeight: 300 }}>
              <Table size="small" stickyHeader>
                <TableHead>
                  <TableRow>
                    {(previewData.headers || []).map((h) => (
                      <TableCell key={h} sx={{ fontWeight: 700, fontSize: '0.74rem', bgcolor: '#f8fafc', whiteSpace: 'nowrap' }}>
                        {h}
                      </TableCell>
                    ))}
                  </TableRow>
                </TableHead>
                <TableBody>
                  {(previewData.preview_rows || []).map((row, idx) => (
                    <TableRow key={idx}>
                      {(previewData.headers || []).map((h) => (
                        <TableCell key={h} sx={{ fontSize: '0.78rem', py: 0.8, whiteSpace: 'nowrap' }}>
                          {row[h] !== undefined && row[h] !== null ? String(row[h]) : '—'}
                        </TableCell>
                      ))}
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
          </Box>
        )}

        {/* STEP 4: Validation Summary */}
        {activeStep === 3 && previewData && (
          <Box display="flex" flexDirection="column" gap={2.5}>
            <Typography variant="body2" color="text.secondary">
              Review pre-flight validation checks before writing changes to the database.
            </Typography>

            <Paper elevation={0} sx={{ p: 2.5, border: '1px solid #e2e8f0', borderRadius: 2.5, bgcolor: '#f8fafc' }}>
              <Grid container spacing={2}>
                <Grid item xs={12} sm={4}>
                  <Box sx={{ p: 1.5, bgcolor: '#ffffff', borderRadius: 2, border: '1px solid #e2e8f0' }}>
                    <Typography variant="caption" color="text.secondary" display="block">Rows Detected</Typography>
                    <Typography variant="h5" fontWeight={800} color="#0f172a">{previewData.total_rows}</Typography>
                  </Box>
                </Grid>
                <Grid item xs={12} sm={4}>
                  <Box sx={{ p: 1.5, bgcolor: 'rgba(16, 185, 129, 0.08)', borderRadius: 2, border: '1px solid rgba(16, 185, 129, 0.2)' }}>
                    <Typography variant="caption" color="#059669" display="block">Mapped Columns</Typography>
                    <Typography variant="h5" fontWeight={800} color="#059669">
                      {Object.values(columnMapping).filter(Boolean).length} / {TARGET_FIELDS.length}
                    </Typography>
                  </Box>
                </Grid>
                <Grid item xs={12} sm={4}>
                  <Box sx={{ p: 1.5, bgcolor: 'rgba(59, 130, 246, 0.08)', borderRadius: 2, border: '1px solid rgba(59, 130, 246, 0.2)' }}>
                    <Typography variant="caption" color="#2563eb" display="block">Target Store</Typography>
                    <Typography variant="h6" fontWeight={800} color="#2563eb">Pandharpur (Store #6)</Typography>
                  </Box>
                </Grid>
              </Grid>
            </Paper>

            {!columnMapping['brand_name'] ? (
              <Alert severity="error" sx={{ borderRadius: 2 }}>
                Validation Error: <strong>Medicine / Brand Name</strong> must be mapped to proceed.
              </Alert>
            ) : (
              <Alert severity="success" sx={{ borderRadius: 2 }}>
                Validation passed! All required schema headers are mapped and ready to import.
              </Alert>
            )}
          </Box>
        )}

        {/* STEP 5: Import Mode Selection */}
        {activeStep === 4 && (
          <Box display="flex" flexDirection="column" gap={2.5}>
            <Typography variant="subtitle2" fontWeight={800} color="#0f172a">
              Select Catalogue Ingestion Strategy
            </Typography>

            <Paper elevation={0} sx={{ p: 2.5, border: '1px solid #e2e8f0', borderRadius: 2.5, bgcolor: '#f8fafc' }}>
              <RadioGroup
                value={importMode}
                onChange={(e) => setImportMode(e.target.value)}
              >
                <Box sx={{ p: 1.5, mb: 1.5, bgcolor: '#ffffff', borderRadius: 2, border: '1px solid #e2e8f0' }}>
                  <FormControlLabel
                    value="update"
                    control={<Radio color="primary" />}
                    label={
                      <Box>
                        <Typography variant="body2" fontWeight={700} color="#0f172a">
                          Update Existing Medicines & Add New Ones (Recommended)
                        </Typography>
                        <Typography variant="caption" color="text.secondary">
                          If medicine exists in catalog, updates prices and adds stock. New medicines are inserted.
                        </Typography>
                      </Box>
                    }
                  />
                </Box>

                <Box sx={{ p: 1.5, bgcolor: '#ffffff', borderRadius: 2, border: '1px solid #e2e8f0' }}>
                  <FormControlLabel
                    value="add"
                    control={<Radio color="primary" />}
                    label={
                      <Box>
                        <Typography variant="body2" fontWeight={700} color="#0f172a">
                          Add New Medicines Only (Skip Existing)
                        </Typography>
                        <Typography variant="caption" color="text.secondary">
                          Medicines that already exist in the database will be preserved unchanged.
                        </Typography>
                      </Box>
                    }
                  />
                </Box>
              </RadioGroup>
            </Paper>
          </Box>
        )}

        {/* STEP 6: Execution & Report */}
        {activeStep === 5 && importResult && (
          <Box display="flex" flexDirection="column" gap={2.5} alignItems="center" textAlign="center" py={2}>
            <CheckCircleIcon sx={{ fontSize: 60, color: '#10b981' }} />
            <Typography variant="h6" fontWeight={800} color="#0f172a">
              Catalogue Import Completed
            </Typography>

            <Paper elevation={0} sx={{ p: 2.5, border: '1px solid #e2e8f0', borderRadius: 2.5, bgcolor: '#f8fafc', width: '100%' }}>
              <Grid container spacing={2}>
                <Grid item xs={4}>
                  <Typography variant="caption" color="text.secondary" display="block">Imported New</Typography>
                  <Typography variant="h5" fontWeight={800} color="#10b981">+{importResult.imported || 0}</Typography>
                </Grid>
                <Grid item xs={4}>
                  <Typography variant="caption" color="text.secondary" display="block">Updated Existing</Typography>
                  <Typography variant="h5" fontWeight={800} color="#3b82f6">{importResult.updated || 0}</Typography>
                </Grid>
                <Grid item xs={4}>
                  <Typography variant="caption" color="text.secondary" display="block">Errors / Skipped</Typography>
                  <Typography variant="h5" fontWeight={800} color={importResult.errors?.length > 0 ? '#ef4444' : '#64748b'}>
                    {importResult.errors?.length || 0}
                  </Typography>
                </Grid>
              </Grid>
            </Paper>

            {importResult.errors && importResult.errors.length > 0 && (
              <Button
                variant="outlined"
                color="error"
                size="small"
                startIcon={<FileDownloadIcon />}
                onClick={downloadFailedRecords}
                sx={{ borderRadius: 2, textTransform: 'none', fontWeight: 700 }}
              >
                Download Failed Records CSV ({importResult.errors.length})
              </Button>
            )}
          </Box>
        )}
      </DialogContent>

      <DialogActions sx={{ px: 3, py: 2, borderTop: '1px solid #e2e8f0', bgcolor: '#f8fafc', justifyContent: 'space-between' }}>
        {activeStep > 0 && activeStep < 5 ? (
          <Button
            size="small"
            startIcon={<ArrowBackIcon />}
            onClick={() => setActiveStep(activeStep - 1)}
            disabled={loading}
            sx={{ fontWeight: 600 }}
          >
            Back
          </Button>
        ) : (
          <Box />
        )}

        <Box display="flex" gap={1.5}>
          {activeStep < 4 && (
            <Button
              variant="contained"
              size="small"
              endIcon={<ArrowForwardIcon />}
              disabled={loading || (activeStep === 0 && !selectedFile) || (activeStep === 1 && !columnMapping['brand_name'])}
              onClick={() => setActiveStep(activeStep + 1)}
              sx={{ borderRadius: 2, fontWeight: 700, px: 2.2 }}
            >
              Continue
            </Button>
          )}

          {activeStep === 4 && (
            <Button
              variant="contained"
              size="small"
              color="primary"
              disabled={loading || !columnMapping['brand_name']}
              onClick={handleExecute}
              sx={{ borderRadius: 2, fontWeight: 700, px: 2.5, bgcolor: '#10b981', '&:hover': { bgcolor: '#059669' } }}
            >
              {loading ? <CircularProgress size={20} color="inherit" /> : 'Execute Import to Catalog'}
            </Button>
          )}

          {activeStep === 5 && (
            <Button
              variant="contained"
              size="small"
              onClick={handleClose}
              sx={{ borderRadius: 2, fontWeight: 700, px: 2.5 }}
            >
              Close & View Catalog
            </Button>
          )}
        </Box>
      </DialogActions>
    </Dialog>
  );
};

export default CatalogueImportDialog;
