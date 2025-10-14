# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

**Last Updated:** October 2025
**Architecture Version:** 2.0 (Next.js + FastAPI)
**GHL API Version:** v2 (Private Integration Token)

---

## Project Overview

DealFinder Pro is an **AI-powered property intelligence platform** that creates autonomous agents monitoring real estate properties 24/7 and delivers matches directly to GoHighLevel CRM.

**Core Innovation:** 3-minute AI conversation → Agent monitors forever → Matches appear in GoHighLevel → User never returns to our site.

**Strategic Position:** We are NOT a dashboard. We are an **intelligence layer** between property data and GoHighLevel CRM.

---

## High-Level Architecture

### System Diagram

```
┌──────────────────┐     ┌──────────────────┐     ┌──────────────────┐
│   Next.js 14     │────→│   FastAPI        │────→│   Python Core    │
│   Frontend       │     │   REST API       │     │   Modules        │
│   (Vercel)       │     │   (Railway)      │     │   (Unchanged)    │
│                  │     │                  │     │                  │
│  - Landing Page  │     │  - 21 Endpoints  │     │  - AI Agent      │
│  - AI Setup      │     │  - Agent CRUD    │     │  - Search Agent  │
│  - TypeScript    │     │  - Chat API      │     │  - Agent Manager │
│  - Tailwind CSS  │     │  - Properties    │     │  - Database      │
│  - Framer Motion │     │  - Pydantic v2   │     │  - GHL Connector │
└──────────────────┘     └──────────────────┘     └──────────────────┘
Port 3000                 Port 8000                 In-Process
```

### Three-Layer Architecture

**Layer 1: Presentation (Next.js)**
- Modern React with TypeScript
- Framer Motion animations
- Tailwind CSS v3 styling
- Two pages only: Landing + AI Setup
- Goal: Get user configured and hand off to GHL

**Layer 2: API (FastAPI)**
- Python 3.9+ with async/await
- 21 REST endpoints (agents, chat, properties)
- Pydantic v2 for validation
- APScheduler for background jobs
- Auto-generated OpenAPI docs at /docs

**Layer 3: Core Business Logic (Python Modules)**
- Completely UNCHANGED from v1.0 Streamlit version
- Property scanning (homeharvest)
- Autonomous agents (APScheduler)
- AI conversation (Claude API)
- Database (SQLite dev / PostgreSQL prod)
- GHL integration

---

## Critical Architectural Decisions

### 1. Why We Migrated From Streamlit

**Old Architecture (v1.0):**
- Monolithic Streamlit app (7 pages)
- Form-based configuration (15 min setup)
- User manages everything in our dashboard
- Single Python process
- Port 8501

**New Architecture (v2.0):**
- Decoupled Next.js + FastAPI (2 pages)
- AI conversational setup (3 min)
- User manages everything in GoHighLevel
- Independent frontend/backend scaling
- Standard ports (3000/8000)

**Migration Complete (October 2025):**
- All Streamlit components archived in `archive/streamlit_v1_dashboard/`
- `streamlit` and `plotly` dependencies commented out in requirements.txt
- Launch script `run_dashboard.sh` archived
- v2.0 is the ONLY active codebase

**Key Insight:** Users already have GoHighLevel. They don't need ANOTHER dashboard. They need intelligence delivered TO their existing workflow.

### 2. Why Core Modules Are Unchanged

The business logic in `modules/` is PRODUCTION-TESTED and WORKING:
- `ai_agent.py` - Claude integration
- `search_agent.py` - Autonomous monitoring
- `agent_manager.py` - Lifecycle management
- `client_db.py` - Database operations
- `property_scanner.py` - Data collection

FastAPI is just an **API wrapper** around these modules. We didn't rewrite the engine, just replaced the UI.

### 3. Product Strategy: Intelligence Layer, Not Dashboard

**What we DON'T do:**
- ❌ Build a property browsing dashboard
- ❌ Build analytics and reports
- ❌ Build notification management
- ❌ Compete with CRMs

