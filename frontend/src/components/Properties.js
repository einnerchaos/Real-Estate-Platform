import React, { useEffect, useState } from 'react';
import { Box, Typography, Grid, Card, CardContent, Chip, Stack, Paper, Button, MenuItem, Select } from '@mui/material';
import axios from '../axiosConfig';
import { MapContainer, TileLayer, Marker, Popup } from 'react-leaflet';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import markerIcon2x from 'leaflet/dist/images/marker-icon-2x.png';
import markerIcon from 'leaflet/dist/images/marker-icon.png';
import markerShadow from 'leaflet/dist/images/marker-shadow.png';
import { useNavigate } from 'react-router-dom';

// Fix default marker icon
L.Icon.Default.mergeOptions({
  iconRetinaUrl: markerIcon2x,
  iconUrl: markerIcon,
  shadowUrl: markerShadow,
});

export default function Properties() {
  const [listings, setListings] = useState([]);
  const [stats, setStats] = useState({ total: 0, byType: {}, avgPrice: {} });
  const [city, setCity] = useState('');
  const navigate = useNavigate();

  useEffect(() => {
    axios.get('/api/listings').then(res => {
      const items = res.data.listings || [];
      setListings(items);
      // Stats
      const byType = {};
      const priceByCity = {};
      const countByCity = {};
      items.forEach(l => {
        byType[l.property_type] = (byType[l.property_type] || 0) + 1;
        priceByCity[l.city] = (priceByCity[l.city] || 0) + l.price;
        countByCity[l.city] = (countByCity[l.city] || 0) + 1;
      });
      const avgPrice = {};
      Object.keys(priceByCity).forEach(city => {
        avgPrice[city] = priceByCity[city] / countByCity[city];
      });
      setStats({
        total: items.length,
        byType,
        avgPrice
      });
    });
  }, []);

  // Filtered listings by city
  const filteredListings = city ? listings.filter(l => l.city === city) : listings;
  const cities = Array.from(new Set(listings.map(l => l.city)));

  // Map center
  const center = filteredListings.length ? [filteredListings[0].latitude, filteredListings[0].longitude] : [51.1657, 10.4515]; // Germany center

  // Newest, most expensive, least expensive
  const newest = [...listings].sort((a, b) => new Date(b.created_at) - new Date(a.created_at))[0];
  const mostExpensive = [...listings].sort((a, b) => b.price - a.price)[0];
  const leastExpensive = [...listings].sort((a, b) => a.price - b.price)[0];

  return (
    <Box>
      <Typography variant="h4" mb={3}>Properties Overview</Typography>
      <Grid container spacing={3} mb={3}>
        <Grid item xs={12} sm={6} md={3}>
          <Card onClick={() => navigate(`/listings/${newest?.id}`)} sx={{ mb: 2, cursor: 'pointer' }}>
            <CardContent>
              <Typography variant="h6">Total Properties</Typography>
              <Typography variant="h4">{stats.total}</Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card onClick={() => navigate(`/listings/${mostExpensive?.id}`)} sx={{ mb: 2, cursor: 'pointer' }}>
            <CardContent>
              <Typography variant="h6">By Type</Typography>
              <Stack direction="row" spacing={1} flexWrap="wrap">
                {Object.entries(stats.byType).map(([type, count]) => (
                  <Chip key={type} label={`${type}: ${count}`} />
                ))}
              </Stack>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={12} md={6}>
          <Card onClick={() => navigate(`/listings/${leastExpensive?.id}`)} sx={{ mb: 2, cursor: 'pointer' }}>
            <CardContent>
              <Typography variant="h6">Average Price by City</Typography>
              <Stack direction="row" spacing={2} flexWrap="wrap">
                {Object.entries(stats.avgPrice).map(([city, price]) => (
                  <Chip key={city} label={`${city}: $${Math.round(price).toLocaleString()}`} />
                ))}
              </Stack>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
      <Grid container spacing={3} mb={3}>
        <Grid item xs={12} md={4}>
          <Card onClick={() => navigate(`/listings/${newest?.id}`)} sx={{ mb: 2, cursor: 'pointer' }}>
            <CardContent>
              <Typography variant="subtitle2" color="text.secondary">Newest Listing</Typography>
              {newest && (
                <Stack spacing={1}>
                  <img src={newest.primary_image} alt={newest.title} style={{ width: '100%', borderRadius: 8 }} />
                  <Typography variant="h6">{newest.title}</Typography>
                  <Typography>${newest.price?.toLocaleString()}</Typography>
                  <Typography color="text.secondary">{newest.city}, {newest.state}</Typography>
                </Stack>
              )}
            </CardContent>
          </Card>
          <Card onClick={() => navigate(`/listings/${mostExpensive?.id}`)} sx={{ mb: 2, cursor: 'pointer' }}>
            <CardContent>
              <Typography variant="subtitle2" color="text.secondary">Most Expensive</Typography>
              {mostExpensive && (
                <Stack spacing={1}>
                  <img src={mostExpensive.primary_image} alt={mostExpensive.title} style={{ width: '100%', borderRadius: 8 }} />
                  <Typography variant="h6">{mostExpensive.title}</Typography>
                  <Typography>${mostExpensive.price?.toLocaleString()}</Typography>
                  <Typography color="text.secondary">{mostExpensive.city}, {mostExpensive.state}</Typography>
                </Stack>
              )}
            </CardContent>
          </Card>
          <Card onClick={() => navigate(`/listings/${leastExpensive?.id}`)} sx={{ mb: 2, cursor: 'pointer' }}>
            <CardContent>
              <Typography variant="subtitle2" color="text.secondary">Least Expensive</Typography>
              {leastExpensive && (
                <Stack spacing={1}>
                  <img src={leastExpensive.primary_image} alt={leastExpensive.title} style={{ width: '100%', borderRadius: 8 }} />
                  <Typography variant="h6">{leastExpensive.title}</Typography>
                  <Typography>${leastExpensive.price?.toLocaleString()}</Typography>
                  <Typography color="text.secondary">{leastExpensive.city}, {leastExpensive.state}</Typography>
                </Stack>
              )}
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={8}>
          <Paper sx={{ height: 500, mb: 3, p: 2 }}>
            <Box sx={{ mb: 2, display: 'flex', alignItems: 'center', gap: 2 }}>
              <Typography>Filter by City:</Typography>
              <Select value={city} onChange={e => setCity(e.target.value)} displayEmpty size="small">
                <MenuItem value="">All</MenuItem>
                {cities.map(c => <MenuItem key={c} value={c}>{c}</MenuItem>)}
              </Select>
            </Box>
            <MapContainer center={center} zoom={5} style={{ height: '100%', width: '100%' }}>
              <TileLayer url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" />
              {filteredListings.map(l => (
                <Marker key={l.id} position={[l.latitude, l.longitude]}>
                  <Popup>
                    <Stack spacing={1}>
                      <img src={l.primary_image} alt={l.title} style={{ width: 180, borderRadius: 8 }} />
                      <Typography variant="subtitle1">{l.title}</Typography>
                      <Typography variant="body2">${l.price.toLocaleString()}</Typography>
                      <Typography variant="body2">{l.city}, {l.state}</Typography>
                      <Button variant="outlined" size="small" onClick={() => navigate(`/listings/${l.id}`)}>View Details</Button>
                    </Stack>
                  </Popup>
                </Marker>
              ))}
            </MapContainer>
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
} 