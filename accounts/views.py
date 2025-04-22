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
    InvestmentSerializer, PaymentSerializer, QueueSerializer, ReferralHistorySerializer
)
from .models import User, Investment, Payment, Queue, ReferralHistory
from rest_framework.decorators import api_view, permission_classes

# Create your views here.

class UserRegistrationView(generics.CreateAPIView):
    permission_classes = (AllowAny,)
    serializer_class = UserRegistrationSerializer

    def post(self, request, *args, **kwargs):
        print("Registration request received:", request.data)  # Debug print
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            print("Serializer is valid")  # Debug print
            user = serializer.save()
            print("User created:", user.username)  # Debug print
            refresh = RefreshToken.for_user(user)
            response_data = {
                'user': UserSerializer(user).data,
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }
            print("Sending response:", response_data)  # Debug print
            return Response(response_data, status=status.HTTP_201_CREATED)
        print("Serializer errors:", serializer.errors)  # Debug print
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserLoginView(APIView):
    permission_classes = (AllowAny,)
    serializer_class = UserLoginSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            user = authenticate(
                phone_number=serializer.validated_data['phone_number'],
                password=serializer.validated_data['password']
            )
            if user:
                refresh = RefreshToken.for_user(user)
                return Response({
                    'user': UserSerializer(user).data,
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                })
            return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)
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

class PaymentConfirmView(APIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = PaymentSerializer

    @transaction.atomic
    def post(self, request, investment_id):
        try:
            investment = Investment.objects.get(id=investment_id, paired_to=request.user)
            
            # Create payment record
            payment = Payment.objects.create(
                from_user=investment.paired_to,
                to_user=investment.user,
                investment=investment,
                amount=investment.return_amount,
                confirmed_at=timezone.now()
            )
            
            # Update investment status
            investment.is_confirmed = True
            investment.save()
            
            return Response(PaymentSerializer(payment).data)
        except Investment.DoesNotExist:
            return Response({'error': 'Investment not found'}, status=status.HTTP_404_NOT_FOUND)

class ReferralHistoryListView(generics.ListAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = ReferralHistorySerializer

    def get_queryset(self):
        return ReferralHistory.objects.filter(referrer=self.request.user)

class QueueListView(generics.ListAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = QueueSerializer

    def get_queryset(self):
        return Queue.objects.filter(user=self.request.user)

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
                ReferralHistory.objects.filter(
                    referrer=request.user,
                    status='pending'
                ).update(status='used', used_at=timezone.now())
                
                request.user.referral_earnings = 0
                request.user.save()
            
            investment.save()
            
            # If user was referred, calculate referral bonus for referrer
            if request.user.referred_by:
                referral_bonus = investment.amount * 0.03  # 3%
                request.user.referred_by.referral_earnings += referral_bonus
                request.user.referred_by.save()
                
                # Create referral history entry
                ReferralHistory.objects.create(
                    referrer=request.user.referred_by,
                    referred=request.user,
                    amount_invested=investment.amount,
                    bonus_earned=referral_bonus,
                    status='pending'
                )
            
            return Response(
                InvestmentSerializer(investment).data,
                status=status.HTTP_201_CREATED
            )
            
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

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
