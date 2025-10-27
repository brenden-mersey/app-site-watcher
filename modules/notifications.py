"""
modules/notifications.py
-----------------------
Send notifications for site watcher.
"""

import datetime
import logging

logger = logging.getLogger(__name__)

def send_health_check_message(client, from_phone, to_phone, stats, sites, reset_stats=True):
    """Send daily health check summary."""
    uptime_hours = (datetime.datetime.now().timestamp() - stats["last_reset"]) / 3600
    
    msg = f"""🏥 Health Check Report

        ✅ Status: Running
        ⏱️ Uptime: {uptime_hours:.1f} hours
        📊 Total Scans: {stats['total_scans']}
        🔔 Total Matches: {stats['total_matches']}
        📈 Sites Monitored: {len(sites)}
    
        Report generated: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}"""
    
    try:
        client.messages.create(body=msg, from_=from_phone, to=to_phone)
        logger.info("✅ Health check sent")
        
        # Optionally reset stats after reporting (for daily reports)
        if reset_stats:
            stats["total_matches"] = 0
            stats["total_scans"] = 0
            stats["last_reset"] = datetime.datetime.now().timestamp()
        
    except Exception as e:
        logger.error(f"📱 Failed to send health check: {str(e)}")


def send_keyword_alert_message(client, from_phone, to_phone, url, keywords_str):
    """Send keyword match alert."""
    msg = f"🔔 Keyword match found on {url}\nKeywords: {keywords_str}"
    
    try:
        client.messages.create(body=msg, from_=from_phone, to=to_phone)
        logger.info(f"✅ Alert sent: {msg}")
    except Exception as e:
        logger.error(f"📱 Failed to send SMS alert for {url}: {str(e)}")


def send_startup_message(client, from_phone, to_phone, sites, health_check_morning, health_check_evening):
    """Send startup notification."""
    sites_info = "\n".join([f"  • {site['url']}" for site in sites])
    
    msg = f"""🚀 Site Watcher Started

        ✅ Monitoring {len(sites)} site(s)
        📅 Started: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}

        Sites:
        {sites_info}

        Health reports scheduled for {health_check_morning} & {health_check_evening} daily"""
    
    try:
        client.messages.create(body=msg, from_=from_phone, to=to_phone)
        logger.info("✅ Startup message sent")
    except Exception as e:
        logger.error(f"📱 Failed to send startup message: {str(e)}")


def send_shutdown_message(client, from_phone, to_phone, stats):
    """Send shutdown notification."""
    uptime_hours = (datetime.datetime.now().timestamp() - stats["last_reset"]) / 3600
    
    msg = f"""🛑 Site Watcher Stopped

        ⏱️ Final Uptime: {uptime_hours:.1f} hours
        📊 Total Scans (session): {stats['total_scans']}
        🔔 Total Matches (session): {stats['total_matches']}
        🕐 Stopped: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}"""
            
    try:
        client.messages.create(body=msg, from_=from_phone, to=to_phone)
        logger.info("✅ Shutdown message sent")
    except Exception as e:
        logger.error(f"📱 Failed to send shutdown message: {str(e)}")