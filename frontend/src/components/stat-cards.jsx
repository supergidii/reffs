export default function StatCards() {
    return (
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-white p-6 rounded-lg shadow-sm">
          <h3 className="text-lg font-medium text-gray-700">Total Referral Earnings</h3>
          <p className="text-4xl font-bold mt-2">Ksh 5,000</p>
        </div>
  
        <div className="bg-white p-6 rounded-lg shadow-sm">
          <h3 className="text-lg font-medium text-gray-700">Total Returns</h3>
          <p className="text-4xl font-bold mt-2">Ksh 50,000</p>
        </div>
  
        <div className="bg-white p-6 rounded-lg shadow-sm">
          <h3 className="text-lg font-medium text-gray-700">Queue Position</h3>
          <p className="text-4xl font-bold mt-2">3</p>
        </div>
      </div>
    )
  }
  