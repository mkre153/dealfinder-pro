# DealFinder Pro - Documentation Index

**Complete Documentation Suite for Next.js + FastAPI Architecture**

Last Updated: October 2025

---

## Quick Navigation

### 🚀 Getting Started
- [START_HERE.md](../START_HERE.md) - Quick start guide (5 min)
- [NEXTJS_SETUP.md](../NEXTJS_SETUP.md) - Detailed setup instructions

### 📋 Product Documentation
- [PRD_V2.md](PRD_V2.md) - Product requirements and vision
- [USER_JOURNEY_V2.md](USER_JOURNEY_V2.md) - User experience flow
- [MIGRATION_GUIDE.md](MIGRATION_GUIDE.md) - Streamlit → Next.js migration

### 🏗️ Technical Documentation
- [ARCHITECTURE_V2.md](ARCHITECTURE_V2.md) - System architecture
- [API_REFERENCE.md](#) - API endpoints (or visit `/docs`)
- [DEPLOYMENT_GUIDE.md](#) - Production deployment

### 🤖 Agent System
- [AGENTIC_SYSTEM_V2.md](AGENTIC_SYSTEM_V2.md) - Autonomous agent deep dive

---

## Documentation Overview

### For Product Managers / Stakeholders

**Start here to understand the product vision:**

1. **[PRD_V2.md](PRD_V2.md)** (15 min read)
   - Product vision: "AI Property Scout for GoHighLevel"
   - Target users and personas
   - Core features and functionality
   - Success metrics
   - Competitive analysis
   - Pricing strategy
   - Product roadmap

   **Key insight:** We pivoted from a 7-page dashboard to a 2-page wizard. Users configure once via AI chat, then manage everything in GoHighLevel.

2. **[USER_JOURNEY_V2.md](USER_JOURNEY_V2.md)** (20 min read)
   - Complete user flow (7 phases)
   - Detailed conversation examples
   - Time savings analysis (99% reduction)
   - UX principles
   - Edge cases and error handling

   **Key insight:** Setup time reduced from 15 minutes to 3 minutes via conversational AI.

### For Developers / Technical Team

**Start here to understand the implementation:**

1. **[ARCHITECTURE_V2.md](ARCHITECTURE_V2.md)** (25 min read)
   - Complete system architecture with diagrams
   - Technology stack breakdown
   - Component structure
   - API architecture (21 endpoints)
   - Database schema
   - Data flow diagrams
   - Deployment strategy
   - Performance characteristics

   **Key insight:** Decoupled architecture allows independent scaling of frontend (Vercel) and backend (Railway).

2. **[MIGRATION_GUIDE.md](MIGRATION_GUIDE.md)** (15 min read)
   - What changed (UI/UX complete overhaul)
   - What stayed the same (core modules 100% preserved)
   - File structure comparison
   - Feature mapping
   - Code migration examples
   - Testing checklist

   **Key insight:** Core business logic unchanged. No data migration needed. Can rollback to Streamlit if needed.

3. **[AGENTIC_SYSTEM_V2.md](AGENTIC_SYSTEM_V2.md)** (30 min read)
   - Three-layer agent architecture
   - Complete agent lifecycle with state machine
   - System flowcharts (creation, check cycle, GHL integration)
   - Component details (Agent Manager, Search Agent, AI Agent)
   - Matching algorithm (0-100 scoring system)
   - Monitoring, health, and error recovery
   - Scaling and performance optimization

   **Key insight:** Autonomous agents run 24/7 with zero maintenance. Users set it up once via 3-minute AI chat, then matches appear automatically in GoHighLevel.

### For New Developers

**Onboarding path (1-2 hours):**

```
1. START_HERE.md (5 min)
   ↓ Get both services running locally

2. ARCHITECTURE_V2.md (25 min)
   ↓ Understand system structure

3. AGENTIC_SYSTEM_V2.md (30 min)
   ↓ Understand autonomous agent system

4. USER_JOURNEY_V2.md (20 min)
   ↓ Understand user experience

5. MIGRATION_GUIDE.md (15 min)
   ↓ Understand evolution from V1

6. Explore codebase
   - api/main.py - FastAPI app
   - dealfinder-web/app/ - Next.js pages
   - modules/ - Core Python logic (agents!)
```

---

## Architecture Quick Reference

### System Components

```
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│   Next.js    │→ │   FastAPI    │→ │   Python     │
│   Frontend   │  │   REST API   │  │   Modules    │
│   (Vercel)   │  │  (Railway)   │  │  (Core)      │
└──────────────┘  └──────────────┘  └──────────────┘
Port 3000         Port 8000         In-process
```

**Frontend (Next.js 14):**
- Landing page: `dealfinder-web/app/page.tsx`
- AI wizard: `dealfinder-web/app/setup/page.tsx`
- API client: `dealfinder-web/lib/api-client.ts`
- Types: `dealfinder-web/lib/types.ts`

**Backend (FastAPI):**
- Main app: `api/main.py`
- Schemas: `api/models/schemas.py`
- Agent routes: `api/routes/agents.py`
- Chat routes: `api/routes/chat.py`
- Property routes: `api/routes/properties.py`

**Core Modules (Python):**
- AI agent: `modules/ai_agent.py`
- Search agent: `modules/search_agent.py`
- Agent manager: `modules/agent_manager.py`
- Database: `modules/client_db.py`
- GHL integration: `integrations/ghl_connector.py`

---

## Key Features by Phase

### Phase 1: Setup (3 minutes)
**User Experience:**
- Land on homepage
- Click "Start with AI"
- Chat with Claude for 3 minutes
- Review extracted criteria
- Create agent

**Technical Flow:**
- Next.js renders landing page
- User clicks CTA → `/setup`
- Frontend calls `/api/chat/` (FastAPI)
- Claude extracts criteria
- Frontend calls `/api/agents/` (FastAPI)
- Agent created in database
- APScheduler starts monitoring

### Phase 2: Autonomous Monitoring (24/7)
**User Experience:**
- Zero user action required
- Agent checks properties every 4 hours
- Matches appear in GoHighLevel
- Notifications sent automatically

**Technical Flow:**
- APScheduler triggers agent check
- Agent loads latest property scan
- Filters by ZIP codes, price, beds, baths
- Calculates match score (0-100)
- Stores matches in database
- Creates GHL opportunities
- Sends notifications

### Phase 3: Match Management (In GHL)
**User Experience:**
- Log into GoHighLevel
- See opportunities in pipeline
- Review match scores and reasons
- Contact sellers
- Manage in CRM

**Technical Flow:**
- GHL API creates opportunity
- Custom fields populated
- Match notes attached
- Workflows triggered
- User manages in GHL

---

## API Reference Quick Links

**Base URL:** `http://localhost:8000` (dev) or `https://api.dealfinder.app` (prod)

**Interactive Docs:** `http://localhost:8000/docs`

### Core Endpoints

**Agents:**
- `POST /api/agents/` - Create agent
- `GET /api/agents/` - List all agents
- `GET /api/agents/{id}` - Get agent details
- `PATCH /api/agents/{id}` - Update agent
- `DELETE /api/agents/{id}` - Delete agent
- `POST /api/agents/{id}/check` - Force check
- `POST /api/agents/{id}/pause` - Pause agent
- `POST /api/agents/{id}/resume` - Resume agent

**Chat:**
- `POST /api/chat/` - Send message to AI
- `POST /api/chat/extract-criteria` - Extract criteria
- `POST /api/chat/clear` - Clear conversation

**Properties:**
- `GET /api/properties/` - Search properties
- `GET /api/properties/{id}` - Get property details
- `POST /api/properties/scan` - Trigger scan
- `GET /api/properties/recent` - Recent properties

**Health:**
- `GET /health` - API health check

---

## Database Schema Quick Reference

### Tables

**clients**
- `client_id` (PRIMARY KEY)
- `name`
- `email`
- `phone`
- `created_at`

**search_criteria**
- `criteria_id` (PRIMARY KEY)
- `zip_codes` (JSON)
- `price_min`
- `price_max`
- `bedrooms_min`
- `bathrooms_min`
- `property_types` (JSON)
- `deal_quality` (JSON)
- `min_score`
- `investment_type`

**search_agents**
- `agent_id` (PRIMARY KEY)
- `client_id` (FOREIGN KEY)
- `criteria_id` (FOREIGN KEY)
- `status` (active/paused/cancelled/completed)
- `created_at`
- `last_check`
- `next_check`
- `check_count`
- `match_count`

**property_matches**
- `match_id` (PRIMARY KEY)
- `agent_id` (FOREIGN KEY)
- `property_id`
- `match_score`
- `match_reasons` (JSON)
- `property_data` (JSON)
- `matched_at`

---

## Common Development Tasks

### Start Development Environment

**Terminal 1 (Backend):**
```bash
cd "/Users/mikekwak/Real Estate Valuation"
./start_api.sh
```

**Terminal 2 (Frontend):**
```bash
cd dealfinder-web
./start-dev.sh
```

**Verify:**
- Backend: http://localhost:8000/docs
- Frontend: http://localhost:3000

### Test Agent Creation

```bash
# 1. Start both services
# 2. Visit http://localhost:3000/setup
# 3. Chat with AI
# 4. Create agent
# 5. Check database:
sqlite3 database/dealfinder.db "SELECT * FROM search_agents;"
```

### Force Agent Check

```bash
# Get agent ID
curl http://localhost:8000/api/agents/

# Trigger check
curl -X POST http://localhost:8000/api/agents/{agent_id}/check
```

### View Logs

```bash
# Backend logs (uvicorn)
tail -f nohup.out

# Agent manager logs
grep "Agent" nohup.out | tail -20
```

---

## Deployment Quick Reference

### Frontend (Vercel)

```bash
cd dealfinder-web

# Build locally
npm run build

# Deploy to Vercel
vercel deploy

# Production deploy
vercel deploy --prod
```

**Environment Variables:**
- `NEXT_PUBLIC_API_URL` - Backend API URL

### Backend (Railway)

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login
railway login

# Deploy
railway up
```

**Environment Variables:**
- `DATABASE_URL` - PostgreSQL connection string
- `ANTHROPIC_API_KEY` - Claude API key
- `GHL_API_KEY` - GoHighLevel API key
- `GHL_LOCATION_ID` - GHL location ID
- `TWILIO_*` - Twilio credentials (if using SMS)
- `GMAIL_*` - Gmail credentials (if using email)

---

## Success Metrics Dashboard

### Acquisition
- Landing page views
- Landing → Setup click-through: **Target 40%+**
- Setup started → Completed: **Target 70%+**
- Average setup time: **Target <5 min**

### Engagement
- Agents created per week
- Average matches per agent: **Target 3-10/month**
- User creates 2nd agent: **Target 30%+**

### Retention
- Active agents (checked in 24h): **Target 80%+**
- Agent uptime: **Target 95%+**
- Agents paused by user: **Target <20%**

### Quality
- Match relevance rating: **Target 4+/5**
- False positive rate: **Target <10%**
- Notification delivery: **Target <5 min**

---

## Troubleshooting

### Backend won't start
```bash
# Check Python version
python3 --version  # Should be 3.9+

# Check dependencies
pip list | grep fastapi
pip list | grep pydantic

# Reinstall if needed
pip install -r requirements_api.txt
```

### Frontend won't start
```bash
# Check Node version
node --version  # Should be 18+

# Reinstall dependencies
cd dealfinder-web
rm -rf node_modules package-lock.json
npm install
```

### Agent not checking
```bash
# Check agent status
curl http://localhost:8000/api/agents/

# Check logs
grep "Agent.*check" nohup.out | tail -20

# Force check
curl -X POST http://localhost:8000/api/agents/{id}/check
```

### Database errors
```bash
# Check database exists
ls -lh database/dealfinder.db

# Check schema
sqlite3 database/dealfinder.db ".schema"

# Reset database (CAUTION: deletes data)
rm database/dealfinder.db
python3 modules/client_db.py  # Recreate
```

---

## Glossary

**Agent** - Autonomous background process that monitors properties and finds matches

**BANT** - Budget, Authority, Need, Timeline (sales qualification framework)

**Client** - User of DealFinder Pro (real estate investor)

**Criteria** - Property search parameters (ZIP codes, price, beds, baths, etc.)

**Deal Quality** - HOT (exceptional), GOOD (strong), FAIR (acceptable)

**GHL** - GoHighLevel (CRM platform)

**Investment Type** - cash_flow, appreciation, or balanced

**Match** - Property that meets client's criteria with high score

**Match Score** - 0-100 rating of how well property matches criteria

**Opportunity** - GHL pipeline record created for each match

**Senior Acquisition Specialist** - AI persona used in chat (professional, BANT-focused)

---

## Additional Resources

### External Links
- [Next.js Documentation](https://nextjs.org/docs)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [GoHighLevel API](https://highlevel.stoplight.io/)
- [Claude API](https://docs.anthropic.com/)
- [Vercel Deployment](https://vercel.com/docs)
- [Railway Deployment](https://docs.railway.app/)

### Project Links
- GitHub Repository: (configure)
- Production Frontend: https://dealfinder.app (future)
- Production API: https://api.dealfinder.app (future)
- Status Page: (future)

---

## Change Log

**October 2025 - V2.0 Complete Rewrite**
- Architecture: Streamlit → Next.js + FastAPI
- UI: 7-page dashboard → 2-page wizard
- Setup: Form filling → AI conversation
- Product: Dashboard → Intelligence layer
- Deployment: Single app → Vercel + Railway

**October 2025 - V1.0 Initial Version**
- Streamlit 7-page dashboard
- Manual configuration forms
- All features in single app

---

**Documentation complete.** This index provides navigation to all documentation and quick reference for common tasks.
