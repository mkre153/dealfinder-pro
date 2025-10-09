#!/usr/bin/env python3
"""
Test GHL v2 API to fetch pipeline stages
The new GHL API might use different endpoints and require different headers
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
print("  🔍 TESTING GHL v2 API")
print("=" * 70)

api_key = os.getenv('GHL_API_KEY')
location_id = os.getenv('GHL_LOCATION_ID')
pipeline_id = os.getenv('GHL_PIPELINE_ID')

print(f"\n✓ Location ID: {location_id}")
print(f"✓ Pipeline ID: {pipeline_id}")

# Try different v2 API endpoint variations
v2_endpoints = [
    {
        "name": "v2 with Version header",
        "base_url": "https://services.leadconnectorhq.com",
        "endpoint": f"/opportunities/pipelines/{pipeline_id}",
        "headers": {
            'Authorization': f'Bearer {api_key}',
            'Version': '2021-07-28',
            'Content-Type': 'application/json'
        }
    },
    {
        "name": "rest.gohighlevel v1",
        "base_url": "https://rest.gohighlevel.com/v1",
        "endpoint": f"/pipelines/{pipeline_id}",
        "headers": {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }
    },
    {
        "name": "services.leadconnectorhq with location param",
        "base_url": "https://services.leadconnectorhq.com",
        "endpoint": f"/opportunities/pipelines",
        "params": {
            'locationId': location_id,
            'id': pipeline_id
        },
        "headers": {
            'Authorization': f'Bearer {api_key}',
            'Version': '2021-07-28',
            'Content-Type': 'application/json'
        }
    }
]

successful_config = None

for config in v2_endpoints:
    print(f"\n{'='*70}")
    print(f"  Testing: {config['name']}")
    print(f"{'='*70}")

    url = f"{config['base_url']}{config['endpoint']}"
    print(f"\nURL: {url}")

    try:
        params = config.get('params', {})
        response = requests.get(
            url,
            headers=config['headers'],
            params=params,
            timeout=10
        )

        print(f"Status Code: {response.status_code}")

        if response.status_code == 200:
            print(f"\n✅ SUCCESS! This endpoint works!")
            data = response.json()
            print(f"\nResponse:")
            print(json.dumps(data, indent=2))

            successful_config = config

            # Try to extract stages
            if 'pipeline' in data:
                pipeline = data['pipeline']
            elif 'pipelines' in data:
                pipeline = data['pipelines'][0] if data['pipelines'] else {}
            else:
                pipeline = data

            if 'stages' in pipeline:
                print(f"\n🎯 FOUND STAGES!")
                stages = pipeline['stages']
                print(f"\nTotal Stages: {len(stages)}")
                print(f"\n{'='*70}")
                print("  STAGE IDs")
                print(f"{'='*70}\n")

                stage_mapping = {}
                for stage in stages:
                    stage_name = stage.get('name', 'Unknown')
                    stage_id = stage.get('id', 'N/A')
                    print(f"  {stage_name}")
                    print(f"    ID: {stage_id}\n")

                    # Map to env variables
                    name_lower = stage_name.lower().replace(' ', '_')
                    if 'new' in name_lower and 'lead' in name_lower:
                        stage_mapping['GHL_STAGE_NEW'] = stage_id
                    elif 'hot' in name_lower and 'lead' in name_lower:
                        stage_mapping['GHL_STAGE_HOT'] = stage_id
                    elif 'priority' in name_lower:
                        stage_mapping['GHL_STAGE_PRIORITY'] = stage_id
                    elif 'showing' in name_lower:
                        stage_mapping['GHL_STAGE_SHOWING'] = stage_id
                    elif 'offer' in name_lower:
                        stage_mapping['GHL_STAGE_OFFER'] = stage_id
                    elif 'contract' in name_lower:
                        stage_mapping['GHL_STAGE_CONTRACT'] = stage_id
                    elif 'won' in name_lower:
                        stage_mapping['GHL_STAGE_WON'] = stage_id
                    elif 'lost' in name_lower:
                        stage_mapping['GHL_STAGE_LOST'] = stage_id

                if stage_mapping:
                    print(f"{'='*70}")
                    print("  READY TO ADD TO .env")
                    print(f"{'='*70}\n")
                    for key, value in sorted(stage_mapping.items()):
                        print(f"{key}={value}")
                    print()

                    # Save for later use
                    successful_config['stage_mapping'] = stage_mapping
                    successful_config['stages'] = stages

            break  # Found working endpoint, stop trying others

        elif response.status_code == 401:
            print(f"❌ Authentication failed (401)")
        elif response.status_code == 404:
            print(f"❌ Endpoint not found (404)")
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"Response: {response.text[:200]}")

    except Exception as e:
        print(f"❌ Exception: {str(e)}")

# Summary
print(f"\n{'='*70}")
print("  SUMMARY")
print(f"{'='*70}\n")

if successful_config:
    print("✅ Found working API endpoint!")
    print(f"\nWorking Configuration: {successful_config['name']}")
    print(f"Base URL: {successful_config['base_url']}")
    print(f"Endpoint: {successful_config['endpoint']}")

    if 'stage_mapping' in successful_config:
        print(f"\n✅ Successfully extracted {len(successful_config['stage_mapping'])} stage IDs!")
        print("\nNext step: Update .env file with these IDs")
    else:
        print("\n⚠️  API works but couldn't extract stages automatically")
        print("You may need to inspect the response and extract IDs manually")
else:
    print("❌ None of the v2 API endpoints worked")
    print("\nNext steps:")
    print("1. Check GHL API documentation for correct endpoint")
    print("2. Verify API key has correct permissions")
    print("3. Use browser dev tools to manually extract stage IDs")

print(f"\n{'='*70}\n")
