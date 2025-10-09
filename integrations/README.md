# GoHighLevel CRM Integration

Complete API integration with GoHighLevel CRM for automated property opportunity management and intelligent buyer matching.

## Overview

This integration provides:
- **Rate-limited API connector** (95 req/min to stay under GHL's 100 req/min limit)
- **Automated opportunity creation** from property analysis
- **Intelligent buyer-property matching** with scoring algorithm
- **Workflow automation** for hot deals and notifications
- **SMS/Email notifications** with quiet hours and daily limits
- **Task management** for follow-ups and showings
- **Comprehensive error handling** with retries and exponential backoff

## Files

### Core Modules

1. **`ghl_connector.py`** (590 lines)
   - Main GHL API client with rate limiting
   - Handles all HTTP communication with GHL API v1
   - Features:
     - Rate limiter preventing >95 requests/minute
     - Retry logic for 429, 500 errors (3 attempts with exponential backoff)
     - Test mode for dry runs
     - Contact, Opportunity, Task, Workflow management
     - SMS/Email sending
     - Custom field validation

2. **`ghl_workflows.py`** (344 lines)
   - Workflow automation and opportunity lifecycle management
   - Features:
     - Create opportunities from property data
     - Trigger hot deal workflows (score >= 90)
     - Auto-create tasks (review, showing, buyer contact)
     - Progress opportunities through pipeline stages
     - Send hot deal SMS alerts (respects quiet hours)
     - Batch opportunity creation with stats

3. **`ghl_buyer_matcher.py`** (440 lines)
   - Intelligent buyer-property matching engine
   - Features:
     - Fetch and cache active buyers
     - Calculate match scores (0-100) based on:
       - Budget match (40 points)
       - Location match (30 points)
       - Property type (20 points)
       - Bedrooms (10 points)
     - Notify matched buyers via SMS/workflows
     - Enforce SMS limits (max 3/day per buyer)
     - Respect quiet hours (9 PM - 8 AM)
     - Create follow-up tasks

### Configuration

4. **`ghl_field_mapping.json`**
   - Custom field definitions for contacts and opportunities
   - Pipeline stages and workflow configurations
   - Tag definitions
   - Field validation rules
   - Notification and rate limiting settings

5. **`ghl_config_example.py`**
   - Template for GHL credentials and configuration
   - Copy to `ghl_config.py` and update with your values
   - Includes configuration validator

6. **`__init__.py`**
   - Module initialization
   - Exports main classes for easy importing

## Setup

### 1. Install Dependencies

```bash
pip install requests
```

### 2. Configure GHL Settings

1. Copy configuration template:
   ```bash
   cp integrations/ghl_config_example.py integrations/ghl_config.py
   ```

2. Get your GHL credentials:
   - API Key: GHL Settings → Integrations → API
   - Location ID: GHL Settings → Business Profile
   - Pipeline ID: GHL → Opportunities → Settings
   - Stage IDs: Inspect pipeline stages in GHL
   - Workflow IDs: GHL → Automations

3. Update `ghl_config.py` with your values

4. Validate configuration:
   ```bash
   python integrations/ghl_config_example.py
   ```

### 3. Create Custom Fields in GHL

Create these custom fields in your GHL account:

**Contact/Buyer Fields:**
- `budget_min` (Number)
- `budget_max` (Number)
- `location_preference` (Text)
- `property_type_preference` (Text)
- `min_bedrooms` (Number)
- `buyer_status` (Text)

**Opportunity/Property Fields:**
- `property_address` (Text)
- `deal_score` (Number, 0-100)
- `list_price` (Number)
- `est_profit` (Number)
- `mls_id` (Text)
- `price_per_sqft` (Number)
- `below_market_pct` (Number)
- `days_on_market` (Number)
- `deal_quality` (Text)
- `estimated_arv` (Number)
- `bedrooms` (Number)
- `bathrooms` (Number)
- `sqft` (Number)
- `year_built` (Number)
- `property_type` (Text)

### 4. Create Tags in GHL

Create these tags:
- `active_buyer` - For buyers actively looking
- `sms_opt_in` - For SMS notification consent
- `email_opt_in` - For email consent
- `automated` - Applied to automated opportunities
- `dealfinder` - Applied by DealFinder Pro
- `hot_deal` - Score >= 90
- `good_deal` - Score 75-89
- `potential` - Score 60-74

## Usage

### Basic Usage

```python
from integrations import GoHighLevelConnector, GHLWorkflowManager, BuyerMatcher
from integrations.ghl_config_example import get_config

# Load configuration
config = get_config()

# Initialize connector
ghl = GoHighLevelConnector(
    api_key=config["api_key"],
    location_id=config["location_id"],
    test_mode=False
)

# Test connection
if not ghl.test_connection():
    print("Failed to connect to GHL")
    exit(1)

print("Connected to GHL successfully!")
```

### Create Opportunity from Property

```python
# Initialize workflow manager
workflow_mgr = GHLWorkflowManager(ghl, config)

# Property data from analysis
property_data = {
    "address": "123 Main St, Austin, TX 78701",
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
    "property_type": "single_family"
}

# Create opportunity
opp_id = workflow_mgr.create_opportunity_from_property(property_data)
print(f"Created opportunity: {opp_id}")

# Create tasks
task_ids = workflow_mgr.create_tasks_for_property(property_data, opp_id)
print(f"Created {len(task_ids)} tasks")

# Trigger hot deal workflow (if score >= 90)
if property_data["deal_score"] >= 90:
    workflow_mgr.trigger_hot_deal_workflow(property_data, opp_id)
```

### Match and Notify Buyers

```python
# Initialize buyer matcher (requires database manager)
matcher = BuyerMatcher(ghl, db_manager=None, config=config)

# Find matching buyers
matches = matcher.match_property_to_buyers(property_data, min_score=70)
print(f"Found {len(matches)} matching buyers")

# Display matches
for match in matches:
    print(f"  - {match['name']}: {match['score']}/100")
    print(f"    Reasons: {', '.join(match['reasons'])}")

# Notify matched buyers
stats = matcher.notify_matched_buyers(property_data, matches)
print(f"Notified {stats['notified']} buyers, skipped {stats['skipped']}")
```

### Batch Create Opportunities

```python
properties = [
    # ... list of property data dictionaries
]

stats = workflow_mgr.batch_create_opportunities(properties)
print(f"Created: {stats['created']}, Failed: {stats['failed']}")
```

## Rate Limiting Strategy

The integration implements a sophisticated rate limiting system:

1. **Request Tracking**: Uses `deque` to track timestamps of last 95 requests
2. **Auto-Wait**: Automatically sleeps when approaching limit (95 req/min)
3. **429 Handling**: Respects `Retry-After` header from GHL
4. **Buffer**: Uses 95/100 limit to provide safety margin
5. **Time Window**: 60-second sliding window

```python
# Rate limiter internals
rate_limiter = GHLRateLimiter(max_requests=95, time_window=60)
rate_limiter.wait_if_needed()  # Blocks if at limit
remaining = rate_limiter.get_remaining_requests()  # Check capacity
```

## Error Handling

### Error Types

1. **Authentication (401)**: Invalid API key - fails immediately
2. **Rate Limit (429)**: Waits for `Retry-After` seconds
3. **Not Found (404)**: Resource doesn't exist - fails immediately
4. **Server Error (500)**: Retries 3 times with exponential backoff (1s, 2s, 4s)
5. **Network Error**: Retries 3 times with exponential backoff

### Custom Exception

```python
from integrations import GHLAPIError

try:
    ghl.create_opportunity(data)
except GHLAPIError as e:
    print(f"Error: {e.message}")
    print(f"Status Code: {e.status_code}")
    print(f"Response: {e.response}")
```

## Test Mode

Enable test mode to log actions without making actual API calls:

```python
ghl = GoHighLevelConnector(
    api_key="test_key",
    location_id="test_location",
    test_mode=True
)

# All API calls will be logged but not executed
ghl.create_opportunity(data)  # Logs action, returns mock response
```

## GHL API Limitations Discovered

1. **Rate Limit**: 100 requests/minute (strictly enforced)
2. **Pagination**: Contacts API limited to 100 per request, requires offset
3. **Custom Fields**: Must exist before use, no auto-creation
4. **Tags**: For contacts only, not directly on opportunities
5. **Workflows**: Require contact_id to trigger, can't trigger on opportunity alone
6. **Notes**: May require specific endpoint per resource type
7. **Retry-After**: Not always provided in 429 responses (use 60s default)

## Integration Points

### For Other Modules

```python
# Property analysis module
from integrations import GHLWorkflowManager

def on_property_analyzed(property_data):
    workflow_mgr = GHLWorkflowManager(ghl, config)
    opp_id = workflow_mgr.create_opportunity_from_property(property_data)
    return opp_id

# Buyer management module
from integrations import BuyerMatcher

def match_buyers_to_property(property_data):
    matcher = BuyerMatcher(ghl, db, config)
    matches = matcher.match_property_to_buyers(property_data)
    matcher.notify_matched_buyers(property_data, matches)

# Database module
# Pass db_manager to BuyerMatcher for caching and SMS tracking
matcher = BuyerMatcher(ghl, db_manager, config)
```

### Required Database Tables

For full functionality, create these tables:

```sql
-- SMS tracking
CREATE TABLE sms_log (
    id INTEGER PRIMARY KEY,
    contact_id TEXT,
    property_id TEXT,
    sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Buyer cache
CREATE TABLE buyer_cache (
    id INTEGER PRIMARY KEY,
    data TEXT,  -- JSON
    cached_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## Logging

Configure logging in your application:

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/ghl_integration.log'),
        logging.StreamHandler()
    ]
)
```

## Security

1. **Never commit `ghl_config.py`** - Add to `.gitignore`
2. **Store API key in environment variable**:
   ```python
   import os
   api_key = os.getenv("GHL_API_KEY")
   ```
3. **Use test mode** for development/debugging
4. **Validate SSL certificates** (enabled by default in requests)

## Troubleshooting

### Connection Issues
```bash
# Test connection
python -c "from integrations import GoHighLevelConnector; ghl = GoHighLevelConnector('YOUR_KEY', 'YOUR_LOCATION'); print(ghl.test_connection())"
```

### Rate Limiting
- Check remaining requests: `ghl.rate_limiter.get_remaining_requests()`
- Increase safety margin: `GHLRateLimiter(max_requests=90)`

### Custom Fields Not Working
- Verify fields exist in GHL: `ghl.get_custom_fields()`
- Check field keys match configuration

### Workflows Not Triggering
- Verify workflow IDs are correct
- Ensure contact exists for workflow triggers
- Check workflow is active in GHL

## Support

For GHL API documentation: https://highlevel.stoplight.io/docs/integrations/

## License

Proprietary - DealFinder Pro
