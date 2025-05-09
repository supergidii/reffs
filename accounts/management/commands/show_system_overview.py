from django.core.management.base import BaseCommand
from django.db.models import Sum, Count, Avg
from django.db import models
from accounts.models import User, Investment, Payment, Queue
from decimal import Decimal

class Command(BaseCommand):
    help = 'Shows a comprehensive overview of the system data'

    def format_amount(self, amount):
        """Format amount with 2 decimal places"""
        if amount is None:
            return "0.00"
        return f"{Decimal(str(amount)):.2f}"

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS('\n=== SYSTEM OVERVIEW ===\n'))

        # User Statistics
        total_users = User.objects.count()
        self.stdout.write(self.style.SUCCESS('=== USER STATISTICS ==='))
        self.stdout.write(f'Total Users: {total_users}')
        
        # Investment Statistics
        investments = Investment.objects.all()
        total_investments = investments.count()
        
        self.stdout.write(self.style.SUCCESS('\n=== INVESTMENT STATISTICS ==='))
        self.stdout.write(f'Total Investments: {total_investments}')
        
        # Investment Status Breakdown
        status_counts = investments.values('status').annotate(
            count=Count('id'),
            total_amount=Sum('amount'),
            avg_amount=Avg('amount')
        )
        
        self.stdout.write('\nInvestment Status Breakdown:')
        for status in status_counts:
            self.stdout.write(f"\nStatus: {status['status']}")
            self.stdout.write(f"Count: {status['count']}")
            self.stdout.write(f"Total Amount: ₦{self.format_amount(status['total_amount'])}")
            self.stdout.write(f"Average Amount: ₦{self.format_amount(status['avg_amount'])}")

        # Payment Statistics
        payments = Payment.objects.all()
        total_payments = payments.count()
        
        self.stdout.write(self.style.SUCCESS('\n=== PAYMENT STATISTICS ==='))
        self.stdout.write(f'Total Payments: {total_payments}')
        
        payment_stats = payments.aggregate(
            total_amount=Sum('amount'),
            avg_amount=Avg('amount')
        )
        
        self.stdout.write(f'Total Payment Amount: ₦{self.format_amount(payment_stats["total_amount"])}')
        self.stdout.write(f'Average Payment Amount: ₦{self.format_amount(payment_stats["avg_amount"])}')

        # Queue Statistics
        queue_entries = Queue.objects.all()
        total_queue_entries = queue_entries.count()
        
        self.stdout.write(self.style.SUCCESS('\n=== QUEUE STATISTICS ==='))
        self.stdout.write(f'Total Queue Entries: {total_queue_entries}')
        
        queue_stats = queue_entries.aggregate(
            total_amount=Sum('amount_remaining'),
            avg_amount=Avg('amount_remaining')
        )
        
        self.stdout.write(f'Total Queue Amount: ₦{self.format_amount(queue_stats["total_amount"])}')
        self.stdout.write(f'Average Queue Amount: ₦{self.format_amount(queue_stats["avg_amount"])}')

        # User Investment Details
        self.stdout.write(self.style.SUCCESS('\n=== USER INVESTMENT DETAILS ==='))
        for user in User.objects.all():
            user_investments = Investment.objects.filter(user=user)
            if user_investments.exists():
                self.stdout.write(f"\nUser: {user.username} ({user.phone_number})")
                self.stdout.write(f"Total Investments: {user_investments.count()}")
                
                # Investment amounts by status
                for status in ['pending', 'matured', 'paired', 'completed']:
                    status_investments = user_investments.filter(status=status)
                    if status_investments.exists():
                        total = status_investments.aggregate(total=Sum('amount'))['total']
                        self.stdout.write(f"{status.title()} Investments: {status_investments.count()} (Total: ₦{self.format_amount(total)})")
                
                # Payment details
                payments_made = Payment.objects.filter(from_user=user)
                payments_received = Payment.objects.filter(to_user=user)
                
                if payments_made.exists():
                    total_sent = payments_made.aggregate(total=Sum('amount'))['total']
                    self.stdout.write(f"Payments Made: {payments_made.count()} (Total: ₦{self.format_amount(total_sent)})")
                
                if payments_received.exists():
                    total_received = payments_received.aggregate(total=Sum('amount'))['total']
                    self.stdout.write(f"Payments Received: {payments_received.count()} (Total: ₦{self.format_amount(total_received)})")

        self.stdout.write(self.style.SUCCESS('\n=== END OF OVERVIEW ===')) 