from django.core.management.base import BaseCommand
from django.utils import timezone
from accounts.models import User, Investment, ReferralHistory
from datetime import timedelta
import random

class Command(BaseCommand):
    help = 'Populates the database with test data'

    def handle(self, *args, **options):
        self.stdout.write('Creating test data...')
        
        # Create admin user
        admin = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            phone_number='1234567890',
            password='admin123'
        )
        self.stdout.write(self.style.SUCCESS('Created admin user'))

        # Create referrer user
        referrer = User.objects.create_user(
            username='referrer',
            email='referrer@example.com',
            phone_number='2345678901',
            password='test123'
        )
        self.stdout.write(self.style.SUCCESS('Created referrer user'))

        # Create 10 test users with random data
        for i in range(1, 11):
            user = User.objects.create_user(
                username=f'test_user_{i}',
                email=f'test_user_{i}@example.com',
                phone_number=f'34567890{i}',
                password='test123',
                referred_by=referrer if i % 2 == 0 else None  # Alternate users are referred
            )
            
            # Create 2-4 investments per user
            num_investments = random.randint(2, 4)
            for j in range(num_investments):
                # Random amount between 100 and 10000
                amount = random.randint(100, 10000)
                # Random maturity period between 7 and 30 days
                maturity_period = random.randint(7, 30)
                
                # Calculate created_at to have some matured and some immature investments
                days_ago = random.randint(0, maturity_period + 5)
                created_at = timezone.now() - timedelta(days=days_ago)
                
                # Calculate return amount (2% daily interest)
                return_amount = amount * (1 + (0.02 * maturity_period))
                
                investment = Investment.objects.create(
                    user=user,
                    amount=amount,
                    maturity_period=maturity_period,
                    created_at=created_at,
                    return_amount=return_amount,
                    status='matured' if days_ago >= maturity_period else 'pending'
                )
                
                # If user was referred, create referral history
                if user.referred_by:
                    ReferralHistory.objects.create(
                        referrer=user.referred_by,
                        referred=user,
                        amount_invested=amount,
                        bonus_earned=amount * 0.03,  # 3% referral bonus
                        status='pending'
                    )
            
            self.stdout.write(self.style.SUCCESS(f'Created user {i} with investments'))

        self.stdout.write(self.style.SUCCESS('Successfully populated test data')) 