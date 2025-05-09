import React from 'react';
import { useAuth } from '../contexts/AuthContext';
import { Card, CardHeader, CardTitle, CardContent } from './ui/card';

const Account = () => {
    const { user } = useAuth();

    return (
        <div className="container mx-auto px-4 py-8">
            <h1 className="text-3xl font-bold mb-8">My Account</h1>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <Card>
                    <CardHeader>
                        <CardTitle>Profile Information</CardTitle>
                    </CardHeader>
                    <CardContent>
                        <div className="space-y-4">
                            <div>
                                <label className="block text-sm font-medium text-gray-700">Username</label>
                                <p className="mt-1 text-lg">{user?.username}</p>
                            </div>
                            <div>
                                <label className="block text-sm font-medium text-gray-700">Email</label>
                                <p className="mt-1 text-lg">{user?.email}</p>
                            </div>
                            <div>
                                <label className="block text-sm font-medium text-gray-700">Phone Number</label>
                                <p className="mt-1 text-lg">{user?.phone_number}</p>
                            </div>
                            <div>
                                <label className="block text-sm font-medium text-gray-700">Referral Code</label>
                                <p className="mt-1 text-lg">{user?.referral_code}</p>
                            </div>
                        </div>
                    </CardContent>
                </Card>

                <Card>
                    <CardHeader>
                        <CardTitle>Referral Statistics</CardTitle>
                    </CardHeader>
                    <CardContent>
                        <div className="space-y-4">
                            <div>
                                <label className="block text-sm font-medium text-gray-700">Total Referral Earnings</label>
                                <p className="mt-1 text-lg">${user?.referral_earnings || 0}</p>
                            </div>
                            <div>
                                <label className="block text-sm font-medium text-gray-700">Total Referrals</label>
                                <p className="mt-1 text-lg">{user?.total_referrals || 0}</p>
                            </div>
                        </div>
                    </CardContent>
                </Card>
            </div>
        </div>
    );
};

export default Account; 