**What we DO:**
- ✅ 3-minute AI setup conversation
- ✅ Create autonomous monitoring agents
- ✅ Score property matches (0-100)
- ✅ Push opportunities to GoHighLevel
- ✅ Let users manage everything in GHL

---

## Project Structure

```
Real Estate Valuation/
├── api/                          # FastAPI Backend (NEW in v2)
│   ├── main.py                  # Main app + 21 endpoints
│   ├── models/schemas.py        # Pydantic models
│   └── routes/
│       ├── agents.py            # Agent CRUD
│       ├── chat.py              # AI conversation
│       └── properties.py        # Property search
│
├── dealfinder-web/              # Next.js Frontend (NEW in v2)
│   ├── app/
│   │   ├── page.tsx            # Landing page
│   │   ├── setup/page.tsx      # AI wizard
│   │   └── layout.tsx          # Root layout
│   ├── lib/
│   │   ├── api-client.ts        # Backend API client
│   │   └── types.ts             # TypeScript types
│   ├── components/              # React components
│   └── public/                  # Static assets
│
├── modules/                      # Core Python Logic (UNCHANGED)
│   ├── ai_agent.py              # Claude API integration
│   ├── search_agent.py          # Autonomous property monitoring
│   ├── agent_manager.py         # APScheduler lifecycle
│   ├── client_db.py             # SQLite/PostgreSQL operations
│   └── property_scanner.py      # Realtor.com scraping
│
├── integrations/                 # External APIs
│   ├── ghl_connector.py         # GoHighLevel API client (v2)
│   ├── sdmls_connector.py       # San Diego MLS API (RESO Web API 2.0) - NEW
│   └── perplexity_agent.py      # Perplexity AI for web search (in modules/)
│
├── database/                     # Database (UNCHANGED)
│   └── dealfinder.db            # SQLite (dev only)
│
├── data/                         # Property Data (UNCHANGED)
│   └── latest_scan.json         # Latest property scan results
│
├── docs/                         # Documentation (v2)
│   ├── DOCUMENTATION_INDEX.md   # Master navigation
│   ├── PRD_V2.md                # Product requirements
│   ├── ARCHITECTURE_V2.md       # Technical architecture
│   ├── USER_JOURNEY_V2.md       # User experience
│   ├── AGENTIC_SYSTEM_V2.md     # Agent system deep dive
│   └── MIGRATION_GUIDE.md       # v1 → v2 migration
│
└── archive/                      # Archived v1.0 Components
    ├── streamlit_v1_docs/       # Old Streamlit documentation
    ├── streamlit_v1_dashboard/  # Old Streamlit app (7 pages)
    │   └── dashboard/           # Complete v1.0 dashboard code
    └── run_dashboard.sh         # Old Streamlit launch script
```

---

## Key Components Deep Dive

### Autonomous Agent System

**Three-Layer Agent Architecture:**

```
┌─────────────────────────────────────────┐
│         Agent Manager (Layer 1)         │
│  - APScheduler background jobs          │
│  - Agent lifecycle (create/pause/resume)│
│  - Check scheduling (every 4 hours)     │
│  - Health monitoring                    │
└─────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────┐
│        Search Agent (Layer 2)           │
│  - Load latest property scan            │
│  - Filter by criteria (ZIP, price, etc) │
│  - Calculate match scores (0-100)       │
│  - Detect duplicates and price drops    │
│  - Store matches in database            │
└─────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────┐
│          AI Agent (Layer 3)             │
│  - Claude API conversation              │
│  - Extract investment criteria          │
│  - Generate match reasoning             │
│  - Natural language interaction         │
└─────────────────────────────────────────┘
```

**Agent Lifecycle States:**
1. `active` - Running and checking every 4 hours
2. `paused` - Temporarily stopped by user
3. `cancelled` - Permanently stopped by user
4. `completed` - Finished (reserved for future use)

