# Autonomous Search Agents - Implementation Guide

## Overview

DealFinder Pro now features **autonomous search agents** that monitor properties 24/7 and automatically notify clients when matches are found. This transforms the platform from a manual search tool into an intelligent, proactive property discovery system.

## What Was Built

### 1. Core Components

**modules/client_db.py** (470 lines)
- SQLite database with 4 tables:
  - `clients` - Client profiles
  - `search_criteria` - Search preferences
  - `active_agents` - Running search agents
  - `agent_matches` - Found properties
- Full CRUD operations
- Singleton pattern for easy access

**modules/search_agent.py** (530 lines)
- SearchAgent class - Autonomous monitoring logic
- Checks new property scans every 4 hours
- Filters by ZIP codes, price, beds/baths, property type
- Calculates match scores (0-100)
- Sends notifications (email, SMS, in-app)
- Integration with GHL CRM (optional)

**modules/agent_manager.py** (310 lines)
- AgentManager class - Lifecycle management
- Starts/stops/pauses/resumes agents
- APScheduler for 4-hour check intervals
- Health monitoring and status tracking
- Singleton pattern with auto-loading on startup

**modules/ai_agent.py** (enhanced)
- Added 9 new AI tools for agent management:
  - `create_client` - Create client profile
  - `create_search_agent` - Launch autonomous monitor
  - `list_active_agents` - Show all running agents
  - `get_agent_status` - Check agent details
  - `pause_agent` / `resume_agent` - Control agents
  - `cancel_agent` / `complete_agent` - End agents
  - `create_ghl_contact` - GHL CRM integration

### 2. User Experience

**AI-First Interface**
- Homepage redirects to AI Assistant (dashboard/app.py)
- Natural language conversations for setup
- No forms required - just talk to Claude

**Example Conversation Flow**
```
You: "I have a client looking for homes in 92128, 92130, 92131"

AI: "Great! Let me help set up an autonomous search agent.
     A few questions:
     - What's the client's name and email?
     - Price range?
     - Minimum bedrooms/bathrooms?
     - Any specific property types?"

You: "John Smith, john@email.com, $600K-$900K, 3 bed, 2 bath"

AI: *Creates client and launches search agent*
    "✅ Search agent AGENT-ABC123 created and started!

    Agent will check for properties every 4 hours and notify John when matches are found.

    Criteria:
    - ZIP: 92128, 92130, 92131
    - Price: $600K - $900K
    - 3+ beds, 2+ baths
    - Notifications: Email + In-app"
```

## How It Works

### Agent Lifecycle

1. **Creation** (via AI conversation or API)
   ```
   User → AI → create_client() → create_search_agent() → Agent runs
   ```

2. **Monitoring** (automated every 4 hours)
   ```
   AgentManager triggers SearchAgent
   → Load latest_scan.json
   → Filter by criteria (ZIP, price, beds, etc.)
   → Calculate match scores
   → Store matches in database
   → Send notifications (email/SMS/chat)
   ```

3. **Status Check** (anytime via AI)
   ```
   User: "How's the agent doing?"
   AI → get_agent_status(agent_id)
   → Returns: last check time, matches found, criteria summary
   ```

4. **Completion** (when property found)
   ```
   User: "John found a property, close the agent"
   AI → complete_agent(agent_id)
   → Agent stops, marked as completed
   ```

### Match Scoring Algorithm

Properties are scored 0-100 based on:

**From Property Data (40 points max)**
- Opportunity score from latest scan (transferred directly)

**Location Match (30 points)**
- Exact ZIP code match = 30 points

**Price Positioning (15 points)**
- Closer to client's budget midpoint = higher score

**Property Characteristics (15 points)**
- Meets bed/bath requirements = points awarded

**Bonuses (can exceed 100)**
- Strong cash flow (+10)
- High appreciation potential (+10)
- Motivated seller / 60+ days on market (+5)

### Notification Channels

1. **Email** (via GHL or direct SMTP)
   - Full property details
   - Match reasons
   - Link to dashboard

2. **SMS** (via GHL)
   - Short summary
   - Address and price
   - Score

3. **In-App** (dashboard notifications)
   - Stored in agent_matches table
   - Visible in Client Manager page (to be built)

## Database Schema

### clients
```sql
client_id (PK)
name
email
phone
notes
status (active/inactive)
ghl_contact_id (optional)
created_at
updated_at
```

### search_criteria
```sql
criteria_id (PK)
client_id (FK)
zip_codes (JSON array)
price_min, price_max
bedrooms_min, bathrooms_min
property_types (JSON array)
deal_quality (JSON array: HOT, GOOD, FAIR)
min_score (0-100)
investment_type
timeline
created_at
```

### active_agents
```sql
agent_id (PK) - Short readable ID like "ABC123XY"
client_id (FK)
criteria_id (FK)
status (active/paused/completed/cancelled)
notification_email (0/1)
notification_sms (0/1)
notification_chat (0/1)
created_at
last_check (timestamp)
matches_found (count)
paused_at, completed_at, cancelled_at
```

### agent_matches
```sql
match_id (PK)
agent_id (FK)
property_address
property_data (JSON - full property details + match score/reasons)
matched_at
notified (0/1)
notified_at
status (new/sent/viewed/contacted/closed)
```

## GoHighLevel Integration

**When GHL is configured:**
1. Client created in DealFinder → Also created in GHL
2. Agent finds match → GHL workflow triggered
3. Email/SMS sent via GHL platform
4. Contact activity logged in GHL timeline

