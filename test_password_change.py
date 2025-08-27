#!/usr/bin/env python3
"""Test password change functionality"""

import requests

# Base URL
base_url = 'http://localhost:8888'

# Start a session to maintain cookies
session = requests.Session()

print("1️⃣  Logging in with default credentials...")
login_response = session.post(f'{base_url}/login', data={
    'username': 'ucadmin',
    'password': 'MagicUnicorn!8-)'
})

if login_response.status_code == 302:
    print("✅ Login successful")
else:
    print(f"❌ Login failed: {login_response.status_code}")
    exit(1)

print("\n2️⃣  Changing password...")
change_response = session.post(f'{base_url}/api/admin/change-password', json={
    'current_password': 'MagicUnicorn!8-)',
    'new_password': 'NewSecurePassword2025!'
})

if change_response.status_code == 200:
    print("✅ Password changed successfully")
    result = change_response.json()
    print(f"   Response: {result.get('message')}")
else:
    print(f"❌ Password change failed: {change_response.status_code}")
    print(f"   Response: {change_response.text}")

print("\n3️⃣  Testing login with new password...")
# Log out first
session.get(f'{base_url}/logout')

# Try new password
new_login = session.post(f'{base_url}/login', data={
    'username': 'ucadmin',
    'password': 'NewSecurePassword2025!'
})

if new_login.status_code == 302:
    print("✅ Login with new password successful")
else:
    print("❌ Login with new password failed")

print("\n4️⃣  Checking if default message is gone...")
login_page = requests.get(f'{base_url}/login')
if 'Security Notice' in login_page.text:
    print("⚠️  Default message still showing")
else:
    print("✅ Default message no longer shows!")

print("\n5️⃣  Restoring default password for testing...")
restore_response = session.post(f'{base_url}/api/admin/change-password', json={
    'current_password': 'NewSecurePassword2025!',
    'new_password': 'MagicUnicorn!8-)'
})

if restore_response.status_code == 200:
    print("✅ Password restored to default")
    # We should manually reset the password_changed flag in the database
    # but for now this is good enough for testing
else:
    print("⚠️  Could not restore default password")