# GoHighLevel Setup for Agentic System

## Quick Answer: Do You Need a New GHL API?

**NO!** ❌ You use your **existing** GHL API key.

Agents are smart wrappers around your existing GHL integration - no new API needed.

---

## Setup Overview

### What You Have
✅ Your existing GHL connector: `integrations/ghl_connector.py`
✅ Your existing GHL API key and Location ID

### What Agents Add
🤖 Intelligent decision-making about WHEN to use GHL
🤖 Smart field mapping
🤖 Personalized buyer matching
🤖 Adaptive pipeline stage selection

---

## Step-by-Step Setup

### Step 1: Verify Your Existing GHL Setup

**Check your .env file has:**
```bash
GHL_API_KEY=your-existing-api-key
GHL_LOCATION_ID=your-existing-location-id
```

**Test connection:**
```bash
python main.py --test-ghl
```

If this works, you're good! Agents will use this same connection.

---

### Step 2: Create GHL Custom Fields (If Not Already Done)

**For Opportunities** (Settings → Custom Fields → Opportunities):

| Field Name | Type | Description |
|------------|------|-------------|
| `deal_score` | Number | Property opportunity score (0-100) |
| `property_address` | Text | Full property address |
| `list_price` | Currency | Property listing price |
| `est_profit` | Currency | Estimated profit potential |
| `mls_id` | Text | MLS number |
| `price_per_sqft` | Number | Price per square foot |
| `below_market_pct` | Number | Percentage below market |
| `days_on_market` | Number | Days listed |
| `deal_quality` | Dropdown | HOT DEAL, GOOD, FAIR, PASS |
| `estimated_arv` | Currency | After repair value |

**For Contacts/Buyers** (Settings → Custom Fields → Contacts):

| Field Name | Type | Description |
|------------|------|-------------|
| `budget_min` | Currency | Minimum budget |
| `budget_max` | Currency | Maximum budget |
| `location_preference` | Text | Preferred cities/areas |
| `property_type_preference` | Dropdown | Single Family, Multi-Family, Condo, etc. |
| `min_bedrooms` | Number | Minimum bedrooms |
| `buyer_status` | Dropdown | Active, Passive, On Hold |

---

### Step 3: Create GHL Pipeline

**In GHL → Opportunities → Pipelines:**

1. **Create Pipeline**: "Investment Properties"

2. **Add Stages**:
   - New Lead
   - Hot Lead
   - Priority Review
   - Showing Scheduled
   - Offer Submitted
   - Under Contract
   - Closed Won
   - Closed Lost

3. **Copy IDs**:
   - Click on pipeline → Copy Pipeline ID
   - Click on each stage → Copy Stage ID

---

### Step 4: Update .env with Pipeline IDs

Add to your `.env`:

```bash
# GHL Pipeline Configuration
GHL_PIPELINE_ID=your-pipeline-id-here
GHL_STAGE_NEW=new-lead-stage-id
GHL_STAGE_HOT=hot-lead-stage-id
GHL_STAGE_PRIORITY=priority-review-stage-id
GHL_STAGE_SHOWING=showing-scheduled-stage-id
GHL_STAGE_OFFER=offer-submitted-stage-id
GHL_STAGE_CONTRACT=under-contract-stage-id
GHL_STAGE_WON=closed-won-stage-id
GHL_STAGE_LOST=closed-lost-stage-id
```

---

### Step 5: Update config.json

```json
{
  "gohighlevel": {
    "enabled": true,
    "api_version": "v1",
    "base_url": "https://rest.gohighlevel.com/v1",

    "automation_rules": {
      "auto_create_opportunity": true,
      "min_score_for_opportunity": 75,
      "hot_deal_threshold": 90,
      "auto_match_buyers": true,
      "auto_send_sms": false,
      "auto_create_tasks": true
    },

    "workflow_ids": {
      "hot_deal_alert": "WORKFLOW_ID_1",
      "buyer_match_notification": "WORKFLOW_ID_2",
      "follow_up_sequence": "WORKFLOW_ID_3"
    },

    "pipeline_id": "YOUR_PIPELINE_ID",
    "pipeline_stage_new": "NEW_STAGE_ID",
    "pipeline_stage_hot": "HOT_STAGE_ID",
    "pipeline_stage_priority": "PRIORITY_STAGE_ID"
  }
}
```

---

## Agent Integration Examples

### Example 1: Agent Uses Your Existing GHL

