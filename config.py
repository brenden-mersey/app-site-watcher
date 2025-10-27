"""
Site Watcher – Configuration
-----------------------------------------
Contains configuration settings and data used across the app.
"""

# App metadata
APP_NAME = "Site Watcher"
APP_VERSION = "0.1.0"

# Configuration settings
HEALTH_CHECK_MORNING = "08:00"
HEALTH_CHECK_EVENING = "20:00"
REQUEST_TIMEOUT = 15
LOOP_SLEEP_INTERVAL = 60
LOG_FILE_NAME = "site_watcher.log"

# Sites to monitor
SITES = [
    {
        "name": "Kariba",
        "url": "https://kariba.ca/",
        "keywords": [
            "accepting new patients",
            "accepting new patient",
            "new patients welcome",
            "taking new patients",
            "now accepting patients",
            "accepting patients",
            "open to new patients",
            "welcoming new patients",
            # Test keywords that exist on the site
            "clinic",
            "doctor",
            "practice",
            "family practice"
        ],
        "interval_hours": 0.01
    }
]