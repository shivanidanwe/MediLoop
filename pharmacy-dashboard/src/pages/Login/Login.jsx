import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useForm, Controller } from 'react-hook-form';
import {
  Box,
  Card,
  CardContent,
  TextField,
  Button,
  Typography,
  IconButton,
  InputAdornment,
  Alert,
  CircularProgress,
  Chip,
  Stack,
  Divider,
  FormControlLabel,
  Checkbox,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Grid
} from '@mui/material';
import Visibility from '@mui/icons-material/Visibility';
import VisibilityOff from '@mui/icons-material/VisibilityOff';
import AllInclusiveIcon from '@mui/icons-material/AllInclusive';
import StorefrontIcon from '@mui/icons-material/Storefront';
import LockOutlinedIcon from '@mui/icons-material/LockOutlined';
import EmailOutlinedIcon from '@mui/icons-material/EmailOutlined';
import AutoAwesomeIcon from '@mui/icons-material/AutoAwesome';
import SecurityIcon from '@mui/icons-material/Security';
import SpeedIcon from '@mui/icons-material/Speed';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import CloseIcon from '@mui/icons-material/Close';
import ArrowForwardIcon from '@mui/icons-material/ArrowForward';
import { useAuth } from '../../context/AuthContext';
import apiClient from '../../api/apiClient';

