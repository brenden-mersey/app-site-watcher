"""
Configuration module for site watcher.
Loads and validates configuration from config.json.
"""

import json
import os
import logging
from dotenv import load_dotenv
from twilio.rest import Client

logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

def load_config():
    """Load and validate configuration from config.json."""
    try:
        with open("config.json", "r") as f:
            config = json.load(f)
        
        # Basic config validation
        if "sites" not in config:
            raise ValueError("Config file must contain 'sites' key")
        
        if not isinstance(config["sites"], list):
            raise ValueError("'sites' must be a list")
        
        if len(config["sites"]) == 0:
            raise ValueError("No sites configured")
        
        # Load settings with defaults
        settings = config.get("settings", {})
        health_check_morning = settings.get("health_check_morning", "08:00")
        health_check_evening = settings.get("health_check_evening", "20:00")
        request_timeout = settings.get("request_timeout_seconds", 15)
        loop_sleep_interval = settings.get("loop_sleep_interval_seconds", 60)
        log_file_name = settings.get("log_file_name", "site_watcher.log")
        
        logger.info(f"✅ Loaded config with {len(config['sites'])} site(s)")
        
        return {
            'sites': config['sites'],
            'settings': {
                'health_check_morning': health_check_morning,
                'health_check_evening': health_check_evening,
                'request_timeout': request_timeout,
                'loop_sleep_interval': loop_sleep_interval,
                'log_file_name': log_file_name
            }
        }
        
    except FileNotFoundError:
        logger.error("❌ config.json file not found")
        exit(1)
    except json.JSONDecodeError as e:
        logger.error(f"❌ Invalid JSON in config.json: {str(e)}")
        exit(1)
    except ValueError as e:
        logger.error(f"❌ Config validation error: {str(e)}")
        exit(1)
    except Exception as e:
        logger.error(f"💥 Unexpected error loading config: {str(e)}")
        exit(1)


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
        exit(1)

