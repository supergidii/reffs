import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './contexts/AuthContext';
// import Navbar from './components/navbar';
import Login from './components/auth/login';
import Register from './components/auth/register';
import Dashboard from './components/dashboard';
import MyInvestments from './components/my-investments';
import BuyShares from './components/buy-shares';
import SellShares from './components/sell-shares';
import Referrals from './components/referrals';
import Account from './components/account';

// Protected Route component
const ProtectedRoute = ({ children }) => {
    const { user, loading } = useAuth();
    
    if (loading) {
        return <div>Loading...</div>;
    }
    
    if (!user) {
        return <Navigate to="/login" />;
    }
    
    return children;
};

function App() {
    return (
        <AuthProvider>
            <Router>
                <div className="min-h-screen bg-gray-100">
                    {/* <Navbar /> Removed global navbar */}
                    <main className="container mx-auto px-4 py-8">
                        <Routes>
                            <Route path="/login" element={<Login />} />
                            <Route path="/register" element={<Register />} />
                            <Route 
                                path="/" 
                                element={
                                    <ProtectedRoute>
                                        <Dashboard />
                                    </ProtectedRoute>
                                } 
                            />
                            <Route 
                                path="/my-investments" 
                                element={
                                    <ProtectedRoute>
                                        <MyInvestments />
                                    </ProtectedRoute>
                                } 
                            />
                            <Route 
                                path="/buy-shares" 
                                element={
                                    <ProtectedRoute>
                                        <BuyShares />
                                    </ProtectedRoute>
                                } 
                            />
                            <Route 
                                path="/sell-shares" 
                                element={
                                    <ProtectedRoute>
                                        <SellShares />
                                    </ProtectedRoute>
                                } 
                            />
                            <Route 
                                path="/referrals" 
                                element={
                                    <ProtectedRoute>
                                        <Referrals />
                                    </ProtectedRoute>
                                } 
                            />
                            <Route 
                                path="/account" 
                                element={
                                    <ProtectedRoute>
                                        <Account />
                                    </ProtectedRoute>
                                } 
                            />
                        </Routes>
                    </main>
                </div>
            </Router>
        </AuthProvider>
    );
}

export default App; 