"use client"

import { useState, useEffect } from "react"
import AuthenticatedLayout from "./layout/authenticated-layout"
import StatCards from "./stat-cards"
import { ChevronDown, ChevronUp } from "lucide-react"
import api from "../services/api"
import { formatCurrency } from "../utils/formatters"

export default function Dashboard() {
  const [isBuyOpen, setIsBuyOpen] = useState(false)
  const [isSellOpen, setIsSellOpen] = useState(false)
  const [isReferralOpen, setIsReferralOpen] = useState(false)
  const [formData, setFormData] = useState({
    amount: '',
    maturityPeriod: '30'
  })
  const [dashboardData, setDashboardData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [sellSharesData, setSellSharesData] = useState([])

  useEffect(() => {
    const fetchDashboardData = async () => {
      try {
        console.log('Fetching dashboard data...');
        const response = await api.get('/api/user-dashboard/');
        console.log('Dashboard API Response:', response.data);
        
        if (response.data.error) {
          console.error('API returned error:', response.data.error);
          setError(response.data.error);
          setLoading(false);
          return;
        }

        setDashboardData(response.data);
        // Transform and set sell shares data from API response
        const transformedData = response.data?.payments?.map(payment => ({
          id: payment.id,
          amount: formatCurrency(payment.amount),
          investor: payment.from_user__username || 'Unknown',
          phone: payment.from_user__phone_number || 'N/A',
          date: new Date(payment.created_at).toLocaleDateString(),
          status: payment.status
        })) || [];
        setSellSharesData(transformedData);
        setLoading(false);
      } catch (err) {
        console.error('Error fetching dashboard data:', err);
        setError('Failed to load dashboard data');
        setLoading(false);
      }
    };

    fetchDashboardData();
  }, []);

  const handleChange = (e) => {
    const { name, value } = e.target
    setFormData(prev => ({
      ...prev,
      [name]: value
    }))
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    console.log('Submitting investment:', formData)
  }

  const handleConfirmPayment = async (paymentId) => {
    try {
      // Make actual API call to confirm payment
      const response = await api.post(`/api/payments/${paymentId}/confirm/`);
      console.log('Payment confirmation response:', response.data);
      
      // Update local state to reflect the change
      setSellSharesData(prevData => 
        prevData.map(item => 
          item.id === paymentId 
            ? { ...item, status: 'Confirmed' }
            : item
        )
      );
      
      // Refresh dashboard data
      const dashboardResponse = await api.get('/api/user-dashboard/');
      setDashboardData(dashboardResponse.data);
      
      alert('Payment confirmed successfully!');
    } catch (err) {
      console.error('Error confirming payment:', err);
      setError('Failed to confirm payment');
    }
  };

  // Transform API data for referrals table with null checks
  const referralsData = dashboardData?.referral?.referrals
    ?.map(ref => ({
      name: ref?.referred?.username || 'Unknown',
      phone: ref?.referred?.phone_number || 'N/A',
      status: ref?.status === 'pending' ? 'Active' : 'Inactive',
      earnings: formatCurrency(ref?.bonus_earned || 0),
    })) || []

  if (loading) {
    return (
      <AuthenticatedLayout>
        <div className="flex justify-center items-center min-h-[400px]">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
        </div>
      </AuthenticatedLayout>
    );
  }

  if (error) {
    return (
      <AuthenticatedLayout>
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
          {error}
        </div>
      </AuthenticatedLayout>
    );
  }

  return (
    <AuthenticatedLayout>
      <div className="space-y-6">
        {!loading && !error && dashboardData && (
          <StatCards data={dashboardData} />
        )}

        {/* Buy Shares Section */}
        <div className="bg-white rounded-lg shadow-sm overflow-hidden">
          <div 
            className="flex items-center justify-between p-4 cursor-pointer"
            onClick={() => setIsBuyOpen(!isBuyOpen)}
          >
            <h2 className="text-lg sm:text-xl font-semibold text-gray-900">Buy Shares</h2>
            <button className="p-2 rounded-full hover:bg-gray-100">
              {isBuyOpen ? (
                <ChevronUp className="h-5 w-5 text-gray-500" />
              ) : (
                <ChevronDown className="h-5 w-5 text-gray-500" />
              )}
            </button>
          </div>

          <div 
            className={`transition-all duration-300 ease-in-out overflow-hidden ${
              isBuyOpen ? 'max-h-[600px] opacity-100' : 'max-h-0 opacity-0'
            }`}
          >
            <div className="p-4 border-t border-gray-200">
              <form onSubmit={handleSubmit} className="space-y-4">
                <div>
                  <label htmlFor="amount" className="block text-sm font-medium text-gray-700 mb-1">
                    Amount to Invest
                  </label>
                  <div className="relative">
                    <span className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-500">$</span>
                    <input
                      id="amount"
                      name="amount"
                      type="number"
                      value={formData.amount}
                      onChange={handleChange}
                      className="w-full pl-8 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      placeholder="Enter amount"
                      required
                      min="0"
                      step="0.01"
                    />
                  </div>
                </div>

                <div>
                  <label htmlFor="maturityPeriod" className="block text-sm font-medium text-gray-700 mb-1">
                    Maturity Period
                  </label>
                  <select
                    id="maturityPeriod"
                    name="maturityPeriod"
                    value={formData.maturityPeriod}
                    onChange={handleChange}
                    className="w-full p-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  >
                    <option value="30">30 Days</option>
                    <option value="60">60 Days</option>
                    <option value="90">90 Days</option>
                    <option value="180">180 Days</option>
                    <option value="365">365 Days</option>
                  </select>
                </div>

                <div className="bg-gray-50 p-3 rounded-lg">
                  <h3 className="text-sm font-medium text-gray-900 mb-2">Investment Summary</h3>
                  <div className="space-y-1">
                    <div className="flex justify-between text-sm">
                      <span className="text-gray-500">Principal Amount</span>
                      <span className="text-gray-900">${formData.amount || '0.00'}</span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span className="text-gray-500">Daily Interest (2%)</span>
                      <span className="text-gray-900">${(formData.amount * 0.02 || 0).toFixed(2)}</span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span className="text-gray-500">Total Return</span>
                      <span className="text-gray-900">${(formData.amount * (1 + 0.02 * formData.maturityPeriod) || 0).toFixed(2)}</span>
                    </div>
                  </div>
                </div>

                <button
                  type="submit"
                  className="w-full bg-blue-600 text-white py-2 rounded-lg hover:bg-blue-700 transition-colors focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
                >
                  Place Your Bid
                </button>
              </form>
            </div>
          </div>
        </div>

        {/* Sell Shares Section */}
        <div className="bg-white rounded-lg shadow-sm overflow-hidden">
          <div 
            className="flex items-center justify-between p-4 cursor-pointer"
            onClick={() => setIsSellOpen(!isSellOpen)}
          >
            <h2 className="text-lg sm:text-xl font-semibold text-gray-900">Sell Shares</h2>
            <button className="p-2 rounded-full hover:bg-gray-100">
              {isSellOpen ? (
                <ChevronUp className="h-5 w-5 text-gray-500" />
              ) : (
                <ChevronDown className="h-5 w-5 text-gray-500" />
              )}
            </button>
          </div>

          <div 
            className={`transition-all duration-300 ease-in-out overflow-hidden ${
              isSellOpen ? 'max-h-[600px] opacity-100' : 'max-h-0 opacity-0'
            }`}
          >
            <div className="p-4 border-t border-gray-200">
              <div className="overflow-x-auto">
                <table className="w-full min-w-[600px]">
                  <thead>
                    <tr className="border-b">
                      <th className="py-3 px-4 text-left text-sm font-medium text-gray-900">Amount to Receive</th>
                      <th className="py-3 px-4 text-left text-sm font-medium text-gray-900">Paired Investor</th>
                      <th className="py-3 px-4 text-left text-sm font-medium text-gray-900">Phone</th>
                      <th className="py-3 px-4 text-left text-sm font-medium text-gray-900">Date</th>
                      <th className="py-3 px-4 text-left text-sm font-medium text-gray-900">Status</th>
                      <th className="py-3 px-4 text-left text-sm font-medium text-gray-900">Action</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-200">
                    {sellSharesData.map((item) => (
                      <tr key={item.id} className="hover:bg-gray-50">
                        <td className="py-3 px-4 text-sm text-gray-900 whitespace-nowrap">{item.amount}</td>
                        <td className="py-3 px-4 text-sm text-gray-900 whitespace-nowrap">{item.investor}</td>
                        <td className="py-3 px-4 text-sm text-gray-900 whitespace-nowrap">{item.phone}</td>
                        <td className="py-3 px-4 text-sm text-gray-900 whitespace-nowrap">{item.date}</td>
                        <td className="py-3 px-4 text-sm text-gray-900 whitespace-nowrap">
                          <span className={`px-2 py-1 text-xs font-medium rounded-full ${
                            item.status === "Confirmed" ? "bg-green-100 text-green-800" : "bg-yellow-100 text-yellow-800"
                          }`}>
                            {item.status}
                          </span>
                        </td>
                        <td className="py-3 px-4 text-sm text-gray-900 whitespace-nowrap">
                          {item.status === 'Pending' && (
                            <button 
                              onClick={() => handleConfirmPayment(item.id)}
                              className="px-3 py-1 bg-white text-black border border-gray-300 rounded hover:bg-gray-100"
                            >
                              Confirm
                            </button>
                          )}
                        </td>
                      </tr>
                    ))}
                    {sellSharesData.length === 0 && (
                      <tr>
                        <td colSpan="6" className="py-4 text-center text-gray-500">
                          No pending payments to confirm
                        </td>
                      </tr>
                    )}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        </div>

        {/* Referrals Section */}
        <div className="bg-white rounded-lg shadow-sm overflow-hidden">
          <div 
            className="flex items-center justify-between p-4 cursor-pointer"
            onClick={() => setIsReferralOpen(!isReferralOpen)}
          >
            <h2 className="text-lg sm:text-xl font-semibold text-gray-900">Referrals</h2>
            <button className="p-2 rounded-full hover:bg-gray-100">
              {isReferralOpen ? (
                <ChevronUp className="h-5 w-5 text-gray-500" />
              ) : (
                <ChevronDown className="h-5 w-5 text-gray-500" />
              )}
            </button>
          </div>

          <div 
            className={`transition-all duration-300 ease-in-out overflow-hidden ${
              isReferralOpen ? 'max-h-[600px] opacity-100' : 'max-h-0 opacity-0'
            }`}
          >
            <div className="p-4 border-t border-gray-200">
              <div className="overflow-x-auto">
                <table className="w-full min-w-[600px]">
                  <thead>
                    <tr className="border-b">
                      <th className="py-3 px-4 text-left text-sm font-medium text-gray-900">Referred User</th>
                      <th className="py-3 px-4 text-left text-sm font-medium text-gray-900">Phone Number</th>
                      <th className="py-3 px-4 text-left text-sm font-medium text-gray-900">Status</th>
                      <th className="py-3 px-4 text-left text-sm font-medium text-gray-900">Earnings</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-200">
                    {referralsData.map((item, index) => (
                      <tr key={index} className="hover:bg-gray-50">
                        <td className="py-3 px-4 text-sm text-gray-900 whitespace-nowrap">{item.name}</td>
                        <td className="py-3 px-4 text-sm text-gray-900 whitespace-nowrap">{item.phone}</td>
                        <td className="py-3 px-4 text-sm text-gray-900 whitespace-nowrap">
                          <span className={`px-2 py-1 text-xs font-medium rounded-full ${
                            item.status === "Active" ? "bg-green-100 text-green-800" : "bg-gray-100 text-gray-800"
                          }`}>
                            {item.status}
                          </span>
                        </td>
                        <td className="py-3 px-4 text-sm text-gray-900 whitespace-nowrap">{item.earnings}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        </div>
      </div>
    </AuthenticatedLayout>
  );
}
