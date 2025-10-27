#!/usr/bin/env python3
"""
Site Watcher – Main App
-------------------------------------------
Runs the site watcher app.
"""

import time, hashlib, requests, schedule, logging, signal, sys, datetime
from bs4 import BeautifulSoup

# Import modules in the pattern style
from config import SITES, HEALTH_CHECK_MORNING, HEALTH_CHECK_EVENING, REQUEST_TIMEOUT, LOOP_SLEEP_INTERVAL, LOG_FILE_NAME
from modules.twilio_handler import initialize_twilio
from modules.notifications import send_startup_message, send_shutdown_message, send_health_check_message, send_keyword_alert_message
from modules.logger import initialize_logger

# Initialize logger
logger = initialize_logger(LOG_FILE_NAME)

# Initialize Twilio
TWILIO_CLIENT, TWILIO_FROM_PHONE, TWILIO_TO_PHONE = initialize_twilio()

# Memory of last seen content
LAST_HASHES = {}

# Track keyword matches and scans
STATS = {
    "total_matches": 0,
    "total_scans": 0,
    "last_reset": time.time()
}

# Helper function to scan a site for keywords
def scan_site(url, keywords):
    """Fetch page, look for keywords, alert on new matches."""
    logger.info(f"Scanning {url} ...")
    STATS["total_scans"] += 1
    
    try:
        # Make HTTP request with timeout
        res = requests.get(url, timeout=REQUEST_TIMEOUT)
        res.raise_for_status()
        
        # Parse HTML content
        text = BeautifulSoup(res.text, "html.parser").get_text().lower()
        
        # Check which keywords were found
        found_keywords = [k for k in keywords if k.lower() in text]
        
        if found_keywords:
            page_hash = hashlib.sha256(text.encode()).hexdigest()
            if LAST_HASHES.get(url) != page_hash:
                LAST_HASHES[url] = page_hash
                keywords_str = ", ".join(found_keywords)
                
                STATS["total_matches"] += 1
                
                # Send keyword alert
                send_keyword_alert_message(TWILIO_CLIENT, TWILIO_FROM_PHONE, TWILIO_TO_PHONE, url, keywords_str)
            else:
                logger.debug("No new content since last check.")
        else:
            logger.debug("No keyword matches found.")
            
    except requests.exceptions.Timeout:
        logger.error(f"⏰ Timeout while fetching {url} ({REQUEST_TIMEOUT}s limit exceeded)")
    except requests.exceptions.ConnectionError:
        logger.error(f"🌐 Connection error while fetching {url} (site may be down)")
    except requests.exceptions.HTTPError as e:
        logger.error(f"🚫 HTTP error {e.response.status_code} while fetching {url}")
    except requests.exceptions.RequestException as e:
        logger.error(f"❌ Request failed for {url}: {str(e)}")
    except Exception as e:
        logger.error(f"💥 Unexpected error while processing {url}: {str(e)}")


def send_health_check_notification():
    """Send health check notification."""
    send_health_check_message(TWILIO_CLIENT, TWILIO_FROM_PHONE, TWILIO_TO_PHONE, STATS, SITES, reset_stats=True)


# Register jobs from config
def register_jobs():
    """Read config and register each site's schedule."""
    for site in SITES:
        name = site["name"]
        url = site["url"]
        keywords = site["keywords"]
        interval_hours = site.get("interval_hours", 1)
        schedule.every(interval_hours).hours.do(scan_site, url, keywords)
        logger.info(f"⏰ Registered {name} ({url}) every {interval_hours}h for {keywords}")

     # Schedule health checks twice a day (morning and evening)
    schedule.every().day.at(HEALTH_CHECK_MORNING).do(send_health_check_notification)
    schedule.every().day.at(HEALTH_CHECK_EVENING).do(send_health_check_notification)

    logger.info(f"📊 Health checks scheduled for {HEALTH_CHECK_MORNING} and {HEALTH_CHECK_EVENING} daily")


# Signal handler for graceful shutdown
def signal_handler(sig, frame):
    """Handle shutdown signals gracefully."""
    logger.info("Received shutdown signal, shutting down gracefully...")
    send_shutdown_message(TWILIO_CLIENT, TWILIO_FROM_PHONE, TWILIO_TO_PHONE, STATS)
    sys.exit(0)


# Main loop
if __name__ == "__main__":
    # Register signal handlers for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)  # Ctrl+C
    signal.signal(signal.SIGTERM, signal_handler)  # Terminate signal
    
    register_jobs()
    logger.info("Announcement scanner running...")
    
    # Send startup notification
    send_startup_message(TWILIO_CLIENT, TWILIO_FROM_PHONE, TWILIO_TO_PHONE, SITES, HEALTH_CHECK_MORNING, HEALTH_CHECK_EVENING)
    
    try:
        while True:
            schedule.run_pending()
            time.sleep(LOOP_SLEEP_INTERVAL)
    except KeyboardInterrupt:
        logger.info("Keyboard interrupt received")
        send_shutdown_message(TWILIO_CLIENT, TWILIO_FROM_PHONE, TWILIO_TO_PHONE, STATS)
    except Exception as e:
        logger.error(f"💥 Fatal error: {str(e)}")
        send_shutdown_message(TWILIO_CLIENT, TWILIO_FROM_PHONE, TWILIO_TO_PHONE, STATS)
        sys.exit(1)