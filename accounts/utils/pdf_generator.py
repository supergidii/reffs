import os
import pdfkit
from django.template.loader import render_to_string
from django.conf import settings
from datetime import datetime, timedelta

class PDFGenerator:
    @staticmethod
    def generate_investment_statement(investment):
        """
        Generate a PDF statement for an investment
        Args:
            investment: Investment model instance
        Returns:
            str: Path to the generated PDF file
        """
        # Create statements directory if it doesn't exist
        statements_dir = os.path.join(settings.MEDIA_ROOT, 'statements')
        os.makedirs(statements_dir, exist_ok=True)

        # Generate filename with timestamp
        filename = f"investment_statement_{investment.id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        output_path = os.path.join(statements_dir, filename)

        # Prepare context for the template
        context = {
            'user': investment.user,
            'investment': investment,
            'return_amount': investment.return_amount,
            'referral_bonus': investment.referral_bonus_used,
            'interest_earned': investment.return_amount - investment.amount - investment.referral_bonus_used,
            'generated_date': datetime.now(),
            'maturity_date': investment.created_at + timedelta(days=investment.maturity_period),
            'site_name': settings.SITE_NAME,
        }

        # Render HTML template
        html_content = render_to_string('accounts/pdf/investment_statement.html', context)

        # PDF configuration options
        options = {
            'page-size': 'A4',
            'margin-top': '0.75in',
            'margin-right': '0.75in',
            'margin-bottom': '0.75in',
            'margin-left': '0.75in',
            'encoding': "UTF-8",
            'no-outline': None,
            'enable-local-file-access': None,
        }

        # Generate PDF
        pdfkit.from_string(html_content, output_path, options=options)
        
        return output_path

    @staticmethod
    def generate_referral_statement(user, start_date=None, end_date=None):
        """
        Generate a PDF statement for referral earnings
        Args:
            user: User model instance
            start_date: Optional start date for filtering
            end_date: Optional end date for filtering
        Returns:
            str: Path to the generated PDF file
        """
        statements_dir = os.path.join(settings.MEDIA_ROOT, 'statements')
        os.makedirs(statements_dir, exist_ok=True)

        filename = f"referral_statement_{user.id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        output_path = os.path.join(statements_dir, filename)

        # Get referral history
        referrals = user.referralhistory_set.all()
        if start_date:
            referrals = referrals.filter(created_at__gte=start_date)
        if end_date:
            referrals = referrals.filter(created_at__lte=end_date)

        context = {
            'user': user,
            'referrals': referrals,
            'total_earnings': sum(ref.bonus_earned for ref in referrals),
            'total_used': sum(ref.bonus_earned for ref in referrals.filter(status='used')),
            'total_pending': sum(ref.bonus_earned for ref in referrals.filter(status='pending')),
            'generated_date': datetime.now(),
            'start_date': start_date,
            'end_date': end_date,
            'site_name': settings.SITE_NAME,
        }

        html_content = render_to_string('accounts/pdf/referral_statement.html', context)

        options = {
            'page-size': 'A4',
            'margin-top': '0.75in',
            'margin-right': '0.75in',
            'margin-bottom': '0.75in',
            'margin-left': '0.75in',
            'encoding': "UTF-8",
            'no-outline': None,
            'enable-local-file-access': None,
        }

        pdfkit.from_string(html_content, output_path, options=options)
        
        return output_path 