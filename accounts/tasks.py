from celery import shared_task
from django.utils import timezone
from django.db import transaction
from datetime import timedelta
from decimal import Decimal
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from .models import Investment, Queue, Payment, ReferralHistory, User
import pdfkit # type: ignore
import os
import logging

logger = logging.getLogger(__name__)

@shared_task
def check_matured_investments():
    """Check and process matured investments"""
    try:
        matured_investments = Investment.objects.filter(
            status='pending',
            created_at__lte=timezone.now() - timezone.timedelta(days=1)
        )
        
        for investment in matured_investments:
            investment.status = 'matured'
            investment.save()
            
            # Add to queue
            Queue.objects.create(
                user=investment.user,
                amount_remaining=investment.return_amount
            )
            
            # Send maturity notification
            send_maturity_notification.delay(investment.id)
        
        logger.info(f"Processed {matured_investments.count()} matured investments")
    except Exception as e:
        logger.error(f"Error checking matured investments: {str(e)}")

@shared_task
def run_pairing_job():
    """Pair matured investments with new investors"""
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
                    
                    # Send pairing notification
                    send_pairing_notification.delay(investment.id)
                else:
                    # Partial match
                    investment.paired_to = queue_entry.user
                    investment.status = 'paired'
                    investment.save()
                    
                    queue_entry.amount_remaining -= amount_to_match
                    queue_entry.save()
                    amount_to_match = Decimal('0')
                    
                    # Send pairing notification
                    send_pairing_notification.delay(investment.id)
                
                queue_entries = queue_entries.exclude(id=queue_entry.id)

@shared_task
def process_referral_bonus(investment_id):
    """Process referral bonus for a new investment"""
    try:
        investment = Investment.objects.get(id=investment_id)
        if investment.user.referred_by:
            referrer = investment.user.referred_by
            bonus_amount = investment.amount * Decimal('0.03')  # 3% referral bonus
            
            # Create referral history entry
            ReferralHistory.objects.create(
                referrer=referrer,
                referred=investment.user,
                amount_invested=investment.amount,
                bonus_earned=bonus_amount,
                status='pending'
            )
            
            # Add bonus to referrer's earnings
            referrer.referral_earnings += bonus_amount
            referrer.save()
            
            logger.info(f"Processed referral bonus for investment {investment_id}")
    except Investment.DoesNotExist:
        logger.error(f"Investment {investment_id} not found")
    except Exception as e:
        logger.error(f"Error processing referral bonus for investment {investment_id}: {str(e)}")

@shared_task
def send_maturity_notification(investment_id):
    """Send email notification when investment matures"""
    try:
        investment = Investment.objects.get(id=investment_id)
        if investment.status == 'matured':
            context = {
                'user': investment.user,
                'investment': investment,
                'return_amount': investment.return_amount,
                'dashboard_url': f"{settings.SITE_URL}/dashboard/"
            }
            
            html_message = render_to_string('accounts/email/investment_matured.html', context)
            
            send_mail(
                subject='Your Investment has Matured!',
                message='',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[investment.user.email],
                html_message=html_message
            )
            
            logger.info(f"Sent maturity notification for investment {investment_id}")
    except Investment.DoesNotExist:
        logger.error(f"Investment {investment_id} not found")
    except Exception as e:
        logger.error(f"Error sending maturity notification for investment {investment_id}: {str(e)}")

@shared_task
def process_investment_matching():
    """Match matured investments with new investors"""
    try:
        # Get matured investments from queue
        queue_entries = Queue.objects.filter(amount_remaining__gt=0).order_by('created_at')
        
        for queue_entry in queue_entries:
            # Find pending investments to match with
            pending_investments = Investment.objects.filter(
                status='pending',
                amount__lte=queue_entry.amount_remaining
            ).order_by('created_at')
            
            for investment in pending_investments:
                # Create pairing
                amount_to_pair = min(queue_entry.amount_remaining, investment.amount)
                
                investment.status = 'paired'
                investment.paired_to = queue_entry.user
                investment.save()
                
                queue_entry.amount_remaining -= amount_to_pair
                queue_entry.save()
                
                # Send notification emails
                send_pairing_notification.delay(investment.id)
                
                if queue_entry.amount_remaining <= 0:
                    break
        
        logger.info("Completed investment matching process")
    except Exception as e:
        logger.error(f"Error in investment matching process: {str(e)}")

@shared_task
def send_pairing_notification(investment_id):
    """Send email notification for investment pairing"""
    try:
        investment = Investment.objects.get(id=investment_id)
        context = {
            'user': investment.user,
            'investment': investment,
            'paired_user': investment.paired_to,
            'return_amount': investment.return_amount,
            'dashboard_url': f"{settings.SITE_URL}/dashboard/"
        }
        
        html_message = render_to_string('accounts/email/investment_paired.html', context)
        
        send_mail(
            subject='Your Investment has been Paired!',
            message='',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[investment.user.email],
            html_message=html_message
        )
        
        logger.info(f"Sent pairing notification for investment {investment_id}")
    except Investment.DoesNotExist:
        logger.error(f"Investment {investment_id} not found")
    except Exception as e:
        logger.error(f"Error sending pairing notification for investment {investment_id}: {str(e)}")

