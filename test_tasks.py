import os
import django
from datetime import timedelta
from django.utils import timezone
import random
import time
from decimal import Decimal

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'referral_system.settings')
django.setup()

from accounts.models import User, Investment, Queue
from accounts.tasks import check_matured_investments, run_pairing_job

def cleanup_test_data():
    """Clean up any existing test data"""
    User.objects.filter(username__startswith='testuser').delete()
    Investment.objects.filter(user__username__startswith='testuser').delete()
    Queue.objects.filter(user__username__startswith='testuser').delete()

def create_test_data():
    # Clean up any existing test data
    cleanup_test_data()
    
    # Generate unique phone numbers
    phone1 = f"1234567{random.randint(100, 999)}"
    phone2 = f"9876543{random.randint(100, 999)}"
    
    # Create test users
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
    
    # Create a matured investment
    investment = Investment.objects.create(
        user=user1,
        amount=1000,
        maturity_period=1,
        status='pending',
        created_at=timezone.now() - timedelta(days=2)  # Created 2 days ago
    )
    
    print(f"Created test investment: {investment.id}")
    return user1, user2, investment

def test_maturity_check():
    print("\nTesting maturity check...")
    check_matured_investments()
    
    # Verify the investment was moved to queue
    queue_entries = Queue.objects.all()
    print(f"Queue entries after maturity check: {queue_entries.count()}")
    for entry in queue_entries:
        print(f"Queue entry: {entry.id}, Amount: {entry.amount_remaining}")
    
    # Verify the investment status was updated
    matured_investments = Investment.objects.filter(status='matured')
    print(f"Matured investments: {matured_investments.count()}")
    for investment in matured_investments:
        print(f"Investment {investment.id} status: {investment.status}, return_amount: {investment.return_amount}")

def test_pairing():
    print("\nTesting pairing...")
    # Create a new investment to be paired
    user1, user2, _ = create_test_data()
    
    # First, create and mature an investment
    matured_investment = Investment.objects.create(
        user=user1,
        amount=1000,
        maturity_period=1,
        status='pending',
        created_at=timezone.now() - timedelta(days=2)
    )
    
    # Calculate expected return amount
    daily_interest_rate = Decimal('0.02')
    interest_amount = matured_investment.amount * daily_interest_rate * matured_investment.maturity_period
    expected_return = matured_investment.amount + interest_amount
    
    print(f"\nCreated matured investment:")
    print(f"ID: {matured_investment.id}")
    print(f"Amount: {matured_investment.amount}")
    print(f"Expected return amount: {expected_return}")
    
    # Run maturity check
    print("\nRunning maturity check...")
    check_matured_investments()
    
    # Verify the investment was moved to queue
    queue_entries = Queue.objects.all()
    if not queue_entries.exists():
        print("Error: No queue entries found after maturity check")
        return
    
    print(f"\nQueue entries before pairing: {queue_entries.count()}")
    for entry in queue_entries:
        print(f"Queue entry: {entry.id}")
        print(f"Amount remaining: {entry.amount_remaining}")
        print(f"User: {entry.user.username}")
    
    # Create a new investment to be paired
    new_investment = Investment.objects.create(
        user=user2,
        amount=500,  # This amount should be less than or equal to the queue entry amount
        maturity_period=1,
        status='pending'
    )
    
    print(f"\nCreated new investment:")
    print(f"ID: {new_investment.id}")
    print(f"Amount: {new_investment.amount}")
    print(f"User: {new_investment.user.username}")
    
    # Run pairing job
    print("\nRunning pairing job...")
    run_pairing_job()
    
    # Verify pairing
    paired_investments = Investment.objects.filter(status='paired')
    print(f"\nPaired investments: {paired_investments.count()}")
    for investment in paired_investments:
        print(f"\nInvestment {investment.id}:")
        print(f"Amount: {investment.amount}")
        print(f"Status: {investment.status}")
        print(f"Paired to: {investment.paired_to.username}")
    
    # Verify queue entries
    remaining_queue_entries = Queue.objects.all()
    print(f"\nRemaining queue entries: {remaining_queue_entries.count()}")
    for entry in remaining_queue_entries:
        print(f"\nQueue entry {entry.id}:")
        print(f"Amount remaining: {entry.amount_remaining}")
        print(f"User: {entry.user.username}")
    
    # Verify payments
    from accounts.models import Payment
    payments = Payment.objects.all()
    print(f"\nCreated payments: {payments.count()}")
    for payment in payments:
        print(f"\nPayment {payment.id}:")
        print(f"Amount: {payment.amount}")
        print(f"From: {payment.from_user.username}")
        print(f"To: {payment.to_user.username}")
        print(f"Investment: {payment.investment.id}")

if __name__ == '__main__':
    try:
        print("Starting test...")
        test_pairing()  # Run only the pairing test which includes maturity check
        print("\nTest completed successfully!")
    except Exception as e:
        print(f"\nTest failed with error: {str(e)}")
    finally:
        # Clean up test data
        cleanup_test_data()
        print("Test data cleaned up.") 