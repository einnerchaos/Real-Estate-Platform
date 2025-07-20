import React, { useState } from 'react';
import { Box, Typography, Grid, List, ListItem, ListItemText, Paper, Divider, TextField, Button } from '@mui/material';

const demoConversations = [
  { id: 1, name: 'Sarah Johnson', last: 'Is the house still available?', messages: [
    { from: 'them', text: 'Is the house still available?' },
    { from: 'me', text: 'Yes, it is! Would you like to schedule a visit?' },
    { from: 'them', text: 'Yes, please. Tomorrow works.' },
  ]},
  { id: 2, name: 'David Lee', last: 'Thanks for the info!', messages: [
    { from: 'me', text: 'I sent you the documents.' },
    { from: 'them', text: 'Thanks for the info!' },
  ]},
];

export default function Messages() {
  const [selected, setSelected] = useState(0);
  const [input, setInput] = useState('');
  const [convos, setConvos] = useState(demoConversations);

  const handleSend = () => {
    if (!input.trim()) return;
    const newConvos = [...convos];
    newConvos[selected].messages.push({ from: 'me', text: input });
    setConvos(newConvos);
    setInput('');
  };

  return (
    <Box>
      <Typography variant="h4" mb={3}>Messages</Typography>
      <Grid container spacing={2}>
        <Grid item xs={12} md={4}>
          <Paper sx={{ height: 400, overflow: 'auto' }}>
            <List>
              {convos.map((c, i) => (
                <ListItem button selected={selected === i} onClick={() => setSelected(i)} key={c.id}>
                  <ListItemText primary={c.name} secondary={c.last} />
                </ListItem>
              ))}
            </List>
          </Paper>
        </Grid>
        <Grid item xs={12} md={8}>
          <Paper sx={{ height: 400, p: 2, display: 'flex', flexDirection: 'column' }}>
            <Box sx={{ flex: 1, overflow: 'auto', mb: 2 }}>
              {convos[selected].messages.map((m, idx) => (
                <Box key={idx} sx={{ textAlign: m.from === 'me' ? 'right' : 'left', mb: 1 }}>
                  <Typography variant="body2" color={m.from === 'me' ? 'primary' : 'text.secondary'}>
                    {m.text}
                  </Typography>
                </Box>
              ))}
            </Box>
            <Divider sx={{ mb: 2 }} />
            <Box sx={{ display: 'flex', gap: 2 }}>
              <TextField fullWidth size="small" value={input} onChange={e => setInput(e.target.value)} placeholder="Type a message..." />
              <Button variant="contained" onClick={handleSend}>Send</Button>
            </Box>
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
} 