**Agent Check Cycle (every 4 hours):**
1. APScheduler triggers check
2. Load latest property scan from `data/latest_scan.json`
3. Filter by ZIP codes, price range, beds, baths
4. Calculate match score for each property (0-100)
5. Filter by minimum score threshold
6. Check for duplicates (skip if seen before)
7. Store new matches in `property_matches` table
8. Create GHL opportunity for each match
9. Send notifications (SMS/Email if configured)
10. Update agent stats (last_check, match_count)

**Match Scoring Algorithm (0-100):**
```python
Base Score: 50

# Price Factor (+/- 20 points)
- Below budget range: +20
- In budget range: +10
- Slightly over budget: 0
- Way over budget: -20

# Deal Quality (+/- 15 points)
- HOT (>20% discount): +15
- GOOD (10-20% discount): +10
- FAIR (5-10% discount): +5
- Poor (<5% discount): -10

# Property Size (+/- 10 points)
- Exceeds minimums by 2+: +10
- Exceeds minimums by 1: +5
- Meets minimums exactly: 0
- Below minimums: -10

# Days on Market (+/- 5 points)
- 60+ days: +5
- 30-60 days: +3
- <30 days: 0

Final Score = Base + Price + Quality + Size + DOM
Clamped to 0-100 range
```

### Database Schema

**Tables:**
```sql
-- Clients (investors)
CREATE TABLE clients (
    client_id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    email TEXT,
    phone TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Search Criteria
CREATE TABLE search_criteria (
    criteria_id TEXT PRIMARY KEY,
    zip_codes TEXT NOT NULL,  -- JSON array
    price_min REAL,
    price_max REAL,
    bedrooms_min INTEGER,
    bathrooms_min REAL,
    property_types TEXT,  -- JSON array
    deal_quality TEXT,    -- JSON array ['HOT', 'GOOD', 'FAIR']
    min_score INTEGER DEFAULT 70,
    investment_type TEXT  -- 'cash_flow', 'appreciation', 'balanced'
);

-- Search Agents
CREATE TABLE search_agents (
    agent_id TEXT PRIMARY KEY,
    client_id TEXT NOT NULL,
    criteria_id TEXT NOT NULL,
    status TEXT DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_check TIMESTAMP,
    next_check TIMESTAMP,
    check_count INTEGER DEFAULT 0,
    match_count INTEGER DEFAULT 0,
    FOREIGN KEY (client_id) REFERENCES clients(client_id),
    FOREIGN KEY (criteria_id) REFERENCES search_criteria(criteria_id)
);

-- Property Matches
CREATE TABLE property_matches (
    match_id TEXT PRIMARY KEY,
    agent_id TEXT NOT NULL,
    property_id TEXT NOT NULL,
    match_score REAL NOT NULL,
    match_reasons TEXT,  -- JSON array
    property_data TEXT NOT NULL,  -- Full JSON
    matched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (agent_id) REFERENCES search_agents(agent_id)
);
```

### Data Sources & MLS Integration

**Official MLS Data via SDMLS (San Diego MLS)**

DealFinder Pro supports integration with **San Diego MLS (SDMLS)** for official real estate data through the RESO Web API 2.0 standard.

**Why SDMLS vs Web Scraping:**

| Feature | SDMLS MLS API | Web Scraping (HomeHarvest) |
|---------|---------------|----------------------------|
| **Data Quality** | Official MLS data | Public listing data |
| **Field Count** | 200+ fields | 20-30 fields |
| **Update Speed** | Real-time | Daily scraping |
| **Reliability** | 99.9% uptime | CAPTCHA/rate limits |
| **Legal Status** | Fully compliant | Gray area |
| **Cost** | $50-100/month | Free |
| **Coverage** | All San Diego County | Realtor.com only |

**RESO Web API 2.0 Integration:**

The `integrations/sdmls_connector.py` module provides:
- **RESO-compliant OData queries** - Standard filtering and pagination
- **Data Dictionary 2.0 mapping** - 200+ standardized property fields
- **Bearer token authentication** - Secure API access via MLS Router
- **Test mode** - Mock data for development without credentials
- **Automatic field transformation** - Maps RESO fields to internal schema

