#!/usr/bin/env python3
"""
Example Usage of GoHighLevel Integration

This script demonstrates how to use the GHL integration modules
for property opportunity management and buyer matching.
"""

import logging
from integrations import GoHighLevelConnector, GHLWorkflowManager, BuyerMatcher
from integrations.ghl_config_example import get_config, validate_config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def example_connection_test():
    """Example: Test GHL connection"""
    print("\n=== Testing GHL Connection ===")

    # Load and validate config
    is_valid, errors = validate_config()
    if not is_valid:
        print("Configuration errors found:")
        for error in errors:
            print(f"  - {error}")
        print("\nPlease update ghl_config.py with your credentials")
        return None

    config = get_config()

    # Initialize connector
    ghl = GoHighLevelConnector(
        api_key=config["api_key"],
        location_id=config["location_id"],
        test_mode=config.get("test_mode", False)
    )

    # Test connection
    if ghl.test_connection():
        print("✓ Successfully connected to GoHighLevel")
        return ghl
    else:
        print("✗ Failed to connect to GoHighLevel")
        return None


def example_create_opportunity(ghl):
    """Example: Create opportunity from property analysis"""
    print("\n=== Creating Opportunity ===")

    if not ghl:
        print("No GHL connection available")
        return

    config = get_config()
    workflow_mgr = GHLWorkflowManager(ghl, config)

    # Sample property data (would come from property analysis module)
    property_data = {
        "address": "123 Main St, Austin, TX 78701",
        "city": "Austin",
        "zip_code": "78701",
        "deal_score": 95,
        "list_price": 350000,
        "estimated_profit": 85000,
        "mls_id": "MLS-12345",
        "below_market_pct": 15.5,
        "days_on_market": 45,
        "price_per_sqft": 180,
        "estimated_arv": 435000,
        "bedrooms": 3,
        "bathrooms": 2,
        "sqft": 1945,
        "year_built": 2015,
        "property_type": "single_family",
        "analysis_breakdown": "Strong deal based on below-market pricing and quick sale potential"
    }

    try:
        # Create opportunity
        opp_id = workflow_mgr.create_opportunity_from_property(property_data)
        print(f"✓ Created opportunity: {opp_id}")

        # Create tasks
        task_ids = workflow_mgr.create_tasks_for_property(property_data, opp_id)
        print(f"✓ Created {len(task_ids)} tasks")

        # Trigger hot deal workflow if applicable
        if property_data["deal_score"] >= 90:
            success = workflow_mgr.trigger_hot_deal_workflow(property_data, opp_id)
            if success:
                print("✓ Triggered hot deal workflow")

        return opp_id

    except Exception as e:
        print(f"✗ Error creating opportunity: {e}")
        return None


def example_buyer_matching(ghl):
    """Example: Match buyers to property"""
    print("\n=== Matching Buyers ===")

    if not ghl:
        print("No GHL connection available")
        return

    config = get_config()

    # Initialize buyer matcher (db_manager=None for this example)
    matcher = BuyerMatcher(ghl, db_manager=None, config=config)

    # Sample property
    property_data = {
        "id": "prop_123",
        "address": "456 Oak Ave, Dallas, TX 75201",
        "city": "Dallas",
        "zip_code": "75201",
        "list_price": 275000,
        "property_type": "single_family",
        "bedrooms": 3,
        "bathrooms": 2.5,
        "sqft": 1850,
        "deal_score": 82
    }

    try:
        # Find matching buyers
        matches = matcher.match_property_to_buyers(property_data, min_score=70)

        if matches:
            print(f"✓ Found {len(matches)} matching buyers:")
            for i, match in enumerate(matches, 1):
                print(f"\n  {i}. {match['name']} ({match['email']})")
                print(f"     Match Score: {match['score']}/100")
                print(f"     Reasons:")
                for reason in match['reasons']:
                    print(f"       - {reason}")

            # Notify matched buyers (in test mode, this just logs)
            stats = matcher.notify_matched_buyers(property_data, matches)
            print(f"\n✓ Notification stats:")
            print(f"   - Notified: {stats['notified']}")
            print(f"   - Skipped: {stats['skipped']}")
            print(f"   - Errors: {len(stats['errors'])}")
        else:
            print("✗ No matching buyers found")

    except Exception as e:
        print(f"✗ Error matching buyers: {e}")


