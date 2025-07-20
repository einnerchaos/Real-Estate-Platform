import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import axios from '../axiosConfig';
import { Box, Typography, Grid, Paper, Chip, Avatar, Button, CircularProgress, Stack } from '@mui/material';

export default function PropertyDetail() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [property, setProperty] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [imgIdx, setImgIdx] = useState(0);

  useEffect(() => {
    const fetchProperty = async () => {
      try {
        const res = await axios.get(`/api/listings/${id}`);
        setProperty(res.data);
      } catch (err) {
        setError('Failed to load property.');
      }
      setLoading(false);
    };
    fetchProperty();
  }, [id]);

  if (loading) return <Box sx={{ textAlign: 'center', mt: 8 }}><CircularProgress /></Box>;
  if (error) return <Typography color="error">{error}</Typography>;
  if (!property) return null;

  return (
    <Box sx={{ maxWidth: 1100, mx: 'auto', mt: 5, mb: 5 }}>
      <Button variant="outlined" sx={{ mb: 2 }} onClick={() => navigate(-1)}>Back</Button>
      <Paper elevation={3} sx={{ p: 4, borderRadius: 3 }}>
        <Grid container spacing={4}>
          <Grid item xs={12} md={6}>
            {/* Image carousel */}
            <Box sx={{ position: 'relative', mb: 2 }}>
              {property.images && property.images.length > 0 && (
                <img
                  src={property.images[imgIdx].image_url}
                  alt={property.title}
                  style={{ width: '100%', height: 340, objectFit: 'cover', borderRadius: 12 }}
                />
              )}
              <Box sx={{ display: 'flex', justifyContent: 'center', mt: 1 }}>
                {property.images && property.images.map((img, idx) => (
                  <Box
                    key={img.id}
                    onClick={() => setImgIdx(idx)}
                    sx={{
                      width: 48, height: 48, borderRadius: 2, overflow: 'hidden', mx: 0.5, cursor: 'pointer',
                      border: imgIdx === idx ? '2px solid #1976d2' : '2px solid transparent',
                      boxShadow: imgIdx === idx ? 2 : 0
                    }}
                  >
                    <img src={img.image_url} alt={property.title} style={{ width: '100%', height: '100%', objectFit: 'cover' }} />
                  </Box>
                ))}
              </Box>
            </Box>
          </Grid>
          <Grid item xs={12} md={6}>
            <Typography variant="h4" gutterBottom>{property.title}</Typography>
            <Typography variant="h6" color="primary" gutterBottom>
              €{property.price.toLocaleString()} &nbsp;
              <Chip label={property.property_type} size="small" color="primary" />
            </Typography>
            <Typography variant="body1" sx={{ mb: 2 }}>{property.description}</Typography>
            <Stack direction="row" spacing={2} sx={{ mb: 2 }}>
              <Chip label={`${property.bedrooms} Zimmer`} />
              <Chip label={`${property.bathrooms} Bad`} />
              <Chip label={`${property.square_feet} m²`} />
              <Chip label={property.status} color={property.status === 'active' ? 'success' : 'default'} />
            </Stack>
            <Typography variant="subtitle1" sx={{ mb: 1 }}>
              Adresse: {property.address}, {property.zip_code} {property.city}, {property.state}
            </Typography>
            <Typography variant="subtitle2" color="text.secondary" sx={{ mb: 2 }}>
              Erstellt am: {new Date(property.created_at).toLocaleDateString()}
            </Typography>
            <Box sx={{ mb: 2 }}>
              <Typography variant="h6" sx={{ mb: 1 }}>Ausstattung & Merkmale</Typography>
              <Grid container spacing={1}>
                {property.features && property.features.map((f, idx) => (
                  <Grid item xs={6} sm={4} key={idx}>
                    <Chip label={`${f.name}: ${f.value}`} variant="outlined" />
                  </Grid>
                ))}
              </Grid>
            </Box>
            <Box sx={{ mt: 3 }}>
              <Typography variant="subtitle1" sx={{ mb: 1 }}>Anbieter</Typography>
              <Stack direction="row" spacing={2} alignItems="center">
                <Avatar>{property.owner.name[0]}</Avatar>
                <Box>
                  <Typography>{property.owner.name}</Typography>
                  <Typography color="text.secondary" variant="body2">{property.owner.email}</Typography>
                  <Typography color="text.secondary" variant="body2">{property.owner.phone}</Typography>
                </Box>
              </Stack>
            </Box>
          </Grid>
        </Grid>
      </Paper>
    </Box>
  );
} 