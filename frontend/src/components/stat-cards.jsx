export default function StatCards({ data }) {
  console.log('StatCards received data:', data);

  // Safely extract values with defaults
  const totalReferralEarnings = data?.statistics?.total_referral_earnings || 0;
  const totalReturns = data?.statistics?.total_returns || 0;
  const dueEarnings = data?.statistics?.due_earnings || 0;
  const activeInvestments = data?.statistics?.active_investments || 0;
  const pendingPayments = data?.statistics?.pending_payments || 0;
  const totalReferrals = data?.referral?.total_referrals || 0;
  const completedInvestments = data?.investments?.by_status?.completed || 0;

  console.log('StatCards extracted values:', {
    totalReferralEarnings,
    totalReturns,
    dueEarnings,
    activeInvestments,
    pendingPayments,
    totalReferrals,
    completedInvestments
  });

  // Format numbers with proper currency formatting
  const formatAmount = (amount) => {
    return `Ksh ${Number(amount).toLocaleString('en-KE', {
      minimumFractionDigits: 2,
      maximumFractionDigits: 2
    })}`;
  };

  return (
    <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
      <div className="bg-white p-6 rounded-lg shadow-sm">
        <h3 className="text-lg font-medium text-gray-700">Total Referral Earnings</h3>
        <p className="text-4xl font-bold mt-2">{formatAmount(totalReferralEarnings)}</p>
        <p className="text-sm text-gray-500 mt-1">From {totalReferrals} referrals</p>
      </div>

      <div className="bg-white p-6 rounded-lg shadow-sm">
        <h3 className="text-lg font-medium text-gray-700">Total Returns</h3>
        <p className="text-4xl font-bold mt-2">{formatAmount(totalReturns)}</p>
        <p className="text-sm text-gray-500 mt-1">From {completedInvestments} completed investments</p>
      </div>

      <div className="bg-white p-6 rounded-lg shadow-sm">
        <h3 className="text-lg font-medium text-gray-700">Due Earnings</h3>
        <p className="text-4xl font-bold mt-2">{formatAmount(dueEarnings)}</p>
        <p className="text-sm text-gray-500 mt-1">From matured investments</p>
      </div>

      <div className="bg-white p-6 rounded-lg shadow-sm">
        <h3 className="text-lg font-medium text-gray-700">Active Investments</h3>
        <p className="text-4xl font-bold mt-2">{activeInvestments}</p>
        <p className="text-sm text-gray-500 mt-1">Current active investments</p>
      </div>

      <div className="bg-white p-6 rounded-lg shadow-sm">
        <h3 className="text-lg font-medium text-gray-700">Pending Payments</h3>
        <p className="text-4xl font-bold mt-2">{pendingPayments}</p>
        <p className="text-sm text-gray-500 mt-1">Awaiting confirmation</p>
      </div>
    </div>
  )
}
  