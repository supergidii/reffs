import React from 'react';
import { Card, CardContent, Typography, Grid } from '@mui/material';
import { formatCurrency } from '../../utils/formatters';

const StatCard = ({ title, value, subtitle }) => (
  <Card className="bg-white rounded-lg shadow-sm">
    <CardContent>
      <Typography className="text-gray-500 text-sm" gutterBottom>
        {title}
      </Typography>
      <Typography className="text-2xl font-semibold text-gray-900">
        {value}
      </Typography>
      {subtitle && (
        <Typography className="text-sm text-gray-500 mt-1">
          {subtitle}
        </Typography>
      )}
    </CardContent>
  </Card>
);

const StatCards = ({ data }) => {
  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
      <StatCard
        title="Total Returns"
        value={formatCurrency(data.statistics.total_returns)}
        subtitle={`From ${data.investments.by_status.completed} completed investments`}
      />
      <StatCard
        title="Active Investments"
        value={data.statistics.active_investments}
        subtitle={`${data.investments.by_status.pending} pending, ${data.investments.by_status.paired} paired`}
      />
      <StatCard
        title="Total Referral Earnings"
        value={formatCurrency(data.statistics.total_referral_earnings)}
        subtitle={`From ${data.referral.total_referrals} referrals`}
      />
      <StatCard
        title="Queue Position"
        value={data.statistics.queue_position}
        subtitle="Your position in the queue"
      />
    </div>
  );
};

export default StatCards; 