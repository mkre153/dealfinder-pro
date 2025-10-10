# DealFinder Pro v2.0

**AI-Powered Property Intelligence Platform for GoHighLevel Users**

Modern Next.js + FastAPI architecture with autonomous AI agents that monitor properties 24/7 and deliver matches directly to your GoHighLevel CRM.

---

## What is DealFinder Pro?

DealFinder Pro is an **intelligence layer** that sits between property data sources and your GoHighLevel CRM. Instead of building another dashboard you'll never use, we provide a **3-minute conversational setup** that creates autonomous agents monitoring properties forever.

**Core Innovation:** Chat with Claude AI for 3 minutes → Agent monitors 24/7 → Matches appear in GoHighLevel → You never need to return to our site.

---

## Quick Start

### Step 1: Start Backend API
```bash
cd "/Users/mikekwak/Real Estate Valuation"
./start_api.sh
```
Backend: http://localhost:8000
Docs: http://localhost:8000/docs

### Step 2: Start Frontend
```bash
cd dealfinder-web
./start-dev.sh
```
Frontend: http://localhost:3000

### Step 3: Create Your First Agent
1. Visit http://localhost:3000
2. Click "Start with AI"
3. Chat with Claude for 3 minutes
4. Agent created and monitoring starts!

---

## Architecture

### System Overview

```
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│   Next.js    │→ │   FastAPI    │→ │   Python     │
│   Frontend   │  │   REST API   │  │   Modules    │
│   (Vercel)   │  │  (Railway)   │  │  (Core)      │
└──────────────┘  └──────────────┘  └──────────────┘
Port 3000         Port 8000         In-process
```

### Technology Stack

**Frontend:**
- Next.js 14 (App Router, TypeScript)
- Tailwind CSS v3
- Framer Motion (animations)
- Axios (HTTP client)

**Backend:**
- FastAPI (Python 3.9+)
- Pydantic v2 (validation)
- Uvicorn (ASGI server)
- APScheduler (background jobs)

**Core Modules (unchanged from v1):**
- AI Agent (Claude integration)
- Search Agent (autonomous monitoring)
- Agent Manager (lifecycle management)
- Database (SQLite/PostgreSQL)
- GHL Connector (GoHighLevel API)

---

## Key Features

### 1. AI-Powered Setup (3 minutes)
- Conversational interface with Claude
- Natural language property criteria
- Automatic criteria extraction
- Visual review before creation

### 2. Autonomous Monitoring (24/7)
- Background agents check every 4 hours
- Smart matching algorithm (0-100 score)
- Duplicate detection
- Price reduction tracking

### 3. GoHighLevel Integration
- Auto-create opportunities in GHL
- Match scoring and reasons in notes
- Workflow triggers
- SMS/Email notifications

### 4. Zero Daily Maintenance
- Set it and forget it
- Matches appear in GHL automatically
- No dashboard to check
- No manual data entry

---

## Product Strategy

### Old Architecture (Streamlit v1)
- ❌ 7-page dashboard
- ❌ Complex form filling (15 min setup)
- ❌ User manages everything in our app
- ❌ Daily checking required

### New Architecture (Next.js v2)
- ✅ 2-page wizard (landing + setup)
- ✅ AI conversation (3 min setup)
- ✅ User manages in GoHighLevel
- ✅ Zero daily maintenance

**Strategic Shift:** From "we are the dashboard" to "we are the intelligence layer"

---

## Project Structure

```
Real Estate Valuation/
├── api/                          # FastAPI Backend
│   ├── main.py                  # Main application (21 endpoints)
│   ├── models/schemas.py        # Pydantic models
│   └── routes/
│       ├── agents.py            # Agent CRUD
│       ├── chat.py              # AI conversation
│       └── properties.py        # Property search
│
├── dealfinder-web/              # Next.js Frontend
│   ├── app/
│   │   ├── page.tsx            # Landing page
│   │   └── setup/page.tsx      # AI wizard
│   └── lib/
│       ├── api-client.ts        # API integration
│       └── types.ts             # TypeScript types
│
├── modules/                      # Core Python Modules
│   ├── ai_agent.py              # Claude integration
│   ├── search_agent.py          # Autonomous monitoring
│   ├── agent_manager.py         # Lifecycle management
│   ├── client_db.py             # Database operations
│   └── property_scanner.py      # Property data collection
│
├── integrations/                 # External Integrations
│   └── ghl_connector.py         # GoHighLevel API
│
├── docs/                         # Documentation
│   ├── PRD_V2.md                # Product requirements
│   ├── ARCHITECTURE_V2.md       # Technical architecture
│   ├── USER_JOURNEY_V2.md       # User experience
│   ├── MIGRATION_GUIDE.md       # V1 → V2 changes
│   └── DOCUMENTATION_INDEX.md   # Master index
│
├── database/                     # Database
│   └── dealfinder.db            # SQLite (dev)
│
├── data/                         # Property Data
│   └── latest_scan.json         # Latest property scan
│
└── archive/                      # Old Documentation
    └── streamlit_v1_docs/       # Archived Streamlit docs
```

---

## Documentation

### Getting Started
- **START_HERE.md** - Quick start guide (5 min)
- **NEXTJS_SETUP.md** - Detailed setup instructions

### Product Documentation
- **docs/PRD_V2.md** - Product vision and requirements
- **docs/USER_JOURNEY_V2.md** - User experience flow
- **docs/MIGRATION_GUIDE.md** - Streamlit → Next.js migration

### Technical Documentation
- **docs/ARCHITECTURE_V2.md** - System architecture
- **docs/DOCUMENTATION_INDEX.md** - Master navigation

