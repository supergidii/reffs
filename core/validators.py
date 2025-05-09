from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import time

def validate_bidding_window():
    """Validate that the current time is within bidding windows"""
    current_time = timezone.localtime().time()
    morning_start = time(9, 0)
    morning_end = time(9, 40)
    evening_start = time(17, 0)
    evening_end = time(17, 40)
    
    if not (
        (morning_start <= current_time <= morning_end) or
        (evening_start <= current_time <= evening_end)
    ):
        raise ValidationError(
            "Investments can only be made during bidding windows: "
            "9:00 AM - 9:40 AM or 5:00 PM - 5:40 PM"
        ) 