import React, { useState } from "react"
import { Link, useNavigate } from "react-router-dom"
import { ChevronDown, User, LogOut, Menu, X } from "lucide-react"
import { authService } from "../services/api"
// import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar" // Commented out - component not found

export default function Navbar() {
  const navigate = useNavigate()
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false)
  const [currentUser, setCurrentUser] = useState({
    name: "John Doe",
    email: "john@example.com",
    avatar: null
  })

  const onLogout = () => {
    authService.logout()
    navigate("/login")
  }

  const toggleMobileMenu = () => {
    setIsMobileMenuOpen(!isMobileMenuOpen)
  }

  const navLinks = [
    { to: "/", label: "Dashboard" },
    { to: "/buy", label: "Buy Shares" },
    { to: "/sell", label: "Sell Shares" },
    { to: "/my-investments", label: "My Investments" },
    { to: "/referrals", label: "Referrals" }
  ]

  return (
    <nav className="bg-white shadow-sm border-b border-gray-100 sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-20 items-center">
          {/* Mobile menu button */}
          <div className="flex items-center lg:hidden">
            <button
              onClick={toggleMobileMenu}
              className="inline-flex items-center justify-center p-2 rounded-md text-gray-400 hover:text-gray-500 hover:bg-gray-100 focus:outline-none focus:ring-2 focus:ring-inset focus:ring-blue-500"
            >
              <span className="sr-only">Open main menu</span>
              {isMobileMenuOpen ? (
                <X className="block h-6 w-6" aria-hidden="true" />
              ) : (
                <Menu className="block h-6 w-6" aria-hidden="true" />
              )}
            </button>
          </div>

          {/* Desktop navigation */}
          <div className="hidden lg:flex lg:space-x-16 items-center">
            {navLinks.map((link) => (
              <Link
                key={link.to}
                to={link.to}
                className="text-gray-900 hover:text-black text-base font-medium"
              >
                {link.label}
              </Link>
            ))}
            <div className="relative group flex items-center">
              <Link to="#" className="flex items-center text-gray-900 font-medium group-hover:text-blue-600">
                Account
                <ChevronDown className="ml-1 h-4 w-4" />
              </Link>

              {/* Dropdown menu */}
              <div className="absolute left-0 top-full z-10 mt-1 w-56 origin-top-right bg-white rounded-md shadow-lg ring-1 ring-black ring-opacity-5 focus:outline-none invisible opacity-0 group-hover:visible group-hover:opacity-100 transition-all duration-200">
                <div className="py-1">
                  {/* User info section */}
                  <div className="px-4 py-3">
                    <div className="flex items-center">
                      <div className="flex-shrink-0 h-10 w-10 rounded-full bg-gray-200 flex items-center justify-center">
                        {currentUser.avatar ? (
                          <img
                            src={currentUser.avatar || "/placeholder.svg"}
                            alt={currentUser.name}
                            className="h-10 w-10 rounded-full"
                          />
                        ) : (
                          <User className="h-5 w-5 text-gray-500" />
                        )}
                      </div>
                      <div className="ml-3">
                        <div className="text-sm font-medium text-gray-900">{currentUser.name}</div>
                        <div className="text-xs text-gray-500">{currentUser.email}</div>
                      </div>
                    </div>
                  </div>

                  <div className="border-t border-gray-100"></div>

                  {/* Profile link */}
                  <Link
                    to="/profile"
                    className="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 hover:text-gray-900"
                  >
                    <div className="flex items-center">
                      <User className="mr-2 h-4 w-4" />
                      Profile
                    </div>
                  </Link>

                  {/* Logout button */}
                  <button
                    onClick={onLogout}
                    className="block w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 hover:text-gray-900"
                  >
                    <div className="flex items-center">
                      <LogOut className="mr-2 h-4 w-4" />
                      Logout
                    </div>
                  </button>
                </div>
              </div>
            </div>
          </div>

          {/* Mobile menu */}
          <div
            className={`lg:hidden fixed inset-0 bg-gray-600 bg-opacity-75 transition-opacity ${
              isMobileMenuOpen ? 'opacity-100' : 'opacity-0 pointer-events-none'
            }`}
            onClick={toggleMobileMenu}
          ></div>

          <div
            className={`lg:hidden fixed inset-y-0 left-0 max-w-xs w-full bg-white shadow-xl transform transition-transform ${
              isMobileMenuOpen ? 'translate-x-0' : '-translate-x-full'
            }`}
          >
            <div className="pt-5 pb-4 px-5">
              <div className="flex items-center justify-between">
                <div className="flex-shrink-0">
                  <span className="text-xl font-bold text-gray-900">Menu</span>
                </div>
                <div className="ml-3">
                  <button
                    onClick={toggleMobileMenu}
                    className="rounded-md text-gray-400 hover:text-gray-500 focus:outline-none focus:ring-2 focus:ring-inset focus:ring-blue-500"
                  >
                    <span className="sr-only">Close menu</span>
                    <X className="h-6 w-6" aria-hidden="true" />
                  </button>
                </div>
              </div>
              <div className="mt-5">
                <nav className="space-y-1">
                  {navLinks.map((link) => (
                    <Link
                      key={link.to}
                      to={link.to}
                      className="block px-3 py-2 rounded-md text-base font-medium text-gray-700 hover:text-gray-900 hover:bg-gray-50"
                      onClick={toggleMobileMenu}
                    >
                      {link.label}
                    </Link>
                  ))}
                  <Link
                    to="/profile"
                    className="block px-3 py-2 rounded-md text-base font-medium text-gray-700 hover:text-gray-900 hover:bg-gray-50"
                    onClick={toggleMobileMenu}
                  >
                    Profile
                  </Link>
                  <button
                    onClick={() => {
                      onLogout();
                      toggleMobileMenu();
                    }}
                    className="block w-full text-left px-3 py-2 rounded-md text-base font-medium text-gray-700 hover:text-gray-900 hover:bg-gray-50"
                  >
                    Logout
                  </button>
                </nav>
              </div>
            </div>
          </div>

          {/* Avatar */}
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
