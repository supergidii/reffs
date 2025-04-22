from django.core.management.base import BaseCommand
from django.db import transaction
from accounts.models import Investment, Queue
from decimal import Decimal

class Command(BaseCommand):
    help = 'Pair matured investments with new investors'

    def handle(self, *args, **options):
        # Get all pending investments
        pending_investments = Investment.objects.filter(status='pending')
        
        # Get all queue entries
        queue_entries = Queue.objects.all().order_by('created_at')

        with transaction.atomic():
            for investment in pending_investments:
                amount_to_match = investment.amount
                
                while amount_to_match > 0 and queue_entries.exists():
                    queue_entry = queue_entries.first()
                    
                    if queue_entry.amount_remaining <= amount_to_match:
                        # Full match
                        investment.paired_to = queue_entry.user
                        investment.status = 'paired'
                        investment.save()
                        
                        queue_entry.delete()
                        amount_to_match = Decimal('0')
                        
                        self.stdout.write(
                            self.style.SUCCESS(
                                f'Paired investment {investment.id} with queue entry {queue_entry.id}'
                            )
                        )
                    else:
                        # Partial match
                        investment.paired_to = queue_entry.user
                        investment.status = 'paired'
                        investment.save()
                        
                        queue_entry.amount_remaining -= amount_to_match
                        queue_entry.save()
                        amount_to_match = Decimal('0')
                        
                        self.stdout.write(
                            self.style.SUCCESS(
                                f'Partially paired investment {investment.id} with queue entry {queue_entry.id}'
                            )
                        )
                    
                    queue_entries = queue_entries.exclude(id=queue_entry.id) 