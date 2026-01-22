"""
Test script for WhatsApp message flow with real phone numbers.

Tests:
1. Loyalty Use Case - Send message to Abdoul Aziz KANE (+221774454330)
2. myAgro Use Case - Send reminder to Maryam KANE (+221774187030)

Run with: python test_whatsapp_flow.py
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sentreso.settings.local')
django.setup()

import requests
from apps.masters.models import Master
from apps.agents.models import Agent
from apps.collections.models import Collection
from apps.whatsapp.models import WhatsAppTemplate, WhatsAppMessage

BASE_URL = 'http://localhost:8000/api/v1'


def test_loyalty_use_case():
    """Test Loyalty Use Case - Send message to Abdoul Aziz."""
    print('\n' + '='*60)
    print('TEST 1: LOYALTY USE CASE - Abdoul Aziz KANE')
    print('='*60)
    
    # Get data
    loyalty = Master.objects.get(email='loyalty@pinpay-test.com')
    aziz = Agent.objects.get(master=loyalty, whatsapp_number='+221774454330')
    pending_coll = Collection.objects.filter(master=loyalty, status='pending').first()
    
    print(f'Master: {loyalty.name}')
    print(f'Agent: {aziz.name} ({aziz.whatsapp_number})')
    print(f'API Key: {loyalty.api_key[:20]}...')
    
    headers = {
        'Authorization': f'Bearer {loyalty.api_key}',
        'Content-Type': 'application/json'
    }
    
    # Test 1: List agents
    print('\n--- Test 1.1: List Agents ---')
    response = requests.get(f'{BASE_URL}/agents/', headers=headers)
    print(f'GET /agents/ -> {response.status_code}')
    if response.status_code == 200:
        agents = response.json()
        print(f'  Found {len(agents.get("results", agents))} agent(s)')
    else:
        print(f'  Error: {response.text}')
    
    # Test 2: List collections
    print('\n--- Test 1.2: List Collections ---')
    response = requests.get(f'{BASE_URL}/collections/', headers=headers)
    print(f'GET /collections/ -> {response.status_code}')
    if response.status_code == 200:
        collections = response.json()
        print(f'  Found {len(collections.get("results", collections))} collection(s)')
    else:
        print(f'  Error: {response.text}')
    
    # Test 3: List templates
    print('\n--- Test 1.3: List WhatsApp Templates ---')
    response = requests.get(f'{BASE_URL}/whatsapp/templates/', headers=headers)
    print(f'GET /whatsapp/templates/ -> {response.status_code}')
    if response.status_code == 200:
        templates = response.json()
        print(f'  Found {len(templates.get("results", templates))} template(s)')
        for tpl in templates.get("results", templates):
            print(f'    - {tpl["name"]} ({tpl["template_type"]})')
    else:
        print(f'  Error: {response.text}')
    
    # Test 4: Send custom message
    print('\n--- Test 1.4: Send Custom WhatsApp Message ---')
    message_data = {
        'agent_id': str(aziz.id),
        'content': f'Bonjour {aziz.name}! Ceci est un test de Pinpay. Merci pour votre fidelite chez Fatou!'
    }
    response = requests.post(f'{BASE_URL}/whatsapp/messages/send/', headers=headers, json=message_data)
    print(f'POST /whatsapp/messages/send/ -> {response.status_code}')
    if response.status_code == 200:
        print(f'  Response: {response.json()}')
    else:
        print(f'  Error: {response.text}')
    
    # Test 5: Send collection reminder
    if pending_coll:
        print('\n--- Test 1.5: Send Collection Reminder ---')
        reminder_data = {
            'collection_id': str(pending_coll.id)
        }
        response = requests.post(f'{BASE_URL}/whatsapp/messages/send_reminder/', headers=headers, json=reminder_data)
        print(f'POST /whatsapp/messages/send_reminder/ -> {response.status_code}')
        if response.status_code == 200:
            print(f'  Response: {response.json()}')
        else:
            print(f'  Error: {response.text}')
    
    return True


def test_myagro_use_case():
    """Test myAgro Use Case - Send reminder to Maryam."""
    print('\n' + '='*60)
    print('TEST 2: MYAGRO USE CASE - Maryam KANE (Village Entrepreneur)')
    print('='*60)
    
    # Get data
    myagro = Master.objects.get(email='myagro@pinpay-test.com')
    maryam = Agent.objects.get(master=myagro, whatsapp_number='+221774187030')
    overdue_coll = Collection.objects.filter(master=myagro, status='pending').order_by('due_date').first()
    
    print(f'Master: {myagro.name}')
    print(f'VE: {maryam.name} ({maryam.whatsapp_number})')
    print(f'API Key: {myagro.api_key[:20]}...')
    
    headers = {
        'Authorization': f'Bearer {myagro.api_key}',
        'Content-Type': 'application/json'
    }
    
    # Test 1: List pending collections
    print('\n--- Test 2.1: List Pending Collections ---')
    response = requests.get(f'{BASE_URL}/collections/?status=pending', headers=headers)
    print(f'GET /collections/?status=pending -> {response.status_code}')
    if response.status_code == 200:
        collections = response.json()
        results = collections.get("results", collections)
        print(f'  Found {len(results)} pending collection(s)')
        for coll in results:
            print(f'    - {coll["amount"]} FCFA (due: {coll["due_date"][:10]})')
    else:
        print(f'  Error: {response.text}')
    
    # Test 2: List templates
    print('\n--- Test 2.2: List WhatsApp Templates ---')
    response = requests.get(f'{BASE_URL}/whatsapp/templates/', headers=headers)
    print(f'GET /whatsapp/templates/ -> {response.status_code}')
    if response.status_code == 200:
        templates = response.json()
        print(f'  Found {len(templates.get("results", templates))} template(s)')
        for tpl in templates.get("results", templates):
            print(f'    - {tpl["name"]} ({tpl["template_type"]})')
    else:
        print(f'  Error: {response.text}')
    
    # Test 3: Send custom message to VE
    print('\n--- Test 2.3: Send Custom WhatsApp Message to VE ---')
    message_data = {
        'agent_id': str(maryam.id),
        'content': f'Bonjour {maryam.name}! Rappel de Semences Sahel: Vous avez des paiements agriculteurs en attente. Merci pour votre travail!'
    }
    response = requests.post(f'{BASE_URL}/whatsapp/messages/send/', headers=headers, json=message_data)
    print(f'POST /whatsapp/messages/send/ -> {response.status_code}')
    if response.status_code == 200:
        print(f'  Response: {response.json()}')
    else:
        print(f'  Error: {response.text}')
    
    # Test 4: Send overdue collection reminder
    if overdue_coll and overdue_coll.is_overdue():
        print('\n--- Test 2.4: Send Overdue Collection Reminder ---')
        print(f'  Collection: {overdue_coll.amount} FCFA (OVERDUE)')
        reminder_data = {
            'collection_id': str(overdue_coll.id)
        }
        response = requests.post(f'{BASE_URL}/whatsapp/messages/send_reminder/', headers=headers, json=reminder_data)
        print(f'POST /whatsapp/messages/send_reminder/ -> {response.status_code}')
        if response.status_code == 200:
            print(f'  Response: {response.json()}')
        else:
            print(f'  Error: {response.text}')
    
    return True


def test_dashboard():
    """Test dashboard/reports endpoints."""
    print('\n' + '='*60)
    print('TEST 3: DASHBOARD & REPORTS')
    print('='*60)
    
    myagro = Master.objects.get(email='myagro@pinpay-test.com')
    
    headers = {
        'Authorization': f'Bearer {myagro.api_key}',
        'Content-Type': 'application/json'
    }
    
    # Test dashboard
    print('\n--- Test 3.1: Dashboard Stats ---')
    response = requests.get(f'{BASE_URL}/reports/dashboard/', headers=headers)
    print(f'GET /reports/dashboard/ -> {response.status_code}')
    if response.status_code == 200:
        stats = response.json()
        print(f'  Stats: {stats}')
    else:
        print(f'  Error: {response.text}')
    
    return True


def check_messages_created():
    """Check if WhatsApp messages were created in the database."""
    print('\n' + '='*60)
    print('CHECK: WhatsApp Messages in Database')
    print('='*60)
    
    messages = WhatsAppMessage.objects.all().order_by('-created_at')[:10]
    print(f'Found {messages.count()} recent message(s):')
    
    for msg in messages:
        print(f'  - To: {msg.to_number} | Status: {msg.status} | Content: {msg.content[:50]}...')
    
    return True


if __name__ == '__main__':
    print('='*60)
    print('PINPAY WHATSAPP FLOW TEST')
    print('='*60)
    print('Testing with real WhatsApp numbers:')
    print('  - Abdoul Aziz KANE: +221774454330')
    print('  - Maryam KANE: +221774187030')
    print('='*60)
    
    try:
        # Run tests
        test_loyalty_use_case()
        test_myagro_use_case()
        test_dashboard()
        check_messages_created()
        
        print('\n' + '='*60)
        print('ALL TESTS COMPLETED')
        print('='*60)
        print('\nNote: Messages are queued via Redis/RQ.')
        print('Check the RQ worker to see actual WhatsApp API calls.')
        print('Run: python manage.py rqworker default')
        
    except requests.exceptions.ConnectionError:
        print('\nERROR: Cannot connect to server.')
        print('Make sure the Django server is running:')
        print('  python manage.py runserver')
    except Exception as e:
        print(f'\nERROR: {e}')
        import traceback
        traceback.print_exc()




