from celery import shared_task
from django.utils import timezone
from django.db import transaction, models
from datetime import timedelta
from decimal import Decimal
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from django.apps import apps
import pdfkit # type: ignore
import os
import logging
from django.db.models import Sum, Count
import random

from accounts.models import Investment, PairedInvestment, Pairing, ReferralHistory, User

logger = logging.getLogger(__name__)

@shared_task
def check_matured_investments():
    """Check for investments that have reached maturity"""
    now = timezone.now()
    # Get all pending investments
    pending_investments = Investment.objects.filter(
        status='pending'
    )
    
    for investment in pending_investments:
        # Calculate maturity date based on created_at and maturity_period
        maturity_date = investment.created_at + timedelta(days=investment.maturity_period)
        if now >= maturity_date:
            investment.status = 'matured'
            investment.save()
            # Send maturity notification
            send_maturity_notification.delay(investment.id)

@shared_task
def send_maturity_notification(investment_id=None):
    """Send email notification when investment matures"""
    try:
        if investment_id:
            # Handle single investment notification
            investments = Investment.objects.filter(id=investment_id)
        else:
            # Handle all matured investments
            investments = Investment.objects.filter(
                status='matured',
                maturity_notification_sent=False
            )
        
        for investment in investments:
            user = investment.user
            
            # Prepare email content
            subject = f'Investment Matured - {investment.id}'
            context = {
                'user': user,
                'investment': investment,
                'return_amount': investment.return_amount,
                'maturity_date': investment.maturity_date,
            }
            
            message = render_to_string('accounts/email/maturity_notification.html', context)
            
            # Send email
            send_mail(
                subject=subject,
                message='',  # Empty message as we're using HTML
                html_message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                fail_silently=False,
            )
            
            # Mark notification as sent
            investment.maturity_notification_sent = True
            investment.save()
            
            logger.info(f"Sent maturity notification for investment {investment.id}")
    except Exception as e:
        logger.error(f"Failed to send maturity notification: {str(e)}")

@shared_task
def process_referral_bonus(investment_id):
    """Process referral bonus for a new investment"""
    try:
        investment = Investment.objects.get(id=investment_id)
        user = investment.user
        
        if user.referred_by:
            # Calculate referral bonus (3% of investment amount)
            bonus_amount = investment.amount * Decimal('0.03')
            
            # Update referrer's earnings
            referrer = user.referred_by
            referrer.referral_earnings += bonus_amount
            referrer.save()
            
            # Create referral history entry
            ReferralHistory.objects.create(
                referrer=referrer,
                referred=user,
                amount_invested=investment.amount,
                bonus_earned=bonus_amount,
                status='pending'
            )
            
            # Send notification
            send_referral_bonus_notification.delay(referrer.id, investment.id, float(bonus_amount))
            
            logger.info(f"Processed referral bonus for investment {investment_id}")
    except Exception as e:
        logger.error(f"Failed to process referral bonus for investment {investment_id}: {str(e)}")

@shared_task
def send_referral_bonus_notification(referrer_id, investment_id, bonus_amount):
    """Send email notification for referral bonus"""
    try:
        referrer = User.objects.get(id=referrer_id)
        investment = Investment.objects.get(id=investment_id)
        
        # Prepare email content
        subject = f'New Referral Bonus - {investment.id}'
        context = {
            'referrer': referrer,
            'investment': investment,
            'bonus_amount': bonus_amount,
        }
        
        message = render_to_string('accounts/email/referral_bonus_notification.html', context)
        
        # Send email
        send_mail(
            subject=subject,
            message='',  # Empty message as we're using HTML
            html_message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[referrer.email],
            fail_silently=False,
        )
        
        logger.info(f"Sent referral bonus notification for investment {investment_id}")
    except Exception as e:
        logger.error(f"Failed to send referral bonus notification for investment {investment_id}: {str(e)}")

