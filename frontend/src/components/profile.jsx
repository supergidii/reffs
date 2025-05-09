import { Link, useNavigate } from "react-router-dom"
import { ArrowLeft, Mail, Phone, User, LogOut, CreditCard, Calendar, DollarSign, Users } from "lucide-react"
import AuthenticatedLayout from "./layout/authenticated-layout"
import { authService } from "../services/api"

const Profile = () => {
  const navigate = useNavigate()
  // This would typically come from a database or authentication service
  const user = {
    name: "John Doe",
    email: "john.doe@example.com",
    phone: "+254 721123456",
    username: "johndoe",
    joinDate: "April 15, 2023",
    totalInvestment: "Ksh 75,000",
    totalReturns: "Ksh 50,000",
    referralEarnings: "Ksh 5,000",
    accountNumber: "ACC123456789",
    referralCode: "REF123456",
    activeInvestments: 3,
    completedInvestments: 5,
    totalReferrals: 8
  }

  const handleLogout = () => {
    authService.logout()
    navigate("/login")
  }

  return (
    <AuthenticatedLayout>
      <div className="max-w-4xl mx-auto">
        <div className="mb-6">
          <Link to="/dashboard" className="inline-flex items-center text-sm text-gray-600 hover:text-gray-900 mb-4">
            <ArrowLeft className="mr-2 h-4 w-4" />
            Back to Dashboard
          </Link>
          <h1 className="text-2xl font-bold">My Profile</h1>
          <p className="text-gray-500">View and manage your account details</p>
        </div>

        <div className="grid gap-6 md:grid-cols-2">
          {/* Personal Information Card */}
          <div className="bg-white rounded-lg shadow-sm border p-6">
            <div className="mb-4">
              <h2 className="text-lg font-semibold">Personal Information</h2>
              <p className="text-sm text-gray-500">Your personal details and contact information</p>
            </div>

            <div className="flex items-center space-x-4 mb-6">
              <div className="h-16 w-16 rounded-full bg-blue-100 flex items-center justify-center text-blue-600 text-xl font-medium">
                {user.name
                  .split(" ")
                  .map((n) => n[0])
                  .join("")}
              </div>
              <div>
                <h3 className="font-medium text-lg">{user.name}</h3>
                <p className="text-gray-500">Member since {user.joinDate}</p>
              </div>
            </div>

            <div className="space-y-4">
              <div className="flex items-center">
                <User className="h-4 w-4 mr-2 text-gray-400" />
                <span>Username: {user.username}</span>
              </div>
              <div className="flex items-center">
                <Mail className="h-4 w-4 mr-2 text-gray-400" />
                <span>{user.email}</span>
              </div>
              <div className="flex items-center">
                <Phone className="h-4 w-4 mr-2 text-gray-400" />
                <span>{user.phone}</span>
              </div>
              <div className="flex items-center">
                <CreditCard className="h-4 w-4 mr-2 text-gray-400" />
                <span>Account: {user.accountNumber}</span>
              </div>
              <div className="flex items-center">
                <Users className="h-4 w-4 mr-2 text-gray-400" />
                <span>Referral Code: {user.referralCode}</span>
              </div>
            </div>

            <div className="h-px bg-gray-200 my-6"></div>

            <div className="space-y-4">
              <button 
                onClick={handleLogout}
                className="w-full py-2 px-4 bg-red-600 hover:bg-red-700 text-white font-medium rounded-md flex items-center justify-center"
              >
                <LogOut className="mr-2 h-4 w-4" />
                Logout
              </button>
            </div>
          </div>

          {/* Investment Summary Card */}
          <div className="bg-white rounded-lg shadow-sm border p-6">
            <div className="mb-4">
              <h2 className="text-lg font-semibold">Investment Summary</h2>
              <p className="text-sm text-gray-500">Overview of your investments and earnings</p>
            </div>

            <div className="space-y-4">
              <div className="flex justify-between items-center">
                <span className="text-gray-500">Total Investment</span>
                <span className="font-medium">{user.totalInvestment}</span>
              </div>
              <div className="h-px bg-gray-200"></div>
              <div className="flex justify-between items-center">
                <span className="text-gray-500">Total Returns</span>
                <span className="font-medium text-green-600">{user.totalReturns}</span>
              </div>
              <div className="h-px bg-gray-200"></div>
              <div className="flex justify-between items-center">
                <span className="text-gray-500">Referral Earnings</span>
                <span className="font-medium">{user.referralEarnings}</span>
              </div>
              <div className="h-px bg-gray-200"></div>
              <div className="flex justify-between items-center">
                <span className="text-gray-500">Active Investments</span>
                <span className="font-medium">{user.activeInvestments}</span>
              </div>
              <div className="h-px bg-gray-200"></div>
              <div className="flex justify-between items-center">
                <span className="text-gray-500">Completed Investments</span>
                <span className="font-medium">{user.completedInvestments}</span>
              </div>
              <div className="h-px bg-gray-200"></div>
              <div className="flex justify-between items-center">
                <span className="text-gray-500">Total Referrals</span>
                <span className="font-medium">{user.totalReferrals}</span>
              </div>
            </div>

            <div className="mt-6 p-4 bg-blue-50 rounded-lg border border-blue-100">
              <h4 className="font-medium text-blue-800 mb-2">Investment Growth</h4>
              <div className="w-full bg-gray-200 rounded-full h-2.5">
                <div className="bg-blue-600 h-2.5 rounded-full" style={{ width: "66%" }}></div>
              </div>
              <p className="text-sm text-blue-700 mt-2">Your investments have grown by 66% since you joined</p>
            </div>
          </div>
        </div>
      </div>
    </AuthenticatedLayout>
  )
}

export default Profile
