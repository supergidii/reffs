import React from 'react';
import { Card, CardContent, Typography, Table, TableBody, TableCell, TableContainer, TableHead, TableRow, Paper } from '@mui/material';
import { formatCurrency } from '../../utils/formatters';

const StatusBadge = ({ status }) => {
  const getStatusColor = (status) => {
    switch (status.toLowerCase()) {
      case 'pending':
        return 'bg-yellow-100 text-yellow-800';
      case 'paired':
        return 'bg-blue-100 text-blue-800';
      case 'completed':
        return 'bg-green-100 text-green-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  return (
    <span className={`px-2 py-1 text-xs font-medium rounded-full ${getStatusColor(status)}`}>
      {status}
    </span>
  );
};

const RecentInvestments = ({ investments }) => {
  return (
    <Card className="bg-white rounded-lg shadow-sm">
      <CardContent>
        <Typography className="text-lg font-semibold text-gray-900 mb-4">
          Recent Investments
        </Typography>
        <div className="overflow-x-auto">
          <table className="w-full min-w-[600px]">
            <thead>
              <tr className="border-b">
                <th className="py-3 px-4 text-left text-sm font-medium text-gray-900">Amount</th>
                <th className="py-3 px-4 text-left text-sm font-medium text-gray-900">Status</th>
                <th className="py-3 px-4 text-left text-sm font-medium text-gray-900">Maturity Period</th>
                <th className="py-3 px-4 text-left text-sm font-medium text-gray-900">Return Amount</th>
                <th className="py-3 px-4 text-left text-sm font-medium text-gray-900">Created At</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200">
              {investments.map((investment) => (
                <tr key={investment.id} className="hover:bg-gray-50">
                  <td className="py-3 px-4 text-sm text-gray-900 whitespace-nowrap">
                    {formatCurrency(investment.amount)}
                  </td>
                  <td className="py-3 px-4 text-sm text-gray-900 whitespace-nowrap">
                    <StatusBadge status={investment.status} />
                  </td>
                  <td className="py-3 px-4 text-sm text-gray-900 whitespace-nowrap">
                    {investment.maturity_period} days
                  </td>
                  <td className="py-3 px-4 text-sm text-gray-900 whitespace-nowrap">
                    {formatCurrency(investment.return_amount)}
                  </td>
                  <td className="py-3 px-4 text-sm text-gray-900 whitespace-nowrap">
                    {new Date(investment.created_at).toLocaleDateString()}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </CardContent>
    </Card>
  );
};

export default RecentInvestments; 