**Setup Process:**

1. **Prerequisites:** Active SDMLS membership (or broker with SDMLS access)
2. **Request Access:** Contact SDMLS Data Access at https://sdmls.com/nmsubscribers/data-access/
3. **Choose Tier:** Tiered Vendor Access Program ($25-50/month) recommended for small operations
4. **Sign Agreement:** Broker Data Access Agreement (standard MLS terms)
5. **Receive Credentials:** MLS Router Bearer token (500+ character JWT)
6. **Configure:** Add `SDMLS_API_TOKEN` to `.env` file
7. **Test:** Run `python3 integrations/sdmls_connector.py` to verify connection

**Complete setup guide:** See `SDMLS_API_SETUP.md` for step-by-step instructions

**Using SDMLS Connector:**

```python
from integrations.sdmls_connector import SDMLSConnector

# Initialize connector
connector = SDMLSConnector(test_mode=False)  # Use real API

# Test connection
result = connector.test_connection()
print(result)  # {'success': True, 'message': 'Successfully connected...'}

# Search properties
properties = connector.search_properties(
    zip_codes=['92126', '92127', '92128', '92129', '92130', '92131'],
    price_min=500000,
    price_max=2000000,
    bedrooms_min=3,
    bathrooms_min=2,
    property_types=['Residential'],
    status='Active',
    days_back=30,
    limit=1000
)

print(f"Found {len(properties)} properties from SDMLS")

# Get property details
property_details = connector.get_property_details(listing_key='12345678')

# Get property photos
media = connector.get_property_media(listing_key='12345678')
```

**RESO Field Mapping Examples:**

RESO Web API uses standardized field names that are automatically mapped to DealFinder Pro's internal schema:

```python
# RESO → Internal Mapping
'ListingKey' → 'mls_number'
'UnparsedAddress' → 'street_address'
'PostalCode' → 'zip_code'
'ListPrice' → 'list_price'
'BedroomsTotal' → 'bedrooms'
'BathroomsTotalInteger' → 'bathrooms'
'LivingArea' → 'square_feet'
'DaysOnMarket' → 'days_on_market'
'StandardStatus' → 'status'
'ListAgentFullName' → 'listing_agent_name'
# ... 190+ more fields
```

**Hybrid Strategy (Recommended):**

For maximum coverage and reliability:
1. **Primary:** SDMLS MLS API for San Diego County properties
2. **Backup:** HomeHarvest scraping for other markets (Las Vegas, etc.)
3. **Future:** Additional MLS integrations (ARMLS for Arizona, CRMLS for Southern California)

**Current Implementation Status:**
- ✅ SDMLS connector created (`integrations/sdmls_connector.py`)
- ✅ RESO Web API 2.0 compliance
- ✅ Test mode for development
- ✅ Complete field mapping (200+ fields)
- ⏳ Pending: SDMLS API credentials (contact SDMLS to request access)
- ⏳ Pending: Integration into property scanner (Phase 4)

**Legacy Data Source:**

For non-San Diego markets or until SDMLS credentials are obtained, DealFinder Pro uses:
- **HomeHarvest** - Python library that scrapes Realtor.com
- **Scraper:** `modules/scraper.py`
- **Scanner:** `modules/property_scanner.py`
- **Data Storage:** `data/latest_scan.json`

This will remain as a fallback data source for markets without MLS API access.

### API Endpoints (21 Total)

**Agents (8 endpoints):**
- `POST /api/agents/` - Create agent
- `GET /api/agents/` - List all agents
- `GET /api/agents/{id}` - Get agent details
- `PATCH /api/agents/{id}` - Update agent
- `DELETE /api/agents/{id}` - Delete agent
- `POST /api/agents/{id}/check` - Force check
- `POST /api/agents/{id}/pause` - Pause agent
- `POST /api/agents/{id}/resume` - Resume agent

