from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
import uuid

class User(AbstractUser):
    phone_number = models.CharField(max_length=15, unique=True)
    referral_code = models.CharField(max_length=20, unique=True, blank=True)
    referred_by = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True)
    referral_earnings = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email', 'phone_number']

    def save(self, *args, **kwargs):
        if not self.referral_code:
            # Generate a unique referral code
            self.referral_code = str(uuid.uuid4())[:8].upper()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.username

class Investment(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('matured', 'Matured'),
        ('paired', 'Paired'),
        ('completed', 'Completed')
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='investments')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    maturity_period = models.PositiveIntegerField(help_text='Maturity period in days')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    paired_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='paired_investments')
    return_amount = models.DecimalField(max_digits=10, decimal_places=2)
    referral_bonus_used = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    is_confirmed = models.BooleanField(default=False)
    start_countdown_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Investment: {self.user.username} - ${self.amount} ({self.status})"

    def calculate_return_amount(self):
        """Calculate return amount including 2% daily interest"""
        if self.status == 'pending':
            return None
        
        daily_interest = Decimal('0.02')  # 2% daily interest
        interest_amount = self.amount * daily_interest * self.maturity_period
        total_return = self.amount + interest_amount + self.referral_bonus_used
        
        return total_return

    def save(self, *args, **kwargs):
        if self.status in ['matured', 'paired', 'completed']:
            self.return_amount = self.calculate_return_amount()
        super().save(*args, **kwargs)

class QueueEntry(models.Model):
    investment = models.ForeignKey(Investment, on_delete=models.CASCADE)
    amount_remaining = models.DecimalField(max_digits=10, decimal_places=2)
    joined_queue_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.investment.user.username}'s queue entry: {self.amount_remaining} remaining"

class Pairing(models.Model):
    matured_investment = models.ForeignKey(Investment, on_delete=models.CASCADE, related_name='matured_pairings')
    new_investment_id = models.ForeignKey(Investment, on_delete=models.CASCADE, related_name='new_pairings')
    amount_paired = models.DecimalField(max_digits=10, decimal_places=2)
    is_confirmed = models.BooleanField(default=False)
    paired_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Pairing: {self.matured_investment.user.username} -> {self.new_investment_id.user.username}"

class Payment(models.Model):
    from_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='payments_sent')
    to_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='payments_received')
    investment = models.ForeignKey('Investment', on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    confirmed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Payment: {self.from_user.username} -> {self.to_user.username} (${self.amount})"

class Referral(models.Model):
    referrer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='referrals_created')
    referral_code = models.CharField(max_length=20, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"Referral Code: {self.referral_code} by {self.referrer.username}"

class ReferralHistory(models.Model):
    referrer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='referral_history')
    referred = models.ForeignKey(User, on_delete=models.CASCADE, related_name='referred_by_history')
    amount_invested = models.DecimalField(max_digits=10, decimal_places=2)
    bonus_earned = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=[('pending', 'Pending'), ('used', 'Used')])
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    used_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Referral: {self.referrer.username} -> {self.referred.username} ({self.status})"

class Queue(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='queue_entries')
    amount_remaining = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['created_at']
        
    def __str__(self):
        return f"Queue: {self.user.username} - ${self.amount_remaining}"

# Signal handlers
@receiver(post_save, sender=Investment)
def investment_post_save(sender, instance, created, **kwargs):
    if created:
        from .tasks import process_referral_bonus, send_maturity_notification
        # Process referral bonus asynchronously
        process_referral_bonus.delay(instance.id)
        
        # Schedule maturity notification
        send_maturity_notification.apply_async(
            args=[instance.id],
            eta=timezone.now() + timezone.timedelta(days=instance.maturity_period)
        ) 