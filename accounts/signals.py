from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db import transaction
from .models import Investment, ReferralHistory
from decimal import Decimal
from .tasks import process_referral_bonus

@receiver(post_save, sender=Investment)
def handle_investment_post_save(sender, instance, created, **kwargs):
    """
    Signal handler for Investment post_save
    - If investment is new, process referral bonus
    - If investment is matured, add to queue
    """
    if created:
        # Process referral bonus for new investments
        if instance.user.referred_by:
            referrer = instance.user.referred_by
            bonus_amount = instance.amount * Decimal('0.03')  # 3% referral bonus
            
            # Create referral history entry
            ReferralHistory.objects.create(
                referrer=referrer,
                referred=instance.user,
                amount_invested=instance.amount,
                bonus_earned=bonus_amount,
                status='pending'
            )
            
            # Add bonus to referrer's earnings
            referrer.referral_earnings += bonus_amount
            referrer.save()
    
    # Handle matured investments
    if instance.status == 'matured':
        # Add to queue for pairing
        from .models import Queue
        Queue.objects.create(
            user=instance.user,
            amount_remaining=instance.return_amount
        )

@receiver(post_save, sender=Investment)
def handle_referral_bonus(sender, instance, created, **kwargs):
    if created and instance.user.referred_by:
        # Calculate 3% bonus
        bonus_amount = instance.amount * Decimal('0.03')
        
        # Update referrer's earnings
        referrer = instance.user.referred_by
        referrer.referral_earnings += bonus_amount
        referrer.save()
        
        # Create referral history entry
        ReferralHistory.objects.create(
            referrer=referrer,
            referred=instance.user,
            amount_invested=instance.amount,
            bonus_earned=bonus_amount
        ) 