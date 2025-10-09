#!/usr/bin/env python3
"""
Create test opportunity to discover stage ID
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

from integrations.ghl_connector import GoHighLevelConnector

print("\n" + "=" * 70)
print("  🧪 CREATING TEST OPPORTUNITY")
print("=" * 70)

# Initialize
ghl = GoHighLevelConnector(
    api_key=os.getenv('GHL_API_KEY'),
    location_id=os.getenv('GHL_LOCATION_ID')
)

pipeline_id = os.getenv('GHL_PIPELINE_ID')

print(f"\n✓ Pipeline ID: {pipeline_id}")
print(f"\n📋 Creating minimal test opportunity...\n")

# Try WITHOUT pipelineStageId - see if GHL auto-assigns first stage
test_data = {
    "pipelineId": pipeline_id,
    "name": "🧪 TEST - Stage ID Discovery",
    "monetaryValue": 100000,
    "status": "open"
}

print(f"Creating opportunity:")
print(f"  Name: {test_data['name']}")
print(f"  Value: ${test_data['monetaryValue']:,}")
print(f"  Pipeline: {pipeline_id}")
print(f"  Stage: (auto-assign to first stage)")

try:
    result = ghl.create_opportunity(test_data)

    print(f"\n✅ SUCCESS!\n")
    print("=" * 70)
    print("  RESPONSE DATA")
    print("=" * 70)
    print(json.dumps(result, indent=2))

    # Extract key info
    opp_id = result.get('id', 'N/A')
    stage_id = result.get('pipelineStageId', 'N/A')
    stage_name = result.get('stage', 'Unknown')

    print("\n" + "=" * 70)
    print("  KEY INFORMATION")
    print("=" * 70)
    print(f"\n✓ Opportunity ID: {opp_id}")
    print(f"✓ Stage Name: {stage_name}")
    print(f"✓ Stage ID: {stage_id}")

    print(f"\n💡 This is likely the '{stage_name}' stage!")
    print(f"   Add to .env: GHL_STAGE_NEW={stage_id}")

    print(f"\n📝 You can delete this test opportunity from GHL dashboard")
    print(f"   Or we can use it to discover other stage IDs by moving it")

except Exception as e:
    print(f"\n❌ Error: {str(e)}")
    print("\nTroubleshooting:")
    print("  • Check Pipeline ID in .env")
    print("  • Verify API permissions")

print("\n" + "=" * 70 + "\n")