@shared_task
def send_referral_bonus_notification(referrer_id, investment_id, bonus_amount):
    """Send notification when referral bonus is earned"""
    try:
        referrer = User.objects.get(id=referrer_id)
        investment = Investment.objects.get(id=investment_id)
        
        subject = f"You've Earned a Referral Bonus!"
        message = render_to_string('accounts/email/referral_bonus.html', {
            'user': referrer,
            'referred_user': investment.user,
            'investment': investment,
            'bonus_amount': bonus_amount
        })
        
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [referrer.email],
            html_message=message,
            fail_silently=False
        )
        
        logger.info(f"Sent referral bonus notification to {referrer.email} for investment {investment_id}")
    except (User.DoesNotExist, Investment.DoesNotExist) as e:
        logger.error(f"Error sending referral bonus notification: {str(e)}")

@shared_task
def generate_investment_statement(investment_id):
    """Generate PDF statement for an investment"""
    try:
        investment = Investment.objects.get(id=investment_id)
        
        # Prepare data for PDF
        context = {
            'investment': investment,
            'user': investment.user,
            'principal': investment.amount,
            'interest': investment.return_amount - investment.amount - investment.referral_bonus_used,
            'referral_bonus': investment.referral_bonus_used,
            'total_return': investment.return_amount,
            'maturity_date': investment.created_at + timedelta(days=investment.maturity_period),
            'generated_at': timezone.now()
        }
        
        # Render HTML template
        html_content = render_to_string('accounts/pdf/investment_statement.html', context)
        
        # Create PDF directory if it doesn't exist
        pdf_dir = os.path.join(settings.MEDIA_ROOT, 'statements')
        os.makedirs(pdf_dir, exist_ok=True)
        
        # Generate PDF
        pdf_path = os.path.join(pdf_dir, f'investment_{investment_id}_statement.pdf')
        pdfkit.from_string(html_content, pdf_path)
        
        logger.info(f"Generated PDF statement for investment {investment_id}")
        return pdf_path
    except Investment.DoesNotExist:
        logger.error(f"Investment {investment_id} not found for PDF generation")
        return None
    except Exception as e:
        logger.error(f"Error generating PDF for investment {investment_id}: {str(e)}")
        return None

@shared_task
def cleanup_old_queue_entries():
    """Clean up old queue entries that are no longer needed"""
    try:
        # Delete queue entries older than 30 days
        cutoff_date = timezone.now() - timedelta(days=30)
        old_entries = Queue.objects.filter(created_at__lt=cutoff_date)
        count = old_entries.count()
        old_entries.delete()
        
        logger.info(f"Cleaned up {count} old queue entries")
    except Exception as e:
        logger.error(f"Error cleaning up old queue entries: {str(e)}")

@shared_task
def send_payment_reminder():
    """Send reminders for pending payments"""
    try:
        # Find paired investments without confirmed payments
        pending_payments = Investment.objects.filter(
            status='paired',
            is_confirmed=False,
            created_at__lte=timezone.now() - timedelta(days=1)  # At least 1 day old
        )
        
        for investment in pending_payments:
            subject = f"Payment Reminder for Investment #{investment.id}"
            message = render_to_string('accounts/email/payment_reminder.html', {
                'user': investment.paired_to,
                'investment': investment,
                'investor': investment.user
            })
            
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [investment.paired_to.email],
                html_message=message,
                fail_silently=False
            )
            
            logger.info(f"Sent payment reminder for investment {investment.id} to {investment.paired_to.email}")
    except Exception as e:
        logger.error(f"Error sending payment reminders: {str(e)}")

@shared_task
def calculate_daily_statistics():
    """Calculate daily statistics for reporting"""
    try:
        today = timezone.now().date()
        yesterday = today - timedelta(days=1)
        
        # Calculate statistics
        new_investments = Investment.objects.filter(
            created_at__date=today
        ).count()
        
        matured_investments = Investment.objects.filter(
            status='matured',
            created_at__date=today
        ).count()
        
        completed_investments = Investment.objects.filter(
            status='completed',
            created_at__date=today
        ).count()
        
        total_investment_amount = Investment.objects.filter(
            created_at__date=today
        ).aggregate(total=models.Sum('amount'))['total'] or 0
        
        # Log statistics
        logger.info(f"Daily statistics for {today}:")
        logger.info(f"New investments: {new_investments}")
        logger.info(f"Matured investments: {matured_investments}")
        logger.info(f"Completed investments: {completed_investments}")
        logger.info(f"Total investment amount: {total_investment_amount}")
        
        # TODO: Store statistics in a model for reporting
    except Exception as e:
        logger.error(f"Error calculating daily statistics: {str(e)}") 