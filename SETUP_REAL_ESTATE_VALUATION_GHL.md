# Setting Up "Real Estate Valuation" GHL Account for Agents

**Date**: October 8, 2025
**GHL Account**: Real Estate Valuation
**Purpose**: Configure your FIRST GHL account for the agent system

---

## Important: Your GHL Setup

✅ **You have ONE GHL account**: "Real Estate Valuation"
✅ **This is for the agent system ONLY**
✅ **Main DealFinder Pro does NOT use GHL** (and never did)

---

## Quick Setup Checklist

- [ ] Step 1: Get API Key from "Real Estate Valuation" GHL
- [ ] Step 2: Get Location ID from "Real Estate Valuation" GHL
- [ ] Step 3: Create .env file with credentials
- [ ] Step 4: Create custom fields in GHL
- [ ] Step 5: Create pipeline in GHL
- [ ] Step 6: Add pipeline IDs to .env
- [ ] Step 7: Get LLM API key (Claude)
- [ ] Step 8: Create agent memory database tables
- [ ] Step 9: Test agent + GHL connection

---

## Step 1: Get Your GHL API Key

### Login to "Real Estate Valuation" Account
1. Go to https://app.gohighlevel.com/
2. Login to your **"Real Estate Valuation"** account
3. Navigate: **Settings → Integrations**
4. Find **"API Key"** section
5. Click **"Create API Key"** or **"View API Key"**
6. Copy your API key (starts with something like `eyJ...`)

**Important**: This is your Bearer token for API authentication.

---

## Step 2: Get Your Location ID

### In "Real Estate Valuation" Account
1. Still in GHL, go to: **Settings → Business Profile**
2. Scroll down to **Location Details**
3. Copy your **Location ID**
   - It's a long string like: `AbC123XyZ456...`
   - May also be labeled as "Company ID" or "Sub-account ID"

**Alternative method**:
1. Go to **Settings → Company**
2. Look at the URL in your browser
3. The Location ID is in the URL: `https://app.gohighlevel.com/location/YOUR_LOCATION_ID/dashboard`

---

## Step 3: Create .env File

### Copy Template
```bash
# In your project root
cp .env.example .env
```

### Edit .env File
Open `.env` in a text editor and add:

```bash
# ========================================
# GOHIGHLEVEL API (Real Estate Valuation Account)
# ========================================
GHL_API_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...    # Your actual API key
GHL_LOCATION_ID=AbC123XyZ456...                        # Your actual Location ID

# GHL Pipeline Configuration (will add these in Step 6)
GHL_PIPELINE_ID=
GHL_STAGE_NEW=
GHL_STAGE_HOT=
GHL_STAGE_PRIORITY=
GHL_STAGE_SHOWING=
GHL_STAGE_OFFER=
GHL_STAGE_CONTRACT=
GHL_STAGE_WON=
GHL_STAGE_LOST=

# ========================================
# LLM API (For Agent Intelligence)
# ========================================
ANTHROPIC_API_KEY=sk-ant-api03-your-key-here           # Get from console.anthropic.com

# ========================================
# DATABASE (Already Configured)
# ========================================
DB_USER=postgres
DB_PASSWORD=your_database_password
DB_HOST=localhost
DB_PORT=5432
DB_NAME=dealfinder

# ========================================
# EMAIL (Already Configured)
# ========================================
EMAIL_USERNAME=your_email@gmail.com
EMAIL_PASSWORD=your_app_password
```

**Save the file!**

---

## Step 4: Create Custom Fields in GHL

### For Opportunities (Properties)

Login to "Real Estate Valuation" GHL account:

1. Go to: **Settings → Custom Fields**
2. Select: **Opportunities**
3. Click: **+ Add Custom Field**

Create these fields:

| Field Name | Field Type | Description |
|------------|-----------|-------------|
| `deal_score` | Number | Property opportunity score (0-100) |
| `property_address` | Text (Single Line) | Full property address |
| `list_price` | Currency | Property listing price |
| `est_profit` | Currency | Estimated profit potential |
| `mls_id` | Text (Single Line) | MLS number |
| `price_per_sqft` | Number | Price per square foot |
| `below_market_pct` | Number | Percentage below market value |
| `days_on_market` | Number | Days property has been listed |
| `deal_quality` | Dropdown | Options: HOT DEAL, GOOD, FAIR, PASS |
| `estimated_arv` | Currency | After repair value |

**Important**: Note the exact field names you create. You'll need them later.

### For Contacts (Buyers)

Still in **Settings → Custom Fields**, select: **Contacts**

Create these fields:

