# GoHighLevel Integration - Quick Reference

## Setup (One-time)

```bash
# 1. Copy config template
cp integrations/ghl_config_example.py integrations/ghl_config.py

# 2. Edit with your credentials
# Update: api_key, location_id, pipeline_id, stage IDs, workflow IDs

# 3. Add to .gitignore
echo "integrations/ghl_config.py" >> .gitignore

# 4. Validate config
python integrations/ghl_config_example.py
```

## Import & Initialize

```python
from integrations import GoHighLevelConnector, GHLWorkflowManager, BuyerMatcher
from integrations.ghl_config_example import get_config

config = get_config()
ghl = GoHighLevelConnector(config["api_key"], config["location_id"])
```

## Common Operations

### Create Opportunity

```python
workflow_mgr = GHLWorkflowManager(ghl, config)

property_data = {
    "address": "123 Main St",
    "deal_score": 95,
    "list_price": 350000,
    "estimated_profit": 85000,
    # ... other fields
}

opp_id = workflow_mgr.create_opportunity_from_property(property_data)
```

### Match Buyers

```python
matcher = BuyerMatcher(ghl, db_manager, config)

matches = matcher.match_property_to_buyers(property_data, min_score=70)
stats = matcher.notify_matched_buyers(property_data, matches)
```

### Create Tasks

```python
task_ids = workflow_mgr.create_tasks_for_property(property_data, opp_id)
```

### Trigger Workflows

```python
# Hot deal workflow (score >= 90)
workflow_mgr.trigger_hot_deal_workflow(property_data, opp_id)

# Custom workflow
ghl.trigger_workflow(workflow_id, contact_id, custom_data)
```

### Send Communications

```python
# SMS
ghl.send_sms(contact_id, "Your message here")

# Email
ghl.send_email(contact_id, "Subject", "<html>body</html>")

# Note
ghl.add_note(contact_id, "Note text")
```

### Manage Contacts

```python
# Search by tags
buyers = ghl.search_contacts(tags=["active_buyer"])

# Get by email
contact = ghl.get_contact_by_email("buyer@example.com")

# Create contact
contact = ghl.create_contact({
    "firstName": "John",
    "lastName": "Doe",
    "email": "john@example.com",
    "phone": "+1234567890",
    "customFields": {
        "budget_min": 250000,
        "budget_max": 400000
    }
})

# Update custom field
ghl.update_custom_field(contact_id, "budget_min", 300000)

# Add tags
ghl.add_contact_tags(contact_id, ["active_buyer", "sms_opt_in"])
```

### Manage Opportunities

```python
# Get opportunity
opp = ghl.get_opportunity(opp_id)

# Update
ghl.update_opportunity(opp_id, {"monetaryValue": 360000})

# Move stage
ghl.move_opportunity_stage(opp_id, stage_id)

# Assign
ghl.assign_opportunity(opp_id, user_id)
```

### Batch Operations

```python
properties = [prop1, prop2, prop3, ...]
stats = workflow_mgr.batch_create_opportunities(properties)
# Returns: {"total": 10, "created": 8, "failed": 2, "errors": [...]}
```

## Error Handling

```python
from integrations import GHLAPIError

try:
    ghl.create_opportunity(data)
except GHLAPIError as e:
    print(f"Status: {e.status_code}")
    print(f"Message: {e.message}")
    print(f"Response: {e.response}")
```

## Test Mode

```python
# Enable test mode - logs actions without API calls
ghl = GoHighLevelConnector(api_key, location_id, test_mode=True)
```

## Rate Limiting

```python
# Check capacity
remaining = ghl.rate_limiter.get_remaining_requests()

# Manually wait if needed
ghl.rate_limiter.wait_if_needed()
```

## Configuration Keys

### Required
- `api_key` - GHL API key
- `location_id` - GHL location ID
- `pipeline_id` - Opportunities pipeline ID

### Stages (map names to IDs)
- `new_lead`
- `priority_review`
- `showing_scheduled`
- `offer_submitted`
- `under_contract`
- `closed_won`
- `closed_lost`

### Workflows (map names to IDs)
- `hot_deal_alert` - Triggered for score >= 90
- `property_match` - Triggered on buyer match
- `new_opportunity` - New opportunity created
- `showing_scheduled` - Showing scheduled

### Settings
- `default_assignee` - User ID for auto-assignment
- `buyer_cache_duration_minutes` - Default: 60
- `max_sms_per_buyer_per_day` - Default: 3
- `quiet_hours_start` - Default: 21 (9 PM)
- `quiet_hours_end` - Default: 8 (8 AM)

## Match Score Algorithm

**Budget (40 points)**
- Exact match: 40 points
- Below budget: 30 points
- Within 110%: 20 points

**Location (30 points)**
- City/ZIP match: 30 points

**Property Type (20 points)**
- Type match: 20 points

**Bedrooms (10 points)**
- Meets requirement: 10 points

**Total: 0-100**

## Custom Fields Reference

### Contact/Buyer
- `budget_min` (Number)
- `budget_max` (Number)
- `location_preference` (Text - comma-separated)
- `property_type_preference` (Text - comma-separated)
- `min_bedrooms` (Number)

### Opportunity/Property
- `property_address` (Text)
- `deal_score` (Number 0-100)
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
- `property_type` (Text)

## Tags

### Buyer Tags
- `active_buyer` - Currently looking
- `sms_opt_in` - SMS consent
- `email_opt_in` - Email consent

### Property Tags
- `automated` - Auto-created
- `dealfinder` - From DealFinder Pro
- `hot_deal` - Score >= 90
- `good_deal` - Score 75-89
- `potential` - Score 60-74

## Logging

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/ghl.log'),
        logging.StreamHandler()
    ]
)
```

## Environment Variables (Recommended)

```bash
export GHL_API_KEY="your_api_key"
export GHL_LOCATION_ID="your_location_id"
```

```python
import os
api_key = os.getenv("GHL_API_KEY")
location_id = os.getenv("GHL_LOCATION_ID")
```

## Troubleshooting

### "Authentication failed"
- Check API key in GHL Settings → Integrations → API
- Verify key is active and has correct permissions

### "Rate limit exceeded"
- Wait 60 seconds
- Check `ghl.rate_limiter.get_remaining_requests()`
- Reduce batch sizes

### "Custom field not found"
- Create field in GHL Settings → Custom Fields
- Verify field key matches configuration
- Check field type (contact vs opportunity)

### "Workflow not triggering"
- Verify workflow ID in GHL → Automations
- Ensure workflow is active/published
- Check if contact exists (workflows need contact_id)

## API Limits

- **Rate Limit**: 100 requests/minute
- **Contact Pagination**: 100 per request
- **SMS Length**: 160 chars (single message)
- **Test Mode**: Unlimited (no actual calls)

## File Structure

```
integrations/
├── __init__.py              # Module exports
├── ghl_connector.py         # Core API client (636 lines)
├── ghl_workflows.py         # Workflow automation (412 lines)
├── ghl_buyer_matcher.py     # Buyer matching (479 lines)
├── ghl_config_example.py    # Config template (182 lines)
├── example_usage.py         # Usage examples (259 lines)
├── README.md                # Full documentation
└── QUICK_REFERENCE.md       # This file

mappings/
└── ghl_field_mapping.json   # Field definitions (141 lines)
```

## Next Steps

1. Configure `ghl_config.py` with your GHL credentials
2. Create custom fields in GHL dashboard
3. Create required tags in GHL
4. Set up pipelines and stages
5. Create automation workflows
6. Run `example_usage.py` to test
7. Integrate with property analysis module
8. Set up database for SMS tracking and caching
