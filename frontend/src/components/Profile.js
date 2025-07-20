import React, { useEffect, useState } from 'react';
import { Box, Typography, TextField, Button, Grid, Card, CardContent, CardMedia, Stack, Alert, Avatar, Paper } from '@mui/material';
import axios from '../axiosConfig';
import { useNavigate } from 'react-router-dom';

export default function Profile() {
  const navigate = useNavigate();
  const [profile, setProfile] = useState(null);
  const [listings, setListings] = useState([]);
  const [edit, setEdit] = useState(false);
  const [form, setForm] = useState({ name: '', phone: '' });
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchProfile = async () => {
      try {
        const res = await axios.get('/api/user/profile');
        setProfile(res.data);
        setForm({ name: res.data.name || '', phone: res.data.phone || '' });
      } catch (err) {
        setError('Failed to load profile.');
      }
      setLoading(false);
    };
    fetchProfile();
  }, []);

  useEffect(() => {
    if (profile) {
      axios.get('/api/listings').then(res => {
        setListings((res.data.listings || []).filter(l => l.owner.id === profile.id));
      });
    }
  }, [profile]);

  const handleChange = e => setForm({ ...form, [e.target.name]: e.target.value });
  const handleSave = async () => {
    try {
      await axios.put('/api/user/profile', form);
      setSuccess('Profile updated!');
      setEdit(false);
      setProfile({ ...profile, ...form });
    } catch {
      setError('Failed to update profile.');
    }
  };

  if (loading) return <Typography>Loading...</Typography>;

  return (
    <Box>
      <Typography variant="h4" mb={3}>Profile</Typography>
      {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}
      {success && <Alert severity="success" sx={{ mb: 2 }}>{success}</Alert>}
      <Paper sx={{ p: 3, mb: 4, display: 'flex', alignItems: 'center', gap: 3, maxWidth: 600 }}>
        <Avatar sx={{ width: 72, height: 72, mr: 3 }}>{profile?.name?.[0] || '?'}</Avatar>
        <Box sx={{ flex: 1 }}>
          <Stack spacing={2} direction={{ xs: 'column', sm: 'row' }} alignItems="center">
            <TextField label="Name" name="name" value={form.name} onChange={handleChange} disabled={!edit} sx={{ mr: 2, flex: 1 }} />
            <TextField label="Phone" name="phone" value={form.phone} onChange={handleChange} disabled={!edit} sx={{ mr: 2, flex: 1 }} />
            <TextField label="Email" value={profile?.email || ''} disabled sx={{ mr: 2, flex: 1 }} />
            <Button variant={edit ? 'contained' : 'outlined'} onClick={() => edit ? handleSave() : setEdit(true)}>{edit ? 'Save' : 'Edit'}</Button>
          </Stack>
        </Box>
      </Paper>
      <Typography variant="h6" mb={2}>My Listings</Typography>
      <Grid container spacing={3}>
        {listings.length === 0 && <Grid item xs={12}><Typography color="text.secondary">No listings found.</Typography></Grid>}
        {listings.map(listing => (
          <Grid item xs={12} sm={6} md={4} key={listing.id}>
            <Card
              sx={{ cursor: 'pointer', transition: 'box-shadow 0.2s', '&:hover': { boxShadow: 6 } }}
              onClick={() => navigate(`/listings/${listing.id}`)}
            >
              <CardMedia component="img" height="140" image={listing.primary_image} alt={listing.title} />
              <CardContent>
                <Typography variant="h6">{listing.title}</Typography>
                <Typography variant="body2">{listing.city}, {listing.state}</Typography>
                <Typography variant="body2">${listing.price.toLocaleString()}</Typography>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>
    </Box>
  );
} 