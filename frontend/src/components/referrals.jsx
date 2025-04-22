import React from "react"



  export default function Referrals({ data }) {
    return (
      <div className="bg-white p-6 rounded-lg shadow-sm">
        <h2 className="text-xl font-bold mb-4">Referrals</h2>
        <div className="mb-4">
          <input
            type="text"
            placeholder="https://example.com/ref/CODE"
            className="w-full p-2 border border-gray-300 rounded-md"
          />
        </div>
        <div className="overflow-x-auto">
          <table className="min-w-full">
            <thead>
              <tr className="text-left text-sm font-medium text-gray-700 border-b border-gray-200">
                <th className="pb-2">Name</th>
                <th className="pb-2">Phone Number</th>
                <th className="pb-2">Status</th>
                <th className="pb-2">Earnings</th>
              </tr>
            </thead>
            <tbody>
              {data.map((item, index) => (
                <tr key={index} className="border-b border-gray-200">
                  <td className="py-3">{item.name}</td>
                  <td className="py-3">{item.phone}</td>
                  <td className="py-3">{item.status}</td>
                  <td className="py-3">{item.earnings}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    )
  }
  