@shared_task
def generate_investment_statement(investment_id):
    """Generate PDF statement for an investment"""
    try:
        investment = Investment.objects.get(id=investment_id)
        user = investment.user
        
        # Prepare PDF content
        context = {
            'user': user,
            'investment': investment,
            'return_amount': investment.return_amount,
            'maturity_date': investment.maturity_date,
        }
        
        # Generate PDF
        html = render_to_string('accounts/pdf/investment_statement.html', context)
        pdf = pdfkit.from_string(html, False, options=settings.PDFKIT_OPTIONS)
        
        # Save PDF to media directory
        filename = f'investment_statement_{investment_id}.pdf'
        filepath = os.path.join(settings.MEDIA_ROOT, 'statements', filename)
        
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, 'wb') as f:
            f.write(pdf)
        
        logger.info(f"Generated investment statement for investment {investment_id}")
        return filepath
    except Exception as e:
        logger.error(f"Failed to generate investment statement for investment {investment_id}: {str(e)}")
        return None

@shared_task
def calculate_daily_statistics():
    """Calculate daily statistics for the system"""
    try:
        # Get total investments
        total_investments = Investment.objects.count()
        total_amount = Investment.objects.aggregate(total=Sum('amount'))['total'] or 0
        
        # Get total referral bonuses
        total_referral_bonuses = ReferralHistory.objects.filter(
            status='used'
        ).aggregate(total=Sum('bonus_earned'))['total'] or 0
        
        # Get total matured investments
        matured_investments = Investment.objects.filter(
            status='matured'
        ).count()
        
        # Log statistics
        logger.info(f"Daily Statistics:")
        logger.info(f"Total Investments: {total_investments}")
        logger.info(f"Total Amount: {total_amount}")
        logger.info(f"Total Referral Bonuses: {total_referral_bonuses}")
        logger.info(f"Matured Investments: {matured_investments}")
        
    except Exception as e:
        logger.error(f"Failed to calculate daily statistics: {str(e)}")

@shared_task
def run_pairing_job():
    """
    Task to match matured investments with new investments
    """
    try:
        # Get matured investments that haven't been paired yet
        matured_investments = Investment.objects.filter(
            status='matured',
            paired_to__isnull=True
        ).order_by('created_at')

        # Get new investments that are pending
        new_investments = Investment.objects.filter(
            status='pending'
        ).order_by('created_at')

        # Process each matured investment
        for matured in matured_investments:
            remaining_return = matured.return_amount
            matured_paired = False

            # Try to pair with new investments until return amount is exhausted
            for new in new_investments:
                if new.status == 'paired':
                    continue

                if remaining_return >= new.amount:
                    # Full pairing of new investment
                    new.status = 'paired'
                    new.paired_to = matured.user
                    new.paired_investment = PairedInvestment.objects.create(
                        matured_investor=matured.user,
                        new_investor=new.user,
                        amount_paired=new.amount,
                        status='paired',
                        payment_status='pending',
                        paired_at=timezone.now(),

                    )
                    new.save()
                    
                    remaining_return -= new.amount
                    send_pairing_notification.delay(matured.user.id, new.user.id)
                    
                    if remaining_return == 0:
                        matured.status = 'paired'
                        matured.paired_to = new.user
                        matured.save()
                        matured_paired = True
                        break
                        
                else:
                    
                   
                    
                    # Update original new investment
                    new.amount -= remaining_return
                    matured.status='paired'
                    
                    
                    send_pairing_notification.delay(matured.user.id, new.user.id)
                    
                    matured.status = 'paired'
                    matured.paired_to = new.user
                    matured.paired_investment = PairedInvestment.objects.create(
                        matured_investor=matured.user,
                        new_investor=new.user,
                        amount_paired=new.amount,
                        status='paired',
                        payment_status='pending',)
                    matured.save()
                    matured_paired = True
                    break

            if not matured_paired and remaining_return > 0:
                # Look for another matured investment to combine with
                for other_matured in matured_investments:
                    if other_matured != matured and other_matured.status == 'matured':
                        combined_return = remaining_return + other_matured.return_amount
                        # Try pairing again with combined amount
                        for new in new_investments:
                            if new.status != 'paired' and new.amount <= combined_return:
                                new.status = 'paired'
                                new.paired_to = matured.user
                                new.save()
                                
                                matured.status = 'paired'
                                matured.paired_to = new.user
                                matured.save()
                                
                                other_matured.status = 'paired'
                                other_matured.paired_to = new.user
                                other_matured.save()
                                
                                send_pairing_notification.delay(matured.user.id, new.user.id)
                                send_pairing_notification.delay(other_matured.user.id, new.user.id)
                                break
        logger.info("Pairing job completed successfully")
    except Exception as e:
        logger.error(f"Failed to run pairing job: {str(e)}")
        raise

