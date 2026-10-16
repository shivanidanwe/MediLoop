import React from 'react';
import { BrowserRouter } from 'react-router-dom';
import { ThemeProvider, createTheme, CssBaseline } from '@mui/material';
import { AuthProvider } from './context/AuthContext';
import { MockDataProvider } from './context/MockDataContext';
import AppRoutes from './routes/AppRoutes';

// Custom modern Material Design 3 theme config
const theme = createTheme({
  palette: {
    primary: {
      main: '#10b981', // Medical Green
      lightBg: 'rgba(16, 185, 129, 0.08)',
      lightBorder: 'rgba(16, 185, 129, 0.2)',
      contrastText: '#ffffff'
    },
    secondary: {
      main: '#3b82f6', // Accent Blue
      lightBg: 'rgba(59, 130, 246, 0.08)',
      contrastText: '#ffffff'
    },
    success: {
      main: '#10b981',
      lightBg: 'rgba(16, 185, 129, 0.08)',
      lightBorder: 'rgba(16, 185, 129, 0.2)'
    },
    warning: {
      main: '#f59e0b',
      lightBg: 'rgba(245, 158, 11, 0.08)',
      lightBorder: 'rgba(245, 158, 11, 0.2)'
    },
    error: {
      main: '#ef4444',
      lightBg: 'rgba(239, 68, 68, 0.08)',
      lighterBg: 'rgba(239, 68, 68, 0.04)',
      lightBorder: 'rgba(239, 68, 68, 0.2)'
    },
    info: {
      main: '#3b82f6',
      lightBg: 'rgba(59, 130, 246, 0.08)',
      lightBorder: 'rgba(59, 130, 246, 0.2)'
    },
    background: {
      default: '#f9fafb',
      paper: '#ffffff'
    },
    text: {
      primary: '#0f172a',
      secondary: '#475569'
    },
    divider: '#f1f5f9'
  },
  typography: {
    fontFamily: `'Outfit', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif`,
    h1: { fontWeight: 800 },
    h2: { fontWeight: 800 },
    h3: { fontWeight: 800 },
    h4: { fontWeight: 800 },
    h5: { fontWeight: 700 },
    h6: { fontWeight: 700 },
    subtitle1: { fontWeight: 600 },
    subtitle2: { fontWeight: 600 },
    body1: { fontSize: '0.95rem', lineHeight: 1.6 },
    body2: { fontSize: '0.875rem', lineHeight: 1.6 },
    button: { textTransform: 'none', fontWeight: 600 }
  },
  shape: {
    borderRadius: 16
  },
  components: {
    MuiButton: {
      styleOverrides: {
        root: {
          borderRadius: 12,
          padding: '8px 18px',
          boxShadow: 'none',
          '&:hover': {
            boxShadow: 'none'
          }
        },
        containedPrimary: {
          '&:hover': {
            backgroundColor: '#059669'
          }
        }
      }
    },
    MuiCard: {
      styleOverrides: {
        root: {
          borderRadius: 16,
          boxShadow: '0px 4px 20px rgba(0, 0, 0, 0.02)',
          border: '1px solid #f1f5f9'
        }
      }
    },
    MuiPaper: {
      styleOverrides: {
        root: {
          borderRadius: 16
        }
      }
    },
    MuiOutlinedInput: {
      styleOverrides: {
        root: {
          borderRadius: 12,
          '&.Mui-focused .MuiOutlinedInput-notchedOutline': {
            borderWidth: '1.5px'
          }
        }
      }
    }
  }
});

const App = () => {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <BrowserRouter>
        <MockDataProvider>
          <AuthProvider>
            <AppRoutes />
          </AuthProvider>
        </MockDataProvider>
      </BrowserRouter>
    </ThemeProvider>
  );
};

export default App;
