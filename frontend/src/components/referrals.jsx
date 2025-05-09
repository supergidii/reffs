"use client"

import { useState } from "react"
import AuthenticatedLayout from "./layout/authenticated-layout"
import { Button } from "./ui/button"

export default function Referrals() {
  const [copied, setCopied] = useState(false)
  const referralLink = "https://example.com/ref=ABC123"

  const referralsData = [
    {
      name: "John Doe",
      phone: "(123) 456-7890",
      status: "Active",
      earnings: "$20.00"
    },
    {
      name: "Jane Smith",
      phone: "(987) 654-3210",
      status: "Inactive",
      earnings: "$0.00"
    },
    {
      name: "Michael Brown",
      phone: "(555) 123-4567",
      status: "Active",
      earnings: "$20.00"
    },
    {
      name: "Jane DIrown",
      phone: "(555) 123-4567",
      status: "Active",
      earnings: "$20.00"
    },
  ]

  const handleCopy = () => {
    navigator.clipboard.writeText(referralLink)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  return (
    <AuthenticatedLayout>
      <div className="max-w-4xl mx-auto">
        <div className="bg-white rounded-lg shadow-sm overflow-hidden">
          <div className="p-4 sm:p-6">
            <h1 className="text-2xl sm:text-3xl font-bold mb-4 sm:mb-6">Referrals</h1>

            {/* Referral Link Section */}
            <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 mb-6 border-b pb-4 sm:pb-6">
              <div className="w-full sm:w-auto">
                <div className="text-sm sm:text-base text-gray-600 break-all">{referralLink}</div>
              </div>
              <Button 
                onClick={handleCopy} 
                className="w-full sm:w-auto bg-gray-800 hover:bg-gray-700 text-white text-sm sm:text-base"
              >
                {copied ? "Copied!" : "Copy Link"}
              </Button>
            </div>

            {/* Referrals Table */}
            <div className="overflow-x-auto">
              <table className="w-full min-w-[600px]">
                <thead>
                  <tr className="border-b">
                    <th className="py-3 px-4 text-left text-sm font-medium text-gray-900">Referred User</th>
                    <th className="py-3 px-4 text-left text-sm font-medium text-gray-900">Phone Number</th>
                    <th className="py-3 px-4 text-left text-sm font-medium text-gray-900">Status</th>
                    <th className="py-3 px-4 text-left text-sm font-medium text-gray-900">Total Earnings</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-200">
                  {referralsData.map((item, index) => (
                    <tr key={index} className="hover:bg-gray-50">
                      <td className="py-3 px-4 text-sm text-gray-900 whitespace-nowrap">{item.name}</td>
                      <td className="py-3 px-4 text-sm text-gray-900 whitespace-nowrap">{item.phone}</td>
                      <td className="py-3 px-4 text-sm text-gray-900 whitespace-nowrap">
                        {item.status === "Active" ? (
                          <span className="px-2 py-1 text-xs font-medium rounded-full bg-green-100 text-green-800">
                            {item.status}
                          </span>
                        ) : (
                          <span className="px-2 py-1 text-xs font-medium rounded-full bg-gray-100 text-gray-800">
                            {item.status}
                          </span>
                        )}
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
    </AuthenticatedLayout>
  )
}
