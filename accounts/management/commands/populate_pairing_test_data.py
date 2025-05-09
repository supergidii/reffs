from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal
from accounts.models import User, Investment, Queue, Payment
import random
from django.db import models

class Command(BaseCommand):
    help = 'Populates the database with test data for pairing scenarios'

    def generate_unique_phone(self):
        """Generate a unique phone number that doesn't exist in the database."""
        while True:
            # Generate a phone number in format: +234 7XX XXX XXXX (Nigerian format)
            phone = f"+2347{random.randint(0, 9)}{random.randint(0, 9)}{random.randint(0, 9)}{random.randint(0, 9)}{random.randint(0, 9)}{random.randint(0, 9)}{random.randint(0, 9)}{random.randint(0, 9)}"
            if not User.objects.filter(phone_number=phone).exists():
                return phone

    def generate_investment_amount(self):
        """Generate a random investment amount between 1000 and 10000"""
        return Decimal(str(random.randint(1000, 10000)))

    def create_payment(self, from_user, to_user, investment, amount):
        """Create a payment record for a paired investment"""
        payment = Payment.objects.create(
            from_user=from_user,
            to_user=to_user,
            investment=investment,
            amount=amount,
            confirmed_at=timezone.now()  # Simulate confirmed payment
        )
        self.stdout.write(f'Created payment: {payment.id} from {from_user.username} to {to_user.username} for investment {investment.id}')
        return payment

    def handle(self, *args, **kwargs):
        self.stdout.write('Starting to populate pairing test data...')
        
        # Create 30 test users
        users = []
        for i in range(30):
            phone_number = self.generate_unique_phone()
            user = User.objects.create_user(
                username=f'testuser{i+1}',
                email=f'test{i+1}@example.com',
                phone_number=phone_number,
                password='testpass123'
            )
            users.append(user)
            self.stdout.write(f'Created user: {user.username} with phone: {phone_number}')
        
        # Create matured investments (10 users)
        matured_users = users[:10]
        matured_investments = []
        for user in matured_users:
            # Create 1-3 matured investments per user
            num_investments = random.randint(1, 3)
            for _ in range(num_investments):
                amount = self.generate_investment_amount()
                investment = Investment.objects.create(
                    user=user,
                    amount=amount,
                    maturity_period=random.randint(1, 7),  # 1-7 days maturity
                    status='matured',
                    return_amount=amount * Decimal('1.02')  # 2% return
                )
                matured_investments.append(investment)
                
                # Create queue entry
                Queue.objects.create(
                    user=user,
                    amount_remaining=amount
                )
                
                self.stdout.write(f'Created matured investment: {investment.id} for user {user.username}')
        
        # Create pending investments (20 users)
        pending_users = users[10:]
        pending_investments = []
        for user in pending_users:
            # Create 1-2 pending investments per user
            num_investments = random.randint(1, 2)
            for _ in range(num_investments):
                amount = self.generate_investment_amount()
                investment = Investment.objects.create(
                    user=user,
                    amount=amount,
                    maturity_period=random.randint(1, 7),  # 1-7 days maturity
                    status='pending',
                    return_amount=amount * Decimal('1.02')  # 2% return
                )
                pending_investments.append(investment)
                self.stdout.write(f'Created pending investment: {investment.id} for user {user.username}')
        
        # Simulate pairing process
        self.stdout.write('\nSimulating pairing process...')
        for pending_investment in pending_investments:
            # Find a matured investment to pair with
            for matured_investment in matured_investments:
                if matured_investment.status == 'matured':
                    # Pair the investments
                    pending_investment.status = 'paired'
                    pending_investment.paired_to = matured_investment.user
                    pending_investment.save()
                    
                    # Create payment record
                    self.create_payment(
                        from_user=pending_investment.user,
                        to_user=matured_investment.user,
                        investment=pending_investment,
                        amount=pending_investment.amount
                    )
                    
                    # Update matured investment status
                    matured_investment.status = 'completed'
                    matured_investment.save()
                    
                    self.stdout.write(f'Paired investment {pending_investment.id} with matured investment {matured_investment.id}')
                    break
        
        self.stdout.write(self.style.SUCCESS('Successfully populated pairing test data!'))
        
        # Print summary
        self.stdout.write('\nSummary:')
        self.stdout.write(f'Total Users: {User.objects.count()}')
        self.stdout.write(f'Total Investments: {Investment.objects.count()}')
        self.stdout.write(f'Matured Investments: {Investment.objects.filter(status="matured").count()}')
        self.stdout.write(f'Pending Investments: {Investment.objects.filter(status="pending").count()}')
        self.stdout.write(f'Paired Investments: {Investment.objects.filter(status="paired").count()}')
        self.stdout.write(f'Completed Investments: {Investment.objects.filter(status="completed").count()}')
        self.stdout.write(f'Queue Entries: {Queue.objects.count()}')
        self.stdout.write(f'Total Payments: {Payment.objects.count()}')
        
        # Print investment distribution
        matured_investments = Investment.objects.filter(status='matured')
        pending_investments = Investment.objects.filter(status='pending')
        paired_investments = Investment.objects.filter(status='paired')
        completed_investments = Investment.objects.filter(status='completed')
        
        self.stdout.write('\nInvestment Distribution:')
        
        def get_safe_avg(queryset):
            avg = queryset.aggregate(models.Avg('amount'))['amount__avg']
            return f"{avg:.2f}" if avg is not None else "0.00"
            
        def get_safe_sum(queryset):
            total = queryset.aggregate(models.Sum('amount'))['amount__sum']
            return f"{total:.2f}" if total is not None else "0.00"
        
        self.stdout.write(f'Average Matured Investment Amount: {get_safe_avg(matured_investments)}')
        self.stdout.write(f'Average Pending Investment Amount: {get_safe_avg(pending_investments)}')
        self.stdout.write(f'Average Paired Investment Amount: {get_safe_avg(paired_investments)}')
        self.stdout.write(f'Average Completed Investment Amount: {get_safe_avg(completed_investments)}')
        self.stdout.write(f'Total Matured Amount: {get_safe_sum(matured_investments)}')
        self.stdout.write(f'Total Pending Amount: {get_safe_sum(pending_investments)}')
        self.stdout.write(f'Total Paired Amount: {get_safe_sum(paired_investments)}')
        self.stdout.write(f'Total Completed Amount: {get_safe_sum(completed_investments)}') 