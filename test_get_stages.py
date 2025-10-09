#!/usr/bin/env python3
"""
Test script to create an opportunity and discover stage IDs
"""

import sys
import os
import json

sys.path.insert(0, os.getcwd())

# Load .env
env_path = os.path.join(os.getcwd(), '.env')
if os.path.exists(env_path):
    with open(env_path) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                os.environ[key.strip()] = value.strip()

import requests

print("\n" + "=" * 70)
print("  🔍 FETCHING STAGE IDs FROM GHL")
print("=" * 70)

api_key = os.getenv('GHL_API_KEY')
location_id = os.getenv('GHL_LOCATION_ID')
pipeline_id = os.getenv('GHL_PIPELINE_ID')

print(f"\n✓ Location ID: {location_id}")
print(f"✓ Pipeline ID: {pipeline_id}")

# Try to list all opportunities to see what stages exist
print("\n📋 Attempting to fetch opportunities to discover stage IDs...")

url = f'https://services.leadconnectorhq.com/opportunities/search'

headers = {
    'Authorization': f'Bearer {api_key}',
    'Version': '2021-07-28',
    'Content-Type': 'application/json'
}

params = {
    'location_id': location_id,
    'pipelineId': pipeline_id
}

response = requests.get(url, headers=headers, params=params)

print(f"\nStatus Code: {response.status_code}")

if response.status_code == 200:
    data = response.json()
    print(f"\nResponse: {json.dumps(data, indent=2)}")

    # Look for stage information
    if 'opportunities' in data and len(data['opportunities']) > 0:
        print("\n✓ Found existing opportunities! Stage IDs:")
        for opp in data['opportunities']:
            if 'pipelineStageId' in opp:
                print(f"  • Stage: {opp.get('stage', 'Unknown')} → ID: {opp['pipelineStageId']}")
    else:
        print("\n⚠️  No existing opportunities found.")
        print("We'll create a test opportunity to discover the stage ID.")
else:
    print(f"\n❌ Error: {response.text}")

# Try creating a minimal test opportunity
print("\n" + "=" * 70)
print("  🧪 CREATING TEST OPPORTUNITY")
print("=" * 70)

create_url = 'https://services.leadconnectorhq.com/opportunities/'

test_data = {
    "pipelineId": pipeline_id,
    "locationId": location_id,
    "name": "🧪 TEST - Stage ID Discovery",
    "monetaryValue": 100000,
    "status": "open"
}

print(f"\nCreating test opportunity...")
print(f"  Name: {test_data['name']}")
print(f"  Pipeline: {pipeline_id}")

create_response = requests.post(create_url, headers=headers, json=test_data)

print(f"\nStatus Code: {create_response.status_code}")

if create_response.status_code in [200, 201]:
    result = create_response.json()
    print(f"\n✅ SUCCESS! Response:")
    print(json.dumps(result, indent=2))

    # Extract stage ID
    if 'opportunity' in result:
        opp = result['opportunity']
    else:
        opp = result

    if 'pipelineStageId' in opp:
        print(f"\n🎯 FOUND STAGE ID!")
        print(f"  Stage Name: {opp.get('stage', 'Unknown')}")
        print(f"  Stage ID: {opp['pipelineStageId']}")
        print(f"\nThis is probably the 'New Lead' stage (first stage in pipeline)")
        print(f"\n💡 Add this to your .env as GHL_STAGE_NEW={opp['pipelineStageId']}")

    # Show opportunity ID so user can delete it
    opp_id = opp.get('id', 'N/A')
    print(f"\n📝 Test Opportunity ID: {opp_id}")
    print(f"You can delete this test opportunity from GHL dashboard")
else:
    print(f"\n❌ Error creating opportunity:")
    print(response.text)

print("\n" + "=" * 70)
print("  NEXT STEPS")
print("=" * 70)
print("\nTo get ALL stage IDs, we need to:")
print("1. Move the test opportunity through each stage")
print("2. Or create opportunities in different stages")
print("3. Or use browser dev tools to inspect the HTML")
print("\nAlternatively:")
print("• We can update GHL connector to fetch stages on first run")
print("• Or use the first stage ID we just found and move opportunities programmatically")
print("\n" + "=" * 70 + "\n")
