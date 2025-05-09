import React, { useState } from 'react';
import { Card, CardContent, Typography, TextField, InputAdornment, IconButton, Box } from '@mui/material';
import { ContentCopy as CopyIcon } from '@mui/icons-material';
import { formatCurrency } from '../../utils/formatters';

const ReferralSection = ({ data }) => {
  const [copied, setCopied] = useState(false);

  const copyReferralLink = () => {
    navigator.clipboard.writeText(data.referral.referral_link);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <Card className="bg-white rounded-lg shadow-sm mb-6">
      <CardContent>
        <Typography className="text-lg font-semibold text-gray-900 mb-4">
          Referral Program
        </Typography>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="md:col-span-2">
            <TextField
              fullWidth
              value={data.referral.referral_link}
              className="bg-gray-50"
              InputProps={{
                readOnly: true,
                className: "text-sm",
                endAdornment: (
                  <InputAdornment position="end">
                    <IconButton 
                      onClick={copyReferralLink}
                      className="hover:bg-gray-100"
                    >
                      <CopyIcon className="text-gray-500" />
                    </IconButton>
                  </InputAdornment>
                ),
              }}
            />
          </div>
          <div className="space-y-2">
            <Typography className="text-sm text-gray-600">
              Total Referrals: <span className="font-semibold">{data.referral.total_referrals}</span>
            </Typography>
            <Typography className="text-sm text-gray-600">
              Active Referrals: <span className="font-semibold">{data.referral.active_referrals}</span>
            </Typography>
            <Typography className="text-sm text-gray-600">
              Total Earnings: <span className="font-semibold">{formatCurrency(data.referral.total_earnings)}</span>
            </Typography>
          </div>
        </div>
      </CardContent>
    </Card>
  );
};

export default ReferralSection; 