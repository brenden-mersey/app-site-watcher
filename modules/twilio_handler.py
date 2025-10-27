"""
modules/twilio_handler.py
-----------------------
Twilio client initialization and management.
"""

import os
import logging
from twilio.rest import Client
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()


def initialize_twilio():
    """Initialize Twilio client with credentials from environment."""
    try:
        twilio_sid = os.getenv("TWILIO_SID")
        twilio_token = os.getenv("TWILIO_TOKEN")
        to_phone = os.getenv("TO_PHONE")
        from_phone = os.getenv("FROM_PHONE")
        
        if not all([twilio_sid, twilio_token, to_phone, from_phone]):
            missing = []
            if not twilio_sid: missing.append("TWILIO_SID")
            if not twilio_token: missing.append("TWILIO_TOKEN")
            if not to_phone: missing.append("TO_PHONE")
            if not from_phone: missing.append("FROM_PHONE")
            raise ValueError(f"Missing required environment variables: {', '.join(missing)}")
        
        client = Client(twilio_sid, twilio_token)
        logger.info("✅ Twilio client initialized successfully")
        
        return client, from_phone, to_phone
        
    except Exception as e:
        logger.error(f"❌ Failed to initialize Twilio client: {str(e)}")
        raise


def get_twilio_credentials():
    """Get Twilio credentials from environment variables."""
    return {
        'sid': os.getenv("TWILIO_SID"),
        'token': os.getenv("TWILIO_TOKEN"),
        'to_phone': os.getenv("TO_PHONE"),
        'from_phone': os.getenv("FROM_PHONE")
    }

