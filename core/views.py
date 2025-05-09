from django.forms import ValidationError
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db import transaction
from django.db.models import Sum, Count
from django.utils import timezone
from .models import Investment, Queue, ReferralHistory
from .serializers import InvestmentSerializer
from .validators import validate_bidding_window
from decimal import Decimal

class InvestmentViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = InvestmentSerializer
    
    def get_queryset(self):
        return Investment.objects.filter(user=self.request.user)
    
    @action(detail=False, methods=['get'])
    def dashboard(self, request):
        try:
            user = request.user
            
            # Get active investments
            active_investments = Investment.objects.filter(
                user=user,
                status__in=['pending', 'paired']
            ).order_by('-created_at')[:5]
            
            # Get matured investments in queue
            queue_position = Queue.objects.filter(
                user=user,
                amount_remaining__gt=0
            ).count()
            
            # Get total referral earnings
            total_referral_earnings = ReferralHistory.objects.filter(
                referrer=user,
                status='pending'
            ).aggregate(total=Sum('bonus_earned'))['total'] or 0
            
            # Get total returns
            total_returns = Investment.objects.filter(
                user=user,
                status='completed'
            ).aggregate(total=Sum('return_amount'))['total'] or 0
            
            # Get pending payments
            pending_payments = Investment.objects.filter(
                paired_to=user,
                is_confirmed=False,
                status='paired'
            ).order_by('-created_at')[:5]
            
            # Get next bidding window
            next_window = self._get_next_bidding_window()
            
            return Response({
                'active_investments': InvestmentSerializer(active_investments, many=True).data,
                'queue_position': queue_position,
                'total_referral_earnings': total_referral_earnings,
                'total_returns': total_returns,
                'pending_payments': InvestmentSerializer(pending_payments, many=True).data,
                'next_bidding_window': next_window,
                'referral_code': user.referral_code,
                'referral_link': f"{request.build_absolute_uri('/')}?ref={user.referral_code}"
            })
            
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['post'])
    def buy_shares(self, request):
        try:
            # Validate bidding window
            validate_bidding_window()
            
            amount = Decimal(request.data.get('amount', 0))
            maturity_period = int(request.data.get('maturity_period', 0))
            
            if amount <= 0:
                return Response(
                    {'error': 'Investment amount must be greater than 0'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            if maturity_period <= 0:
                return Response(
                    {'error': 'Maturity period must be greater than 0'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            with transaction.atomic():
                # Create investment
                investment = Investment.objects.create(
                    user=request.user,
                    amount=amount,
                    maturity_period=maturity_period,
                    status='pending'
                )
                
                # Handle referral bonus if applicable
                if request.user.referral_earnings > 0:
                    bonus_to_use = min(request.user.referral_earnings, amount)
                    investment.referral_bonus_used = bonus_to_use
                    investment.return_amount += bonus_to_use
                    request.user.referral_earnings -= bonus_to_use
                    request.user.save()
                    investment.save()
                
                return Response(
                    {
                        'message': 'Investment placed successfully',
                        'investment': InvestmentSerializer(investment).data,
                        'next_bidding_window': self._get_next_bidding_window()
                    },
                    status=status.HTTP_201_CREATED
                )
                
        except ValidationError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def _get_next_bidding_window(self):
        """Get information about the next bidding window"""
        from django.utils import timezone
        from datetime import datetime, time
        
        current_time = timezone.localtime()
        current_hour = current_time.hour
        
        if current_hour < 9:
            return {
                'window': 'morning',
                'start': current_time.replace(hour=9, minute=0).strftime('%Y-%m-%d %H:%M'),
                'end': current_time.replace(hour=9, minute=40).strftime('%Y-%m-%d %H:%M')
            }
        elif current_hour < 17:
            return {
                'window': 'evening',
                'start': current_time.replace(hour=17, minute=0).strftime('%Y-%m-%d %H:%M'),
                'end': current_time.replace(hour=17, minute=40).strftime('%Y-%m-%d %H:%M')
            }
        else:
            # If after 5:40 PM, return next day's morning window
            next_day = current_time + timezone.timedelta(days=1)
            return {
                'window': 'morning',
                'start': next_day.replace(hour=9, minute=0).strftime('%Y-%m-%d %H:%M'),
                'end': next_day.replace(hour=9, minute=40).strftime('%Y-%m-%d %H:%M')
            } 