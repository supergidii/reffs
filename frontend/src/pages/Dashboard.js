import React from 'react';
import { Box, Container } from '@mui/material';
import UserDashboard from '../components/Dashboard/UserDashboard';

const Dashboard = () => {
  return (
    <Container maxWidth="lg">
      <Box py={4}>
        <UserDashboard />
      </Box>
    </Container>
  );
};

export default Dashboard; 