| Field Name | Field Type | Description |
|------------|-----------|-------------|
| `budget_min` | Currency | Minimum budget |
| `budget_max` | Currency | Maximum budget |
| `location_preference` | Text (Single Line) | Preferred cities/areas |
| `property_type_preference` | Dropdown | Options: Single Family, Multi-Family, Condo, Townhouse |
| `min_bedrooms` | Number | Minimum bedrooms required |
| `buyer_status` | Dropdown | Options: Active, Passive, On Hold |

---

## Step 5: Create Pipeline in GHL

### Create New Pipeline

In "Real Estate Valuation" GHL account:

1. Go to: **Opportunities → Pipelines**
2. Click: **+ Create Pipeline**
3. Name: **"Investment Properties"**
4. Click: **Create**

### Add Pipeline Stages

Click on your new "Investment Properties" pipeline, then add these stages:

1. **New Lead** - Initial property evaluation
2. **Hot Lead** - High-priority properties
3. **Priority Review** - Needs detailed analysis
4. **Showing Scheduled** - Property viewing set up
5. **Offer Submitted** - Made an offer
6. **Under Contract** - Offer accepted
7. **Closed Won** - Deal completed ✅
8. **Closed Lost** - Deal fell through ❌

**Drag to reorder** stages if needed.

---

## Step 6: Get Pipeline and Stage IDs

### Get Pipeline ID

1. In GHL, click on **"Investment Properties"** pipeline
2. Look at the browser URL
3. Copy the Pipeline ID from URL:
   ```
   https://app.gohighlevel.com/location/YOUR_LOC/opportunities/pipelines/PIPELINE_ID_HERE/stages
   ```
4. Add to `.env`:
   ```bash
   GHL_PIPELINE_ID=YOUR_PIPELINE_ID_HERE
   ```

### Get Stage IDs

**Method 1: From URL** (easier)
1. Click on each stage name
2. URL changes to include stage ID:
   ```
   .../stages/STAGE_ID_HERE
   ```
3. Copy each stage ID