### API Reference
- **http://localhost:8000/docs** - Interactive API documentation (FastAPI)

---

## Key Differentiators

### vs Traditional Property Search Tools
| Feature | Traditional | DealFinder Pro |
|---------|-------------|----------------|
| Setup Time | 15 minutes | 3 minutes |
| Configuration | Complex forms | AI conversation |
| Daily Maintenance | 15-30 min | 0 min |
| Property Management | External site | Your GoHighLevel |
| AI Intelligence | None | Claude-powered |

### vs Building In-House
- **Cost:** $50/mo vs $10K+ development
- **Time:** 3 minutes vs weeks/months
- **Maintenance:** Zero vs ongoing dev time
- **AI Quality:** Claude API vs DIY

---

## User Experience

### Setup Flow (3 minutes)

```
1. Land on homepage
   ↓
2. Click "Start with AI"
   ↓
3. Chat with Claude:
   AI: "What type of properties are you targeting?"
   User: "Investment properties in San Diego, $600K-$1.2M"
   AI: "Got it. What's your minimum size requirement?"
   User: "At least 3 beds, 2 baths"
   AI: "Perfect! One more question..."
   ↓
4. Review extracted criteria
   📍 Locations: 92037, 92130
   💰 Price Range: $600K - $1.2M
   🏠 Property Size: 3+ beds, 2+ baths
   ↓
5. Enter name and click "Create Agent"
   ↓
6. Agent monitoring starts immediately!
```

### Daily Experience (zero work)

```
Morning: Wake up
   ↓
Check GoHighLevel
   ↓
See 2 new opportunities
   ↓
Review match scores and reasons
   ↓
Contact interested properties
   ↓
Done! (Agent continues monitoring 24/7)
```

---

## Success Metrics

### Time Savings
- **Setup:** 15 min → 3 min (80% reduction)
- **Daily maintenance:** 15 min → 0 min (100% elimination)
- **Monthly time:** 300+ min → 3 min (99% reduction)

### User Experience
- **Configuration:** Forms → Conversation
- **Property viewing:** Dashboard → GoHighLevel
- **Notifications:** Manual check → Automatic alerts
- **Match quality:** Generic → AI-scored with reasoning

---

## Development

### Local Development

**Terminal 1 (Backend):**
```bash
cd "/Users/mikekwak/Real Estate Valuation"
./start_api.sh

# Or manually:
python3 -m venv venv
source venv/bin/activate
pip install -r requirements_api.txt
uvicorn api.main:app --reload
```

**Terminal 2 (Frontend):**
```bash
cd dealfinder-web
./start-dev.sh

# Or manually:
npm install
npm run dev
```

### Environment Variables

**Backend (.env):**
```bash
ANTHROPIC_API_KEY=your_claude_api_key
GHL_API_KEY=your_ghl_api_key
GHL_LOCATION_ID=your_location_id
DATABASE_URL=sqlite:///database/dealfinder.db
```

**Frontend (.env.local):**
```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### Testing

```bash
# Test backend API
curl http://localhost:8000/health

# Test agent creation
curl -X POST http://localhost:8000/api/agents/ \
  -H "Content-Type: application/json" \
  -d '{"client_name": "Test", "criteria": {...}}'

# View API docs
open http://localhost:8000/docs
```

---

## Deployment

### Frontend (Vercel)
```bash
cd dealfinder-web
vercel deploy --prod
```

### Backend (Railway)
```bash
railway up
```

See **docs/ARCHITECTURE_V2.md** for complete deployment guide.

---

## Roadmap

### Phase 1 ✅ (Complete)
- FastAPI backend with 21 endpoints
- Agent CRUD operations
- AI chat with Claude
- Property search

### Phase 2 ✅ (Complete)
- Next.js frontend
- Landing page with animations
- AI setup wizard
- Production build

### Phase 3 🔜 (In Progress)
- GHL opportunity auto-creation
- Custom field mapping
- Workflow integration
- End-to-end testing

### Phase 4 📅 (Planned)
- Production deployment
- Domain setup
- Monitoring (Sentry)
- User onboarding

### Phase 5 🔮 (Future)
- User authentication
- Billing integration
- Agent feedback loop
- Mobile app

---

## Migration from V1

If you were using the old Streamlit dashboard, see **docs/MIGRATION_GUIDE.md** for:

- What changed (UI/UX complete overhaul)
- What stayed same (core modules 100% preserved)
- File structure changes
- Testing checklist
- Rollback plan

**Good news:** No data migration needed! Your existing SQLite database works as-is.

---

## Support & Resources

**Documentation:**
- Complete docs in `docs/` folder
- Master index: `docs/DOCUMENTATION_INDEX.md`
- Quick start: `START_HERE.md`

**API Documentation:**
- Interactive: http://localhost:8000/docs
- All 21 endpoints documented

**External Links:**
- [Next.js Docs](https://nextjs.org/docs)
- [FastAPI Docs](https://fastapi.tiangolo.com/)
- [GoHighLevel API](https://highlevel.stoplight.io/)
- [Claude API](https://docs.anthropic.com/)

---

## License

Proprietary - All Rights Reserved

---

## Changelog

### Version 2.0.0 (October 2025)
- Complete architecture transformation (Streamlit → Next.js + FastAPI)
- AI-powered conversational setup
- GHL-first product strategy
- 2-page wizard (vs 7-page dashboard)
- 99% reduction in user time investment

### Version 1.0.0 (October 2025)
- Initial Streamlit dashboard
- Manual configuration forms
- 7-page interface
- PostgreSQL integration
- GHL connector

---

**Built with ❤️ for Real Estate Investors**

**Powered by:** Next.js | FastAPI | Claude AI | GoHighLevel
