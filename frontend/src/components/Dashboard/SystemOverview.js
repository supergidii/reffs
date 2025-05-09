import React, { useState, useEffect } from 'react';
import {
  Box,
  Grid,
  Card,
  CardContent,
  Typography,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  CircularProgress,
  Alert,
} from '@mui/material';
import { formatCurrency } from '../../utils/formatters';
import axios from 'axios';

const StatCard = ({ title, value, subtitle }) => (
  <Card>
    <CardContent>
      <Typography color="textSecondary" gutterBottom>
        {title}
      </Typography>
      <Typography variant="h4" component="div">
        {value}
      </Typography>
      {subtitle && (
        <Typography color="textSecondary">
          {subtitle}
        </Typography>
      )}
    </CardContent>
  </Card>
);

const SystemOverview = () => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await axios.get('/api/system-overview/');
        setData(response.data);
        setLoading(false);
      } catch (err) {
        setError('Failed to fetch system overview data');
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return <Alert severity="error">{error}</Alert>;
  }

  if (!data) return null;

  return (
    <Box p={3}>
      <Typography variant="h4" gutterBottom>
        System Overview
      </Typography>

      {/* Statistics Cards */}
      <Grid container spacing={3} mb={4}>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Total Users"
            value={data.user_statistics.total_users}
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Total Investments"
            value={data.investment_statistics.total_investments}
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Total Payments"
            value={data.payment_statistics.total_payments}
            subtitle={`Total: ${formatCurrency(data.payment_statistics.total_amount)}`}
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Queue Entries"
            value={data.queue_statistics.total_entries}
            subtitle={`Total: ${formatCurrency(data.queue_statistics.total_amount)}`}
          />
        </Grid>
      </Grid>

      {/* Investment Status Breakdown */}
      <Card mb={4}>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Investment Status Breakdown
          </Typography>
          <TableContainer component={Paper}>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Status</TableCell>
                  <TableCell align="right">Count</TableCell>
                  <TableCell align="right">Total Amount</TableCell>
                  <TableCell align="right">Average Amount</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {data.investment_statistics.status_breakdown.map((status) => (
                  <TableRow key={status.status}>
                    <TableCell>{status.status}</TableCell>
                    <TableCell align="right">{status.count}</TableCell>
                    <TableCell align="right">{formatCurrency(status.total_amount)}</TableCell>
                    <TableCell align="right">{formatCurrency(status.avg_amount)}</TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        </CardContent>
      </Card>

      {/* User Details */}
      <Card>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            User Investment Details
          </Typography>
          <TableContainer component={Paper}>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>User</TableCell>
                  <TableCell>Phone</TableCell>
                  <TableCell align="right">Total Investments</TableCell>
                  <TableCell align="right">Pending</TableCell>
                  <TableCell align="right">Paired</TableCell>
                  <TableCell align="right">Completed</TableCell>
                  <TableCell align="right">Payments Made</TableCell>
                  <TableCell align="right">Payments Received</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {data.user_details.map((user) => (
                  <TableRow key={user.username}>
                    <TableCell>{user.username}</TableCell>
                    <TableCell>{user.phone_number}</TableCell>
                    <TableCell align="right">{user.total_investments}</TableCell>
                    <TableCell align="right">
                      {user.investments_by_status.pending?.count || 0}
                      <br />
                      {formatCurrency(user.investments_by_status.pending?.total || 0)}
                    </TableCell>
                    <TableCell align="right">
                      {user.investments_by_status.paired?.count || 0}
                      <br />
                      {formatCurrency(user.investments_by_status.paired?.total || 0)}
                    </TableCell>
                    <TableCell align="right">
                      {user.investments_by_status.completed?.count || 0}
                      <br />
                      {formatCurrency(user.investments_by_status.completed?.total || 0)}
                    </TableCell>
                    <TableCell align="right">
                      {user.payments.made.count}
                      <br />
                      {formatCurrency(user.payments.made.total)}
                    </TableCell>
                    <TableCell align="right">
                      {user.payments.received.count}
                      <br />
                      {formatCurrency(user.payments.received.total)}
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        </CardContent>
      </Card>
    </Box>
  );
};

export default SystemOverview; 