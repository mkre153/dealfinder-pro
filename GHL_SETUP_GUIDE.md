# GoHighLevel Setup Guide for DealFinder Pro

This guide walks you through setting up GoHighLevel (GHL) integration for DealFinder Pro.

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [API Access Setup](#api-access-setup)
3. [Custom Fields Configuration](#custom-fields-configuration)
4. [Pipeline Setup](#pipeline-setup)
5. [Workflow Configuration](#workflow-configuration)
6. [Buyer Profile Setup](#buyer-profile-setup)
7. [Testing the Integration](#testing-the-integration)
8. [Troubleshooting](#troubleshooting)

---

## Prerequisites

- GoHighLevel Agency or SaaS account
- Admin access to your GHL location
- API access enabled (contact GHL support if needed)

---

## 1. API Access Setup

### Generate API Key

1. **Log in to GoHighLevel**
2. **Navigate to Settings**
   - Click Settings (gear icon) in left sidebar
   - Select "API & Integrations"

3. **Create API Key**
   - Click "Create API Key"
   - Name: `DealFinder Pro`
   - Permissions needed:
     - ✅ Contacts: Read, Write
     - ✅ Opportunities: Read, Write, Delete
     - ✅ Workflows: Trigger
     - ✅ Tasks: Create, Update
     - ✅ Notes: Create
     - ✅ SMS: Send (if using GHL for SMS)
   - Click "Create"
   - **Copy the API key immediately** (you won't see it again!)

4. **Get Location ID**
   - In GHL, go to Settings → Business Profile
   - Your Location ID is in the URL: `https://app.gohighlevel.com/location/{LOCATION_ID}/dashboard`
   - Or find it in Settings → Business Profile → Location ID

5. **Add to .env file**
   ```bash
   GHL_API_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
   GHL_LOCATION_ID=abc123def456ghi789
   ```

---

## 2. Custom Fields Configuration

DealFinder Pro uses custom fields to store property data in GHL contacts and opportunities.

### Contact Custom Fields (for Buyers)

Navigate to: **Settings → Custom Fields → Contacts**

Create the following fields:

| Field Name | Field Type | Options |
|------------|------------|---------|
| `buyer_status` | Dropdown | active, inactive, closed |
| `min_budget` | Number | - |
| `max_budget` | Number | - |
| `preferred_locations` | Text Area | - |
| `preferred_property_types` | Multi-Select | Single Family, Multi Family, Condo, Townhouse |
| `min_bedrooms` | Number | - |
| `min_bathrooms` | Number | - |
| `investment_strategy` | Dropdown | buy_and_hold, fix_and_flip, wholesale, both |
| `sms_opt_in` | Checkbox | - |
| `last_property_sent` | Date | - |

### Opportunity Custom Fields (for Properties)

Navigate to: **Settings → Custom Fields → Opportunities**

Create the following fields:

| Field Name | Field Type | Notes |
|------------|------------|-------|
| `property_id` | Text | Unique property identifier |
| `street_address` | Text | Full street address |
| `city` | Text | City |
| `state` | Text | State (2-letter) |
| `zip_code` | Text | ZIP code |
| `list_price` | Number | Asking price |
| `bedrooms` | Number | Number of bedrooms |
| `bathrooms` | Number | Number of bathrooms |
| `square_feet` | Number | Square footage |
| `lot_size` | Text | Lot size |
| `property_type` | Dropdown | Single Family, Multi Family, Condo, Townhouse |
| `year_built` | Number | Year built |
| `days_on_market` | Number | Days on market |
| `opportunity_score` | Number | 0-100 score |
| `deal_quality` | Dropdown | HOT DEAL, GOOD OPPORTUNITY, FAIR DEAL, PASS |
| `below_market_percentage` | Number | % below market |
| `estimated_market_value` | Number | ARV estimate |
| `estimated_profit` | Number | Estimated profit |
| `cap_rate` | Number | Cap rate % |
| `estimated_monthly_rent` | Number | Monthly rent estimate |
| `price_per_sqft` | Number | Price per square foot |
| `price_reduction_amount` | Number | Recent price reduction |
| `listing_url` | URL | Realtor.com URL |
| `mls_number` | Text | MLS listing number |
| `recommendation` | Text Area | Investment recommendation |

---

## 3. Pipeline Setup

### Create Investment Properties Pipeline

1. **Navigate to Opportunities → Pipelines**
2. **Click "Add Pipeline"**
3. **Configure Pipeline:**
   - Name: `Investment Properties`
   - Type: Opportunities

4. **Create Pipeline Stages:**

   | Stage Name | Purpose |
   |------------|---------|
   | New Lead | Newly discovered properties |
   | Reviewing | Under analysis |
   | Hot Deal | Score >= 90 |
   | Matched to Buyer | Property matched to buyer(s) |
   | Under Contract | Deal in progress |
   | Closed - Won | Successful acquisition |
   | Closed - Lost | Property no longer available |

5. **Copy Pipeline ID**
   - Click pipeline settings (gear icon)
   - Copy the Pipeline ID
   - Add to `config.json`:
     ```json
     "gohighlevel": {
       "pipeline_id": "YOUR_PIPELINE_ID"
     }
     ```

6. **Copy Stage IDs**
   - For each stage, click settings and copy Stage ID
   - Add to `config.json`:
     ```json
     "pipeline_stage_new": "STAGE_ID_NEW",
     "pipeline_stage_reviewing": "STAGE_ID_REVIEWING",
     "pipeline_stage_hot": "STAGE_ID_HOT"
     ```

---

## 4. Workflow Configuration

DealFinder Pro can trigger GHL workflows automatically. Here are recommended workflows:

### Workflow 1: Hot Deal Alert

**Purpose:** Immediately notify team when Score >= 90 property is found

**Setup:**
1. Go to **Automation → Workflows**
2. Click **"Create Workflow"**
3. Name: `Hot Deal Alert`
4. Trigger: **Manual** (triggered via API)

**Actions:**
1. **Send SMS** to broker
   - Template:
     ```
     🔥 HOT DEAL ALERT!

     {{custom_values.street_address}}
     {{custom_values.city}}, {{custom_values.state}}

     💰 ${{custom_values.list_price}}
     📊 Score: {{custom_values.opportunity_score}}/100
     📉 {{custom_values.below_market_percentage}}% below market

     Review in GHL now!
     ```

2. **Send Email** to team
   - Subject: `🔥 Hot Deal Alert: {{custom_values.street_address}}`
   - Include property details, photos, analysis

3. **Create Task**
   - Assigned to: Deal Analyst
   - Title: `Review Hot Deal - {{custom_values.street_address}}`
   - Due: Today

4. **Add Tag** to opportunity
   - Tag: `hot-deal`

**Copy Workflow ID:**
- Click workflow settings
- Copy Workflow ID
- Add to `config.json`:
  ```json
  "workflow_ids": {
    "hot_deal_alert": "WORKFLOW_ID_HERE"
  }
  ```

### Workflow 2: Buyer Match Notification

**Purpose:** Notify buyer when property matches their criteria

**Setup:**
1. Create new workflow: `Buyer Match Notification`
2. Trigger: **Manual** (triggered via API)

**Actions:**
1. **Send Email** to matched buyer
   - Subject: `New Property Match: {{custom_values.street_address}}`
   - Template:
     ```html
     <h2>We found a property that matches your criteria!</h2>

     <p><strong>{{custom_values.street_address}}</strong><br>
     {{custom_values.city}}, {{custom_values.state}} {{custom_values.zip_code}}</p>

     <p><strong>Price:</strong> ${{custom_values.list_price}}<br>
     <strong>Beds/Baths:</strong> {{custom_values.bedrooms}}/{{custom_values.bathrooms}}<br>
     <strong>Square Feet:</strong> {{custom_values.square_feet}}</p>

     <p><strong>Why this matches:</strong><br>
     {{custom_values.match_reasons}}</p>

     <p><a href="{{custom_values.listing_url}}">View Listing</a></p>
     ```

2. **Send SMS** (if opted in)
   - Template:
     ```
     New property match!

     {{custom_values.street_address}}
     ${{custom_values.list_price}}

     Check your email for details.
     ```

3. **Create Task** for agent
   - Title: `Follow up with {{contact.first_name}} on property match`
   - Due: Tomorrow

**Copy Workflow ID** and add to `config.json`

### Workflow 3: Follow-Up Sequence

**Purpose:** Automated follow-up for properties

**Setup:**
1. Create workflow: `Property Follow-Up Sequence`
2. Trigger: **Manual**

**Actions:**
1. **Wait 1 day**
2. **Create Task**: Initial property review
3. **Wait 3 days**
4. **Send Email**: Property still available?
5. **Wait 7 days**
6. **Create Task**: Final review before archiving

---

## 5. Buyer Profile Setup

### Import Buyers into GHL

You can manually create buyer contacts or import from CSV.

### Manual Buyer Creation

1. Go to **Contacts**
2. Click **"Add Contact"**
3. Fill in buyer information:
   - First Name, Last Name
   - Email, Phone
   - **Custom Fields:**
     - `buyer_status`: active
     - `min_budget`: 300000
     - `max_budget`: 800000
     - `preferred_locations`: Beverly Hills, CA; Malibu, CA
     - `preferred_property_types`: Single Family, Multi Family
     - `min_bedrooms`: 3
     - `min_bathrooms`: 2
     - `investment_strategy`: buy_and_hold
     - `sms_opt_in`: Yes

4. **Add Tags:**
   - `active-buyer`
   - `investor`

### CSV Import

1. Prepare CSV with columns:
   ```
   first_name,last_name,email,phone,buyer_status,min_budget,max_budget,preferred_locations
   ```

2. Go to **Contacts → Import**
3. Upload CSV
4. Map fields to custom fields
5. Complete import

### Buyer Matching Criteria

DealFinder Pro matches properties to buyers based on:

1. **Budget match** (property price within min/max budget)
2. **Location match** (property in preferred locations)
3. **Property type match** (matches preferred types)
4. **Bedroom/bathroom requirements**
5. **Investment strategy** (rental vs flip properties)

Matching algorithm scores each buyer 0-100 for each property.

---

## 6. Testing the Integration

### Test 1: API Connection

```bash
python main.py --test-ghl
```

Expected output:
```
✅ GHL connection successful!
Location: Your Business Name
```

### Test 2: Create Test Opportunity

```python
# Run Python interactive shell
python

from integrations.ghl_connector import GoHighLevelConnector
import os

ghl = GoHighLevelConnector(
    api_key=os.getenv('GHL_API_KEY'),
    location_id=os.getenv('GHL_LOCATION_ID')
)

# Create test opportunity
test_property = {
    'name': 'Test Property - 123 Main St',
    'pipeline_id': 'YOUR_PIPELINE_ID',
    'pipeline_stage_id': 'YOUR_STAGE_ID',
    'custom_fields': {
        'property_id': 'TEST_001',
        'street_address': '123 Main St',
        'city': 'Beverly Hills',
        'state': 'CA',
        'zip_code': '90210',
        'list_price': 500000,
        'opportunity_score': 85
    }
}

result = ghl.create_opportunity(test_property)
print(f"Created opportunity: {result}")
```

### Test 3: Trigger Workflow

```python
# Trigger hot deal workflow
workflow_id = 'YOUR_WORKFLOW_ID'
opportunity_id = 'OPPORTUNITY_ID_FROM_ABOVE'

result = ghl.trigger_workflow(workflow_id, opportunity_id)
print(f"Workflow triggered: {result}")
```

### Test 4: Full Workflow (Dry Run)

Add to `.env`:
```bash
DRY_RUN=true
```

Then run:
```bash
python main.py --full-workflow
```

This will run the complete workflow without actually creating GHL opportunities or sending notifications. Check logs to verify everything works.

---

## 7. Configuration in config.json

Update your `config.json` with GHL settings:

```json
{
  "gohighlevel": {
    "enabled": true,
    "api_version": "v1",
    "base_url": "https://rest.gohighlevel.com/v1",

    "automation_rules": {
      "auto_create_opportunity": true,
      "min_score_for_opportunity": 75,
      "auto_trigger_hot_deal_workflow": true,
      "hot_deal_threshold": 90,
      "auto_match_buyers": true,
      "auto_send_sms": true,
      "auto_create_tasks": true
    },

    "workflow_ids": {
      "hot_deal_alert": "YOUR_HOT_DEAL_WORKFLOW_ID",
      "buyer_match_notification": "YOUR_BUYER_MATCH_WORKFLOW_ID",
      "follow_up_sequence": "YOUR_FOLLOW_UP_WORKFLOW_ID"
    },

    "pipeline_id": "YOUR_PIPELINE_ID",
    "pipeline_stage_new": "YOUR_NEW_STAGE_ID",
    "pipeline_stage_reviewing": "YOUR_REVIEWING_STAGE_ID",
    "pipeline_stage_hot": "YOUR_HOT_STAGE_ID"
  }
}
```

---

## 8. Troubleshooting

### API Connection Issues

**Error: "Invalid API key"**
- Verify API key is correct in `.env`
- Check API key hasn't been deactivated in GHL
- Ensure no extra spaces in `.env` file

**Error: "Location not found"**
- Verify Location ID is correct
- Ensure you have access to that location

### Custom Fields Not Populating

**Issue: Custom fields show as empty in GHL**
- Verify custom field names match exactly (case-sensitive)
- Check field types match (number vs text)
- Ensure custom fields exist for Opportunities (not just Contacts)

### Workflows Not Triggering

**Issue: Workflows don't fire when expected**
- Verify workflow IDs are correct in `config.json`
- Check workflows are published (not draft)
- Ensure workflow trigger is set to "Manual"
- Check GHL workflow execution logs

### Buyer Matching Not Working

**Issue: No buyers being matched to properties**
- Verify buyer contacts have `buyer_status = 'active'`
- Check custom fields are populated for buyers
- Ensure `preferred_locations` format matches property locations
- Review match scoring thresholds in `integrations/ghl_buyer_matcher.py`

### Rate Limiting

**Error: "Too many requests"**
- GHL API has rate limits (varies by plan)
- Add delays between API calls if needed
- Consider batching operations
- Check your GHL plan's API limits

---

## Best Practices

### Data Quality

1. **Keep buyer profiles updated**
   - Regularly review and update buyer criteria
   - Remove inactive buyers
   - Update budget ranges based on market changes

2. **Tag management**
   - Use consistent tagging strategy
   - Tag buyers by investment type, location preference
   - Tag properties by deal quality, status

3. **Pipeline hygiene**
   - Move stale opportunities to "Closed - Lost"
   - Archive old properties regularly
   - Review "Hot Deal" stage weekly

### Performance

1. **Workflow optimization**
   - Don't trigger too many workflows per property
   - Use conditional triggers based on score thresholds
   - Batch buyer notifications when possible

2. **API usage**
   - Enable only needed automation rules
   - Set reasonable `min_score_for_opportunity` (75+)
   - Use webhooks for real-time updates if needed

### Security

1. **API key protection**
   - Never commit `.env` to version control
   - Rotate API keys quarterly
   - Use separate API keys for dev/prod

2. **Data privacy**
   - Comply with CAN-SPAM for email
   - Honor SMS opt-out requests
   - Follow TCPA regulations

---

## Support Resources

- **GHL Documentation**: https://highlevel.stoplight.io/
- **GHL Support**: support@gohighlevel.com
- **GHL Community**: https://www.facebook.com/groups/gohighlevel
- **DealFinder Pro Issues**: [Create an issue in this repository]

---

## Appendix: Field Mapping Reference

### Property → GHL Opportunity

| DealFinder Field | GHL Field | Type |
|-----------------|-----------|------|
| property_id | property_id | Text |
| street_address | street_address | Text |
| city | city | Text |
| state | state | Text |
| zip_code | zip_code | Text |
| list_price | list_price | Number |
| opportunity_score | opportunity_score | Number |
| deal_quality | deal_quality | Dropdown |

### Buyer → GHL Contact

| DealFinder Field | GHL Field | Type |
|-----------------|-----------|------|
| first_name | firstName | Text |
| last_name | lastName | Text |
| email | email | Email |
| phone | phone | Phone |
| min_budget | min_budget | Number |
| max_budget | max_budget | Number |

---

**Setup Complete!** 🎉

Your GoHighLevel integration is now ready. Run `python main.py --full-workflow` to start discovering deals!