```python
#!/usr/bin/env python3
"""
Agent uses YOUR existing GHL integration - no new API needed
"""

from agents import LLMClient, BaseAgent
from integrations.ghl_connector import GoHighLevelConnector  # YOUR existing code

# 1. Initialize YOUR existing GHL (same as before)
ghl = GoHighLevelConnector(
    api_key=os.getenv('GHL_API_KEY'),      # Your existing key
    location_id=os.getenv('GHL_LOCATION_ID')  # Your existing location
)

# 2. Initialize LLM for agent intelligence
llm = LLMClient(provider="claude")

# 3. Create agent that uses YOUR GHL
class SmartAgent(BaseAgent):
    def __init__(self, llm, db, ghl_connector):
        super().__init__(name="smart_agent", role="...", goal="...", llm_client=llm, db_manager=db)

        # Add YOUR GHL functions as agent tools
        self.add_tool("create_opp", ghl_connector.create_opportunity, "...", {})
        self.add_tool("send_sms", ghl_connector.send_sms, "...", {})

# 4. Agent uses YOUR existing GHL API
agent = SmartAgent(llm, db, ghl)

# Agent makes intelligent decision
property_data = {"address": "123 Main", "deal_score": 92, ...}

decision = agent.make_decision(
    context=property_data,
    question="Should I create GHL opportunity?",
    options=["yes", "no"]
)

if decision['decision'] == 'yes':
    # Agent uses YOUR existing create_opportunity function
    agent.use_tool("create_opp", opportunity_data=property_data)
```

**Key Point**: Same GHL API, just smarter decisions!

---

### Example 2: Complete Workflow

```python
#!/usr/bin/env python3
"""
Complete agent + GHL workflow
"""

from agents import LLMClient, BaseAgent, AgentCoordinator
from integrations.ghl_connector import GoHighLevelConnector

# Initialize (all your existing code)
ghl = GoHighLevelConnector(api_key, location_id)  # Existing
llm = LLMClient(provider="claude")                 # New (for AI)
db = DatabaseManager(config)                       # Existing

# Create agents
market_agent = MarketAnalystAgent(llm, db)         # New
ghl_agent = GHLAgent(llm, db, ghl)                # New (uses your GHL)

# Workflow: New property found
new_property = {
    "address": "789 Dream St",
    "list_price": 750000,
    "zip_code": "90210",
    "deal_score": 88
}

# Step 1: Market agent analyzes
analysis = market_agent.analyze_market("90210")

# Step 2: GHL agent decides what to do
decision = ghl_agent.execute_task({
    "type": "evaluate_property",
    "data": new_property
})

# Step 3: If good deal, create opportunity
if decision['should_create']:
    result = ghl_agent.execute_task({
        "type": "create_opportunity",
        "data": new_property
    })

    print(f"✅ GHL Opportunity created: {result['opportunity_id']}")
```

---

## Testing Your Setup

### Test 1: Verify GHL Connection
```bash
python main.py --test-ghl
```

Should show: ✅ GHL connection successful

### Test 2: Run Agent Example
```bash
python examples/agents/agent_ghl_integration.py
```

Should show:
- Agent evaluating property
- Agent deciding pipeline stage
- Agent creating opportunity (if GHL configured)

### Test 3: Check GHL Dashboard

Go to GHL → Opportunities

You should see new opportunity created with:
- ✅ Property address
- ✅ Deal score
- ✅ Custom fields populated
- ✅ Correct pipeline stage

---

## FAQ

**Q: Do I need a separate GHL API key for agents?**
A: No! Agents use your existing key.

**Q: Will agents mess up my existing GHL setup?**
A: No! Agents enhance it. They make smarter decisions about WHEN to create opportunities.

**Q: What if I don't have GHL?**
A: Agents work without GHL too! They'll just skip GHL-specific actions.

**Q: Can I test without affecting real GHL data?**
A: Yes! Create a test pipeline in GHL, or agents can run in "dry run" mode.

**Q: How do I see what the agent decided?**
A: Agent explains every decision:
```python
decision = agent.make_decision(...)
print(decision['reasoning'])  # "This is a hot deal because..."
```

---

## Troubleshooting

### Issue: "GHL_API_KEY not found"
```bash
# Add to .env
echo "GHL_API_KEY=your-key" >> .env
echo "GHL_LOCATION_ID=your-location" >> .env
```

### Issue: "Custom field not found"
- Go to GHL → Settings → Custom Fields
- Add the missing field
- Restart your script

### Issue: "Pipeline stage not found"
- Verify pipeline IDs in .env match GHL
- Use GHL API to list stages:
```python
ghl.get_pipelines()
```

### Issue: Agent creates too many opportunities
- Adjust `min_score_for_opportunity` in config.json
- Increase threshold (e.g., 75 → 85)

---

## Summary

### What You Need
- ✅ Your existing GHL API key (no new one needed)
- ✅ Custom fields created in GHL
- ✅ Pipeline set up
- ✅ Pipeline IDs in .env
- ✅ LLM API key (Claude or OpenAI)

### What Agents Do
- 🤖 Make intelligent decisions about creating opportunities
- 🤖 Choose best pipeline stages
- 🤖 Match properties to buyers
- 🤖 Personalize outreach
- 🤖 Learn from outcomes

### What Doesn't Change
- ✅ Your existing GHL account
- ✅ Your existing API key
- ✅ Your existing integrations/ghl_connector.py
- ✅ Your existing workflows

**Agents are a smart layer on top of what you already have!** 🎯

---

## Next Steps

1. **Verify GHL Setup**: `python main.py --test-ghl`
2. **Run Example**: `python examples/agents/agent_ghl_integration.py`
3. **Build Custom Agent**: See AGENT_SYSTEM_GUIDE.md
4. **Deploy**: Integrate into main workflow

**You're ready to use intelligent agents with GHL!** 🚀
