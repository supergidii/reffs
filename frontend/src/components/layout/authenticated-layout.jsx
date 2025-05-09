import React from 'react';
import Navbar from '../navbar';

const AuthenticatedLayout = ({ children }) => {
  return (
    <div className="min-h-screen bg-gray-50 flex flex-col">
      <Navbar />
      <main className="flex-1 container mx-auto px-4 py-8 max-w-7xl overflow-auto">
        {children}
      </main>
    </div>
  );
};

export default AuthenticatedLayout; 