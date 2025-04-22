import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import Layout from './components/app/layout';
import Dashboard from './components/dashboard';
import BuyShares from './components/buy-shares';
import SellShares from './components/sell-shares';
import Register from './components/auth/register';
import Login from './components/auth/login';
import { authService } from './services/api';

// Protected Route wrapper
const ProtectedRoute = ({ children }) => {
  const isAuthenticated = authService.isAuthenticated();
  
  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }
  
  return children;
};

const App = () => {
  return (
    <Router>
      <Routes>
        {/* Start by testing only the simplest routes */}
        <Route path="/register" element={<Register />} /> 
        <Route path="/login" element={<Login />} />
        
        
        <Route
          path="/"
          element={
            <ProtectedRoute>
              <Layout>
                <Dashboard />
              </Layout>
            </ProtectedRoute>
          }
        />
        <Route
          path="/buy"
          element={
            <ProtectedRoute>
              <Layout>
                <BuyShares />
              </Layout>
            </ProtectedRoute>
          }
        />
        <Route
          path="/sell"
          element={
            <ProtectedRoute>
              <Layout>
                <SellShares />
              </Layout>
            </ProtectedRoute>
          }
        />
        <Route path="*" element={<Navigate to="/" replace />} /> 
        
      </Routes>
    </Router>
  );
};

export default App; 