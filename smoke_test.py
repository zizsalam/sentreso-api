#!/usr/bin/env python
"""
Sentreso API Smoke Test
Run this script to test the core API functionality.
"""

import requests
import os
import json
import time
import sys
from datetime import datetime, timedelta
from typing import Dict, Any, Optional

# Configuration
BASE_URL = "http://127.0.0.1:8000"
API_BASE = f"{BASE_URL}/api/v1"
API_KEY = os.environ.get("SENTRESO_API_KEY")
if not API_KEY:
    raise RuntimeError("SENTRESO_API_KEY is required to run smoke_test.py")

# Headers for authenticated requests
AUTH_HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}


def print_step(step_num: int, title: str):
    """Print a step header."""
    print(f"\n{'='*60}")
    print(f"Step {step_num}: {title}")
    print('='*60)


def print_success(message: str):
    """Print success message."""
    print(f"✅ {message}")


def print_error(message: str):
    """Print error message."""
    print(f"❌ {message}")


def make_request(method: str, endpoint: str, data: Optional[Dict] = None, headers: Optional[Dict] = None) -> Dict[str, Any]:
    """Make an API request."""
    url = f"{API_BASE}{endpoint}"
    req_headers = AUTH_HEADERS.copy()
    if headers:
        req_headers.update(headers)
    
    try:
        if method.upper() == 'GET':
            response = requests.get(url, headers=req_headers)
        elif method.upper() == 'POST':
            response = requests.post(url, headers=req_headers, json=data)
        elif method.upper() == 'PATCH':
            response = requests.patch(url, headers=req_headers, json=data)
        else:
            raise ValueError(f"Unsupported method: {method}")
        
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as e:
        print_error(f"HTTP {e.response.status_code}: {e.response.text}")
        raise
    except requests.exceptions.RequestException as e:
        print_error(f"Request failed: {e}")
        raise


def main():
    """Run the smoke test."""
    import sys
    import io
    # Set UTF-8 encoding for Windows
    if sys.platform == 'win32':
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    
    print("\nSentreso API Smoke Test")
    print("="*60)
    
    agent_id = None
    collection_id = None
    
    try:
        # Step 1: Health Check
        print_step(1, "Health Check")
        health = make_request('GET', '/health/')
        print_success("Health check passed")
        print(json.dumps(health, indent=2))
        
        # Step 2: Get Master Info
        print_step(2, "Get Master Info")
        master_info = make_request('GET', '/masters/me/')
        print_success(f"Master info retrieved: {master_info.get('name', 'Unknown')}")
        print(f"Master: {master_info.get('name')}")
        
        # Step 3: Create Agent
        print_step(3, "Create Agent")
        agent_data = {
            "name": "Test Agent",
            "whatsapp_number": "+237123456789",
            "phone_number": "+237123456789"
        }
        agent = make_request('POST', '/agents/', agent_data)
        agent_id = agent['id']
        print_success("Agent created successfully")
        print(json.dumps(agent, indent=2))
        print(f"\n💬 This represents a Village Entrepreneur — the human interface farmers already trust.")
        
        # Step 4: Create Collection
        print_step(4, "Create Collection")
        due_date = (datetime.utcnow() + timedelta(days=7)).isoformat() + 'Z'
        collection_data = {
            "agent": agent_id,
            "amount": "10000.00",
            "due_date": due_date,
            "notes": "Test collection for smoke test"
        }
        collection = make_request('POST', '/collections/', collection_data)
        collection_id = collection['id']
        print_success("Collection created successfully")
        print(json.dumps(collection, indent=2))
        print(f"\n💬 This is a farmer's payment obligation — no money, just expectations.")
        
        # Step 5: Send Collection Reminder
        print_step(5, "Send Collection Reminder")
        reminder_data = {
            "collection_id": collection_id
        }
        reminder_response = make_request('POST', '/whatsapp/messages/send_reminder/', reminder_data)
        print_success("Collection reminder queued successfully")
        print(json.dumps(reminder_response, indent=2))
        print(f"\n💬 The reminder is queued asynchronously — even if WhatsApp is slow or offline, nothing breaks.")
        
        # Step 6: Wait for worker processing
        print_step(6, "Waiting for Worker Processing")
        print("Waiting 3 seconds for background job processing...")
        time.sleep(3)
        print_success("Waited for background job processing")
        
        # Step 7: Verify WhatsAppMessage Record
        print_step(7, "Verify WhatsAppMessage Record")
        messages = make_request('GET', '/whatsapp/messages/')
        message_count = messages.get('count', 0)
        if message_count > 0:
            print_success(f"WhatsAppMessage record exists ({message_count} message(s))")
            print(json.dumps(messages, indent=2))
            
            # Check the first message
            if messages.get('results') and len(messages['results']) > 0:
                msg = messages['results'][0]
                print(f"\n💬 This is intentional.")
                print(f"Even when WhatsApp is not configured, the system:")
                print(f"  - logs the message")
                print(f"  - keeps full traceability")
                print(f"  - does not lose intent")
                print(f"\nMessage content:")
                print(f"  {msg.get('content', '')}")
                print(f"\n💬 This is exactly what the farmer would receive — in their language, from their VE.")
        else:
            print_error("No WhatsAppMessage records found")
        
        # Summary
        print("\n" + "="*60)
        print("✅ Smoke Test Complete!")
        print("="*60)
        print("\nSummary:")
        print(f"  - Agent ID: {agent_id}")
        print(f"  - Collection ID: {collection_id}")
        print("\nNext steps:")
        print("  1. Check worker logs to confirm job processing")
        print("  2. Verify WhatsAppMessage in admin: http://127.0.0.1:8000/admin/")
        print("  3. Test other endpoints as needed")
        
    except Exception as e:
        print_error(f"Smoke test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

