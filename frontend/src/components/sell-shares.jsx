import { Button } from "./ui/button"

export default function SellShares({ data }) {
  return (
    <div className="bg-white p-6 rounded-lg shadow-sm">
      <h2 className="text-xl font-bold mb-4">Sell Shares</h2>
      <div className="overflow-x-auto">
        <table className="min-w-full">
          <thead>
            <tr className="text-left text-sm font-medium text-gray-700">
              <th className="pb-2">Amount to be Paid</th>
              <th className="pb-2">Investor</th>
              <th className="pb-2">Date</th>
              <th className="pb-2">Status</th>
              <th className="pb-2">Action</th>
            </tr>
          </thead>
          <tbody>
            {data.map((item, index) => (
              <tr key={index} className="border-t border-gray-200">
                <td className="py-3">{item.amount}</td>
                <td className="py-3">{item.investor}</td>
                <td className="py-3">{item.date}</td>
                <td className="py-3">{item.status}</td>
                <td className="py-3">
                  <Button className="bg-blue-500 hover:bg-blue-600 text-white">Confirm</Button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
