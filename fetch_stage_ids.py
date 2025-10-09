#!/usr/bin/env python3
"""
Fetch Pipeline Stage IDs using GHL Connector
"""

import sys
import os

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
print("  🔍 FETCHING PIPELINE STAGE IDs")
print("=" * 70)

# Initialize connector
ghl = GoHighLevelConnector(
    api_key=os.getenv('GHL_API_KEY'),
    location_id=os.getenv('GHL_LOCATION_ID')
)

pipeline_id = os.getenv('GHL_PIPELINE_ID')

print(f"\n✓ Pipeline ID: {pipeline_id}")
print(f"\n📋 Fetching stages for 'Investment Properties' pipeline...\n")

try:
    stages = ghl.get_pipeline_stages(pipeline_id)

    print(f"✅ Found {len(stages)} stages!\n")
    print("=" * 70)

    # Map stage names to env variable names
    stage_mapping = {
        "New Lead": "GHL_STAGE_NEW",
        "Hot Lead": "GHL_STAGE_HOT",
        "Priority Review": "GHL_STAGE_PRIORITY",
        "Showing Scheduled": "GHL_STAGE_SHOWING",
        "Offer Submitted": "GHL_STAGE_OFFER",
        "Under Contract": "GHL_STAGE_CONTRACT",
        "Closed Won": "GHL_STAGE_WON",
        "Closed Lost": "GHL_STAGE_LOST",
        "Cosed Lost": "GHL_STAGE_LOST"  # Handle typo
    }

    env_updates = {}

    for stage in stages:
        stage_name = stage.get('name', 'Unknown')
        stage_id = stage.get('id', 'N/A')

        print(f"  {stage_name}")
        print(f"    ID: {stage_id}")
        print()

        # Map to env variable
        if stage_name in stage_mapping:
            env_var = stage_mapping[stage_name]
            env_updates[env_var] = stage_id

    print("=" * 70)
    print("  📝 ADD THESE TO YOUR .env FILE")
    print("=" * 70)
    print()

    for env_var, stage_id in sorted(env_updates.items()):
        print(f"{env_var}={stage_id}")

    print()
    print("=" * 70)
    print("\nI'll update your .env file now...")

    # Read current .env
    with open('.env', 'r') as f:
        lines = f.readlines()

    # Update stage IDs
    with open('.env', 'w') as f:
        for line in lines:
            written = False
            for env_var, stage_id in env_updates.items():
                if line.strip().startswith(f"{env_var}="):
                    f.write(f"{env_var}={stage_id}\n")
                    written = True
                    break
            if not written:
                f.write(line)

    print("✅ .env file updated successfully!")
    print("\n" + "=" * 70)
    print("  ✅ SETUP COMPLETE!")
    print("=" * 70)
    print("\nYour pipeline is fully configured!")
    print("You can now run the full integration test.\n")

except Exception as e:
    print(f"\n❌ Error: {str(e)}")
    print("\nTroubleshooting:")
    print("  • Make sure Pipeline ID is correct in .env")
    print("  • Check API permissions")
    print(f"\nDetails: {e}")
