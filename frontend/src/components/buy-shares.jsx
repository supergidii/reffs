"use client"

import React, { useState } from 'react'
import PropTypes from 'prop-types'
import { Link } from 'react-router-dom'
import { ChevronDown, ChevronUp, User, LogOut } from 'lucide-react'
import { authService } from '../services/api'
import AuthenticatedLayout from "./layout/authenticated-layout"

export default function BuyShares() {
  const [isOpen, setIsOpen] = useState(false)
  const [formData, setFormData] = useState({
    amount: '',
    maturityPeriod: '30' // Default to 30 days
  })

  const handleChange = (e) => {
    const { name, value } = e.target
    setFormData(prev => ({
      ...prev,
      [name]: value
    }))
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    // TODO: Implement investment creation
    console.log('Submitting investment:', formData)
  }

  return (
    <AuthenticatedLayout>
      <div className="max-w-2xl mx-auto">
        <div className="bg-white rounded-lg shadow-lg overflow-hidden">
          {/* Header with toggle */}
          <div 
            className="flex items-center justify-between p-4 cursor-pointer"
            onClick={() => setIsOpen(!isOpen)}
          >
            <h2 className="text-xl font-semibold text-gray-900">Buy Shares</h2>
            <button className="p-2 rounded-full hover:bg-gray-100">
              {isOpen ? (
                <ChevronUp className="h-5 w-5 text-gray-500" />
              ) : (
                <ChevronDown className="h-5 w-5 text-gray-500" />
              )}
            </button>
          </div>

          {/* Collapsible content */}
          <div 
            className={`transition-all duration-300 ease-in-out overflow-hidden ${
              isOpen ? 'max-h-[600px] opacity-100' : 'max-h-0 opacity-0'
            }`}
          >
            <div className="p-4 border-t border-gray-200">
              <form onSubmit={handleSubmit} className="space-y-4">
                {/* Amount Input */}
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

                {/* Maturity Period Select */}
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

                {/* Investment Summary */}
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

                {/* Submit Button */}
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
      </div>
    </AuthenticatedLayout>
  )
}

BuyShares.propTypes = {
  amount: PropTypes.string.isRequired,
  setAmount: PropTypes.func.isRequired,
  onBid: PropTypes.func.isRequired,
}
