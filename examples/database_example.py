#!/usr/bin/env python3
"""
DealFinder Pro - Database Layer Example
Demonstrates usage of DatabaseManager, SchemaMapper, and SyncManager

This example shows how to:
1. Connect to database
2. Map external data to internal schema
3. Insert/update properties
4. Query properties
5. Manage buyers
6. Create property-buyer matches
"""

import sys
import os
from datetime import datetime

# Add parent directory to path to import modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules.database import DatabaseManager, DatabaseError
from modules.schema_mapper import SchemaMapper, SchemaMapperError


def main():
    """Main example function"""

    print("=" * 80)
    print("DealFinder Pro - Database Layer Example")
    print("=" * 80)
    print()

    # ========================================
    # 1. Initialize Database Connection
    # ========================================
    print("1. Initializing Database Connection...")
    print("-" * 80)

    # SQLite configuration (for demo - no setup required)
    config = {
        'db_type': 'sqlite',
        'database': 'dealfinder_demo.db'
    }

    # For PostgreSQL, use this instead:
    # config = {
    #     'db_type': 'postgresql',
    #     'host': 'localhost',
    #     'port': 5432,
    #     'database': 'dealfinder',
    #     'user': 'postgres',
    #     'password': 'your_password',
    #     'min_connections': 1,
    #     'max_connections': 5
    # }

    try:
        db = DatabaseManager(config)

        # Test connection
        if db.test_connection():
            print("✓ Database connection successful!")
        else:
            print("✗ Database connection failed!")
            return

    except DatabaseError as e:
        print(f"✗ Error initializing database: {e}")
        return

    print()

    # ========================================
    # 2. Initialize Schema Mapper
    # ========================================
    print("2. Initializing Schema Mapper...")
    print("-" * 80)

    # Use the field mappings configuration
    mapping_file = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        'mappings',
        'field_mappings.json'
    )

    try:
        mapper = SchemaMapper(mapping_file)
        print(f"✓ Schema mapper loaded with {len(mapper.list_source_types())} source types:")
        for source_type in mapper.list_source_types():
            print(f"  - {source_type}")
    except SchemaMapperError as e:
        print(f"✗ Error loading mapper: {e}")
        return

    print()

    # ========================================
    # 3. Map and Insert Property Data
    # ========================================
    print("3. Mapping and Inserting Property Data...")
    print("-" * 80)

    # Example: Realtor.com data
    realtor_data = {
        'property_id': 'R_2024_001',
        'mls': 'MLS123456',
        'full_street_line': '123 Beverly Glen Blvd',
        'city': 'Los Angeles',
        'state_code': 'CA',
        'postal_code': '90077',
        'lat': 34.0935,
        'lon': -118.4348,
        'type': 'Single Family',
        'beds': 4,
        'baths': 3.5,
        'sqft': 3200,
        'lot_sqft': 8500,
        'year_built': 1995,
        'list_price': 2450000,
        'price_per_sqft': 765.63,
        'days_on_mls': 45,
        'description': 'Beautiful updated home in prime Beverly Hills location. Motivated seller!',
        'agent_name': 'John Smith',
        'agent_phone': '310-555-1234',
        'agent_email': 'john@realestate.com'
    }

    # Map to internal schema
    property_data = mapper.map_fields(realtor_data, source_type='realtor')

    # Validate required fields
    is_valid, missing_fields = mapper.validate_required_fields(property_data)
    if not is_valid:
        print(f"✗ Missing required fields: {missing_fields}")
        return

    print("✓ Property data mapped successfully")
    print(f"  Address: {property_data['street_address']}, {property_data['city']}")
    print(f"  Price: ${property_data['list_price']:,.0f}")
    print(f"  Beds/Baths: {property_data['bedrooms']}/{property_data['bathrooms']}")

    # Add analysis results (normally calculated by analyzer module)
    property_data.update({
        'opportunity_score': 87,
        'deal_quality': 'GOOD OPPORTUNITY',
        'below_market_percentage': 8.5,
        'estimated_market_value': 2675000,
        'estimated_profit': 225000,
        'analysis_date': datetime.now()
    })

    # Insert into database
    try:
        prop_id = db.insert_property(property_data)
        print(f"✓ Property inserted with ID: {prop_id}")
    except DatabaseError as e:
        print(f"✗ Error inserting property: {e}")

    print()

    # ========================================
    # 4. Query Properties
    # ========================================
    print("4. Querying Properties...")
    print("-" * 80)

    # Get properties by score
    hot_deals = db.get_properties_by_score(min_score=85, limit=10)
    print(f"✓ Found {len(hot_deals)} properties with score >= 85")

    for prop in hot_deals:
        print(f"  • {prop['street_address']}, {prop['city']} - Score: {prop['opportunity_score']}")

    # Get unsynced properties
    unsynced = db.get_unsynced_properties()
    print(f"✓ Found {len(unsynced)} properties pending GHL sync")

    # Get specific property
    prop = db.get_property_by_id('R_2024_001')
    if prop:
        print(f"✓ Retrieved property: {prop['street_address']}")

    print()

    # ========================================
    # 5. Manage Buyers
    # ========================================
    print("5. Managing Buyers...")
    print("-" * 80)

    buyer_data = {
        'ghl_contact_id': 'GHL_CONTACT_001',
        'first_name': 'Jane',
        'last_name': 'Investor',
        'email': 'jane@investor.com',
        'phone': '310-555-9999',
        'min_budget': 2000000,
        'max_budget': 3000000,
        'preferred_locations': ['Los Angeles', 'Beverly Hills', 'Santa Monica'],
        'property_types': ['single_family', 'condo'],
        'min_bedrooms': 3,
        'min_bathrooms': 2.5,
        'buyer_status': 'active',
        'tags': ['active_buyer', 'investor', 'cash_buyer'],
        'sms_opt_in': True
    }

    try:
        buyer_id = db.upsert_buyer(buyer_data)
        print(f"✓ Buyer upserted with ID: {buyer_id}")
        print(f"  Name: {buyer_data['first_name']} {buyer_data['last_name']}")
        print(f"  Budget: ${buyer_data['min_budget']:,.0f} - ${buyer_data['max_budget']:,.0f}")
    except DatabaseError as e:
        print(f"✗ Error upserting buyer: {e}")

    # Get active buyers
    active_buyers = db.get_active_buyers()
    print(f"✓ Found {len(active_buyers)} active buyers")

    print()

    # ========================================
    # 6. Create Property-Buyer Matches
    # ========================================
    print("6. Creating Property-Buyer Matches...")
    print("-" * 80)

    # Calculate match score (simplified - normally done by matching engine)
    match_data = {
        'match_score': 85,
        'match_reasons': [
            'Budget match: Property $2,450,000 within buyer range',
            'Location match: Los Angeles',
            'Property type match: single_family',
            'Bedroom match: 4 >= 3'
        ],
        'sms_sent': False,
        'workflow_triggered': False,
        'task_created': False
    }

    try:
        match_id = db.insert_property_match(prop_id, buyer_id, match_data)
        print(f"✓ Match created with ID: {match_id}")
        print(f"  Match Score: {match_data['match_score']}/100")
        print(f"  Reasons: {len(match_data['match_reasons'])} criteria matched")
    except DatabaseError as e:
        print(f"✗ Error creating match: {e}")

    # Get matches for property
    matches = db.get_matches_for_property(prop_id)
    print(f"✓ Found {len(matches)} matches for this property")

    # Update match actions (simulate SMS sent)
    if matches:
        update_result = db.update_match_actions(match_id, {
            'sms_sent': True,
            'sms_sent_at': datetime.now()
        })
        if update_result:
            print("✓ Match actions updated (SMS sent)")

    print()

    # ========================================
    # 7. Log Sync Operation
    # ========================================
    print("7. Logging Sync Operations...")
    print("-" * 80)

    sync_log_data = {
        'sync_type': 'example_sync',
        'status': 'success',
        'records_processed': 25,
        'records_succeeded': 23,
        'records_failed': 2,
        'error_message': '2 records failed validation',
        'execution_time_seconds': 45,
        'started_at': datetime.now(),
        'completed_at': datetime.now()
    }

    try:
        log_id = db.log_sync(sync_log_data)
        print(f"✓ Sync operation logged with ID: {log_id}")
    except DatabaseError as e:
        print(f"✗ Error logging sync: {e}")

    # Get recent sync history
    recent_syncs = db.get_recent_syncs('example_sync', limit=5)
    print(f"✓ Found {len(recent_syncs)} recent sync operations")

    print()

    # ========================================
    # 8. Cleanup
    # ========================================
    print("8. Cleanup...")
    print("-" * 80)

    db.close()
    print("✓ Database connections closed")

    print()
    print("=" * 80)
    print("Example completed successfully!")
    print("=" * 80)


if __name__ == '__main__':
    main()
