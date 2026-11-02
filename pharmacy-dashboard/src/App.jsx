import React from 'react';
import { BrowserRouter } from 'react-router-dom';
import { ThemeProvider, createTheme, CssBaseline } from '@mui/material';
import { AuthProvider } from './context/AuthContext';
import { MockDataProvider } from './context/MockDataContext';
import AppRoutes from './routes/AppRoutes';

// MediLoop Next-Generation Liquid Glass SaaS Theme
const theme = createTheme({
  palette: {
    primary: {
      main: '#477BFF', // Royal Blue
      light: '#27D8E8', // Electric Cyan
      dark: '#102A56', // Deep Blue
      lightBg: 'rgba(71, 123, 255, 0.08)',
      lightBorder: 'rgba(71, 123, 255, 0.25)',
      contrastText: '#ffffff'
    },
    secondary: {
      main: '#8865F7', // Violet
      light: '#B99CFF', // Lavender
      lightBg: 'rgba(136, 101, 247, 0.08)',
      contrastText: '#ffffff'
    },
    success: {
      main: '#10b981', // Emerald Mint
      lightBg: 'rgba(16, 185, 129, 0.08)',
      lightBorder: 'rgba(16, 185, 129, 0.25)'
    },
    warning: {
      main: '#f59e0b', // Warm Amber
      lightBg: 'rgba(245, 158, 11, 0.08)',
      lightBorder: 'rgba(245, 158, 11, 0.25)'
    },
    error: {
      main: '#FF8C83', // Coral
      lightBg: 'rgba(255, 140, 131, 0.1)',
      lighterBg: 'rgba(255, 140, 131, 0.05)',
      lightBorder: 'rgba(255, 140, 131, 0.25)'
    },
    info: {
      main: '#27D8E8', // Electric Cyan
      lightBg: 'rgba(39, 216, 232, 0.08)',
      lightBorder: 'rgba(39, 216, 232, 0.25)'
    },
    background: {
      default: '#F7F9FF', // Cloud White
      paper: '#ffffff',
      darkNavy: '#07152F'
    },
    text: {
      primary: '#07152F', // Midnight Navy
      secondary: '#64748B' // Slate Gray
    },
    divider: '#E2E8F0'
  },
  typography: {
    fontFamily: `'Outfit', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif`,
    h1: { fontWeight: 800, letterSpacing: '-0.8px' },
    h2: { fontWeight: 800, letterSpacing: '-0.6px' },
    h3: { fontWeight: 800, letterSpacing: '-0.5px' },
    h4: { fontWeight: 800, letterSpacing: '-0.4px' },
    h5: { fontWeight: 700, letterSpacing: '-0.3px' },
    h6: { fontWeight: 700, letterSpacing: '-0.2px' },
    subtitle1: { fontWeight: 700 },
    subtitle2: { fontWeight: 600 },
    body1: { fontSize: '0.94rem', lineHeight: 1.6 },
    body2: { fontSize: '0.86rem', lineHeight: 1.6 },
    button: { textTransform: 'none', fontWeight: 700, letterSpacing: '0.1px' }
  },
  shape: {
    borderRadius: 18
  },
  components: {
    MuiButton: {
      styleOverrides: {
        root: {
          borderRadius: 12,
          padding: '7px 18px',
          boxShadow: 'none',
          textTransform: 'none',
          fontWeight: 700,
          transition: 'all 0.2s ease',
          '&:hover': {
            boxShadow: '0 4px 14px rgba(71, 123, 255, 0.2)',
            transform: 'translateY(-1px)'
          }
        },
        containedPrimary: {
          background: 'linear-gradient(135deg, #477BFF 0%, #2563EB 100%)',
          color: '#ffffff',
          '&:hover': {
            background: 'linear-gradient(135deg, #3B82F6 0%, #1D4ED8 100%)'
          }
        }
      }
    },
    MuiCard: {
      styleOverrides: {
        root: {
          borderRadius: 20,
          boxShadow: '0 4px 20px rgba(7, 21, 47, 0.03)',
          border: '1px solid #E2E8F0',
          transition: 'all 0.2s ease'
        }
      }
    },
    MuiPaper: {
      styleOverrides: {
        root: {
          borderRadius: 20
        }
      }
    },
    MuiChip: {
      styleOverrides: {
        root: {
          borderRadius: 10,
          fontWeight: 700
        }
      }
    },
    MuiOutlinedInput: {
      styleOverrides: {
        root: {
          borderRadius: 14,
          backgroundColor: '#ffffff',
          '&.Mui-focused .MuiOutlinedInput-notchedOutline': {
            borderColor: '#477BFF',
            borderWidth: '2px'
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
