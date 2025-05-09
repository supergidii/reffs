from celery import shared_task
from django.utils import timezone
from datetime import timedelta, time
from decimal import Decimal
from .models import Investment, Queue, ReferralHistory, Payment
from django.db.models import F
from django.core.mail import send_mail
from django.conf import settings

def is_within_bidding_window():
    """Check if current time is within bidding windows (9:00-9:40 AM or 5:00-5:40 PM)"""
    current_time = timezone.localtime().time()
    morning_start = time(9, 0)
    morning_end = time(9, 40)
    evening_start = time(17, 0)
    evening_end = time(17, 40)
    
    return (
        (morning_start <= current_time <= morning_end) or
        (evening_start <= current_time <= evening_end)
    )

@shared_task
def check_matured_investments():
    """Check for investments that have reached maturity and move them to queue"""
    today = timezone.now()
    
    # Find investments that have reached maturity
    matured_investments = Investment.objects.filter(
        status='pending',
        created_at__lte=today - timedelta(days=F('maturity_period'))
    )
    
    for investment in matured_investments:
        # Create queue entry
        Queue.objects.create(
            user=investment.user,
            amount_remaining=investment.return_amount
        )
        
        # Update investment status
        investment.status = 'matured'
        investment.save()
        
        # Send email notification
        send_maturity_email.delay(investment.id)

@shared_task
def run_pairing_job():
    """Pair matured investments with new investments during bidding windows"""
    if not is_within_bidding_window():
        return
        
    # Get all matured investments in queue
    queue_entries = Queue.objects.all().order_by('created_at')
    
    # Get all pending investments from the current bidding window
    current_time = timezone.now()
    window_start = current_time.replace(
        hour=9 if current_time.hour < 12 else 17,
        minute=0,
        second=0,
        microsecond=0
    )
    
    pending_investments = Investment.objects.filter(
        status='pending',
        created_at__gte=window_start
    ).order_by('created_at')
    
    for queue_entry in queue_entries:
        if queue_entry.amount_remaining <= 0:
            continue
            
        for investment in pending_investments:
            if investment.status != 'pending':
                continue
                
            # Calculate matching amount
            match_amount = min(queue_entry.amount_remaining, investment.amount)
            
            if match_amount > 0:
                # Update queue entry
                queue_entry.amount_remaining -= match_amount
                queue_entry.save()
                
                # Update investment
                investment.status = 'paired'
                investment.paired_to = queue_entry.user
                investment.save()
                
                # Create payment record
                Payment.objects.create(
                    from_user=investment.user,
                    to_user=queue_entry.user,
                    investment=investment,
                    amount=match_amount
                )
                
                if queue_entry.amount_remaining <= 0:
                    break

@shared_task
def send_maturity_email(investment_id):
    """Send email notification for matured investment"""
    try:
        investment = Investment.objects.get(id=investment_id)
        subject = f'Investment Matured - {investment.amount}'
        message = f"""
        Your investment has matured!
        
        Principal: {investment.amount}
        Interest: {investment.return_amount - investment.amount}
        Referral Bonus Used: {investment.referral_bonus_used}
        Total Return: {investment.return_amount}
        
        Please wait for pairing with a new investor during the next bidding window:
        - Morning: 9:00 AM - 9:40 AM
        - Evening: 5:00 PM - 5:40 PM
        """
        
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [investment.user.email],
            fail_silently=False,
        )
    except Investment.DoesNotExist:
        pass 