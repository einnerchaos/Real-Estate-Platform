import React, { useState, useEffect } from 'react';
import { Box, Typography, Grid, Card, CardContent, CardMedia, TextField, MenuItem, Button, Chip, Stack } from '@mui/material';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';

const propertyTypes = [
  'house', 'apartment', 'condo', 'land'
];

export default function Search() {
  const [filters, setFilters] = useState({ city: '', property_type: '', min_price: '', max_price: '', bedrooms: '' });
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const fetchResults = async () => {
    setLoading(true);
    const params = {};
    if (filters.city) params.city = filters.city;
    if (filters.property_type) params.property_type = filters.property_type;
    if (filters.min_price) params.min_price = filters.min_price;
    if (filters.max_price) params.max_price = filters.max_price;
    if (filters.bedrooms) params.bedrooms = filters.bedrooms;
    const res = await axios.get('/api/listings', { params });
    setResults(res.data.listings || []);
    setLoading(false);
  };

  useEffect(() => { fetchResults(); }, []);

  const handleChange = e => setFilters({ ...filters, [e.target.name]: e.target.value });
  const handleSearch = e => { e.preventDefault(); fetchResults(); };
  const handleClear = () => { setFilters({ city: '', property_type: '', min_price: '', max_price: '', bedrooms: '' }); fetchResults(); };

  return (
    <Box>
      <Typography variant="h4" mb={3}>Find Your Dream Property</Typography>
      <Box component="form" onSubmit={handleSearch} sx={{ display: 'flex', gap: 2, mb: 4 }}>
        <TextField label="City" name="city" value={filters.city} onChange={handleChange} />
        <TextField select label="Property Type" name="property_type" value={filters.property_type} onChange={handleChange} sx={{ minWidth: 140 }}>
          <MenuItem value="">All</MenuItem>
          {propertyTypes.map(type => <MenuItem key={type} value={type}>{type.charAt(0).toUpperCase() + type.slice(1)}</MenuItem>)}
        </TextField>
        <TextField label="Min Price" name="min_price" type="number" value={filters.min_price} onChange={handleChange} />
        <TextField label="Max Price" name="max_price" type="number" value={filters.max_price} onChange={handleChange} />
        <TextField label="Bedrooms" name="bedrooms" type="number" value={filters.bedrooms} onChange={handleChange} />
        <Button type="submit" variant="contained">Search</Button>
        <Button onClick={handleClear} variant="outlined">Clear</Button>
      </Box>
      <Typography variant="h6" mb={2}>{results.length} properties found</Typography>
      <Grid container spacing={3}>
        {results.map((listing) => (
          <Grid item xs={12} sm={6} md={4} key={listing.id}>
            <Card
              sx={{ cursor: 'pointer', transition: 'box-shadow 0.2s', '&:hover': { boxShadow: 6 } }}
              onClick={() => navigate(`/listings/${listing.id}`)}
            >
              <CardMedia component="img" height="180" image={listing.primary_image} alt={listing.title} />
              <CardContent>
                <Typography variant="h6" gutterBottom>{listing.title}</Typography>
                <Typography variant="body2" color="text.secondary" gutterBottom>{listing.city}, {listing.state}</Typography>
                <Stack direction="row" spacing={1} mb={1}>
                  <Chip label={listing.property_type} size="small" />
                  <Chip label={listing.status} size="small" color="success" />
                </Stack>
                <Typography variant="body2">{listing.bedrooms} beds • {listing.bathrooms} baths • {listing.square_feet} sq ft</Typography>
                <Typography variant="h6" color="primary" mt={1}>${listing.price.toLocaleString()}</Typography>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>
    </Box>
  );
} 