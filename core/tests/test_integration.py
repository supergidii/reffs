from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal
from accounts.models import Investment, Queue, ReferralHistory
from accounts.models import User

User = get_user_model()

class IntegrationTest(TestCase):
    def setUp(self):
        # Create 10 users
        self.users = []
        for i in range(10):
            user = User.objects.create_user(
                username=f'user{i}',
                email=f'user{i}@example.com',
                phone_number=f'123456789{i}',
                password='testpass123'
            )
            self.users.append(user)
        
        # Set up referral chain: user0 -> user1 -> user2 -> user3
        self.users[1].referred_by = self.users[0]
        self.users[1].save()
        self.users[2].referred_by = self.users[1]
        self.users[2].save()
        self.users[3].referred_by = self.users[2]
        self.users[3].save()

    def test_referral_chain(self):
        """Test that referral chain is properly set up"""
        self.assertEqual(self.users[1].referred_by, self.users[0])
        self.assertEqual(self.users[2].referred_by, self.users[1])
        self.assertEqual(self.users[3].referred_by, self.users[2])

    def test_investment_with_referral(self):
        """Test investment with referral bonus"""
        # User3 invests $1000
        investment = Investment.objects.create(
            user=self.users[3],
            amount=Decimal('1000.00'),
            maturity_period=30,
            status='pending'
        )
        
        # Refresh user objects from database
        self.users[0].refresh_from_db()
        self.users[1].refresh_from_db()
        self.users[2].refresh_from_db()
        
        # Each referrer in the chain gets 3% bonus
        self.assertEqual(self.users[2].referral_earnings, Decimal('30.00'))  # Direct referrer
        self.assertEqual(self.users[1].referral_earnings, Decimal('30.00'))  # Second level
        self.assertEqual(self.users[0].referral_earnings, Decimal('30.00'))  # Third level

    def test_multiple_investments(self):
        """Test multiple users making investments"""
        # Create investments for users 4-9
        investments = []
        for i in range(4, 10):
            investment = Investment.objects.create(
                user=self.users[i],
                amount=Decimal('500.00'),
                maturity_period=30,
                status='pending'
            )
            investments.append(investment)

        # Verify all investments were created
        self.assertEqual(Investment.objects.count(), 6)

    def test_investment_maturity(self):
        """Test investment maturity and queue placement"""
        # Create an investment
        investment = Investment.objects.create(
            user=self.users[4],
            amount=Decimal('1000.00'),
            maturity_period=1,  # 1 day for testing
            status='pending'
        )
        
        # Simulate maturity by updating created_at and status
        investment.created_at = timezone.now() - timedelta(days=2)
        investment.status = 'matured'
        investment.save()
        
        # Verify investment is matured and return amount is calculated
        investment.refresh_from_db()
        self.assertEqual(investment.status, 'matured')
        self.assertIsNotNone(investment.return_amount)
        
        # Create queue entry
        queue = Queue.objects.create(
            user=self.users[4],
            amount_remaining=investment.return_amount,
            created_at=timezone.now()
        )
        
        # Verify queue entry
        self.assertTrue(Queue.objects.filter(user=self.users[4]).exists())

    def test_payment_confirmation(self):
        """Test payment confirmation flow"""
        # Create matured investment for user5
        investment = Investment.objects.create(
            user=self.users[5],
            amount=Decimal('1000.00'),
            maturity_period=1,
            status='matured'
        )
        
        # Create queue entry
        queue = Queue.objects.create(
            user=self.users[5],
            amount_remaining=investment.return_amount,
            created_at=timezone.now()
        )
        
        # Simulate payment confirmation
        investment.is_confirmed = True
        investment.save()
        
        # Verify investment status
        investment.refresh_from_db()
        self.assertTrue(investment.is_confirmed)

    def test_referral_history(self):
        """Test referral history tracking"""
        # Set up referral chain for user6
        self.users[6].referred_by = self.users[5]
        self.users[6].save()
        
        # User6 invests $2000
        investment = Investment.objects.create(
            user=self.users[6],
            amount=Decimal('2000.00'),
            maturity_period=30,
            status='pending'
        )
        
        # Verify referral history entry
        self.assertEqual(ReferralHistory.objects.count(), 1)
        history = ReferralHistory.objects.first()
        self.assertEqual(history.amount_invested, Decimal('2000.00'))
        self.assertEqual(history.bonus_earned, Decimal('60.00'))  # 3% of 2000
        self.assertEqual(history.referrer, self.users[5])  # Direct referrer 