def example_batch_opportunities(ghl):
    """Example: Batch create opportunities"""
    print("\n=== Batch Creating Opportunities ===")

    if not ghl:
        print("No GHL connection available")
        return

    config = get_config()
    workflow_mgr = GHLWorkflowManager(ghl, config)

    # Sample properties
    properties = [
        {
            "address": "789 Elm St, Houston, TX 77001",
            "city": "Houston",
            "deal_score": 88,
            "list_price": 425000,
            "estimated_profit": 65000,
            "mls_id": "MLS-67890",
            "property_type": "single_family"
        },
        {
            "address": "321 Pine Rd, Austin, TX 78702",
            "city": "Austin",
            "deal_score": 92,
            "list_price": 310000,
            "estimated_profit": 95000,
            "mls_id": "MLS-54321",
            "property_type": "townhouse"
        },
        {
            "address": "555 Maple Dr, Dallas, TX 75202",
            "city": "Dallas",
            "deal_score": 76,
            "list_price": 285000,
            "estimated_profit": 48000,
            "mls_id": "MLS-11111",
            "property_type": "condo"
        }
    ]

    try:
        stats = workflow_mgr.batch_create_opportunities(properties)
        print(f"✓ Batch creation complete:")
        print(f"   - Total: {stats['total']}")
        print(f"   - Created: {stats['created']}")
        print(f"   - Failed: {stats['failed']}")

        if stats['errors']:
            print(f"\n  Errors:")
            for error in stats['errors']:
                print(f"    - {error['property']}: {error['error']}")

    except Exception as e:
        print(f"✗ Error in batch creation: {e}")


def example_rate_limiter_demo(ghl):
    """Example: Demonstrate rate limiter in action"""
    print("\n=== Rate Limiter Demo ===")

    if not ghl:
        print("No GHL connection available")
        return

    print(f"Current requests in window: {len(ghl.rate_limiter.requests)}")
    print(f"Remaining capacity: {ghl.rate_limiter.get_remaining_requests()}")

    # Simulate making requests
    print("\nSimulating 10 rapid requests...")
    for i in range(10):
        ghl.rate_limiter.wait_if_needed()  # This will auto-throttle if needed
        print(f"  Request {i+1} - Remaining: {ghl.rate_limiter.get_remaining_requests()}")


def example_custom_field_validation(ghl):
    """Example: Validate custom fields exist"""
    print("\n=== Validating Custom Fields ===")

    if not ghl:
        print("No GHL connection available")
        return

    required_fields = [
        ("deal_score", "opportunity"),
        ("property_address", "opportunity"),
        ("budget_min", "contact"),
        ("budget_max", "contact")
    ]

    try:
        for field_key, field_type in required_fields:
            exists = ghl.validate_custom_field_exists(field_key, field_type)
            status = "✓" if exists else "✗"
            print(f"{status} {field_type}.{field_key}: {'EXISTS' if exists else 'MISSING'}")

    except Exception as e:
        print(f"✗ Error validating fields: {e}")


def main():
    """Run all examples"""
    print("=" * 60)
    print("GoHighLevel Integration - Example Usage")
    print("=" * 60)

    # Test connection
    ghl = example_connection_test()

    if not ghl:
        print("\nCannot proceed without GHL connection.")
        print("Please configure ghl_config.py with your credentials.")
        return

    # Run examples
    example_custom_field_validation(ghl)
    example_rate_limiter_demo(ghl)
    example_create_opportunity(ghl)
    example_buyer_matching(ghl)
    example_batch_opportunities(ghl)

    print("\n" + "=" * 60)
    print("Examples completed!")
    print("=" * 60)


if __name__ == "__main__":
    main()
