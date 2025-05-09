from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _
from .models import User, Investment, ReferralHistory,Pairing

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'phone_number', 'referral_code', 'referral_earnings')
    search_fields = ('username', 'email', 'phone_number', 'referral_code')
    list_filter = ('is_active', 'is_staff', 'date_joined')
    fieldsets = UserAdmin.fieldsets + (
        ('Referral Information', {'fields': ('phone_number', 'referral_code', 'referred_by', 'referral_earnings')}),
    )

@admin.register(Investment)
class InvestmentAdmin(admin.ModelAdmin):
    list_display = ('user', 'amount', 'maturity_period', 'status', 'created_at', 'return_amount')
    list_filter = ('status', 'created_at')
    search_fields = ('user__username', 'user__email')
    date_hierarchy = 'created_at'




@admin.register(ReferralHistory)
class ReferralHistoryAdmin(admin.ModelAdmin):
    list_display = ('referrer', 'referred', 'amount_invested', 'bonus_earned', 'status', 'used_at')
    list_filter = ('status', 'created_at')
    search_fields = ('referrer__username', 'referred__username')
    date_hierarchy = 'created_at'
@admin.register(Pairing)
class PairingAdmin(admin.ModelAdmin):
 
    search_fields = ('user__username', 'pair_user__username')
   