**Chat (3 endpoints):**
- `POST /api/chat/` - Send message
- `POST /api/chat/extract-criteria` - Extract investment criteria
- `POST /api/chat/clear` - Clear conversation

**Properties (9 endpoints):**
- `GET /api/properties/` - Search properties
- `GET /api/properties/{id}` - Get property details
- `POST /api/properties/scan` - Trigger new scan
- `GET /api/properties/recent` - Recent properties
- `GET /api/properties/matches/{agent_id}` - Get agent matches
- Plus 4 more utility endpoints

**Health (1 endpoint):**
- `GET /health` - API health check

---

## Development Commands

### Quick Start (Both Services)

**Terminal 1 - Backend:**
```bash
cd "/Users/mikekwak/Real Estate Valuation"
./start_api.sh
```
Backend: http://localhost:8000
API Docs: http://localhost:8000/docs

**Terminal 2 - Frontend:**
```bash
cd dealfinder-web
./start-dev.sh
```
Frontend: http://localhost:3000

### Backend Development

**Manual Start:**
```bash
cd "/Users/mikekwak/Real Estate Valuation"
python3 -m venv venv
source venv/bin/activate
pip install -r requirements_api.txt
uvicorn api.main:app --reload --port 8000
```

**Test API:**
```bash
# Health check
curl http://localhost:8000/health

# View interactive docs
open http://localhost:8000/docs

# Create test agent
curl -X POST http://localhost:8000/api/agents/ \
  -H "Content-Type: application/json" \
  -d '{
    "client_name": "Test Investor",
    "criteria": {
      "zip_codes": ["92037"],
      "price_min": 500000,
      "price_max": 1000000,
      "bedrooms_min": 2,
      "bathrooms_min": 2
    }
  }'

# List agents
curl http://localhost:8000/api/agents/

# Force agent check
curl -X POST http://localhost:8000/api/agents/{agent_id}/check
```

**View Logs:**
```bash
# Backend logs
tail -f nohup.out

# Agent manager logs
grep "Agent" nohup.out | tail -20

# Error logs
grep "ERROR" nohup.out | tail -20
```

### Frontend Development

**Manual Start:**
```bash
cd dealfinder-web
npm install
npm run dev
```

**Build for Production:**
```bash
npm run build
npm run start
```

**Type Checking:**
```bash
npm run type-check  # (if configured)
# or
npx tsc --noEmit
```

**Linting:**
```bash
npm run lint  # (if configured)
# or
npx eslint .
```

### Database Operations

**View Database:**
```bash
sqlite3 database/dealfinder.db

# List tables
.tables

# Show schema
.schema search_agents

# Query agents
SELECT agent_id, status, last_check FROM search_agents;

# Query matches
SELECT match_id, match_score, matched_at FROM property_matches LIMIT 10;

# Exit
.quit
```

**Reset Database (CAUTION - Deletes All Data):**
```bash
rm database/dealfinder.db
python3 modules/client_db.py  # Recreate schema
```

### Testing

**Backend API Tests:**
```bash
# Unit tests (if configured)
pytest tests/

# Integration tests
python3 -m pytest tests/integration/

# Coverage
pytest --cov=api --cov=modules tests/
```

**Frontend Tests:**
```bash
cd dealfinder-web

# Run tests (if configured)
npm test

# E2E tests
npm run test:e2e  # (if configured)
```

**Manual End-to-End Test:**
1. Start both services
2. Visit http://localhost:3000
3. Click "Start with AI"
4. Complete AI conversation
5. Create agent
6. Check database: `sqlite3 database/dealfinder.db "SELECT * FROM search_agents;"`
7. Check logs: `grep "Agent.*created" nohup.out`
8. Force check: `curl -X POST http://localhost:8000/api/agents/{id}/check`
9. Verify matches: `sqlite3 database/dealfinder.db "SELECT * FROM property_matches;"`

---

## Environment Variables

### Backend (.env)

