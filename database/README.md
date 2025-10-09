# DealFinder Pro - Database Layer

## Overview

This directory contains the complete database layer for DealFinder Pro, including schema definitions, migration scripts, and database management modules.

## Database Architecture

### Supported Databases

- **PostgreSQL 12+** (recommended for production)
- **MySQL 8.0+ / MariaDB 10.5+**
- **SQLite 3.35+** (development/testing only)

### Schema Design

The database consists of four core tables:

1. **properties** - Property listings and analysis results
2. **buyers** - Buyer information synced from GoHighLevel
3. **property_matches** - Property-to-buyer matching records
4. **sync_logs** - Synchronization operation tracking

## Files Structure

```
database/
├── schema.sql                    # Complete PostgreSQL schema
├── migrations/
│   └── 001_initial_schema.sql    # Initial migration
└── README.md                     # This file

modules/
├── database.py                   # DatabaseManager class
├── schema_mapper.py              # Field mapping engine
└── sync_manager.py               # Bidirectional sync coordinator

mappings/
└── field_mappings.json           # Field mapping configuration
```

## Setup Instructions

### 1. PostgreSQL Setup (Recommended)

```bash
# Install PostgreSQL (macOS)
brew install postgresql@14
brew services start postgresql@14

# Create database
createdb dealfinder

# Apply schema
psql dealfinder < database/schema.sql

# Verify setup
psql dealfinder -c "SELECT version FROM schema_version;"
```

### 2. MySQL Setup

```bash
# Install MySQL (macOS)
brew install mysql
brew services start mysql

# Create database
mysql -u root -p -e "CREATE DATABASE dealfinder CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"

# Apply schema (convert PostgreSQL syntax to MySQL)
# Note: schema.sql uses PostgreSQL-specific features (arrays, SERIAL)
# For MySQL, use appropriate data types (JSON for arrays, AUTO_INCREMENT for SERIAL)
```

### 3. SQLite Setup (Development Only)

```bash
# No installation needed - comes with Python
# Schema will be created automatically on first run
```

## Environment Configuration

Create a `.env` file with database credentials:

```bash
# PostgreSQL
DB_TYPE=postgresql
DB_HOST=localhost
DB_PORT=5432
DB_NAME=dealfinder
DB_USER=your_username
DB_PASSWORD=your_password
DB_MIN_CONNECTIONS=1
DB_MAX_CONNECTIONS=5

# Or SQLite (for development)
DB_TYPE=sqlite
DB_NAME=/path/to/dealfinder.db
```

## Usage Examples

### Database Manager

```python
from modules.database import DatabaseManager

# Initialize database connection
config = {
    'db_type': 'postgresql',
    'host': 'localhost',
    'port': 5432,
    'database': 'dealfinder',
    'user': 'postgres',
    'password': 'your_password',
    'min_connections': 1,
    'max_connections': 5
}

db = DatabaseManager(config)

# Test connection
if db.test_connection():
    print("Database connected successfully!")

# Insert property
property_data = {
    'property_id': 'PROP001',
    'street_address': '123 Main St',
    'city': 'Los Angeles',
    'state': 'CA',
    'zip_code': '90210',
    'list_price': 500000.00,
    'bedrooms': 3,
    'bathrooms': 2.0,
    'square_feet': 1500,
    'opportunity_score': 85,
    'deal_quality': 'GOOD OPPORTUNITY',
    'data_source': 'realtor'
}

prop_id = db.insert_property(property_data)
print(f"Inserted property with ID: {prop_id}")

# Get high-scoring properties
hot_deals = db.get_properties_by_score(min_score=90, limit=10)
print(f"Found {len(hot_deals)} hot deals")

# Get unsynced properties
unsynced = db.get_unsynced_properties()
print(f"{len(unsynced)} properties pending GHL sync")

# Close connections
db.close()
```

### Schema Mapper

