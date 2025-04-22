import os
import django
from datetime import datetime, timedelta
from decimal import Decimal

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ref.settings')
django.setup()

from accounts.models import User, Investment, Queue, ReferralHistory
from accounts.tasks import (
    process_referral_bonus,
    send_maturity_notification,
    process_investment_matching,
    check_matured_investments
)

def create_test_data():
    """Create test data for Celery tasks"""
    print("Creating test data...")
    
    # Create test users
    referrer = User.objects.create(
        username="test_referrer",
        email="referrer@test.com",
        phone_number="1234567890",
        referral_code="TEST123"
    )
    
    investor = User.objects.create(
        username="test_investor",
        email="investor@test.com",
        phone_number="0987654321",
        referral_code="TEST456",
        referred_by=referrer
    )
    
    # Create test investment
    investment = Investment.objects.create(
        user=investor,
        amount=Decimal("1000.00"),
        maturity_period=30,
        status="pending",
        return_amount=Decimal("1600.00")  # 1000 + 2% daily interest
    )
    
    print(f"Created test investment: {investment.id}")
    return investment

def test_tasks():
    """Test Celery tasks"""
    print("\nTesting Celery tasks...")
    
    # Create test data
    investment = create_test_data()
    
    # Test process_referral_bonus
    print("\nTesting process_referral_bonus...")
    result = process_referral_bonus.delay(investment.id)
    print(f"Task ID: {result.id}")
    
    # Test send_maturity_notification
    print("\nTesting send_maturity_notification...")
    result = send_maturity_notification.delay(investment.id)
    print(f"Task ID: {result.id}")
    
    # Test check_matured_investments
    print("\nTesting check_matured_investments...")
    result = check_matured_investments.delay()
    print(f"Task ID: {result.id}")
    
    # Test process_investment_matching
    print("\nTesting process_investment_matching...")
    result = process_investment_matching.delay()
    print(f"Task ID: {result.id}")
    
    print("\nAll tasks have been queued. Check the Celery worker logs for results.")

if __name__ == "__main__":
    test_tasks() 