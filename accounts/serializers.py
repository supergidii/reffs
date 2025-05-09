from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.db import transaction
from .models import ReferralHistory, Investment, User
from django.utils import timezone
from decimal import Decimal

User = get_user_model()

class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    referral_code = serializers.CharField(required=False, allow_blank=True)
    
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'phone_number', 'password', 'referral_code')
        extra_kwargs = {
            'password': {'write_only': True},
        }

    @transaction.atomic
    def create(self, validated_data):
        referral_code = validated_data.pop('referral_code', None)
        
        # Create user
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            phone_number=validated_data['phone_number'],
            password=validated_data['password']
        )
        
        # Handle referral if code provided
        if referral_code:
            try:
                referrer = User.objects.get(referral_code=referral_code)
                if referrer != user:  # Prevent self-referral
                    user.referred_by = referrer
                    user.save()
            except User.DoesNotExist:
                pass  # Invalid referral code, ignore
        
        return user

class UserLoginSerializer(serializers.Serializer):
    phone_number = serializers.CharField(required=True)
    password = serializers.CharField(required=True, write_only=True)

    def validate(self, data):
        phone_number = data.get('phone_number')
        password = data.get('password')

        if not phone_number or not password:
            raise serializers.ValidationError('Both phone number and password are required.')

        return data

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'phone_number', 'referral_code', 'referral_earnings')
        read_only_fields = ('referral_code', 'referral_earnings')

class UserMinimalSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'phone_number']

class InvestmentSerializer(serializers.ModelSerializer):
    user = UserMinimalSerializer(read_only=True)
    
    class Meta:
        model = Investment
        fields = [
            'id', 'user', 'amount', 'created_at', 'maturity_period',
            'status', 'return_amount', 'referral_bonus_used',
            'maturity_date'
        ]
        read_only_fields = [
            'id', 'user', 'created_at', 'status',
            'return_amount', 'referral_bonus_used', 'maturity_date'
        ]

    def validate_amount(self, value):
        """
        Validate the investment amount.
        """
        if value <= Decimal('0'):
            raise serializers.ValidationError("Investment amount must be greater than 0")
        
        # You can add minimum/maximum investment amount validation here
        # if value < Decimal('1000'):
        #     raise serializers.ValidationError("Minimum investment amount is 1000")
        
        return value

    def validate_maturity_period(self, value):
        """
        Validate the maturity period.
        """
        if value <= 0:
            raise serializers.ValidationError("Maturity period must be greater than 0 days")
        
        # You can add maximum maturity period validation here
        # if value > 365:
        #     raise serializers.ValidationError("Maximum maturity period is 365 days")
        
        return value

    @transaction.atomic
    def create(self, validated_data):
        """
        Create and return a new Investment instance.
        """
        user = self.context['request'].user
        investment = Investment.objects.create(
            user=user,
            **validated_data
        )
        
        # Handle referral bonus if user was referred
        if user.referred_by and user.referral_earnings > 0:
            if investment.amount >= user.referral_earnings:
                investment.referral_bonus_used = user.referral_earnings
                user.referral_earnings = 0
                user.save()
                
                # Mark referral history as used
                ReferralHistory.objects.filter(
                    referrer=user.referred_by,
                    referred=user,
                    status='pending'
                ).update(status='used', used_at=timezone.now())
        
        investment.save()
        return investment


class ReferralHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ReferralHistory
        fields = ('id', 'referrer', 'referred', 'amount_invested', 'bonus_earned', 'status', 'used_at')
        read_only_fields = ('referrer', 'referred', 'amount_invested', 'bonus_earned', 'status', 'used_at') 