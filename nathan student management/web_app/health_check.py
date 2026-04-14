#!/usr/bin/env python3
"""
Student Management System - Health Check Script
This script verifies that all services are running correctly after deployment.
"""

import requests
import sys
import time
from datetime import datetime

def check_service(name, url, timeout=10):
    """Check if a service is responding."""
    try:
        start_time = time.time()
        response = requests.get(url, timeout=timeout)
        response_time = time.time() - start_time

        if response.status_code == 200:
            print(f"✅ {name}: OK ({response_time:.2f}s)")
            return True
        else:
            print(f"❌ {name}: HTTP {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ {name}: Connection failed - {str(e)}")
        return False

def check_database_connection():
    """Check database connectivity through API."""
    try:
        # Try to access a simple API endpoint that requires DB
        response = requests.get("http://localhost/api/auth/status", timeout=10)
        if response.status_code == 200:
            print("✅ Database: Connected")
            return True
        else:
            print(f"❌ Database: HTTP {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Database: Connection failed - {str(e)}")
        return False

def main():
    print("🏥 Student Management System - Health Check")
    print("=" * 50)
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    services = [
        ("Frontend", "http://localhost"),
        ("API Gateway", "http://localhost/api"),
    ]

    all_healthy = True

    for name, url in services:
        if not check_service(name, url):
            all_healthy = False

    # Check database through API
    if not check_database_connection():
        all_healthy = False

    print()
    if all_healthy:
        print("🎉 All services are healthy!")
        sys.exit(0)
    else:
        print("⚠️  Some services are not responding. Check the logs:")
        print("   docker-compose logs -f")
        sys.exit(1)

if __name__ == "__main__":
    main()