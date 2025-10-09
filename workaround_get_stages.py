#!/usr/bin/env python3
"""
Workaround: Create test opportunities to discover stage IDs
Since we can't query the pipeline API, we'll:
1. Create opportunity without stage ID (should auto-assign to first stage)
2. Get the stage ID from the created opportunity
3. Guide user to move it and get other stage IDs
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
print("  🔧 WORKAROUND: Discover Stage IDs via Opportunity Creation")
print("=" * 70)

api_key = os.getenv('GHL_API_KEY')
location_id = os.getenv('GHL_LOCATION_ID')
pipeline_id = os.getenv('GHL_PIPELINE_ID')

print(f"\n✓ Location ID: {location_id}")
print(f"✓ Pipeline ID: {pipeline_id}")

print("\n" + "=" * 70)
print("  STEP 1: Create Test Opportunity")
print("=" * 70)

# Try to create opportunity with minimal data
# Test both v1 and alternative endpoints

endpoints_to_try = [
    {
        "name": "rest.gohighlevel.com/v1",
        "url": "https://rest.gohighlevel.com/v1/opportunities/",
        "headers": {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }
    },
    {
        "name": "services.leadconnectorhq.com",
        "url": "https://services.leadconnectorhq.com/opportunities/",
        "headers": {
            'Authorization': f'Bearer {api_key}',
            'Version': '2021-07-28',
            'Content-Type': 'application/json'
        }
    }
]

# Minimal opportunity data
opp_data = {
    "locationId": location_id,
    "pipelineId": pipeline_id,
    "name": "🧪 TEST - Stage ID Discovery",
    "monetaryValue": 100000,
    "status": "open"
}

print(f"\nTrying to create test opportunity...")
print(f"  Name: {opp_data['name']}")
print(f"  Pipeline: {pipeline_id}")

successful_endpoint = None
created_opportunity = None

for endpoint_config in endpoints_to_try:
    print(f"\nTrying endpoint: {endpoint_config['name']}")

    try:
        response = requests.post(
            endpoint_config['url'],
            headers=endpoint_config['headers'],
            json=opp_data,
            timeout=10
        )

        print(f"Status Code: {response.status_code}")

        if response.status_code in [200, 201]:
            print(f"✅ SUCCESS!")
            result = response.json()

            # Extract opportunity data
            if 'opportunity' in result:
                created_opportunity = result['opportunity']
            else:
                created_opportunity = result

            successful_endpoint = endpoint_config

            print(f"\nResponse:")
            print(json.dumps(result, indent=2))
            break

        else:
            print(f"❌ Failed: {response.status_code}")
            if response.text:
                print(f"Response: {response.text[:200]}")

    except Exception as e:
        print(f"❌ Exception: {str(e)}")

if created_opportunity:
    print("\n" + "=" * 70)
    print("  ✅ OPPORTUNITY CREATED!")
    print("=" * 70)

    opp_id = created_opportunity.get('id', 'N/A')
    stage_id = created_opportunity.get('pipelineStageId', 'N/A')
    stage_name = created_opportunity.get('stageName', created_opportunity.get('stage', 'Unknown'))

    print(f"\nOpportunity ID: {opp_id}")
    print(f"Stage Name: {stage_name}")
    print(f"Stage ID: {stage_id}")

    if stage_id and stage_id != 'N/A':
        print(f"\n🎯 GOT FIRST STAGE ID!")
        print(f"\nThis is likely the '{stage_name}' stage")
        print(f"Add to .env: GHL_STAGE_NEW={stage_id}")

        print(f"\n" + "=" * 70)
        print("  NEXT: Get Remaining Stage IDs")
        print("=" * 70)

        print(f"\nOption A - Manual (in GHL Dashboard):")
        print(f"1. Go to GHL → Opportunities")
        print(f"2. Find: '{opp_data['name']}'")
        print(f"3. Drag it to 'Hot Lead' stage")
        print(f"4. Come back and run: python3 get_stage_from_opportunity.py {opp_id}")
        print(f"5. Repeat for each stage")

        print(f"\nOption B - Programmatic (if API allows):")
        print(f"1. I'll try to move the opportunity via API")
        print(f"2. Each move will give us a stage ID")

        # Save opportunity ID for future reference
        with open('.test_opportunity_id.txt', 'w') as f:
            f.write(opp_id)

        print(f"\n💾 Saved opportunity ID to .test_opportunity_id.txt")

    print(f"\n📝 You can delete this test opportunity from GHL after we get all stage IDs")

else:
    print("\n" + "=" * 70)
    print("  ❌ COULD NOT CREATE OPPORTUNITY")
    print("=" * 70)

    print(f"\nNone of the API endpoints worked for creating opportunities.")
    print(f"\nThis means:")
    print(f"1. API key might not have opportunity creation permissions")
    print(f"2. Or endpoints have changed")
    print(f"3. Or there's a required field we're missing")

    print(f"\n" + "=" * 70)
    print("  RECOMMENDED: Manual Stage ID Extraction")
    print("=" * 70)

    print(f"\nPlease use the browser method:")
    print(f"1. Open: GET_STAGE_IDS.md")
    print(f"2. Follow Option 1 (JavaScript console) - takes 2 minutes")
    print(f"3. Send me the output")
    print(f"\nOr just tell me 'skip stages for now' and we can:")
    print(f"- Test without stage IDs")
    print(f"- Let GHL auto-assign stages")
    print(f"- You can add stage IDs later")

print("\n" + "=" * 70 + "\n")