```bash
# AI
ANTHROPIC_API_KEY=sk-ant-...

# GoHighLevel
GHL_API_KEY=your_ghl_api_key
GHL_LOCATION_ID=your_ghl_location_id

# SDMLS (San Diego MLS) - Official MLS Data
SDMLS_API_TOKEN=your_mls_router_token  # See SDMLS_API_SETUP.md

# Database
DATABASE_URL=sqlite:///database/dealfinder.db  # Dev
# DATABASE_URL=postgresql://user:pass@host/db  # Prod

# Notifications (Optional)
TWILIO_ACCOUNT_SID=...
TWILIO_AUTH_TOKEN=...
TWILIO_PHONE_NUMBER=...
GMAIL_USER=...
GMAIL_APP_PASSWORD=...

# API Config
API_HOST=0.0.0.0
API_PORT=8000
DEBUG=true
```

### Frontend (.env.local)

```bash
NEXT_PUBLIC_API_URL=http://localhost:8000  # Dev
# NEXT_PUBLIC_API_URL=https://api.dealfinder.app  # Prod
```

---

## Deployment

### Frontend (Vercel)

```bash
cd dealfinder-web

# Install Vercel CLI
npm i -g vercel

# Deploy preview
vercel

# Deploy production
vercel --prod
```

**Environment Variables in Vercel:**
- `NEXT_PUBLIC_API_URL` → Production API URL

### Backend (Railway)

```bash
# Install Railway CLI
npm i -g @railway/cli

# Login
railway login

# Initialize project
railway init

# Deploy
railway up
```

**Environment Variables in Railway:**
- All backend .env variables listed above
- Set `DATABASE_URL` to PostgreSQL connection string
- Railway provides PostgreSQL add-on automatically

### Database Migration (SQLite → PostgreSQL)

```bash
# Export SQLite data
sqlite3 database/dealfinder.db .dump > backup.sql

# Import to PostgreSQL (adjust for PostgreSQL syntax)
psql $DATABASE_URL < backup.sql
```

---

## Key User Flows

### 1. Agent Creation (3 minutes)

**User Journey:**
```
1. Land on homepage (page.tsx)
2. Click "Start with AI" CTA
3. Navigate to /setup (setup/page.tsx)
4. AI: "What type of properties are you targeting?"
5. User: "Investment properties in San Diego, $600K-$1.2M"
6. AI: "Got it. What's your minimum size requirement?"
7. User: "At least 3 beds, 2 baths"
8. AI: "Perfect! One more question about your investment strategy..."
9. User: "Cash flow focused"
10. AI extracts criteria and displays card
11. User enters name and clicks "Create Agent"
12. Agent created, monitoring starts immediately
```

**Technical Flow:**
```
1. Frontend: setup/page.tsx renders chat UI
2. User types message
3. Frontend: POST /api/chat/ with message + history
4. Backend: ai_agent.py processes with Claude
5. Claude responds with questions or extracts criteria
6. Backend: Returns { message, agent_configured: true/false, suggested_criteria }
7. Frontend: Displays message, shows criteria card if configured
8. User clicks "Create Agent"
9. Frontend: POST /api/agents/ with client_name + criteria
10. Backend: Creates client, criteria, agent records
11. Backend: agent_manager.py schedules APScheduler job (every 4 hours)
12. Backend: Returns { agent_id, status: 'active', next_check }
13. Frontend: Shows success, displays agent details
```

### 2. Agent Check Cycle (Every 4 hours)

**Autonomous Flow (No User Action):**
```
1. APScheduler triggers check for agent X
2. agent_manager.py calls search_agent.check_for_matches(agent_id)
3. search_agent.py loads agent criteria from database
4. Loads latest_scan.json (all properties)
5. Filters by ZIP codes: 92037, 92130
6. Filters by price: $600K-$1.2M
7. Filters by size: 3+ beds, 2+ baths
8. For each property:
   a. Calculate match score (0-100)
   b. Check if score >= min_score (70)
   c. Check if duplicate (property_id already matched)
   d. If new match, store in property_matches table
9. For each new match:
   a. ghl_connector.py creates opportunity in GHL
   b. Sets custom fields (match_score, property_address, price)
   c. Adds note with match reasons
10. Update agent: last_check, next_check, match_count
11. Log results: "Agent X found 3 new matches"
```

