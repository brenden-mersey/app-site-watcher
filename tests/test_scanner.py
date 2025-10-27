#!/usr/bin/env python3
"""
Test script to verify the site watcher scanner functionality.
"""

import sys
import os

# Add parent directory to path to import app module
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import scan_site, SITES

def test_site_scanner():
    """Test the site scanner functionality."""
    print("🧪 Testing Site Watcher...")
    print(f"Testing {len(SITES)} site(s)\n")
    
    for site in SITES:
        name = site["name"]
        url = site["url"]
        keywords = site["keywords"]
        
        print(f"📋 Testing: {name}")
        print(f"   URL: {url}")
        print(f"   Keywords: {keywords[:3]}... ({len(keywords)} total)")
        print()
        
        # Run a test scan
        try:
            scan_site(url, keywords)
            print("✅ Test scan completed successfully\n")
        except Exception as e:
            print(f"❌ Test scan failed: {e}\n")
    
    print("🎉 Test complete!")

if __name__ == "__main__":
    test_site_scanner()

