from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db import transaction
from accounts.models import Investment, Queue
from datetime import timedelta

class Command(BaseCommand):
    help = 'Check and process matured investments'

    def handle(self, *args, **options):
        # Get all pending investments that have reached maturity
        matured_investments = Investment.objects.filter(
            status='pending',
            created_at__lte=timezone.now() - timedelta(days=F('maturity_period'))
        )

        with transaction.atomic():
            for investment in matured_investments:
                # Update investment status
                investment.status = 'matured'
                investment.save()

                # Create queue entry
                Queue.objects.create(
                    user=investment.user,
                    amount_remaining=investment.return_amount
                )

                self.stdout.write(
                    self.style.SUCCESS(
                        f'Processed matured investment {investment.id} for user {investment.user.username}'
                    )
                ) 