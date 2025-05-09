import os
import django
from datetime import timedelta
from django.utils import timezone
from decimal import Decimal
import random

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'referral_system.settings')
django.setup()

from accounts.models import User, Investment, Queue, Payment
from accounts.tasks import run_pairing_job

def cleanup_test_data():
    """Clean up any existing test data"""
    User.objects.filter(username__startswith='testuser').delete()
    Investment.objects.filter(user__username__startswith='testuser').delete()
    Queue.objects.filter(user__username__startswith='testuser').delete()
    Payment.objects.filter(from_user__username__startswith='testuser').delete()

def create_test_users():
    """Create test users with unique phone numbers"""
    # Generate unique phone numbers
    phone1 = f"1234567{random.randint(100, 999)}"
    phone2 = f"9876543{random.randint(100, 999)}"
    
    user1 = User.objects.create_user(
        username='testuser1',
        email='test1@example.com',
        password='testpass123',
        phone_number=phone1
    )
    
    user2 = User.objects.create_user(
        username='testuser2',
        email='test2@example.com',
        password='testpass123',
        phone_number=phone2
    )
    
    return user1, user2

def create_queue_entry(user, amount):
    """Create a queue entry"""
    return Queue.objects.create(
        user=user,
        amount_remaining=amount
    )

def create_investment(user, amount):
    """Create a new investment"""
    return Investment.objects.create(
        user=user,
        amount=amount,
        maturity_period=1,
        status='pending'
    )

def test_queue_pairing():
    print("\nStarting Queue Pairing Test...")
    
    try:
        # Clean up any existing test data
        cleanup_test_data()
        
        # Create test users
        user1, user2 = create_test_users()
        print(f"Created test users: {user1.username}, {user2.username}")
        
        # Create queue entries
        queue_entry1 = create_queue_entry(user1, Decimal('1000.00'))
        queue_entry2 = create_queue_entry(user1, Decimal('500.00'))
        print(f"\nCreated queue entries:")
        print(f"Queue Entry 1: {queue_entry1.id}, Amount: {queue_entry1.amount_remaining}")
        print(f"Queue Entry 2: {queue_entry2.id}, Amount: {queue_entry2.amount_remaining}")
        
        # Create new investments
        investment1 = create_investment(user2, Decimal('300.00'))
        investment2 = create_investment(user2, Decimal('700.00'))
        print(f"\nCreated new investments:")
        print(f"Investment 1: {investment1.id}, Amount: {investment1.amount}")
        print(f"Investment 2: {investment2.id}, Amount: {investment2.amount}")
        
        # Run pairing job
        print("\nRunning pairing job...")
        run_pairing_job()
        
        # Verify results
        print("\nVerifying results...")
        
        # Check paired investments
        paired_investments = Investment.objects.filter(status='paired')
        print(f"\nPaired investments: {paired_investments.count()}")
        for investment in paired_investments:
            print(f"\nInvestment {investment.id}:")
            print(f"Amount: {investment.amount}")
            print(f"Status: {investment.status}")
            print(f"Paired to: {investment.paired_to.username}")
        
        # Check remaining queue entries
        remaining_queue = Queue.objects.all()
        print(f"\nRemaining queue entries: {remaining_queue.count()}")
        for entry in remaining_queue:
            print(f"\nQueue entry {entry.id}:")
            print(f"Amount remaining: {entry.amount_remaining}")
            print(f"User: {entry.user.username}")
        
        # Check created payments
        payments = Payment.objects.all()
        print(f"\nCreated payments: {payments.count()}")
        for payment in payments:
            print(f"\nPayment {payment.id}:")
            print(f"Amount: {payment.amount}")
            print(f"From: {payment.from_user.username}")
            print(f"To: {payment.to_user.username}")
            print(f"Investment: {payment.investment.id}")
        
    except Exception as e:
        print(f"\nTest failed with error: {str(e)}")
    finally:
        # Clean up test data
        cleanup_test_data()
        print("\nTest data cleaned up.")

if __name__ == '__main__':
    test_queue_pairing() 