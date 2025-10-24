import os, time, hashlib, requests, schedule
from bs4 import BeautifulSoup
from twilio.rest import Client
from dotenv import load_dotenv

load_dotenv()

urls = [
    "https://example.com/news",
]
keywords = ["announcement", "funding", "partnership"]
last_hashes = {}

client = Client(os.getenv("TWILIO_SID"), os.getenv("TWILIO_TOKEN"))
TO_PHONE = os.getenv("TO_PHONE")
FROM_PHONE = os.getenv("FROM_PHONE")

def scan_site(url):
    res = requests.get(url, timeout=10)
    res.raise_for_status()
    soup = BeautifulSoup(res.text, "html.parser")
    text = soup.get_text().lower()
    if any(k in text for k in keywords):
        page_hash = hashlib.sha256(text.encode()).hexdigest()
        if last_hashes.get(url) != page_hash:
            last_hashes[url] = page_hash
            client.messages.create(
                body=f"Keyword match on {url}",
                from_=FROM_PHONE,
                to=TO_PHONE
            )
            print(f"[ALERT] Keyword found on {url}")
        else:
            print(f"[OK] No new changes for {url}")
    else:
        print(f"[OK] No keyword match on {url}")

def job():
    print("Running scan...")
    for site in urls:
        try:
            scan_site(site)
        except Exception as e:
            print(f"Error scanning {site}: {e}")

schedule.every().hour.do(job)
print("🕵️‍♀️ Announcement scanner started (hourly)...")
while True:
    schedule.run_pending()
    time.sleep(60)