import React, { useState, useEffect } from 'react';
import {
  Container,
  Grid,
  Card,
  CardContent,
  CardMedia,
  Typography,
  Box,
  Chip,
  Button,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Slider,
  IconButton,
  Pagination,
  LinearProgress
} from '@mui/material';
import {
  LocationOn,
  Bed,
  Bathtub,
  SquareFoot,
  Favorite,
  FavoriteBorder,
  Search,
  FilterList
} from '@mui/icons-material';
import axios from 'axios';
import { useAuth } from '../contexts/AuthContext';
import { useNavigate } from 'react-router-dom';

const PropertyList = () => {
  const [listings, setListings] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filters, setFilters] = useState({
    property_type: '',
    min_price: '',
    max_price: '',
    bedrooms: '',
    city: ''
  });
  const [pagination, setPagination] = useState({
    current_page: 1,
    total: 0,
    pages: 0
  });
  const { user } = useAuth();
  const navigate = useNavigate();

  useEffect(() => {
    fetchListings();
  }, [pagination.current_page, filters]);

  const fetchListings = async () => {
    try {
      setLoading(true);
      const params = {
        page: pagination.current_page,
        per_page: 12,
        ...filters
      };
      
      const response = await axios.get('/api/listings', { params });
      setListings(response.data.listings);
      setPagination({
        current_page: response.data.current_page,
        total: response.data.total,
        pages: response.data.pages
      });
    } catch (error) {
      console.error('Error fetching listings:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleFilterChange = (field, value) => {
    setFilters(prev => ({
      ...prev,
      [field]: value
    }));
    setPagination(prev => ({ ...prev, current_page: 1 }));
  };

  const handlePageChange = (event, page) => {
    setPagination(prev => ({ ...prev, current_page: page }));
  };

  const toggleFavorite = async (listingId) => {
    try {
      const isFavorited = listings.find(l => l.id === listingId)?.is_favorited;
      
      if (isFavorited) {
        await axios.delete(`/api/favorites/${listingId}`);
      } else {
        await axios.post('/api/favorites', { listing_id: listingId });
      }
      
      // Update the listing's favorite status
      setListings(prev => prev.map(listing => 
        listing.id === listingId 
          ? { ...listing, is_favorited: !isFavorited }
          : listing
      ));
    } catch (error) {
      console.error('Error toggling favorite:', error);
    }
  };

  const formatPrice = (price) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(price);
  };

  if (loading) {
    return (
      <Container maxWidth="lg" sx={{ mt: 4 }}>
        <LinearProgress />
      </Container>
    );
  }

  return (
    <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
      {/* Search and Filters */}
      <Box className="search-container">
        <Typography variant="h5" gutterBottom>
          <Search sx={{ mr: 1, verticalAlign: 'middle' }} />
          Find Your Dream Property
        </Typography>
        
        <Grid container spacing={2} className="filters-grid">
          <Grid item xs={12} sm={6} md={3}>
            <TextField
              fullWidth
              label="City"
              value={filters.city}
              onChange={(e) => handleFilterChange('city', e.target.value)}
              placeholder="Enter city name"
            />
          </Grid>
          
          <Grid item xs={12} sm={6} md={2}>
            <FormControl fullWidth>
              <InputLabel>Property Type</InputLabel>
              <Select
                value={filters.property_type}
                onChange={(e) => handleFilterChange('property_type', e.target.value)}
                label="Property Type"
              >
                <MenuItem value="">All Types</MenuItem>
                <MenuItem value="house">House</MenuItem>
                <MenuItem value="apartment">Apartment</MenuItem>
                <MenuItem value="condo">Condo</MenuItem>
                <MenuItem value="land">Land</MenuItem>
              </Select>
            </FormControl>
          </Grid>
          
          <Grid item xs={12} sm={6} md={2}>
            <TextField
              fullWidth
              label="Min Price"
              type="number"
              value={filters.min_price}
              onChange={(e) => handleFilterChange('min_price', e.target.value)}
              placeholder="0"
            />
          </Grid>
          
          <Grid item xs={12} sm={6} md={2}>
            <TextField
              fullWidth
              label="Max Price"
              type="number"
              value={filters.max_price}
              onChange={(e) => handleFilterChange('max_price', e.target.value)}
              placeholder="1000000"
            />
          </Grid>
          
          <Grid item xs={12} sm={6} md={2}>
            <FormControl fullWidth>
              <InputLabel>Bedrooms</InputLabel>
              <Select
                value={filters.bedrooms}
                onChange={(e) => handleFilterChange('bedrooms', e.target.value)}
                label="Bedrooms"
              >
                <MenuItem value="">Any</MenuItem>
                <MenuItem value="1">1+</MenuItem>
                <MenuItem value="2">2+</MenuItem>
                <MenuItem value="3">3+</MenuItem>
                <MenuItem value="4">4+</MenuItem>
              </Select>
            </FormControl>
          </Grid>
          
          <Grid item xs={12} sm={6} md={1}>
            <Button
              fullWidth
              variant="outlined"
              onClick={() => setFilters({})}
              sx={{ height: '56px' }}
            >
              Clear
            </Button>
          </Grid>
        </Grid>
      </Box>

      {/* Results Count */}
      <Box sx={{ mb: 3 }}>
        <Typography variant="h6" color="text.secondary">
          {pagination.total} properties found
        </Typography>
      </Box>

      {/* Property Grid */}
      <Grid container spacing={3} className="property-gallery">
        {listings.map((listing) => (
          <Grid item xs={12} sm={6} md={4} key={listing.id}>
            <Card
              sx={{ cursor: 'pointer', transition: 'box-shadow 0.2s', '&:hover': { boxShadow: 6 } }}
              onClick={() => navigate(`/listings/${listing.id}`)}
            >
              <CardMedia
                component="img"
                height="200"
                image={listing.primary_image || 'https://via.placeholder.com/400x200?text=No+Image'}
                alt={listing.title}
                className="property-image"
              />
              
              <CardContent className="property-content">
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 1 }}>
                  <Typography className="property-price">
                    {formatPrice(listing.price)}
                  </Typography>
                  {user && (
                    <IconButton
                      onClick={() => toggleFavorite(listing.id)}
                      color="primary"
                      size="small"
                    >
                      {listing.is_favorited ? <Favorite /> : <FavoriteBorder />}
                    </IconButton>
                  )}
                </Box>
                
                <Typography className="property-title" variant="h6">
                  {listing.title}
                </Typography>
                
                <Box className="property-location">
                  <LocationOn fontSize="small" />
                  <Typography variant="body2">
                    {listing.city}, {listing.state}
                  </Typography>
                </Box>
                
                <Box className="property-features">
                  {listing.bedrooms && (
                    <Box className="property-feature">
                      <Bed fontSize="small" />
                      <span>{listing.bedrooms} beds</span>
                    </Box>
                  )}
                  {listing.bathrooms && (
                    <Box className="property-feature">
                      <Bathtub fontSize="small" />
                      <span>{listing.bathrooms} baths</span>
                    </Box>
                  )}
                  {listing.square_feet && (
                    <Box className="property-feature">
                      <SquareFoot fontSize="small" />
                      <span>{listing.square_feet.toLocaleString()} sq ft</span>
                    </Box>
                  )}
                </Box>
                
                <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap', mb: 2 }}>
                  <Chip 
                    label={listing.property_type} 
                    size="small" 
                    color="primary" 
                    variant="outlined" 
                  />
                  <Chip 
                    label={listing.status} 
                    size="small" 
                    color={listing.status === 'active' ? 'success' : 'default'} 
                  />
                </Box>
                
                <Button
                  fullWidth
                  variant="contained"
                  href={`/listing/${listing.id}`}
                >
                  View Details
                </Button>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>

      {/* Pagination */}
      {pagination.pages > 1 && (
        <Box sx={{ display: 'flex', justifyContent: 'center', mt: 4 }}>
          <Pagination
            count={pagination.pages}
            page={pagination.current_page}
            onChange={handlePageChange}
            color="primary"
            size="large"
          />
        </Box>
      )}

      {listings.length === 0 && !loading && (
        <Box sx={{ textAlign: 'center', mt: 4 }}>
          <Typography variant="h6" color="text.secondary">
            No properties found matching your criteria
          </Typography>
          <Button
            variant="outlined"
            onClick={() => setFilters({})}
            sx={{ mt: 2 }}
          >
            Clear Filters
          </Button>
        </Box>
      )}
    </Container>
  );
};

export default PropertyList; 