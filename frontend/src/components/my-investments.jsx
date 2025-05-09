import React, { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { Card, CardHeader, CardTitle, CardContent } from './ui/card';
import { Table, TableHeader, TableBody, TableRow, TableHead, TableCell } from './ui/table';
import { Badge } from './ui/badge';
import axios from 'axios';
import { Button } from './ui/button';
import { Download } from 'lucide-react';

const MyInvestments = () => {
    const { user } = useAuth();
    const [investments, setInvestments] = useState([]);
    const [stats, setStats] = useState({
        totalInvested: 0,
        totalReturns: 0,
        activeInvestments: 0,
        maturedInvestments: 0
    });
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        const fetchInvestments = async () => {
            try {
                const response = await axios.get('/api/investments/', {
                    headers: {
                        'Authorization': `Bearer ${localStorage.getItem('token')}`
                    }
                });
                setInvestments(response.data);
                
                // Calculate statistics
                const totalInvested = response.data.reduce((sum, inv) => sum + parseFloat(inv.amount), 0);
                const totalReturns = response.data.reduce((sum, inv) => sum + parseFloat(inv.return_amount), 0);
                const activeInvestments = response.data.filter(inv => inv.status === 'pending').length;
                const maturedInvestments = response.data.filter(inv => inv.status === 'matured').length;

                setStats({
                    totalInvested,
                    totalReturns,
                    activeInvestments,
                    maturedInvestments
                });
            } catch (err) {
                setError('Failed to fetch investments');
                console.error('Error fetching investments:', err);
            } finally {
                setLoading(false);
            }
        };

        fetchInvestments();
    }, []);

    const getStatusBadge = (status) => {
        const statusConfig = {
            pending: { color: 'bg-yellow-500', text: 'Pending' },
            matured: { color: 'bg-green-500', text: 'Matured' },
            paired: { color: 'bg-blue-500', text: 'Paired' },
            completed: { color: 'bg-purple-500', text: 'Completed' }
        };

        const config = statusConfig[status] || { color: 'bg-gray-500', text: status };
        return (
            <Badge className={`${config.color} text-white`}>
                {config.text}
            </Badge>
        );
    };

    const downloadStatement = async (investmentId) => {
        try {
            const response = await axios.get(`/api/investments/${investmentId}/statement/`, {
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('token')}`
                },
                responseType: 'blob'
            });
            
            const url = window.URL.createObjectURL(new Blob([response.data]));
            const link = document.createElement('a');
            link.href = url;
            link.setAttribute('download', `investment_statement_${investmentId}.pdf`);
            document.body.appendChild(link);
            link.click();
            link.remove();
        } catch (err) {
            console.error('Error downloading statement:', err);
        }
    };

    if (loading) {
        return (
            <div className="flex items-center justify-center min-h-screen">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
            </div>
        );
    }

    if (error) {
        return (
            <div className="flex items-center justify-center min-h-screen">
                <div className="text-red-500">{error}</div>
            </div>
        );
    }

    return (
        <div className="container mx-auto px-4 py-8">
            <h1 className="text-3xl font-bold mb-8">My Investments</h1>

            {/* Statistics Cards */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
                <Card>
                    <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                        <CardTitle className="text-sm font-medium">Total Invested</CardTitle>
                    </CardHeader>
                    <CardContent>
                        <div className="text-2xl font-bold">${stats.totalInvested.toFixed(2)}</div>
                    </CardContent>
                </Card>

                <Card>
                    <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                        <CardTitle className="text-sm font-medium">Total Returns</CardTitle>
                    </CardHeader>
                    <CardContent>
                        <div className="text-2xl font-bold">${stats.totalReturns.toFixed(2)}</div>
                    </CardContent>
                </Card>

                <Card>
                    <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                        <CardTitle className="text-sm font-medium">Active Investments</CardTitle>
                    </CardHeader>
                    <CardContent>
                        <div className="text-2xl font-bold">{stats.activeInvestments}</div>
                    </CardContent>
                </Card>

                <Card>
                    <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                        <CardTitle className="text-sm font-medium">Matured Investments</CardTitle>
                    </CardHeader>
                    <CardContent>
                        <div className="text-2xl font-bold">{stats.maturedInvestments}</div>
                    </CardContent>
                </Card>
            </div>

            {/* Investments Table */}
            <Card>
                <CardHeader>
                    <CardTitle>Investment History</CardTitle>
                </CardHeader>
                <CardContent>
                    <Table>
                        <TableHeader>
                            <TableRow>
                                <TableHead>Date</TableHead>
                                <TableHead>Amount</TableHead>
                                <TableHead>Return Amount</TableHead>
                                <TableHead>Maturity Period</TableHead>
                                <TableHead>Status</TableHead>
                                <TableHead>Actions</TableHead>
                            </TableRow>
                        </TableHeader>
                        <TableBody>
                            {investments.length > 0 ? (
                                investments.map((investment) => (
                                    <TableRow key={investment.id}>
                                        <TableCell>
                                            {new Date(investment.created_at).toLocaleDateString()}
                                        </TableCell>
                                        <TableCell>${parseFloat(investment.amount).toFixed(2)}</TableCell>
                                        <TableCell>${parseFloat(investment.return_amount).toFixed(2)}</TableCell>
                                        <TableCell>{investment.maturity_period} days</TableCell>
                                        <TableCell>{getStatusBadge(investment.status)}</TableCell>
                                        <TableCell>
                                            <Button
                                                variant="outline"
                                                size="sm"
                                                onClick={() => downloadStatement(investment.id)}
                                            >
                                                <Download className="h-4 w-4 mr-2" />
                                                Statement
                                            </Button>
                                        </TableCell>
                                    </TableRow>
                                ))
                            ) : (
                                <TableRow>
                                    <TableCell colSpan={6} className="text-center">
                                        No investments found
                                    </TableCell>
                                </TableRow>
                            )}
                        </TableBody>
                    </Table>
                </CardContent>
            </Card>
        </div>
    );
};

export default MyInvestments; 