**Data Sync:**
- `ghl_contact_id` stored in clients table
- Buyer preferences stored in GHL custom fields
- Opportunity pipeline updated when matches found

## Testing the System

### Test Scenario 1: Create Agent via AI

```
1. Visit dashboard (auto-redirects to AI Assistant)
2. Say: "I have a client looking for homes in 92128 area,
         budget $700K-$900K, 3 bedroom minimum"
3. AI will:
   - Ask for client name/email
   - Confirm criteria
   - Create client
   - Launch search agent
   - Return agent ID
4. Agent immediately checks latest_scan.json
5. If matches found, notifications sent
```

### Test Scenario 2: Check Agent Status

```
1. Ask AI: "Show me active agents"
2. AI returns list with:
   - Agent IDs
   - Client names
   - Criteria summaries
   - Last check time
   - Matches found count
```

### Test Scenario 3: Manual Agent Check

```python
from modules.agent_manager import get_agent_manager

manager = get_agent_manager()
manager.force_check_all()  # Trigger immediate check for all agents
```

## Configuration

### Environment Variables (.env)
```bash
# Required for AI Assistant
ANTHROPIC_API_KEY=your_key_here

# Optional for GHL integration
GHL_API_KEY=your_ghl_key
GHL_LOCATION_ID=your_location_id

# Optional for direct SMS (if not using GHL)
TWILIO_ACCOUNT_SID=your_sid
TWILIO_AUTH_TOKEN=your_token
TWILIO_PHONE_NUMBER=+1234567890
```

### Customization

**Change check frequency** (modules/agent_manager.py:113)
```python
# Current: Every 4 hours
trigger=IntervalTrigger(hours=4)

# Change to hourly:
trigger=IntervalTrigger(hours=1)

# Change to daily:
trigger=IntervalTrigger(days=1)
```

**Adjust match score threshold** (in criteria)
```python
criteria = {
    'min_score': 80,  # Default - good matches
    # 'min_score': 90,  # HOT deals only
    # 'min_score': 70,  # More lenient
}
```

## File Structure

```
Real Estate Valuation/
├── modules/
│   ├── client_db.py          ← Database management
│   ├── search_agent.py       ← Autonomous monitoring logic
│   ├── agent_manager.py      ← Lifecycle management
│   ├── ai_agent.py           ← AI tools integration
│   └── perplexity_agent.py   ← Web search (existing)
├── integrations/
│   ├── ghl_connector.py      ← GHL API client (existing)
│   └── ghl_buyer_matcher.py  ← Buyer matching (existing)
├── dashboard/
│   ├── app.py                ← Homepage redirect to AI
│   └── pages/
│       └── 7_🤖_AI_Assistant.py  ← Main chat interface
├── database/
│   └── clients.db            ← SQLite database (auto-created)
└── data/
    └── latest_scan.json      ← Property data source
```

## Next Steps

### Immediate:
1. **Test the System**
   - Try creating an agent via AI
   - Check database/clients.db was created
   - Verify agent runs every 4 hours (check logs)

2. **Configure Notifications**
   - Add email SMTP settings (if not using GHL)
   - Set up Twilio for SMS (if not using GHL)

### Future Enhancements:
1. **Client Manager Dashboard Page**
   - View all clients
   - See active agents per client
   - Browse matches found
   - Manual agent controls (pause/resume/cancel)

2. **Analytics Dashboard**
   - Agent performance metrics
   - Match quality trends
   - Client engagement statistics

3. **Advanced Features**
   - Multi-market search (San Diego + Las Vegas + ...)
   - Price drop alerts
   - Neighborhood insights (schools, crime via Perplexity)
   - Automated valuation model (AVM) integration

## Troubleshooting

### Agent not finding matches
- Check `database/clients.db` - is agent status "active"?
- Check `data/latest_scan.json` - are there properties in the ZIP codes?
- Check criteria - too restrictive? (e.g., $500K-$600K in expensive area)
- Check min_score - set to 80+ means only good deals

### Notifications not sending
- Check .env - email/SMS credentials configured?
- Check agent notifications settings (notification_email, notification_sms)
- Check GHL integration - API key valid?

### Database errors
- Ensure `database/` directory exists
- Check file permissions on `database/clients.db`
- SQLite automatically creates tables on first run

### Import errors
```python
# If you see import errors:
pip install apscheduler anthropic python-dotenv
```

## API Reference

### AgentManager

```python
from modules.agent_manager import get_agent_manager

manager = get_agent_manager()

# Create agent
agent_id = manager.create_agent(
    client_id="<uuid>",
    criteria={
        'zip_codes': ['92128', '92130'],
        'price_min': 600000,
        'price_max': 900000,
        'bedrooms_min': 3,
        'bathrooms_min': 2
    },
    notification_email=True,
    notification_sms=False
)

# Control agents
manager.pause_agent(agent_id)
manager.resume_agent(agent_id)
manager.cancel_agent(agent_id)

# Check status
status = manager.get_agent_status(agent_id)
all_agents = manager.list_active_agents()
matches = manager.get_agent_matches(agent_id)

# Force immediate check
manager.force_check_all()
```

### ClientDatabase

```python
from modules.client_db import get_db

db = get_db()

# Create client
client_id = db.create_client(
    name="John Smith",
    email="john@email.com",
    phone="+1234567890"
)

# Get clients
client = db.get_client(client_id)
all_clients = db.get_all_clients()
active_clients = db.get_all_clients(status='active')
```

---

**Built with Claude Code** | **Powered by Anthropic Claude 3.5 Sonnet**
