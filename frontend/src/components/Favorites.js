import React, { useEffect, useState } from 'react';
import { Box, Typography, Grid, Card, CardContent, CardMedia, IconButton, Stack, Alert } from '@mui/material';
import DeleteIcon from '@mui/icons-material/Delete';
import axios from '../axiosConfig';
import { useNavigate } from 'react-router-dom';

export default function Favorites() {
  const [favorites, setFavorites] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const navigate = useNavigate();

  const fetchFavorites = async () => {
    setLoading(true);
    setError('');
    try {
      const res = await axios.get('/api/favorites');
      setFavorites(res.data || []);
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to load favorites.');
    }
    setLoading(false);
  };

  useEffect(() => { fetchFavorites(); }, []);

  const handleRemove = async (id) => {
    try {
      await axios.delete(`/api/favorites/${id}`);
      fetchFavorites();
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to remove favorite.');
    }
  };

  return (
    <Box>
      <Typography variant="h4" mb={3}>Favorites</Typography>
      {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}
      <Grid container spacing={3}>
        {favorites.map((fav) => (
          <Grid item xs={12} sm={6} md={4} key={fav.id}>
            <Card
              sx={{ cursor: 'pointer', transition: 'box-shadow 0.2s', '&:hover': { boxShadow: 6 } }}
              onClick={() => navigate(`/listings/${fav.listing.id}`)}
            >
              <CardMedia component="img" height="180" image={fav.listing.primary_image} alt={fav.listing.title} />
              <CardContent>
                <Typography variant="h6" gutterBottom>{fav.listing.title}</Typography>
                <Typography variant="body2" color="text.secondary" gutterBottom>{fav.listing.city}</Typography>
                <Stack direction="row" spacing={1} mb={1}>
                  <Typography variant="body2">{fav.listing.property_type}</Typography>
                  <Typography variant="body2">${fav.listing.price.toLocaleString()}</Typography>
                </Stack>
                <IconButton color="error" onClick={() => handleRemove(fav.listing.id)}><DeleteIcon /></IconButton>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>
    </Box>
  );
} 