**Method 2: Use GHL API** (if Method 1 doesn't work)
```bash
# Test script to get stage IDs
python -c "
from integrations.ghl_connector import GoHighLevelConnector
import os
from dotenv import load_dotenv

load_dotenv()
ghl = GoHighLevelConnector(
    api_key=os.getenv('GHL_API_KEY'),
    location_id=os.getenv('GHL_LOCATION_ID')
)

# Replace with your pipeline ID
stages = ghl.get_pipeline_stages('YOUR_PIPELINE_ID')
for stage in stages:
    print(f'{stage[\"name\"]}: {stage[\"id\"]}')
"
```

### Update .env with Stage IDs

```bash
GHL_PIPELINE_ID=abc123pipeline
GHL_STAGE_NEW=stage_new_lead_id
GHL_STAGE_HOT=stage_hot_lead_id
GHL_STAGE_PRIORITY=stage_priority_review_id
GHL_STAGE_SHOWING=stage_showing_scheduled_id
GHL_STAGE_OFFER=stage_offer_submitted_id
GHL_STAGE_CONTRACT=stage_under_contract_id
GHL_STAGE_WON=stage_closed_won_id
GHL_STAGE_LOST=stage_closed_lost_id
```

---

## Step 7: Get LLM API Key

Agents need AI to make intelligent decisions.

### Option 1: Claude (Recommended)

1. Go to: https://console.anthropic.com/
2. Sign up or login
3. Click: **"Get API Keys"**
4. Create new key
5. Copy key (starts with `sk-ant-`)
6. Add to `.env`:
   ```bash
   ANTHROPIC_API_KEY=sk-ant-api03-your-key-here
   ```

**Cost**: ~$0.01-0.10 per agent decision (very affordable)

### Option 2: OpenAI GPT-4 (Alternative)

1. Go to: https://platform.openai.com/api-keys
2. Create new secret key
3. Copy key (starts with `sk-`)
4. Add to `.env`:
   ```bash
   OPENAI_API_KEY=sk-your-key-here
   ```

**Cost**: Similar to Claude

---

## Step 8: Create Agent Memory Database Tables

Agents store what they learn in the database.

### Run SQL Schema

```bash
# Make sure PostgreSQL is running
psql dealfinder < database/agent_memory_schema.sql
```

**Expected output**:
```
CREATE TABLE
CREATE INDEX
CREATE FUNCTION
...
Agent memory schema created successfully!
```

### Verify Tables Created

```bash
psql dealfinder -c "\dt agent_*"
```

Should show:
- `agent_memories`
- `agent_performance`
- `agent_communications`

---

## Step 9: Test Your Setup

### Test GHL Connection

```bash
python main.py --test-ghl
```

**Expected output**:
```
Testing GHL connection...
✅ GHL connection successful!
```

**If it fails**:
- Check `GHL_API_KEY` in `.env`
- Check `GHL_LOCATION_ID` in `.env`
- Make sure you're logged into the correct GHL account

### Test Agent with GHL

```bash
python examples/agents/agent_ghl_integration.py
```

**Expected output**:
```
Initializing AI...
✓ LLM initialized

Connecting to GoHighLevel...
✓ GHL connected

Creating GHL Intelligent Agent...
✓ Agent created: ghl_intelligent_agent

============================================================
TEST 1: Should we create GHL opportunity?
============================================================

🤖 GHL Agent: ghl_intelligent_agent
📋 Task: evaluate_property

Step 1: Agent evaluating property for GHL...
   Decision: yes - hot_lead (score 90+, immediate action)
   Confidence: 92%
   Reasoning: This is a hot deal because deal_score is 92, which exceeds the 90 threshold...

============================================================
TEST 2: Creating GHL Opportunity
============================================================

   Chosen Stage: hot_lead
   Reason: Deal score of 92 warrants immediate hot lead classification...

   Creating opportunity in GHL...
   ✅ Success! Opportunity ID: opp_abc123xyz

============================================================
Demo complete!
============================================================
```

### Verify in GHL Dashboard

1. Login to "Real Estate Valuation" GHL
2. Go to: **Opportunities**
3. Select: **"Investment Properties"** pipeline
4. You should see the test opportunity:
   - **Name**: "123 Sunset Blvd, Beverly Hills, CA 90210 - Score: 92"
   - **Stage**: Hot Lead
   - **Custom Fields**: deal_score, property_address, etc. filled in

---

## Troubleshooting

### "GHL_API_KEY not found"
- Check `.env` file exists in project root
- Check variable name is exactly `GHL_API_KEY` (no typos)
- Check no extra spaces around the `=` sign

### "Authentication failed - invalid API key"
- API key might be expired - generate a new one in GHL
- Make sure you copied the entire key (they're long!)
- Check you're using the API key from "Real Estate Valuation" account

### "Custom field not found"
- Make sure you created the custom field in GHL
- Check the field name matches exactly (case-sensitive)
- Restart the script after creating fields

### "Pipeline stage not found"
- Verify pipeline ID is correct in `.env`
- Verify stage IDs are correct
- Use the helper script in Step 6 to list all stages

### Agent creates opportunity but fields are empty
- Check custom field names match exactly
- Make sure fields are set for "Opportunities" not "Contacts"
- Check field data types (Currency, Number, Text, etc.)

---

## Your Complete .env File Template

Here's what your `.env` should look like when complete:

```bash
# ========================================
# GOHIGHLEVEL API (Real Estate Valuation Account)
# ========================================
GHL_API_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.YOUR_ACTUAL_KEY
GHL_LOCATION_ID=AbC123XyZ456YourActualLocationID

# GHL Pipeline Configuration
GHL_PIPELINE_ID=pipeline_investment_properties_id
GHL_STAGE_NEW=stage_new_lead_id
GHL_STAGE_HOT=stage_hot_lead_id
GHL_STAGE_PRIORITY=stage_priority_review_id
GHL_STAGE_SHOWING=stage_showing_scheduled_id
GHL_STAGE_OFFER=stage_offer_submitted_id
GHL_STAGE_CONTRACT=stage_under_contract_id
GHL_STAGE_WON=stage_closed_won_id
GHL_STAGE_LOST=stage_closed_lost_id

# ========================================
# LLM API (For Agent Intelligence)
# ========================================
ANTHROPIC_API_KEY=sk-ant-api03-your-actual-anthropic-key

# ========================================
# DATABASE
# ========================================
DB_USER=postgres
DB_PASSWORD=your_postgres_password
DB_HOST=localhost
DB_PORT=5432
DB_NAME=dealfinder

# ========================================
# EMAIL
# ========================================
EMAIL_USERNAME=your_email@gmail.com
EMAIL_PASSWORD=your_gmail_app_password
```

---

## Next Steps After Setup

Once everything is working:

1. **Read the guides**:
   - `QUICKSTART_AGENTS.md` - Quick introduction
   - `AGENT_SYSTEM_GUIDE.md` - Complete tutorial

2. **Build your first custom agent**:
   - Start with Market Analyst Agent
   - Connect to PropertyAnalyzer module
   - Test with real property data

3. **Deploy to production**:
   - Integrate agents into main workflow
   - Set confidence thresholds
   - Monitor agent performance

---

## Support

If you get stuck:
1. Check this guide first
2. Read `GHL_AGENT_SETUP.md` for additional details
3. Review `GHL_INTEGRATION_SUMMARY.md` for conceptual overview
4. Check example code in `examples/agents/agent_ghl_integration.py`

---

**You're setting up your FIRST GHL integration - for the agent system!** 🎯

**Remember**: Main DealFinder Pro does NOT use GHL and never did. This is agent-only.
