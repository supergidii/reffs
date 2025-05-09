import React, { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import axios from 'axios';
import {
    Box,
    Grid,
    Heading,
    Text,
    Stat,
    StatLabel,
    StatNumber,
    StatHelpText,
    Table,
    Thead,
    Tbody,
    Tr,
    Th,
    Td,
    Button,
    useToast,
    Input,
    InputGroup,
    InputRightElement,
    VStack,
    HStack,
    Badge,
    Card,
    CardBody,
    Alert,
    AlertIcon,
    AlertTitle,
    AlertDescription,
    Spinner,
    Center,
} from '@chakra-ui/react';
import { CopyIcon } from '@chakra-ui/icons';

const Dashboard = () => {
    const [dashboardData, setDashboardData] = useState(null);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState(null);
    const { token } = useAuth();
    const toast = useToast();

    const fetchDashboardData = async () => {
        try {
            setError(null);
            console.log('Fetching dashboard data...');
            const response = await axios.get('/api/user-dashboard/', {
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json',
                },
                baseURL: process.env.REACT_APP_API_URL || 'http://localhost:8000',
            });
            console.log('Dashboard data received:', response.data);
            setDashboardData(response.data);
        } catch (error) {
            console.error('Dashboard data fetch error:', error);
            const errorMessage = error.response?.data?.error || error.message || 'Failed to fetch dashboard data';
            setError(errorMessage);
            toast({
                title: 'Error',
                description: errorMessage,
                status: 'error',
                duration: 5000,
                isClosable: true,
            });
        } finally {
            setIsLoading(false);
        }
    };

    useEffect(() => {
        if (!token) {
            setError('Authentication token not found');
            setIsLoading(false);
            return;
        }
        fetchDashboardData();
        const interval = setInterval(fetchDashboardData, 60000); // Refresh every minute
        return () => clearInterval(interval);
    }, [token]);

    const copyReferralLink = () => {
        if (!dashboardData?.referral_link) {
            toast({
                title: 'Error',
                description: 'Referral link not available',
                status: 'error',
                duration: 2000,
                isClosable: true,
            });
            return;
        }
        navigator.clipboard.writeText(dashboardData.referral_link);
        toast({
            title: 'Success',
            description: 'Referral link copied to clipboard',
            status: 'success',
            duration: 2000,
            isClosable: true,
        });
    };

    if (isLoading) {
        return (
            <Center h="100vh">
                <VStack spacing={4}>
                    <Spinner size="xl" />
                    <Text>Loading dashboard data...</Text>
                </VStack>
            </Center>
        );
    }

    if (error) {
        return (
            <Box p={4}>
                <Alert status="error">
                    <AlertIcon />
                    <AlertTitle>Error loading dashboard</AlertTitle>
                    <AlertDescription>{error}</AlertDescription>
                </Alert>
                <Button mt={4} onClick={fetchDashboardData}>
                    Retry
                </Button>
            </Box>
        );
    }

    if (!dashboardData) {
        return (
            <Box p={4}>
                <Alert status="warning">
                    <AlertIcon />
                    <AlertTitle>No Data Available</AlertTitle>
                    <AlertDescription>Unable to load dashboard data. Please try again later.</AlertDescription>
                </Alert>
                <Button mt={4} onClick={fetchDashboardData}>
                    Retry
                </Button>
            </Box>
        );
    }

    return (
        <Box p={4}>
            <VStack spacing={6} align="stretch">
                {/* Stats Grid */}
                <Grid templateColumns={{ base: '1fr', md: 'repeat(4, 1fr)' }} gap={4}>
                    <Card>
                        <CardBody>
                            <Stat>
                                <StatLabel>Total Returns</StatLabel>
                                <StatNumber>${dashboardData.total_returns || 0}</StatNumber>
                            </Stat>
                        </CardBody>
                    </Card>
                    <Card>
                        <CardBody>
                            <Stat>
                                <StatLabel>Referral Earnings</StatLabel>
                                <StatNumber>${dashboardData.total_referral_earnings || 0}</StatNumber>
                            </Stat>
                        </CardBody>
                    </Card>
                    <Card>
                        <CardBody>
                            <Stat>
                                <StatLabel>Queue Position</StatLabel>
                                <StatNumber>{dashboardData.queue_position || 0}</StatNumber>
                                <StatHelpText>Matured investments</StatHelpText>
                            </Stat>
                        </CardBody>
                    </Card>
                    <Card>
                        <CardBody>
                            <Stat>
                                <StatLabel>Next Bidding Window</StatLabel>
                                <StatNumber>
                                    {dashboardData.next_bidding_window?.start ? 
                                        new Date(dashboardData.next_bidding_window.start).toLocaleTimeString() :
                                        'Not available'}
                                </StatNumber>
                                <StatHelpText>
                                    {dashboardData.next_bidding_window?.window === 'morning' ? 'Morning' : 'Evening'} Window
                                </StatHelpText>
                            </Stat>
                        </CardBody>
                    </Card>
                </Grid>

                {/* Referral Link */}
                <Card>
                    <CardBody>
                        <VStack align="stretch" spacing={4}>
                            <Heading size="md">Your Referral Link</Heading>
                            <InputGroup>
                                <Input
                                    value={dashboardData.referral_link || ''}
                                    isReadOnly
                                    placeholder="Referral link not available"
                                />
                                <InputRightElement>
                                    <Button 
                                        onClick={copyReferralLink}
                                        isDisabled={!dashboardData.referral_link}
                                    >
                                        <CopyIcon />
                                    </Button>
                                </InputRightElement>
                            </InputGroup>
                        </VStack>
                    </CardBody>
                </Card>

                {/* Active Investments */}
                <Card>
                    <CardBody>
                        <VStack align="stretch" spacing={4}>
                            <Heading size="md">Active Investments</Heading>
                            {dashboardData.active_investments?.length > 0 ? (
                                <Table variant="simple">
                                    <Thead>
                                        <Tr>
                                            <Th>Amount</Th>
                                            <Th>Return Amount</Th>
                                            <Th>Status</Th>
                                            <Th>Created</Th>
                                        </Tr>
                                    </Thead>
                                    <Tbody>
                                        {dashboardData.active_investments.map((investment) => (
                                            <Tr key={investment.id}>
                                                <Td>${investment.amount}</Td>
                                                <Td>${investment.return_amount}</Td>
                                                <Td>
                                                    <Badge
                                                        colorScheme={
                                                            investment.status === 'pending' ? 'yellow' :
                                                            investment.status === 'paired' ? 'green' : 'blue'
                                                        }
                                                    >
                                                        {investment.status}
                                                    </Badge>
                                                </Td>
                                                <Td>{new Date(investment.created_at).toLocaleDateString()}</Td>
                                            </Tr>
                                        ))}
                                    </Tbody>
                                </Table>
                            ) : (
                                <Text>No active investments found</Text>
                            )}
                        </VStack>
                    </CardBody>
                </Card>

                {/* Pending Payments */}
                <Card>
                    <CardBody>
                        <VStack align="stretch" spacing={4}>
                            <Heading size="md">Pending Payments</Heading>
                            {dashboardData.pending_payments?.length > 0 ? (
                                <Table variant="simple">
                                    <Thead>
                                        <Tr>
                                            <Th>Amount</Th>
                                            <Th>From User</Th>
                                            <Th>Created</Th>
                                            <Th>Action</Th>
                                        </Tr>
                                    </Thead>
                                    <Tbody>
                                        {dashboardData.pending_payments.map((payment) => (
                                            <Tr key={payment.id}>
                                                <Td>${payment.amount}</Td>
                                                <Td>{payment.user}</Td>
                                                <Td>{new Date(payment.created_at).toLocaleDateString()}</Td>
                                                <Td>
                                                    <Button
                                                        size="sm"
                                                        colorScheme="green"
                                                        onClick={() => handleConfirmPayment(payment.id)}
                                                    >
                                                        Confirm
                                                    </Button>
                                                </Td>
                                            </Tr>
                                        ))}
                                    </Tbody>
                                </Table>
                            ) : (
                                <Text>No pending payments found</Text>
                            )}
                        </VStack>
                    </CardBody>
                </Card>
            </VStack>
        </Box>
    );
};

export default Dashboard; 