@shared_task
def send_pairing_notification(matured_user_id, new_user_id):
    """Send email notifications to both users when investments are paired"""
    try:
        matured_user = User.objects.get(id=matured_user_id)
        new_user = User.objects.get(id=new_user_id)

        # Send notification to matured investment user
        subject = f'Investment Paired - {matured_user.username}'
        context = {
            'user': matured_user,
            'paired_user': new_user,
        }
        
        message = render_to_string('accounts/email/pairing_notification.html', context)
        send_mail(
            subject=subject,
            message='',
            html_message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[matured_user.email],
            fail_silently=False,
        )

        # Send notification to new investment user
        subject = f'Investment Paired - {new_user.username}'
        context = {
            'user': new_user,
            'paired_user': matured_user,
        }
        
        message = render_to_string('accounts/email/pairing_notification.html', context)
        send_mail(
            subject=subject,
            message='',
            html_message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[new_user.email],
            fail_silently=False,
        )

        logger.info(f"Sent pairing notifications for users {matured_user_id} and {new_user_id}")
    except Exception as e:
        logger.error(f"Failed to send pairing notifications: {str(e)}")

@shared_task
def send_payment_reminders():
    """Send payment reminders to users who need to make payments"""
    try:
        # Get all pending pairings where payment is due
        pending_pairings = Pairing.objects.filter(
            status='pending',
            payment_due_date__lte=timezone.now()
        )
        
        for pairing in pending_pairings:
            # Get the users involved
            matured_user = pairing.matured_investment.user
            new_user = pairing.new_investment_id.user
            
            # Send reminder to new user
            subject = 'Payment Reminder - Investment Pairing'
            message = render_to_string('accounts/email/payment_reminder.txt', {
                'user': new_user,
                'matured_user': matured_user,
                'amount': pairing.amount_paired,
                'due_date': pairing.payment_due_date,
            })
            
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [new_user.email],
                fail_silently=False,
            )
            
            logger.info(f"Payment reminder sent to {new_user.email}")
            
    except Exception as e:
        logger.error(f"Error sending payment reminders: {str(e)}")
        raise

@shared_task
def check_admin_pairing():
    """Check for admin pairing requests and process them"""
    try:
        # Get all pending pairings that need admin review
        pending_pairings = Pairing.objects.filter(
            status='pending',
            is_confirmed=False
        ).select_related(
            'matured_investment',
            'new_investment_id',
            'matured_investment__user',
            'new_investment_id__user'
        )
        
        for pairing in pending_pairings:
            # Check if payment is overdue
            if pairing.payment_due_date and pairing.payment_due_date <= timezone.now():
                # Update pairing status to failed
                pairing.status = 'failed'
                pairing.save()
                
                # Send notification to both users
                send_pairing_failed_notification.delay(
                    pairing.matured_investment.user.id,
                    pairing.new_investment_id.user.id,
                    pairing.id
                )
                
                logger.info(f"Pairing {pairing.id} marked as failed due to overdue payment")
            
        logger.info("Admin pairing check completed")
    except Exception as e:
        logger.error(f"Error in check_admin_pairing: {str(e)}")
        raise

@shared_task
def send_pairing_failed_notification(matured_user_id, new_user_id, pairing_id):
    """Send notification when a pairing fails"""
    try:
        matured_user = User.objects.get(id=matured_user_id)
        new_user = User.objects.get(id=new_user_id)
        pairing = Pairing.objects.get(id=pairing_id)
        
        # Send notification to matured user
        subject = 'Pairing Failed - Payment Overdue'
        message = render_to_string('accounts/email/pairing_failed.txt', {
            'user': matured_user,
            'new_user': new_user,
            'amount': pairing.amount_paired,
            'due_date': pairing.payment_due_date,
        })
        
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [matured_user.email],
            fail_silently=False,
        )
        
        # Send notification to new user
        subject = 'Pairing Failed - Payment Overdue'
        message = render_to_string('accounts/email/pairing_failed.txt', {
            'user': new_user,
            'matured_user': matured_user,
            'amount': pairing.amount_paired,
            'due_date': pairing.payment_due_date,
        })
        
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [new_user.email],
            fail_silently=False,
        )
        
        logger.info(f"Pairing failed notifications sent for pairing {pairing_id}")
    except Exception as e:
        logger.error(f"Error sending pairing failed notifications: {str(e)}")
        raise 