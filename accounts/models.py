from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from decimal import Decimal
import uuid
from datetime import timedelta

class User(AbstractUser):
    phone_number = models.CharField(max_length=20, unique=True)
    referral_code = models.CharField(max_length=20, unique=True, blank=True)
    referred_by = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='referrals')
    referral_earnings = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    USERNAME_FIELD = 'phone_number'
    REQUIRED_FIELDS = ['username', 'email']

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
        ('partially_paid', 'Partially Paid'),
        ('completed', 'Completed')
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='investments')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    maturity_period = models.PositiveIntegerField(help_text='Maturity period in days')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    paired_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='paired_investments')
    return_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    referral_bonus_used = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    payment_confirmed_at = models.DateTimeField(null=True, blank=True)
    last_payment_at = models.DateTimeField(null=True, blank=True)
    start_countdown_at = models.DateTimeField(null=True, blank=True)
    transaction_reference = models.CharField(max_length=50, unique=True, null=True, blank=True)
    payment_method = models.CharField(max_length=50, null=True, blank=True)
    payment_notes = models.TextField(blank=True)
    maturity_notification_sent = models.BooleanField(default=False)

    def __str__(self):
        return f"Investment: {self.user.username} - ${self.amount} ({self.status})"

    def calculate_return_amount(self):
        """Calculate return amount including 2% daily interest"""
        daily_interest = Decimal('0.02')  # 2% daily interest
        interest_amount = self.amount * daily_interest * self.maturity_period
        total_return = self.amount + interest_amount + self.referral_bonus_used
        return total_return

    def update_payment(self, amount_paid, payment_method=None, notes=None):
        """Update payment status and amounts"""
        self.amount_paid += amount_paid
        self.last_payment_at = timezone.now()
        
        if payment_method:
            self.payment_method = payment_method
        if notes:
            self.payment_notes = notes
            
        if self.amount_paid >= self.return_amount:
            self.status = 'completed'
            self.payment_confirmed_at = timezone.now()
        elif self.amount_paid > 0:
            self.status = 'partially_paid'
        
        if not self.transaction_reference:
            self.transaction_reference = f"INV-{uuid.uuid4().hex[:8].upper()}"
            
        self.save()

class Pairing(models.Model):
    matured_investment = models.ForeignKey(Investment, on_delete=models.CASCADE, related_name='matured_pairings')
    new_investment_id = models.ForeignKey(Investment, on_delete=models.CASCADE, related_name='new_pairings')
    amount_paired = models.DecimalField(max_digits=10, decimal_places=2)
    is_confirmed = models.BooleanField(default=False)
    paired_at = models.DateTimeField(auto_now_add=True)
    payment_due_date = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=[
        ('paired', 'Paired'),
        
    ], default='paired')
    payment_status = models.CharField(max_length=20, choices=[
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('failed', 'Failed')
    ], default='pending')

    def __str__(self):
        return f"Pairing: {self.matured_investment.user.username} -> {self.new_investment_id.user.username}"

    def save(self, *args, **kwargs):
        if not self.payment_due_date and self.paired_at:
            # Set payment due date to 24 hours after pairing
            self.payment_due_date = self.paired_at + timedelta(hours=24)
        super().save(*args, **kwargs)

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
        return f"{self.referrer.username} -> {self.referred.username}: ${self.bonus_earned}"

class PairedInvestment(models.Model):
    matured_investor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='matured_pairings')
    new_investor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='new_pairings')
    amount_paired = models.DecimalField(max_digits=10, decimal_places=2)
    is_confirmed = models.BooleanField(default=False)
    paired_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=[('pending', 'Pending'), ('confirmed', 'Confirmed'), ('completed', 'Completed')], default='pending')
     
    def __str__(self):
        return f"Paired Investment: {self.matured_investor.username} -> {self.new_investor.username}"
    
    def save(self, *args, **kwargs):
        if not self.paired_at:
            self.paired_at = timezone.now()
        super().save(*args, **kwargs)

class Payment(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('rejected', 'Rejected')
    ]
    
    from_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='payments_made')
    to_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='payments_received')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    confirmed_at = models.DateTimeField(null=True, blank=True)
    rejected_at = models.DateTimeField(null=True, blank=True)
    rejection_reason = models.TextField(blank=True)
    
    def __str__(self):
        return f"Payment: {self.from_user.username} -> {self.to_user.username} - ${self.amount}"
    
    def confirm(self):
        """Confirm the payment"""
        self.status = 'confirmed'
        self.confirmed_at = timezone.now()
        self.save()
    
    def reject(self, reason=''):
        """Reject the payment with a reason"""
        self.status = 'rejected'
        self.rejected_at = timezone.now()
        self.rejection_reason = reason
        self.save()
