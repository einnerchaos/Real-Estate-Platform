import React, { useState } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import { CssBaseline, Box, AppBar, Toolbar, Typography, IconButton } from '@mui/material';
import { Menu } from '@mui/icons-material';
import { AuthProvider, useAuth } from './contexts/AuthContext';
import Login from './components/Login';
import PropertyList from './components/PropertyList';
import Sidebar from './components/Sidebar';
import PrivateRoute from './components/PrivateRoute';
import Search from './components/Search';
import Favorites from './components/Favorites';
import Messages from './components/Messages';
import Profile from './components/Profile';
import Settings from './components/Settings';
import Properties from './components/Properties';
import PropertyDetail from './components/PropertyDetail';

const theme = createTheme({
  palette: {
    primary: {
      main: '#2563eb', // soft blue
      contrastText: '#fff',
    },
    secondary: {
      main: '#d32f2f', // red
      contrastText: '#fff',
    },
    accent: {
      main: '#ffb300', // gold
    },
    background: {
      default: '#f5f6fa', // very light gray
      paper: '#fff',
    },
    text: {
      primary: '#232323',
      secondary: '#5a5a5a',
    },
    divider: '#e0e0e0',
  },
  typography: {
    fontFamily: 'Inter, Roboto, Helvetica, Arial, sans-serif',
    h4: {
      fontWeight: 800,
      letterSpacing: '-1px',
      fontSize: '2.2rem',
      marginBottom: '0.5em',
    },
    h6: {
      fontWeight: 700,
      fontSize: '1.1rem',
    },
    button: {
      fontWeight: 700,
      letterSpacing: '0.5px',
    },
  },
  components: {
    MuiCard: {
      styleOverrides: {
        root: {
          borderRadius: 16,
          boxShadow: '0 4px 16px rgba(37,99,235,0.07)',
          border: '1px solid #ececec',
          background: '#fff',
        },
      },
    },
    MuiPaper: {
      styleOverrides: {
        root: {
          borderRadius: 16,
          background: '#fff',
        },
      },
    },
    MuiButton: {
      styleOverrides: {
        root: {
          borderRadius: 8,
          textTransform: 'none',
          fontWeight: 700,
          boxShadow: 'none',
          padding: '10px 24px',
        },
        containedPrimary: {
          background: '#2563eb',
        },
        outlined: {
          borderColor: '#2563eb',
        },
      },
    },
    MuiAppBar: {
      styleOverrides: {
        root: {
          background: '#fff',
          color: '#21243b',
          boxShadow: '0 2px 8px rgba(37,99,235,0.06)',
        },
      },
    },
    MuiAvatar: {
      styleOverrides: {
        root: {
          background: '#ffb300',
          color: '#21243b',
          fontWeight: 800,
        },
      },
    },
    MuiChip: {
      styleOverrides: {
        root: {
          borderRadius: 8,
          fontWeight: 700,
          background: '#f5f6fa',
          color: '#21243b',
        },
      },
    },
    MuiTextField: {
      styleOverrides: {
        root: {
          borderRadius: 8,
          background: '#fff',
        },
      },
    },
    MuiDrawer: {
      styleOverrides: {
        paper: {
          background: '#f5f6fa',
          color: '#21243b',
          borderRight: '1px solid #ececec',
        },
      },
    },
    MuiListItemButton: {
      styleOverrides: {
        root: {
          borderRadius: 8,
          margin: '4px 0',
          '&.Mui-selected': {
            background: '#e3edfa',
            color: '#2563eb',
            fontWeight: 800,
            borderBottom: 'none',
          },
        },
      },
    },
  },
});

const AppContent = () => {
  const [mobileOpen, setMobileOpen] = useState(false);
  const { user } = useAuth();

  const handleDrawerToggle = () => {
    setMobileOpen(!mobileOpen);
  };

  if (!user) {
    return <Login />;
  }

  return (
    <Box sx={{ display: 'flex' }}>
      {/* Mobile App Bar */}
      <AppBar
        position="fixed"
        sx={{
          width: { sm: `calc(100% - 280px)` },
          ml: { sm: `280px` },
          display: { xs: 'block', sm: 'none' },
        }}
      >
        <Toolbar>
          <IconButton
            color="inherit"
            aria-label="open drawer"
            edge="start"
            onClick={handleDrawerToggle}
            sx={{ mr: 2, display: { sm: 'none' } }}
          >
            <Menu />
          </IconButton>
          <Typography variant="h6" noWrap component="div">
            Real Estate Platform
          </Typography>
        </Toolbar>
      </AppBar>

      {/* Sidebar */}
      <Sidebar
        variant="permanent"
        sx={{ display: { xs: 'none', sm: 'block' } }}
      />
      <Sidebar
        variant="temporary"
        open={mobileOpen}
        onClose={handleDrawerToggle}
      />

      {/* Main Content */}
      <Box
        component="main"
        sx={{
          flexGrow: 1,
          p: 3,
          width: { sm: `calc(100% - 280px)` },
          mt: { xs: 8, sm: 0 },
          ml: { sm: '280px' }, // Add left margin for sidebar
        }}
      >
        <Routes>
          <Route path="/listings/:id" element={<PropertyDetail />} />
          <Route path="/listings" element={<Properties />} />
          <Route path="/search" element={<Search />} />
          <Route path="/favorites" element={<Favorites />} />
          <Route path="/messages" element={<Messages />} />
          <Route path="/profile" element={<Profile />} />
          <Route path="/settings" element={<Settings />} />
          <Route path="/" element={<Navigate to="/listings" replace />} />
          <Route path="*" element={<Navigate to="/listings" replace />} />
        </Routes>
      </Box>
    </Box>
  );
};

const App = () => {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <AuthProvider>
        <Router>
          <AppContent />
        </Router>
      </AuthProvider>
    </ThemeProvider>
  );
};

export default App; 