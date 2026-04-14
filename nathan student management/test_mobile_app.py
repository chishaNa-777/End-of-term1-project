#!/usr/bin/env python3
"""
Mobile App Integration Test
Tests the connection between mobile app and Flask API
"""

import requests
import json
import time

def test_api_connection():
    """Test basic API connectivity"""
    print("Testing API connection...")

    try:
        response = requests.get('http://localhost:5000/health')
        if response.status_code == 200:
            print("✅ API server is running")
            return True
        else:
            print(f"❌ API server responded with status {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to API server. Make sure server.py is running.")
        return False

def test_login():
    """Test parent login"""
    print("\nTesting parent login...")

    login_data = {
        'username': 'parent_john',
        'password': 'john123'
    }

    try:
        response = requests.post('http://localhost:5000/api/login',
                               json=login_data,
                               headers={'Content-Type': 'application/json'})

        if response.status_code == 200:
            data = response.json()
            if 'token' in data:
                print("✅ Login successful")
                return data['token']
            else:
                print("❌ Login failed: No token received")
                return None
        else:
            print(f"❌ Login failed with status {response.status_code}: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Login error: {e}")
        return None

def test_dashboard(token):
    """Test dashboard access"""
    print("\nTesting dashboard access...")

    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }

    try:
        response = requests.get('http://localhost:5000/api/parent/dashboard',
                              headers=headers)

        if response.status_code == 200:
            data = response.json()
            if 'children' in data:
                print(f"✅ Dashboard loaded successfully. Found {len(data['children'])} children.")
                return data
            else:
                print("❌ Dashboard response missing children data")
                return None
        else:
            print(f"❌ Dashboard access failed with status {response.status_code}: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Dashboard error: {e}")
        return None

def test_static_files():
    """Test static file serving"""
    print("\nTesting static file serving...")

    try:
        response = requests.get('http://localhost:5000/mobile_app.html')
        if response.status_code == 200:
            print("✅ Mobile app HTML served successfully")
        else:
            print(f"❌ Mobile app HTML failed with status {response.status_code}")
            return False

        response = requests.get('http://localhost:5000/manifest.json')
        if response.status_code == 200:
            print("✅ Manifest JSON served successfully")
        else:
            print(f"❌ Manifest JSON failed with status {response.status_code}")
            return False

        return True
    except Exception as e:
        print(f"❌ Static file error: {e}")
        return False

def main():
    print("🧪 Mobile App Integration Test")
    print("=" * 40)

    # Test 1: API Connection
    if not test_api_connection():
        print("\n❌ Basic connectivity test failed. Please start the server with: python server.py")
        return

    # Test 2: Static Files
    if not test_static_files():
        print("\n❌ Static file serving test failed.")
        return

    # Test 3: Authentication
    token = test_login()
    if not token:
        print("\n❌ Authentication test failed. Check parent credentials in database.")
        return

    # Test 4: Dashboard
    dashboard_data = test_dashboard(token)
    if not dashboard_data:
        print("\n❌ Dashboard test failed.")
        return

    print("\n" + "=" * 40)
    print("🎉 All tests passed! Mobile app is ready.")
    print("\nNext steps:")
    print("1. Open http://localhost:5000 in your browser")
    print("2. Login with parent credentials (parent_john/john123)")
    print("3. Test the mobile interface")
    print("4. For mobile devices, add to home screen as PWA")

if __name__ == '__main__':
    main()