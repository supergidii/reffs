import React from "react"
import { Link } from "react-router-dom"
// import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar" // Commented out - component not found

export default function Navbar() {
  return (
    <nav className="bg-white shadow-sm border-b border-gray-100 sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-8">
        <div className="flex justify-between h-20 items-center">
          <div className="flex space-x-16 items-center">
            <Link to="/" className="text-gray-900 hover:text-black text-base font-medium">Dashboard</Link>
            <Link to="/buy" className="text-gray-900 hover:text-black text-base font-medium">Buy Shares</Link>
            <Link to="/sell" className="text-gray-900 hover:text-black text-base font-medium">Sell Shares</Link>
            <Link to="/referrals" className="text-gray-900 hover:text-black text-base font-medium">Referrals</Link>
            <Link to="/account" className="text-gray-900 hover:text-black text-base font-medium">Account</Link>
          </div>
          <div className="flex items-center">
            {/* Commented out Avatar usage
            <Avatar className="h-10 w-10">
              <AvatarImage src="/placeholder-user.jpg" />
              <AvatarFallback className="bg-gray-200 text-gray-600 text-sm font-medium">JD</AvatarFallback>
            </Avatar>
            */}
            {/* Placeholder until Avatar is added/fixed */}
            <div className="w-10 h-10 bg-gray-200 rounded-full flex items-center justify-center">
              <span className="text-gray-600 text-sm font-medium">JD</span>
            </div>
          </div>
        </div>
      </div>
    </nav>
  )
}
