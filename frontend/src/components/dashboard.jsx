"use client"

import { useState } from "react"
import Navbar from "./navbar"
import StatCards from "./stat-cards"
import BuyShares from "./buy-shares"
import SellShares from "./sell-shares"
import Referrals from "./referrals"

export default function Dashboard() {
  const [amount, setAmount] = useState("")

  const handleBid = () => {
    // Handle bid submission
    console.log("Placing bid for:", amount)
    setAmount("")
  }

  const sellSharesData = [
    {
      amount: "Ksh 10,000",
      investor: "Naomi",
      date: "2024-04-20",
      status: "Confirmed",
    },
    {
      amount: "Ksh 25,000",
      investor: "Peter",
      date: "2024-04-18",
      status: "Pending",
    },
    {
      amount: "Ksh 15,000",
      investor: "David",
      date: "070123 4567",
      status: "Confirmed",
    },
  ]

  const referralsData = [
    {
      name: "John",
      phone: "0721123456",
      status: "Active",
      earnings: "Ksh 1,500",
    },
    {
      name: "Sarah",
      phone: "0798765432",
      status: "Inactive",
      earnings: "Ksh 2,000",
    },
    {
      name: "Tom",
      phone: "0731345578",
      status: "Active",
      earnings: "Ksh 1,500",
    },
  ]

  return (
    <div className="min-h-screen bg-slate-50">
      <Navbar />
      <div className="container mx-auto px-4 py-6">
        <StatCards />

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mt-6">
          <BuyShares amount={amount} setAmount={setAmount} onBid={handleBid} />
          <SellShares data={sellSharesData} />
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mt-6">
          <Referrals data={referralsData} />
          <Referrals data={referralsData} />
        </div>
      </div>
    </div>
  )
}