### 3. User Checks GoHighLevel (Daily)

**User Experience:**
```
1. User logs into GoHighLevel (not our app)
2. Navigates to Opportunities pipeline
3. Sees 3 new opportunities from last night's check
4. Each opportunity shows:
   - Property address
   - Price and details
   - Match score (e.g., 87/100)
   - Match reasons in notes
5. User reviews and decides to contact interested properties
6. Uses GHL workflows to:
   - Send automated emails
   - Schedule follow-up tasks
   - Track communication
7. All CRM work stays in GoHighLevel
8. User NEVER needs to return to our site
```

---

## Common Issues & Troubleshooting

### Backend Won't Start

**Symptoms:** `./start_api.sh` fails or `uvicorn` crashes

**Check:**
```bash
# Python version
python3 --version  # Must be 3.9+

# Dependencies
pip list | grep fastapi
pip list | grep pydantic

# Reinstall if needed
pip install -r requirements_api.txt

# Port already in use?
lsof -i :8000
kill -9 <PID>
```

### Frontend Won't Start

**Symptoms:** `npm run dev` fails

**Check:**
```bash
# Node version
node --version  # Must be 18+

# Reinstall dependencies
rm -rf node_modules package-lock.json
npm install

# Check for TypeScript errors
npx tsc --noEmit
```

### Agent Not Checking

**Symptoms:** Agent created but no checks happening

**Debug:**
```bash
# Check agent status
curl http://localhost:8000/api/agents/

# Check logs for APScheduler
grep "Agent.*check" nohup.out | tail -20

# Force a check manually
curl -X POST http://localhost:8000/api/agents/{agent_id}/check

# Check database
sqlite3 database/dealfinder.db "SELECT agent_id, status, last_check, next_check FROM search_agents;"

# Verify APScheduler is running
grep "APScheduler" nohup.out | tail -10
```

### No Matches Found

**Symptoms:** Agent checking but finding 0 matches

**Debug:**
```bash
# Check if property scan exists
ls -lh data/latest_scan.json

# Check scan has properties
jq 'length' data/latest_scan.json  # Should return > 0

# Check agent criteria
curl http://localhost:8000/api/agents/{agent_id}

# Manually test search_agent
python3 -c "
from modules.search_agent import SearchAgent
from modules.client_db import get_db
db = get_db()
agent = SearchAgent(agent_id='your_agent_id', db=db)
matches = agent.check_for_matches()
print(f'Found {len(matches)} matches')
"
```

### GHL Integration Issues

**Symptoms:** Matches found but not appearing in GHL

**Debug:**
```bash
# Check GHL credentials
grep GHL .env

# Test GHL connection
python3 -c "
from integrations.ghl_connector import GHLConnector
ghl = GHLConnector()
print(ghl.test_connection())
"

# Check GHL API logs
grep "GHL" nohup.out | tail -20

# Manually create test opportunity
curl -X POST http://localhost:8000/api/agents/{agent_id}/test-ghl
```

---

## Important Constraints & Decisions

### Why Only 2 Pages?

**Decision:** Landing page + AI setup wizard

**Rationale:**
- Users don't need dashboards, they have GHL
- Reduce complexity to single flow: configure → done
- 90% of user value in first 3 minutes
- Everything else happens in background or GHL

### Why Agent Checks Every 4 Hours?

**Decision:** Not every minute, not daily, but 4 hours

**Rationale:**
- Property listings don't change every second
- Too frequent = API rate limits + wasted compute
- 6 checks per day = good coverage without spam
- User configurable in future (Phase 5)

### Why Claude AI vs Custom NLP?

**Decision:** Use Claude API instead of building NLP

**Rationale:**
- World-class understanding out of the box
- No training data needed
- Handles edge cases naturally
- Focus on product, not ML research
- Cost justified by time savings ($1/conversation vs 20 hours building)

