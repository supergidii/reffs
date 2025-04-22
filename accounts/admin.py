from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _
from .models import User, Investment, Payment, Queue, ReferralHistory

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'phone_number', 'referral_code', 'referral_earnings', 'date_joined')
    search_fields = ('username', 'email', 'phone_number', 'referral_code')
    list_filter = ('is_active', 'is_staff', 'date_joined')
    ordering = ('-date_joined',)
    
    fieldsets = (
        (None, {'fields': ('username', 'phone_number', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'email')}),
        (_('Referral Info'), {'fields': ('referral_code', 'referred_by', 'referral_earnings')}),
        (_('Permissions'), {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'phone_number', 'email', 'password1', 'password2'),
        }),
    )

@admin.register(Investment)
class InvestmentAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'amount', 'maturity_period', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('user__username', 'user__email', 'user__phone_number')
    readonly_fields = ('created_at',)
    ordering = ('-created_at',)

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('id', 'from_user', 'to_user', 'amount', 'confirmed_at')
    list_filter = ('confirmed_at',)
    search_fields = ('from_user__username', 'to_user__username')
    readonly_fields = ('confirmed_at',)
    ordering = ('-confirmed_at',)

@admin.register(Queue)
class QueueAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'amount_remaining', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('user__username',)
    readonly_fields = ('created_at',)
    ordering = ('-created_at',)

@admin.register(ReferralHistory)
class ReferralHistoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'referrer', 'referred', 'amount_invested', 'bonus_earned', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('referrer__username', 'referred__username')
    readonly_fields = ('created_at', 'used_at')
    ordering = ('-created_at',)
