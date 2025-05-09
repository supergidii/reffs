from django.test import TestCase
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal
from accounts.models import User, Investment, Queue, Payment
from accounts.tasks import run_pairing_job
import logging

logger = logging.getLogger(__name__)

class PairingJobTest(TestCase):
    def setUp(self):
        # Create test users
        self.user1 = User.objects.create_user(
            username='testuser1',
            email='test1@example.com',
            phone_number='1234567890',
            password='testpass123'
        )
        self.user2 = User.objects.create_user(
            username='testuser2',
            email='test2@example.com',
            phone_number='0987654321',
            password='testpass123'
        )
        self.user3 = User.objects.create_user(
            username='testuser3',
            email='test3@example.com',
            phone_number='1122334455',
            password='testpass123'
        )
        self.user4 = User.objects.create_user(
            username='testuser4',
            email='test4@example.com',
            phone_number='2233445566',
            password='testpass123'
        )
        
        # Create admin user
        self.admin_user = User.objects.create_user(
            username='admin',
            email='admin@example.com',
            phone_number='9999999999',
            password='adminpass123',
            is_staff=True
        )

    def test_full_match(self):
        """Test when new investment fully matches with matured investment"""
        # Create matured investment
        matured_investment = Investment.objects.create(
            user=self.user1,
            amount=Decimal('1000.00'),
            maturity_period=1,
            status='matured',
            return_amount=Decimal('1020.00')
        )
        
        # Create queue entry
        queue_entry = Queue.objects.create(
            user=self.user1,
            amount_remaining=Decimal('1000.00')
        )
        
        # Create new investment
        new_investment = Investment.objects.create(
            user=self.user2,
            amount=Decimal('1000.00'),
            maturity_period=1,
            status='pending',
            return_amount=Decimal('1020.00')
        )
        
        # Run pairing job
        run_pairing_job()
        
        # Check results
        new_investment.refresh_from_db()
        self.assertEqual(new_investment.status, 'paired')
        self.assertEqual(new_investment.paired_to, self.user1)
        
        # Check payment record
        payment = Payment.objects.filter(
            from_user=self.user2,
            to_user=self.user1,
            investment=new_investment
        ).first()
        self.assertIsNotNone(payment)
        self.assertEqual(payment.amount, Decimal('1000.00'))
        
        # Check queue entry is deleted
        self.assertFalse(Queue.objects.filter(id=queue_entry.id).exists())

    def test_multiple_matches(self):
        """Test when new investment matches with multiple matured investments"""
        # Create multiple matured investments
        matured1 = Investment.objects.create(
            user=self.user1,
            amount=Decimal('1000.00'),
            maturity_period=1,
            status='matured',
            return_amount=Decimal('1020.00')
        )
        matured2 = Investment.objects.create(
            user=self.user2,
            amount=Decimal('2000.00'),
            maturity_period=1,
            status='matured',
            return_amount=Decimal('2040.00')
        )
        
        # Create queue entries
        queue1 = Queue.objects.create(
            user=self.user1,
            amount_remaining=Decimal('1000.00')
        )
        queue2 = Queue.objects.create(
            user=self.user2,
            amount_remaining=Decimal('2000.00')
        )
        
        # Create new investment
        new_investment = Investment.objects.create(
            user=self.user3,
            amount=Decimal('3000.00'),
            maturity_period=1,
            status='pending',
            return_amount=Decimal('3060.00')
        )
        
        # Run pairing job
        run_pairing_job()
        
        # Check results
        new_investment.refresh_from_db()
        self.assertEqual(new_investment.status, 'paired')
        
        # Check payment records
        payments = Payment.objects.filter(
            from_user=self.user3,
            investment=new_investment
        )
        self.assertEqual(payments.count(), 2)
        
        # Verify payment amounts
        payment_amounts = [p.amount for p in payments]
        self.assertIn(Decimal('1000.00'), payment_amounts)
        self.assertIn(Decimal('2000.00'), payment_amounts)
        
        # Check queue entries are deleted
        self.assertFalse(Queue.objects.filter(id__in=[queue1.id, queue2.id]).exists())

    def test_one_matured_to_multiple_new(self):
        """Test when one matured investment is matched with multiple new investments"""
        # Create matured investment
        matured_investment = Investment.objects.create(
            user=self.user1,
            amount=Decimal('5000.00'),
            maturity_period=1,
            status='matured',
            return_amount=Decimal('5100.00')
        )
        
        # Create queue entry
        queue_entry = Queue.objects.create(
            user=self.user1,
            amount_remaining=Decimal('5000.00')
        )
        
        # Create multiple new investments
        new_investment1 = Investment.objects.create(
            user=self.user2,
            amount=Decimal('2000.00'),
            maturity_period=1,
            status='pending',
            return_amount=Decimal('2040.00')
        )
        new_investment2 = Investment.objects.create(
            user=self.user3,
            amount=Decimal('1500.00'),
            maturity_period=1,
            status='pending',
            return_amount=Decimal('1530.00')
        )
        new_investment3 = Investment.objects.create(
            user=self.user4,
            amount=Decimal('1500.00'),
            maturity_period=1,
            status='pending',
            return_amount=Decimal('1530.00')
        )
        
        # Run pairing job
        run_pairing_job()
        
        # Check results
        new_investment1.refresh_from_db()
        new_investment2.refresh_from_db()
        new_investment3.refresh_from_db()
        
        # All investments should be paired
        self.assertEqual(new_investment1.status, 'paired')
        self.assertEqual(new_investment2.status, 'paired')
        self.assertEqual(new_investment3.status, 'paired')
        
        # Check payment records
        payments = Payment.objects.filter(
            to_user=self.user1
        )
        self.assertEqual(payments.count(), 3)
        
        # Verify payment amounts
        payment_amounts = [p.amount for p in payments]
        self.assertIn(Decimal('2000.00'), payment_amounts)
        self.assertIn(Decimal('1500.00'), payment_amounts)
        self.assertIn(Decimal('1500.00'), payment_amounts)
        
        # Check queue entry is deleted
        self.assertFalse(Queue.objects.filter(id=queue_entry.id).exists())

    def test_no_matches(self):
        """Test when no matches are available"""
        # Create new investment
        new_investment = Investment.objects.create(
            user=self.user1,
            amount=Decimal('1000.00'),
            maturity_period=1,
            status='pending',
            return_amount=Decimal('1020.00')
        )
        
        # Run pairing job
        run_pairing_job()
        
        # Check investment remains pending
        new_investment.refresh_from_db()
        self.assertEqual(new_investment.status, 'pending')
        self.assertEqual(new_investment.amount, Decimal('1000.00')) 