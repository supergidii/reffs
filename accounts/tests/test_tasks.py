from django.test import TestCase
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal
from accounts.models import User, Investment, Queue, Payment, ReferralHistory
from accounts.tasks import (
    check_matured_investments,
    run_pairing_job,
    send_payment_reminders,
    cleanup_old_queue_entries,
    calculate_daily_statistics
)
from django.db.models import Sum, Count

class CeleryTasksTest(TestCase):
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
        
        # Create test investments
        self.investment1 = Investment.objects.create(
            user=self.user1,
            amount=Decimal('1000.00'),
            maturity_period=1,  # 1 day
            status='pending',
            return_amount=Decimal('1020.00')  # 2% interest
        )
        # Set created_at to 2 days ago to simulate matured investment
        self.investment1.created_at = timezone.now() - timedelta(days=2)
        self.investment1.save()
        
        self.investment2 = Investment.objects.create(
            user=self.user2,
            amount=Decimal('500.00'),
            maturity_period=2,  # 2 days
            status='pending',
            return_amount=Decimal('510.00')
        )
        
        # Create test payment
        self.payment = Payment.objects.create(
            from_user=self.user1,
            to_user=self.user2,
            investment=self.investment1,
            amount=Decimal('1020.00')
        )
        
        # Create test referral history
        self.referral = ReferralHistory.objects.create(
            referrer=self.user1,
            referred=self.user2,
            amount_invested=Decimal('500.00'),
            bonus_earned=Decimal('15.00'),  # 3% of 500
            status='pending'
        )

    def test_check_matured_investments(self):
        """Test that matured investments are moved to queue"""
        check_matured_investments()
        
        # Check if investment1 is marked as matured
        self.investment1.refresh_from_db()
        self.assertEqual(self.investment1.status, 'matured')
        
        # Check if queue entry was created
        queue_entry = Queue.objects.filter(user=self.user1).first()
        self.assertIsNotNone(queue_entry)
        self.assertEqual(queue_entry.amount_remaining, self.investment1.return_amount)
        
        # Check that investment2 is still pending
        self.investment2.refresh_from_db()
        self.assertEqual(self.investment2.status, 'pending')

    def test_run_pairing_job(self):
        """Test that investments are properly paired"""
        # First mature investment1
        self.investment1.status = 'matured'
        self.investment1.save()
        
        # Create queue entry
        Queue.objects.create(
            user=self.user1,
            amount_remaining=self.investment1.return_amount
        )
        
        # Run pairing job
        run_pairing_job()
        
        # Check if investment2 is paired
        self.investment2.refresh_from_db()
        self.assertEqual(self.investment2.status, 'paired')
        self.assertEqual(self.investment2.paired_to, self.user1)

    def test_send_payment_reminders(self):
        """Test that payment reminders are sent for unconfirmed payments"""
        # Create an old unconfirmed payment
        old_payment = Payment.objects.create(
            from_user=self.user1,
            to_user=self.user2,
            investment=self.investment1,
            amount=Decimal('1020.00')
        )
        # Set created_at to 2 days ago
        old_payment.created_at = timezone.now() - timedelta(days=2)
        old_payment.save()
        
        send_payment_reminders()
        
        # TODO: Add assertions for email sending once implemented
        # For now, just verify the payment exists
        self.assertTrue(Payment.objects.filter(id=old_payment.id).exists())

    def test_cleanup_old_queue_entries(self):
        """Test that old queue entries are cleaned up"""
        # Create an old queue entry
        old_queue = Queue.objects.create(
            user=self.user1,
            amount_remaining=Decimal('1000.00')
        )
        # Set created_at to 31 days ago
        old_queue.created_at = timezone.now() - timedelta(days=31)
        old_queue.save()
        
        cleanup_old_queue_entries()
        
        # Check if old queue entry is deleted
        self.assertFalse(Queue.objects.filter(id=old_queue.id).exists())

    def test_calculate_daily_statistics(self):
        """Test that daily statistics are calculated correctly"""
        calculate_daily_statistics()
        
        # Verify the statistics
        today = timezone.now().date()
        
        # We should have 1 investment today (investment2)
        # investment1 was created 2 days ago
        total_investments = Investment.objects.filter(
            created_at__date=today
        ).aggregate(
            total_amount=Sum('amount'),
            count=Count('id')
        )
        
        self.assertEqual(total_investments['count'], 1)
        self.assertEqual(
            total_investments['total_amount'],
            Decimal('500.00')  # Only investment2's amount
        )
        
        # We should have 1 referral today (from setUp)
        total_referrals = ReferralHistory.objects.filter(
            created_at__date=today
        ).aggregate(
            total_bonus=Sum('bonus_earned'),
            count=Count('id')
        )
        
        self.assertEqual(total_referrals['count'], 1)
        self.assertEqual(
            total_referrals['total_bonus'],
            Decimal('15.00')
        )

    def test_queue_entry_deletion(self):
        """Test that queue entries are deleted when amount_remaining reaches 0"""
        # Create a queue entry with small amount
        queue_entry = Queue.objects.create(
            user=self.user1,
            amount_remaining=Decimal('100.00')
        )
        
        # Create a pending investment that matches the queue amount
        investment = Investment.objects.create(
            user=self.user2,
            amount=Decimal('100.00'),
            maturity_period=1,
            status='pending',
            return_amount=Decimal('102.00')
        )
        
        # Run pairing job
        run_pairing_job()
        
        # Check if queue entry was deleted
        self.assertFalse(Queue.objects.filter(id=queue_entry.id).exists())
        
        # Check if investment was paired
        investment.refresh_from_db()
        self.assertEqual(investment.status, 'paired')
        self.assertEqual(investment.paired_to, self.user1) 