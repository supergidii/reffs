import React, { useState, useEffect } from 'react';
import { CircularProgress, Alert } from '@mui/material';
import { useNavigate } from 'react-router-dom';
import api from '../../services/api';
import { authService } from '../../services/api';
import StatCards from './StatCards';
import ReferralSection from './ReferralSection';
import RecentInvestments from './RecentInvestments';

const UserDashboard = () => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const navigate = useNavigate();

  useEffect(() => {
    // Check if user is authenticated
    if (!authService.isAuthenticated()) {
      console.log('User not authenticated, redirecting to login');
      navigate('/login');
      return;
    }

    const fetchData = async () => {
      try {
        console.log('Fetching dashboard data...');
        const response = await api.get('/user-dashboard/');
        console.log('Dashboard data received:', response.data);
        setData(response.data);
        setLoading(false);
      } catch (err) {
        console.error('Dashboard fetch error:', err);
        if (err.response?.status === 401) {
          console.log('Token expired or invalid, redirecting to login');
          navigate('/login');
        } else {
          setError('Failed to fetch dashboard data');
        }
        setLoading(false);
      }
    };

    fetchData();
  }, [navigate]);

  if (loading) {
    return (
      <div className="flex justify-center items-center min-h-[400px]">
        <CircularProgress />
      </div>
    );
  }

  if (error) {
    return <Alert severity="error">{error}</Alert>;
  }

  if (!data) return null;

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-semibold text-gray-900">
        Welcome, {data.user.username}!
      </h1>

      <StatCards data={data} />
      <ReferralSection data={data} />
      <RecentInvestments investments={data.investments.recent} />
    </div>
  );
};

export default UserDashboard; 