from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db import transaction
from decimal import Decimal
from accounts.models import ReferralHistory, Investment

@receiver(post_save, sender='accounts.Investment')
def investment_post_save(sender, instance, created, **kwargs):
    """
    Signal handler for Investment post_save
    - If investment is new, process referral bonus for the entire chain
    """
    if created:
        try:
            with transaction.atomic():
                # Handle new investment creation
                # Process referral bonus for the entire chain
                current_user = instance.user
                
                while current_user.referred_by:
                    referrer = current_user.referred_by
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
                    
                    # Move up the chain
                    current_user = referrer
        except Exception as e:
            # Log the error but don't raise it to prevent the investment creation from failing
            print(f"Error processing referral bonus: {str(e)}") 