```python
from modules.schema_mapper import SchemaMapper

# Initialize mapper with configuration
mapper = SchemaMapper('mappings/field_mappings.json')

# Map Realtor.com data to internal schema
realtor_data = {
    'property_id': 'R123456',
    'full_street_line': '456 Oak Ave',
    'city': 'Beverly Hills',
    'state_code': 'CA',
    'postal_code': '90210',
    'list_price': 1200000,
    'beds': 4,
    'baths': 3.5,
    'sqft': 2500,
    'type': 'Single Family'
}

mapped_data = mapper.map_fields(realtor_data, source_type='realtor')
print(mapped_data)

# Validate required fields
is_valid, missing_fields = mapper.validate_required_fields(mapped_data)
if not is_valid:
    print(f"Missing required fields: {missing_fields}")

# Normalize address
address_data = {
    'street_address': '  123  Main   St  ',
    'city': 'los angeles',
    'state': 'California',
    'zip_code': '90210-1234'
}
normalized = mapper.normalize_address(address_data)
# Result: {'street_address': '123 Main St', 'city': 'Los Angeles', 'state': 'CA', 'zip_code': '90210'}
```

### Sync Manager

```python
from modules.sync_manager import SyncManager
from modules.database import DatabaseManager
# from integrations.ghl_connector import GoHighLevelConnector  # Not yet implemented

# Initialize components
db = DatabaseManager(config)
# ghl = GoHighLevelConnector(api_key, location_id)  # Not yet implemented

sync_config = {
    'conflict_resolution': 'ghl_wins',  # or 'db_wins', 'newest_wins', 'manual'
    'sync_threshold_score': 75,
    'batch_size': 50,
    'retry_attempts': 3
}

sync_manager = SyncManager(db, ghl, sync_config)

# Sync properties to GHL
stats = sync_manager.sync_properties_to_ghl(min_score=80)
print(f"Sync complete: {stats}")
# Output: {'total_processed': 25, 'created': 20, 'updated': 3, 'failed': 2, 'errors': [...]}

# Import buyers from GHL
buyer_stats = sync_manager.sync_buyers_from_ghl()
print(f"Buyer sync: {buyer_stats}")
```

## Database Schema Details

### Properties Table

Core fields:
- **Identifiers**: id, property_id, mls_number
- **Address**: street_address, city, state, zip_code, county, lat/lon
- **Details**: property_type, beds, baths, sqft, lot_size, year_built
- **Financial**: list_price, price_per_sqft, taxes, HOA fees
- **Analysis**: opportunity_score (0-100), deal_quality, estimated_profit
- **GHL Sync**: ghl_opportunity_id, ghl_sync_status, ghl_sync_date

### Buyers Table

Core fields:
- **Identifiers**: id, ghl_contact_id
- **Contact**: first_name, last_name, email, phone
- **Preferences**: budget range, preferred_locations[], property_types[]
- **Status**: buyer_status, tags[], sms_opt_in

### Property Matches Table

Core fields:
- **Relationship**: property_id, buyer_id
- **Scoring**: match_score (0-100), match_reasons[]
- **Actions**: sms_sent, workflow_triggered, task_created

### Sync Logs Table

Core fields:
- **Operation**: sync_type, status, started_at, completed_at
- **Statistics**: records_processed, records_succeeded, records_failed
- **Debugging**: error_message, execution_time_seconds

## Views

Pre-built views for common queries:

```sql
-- Hot deals (score >= 90)
SELECT * FROM vw_hot_deals;

-- Unsynced properties (pending GHL export)
SELECT * FROM vw_unsynced_properties;

-- Active buyers
SELECT * FROM vw_active_buyers;

-- Recent matches (last 7 days)
SELECT * FROM vw_recent_matches;

-- Sync statistics
SELECT * FROM vw_sync_statistics;
```

## Database Functions

Utility functions:

```sql
-- Get properties by score range
SELECT * FROM get_properties_by_score_range(75, 100);

-- Get match count for property
SELECT get_match_count(property_id);
```

