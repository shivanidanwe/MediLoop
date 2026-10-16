import React, { useEffect } from 'react';
import { useForm, Controller } from 'react-hook-form';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  TextField,
  FormControlLabel,
  Switch,
  MenuItem,
  Grid,
  Box
} from '@mui/material';

const MedicineFormDialog = ({
  open,
  onClose,
  onSubmit,
  initialData = null,
  loading = false
}) => {
  const isEdit = !!initialData;

  const {
    control,
    handleSubmit,
    reset,
    formState: { errors }
  } = useForm({
    defaultValues: {
      name: '',
      strength: '',
      category: '',
      manufacturer: '',
      prescriptionRequired: false,
      availability: 'In Stock'
    }
  });

  // Sync state whenever initialData changes (e.g. editing a different item)
  useEffect(() => {
    if (initialData) {
      reset({
        name: initialData.name || '',
        strength: initialData.strength || '',
        category: initialData.category || '',
        manufacturer: initialData.manufacturer || '',
        prescriptionRequired: !!initialData.prescriptionRequired,
        availability: initialData.availability || 'In Stock'
      });
    } else {
      reset({
        name: '',
        strength: '',
        category: '',
        manufacturer: '',
        prescriptionRequired: false,
        availability: 'In Stock'
      });
    }
  }, [initialData, reset, open]);

  const onFormSubmit = (data) => {
    onSubmit(data);
  };

  return (
    <Dialog open={open} onClose={loading ? undefined : onClose} maxWidth="sm" fullWidth>
      <DialogTitle sx={{ fontWeight: 600 }}>
        {isEdit ? 'Edit Catalog Medicine' : 'Add New Medicine'}
      </DialogTitle>
      
      <form onSubmit={handleSubmit(onFormSubmit)} noValidate>
        <DialogContent dividers>
          <Grid container spacing={2.5}>
            <Grid item xs={12}>
              <Controller
                name="name"
                control={control}
                rules={{ required: 'Medicine Name is required' }}
                render={({ field }) => (
                  <TextField
                    {...field}
                    fullWidth
                    label="Medicine Name"
                    variant="outlined"
                    error={!!errors.name}
                    helperText={errors.name?.message}
                    InputProps={{ style: { borderRadius: 12 } }}
                  />
                )}
              />
            </Grid>

            <Grid item xs={12} sm={6}>
              <Controller
                name="strength"
                control={control}
                rules={{ required: 'Strength/Concentration is required' }}
                render={({ field }) => (
                  <TextField
                    {...field}
                    fullWidth
                    label="Strength"
                    placeholder="e.g. 500mg, 5ml"
                    variant="outlined"
                    error={!!errors.strength}
                    helperText={errors.strength?.message}
                    InputProps={{ style: { borderRadius: 12 } }}
                  />
                )}
              />
            </Grid>

            <Grid item xs={12} sm={6}>
              <Controller
                name="category"
                control={control}
                rules={{ required: 'Category is required' }}
                render={({ field }) => (
                  <TextField
                    {...field}
                    fullWidth
                    label="Category"
                    placeholder="e.g. Analgesic, Antibiotic"
                    variant="outlined"
                    error={!!errors.category}
                    helperText={errors.category?.message}
                    InputProps={{ style: { borderRadius: 12 } }}
                  />
                )}
              />
            </Grid>

            <Grid item xs={12} sm={6}>
              <Controller
                name="manufacturer"
                control={control}
                rules={{ required: 'Manufacturer is required' }}
                render={({ field }) => (
                  <TextField
                    {...field}
                    fullWidth
                    label="Manufacturer"
                    variant="outlined"
                    error={!!errors.manufacturer}
                    helperText={errors.manufacturer?.message}
                    InputProps={{ style: { borderRadius: 12 } }}
                  />
                )}
              />
            </Grid>

            <Grid item xs={12} sm={6}>
              <Controller
                name="availability"
                control={control}
                render={({ field }) => (
                  <TextField
                    {...field}
                    select
                    fullWidth
                    label="Availability"
                    variant="outlined"
                    InputProps={{ style: { borderRadius: 12 } }}
                  >
                    <MenuItem value="In Stock">In Stock</MenuItem>
                    <MenuItem value="Out of Stock">Out of Stock</MenuItem>
                  </TextField>
                )}
              />
            </Grid>

            <Grid item xs={12}>
              <Box display="flex" alignItems="center">
                <Controller
                  name="prescriptionRequired"
                  control={control}
                  render={({ field: { value, onChange, ...rest } }) => (
                    <FormControlLabel
                      control={
                        <Switch
                          checked={value}
                          onChange={(e) => onChange(e.target.checked)}
                          color="primary"
                          {...rest}
                        />
                      }
                      label="Requires Prescription Verification"
                    />
                  )}
                />
              </Box>
            </Grid>
          </Grid>
        </DialogContent>

        <DialogActions sx={{ px: 3, py: 2 }}>
          <Button onClick={onClose} disabled={loading} color="inherit">
            Cancel
          </Button>
          <Button type="submit" disabled={loading} variant="contained" color="primary">
            {loading ? 'Submitting...' : isEdit ? 'Update Medicine' : 'Add Medicine'}
          </Button>
        </DialogActions>
      </form>
    </Dialog>
  );
};

export default MedicineFormDialog;
