import React, { useState } from 'react';
import { useForm, Controller } from 'react-hook-form';
import {
  Box,
  Typography,
  Card,
  CardContent,
  Grid,
  TextField,
  Button,
  Avatar,
  Divider,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  IconButton
} from '@mui/material';
import PhotoCameraIcon from '@mui/icons-material/PhotoCamera';
import SecurityIcon from '@mui/icons-material/Security';
import { useAuth } from '../../context/AuthContext';
import SnackbarNotification from '../../components/common/SnackbarNotification';

const Profile = () => {
  const { user, updateProfile } = useAuth();
  
  // Toast notifications
  const [toastOpen, setToastOpen] = useState(false);
  const [toastMsg, setToastMsg] = useState('');
  
  // Password dialog
  const [passwordOpen, setPasswordOpen] = useState(false);

  const {
    control,
    handleSubmit,
    reset,
    formState: { errors }
  } = useForm({
    defaultValues: {
      name: user?.name || '',
      email: user?.email || '',
      phone: user?.phone || '',
      registrationNumber: user?.registrationNumber || '',
      pharmacyName: user?.pharmacyName || '',
      address: user?.address || ''
    }
  });

  const onSubmit = (data) => {
    updateProfile({
      ...user,
      ...data
    });
    setToastMsg('Profile details updated successfully.');
    setToastOpen(true);
  };

  const handleCancel = () => {
    reset({
      name: user?.name || '',
      email: user?.email || '',
      phone: user?.phone || '',
      registrationNumber: user?.registrationNumber || '',
      pharmacyName: user?.pharmacyName || '',
      address: user?.address || ''
    });
    setToastMsg('Changes discarded.');
    setToastOpen(true);
  };

  return (
    <Box display="flex" flexDirection="column" gap={3.5}>
      <Box>
        <Typography variant="h4" fontWeight={800} color="text.primary" letterSpacing="-0.5px">
          My Profile
        </Typography>
        <Typography variant="body2" color="text.secondary" sx={{ mt: 0.5 }}>
          Update your pharmacist identification, pharmacy affiliation details, and contact coordinates.
        </Typography>
      </Box>

      <Grid container spacing={4}>
        {/* Left Side: Avatar block */}
        <Grid item xs={12} md={4}>
          <Card variant="outlined" sx={{ borderRadius: 4, textAlign: 'center', p: 2 }}>
            <CardContent display="flex" flexDirection="column" alignItems="center">
              <Box position="relative" display="inline-block" sx={{ mx: 'auto', mb: 2 }}>
                <Avatar
                  src={user?.photoUrl}
                  alt={user?.name}
                  sx={{
                    width: 120,
                    height: 120,
                    fontSize: '3rem',
                    bgcolor: 'primary.main',
                    color: '#ffffff',
                    fontWeight: 700,
                    border: '4px solid',
                    borderColor: '#ffffff',
                    boxShadow: 2
                  }}
                >
                  {user?.name ? user.name.charAt(0) : 'P'}
                </Avatar>
                <IconButton
                  sx={{
                    position: 'absolute',
                    bottom: 0,
                    right: 4,
                    bgcolor: 'primary.main',
                    color: '#ffffff',
                    border: '2px solid #ffffff',
                    '&:hover': { bgcolor: 'primary.dark' },
                    p: 0.8
                  }}
                  onClick={() => alert('Photo upload dialog placeholder')}
                >
                  <PhotoCameraIcon fontSize="small" />
                </IconButton>
              </Box>
              <Typography variant="h6" fontWeight={700}>
                {user?.name}
              </Typography>
              <Typography variant="body2" color="text.secondary" gutterBottom>
                Registered Pharmacist
              </Typography>
              <Typography variant="caption" color="text.secondary" display="block" sx={{ mt: 0.5, mb: 3 }}>
                Reg Number: {user?.registrationNumber}
              </Typography>

              <Divider sx={{ mb: 3 }} />

              <Button
                variant="outlined"
                color="secondary"
                startIcon={<SecurityIcon />}
                onClick={() => setPasswordOpen(true)}
                fullWidth
                sx={{ borderRadius: 2.5 }}
              >
                Change Password
              </Button>
            </CardContent>
          </Card>
        </Grid>

        {/* Right Side: Inputs */}
        <Grid item xs={12} md={8}>
          <Card variant="outlined" sx={{ borderRadius: 4 }}>
            <CardContent sx={{ p: 4 }}>
              <Typography variant="h6" fontWeight={700} sx={{ mb: 3 }}>
                Pharmacist Identification
              </Typography>
              <form onSubmit={handleSubmit(onSubmit)} noValidate>
                <Grid container spacing={3}>
                  <Grid item xs={12} sm={6}>
                    <Controller
                      name="name"
                      control={control}
                      rules={{ required: 'Full Name is required' }}
                      render={({ field }) => (
                        <TextField
                          {...field}
                          fullWidth
                          label="Full Name"
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
                      name="email"
                      control={control}
                      rules={{
                        required: 'Email is required',
                        pattern: {
                          value: /^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}$/i,
                          message: 'Enter a valid email address'
                        }
                      }}
                      render={({ field }) => (
                        <TextField
                          {...field}
                          fullWidth
                          label="Email Address"
                          variant="outlined"
                          error={!!errors.email}
                          helperText={errors.email?.message}
                          InputProps={{ style: { borderRadius: 12 } }}
                        />
                      )}
                    />
                  </Grid>

                  <Grid item xs={12} sm={6}>
                    <Controller
                      name="phone"
                      control={control}
                      rules={{ required: 'Phone number is required' }}
                      render={({ field }) => (
                        <TextField
                          {...field}
                          fullWidth
                          label="Phone Number"
                          variant="outlined"
                          error={!!errors.phone}
                          helperText={errors.phone?.message}
                          InputProps={{ style: { borderRadius: 12 } }}
                        />
                      )}
                    />
                  </Grid>

                  <Grid item xs={12} sm={6}>
                    <Controller
                      name="registrationNumber"
                      control={control}
                      rules={{ required: 'Registration Number is required' }}
                      render={({ field }) => (
                        <TextField
                          {...field}
                          fullWidth
                          label="Pharmacist License / Registration"
                          variant="outlined"
                          error={!!errors.registrationNumber}
                          helperText={errors.registrationNumber?.message}
                          InputProps={{ style: { borderRadius: 12 } }}
                        />
                      )}
                    />
                  </Grid>

                  <Grid item xs={12}>
                    <Divider sx={{ my: 1 }} />
                  </Grid>

                  <Grid item xs={12}>
                    <Typography variant="h6" fontWeight={700}>
                      Pharmacy Credentials
                    </Typography>
                  </Grid>

                  <Grid item xs={12} sm={6}>
                    <Controller
                      name="pharmacyName"
                      control={control}
                      rules={{ required: 'Pharmacy Name is required' }}
                      render={({ field }) => (
                        <TextField
                          {...field}
                          fullWidth
                          label="Pharmacy Affiliation Name"
                          variant="outlined"
                          error={!!errors.pharmacyName}
                          helperText={errors.pharmacyName?.message}
                          InputProps={{ style: { borderRadius: 12 } }}
                        />
                      )}
                    />
                  </Grid>

                  <Grid item xs={12} sm={6}>
                    <Controller
                      name="address"
                      control={control}
                      rules={{ required: 'Pharmacy address is required' }}
                      render={({ field }) => (
                        <TextField
                          {...field}
                          fullWidth
                          label="Pharmacy Physical Address"
                          variant="outlined"
                          error={!!errors.address}
                          helperText={errors.address?.message}
                          InputProps={{ style: { borderRadius: 12 } }}
                        />
                      )}
                    />
                  </Grid>

                  <Grid item xs={12} display="flex" justifyContent="flex-end" gap={2} sx={{ mt: 2 }}>
                    <Button variant="outlined" color="inherit" onClick={handleCancel} sx={{ borderRadius: 2.5 }}>
                      Cancel
                    </Button>
                    <Button type="submit" variant="contained" color="primary" sx={{ borderRadius: 2.5, boxShadow: 'none' }}>
                      Save Changes
                    </Button>
                  </Grid>
                </Grid>
              </form>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Change Password Dialog */}
      <Dialog open={passwordOpen} onClose={() => setPasswordOpen(false)} maxWidth="xs" fullWidth>
        <DialogTitle sx={{ fontWeight: 600 }}>Change Security Password</DialogTitle>
        <DialogContent dividers>
          <Box display="flex" flexDirection="column" gap={2} sx={{ mt: 1 }}>
            <TextField label="Current Password" type="password" fullWidth InputProps={{ style: { borderRadius: 12 } }} />
            <TextField label="New Password" type="password" fullWidth InputProps={{ style: { borderRadius: 12 } }} />
            <TextField label="Confirm New Password" type="password" fullWidth InputProps={{ style: { borderRadius: 12 } }} />
          </Box>
        </DialogContent>
        <DialogActions sx={{ px: 3, py: 2 }}>
          <Button onClick={() => setPasswordOpen(false)} color="inherit">
            Cancel
          </Button>
          <Button
            onClick={() => {
              setPasswordOpen(false);
              setToastMsg('Security password updated successfully.');
              setToastOpen(true);
            }}
            variant="contained"
            color="primary"
          >
            Update Password
          </Button>
        </DialogActions>
      </Dialog>

      <SnackbarNotification
        open={toastOpen}
        message={toastMsg}
        onClose={() => setToastOpen(false)}
      />
    </Box>
  );
};

export default Profile;
