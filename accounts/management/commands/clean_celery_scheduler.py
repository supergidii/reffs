from django.core.management.base import BaseCommand
from django_celery_beat.models import PeriodicTask

class Command(BaseCommand):
    help = 'Cleans up Celery scheduler by removing non-existent tasks'

    def handle(self, *args, **options):
        # List of valid task names
        valid_tasks = [
            'accounts.tasks.check_matured_investments',
            'accounts.tasks.run_pairing_job',
            'accounts.tasks.send_maturity_notification',
            'accounts.tasks.calculate_daily_statistics',
        ]

        # Get all periodic tasks
        tasks = PeriodicTask.objects.all()
        
        # Remove tasks that don't exist in our codebase
        removed_count = 0
        for task in tasks:
            if task.task not in valid_tasks:
                self.stdout.write(f'Removing non-existent task: {task.task}')
                task.delete()
                removed_count += 1

        self.stdout.write(self.style.SUCCESS(f'Successfully removed {removed_count} non-existent tasks')) 