import AuthenticatedLayout from "./layout/authenticated-layout"
import { Button } from "./ui/button"

export default function SellShares() {
  const sellSharesData = [
    {
      amount: "$1,050.00",
      investor: "Robert Brown",
      phone: "(987) 654-3210",
      date: "May 25, 2024",
      status: "Pending",
    },
    // Add more data here if needed
  ]

  return (
    <AuthenticatedLayout>
      <h1 className="text-4xl font-bold mb-8">Sell Shares</h1>

      {/* Sell Shares Table */}
      <div className="bg-white border rounded-lg shadow-sm overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full min-w-[800px]">
            <thead className="bg-gray-50 border-b">
              <tr>
                <th className="px-6 py-4 text-left text-sm font-medium text-gray-900">Amount to Receive</th>
                <th className="px-6 py-4 text-left text-sm font-medium text-gray-900">Paired Investor Name</th>
                <th className="px-6 py-4 text-left text-sm font-medium text-gray-900">Phone Number</th>
                <th className="px-6 py-4 text-left text-sm font-medium text-gray-900">Date</th>
                <th className="px-6 py-4 text-left text-sm font-medium text-gray-900">Status</th>
                <th className="px-6 py-4 text-left text-sm font-medium text-gray-900">Action</th>
              </tr>
            </thead>
            <tbody>
              {sellSharesData.map((item, index) => (
                <tr key={index} className="border-b">
                  <td className="px-6 py-4 text-sm text-gray-900">{item.amount}</td>
                  <td className="px-6 py-4 text-sm text-gray-900">{item.investor}</td>
                  <td className="px-6 py-4 text-sm text-gray-900">{item.phone}</td>
                  <td className="px-6 py-4 text-sm text-gray-900">{item.date}</td>
                  <td className="px-6 py-4 text-sm text-gray-900">{item.status}</td>
                  <td className="px-6 py-4 text-sm text-gray-900">
                    <Button variant="outline" size="sm">
                      Confirm
                    </Button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </AuthenticatedLayout>
  );
}
