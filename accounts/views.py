from django.shortcuts import render, get_object_or_404
from rest_framework import status, generics
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from django.utils import timezone
from django.db import transaction
from decimal import Decimal
from datetime import datetime, timedelta
from django.template.loader import render_to_string
from django.http import HttpResponse
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from .serializers import (
    UserRegistrationSerializer, UserLoginSerializer, UserSerializer,
    InvestmentSerializer, ReferralHistorySerializer
)
from .models import User, Investment, ReferralHistory, Payment
from rest_framework.decorators import api_view, permission_classes
from django.views.generic import TemplateView
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.db.models import Sum, Count, Avg

# Create your views here.

class UserRegistrationView(generics.CreateAPIView):
    permission_classes = (AllowAny,)
    serializer_class = UserRegistrationSerializer

    def post(self, request, *args, **kwargs):
        print("\n=== Registration Request Debug ===")
        print("Request data:", request.data)
        print("Request headers:", request.headers)
        print("Request method:", request.method)
        print("Request content type:", request.content_type)
        
        # Validate required fields
        required_fields = ['username', 'email', 'phone_number', 'password']
        missing_fields = [field for field in required_fields if field not in request.data]
        if missing_fields:
            print("Missing required fields:", missing_fields)
            return Response({
                'error': f'Missing required fields: {", ".join(missing_fields)}'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Validate phone number format
        phone_number = request.data.get('phone_number', '')
        if not phone_number.startswith('07') or not phone_number.isdigit() or len(phone_number) != 10:
            print("Invalid phone number format:", phone_number)
            return Response({
                'phone_number': ['Phone number must be in format 07XXXXXXXX']
            }, status=status.HTTP_400_BAD_REQUEST)

        # Validate email format
        email = request.data.get('email', '')
        if not '@' in email or not '.' in email:
            print("Invalid email format:", email)
            return Response({
                'email': ['Please enter a valid email address']
            }, status=status.HTTP_400_BAD_REQUEST)

        # Validate password length
        password = request.data.get('password', '')
        if len(password) < 8:
            print("Password too short:", len(password))
            return Response({
                'password': ['Password must be at least 8 characters long']
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            serializer = self.get_serializer(data=request.data)
            if serializer.is_valid():
                print("Serializer is valid")
                try:
                    user = serializer.save()
                    print("User created successfully:", user.username)
                    refresh = RefreshToken.for_user(user)
                    response_data = {
                        'user': UserSerializer(user).data,
                        'refresh': str(refresh),
                        'access': str(refresh.access_token),
                    }
                    print("Sending successful response")
                    return Response(response_data, status=status.HTTP_201_CREATED)
                except Exception as e:
                    print("Error creating user:", str(e))
                    print("Error type:", type(e).__name__)
                    import traceback
                    print("Traceback:", traceback.format_exc())
                    return Response({
                        'error': f'Failed to create user account: {str(e)}'
                    }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
            print("Serializer validation failed")
            print("Serializer errors:", serializer.errors)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            print("Unexpected error during registration:", str(e))
            print("Error type:", type(e).__name__)
            import traceback
            print("Traceback:", traceback.format_exc())
            return Response({
                'error': 'An unexpected error occurred during registration'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class UserLoginView(APIView):
    permission_classes = (AllowAny,)
    serializer_class = UserLoginSerializer

    def post(self, request):
        print("Login request received:", request.data)  # Debug print
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            print("Serializer is valid")  # Debug print
            try:
                user = authenticate(
                    phone_number=serializer.validated_data['phone_number'],
                    password=serializer.validated_data['password']
                )
                print("Authentication result:", user)  # Debug print
                if user:
                    refresh = RefreshToken.for_user(user)
                    response_data = {
                        'user': UserSerializer(user).data,
                        'refresh': str(refresh),
                        'access': str(refresh.access_token),
                    }
                    print("Sending response:", response_data)  # Debug print
                    return Response(response_data)
                print("Authentication failed")  # Debug print
                return Response({'error': 'Invalid phone number or password'}, status=status.HTTP_401_UNAUTHORIZED)
            except Exception as e:
                print("Authentication error:", str(e))  # Debug print
                return Response({'error': 'Authentication failed'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        print("Serializer errors:", serializer.errors)  # Debug print
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserProfileView(generics.RetrieveUpdateAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = UserSerializer

    def get_object(self):
        return self.request.user

class InvestmentCreateView(generics.CreateAPIView):
    serializer_class = InvestmentSerializer
    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = request.user
        amount = serializer.validated_data['amount']
        maturity_period = serializer.validated_data['maturity_period']

        # Calculate return amount (2% per day)
        daily_interest_rate = Decimal('0.02')
        interest_amount = amount * daily_interest_rate * maturity_period
        return_amount = amount + interest_amount
        referral_bonus_used = Decimal('0')

        # Check and apply referral bonus if available
        if user.referral_earnings > 0 and amount >= user.referral_earnings:
            referral_bonus_used = user.referral_earnings
            return_amount += referral_bonus_used
            
            # Update referral history records
            referral_histories = ReferralHistory.objects.filter(
                referrer=user,
                status='pending'
            ).order_by('created_at')

            remaining_bonus = referral_bonus_used
            for history in referral_histories:
                if remaining_bonus <= 0:
                    break
                
                if history.bonus_earned <= remaining_bonus:
                    history.status = 'used'
                    history.used_at = timezone.now()
                    history.save()
                    remaining_bonus -= history.bonus_earned
                else:
                    # Split the history record
                    used_amount = remaining_bonus
                    ReferralHistory.objects.create(
                        referrer=history.referrer,
                        referred=history.referred,
                        amount_invested=history.amount_invested * (used_amount / history.bonus_earned),
                        bonus_earned=used_amount,
                        status='used',
                        used_at=timezone.now()
                    )
                    history.amount_invested = history.amount_invested * ((history.bonus_earned - used_amount) / history.bonus_earned)
                    history.bonus_earned -= used_amount
                    history.save()
                    remaining_bonus = 0

            # Reset user's referral earnings
            user.referral_earnings = 0
            user.save()

        # Create investment
        investment = Investment.objects.create(
            user=user,
            amount=amount,
            maturity_period=maturity_period,
            status='pending',
            return_amount=return_amount,
            referral_bonus_used=referral_bonus_used,
            maturity_date=timezone.now() + timedelta(days=maturity_period)
        )

        response_data = {
            'id': investment.id,
            'amount': amount,
            'return_amount': return_amount,
            'maturity_period': maturity_period,
            'referral_bonus_applied': referral_bonus_used,
            'message': 'Investment created successfully'
        }

        return Response(response_data, status=status.HTTP_201_CREATED)

class InvestmentListView(generics.ListAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = InvestmentSerializer

    def get_queryset(self):
        return Investment.objects.filter(user=self.request.user)

class ReferralHistoryListView(generics.ListAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = ReferralHistorySerializer

    def get_queryset(self):
        return ReferralHistory.objects.filter(referrer=self.request.user)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_investment(request):
    serializer = InvestmentSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        with transaction.atomic():
            # Create the investment
            investment = Investment.objects.create(
                user=request.user,
                amount=serializer.validated_data['amount'],
                maturity_period=serializer.validated_data['maturity_period'],
                status='pending'
            )
            
            # Calculate return amount (2% per day)
            daily_interest = 0.02  # 2%
            interest = investment.amount * daily_interest * investment.maturity_period
            investment.return_amount = investment.amount + interest
            
            # Check and apply referral bonus if available
            if request.user.referral_earnings > 0 and investment.amount >= request.user.referral_earnings:
                investment.referral_bonus_used = request.user.referral_earnings
                investment.return_amount += request.user.referral_earnings
                
                # Reset user's referral earnings and mark related history as used
                request.user.referral_earnings = 0
                request.user.save()
                
                # Mark referral history as used
                ReferralHistory.objects.filter(
                    referrer=request.user,
                    status='pending'
                ).update(
                    status='used',
                    used_at=timezone.now()
                )
            
            investment.save()
            
            return Response({
                'message': 'Investment created successfully',
                'investment': InvestmentSerializer(investment).data
            }, status=status.HTTP_201_CREATED)
            
    except Exception as e:
        return Response({
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class InvestmentStatementPDFView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request, investment_id):
        # Get the investment or return 404
        investment = get_object_or_404(Investment, id=investment_id, user=request.user)
        
        # Calculate interest earned
        daily_interest_rate = Decimal('0.02')
        interest_earned = investment.amount * daily_interest_rate * investment.maturity_period
        
        # Create the HttpResponse object with PDF headers
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="investment_statement_{investment_id}.pdf"'
        
        # Create the PDF document
        doc = SimpleDocTemplate(response, pagesize=letter)
        styles = getSampleStyleSheet()
        story = []
        
        # Add title
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            spaceAfter=30
        )
        story.append(Paragraph("Investment Statement", title_style))
        story.append(Spacer(1, 20))
        
        # Add statement info
        story.append(Paragraph(f"Statement Date: {timezone.now().strftime('%B %d, %Y')}", styles['Normal']))
        story.append(Paragraph(f"Investment ID: {investment.id}", styles['Normal']))
        story.append(Paragraph(f"Investor: {request.user.username}", styles['Normal']))
        story.append(Spacer(1, 20))
        
        # Investment details table
        data = [
            ['Investment Details', ''],
            ['Principal Amount', f'${investment.amount:,.2f}'],
            ['Interest Rate', '2% per day'],
            ['Maturity Period', f'{investment.maturity_period} days'],
            ['Interest Earned', f'${interest_earned:,.2f}'],
            ['Referral Bonus Applied', f'${investment.referral_bonus_used:,.2f}'],
            ['Total Return Amount', f'${investment.return_amount:,.2f}']
        ]
        
        table = Table(data, colWidths=[4*inch, 2*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 14),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        story.append(table)
        
        # Build PDF
        doc.build(story)
        return response

class ReferralStatementPDFView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        user = request.user
        
        # Get all referral history for the user
        referral_history = ReferralHistory.objects.filter(referrer=user).order_by('-created_at')
        
        # Calculate totals
        total_referrals = referral_history.count()
        active_referrals = referral_history.filter(status='pending').count()
        total_earnings = sum(history.bonus_earned for history in referral_history)
        available_balance = user.referral_earnings
        redeemed_amount = sum(history.bonus_earned for history in referral_history.filter(status='used'))
        
        # Create the HttpResponse object with PDF headers
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="referral_statement_{user.id}.pdf"'
        
        # Create the PDF document
        doc = SimpleDocTemplate(response, pagesize=letter)
        styles = getSampleStyleSheet()
        story = []
        
        # Add title
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            spaceAfter=30
        )
        story.append(Paragraph("Referral Earnings Statement", title_style))
        story.append(Spacer(1, 20))
        
        # Add statement info
        story.append(Paragraph(f"Statement Date: {timezone.now().strftime('%B %d, %Y')}", styles['Normal']))
        story.append(Paragraph(f"Name: {user.username}", styles['Normal']))
        story.append(Paragraph(f"Referral Code: {user.referral_code}", styles['Normal']))
        story.append(Spacer(1, 20))
        
        # Summary table
        summary_data = [
            ['Earnings Summary', ''],
            ['Total Referrals', str(total_referrals)],
            ['Active Referrals', str(active_referrals)],
            ['Total Earnings', f'${total_earnings:,.2f}'],
            ['Available Balance', f'${available_balance:,.2f}'],
            ['Redeemed Amount', f'${redeemed_amount:,.2f}']
        ]
        
        summary_table = Table(summary_data, colWidths=[4*inch, 2*inch])
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 14),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        story.append(summary_table)
        story.append(Spacer(1, 20))
        
        # Referral history table
        if referral_history:
            history_data = [['Referred User', 'Date', 'Investment', 'Bonus', 'Status']]
            for history in referral_history:
                history_data.append([
                    history.referred.username,
                    history.created_at.strftime('%b %d, %Y'),
                    f'${history.amount_invested:,.2f}',
                    f'${history.bonus_earned:,.2f}',
                    history.status.title()
                ])
            
            history_table = Table(history_data, colWidths=[2*inch, 1.5*inch, 1.5*inch, 1.5*inch, 1.5*inch])
            history_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.white),
                ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 10),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('ALIGN', (2, 1), (3, -1), 'RIGHT')
            ]))
            story.append(Paragraph("Referral History", styles['Heading2']))
            story.append(Spacer(1, 10))
            story.append(history_table)
        
        # Build PDF
        doc.build(story)
        return response

class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'accounts/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        # Get user's investments
        investments = Investment.objects.filter(user=user)
        
        # Calculate total returns
        total_returns = investments.filter(status='completed').aggregate(
            total=Sum('return_amount')
        )['total'] or Decimal('0.00')
        
        # Get active investments
        active_investments = investments.filter(status__in=['pending', 'paired'])
        
        # Get pending payments
        pending_payments = Payment.objects.filter(
            from_user=user,
            confirmed_at__isnull=True
        )
        
        # Get queue position
        queue_position = Queue.objects.filter(
            created_at__lt=Queue.objects.filter(user=user).first().created_at
        ).count() if Queue.objects.filter(user=user).exists() else 0
        
        context.update({
            'total_referral_earnings': user.referral_earnings,
            'total_returns': total_returns,
            'active_investments': active_investments,
            'pending_payments': pending_payments,
            'queue_position': queue_position,
            'recent_investments': investments.order_by('-created_at')[:5],
            'referral_link': f"{self.request.scheme}://{self.request.get_host()}/register/?ref={user.referral_code}"
        })
        return context

class BuySharesView(LoginRequiredMixin, TemplateView):
    template_name = 'accounts/buy_shares.html'

    def post(self, request, *args, **kwargs):
        amount = Decimal(request.POST.get('amount', 0))
        maturity_period = int(request.POST.get('maturity_period', 0))
        
        if amount <= 0 or maturity_period <= 0:
            messages.error(request, 'Invalid amount or maturity period')
            return redirect('buy_shares')
        
        # Create investment
        investment = Investment.objects.create(
            user=request.user,
            amount=amount,
            maturity_period=maturity_period
        )
        
        messages.success(request, 'Investment placed successfully!')
        return redirect('dashboard')

class SellSharesView(LoginRequiredMixin, TemplateView):
    template_name = 'accounts/sell_shares.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['payments'] = Payment.objects.filter(
            to_user=self.request.user,
            status='pending'
        ).select_related('from_user', 'investment')
        return context

    def post(self, request, *args, **kwargs):
        payment_id = request.POST.get('payment_id')
        action = request.POST.get('action')  # 'confirm' or 'reject'
        rejection_reason = request.POST.get('rejection_reason', '')
        
        try:
            payment = Payment.objects.get(id=payment_id, to_user=request.user)
            
            if action == 'confirm':
                payment.confirm()
                messages.success(request, 'Payment confirmed successfully!')
            elif action == 'reject':
                payment.reject(rejection_reason)
                messages.warning(request, 'Payment rejected.')
            else:
                messages.error(request, 'Invalid action')
                
        except Payment.DoesNotExist:
            messages.error(request, 'Invalid payment')
            
        return redirect('sell_shares')

class ReferralsView(LoginRequiredMixin, TemplateView):
    template_name = 'accounts/referrals.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        context['referral_histories'] = ReferralHistory.objects.filter(referrer=user)
        context['referral_link'] = f"{self.request.scheme}://{self.request.get_host()}/register/?ref={user.referral_code}"
        return context

class MyInvestmentsView(LoginRequiredMixin, TemplateView):
    template_name = 'accounts/my_investments.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        # Get all investments for the user
        investments = Investment.objects.filter(user=user).order_by('-created_at')
        
        # Calculate statistics
        total_invested = investments.aggregate(total=Sum('amount'))['total'] or 0
        total_returns = investments.aggregate(total=Sum('return_amount'))['total'] or 0
        active_investments = investments.filter(status='pending').count()
        matured_investments = investments.filter(status='matured').count()
        
        context.update({
            'investments': investments,
            'total_invested': total_invested,
            'total_returns': total_returns,
            'active_investments': active_investments,
            'matured_investments': matured_investments,
        })
        return context

class CustomLoginView(LoginView):
    template_name = 'accounts/login.html'
    redirect_authenticated_user = True

class CustomLogoutView(LogoutView):
    next_page = 'login'

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def system_overview(request):
    """Get comprehensive system overview data"""
    # User Statistics
    total_users = User.objects.count()
    
    # Investment Statistics
    investments = Investment.objects.all()
    total_investments = investments.count()
    
    # Investment Status Breakdown
    status_counts = investments.values('status').annotate(
        count=Count('id'),
        total_amount=Sum('amount'),
        avg_amount=Avg('amount')
    )
    
    # Payment Statistics
    payments = Payment.objects.all()
    payment_stats = payments.aggregate(
        total_count=Count('id'),
        total_amount=Sum('amount'),
        avg_amount=Avg('amount')
    )
    
    # Queue Statistics
    queue_stats = Queue.objects.aggregate(
        total_count=Count('id'),
        total_amount=Sum('amount_remaining'),
        avg_amount=Avg('amount_remaining')
    )
    
    # User Investment Details
    user_details = []
    for user in User.objects.all():
        user_investments = Investment.objects.filter(user=user)
        if user_investments.exists():
            user_data = {
                'username': user.username,
                'phone_number': user.phone_number,
                'total_investments': user_investments.count(),
                'investments_by_status': {},
                'payments': {
                    'made': {
                        'count': 0,
                        'total': 0
                    },
                    'received': {
                        'count': 0,
                        'total': 0
                    }
                }
            }
            
            # Investment amounts by status
            for status in ['pending', 'matured', 'paired', 'completed']:
                status_investments = user_investments.filter(status=status)
                if status_investments.exists():
                    total = status_investments.aggregate(total=Sum('amount'))['total']
                    user_data['investments_by_status'][status] = {
                        'count': status_investments.count(),
                        'total': float(total)
                    }
            
            # Payment details
            payments_made = Payment.objects.filter(from_user=user)
            payments_received = Payment.objects.filter(to_user=user)
            
            if payments_made.exists():
                total_sent = payments_made.aggregate(total=Sum('amount'))['total']
                user_data['payments']['made'] = {
                    'count': payments_made.count(),
                    'total': float(total_sent)
                }
            
            if payments_received.exists():
                total_received = payments_received.aggregate(total=Sum('amount'))['total']
                user_data['payments']['received'] = {
                    'count': payments_received.count(),
                    'total': float(total_received)
                }
            
            user_details.append(user_data)
    
    return Response({
        'user_statistics': {
            'total_users': total_users
        },
        'investment_statistics': {
            'total_investments': total_investments,
            'status_breakdown': list(status_counts)
        },
        'payment_statistics': {
            'total_payments': payment_stats['total_count'],
            'total_amount': float(payment_stats['total_amount']),
            'average_amount': float(payment_stats['avg_amount'])
        },
        'queue_statistics': {
            'total_entries': queue_stats['total_count'],
            'total_amount': float(queue_stats['total_amount']),
            'average_amount': float(queue_stats['avg_amount'])
        },
        'user_details': user_details
    })

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_dashboard(request):
    try:
        print("Starting user_dashboard view")  # Debug log
        
        # Get user's investments
        investments = Investment.objects.filter(user=request.user)
        print(f"Found {investments.count()} investments")  # Debug log
        
        # Calculate statistics
        total_returns = investments.filter(status='completed').aggregate(
            total=Sum('return_amount')
        )['total'] or 0
        print(f"Total returns: {total_returns}")  # Debug log

        # Get total referral earnings from ReferralHistory
        total_referral_earnings = ReferralHistory.objects.filter(
            referrer=request.user,
            status='pending'
        ).aggregate(
            total=Sum('bonus_earned')
        )['total'] or 0
        print(f"Total referral earnings: {total_referral_earnings}")  # Debug log

        # Get due earnings from matured investments
        due_earnings = investments.filter(
            status='matured'
        ).aggregate(
            total=Sum('return_amount')
        )['total'] or 0
        print(f"Due earnings: {due_earnings}")  # Debug log

        # Get active investments count
        active_investments = investments.filter(
            status__in=['pending', 'paired']
        ).count()
        print(f"Active investments: {active_investments}")  # Debug log

        # Get pending payments count
        pending_payments = Payment.objects.filter(
            to_user=request.user,
            status='pending'
        ).count()
        print(f"Pending payments: {pending_payments}")  # Debug log

        # Get recent investments
        recent_investments = list(investments.order_by('-created_at')[:5].values(
            'id', 'amount', 'status', 'created_at', 'return_amount',
            'paired_to__username', 'payment_confirmed_at'
        ))
        print(f"Recent investments: {len(recent_investments)}")  # Debug log

        # Get payment data for sell shares section
        payments = list(Payment.objects.filter(
            to_user=request.user,
            status='pending'
        ).select_related('from_user').values(
            'id',
            'amount',
            'created_at',
            'status',
            'from_user__username',
            'from_user__phone_number'
        ).order_by('-created_at'))
        print(f"Payments: {len(payments)}")  # Debug log

        # Get referral data
        referrals = list(ReferralHistory.objects.filter(referrer=request.user).select_related(
            'referred'
        ).values(
            'referred__username',
            'referred__phone_number',
            'status',
            'bonus_earned'
        ))
        print(f"Referrals: {len(referrals)}")  # Debug log

        # Calculate investment status counts
        investment_status_counts = {
            'completed': investments.filter(status='completed').count(),
            'pending': investments.filter(status='pending').count(),
            'paired': investments.filter(status='paired').count(),
            'matured': investments.filter(status='matured').count()
        }
        print(f"Investment status counts: {investment_status_counts}")  # Debug log

        data = {
            'statistics': {
                'total_returns': float(total_returns),
                'total_referral_earnings': float(total_referral_earnings),
                'due_earnings': float(due_earnings),
                'active_investments': active_investments,
                'pending_payments': pending_payments
            },
            'investments': {
                'recent': recent_investments,
                'by_status': investment_status_counts
            },
            'payments': payments,  # Add payments data
            'referral': {
                'total_referrals': len(referrals),
                'referrals': referrals
            }
        }
        
        print("Sending response data:", data)  # Debug log
        return Response(data)
        
    except Exception as e:
        import traceback
        print(f"Dashboard error: {str(e)}")  # Error log
        print("Traceback:", traceback.format_exc())  # Full traceback
        return Response(
            {'error': f'Failed to fetch dashboard data: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
