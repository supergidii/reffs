from django.core.management.base import BaseCommand
from accounts.models import User, Investment, Queue, Payment

class Command(BaseCommand):
    help = 'Clears all test data from the database'

    def handle(self, *args, **options):
        self.stdout.write('Starting to clear test data...')
        
        # Clear all payments
        payments_count = Payment.objects.all().delete()[0]
        self.stdout.write(f'Deleted {payments_count} payments')
        
        # Clear all queue entries
        queue_count = Queue.objects.all().delete()[0]
        self.stdout.write(f'Deleted {queue_count} queue entries')
        
        # Clear all investments
        investments_count = Investment.objects.all().delete()[0]
        self.stdout.write(f'Deleted {investments_count} investments')
        
        # Clear all users
        users_count = User.objects.all().delete()[0]
        self.stdout.write(f'Deleted {users_count} users')
        
        self.stdout.write(self.style.SUCCESS('Successfully cleared all test data')) 