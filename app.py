import os, time, hashlib, json, requests, schedule, logging
from bs4 import BeautifulSoup
from twilio.rest import Client
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('site_watcher.log'),
        logging.StreamHandler()  # Also log to console
    ]
)
logger = logging.getLogger(__name__)

# Load environment + config
load_dotenv()

try:
    with open("config.json", "r") as f:
        CONFIG = json.load(f)
    
    # Basic config validation
    if "sites" not in CONFIG:
        raise ValueError("Config file must contain 'sites' key")
    
    if not isinstance(CONFIG["sites"], list):
        raise ValueError("'sites' must be a list")
    
    if len(CONFIG["sites"]) == 0:
        raise ValueError("No sites configured")
    
    logger.info(f"✅ Loaded config with {len(CONFIG['sites'])} site(s)")
    
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

# Twilio setup with error handling
try:
    twilio_sid = os.getenv("TWILIO_SID")
    twilio_token = os.getenv("TWILIO_TOKEN")
    TO_PHONE = os.getenv("TO_PHONE")
    FROM_PHONE = os.getenv("FROM_PHONE")
    
    if not all([twilio_sid, twilio_token, TO_PHONE, FROM_PHONE]):
        missing = []
        if not twilio_sid: missing.append("TWILIO_SID")
        if not twilio_token: missing.append("TWILIO_TOKEN")
        if not TO_PHONE: missing.append("TO_PHONE")
        if not FROM_PHONE: missing.append("FROM_PHONE")
        raise ValueError(f"Missing required environment variables: {', '.join(missing)}")
    
    client = Client(twilio_sid, twilio_token)
    logger.info("✅ Twilio client initialized successfully")
    
except Exception as e:
    logger.error(f"❌ Failed to initialize Twilio client: {str(e)}")
    exit(1)

# Memory of last seen content
last_hashes = {}

# Helper function to scan a site for keywords
def scan_site(url, keywords):
    """Fetch page, look for keywords, alert on new matches."""
    logger.info(f"Scanning {url} ...")
    
    try:
        # Make HTTP request with timeout
        res = requests.get(url, timeout=15)
        res.raise_for_status()
        
        # Parse HTML content
        text = BeautifulSoup(res.text, "html.parser").get_text().lower()
        
        if any(k.lower() in text for k in keywords):
            page_hash = hashlib.sha256(text.encode()).hexdigest()
            if last_hashes.get(url) != page_hash:
                last_hashes[url] = page_hash
                msg = f"Keyword match found on {url}"
                
                try:
                    client.messages.create(body=msg, from_=FROM_PHONE, to=TO_PHONE)
                    logger.info(f"✅ Alert sent: {msg}")
                except Exception as sms_error:
                    logger.error(f"📱 Failed to send SMS alert for {url}: {str(sms_error)}")
            else:
                logger.debug("No new content since last check.")
        else:
            logger.debug("No keyword matches found.")
            
    except requests.exceptions.Timeout:
        logger.error(f"⏰ Timeout while fetching {url} (15s limit exceeded)")
    except requests.exceptions.ConnectionError:
        logger.error(f"🌐 Connection error while fetching {url} (site may be down)")
    except requests.exceptions.HTTPError as e:
        logger.error(f"🚫 HTTP error {e.response.status_code} while fetching {url}")
    except requests.exceptions.RequestException as e:
        logger.error(f"❌ Request failed for {url}: {str(e)}")
    except Exception as e:
        logger.error(f"💥 Unexpected error while processing {url}: {str(e)}")

# Register jobs from config
def register_jobs():
    """Read config and register each site's schedule."""
    for site in CONFIG["sites"]:
        url = site["url"]
        kws = site["keywords"]
        hours = site.get("interval_hours", 1)
        schedule.every(hours).hours.do(scan_site, url, kws)
        logger.info(f"⏰ Registered {url} every {hours}h for {kws}")

# Main loop
if __name__ == "__main__":
    register_jobs()
    logger.info("Announcement scanner running...")
    while True:
        schedule.run_pending()
        time.sleep(60)