# admin_panel/sms_backend.py
import logging
from django.conf import settings

logger = logging.getLogger(__name__)

def send_sms(phone_number: str, message: str):
    """
    Stub function for sending SMS. Replace with Twilio/AWS SNS/etc.
    """
    logger.info(f"[SMS STUB] Sending to {phone_number}: {message}")
    # Example for Twilio:
    # from twilio.rest import Client
    # client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
    # client.messages.create(body=message, from_=settings.TWILIO_FROM_NUMBER, to=phone_number)
