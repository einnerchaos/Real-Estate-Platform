import React, { useState } from 'react';
import { Box, Typography, TextField, Button, Switch, FormControlLabel, Stack, Alert } from '@mui/material';

export default function Settings() {
  const [password, setPassword] = useState('');
  const [notif, setNotif] = useState(true);
  const [success, setSuccess] = useState('');
  const [error, setError] = useState('');

  const handlePassword = () => {
    if (!password) { setError('Enter a new password.'); return; }
    setSuccess('Password changed (demo only).'); setError(''); setPassword('');
  };

  return (
    <Box>
      <Typography variant="h4" mb={3}>Settings</Typography>
      {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}
      {success && <Alert severity="success" sx={{ mb: 2 }}>{success}</Alert>}
      <Box sx={{ mb: 3 }}>
        <Typography variant="h6">Change Password</Typography>
        <Stack direction="row" spacing={2} alignItems="center" sx={{ mt: 1 }}>
          <TextField label="New Password" type="password" value={password} onChange={e => setPassword(e.target.value)} />
          <Button variant="contained" onClick={handlePassword}>Change</Button>
        </Stack>
      </Box>
      <Box sx={{ mb: 3 }}>
        <Typography variant="h6">Notifications</Typography>
        <FormControlLabel control={<Switch checked={notif} onChange={e => setNotif(e.target.checked)} />} label="Email Notifications" />
      </Box>
      <Box>
        <Typography variant="h6">Account Actions</Typography>
        <Button variant="outlined" color="error" sx={{ mt: 1 }}>Delete Account (demo)</Button>
      </Box>
    </Box>
  );
} 