## Indexes

Performance indexes created:
- `opportunity_score` (DESC) - Fast high-score queries
- `deal_quality` - Filter by quality tier
- `days_on_market` - Sort by DOM
- `ghl_sync_status` - Find unsynced records
- `created_at` (DESC) - Recent properties first
- `zip_code`, `city` - Geographic filtering
- `list_price` - Price range queries

## Maintenance

### Backup Database

```python
# Using DatabaseManager
db.backup_database('/path/to/backups/dealfinder_2025-10-08.dump')

# Or manually (PostgreSQL)
pg_dump -h localhost -U postgres -F c -f backup.dump dealfinder
```

### Restore Database

```bash
# PostgreSQL
pg_restore -h localhost -U postgres -d dealfinder backup.dump

# Or recreate from schema
psql dealfinder < database/schema.sql
```

### Cleanup Old Records

```python
# Delete properties older than 365 days (not synced to GHL)
stats = db.cleanup_old_records(retention_days=365)
print(f"Deleted {stats['properties_deleted']} properties, {stats['logs_deleted']} logs")
```

### Database Migrations

For schema changes, create new migration files:

```bash
database/migrations/
├── 001_initial_schema.sql        # Already applied
├── 002_add_photo_urls.sql        # Future migration
└── 003_add_market_analytics.sql  # Future migration
```

Track applied migrations in `schema_version` table.

## Performance Tuning

### Connection Pooling

Connection pool automatically manages database connections:
- Minimum connections: 1 (configurable)
- Maximum connections: 5 (configurable)
- Automatic connection recycling
- Thread-safe for concurrent operations

### Query Optimization

All high-frequency queries use indexes:
- Property score lookups: `idx_properties_opportunity_score`
- Sync status filtering: `idx_properties_ghl_sync_status`
- Geographic searches: `idx_properties_zip_code`, `idx_properties_city`

### Transaction Management

All database operations use context managers for automatic:
- Transaction commit on success
- Rollback on error
- Connection cleanup

## Error Handling

### Common Errors

**Connection Failed**
```python
DatabaseError: Database initialization failed: connection refused
```
Solution: Verify database is running and credentials are correct.

**Duplicate Key**
```python
psycopg2.errors.UniqueViolation: duplicate key value violates unique constraint
```
Solution: Use `update_property()` instead of `insert_property()`, or the database will handle it automatically.

**Missing Required Fields**
```python
SchemaMapperError: Missing required fields: ['property_id', 'list_price']
```
Solution: Ensure source data contains all required fields before mapping.

## Security Considerations

1. **SQL Injection Prevention**: All queries use parameterized statements
2. **Credential Management**: Store credentials in `.env` file, never in code
3. **Connection Encryption**: Use SSL/TLS for production databases
4. **Access Control**: Grant minimum necessary permissions to database user

## Testing

Run database tests:

```bash
# Unit tests
pytest tests/test_database.py -v

# Integration tests (requires running database)
pytest tests/test_database_integration.py -v
```

## Troubleshooting

### Connection Issues

```python
# Test database connectivity
if not db.test_connection():
    print("Connection failed - check credentials and database status")
```

### Slow Queries

```sql
-- Enable query logging (PostgreSQL)
ALTER DATABASE dealfinder SET log_statement = 'all';

-- Check for missing indexes
EXPLAIN ANALYZE SELECT * FROM properties WHERE opportunity_score >= 85;
```

### Lock Conflicts

If experiencing deadlocks:
- Reduce `max_connections` in config
- Ensure transactions are short-lived
- Check for long-running queries

## Support

For database-related issues:
1. Check logs in `logs/database.log`
2. Review sync logs: `SELECT * FROM sync_logs ORDER BY started_at DESC LIMIT 10;`
3. Verify schema version: `SELECT * FROM schema_version;`

## License

Copyright 2025 DealFinder Pro. All rights reserved.
