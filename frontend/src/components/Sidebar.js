import React from 'react';
import {
  Drawer,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  ListItemButton,
  Box,
  Typography,
  Avatar,
  Divider,
  IconButton,
  Chip
} from '@mui/material';
import {
  Home,
  Search,
  Favorite,
  Message,
  Person,
  Settings,
  Logout,
  Menu
} from '@mui/icons-material';
import { useAuth } from '../contexts/AuthContext';
import { useNavigate, useLocation } from 'react-router-dom';

const Sidebar = ({ open, onClose, variant = 'permanent' }) => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  const menuItems = [
    { text: 'Properties', icon: <Home />, path: '/listings' },
    { text: 'Search', icon: <Search />, path: '/search' },
    { text: 'Favorites', icon: <Favorite />, path: '/favorites' },
    { text: 'Messages', icon: <Message />, path: '/messages' },
    { text: 'Profile', icon: <Person />, path: '/profile' },
    { text: 'Settings', icon: <Settings />, path: '/settings' }
  ];

  const handleNavigation = (path) => {
    navigate(path);
    if (variant === 'temporary') {
      onClose();
    }
  };

  const handleLogout = () => {
    logout();
    navigate('/');
  };

  const getUserTypeLabel = (type) => {
    switch (type) {
      case 'buyer': return 'Buyer';
      case 'seller': return 'Seller';
      case 'agent': return 'Agent';
      default: return 'User';
    }
  };

  const drawerContent = (
    <Box sx={{ width: 280, height: '100%', display: 'flex', flexDirection: 'column' }}>
      {/* Header */}
      <Box sx={{ p: 2, textAlign: 'center', borderBottom: 1, borderColor: 'divider' }}>
        <Avatar sx={{ width: 64, height: 64, mx: 'auto', mb: 1, bgcolor: 'primary.main' }}>
          <Person />
        </Avatar>
        <Typography variant="h6" noWrap>
          {user?.name || 'User'}
        </Typography>
        <Typography variant="body2" color="text.secondary" noWrap>
          {user?.email || 'user@example.com'}
        </Typography>
        <Chip 
          label={getUserTypeLabel(user?.user_type)} 
          size="small" 
          color="primary" 
          variant="outlined"
          sx={{ mt: 1 }}
        />
      </Box>

      {/* Menu Items */}
      <List sx={{ flex: 1, pt: 1 }}>
        {menuItems.map((item) => (
          <ListItem key={item.text} disablePadding>
            <ListItemButton
              selected={location.pathname === item.path}
              onClick={() => handleNavigation(item.path)}
              sx={{
                mx: 1,
                borderRadius: 1,
                '&.Mui-selected': {
                  backgroundColor: 'primary.main',
                  color: 'white',
                  '&:hover': {
                    backgroundColor: 'primary.dark',
                  },
                  '& .MuiListItemIcon-root': {
                    color: 'white',
                  },
                },
              }}
            >
              <ListItemIcon sx={{ minWidth: 40 }}>
                {item.icon}
              </ListItemIcon>
              <ListItemText primary={item.text} />
            </ListItemButton>
          </ListItem>
        ))}
      </List>

      {/* Logout */}
      <Divider />
      <List>
        <ListItem disablePadding>
          <ListItemButton onClick={handleLogout} sx={{ mx: 1, borderRadius: 1 }}>
            <ListItemIcon sx={{ minWidth: 40 }}>
              <Logout />
            </ListItemIcon>
            <ListItemText primary="Logout" />
          </ListItemButton>
        </ListItem>
      </List>
    </Box>
  );

  if (variant === 'temporary') {
    return (
      <Drawer
        variant="temporary"
        open={open}
        onClose={onClose}
        ModalProps={{
          keepMounted: true, // Better open performance on mobile.
        }}
        sx={{
          display: { xs: 'block', sm: 'none' },
          '& .MuiDrawer-paper': { boxSizing: 'border-box', width: 280 },
        }}
      >
        {drawerContent}
      </Drawer>
    );
  }

  return (
    <Drawer
      variant="permanent"
      sx={{
        display: { xs: 'none', sm: 'block' },
        '& .MuiDrawer-paper': { boxSizing: 'border-box', width: 280 },
      }}
      open
    >
      {drawerContent}
    </Drawer>
  );
};

export default Sidebar; 