const Login = () => {
  const { login } = useAuth();
  const navigate = useNavigate();

  const [showPassword, setShowPassword] = useState(false);
  const [errorMsg, setErrorMsg] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [rememberMe, setRememberMe] = useState(true);

  // Forgot password modal state
  const [forgotOpen, setForgotOpen] = useState(false);
  const [forgotEmail, setForgotEmail] = useState('');
  const [forgotLoading, setForgotLoading] = useState(false);
  const [forgotMessage, setForgotMessage] = useState({ text: '', type: '' });

  const demoAccounts = [
    {
      name: 'Kalawati Medical & General Stores',
      subtitle: 'Pandharpur • Store #6 (Prescription Store)',
      email: 'pharmacist@mediloop.com',
      password: 'password123'
    },
    {
      name: 'Shri Sitaram Maharaj Medical',
      subtitle: 'Pandharpur • Store #7 (Dr. Sitaram Bhosale)',
      email: 'sitaram@mediloop.com',
      password: 'password123'
    },
    {
      name: 'MediLoop Central Super Pharmacy',
      subtitle: 'Bengaluru • Store #2 (Dr. Ramesh Menon)',
      email: 'pharmacist.ramesh@mediloop.com',
      password: 'password123'
    }
  ];

  const {
    register,
    handleSubmit,
    setValue,
    watch,
    formState: { errors }
  } = useForm({
    defaultValues: {
      email: '',
      password: ''
    }
  });

  const currentEmail = watch('email');

  const handleTogglePassword = () => setShowPassword(!showPassword);

  const onSubmit = async (data) => {
    setIsLoading(true);
    setErrorMsg('');
    try {
      await login(data.email, data.password, rememberMe);
      navigate('/dashboard', { replace: true });
    } catch (err) {
      setErrorMsg(
        err.message || 'Authentication failed. Please verify pharmacist email and password.'
      );
    } finally {
      setIsLoading(false);
    }
  };

  const handleForgotPasswordSubmit = async (e) => {
    e.preventDefault();
    if (!forgotEmail || !forgotEmail.includes('@')) {
      setForgotMessage({ text: 'Please enter a valid registered email address.', type: 'error' });
      return;
    }

    setForgotLoading(true);
    setForgotMessage({ text: '', type: '' });
    try {
      const res = await apiClient.post('/auth/forgot-password', { email: forgotEmail.trim() });
      setForgotMessage({
        text: res.data?.message || `A verification OTP code has been dispatched to ${forgotEmail}. Please check your inbox or contact the Chief Pharmacy Administrator.`,
        type: 'success'
      });
    } catch (err) {
      const errDetail = err.response?.data?.detail;
      setForgotMessage({
        text: errDetail || 'No matching active account found. For security, please contact your Pharmacy System Administrator (admin@mediloop.com).',
        type: 'error'
      });
    } finally {
      setForgotLoading(false);
    }
  };

  return (
    <Box
      sx={{
        minHeight: '100vh',
        width: '100%',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        bgcolor: '#07152F', // Midnight Navy foundation
        position: 'relative',
        overflow: 'hidden',
        py: { xs: 4, md: 6 },
        px: { xs: 2, sm: 3, md: 5 }
      }}
    >
      {/* Dynamic Ambient Glow Spheres */}
      <Box
        sx={{
          position: 'absolute',
          top: '-15%',
          left: '-10%',
          width: { xs: 350, md: 650 },
          height: { xs: 350, md: 650 },
          borderRadius: '50%',
          background: 'radial-gradient(circle, rgba(39, 216, 232, 0.22) 0%, rgba(39, 216, 232, 0) 70%)',
          filter: 'blur(60px)',
          pointerEvents: 'none'
        }}
      />
      <Box
        sx={{
          position: 'absolute',
          bottom: '-15%',
          right: '-10%',
          width: { xs: 380, md: 700 },
          height: { xs: 380, md: 700 },
          borderRadius: '50%',
          background: 'radial-gradient(circle, rgba(71, 123, 255, 0.24) 0%, rgba(71, 123, 255, 0) 70%)',
          filter: 'blur(70px)',
          pointerEvents: 'none'
        }}
      />
      <Box
        sx={{
          position: 'absolute',
          top: '30%',
          right: '25%',
          width: { xs: 280, md: 500 },
          height: { xs: 280, md: 500 },
          borderRadius: '50%',
          background: 'radial-gradient(circle, rgba(136, 101, 247, 0.18) 0%, rgba(136, 101, 247, 0) 70%)',
          filter: 'blur(80px)',
          pointerEvents: 'none'
        }}
      />

      {/* Main Container - Responsive 2-Section Grid */}
      <Box
        sx={{
          width: '100%',
          maxWidth: 1200,
          zIndex: 1,
          display: 'flex',
          flexDirection: { xs: 'column', md: 'row' },
          alignItems: 'center',
          justifyContent: 'center',
          gap: { xs: 4, lg: 7 }
        }}
      >
        {/* ================= LEFT SECTION: BRANDING & SAAS SHOWCASE ================= */}
        <Box
          sx={{
            flex: { xs: 'none', md: 1 },
            width: '100%',
            maxWidth: { xs: 520, md: 560 },
            color: '#ffffff',
            display: 'flex',
            flexDirection: 'column',
            justifyContent: 'center'
          }}
        >
          {/* Top Pill: System Identity */}
          <Stack direction="row" spacing={1} alignItems="center" mb={2}>
            <Box
              sx={{
                display: 'inline-flex',
                alignItems: 'center',
                gap: 1,
                px: 2,
                py: 0.75,
                borderRadius: 5,
                bgcolor: 'rgba(39, 216, 232, 0.12)',
                border: '1.2px solid rgba(39, 216, 232, 0.35)',
                boxShadow: '0 0 16px rgba(39, 216, 232, 0.2)'
              }}
            >
              <AllInclusiveIcon sx={{ fontSize: 18, color: '#27D8E8' }} />
              <Typography
                variant="caption"
                fontWeight={800}
                letterSpacing="0.8px"
                sx={{
                  color: '#27D8E8',
                  textTransform: 'uppercase',
                  fontSize: '0.74rem'
                }}
              >
                MediLoop Platform 2.0
              </Typography>
            </Box>
            <Chip
              label="Live DB Sync"
              size="small"
              sx={{
                bgcolor: 'rgba(16, 185, 129, 0.15)',
                color: '#34d399',
                fontWeight: 700,
                fontSize: '0.7rem',
                border: '1px solid rgba(16, 185, 129, 0.35)'
              }}
            />
          </Stack>

          {/* Master Headline */}
          <Typography
            variant="h3"
            fontWeight={900}
            lineHeight={1.15}
            letterSpacing="-1.2px"
            sx={{
              fontSize: { xs: '2rem', sm: '2.5rem', lg: '3rem' },
              mb: 2,
              background: 'linear-gradient(135deg, #FFFFFF 30%, #C7D9FF 70%, #27D8E8 100%)',
              WebkitBackgroundClip: 'text',
              WebkitTextFillColor: 'transparent'
            }}
          >
            Smarter Pharmacy Management. Connected Care.
          </Typography>

          {/* Platform Description */}
          <Typography
            variant="body1"
            sx={{
              color: 'rgba(255, 255, 255, 0.76)',
              fontSize: { xs: '0.95rem', md: '1.05rem' },
              lineHeight: 1.65,
              mb: 4
            }}
          >
            An AI-powered agentic pharmacy management ecosystem connecting patients, prescriptions, autonomous inventory replenishment, and live pharmacist verification workflows in one seamless workspace.
          </Typography>

          {/* 3 Liquid Glass Feature Cards */}
          <Stack spacing={2} sx={{ mb: { xs: 2, md: 4 } }}>
            {/* Card 1 */}
            <Box
              sx={{
                p: 2,
                borderRadius: 3.5,
                background: 'linear-gradient(135deg, rgba(255, 255, 255, 0.07) 0%, rgba(255, 255, 255, 0.02) 100%)',
                backdropFilter: 'blur(16px)',
                border: '1px solid rgba(255, 255, 255, 0.12)',
                display: 'flex',
                alignItems: 'center',
                gap: 2,
                transition: 'all 0.25s ease',
                '&:hover': {
                  transform: 'translateX(6px)',
                  borderColor: 'rgba(39, 216, 232, 0.4)',
                  boxShadow: '0 8px 24px rgba(39, 216, 232, 0.15)'
                }
              }}
            >
              <Box
                sx={{
                  width: 44,
                  height: 44,
                  borderRadius: 2.5,
                  bgcolor: 'rgba(39, 216, 232, 0.15)',
                  color: '#27D8E8',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  flexShrink: 0
                }}
              >
                <AutoAwesomeIcon sx={{ fontSize: 24 }} />
              </Box>
              <Box>
                <Typography variant="subtitle2" fontWeight={800} color="#ffffff">
                  Autonomous Prescription OCR
                </Typography>
                <Typography variant="caption" sx={{ color: 'rgba(255, 255, 255, 0.65)', display: 'block' }}>
                  Sub-second optical text extraction, dosage parsing, and safety validation.
                </Typography>
              </Box>
            </Box>

            {/* Card 2 */}
            <Box
              sx={{
                p: 2,
                borderRadius: 3.5,
                background: 'linear-gradient(135deg, rgba(255, 255, 255, 0.07) 0%, rgba(255, 255, 255, 0.02) 100%)',
                backdropFilter: 'blur(16px)',
                border: '1px solid rgba(255, 255, 255, 0.12)',
                display: 'flex',
                alignItems: 'center',
                gap: 2,
                transition: 'all 0.25s ease',
                '&:hover': {
                  transform: 'translateX(6px)',
                  borderColor: 'rgba(136, 101, 247, 0.4)',
                  boxShadow: '0 8px 24px rgba(136, 101, 247, 0.15)'
                }
              }}
            >
              <Box
                sx={{
                  width: 44,
                  height: 44,
                  borderRadius: 2.5,
                  bgcolor: 'rgba(136, 101, 247, 0.15)',
                  color: '#8865F7',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  flexShrink: 0
                }}
              >
                <SpeedIcon sx={{ fontSize: 24 }} />
              </Box>
              <Box>
                <Typography variant="subtitle2" fontWeight={800} color="#ffffff">
                  9 Multi-Agent Intelligence Systems
                </Typography>
                <Typography variant="caption" sx={{ color: 'rgba(255, 255, 255, 0.65)', display: 'block' }}>
                  Autonomous stock replenishment, drug interaction alerts, and audit logging.
                </Typography>
              </Box>
            </Box>

            {/* Card 3 */}
            <Box
              sx={{
                p: 2,
                borderRadius: 3.5,
                background: 'linear-gradient(135deg, rgba(255, 255, 255, 0.07) 0%, rgba(255, 255, 255, 0.02) 100%)',
                backdropFilter: 'blur(16px)',
                border: '1px solid rgba(255, 255, 255, 0.12)',
                display: 'flex',
                alignItems: 'center',
                gap: 2,
                transition: 'all 0.25s ease',
                '&:hover': {
                  transform: 'translateX(6px)',
                  borderColor: 'rgba(71, 123, 255, 0.4)',
                  boxShadow: '0 8px 24px rgba(71, 123, 255, 0.15)'
                }
              }}
            >
              <Box
                sx={{
                  width: 44,
                  height: 44,
                  borderRadius: 2.5,
                  bgcolor: 'rgba(71, 123, 255, 0.15)',
                  color: '#477BFF',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  flexShrink: 0
                }}
              >
                <SecurityIcon sx={{ fontSize: 24 }} />
              </Box>
              <Box>
                <Typography variant="subtitle2" fontWeight={800} color="#ffffff">
                  HIPAA & 256-Bit Cryptographic Security
                </Typography>
                <Typography variant="caption" sx={{ color: 'rgba(255, 255, 255, 0.65)', display: 'block' }}>
                  JWT-authorized pharmacist role access protecting patient medical records.
                </Typography>
              </Box>
            </Box>
          </Stack>

          {/* Telemetry Stat Badges */}
          <Grid container spacing={2} sx={{ display: { xs: 'none', sm: 'flex' } }}>
            <Grid item xs={4}>
              <Box
                sx={{
                  p: 1.5,
                  borderRadius: 2.5,
                  bgcolor: 'rgba(255, 255, 255, 0.04)',
                  border: '1px solid rgba(255, 255, 255, 0.08)',
                  textAlign: 'center'
                }}
              >
                <Typography variant="h6" fontWeight={800} color="#27D8E8">
                  99.8%
                </Typography>
                <Typography variant="caption" color="rgba(255, 255, 255, 0.6)">
                  OCR Accuracy
                </Typography>
              </Box>
            </Grid>
            <Grid item xs={4}>
              <Box
                sx={{
                  p: 1.5,
                  borderRadius: 2.5,
                  bgcolor: 'rgba(255, 255, 255, 0.04)',
                  border: '1px solid rgba(255, 255, 255, 0.08)',
                  textAlign: 'center'
                }}
              >
                <Typography variant="h6" fontWeight={800} color="#8865F7">
                  9 Agents
                </Typography>
                <Typography variant="caption" color="rgba(255, 255, 255, 0.6)">
                  Active Orchestration
                </Typography>
              </Box>
            </Grid>
            <Grid item xs={4}>
              <Box
                sx={{
                  p: 1.5,
                  borderRadius: 2.5,
                  bgcolor: 'rgba(255, 255, 255, 0.04)',
                  border: '1px solid rgba(255, 255, 255, 0.08)',
                  textAlign: 'center'
                }}
              >
                <Typography variant="h6" fontWeight={800} color="#10B981">
                  100%
                </Typography>
                <Typography variant="caption" color="rgba(255, 255, 255, 0.6)">
                  Audit Logged
                </Typography>
              </Box>
            </Grid>
          </Grid>
        </Box>

        {/* ================= RIGHT SECTION: PREMIUM GLASS LOGIN CARD ================= */}
        <Box
          sx={{
            flex: { xs: 'none', md: 1 },
            width: '100%',
            maxWidth: { xs: 480, md: 500 }
          }}
        >
          <Card
            sx={{
              borderRadius: 4.5,
              background: 'rgba(255, 255, 255, 0.94)',
              backdropFilter: 'blur(28px)',
              WebkitBackdropFilter: 'blur(28px)',
              border: '1.5px solid rgba(255, 255, 255, 0.85)',
              boxShadow: '0 24px 64px -12px rgba(0, 0, 0, 0.35), 0 0 40px rgba(71, 123, 255, 0.15)',
              overflow: 'hidden',
              position: 'relative'
            }}
          >
            {/* Top Accent Gradient Bar */}
            <Box
              sx={{
                height: 5,
                width: '100%',
                background: 'linear-gradient(90deg, #27D8E8 0%, #477BFF 50%, #8865F7 100%)'
              }}
            />

            <CardContent sx={{ p: { xs: 3, sm: 4.5 } }}>
              {/* Header Branding */}
              <Box display="flex" flexDirection="column" alignItems="center" mb={3}>
                <Box
                  sx={{
                    width: 58,
                    height: 58,
                    borderRadius: 3.5,
                    background: 'linear-gradient(135deg, #477BFF 0%, #27D8E8 100%)',
                    color: '#ffffff',
                    mb: 2,
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    boxShadow: '0 10px 24px rgba(71, 123, 255, 0.35)'
                  }}
                >
                  <AllInclusiveIcon sx={{ fontSize: 34 }} />
                </Box>
                <Typography variant="h5" fontWeight={900} color="#07152F" letterSpacing="-0.5px">
                  Welcome Back
                </Typography>
                <Typography variant="body2" color="#64748B" sx={{ mt: 0.5, fontWeight: 500 }}>
                  Sign in to your pharmacist workspace.
                </Typography>
              </Box>

              {/* Error Alert Display */}
              {errorMsg && (
                <Alert
                  severity="error"
                  onClose={() => setErrorMsg('')}
                  sx={{
                    mb: 3,
                    borderRadius: 3,
                    fontWeight: 600,
                    bgcolor: 'rgba(239, 68, 68, 0.1)',
                    color: '#b91c1c',
                    border: '1px solid rgba(239, 68, 68, 0.25)'
                  }}
                >
                  {errorMsg}
                </Alert>
              )}

              {/* Main Login Form */}
              <form onSubmit={handleSubmit(onSubmit)} noValidate>
                <Stack spacing={2.2}>
                  {/* Email Field */}
                  <Box>
                    <Typography variant="caption" fontWeight={700} color="#334155" sx={{ mb: 0.75, display: 'block' }}>
                      Registered Pharmacist Email
                    </Typography>
                    <TextField
                      fullWidth
                      placeholder="e.g. pharmacist@mediloop.com"
                      variant="outlined"
                      type="email"
                      autoComplete="email"
                      error={!!errors.email}
                      helperText={errors.email?.message}
                      {...register('email', {
                        required: 'Pharmacist email address is required',
                        pattern: {
                          value: /^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}$/i,
                          message: 'Please enter a valid email address'
                        }
                      })}
                      InputProps={{
                        startAdornment: (
                          <InputAdornment position="start">
                            <EmailOutlinedIcon sx={{ color: '#477BFF', fontSize: 20 }} />
                          </InputAdornment>
                        ),
                        sx: {
                          borderRadius: 3,
                          bgcolor: '#f8fafc',
                          '&:hover': { bgcolor: '#ffffff' },
                          '&.Mui-focused': { bgcolor: '#ffffff' }
                        }
                      }}
                    />
                  </Box>

                  {/* Password Field */}
                  <Box>
                    <Typography variant="caption" fontWeight={700} color="#334155" sx={{ mb: 0.75, display: 'block' }}>
                      Access Password
                    </Typography>
                    <TextField
                      fullWidth
                      placeholder="••••••••••••"
                      variant="outlined"
                      type={showPassword ? 'text' : 'password'}
                      autoComplete="current-password"
                      error={!!errors.password}
                      helperText={errors.password?.message}
                      {...register('password', {
                        required: 'Password is required'
                      })}
                      InputProps={{
                        startAdornment: (
                          <InputAdornment position="start">
                            <LockOutlinedIcon sx={{ color: '#477BFF', fontSize: 20 }} />
                          </InputAdornment>
                        ),
                        endAdornment: (
                          <InputAdornment position="end">
                            <IconButton
                              onClick={handleTogglePassword}
                              edge="end"
                              size="small"
                              aria-label="toggle password visibility"
                              sx={{ color: '#64748B' }}
                            >
                              {showPassword ? <VisibilityOff fontSize="small" /> : <Visibility fontSize="small" />}
                            </IconButton>
                          </InputAdornment>
                        ),
                        sx: {
                          borderRadius: 3,
                          bgcolor: '#f8fafc',
                          '&:hover': { bgcolor: '#ffffff' },
                          '&.Mui-focused': { bgcolor: '#ffffff' }
                        }
                      }}
                    />
                  </Box>

                  {/* Remember Me & Forgot Password Row */}
                  <Box display="flex" justifyContent="space-between" alignItems="center">
                    <FormControlLabel
                      control={
                        <Checkbox
                          checked={rememberMe}
                          onChange={(e) => setRememberMe(e.target.checked)}
                          size="small"
                          sx={{
                            color: '#94a3b8',
                            '&.Mui-checked': { color: '#477BFF' }
                          }}
                        />
                      }
                      label={
                        <Typography variant="body2" sx={{ color: '#475569', fontSize: '0.84rem', fontWeight: 600 }}>
                          Remember me
                        </Typography>
                      }
                    />

                    <Typography
                      variant="body2"
                      onClick={() => {
                        setForgotOpen(true);
                        setForgotEmail(currentEmail || '');
                        setForgotMessage({ text: '', type: '' });
                      }}
                      sx={{
                        color: '#477BFF',
                        fontSize: '0.84rem',
                        fontWeight: 700,
                        cursor: 'pointer',
                        '&:hover': { textDecoration: 'underline' }
                      }}
                    >
                      Forgot password?
                    </Typography>
                  </Box>

                  {/* Sign In Button */}
                  <Button
                    type="submit"
                    fullWidth
                    variant="contained"
                    disabled={isLoading}
                    sx={{
                      py: 1.4,
                      borderRadius: 3,
                      fontSize: '0.96rem',
                      fontWeight: 800,
                      textTransform: 'none',
                      background: 'linear-gradient(135deg, #477BFF 0%, #8865F7 100%)',
                      boxShadow: '0 8px 22px rgba(71, 123, 255, 0.35)',
                      transition: 'all 0.22s ease',
                      '&:hover': {
                        background: 'linear-gradient(135deg, #3B82F6 0%, #7C3AED 100%)',
                        boxShadow: '0 10px 28px rgba(71, 123, 255, 0.45)',
                        transform: 'translateY(-1px)'
                      }
                    }}
                  >
                    {isLoading ? (
                      <Stack direction="row" spacing={1.5} alignItems="center">
                        <CircularProgress size={20} color="inherit" />
                        <span>Verifying Credentials...</span>
                      </Stack>
                    ) : (
                      <Stack direction="row" spacing={1} alignItems="center">
                        <span>Sign In to Workspace</span>
                        <ArrowForwardIcon sx={{ fontSize: 18 }} />
                      </Stack>
                    )}
                  </Button>
                </Stack>
              </form>

              {/* Fast 1-Click Demo Credentials Selector */}
              <Box sx={{ mt: 3.5 }}>
                <Divider sx={{ mb: 2 }}>
                  <Chip
                    label="FAST DEMO ACCOUNTS (POSTGRESQL)"
                    size="small"
                    sx={{
                      fontSize: '0.64rem',
                      fontWeight: 800,
                      bgcolor: '#f1f5f9',
                      color: '#475569',
                      letterSpacing: 0.5
                    }}
                  />
                </Divider>

                <Stack spacing={1}>
                  {demoAccounts.map((acc, index) => {
                    const isSelected = currentEmail === acc.email;
                    return (
                      <Box
                        key={index}
                        onClick={() => {
                          setValue('email', acc.email, { shouldValidate: true });
                          setValue('password', acc.password, { shouldValidate: true });
                        }}
                        sx={{
                          p: 1.2,
                          px: 1.6,
                          borderRadius: 2.5,
                          border: '1.2px solid',
                          borderColor: isSelected ? '#477BFF' : '#E2E8F0',
                          bgcolor: isSelected ? 'rgba(71, 123, 255, 0.08)' : '#F8FAFC',
                          cursor: 'pointer',
                          transition: 'all 0.15s ease',
                          '&:hover': {
                            borderColor: '#477BFF',
                            bgcolor: 'rgba(71, 123, 255, 0.05)'
                          }
                        }}
                      >
                        <Box display="flex" justifyContent="space-between" alignItems="center">
                          <Typography variant="body2" fontWeight={700} color="#07152F" sx={{ fontSize: '0.8rem' }}>
                            {acc.name}
                          </Typography>
                          <Chip
                            label="FILL"
                            size="small"
                            sx={{
                              height: 18,
                              fontSize: '0.62rem',
                              fontWeight: 800,
                              bgcolor: isSelected ? '#477BFF' : 'transparent',
                              color: isSelected ? '#ffffff' : '#64748B',
                              border: isSelected ? 'none' : '1px solid #cbd5e1'
                            }}
                          />
                        </Box>
                        <Typography variant="caption" color="text.secondary" sx={{ fontSize: '0.7rem' }}>
                          {acc.subtitle}
                        </Typography>
                      </Box>
                    );
                  })}
                </Stack>
              </Box>

              {/* Security & Copyright Footer */}
              <Box sx={{ mt: 3, pt: 2, borderTop: '1px solid #f1f5f9', textAlign: 'center' }}>
                <Typography variant="caption" color="#64748B" display="block">
                  Protected by 256-bit SSL encryption • HIPAA compliant architecture
                </Typography>
                <Typography variant="caption" color="#94a3b8" sx={{ fontSize: '0.68rem', mt: 0.5, display: 'block' }}>
                  © 2026 MediLoop Technologies Inc. All rights reserved.
                </Typography>
              </Box>
            </CardContent>
          </Card>
        </Box>
      </Box>

      {/* ================= FORGOT PASSWORD DIALOG ================= */}
      <Dialog
        open={forgotOpen}
        onClose={() => setForgotOpen(false)}
        maxWidth="xs"
        fullWidth
        slotProps={{
          paper: {
            sx: {
              borderRadius: 4,
              p: 1,
              bgcolor: '#ffffff',
              boxShadow: '0 20px 60px rgba(0,0,0,0.2)'
            }
          }
        }}
      >
        <DialogTitle sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', pb: 1 }}>
          <Typography variant="h6" fontWeight={800} color="#07152F">
            Password Recovery
          </Typography>
          <IconButton size="small" onClick={() => setForgotOpen(false)}>
            <CloseIcon fontSize="small" />
          </IconButton>
        </DialogTitle>

        <DialogContent dividers sx={{ pt: 2, display: 'flex', flexDirection: 'column', gap: 2 }}>
          <Typography variant="body2" color="text.secondary">
            Enter your registered pharmacist email address. A one-time verification code (OTP) will be dispatched to verify your identity.
          </Typography>

          {forgotMessage.text && (
            <Alert severity={forgotMessage.type || 'info'} sx={{ borderRadius: 2 }}>
              {forgotMessage.text}
            </Alert>
          )}

          <TextField
            autoFocus
            fullWidth
            label="Registered Pharmacist Email"
            type="email"
            value={forgotEmail}
            onChange={(e) => setForgotEmail(e.target.value)}
            disabled={forgotLoading}
            InputProps={{
              sx: { borderRadius: 2.5 }
            }}
          />

          <Box sx={{ p: 1.5, bgcolor: '#f8fafc', borderRadius: 2, border: '1px solid #e2e8f0' }}>
            <Typography variant="caption" color="text.secondary" display="block" fontWeight={600}>
              Need instant access?
            </Typography>
            <Typography variant="caption" color="text.secondary" display="block">
              For security compliance, emergency pharmacist credentials can also be reset directly by the Chief Supervising Pharmacist or via <strong>admin@mediloop.com</strong>.
            </Typography>
          </Box>
        </DialogContent>

        <DialogActions sx={{ p: 2 }}>
          <Button onClick={() => setForgotOpen(false)} color="inherit" sx={{ fontWeight: 600 }}>
            Cancel
          </Button>
          <Button
            variant="contained"
            onClick={handleForgotPasswordSubmit}
            disabled={forgotLoading || !forgotEmail}
            sx={{
              borderRadius: 2.5,
              fontWeight: 700,
              background: 'linear-gradient(135deg, #477BFF 0%, #2563EB 100%)'
            }}
          >
            {forgotLoading ? <CircularProgress size={18} color="inherit" /> : 'Send Reset Code'}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default Login;