### Why FastAPI vs Django/Flask?

**Decision:** FastAPI over alternatives

**Rationale:**
- Async/await for performance
- Auto-generated OpenAPI docs (saves hours)
- Pydantic v2 for validation
- Modern Python 3.9+ features
- Easier to scale than Flask
- Less bloat than Django

### Why Next.js vs React SPA?

**Decision:** Next.js 14 with App Router

**Rationale:**
- Server-side rendering for landing page SEO
- File-based routing (no react-router complexity)
- Built-in API routes (not used yet, but available)
- Image optimization
- Professional production default
- Vercel deployment optimized

---

## Future Roadmap Context

### Phase 3 (Current) - GHL Integration Polish
- Auto-create opportunities for matches
- Custom field mapping (match_score, reasons)
- Workflow triggers
- End-to-end testing with real GHL account

### Phase 4 - Production Launch
- Domain setup (dealfinder.app)
- Vercel + Railway deployment
- Monitoring (Sentry for errors)
- Analytics (PostHog for usage)
- User onboarding flow

### Phase 5 - Advanced Features
- User authentication (Clerk/Auth0)
- Multi-user support
- Billing integration (Stripe)
- Agent feedback loop (user rates matches)
- Mobile app (React Native)

---

## When to Refactor vs When to Preserve

### Preserve (Don't Touch):
- ✅ `modules/` core logic - Production tested
- ✅ Database schema - Stable and working
- ✅ Agent scoring algorithm - Validated by users
- ✅ Property scanner - Data source stable
- ✅ GHL connector - API working

### Safe to Refactor:
- ✅ Frontend components - UI constantly improving
- ✅ API route handlers - Thin wrappers, easy to change
- ✅ Styling - Tailwind makes changes easy
- ✅ Animation timing - Framer Motion config
- ✅ Documentation - Always evolving

### Refactor With Caution:
- ⚠️ APScheduler setup - Background jobs are tricky
- ⚠️ Database queries - Needs testing
- ⚠️ Agent lifecycle - State machine is fragile
- ⚠️ Match deduplication - Logic is subtle

---

## Documentation Map

For deep dives, see:

- **docs/DOCUMENTATION_INDEX.md** - Master navigation (this is your starting point)
- **docs/PRD_V2.md** - Product vision and strategy (15 min read)
- **docs/ARCHITECTURE_V2.md** - Technical architecture diagrams (25 min read)
- **docs/USER_JOURNEY_V2.md** - Complete user experience flow (20 min read)
- **docs/AGENTIC_SYSTEM_V2.md** - Autonomous agent deep dive with flowcharts (30 min read)
- **docs/MIGRATION_GUIDE.md** - v1 → v2 changes (15 min read)
- **SDMLS_API_SETUP.md** - San Diego MLS API setup guide (10 min read)

**Total onboarding time:** ~2.5 hours for complete understanding

---

## Key Takeaways for Future Claude Instances

1. **This is an intelligence layer, not a dashboard.** The product strategy is to get out of the user's way.

2. **Core modules are sacred.** The business logic in `modules/` and `integrations/` is production-tested. FastAPI and Next.js are just new interfaces.

3. **User spends 3 minutes, then never returns.** All value delivered via GoHighLevel integration.

4. **Agents run forever autonomously.** APScheduler checks every 4 hours with zero maintenance required.

5. **Match quality > match quantity.** Scoring algorithm balances price, quality, size, and days on market.

6. **Documentation is comprehensive.** 6 major docs totaling 4,000+ lines. Read before coding.

7. **Architecture is decoupled.** Frontend and backend can be developed, tested, and deployed independently.

8. **Database has no migration needed.** SQLite schema works for both v1 and v2.

9. **Next.js has only 2 pages.** Landing (page.tsx) and Setup (setup/page.tsx). That's intentional.

10. **FastAPI has 21 endpoints.** All documented at http://localhost:8000/docs when running.

---

**Built for real estate investors who want intelligence, not interfaces.**
