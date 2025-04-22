from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    UserRegistrationView, UserLoginView, UserProfileView,
    InvestmentCreateView, InvestmentListView, PaymentConfirmView,
    ReferralHistoryListView, QueueListView, InvestmentStatementPDFView,
    ReferralStatementPDFView
)

urlpatterns = [
    # Authentication endpoints
    path('register/', UserRegistrationView.as_view(), name='register'),
    path('login/', UserLoginView.as_view(), name='login'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('profile/', UserProfileView.as_view(), name='profile'),
    
    # Investment endpoints
    path('investments/create/', InvestmentCreateView.as_view(), name='investment_create'),
    path('investments/', InvestmentListView.as_view(), name='investment_list'),
    
    # Payment endpoints
    path('payments/confirm/<int:investment_id>/', PaymentConfirmView.as_view(), name='payment_confirm'),
    
    # Referral endpoints
    path('referrals/', ReferralHistoryListView.as_view(), name='referral_list'),
    
    # Queue endpoints
    path('queue/', QueueListView.as_view(), name='queue_list'),

    # Statement PDF endpoints
    path('investments/<int:investment_id>/statement/', InvestmentStatementPDFView.as_view(), name='investment_statement_pdf'),
    path('referrals/statement/', ReferralStatementPDFView.as_view(), name='referral_statement_pdf'),
] 