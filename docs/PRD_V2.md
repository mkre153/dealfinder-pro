# DealFinder Pro - Product Requirements Document v2.0

**Last Updated:** October 2025
**Version:** 2.0 (Next.js + FastAPI Architecture)
**Status:** In Development

---

## Executive Summary

**DealFinder Pro** is an AI-powered property intelligence platform for GoHighLevel users. Instead of building yet another real estate dashboard, we provide a **3-minute conversational setup** that creates autonomous agents monitoring properties 24/7, with matches appearing directly in the user's existing GoHighLevel CRM.

**Core Innovation:** Users chat with Claude AI for 3 minutes → Agent monitors forever → Matches appear in GHL → User never needs to return to our site.

---

## Product Vision

### What We're Building
**"The AI Property Scout for GoHighLevel Users"**

An intelligence layer that sits between property data sources and GoHighLevel CRM, powered by autonomous AI agents that never sleep.

### What We're NOT Building
- ❌ Another CRM
- ❌ A property management dashboard
- ❌ A replacement for GoHighLevel
- ❌ Complex multi-page applications

### Core Philosophy
**"Simple UI, Powerful Intelligence"**

Users spend 3 minutes setting up → Everything else happens automatically in their existing workspace (GHL).

---

## Target Users

### Primary Persona: **The GHL Power User**
- **Who:** Real estate investors, wholesalers, agents using GoHighLevel
- **Pain:** Manually searching properties daily is time-consuming
- **Need:** Automated property monitoring that integrates with their existing CRM
- **Tech Savvy:** Comfortable with AI tools and automation
- **Budget:** $50-200/month for good automation

### Secondary Persona: **The Deal Hunter**
- **Who:** Active real estate investors looking for off-market deals
- **Pain:** Missing opportunities due to slow manual searching
- **Need:** 24/7 monitoring with instant notifications
- **Tech Savvy:** Moderate - wants "set and forget"
- **Budget:** Willing to pay for quality leads

### Anti-Persona: **The Casual Browser**
- Not serious investors
- Not using GHL or similar CRM
- Looking for free tools
- Not willing to engage with AI setup

---

## Product Strategy

### V1 Strategy (OLD - Streamlit)
❌ Build comprehensive 7-page dashboard
❌ Users manage everything in our app
❌ Complex UI with analytics, imports, schedules
❌ **Result:** Too much to build, users overwhelmed

### V2 Strategy (NEW - Next.js + GHL-First)
✅ **Minimal UI:** 2 pages (landing + setup wizard)
✅ **AI Configuration:** 3-minute conversation instead of forms
✅ **GHL Native:** All property management in user's GHL
✅ **Intelligence Focus:** Perfect the AI, not the dashboard
✅ **Result:** Faster to ship, better UX, clear differentiation

---

## Core Features

### 1. Landing Page (Homepage)
**Purpose:** Convert visitors in 30 seconds

**Features:**
- Hero section with animated background
- Clear value proposition: "AI Property Scout for GoHighLevel"
- 3-step "How It Works" visual
- Single CTA: "Start with AI"
- Social proof (target personas)
- Mobile responsive

**Success Metric:** 40%+ click-through to setup

### 2. AI Setup Wizard (Core Product)
**Purpose:** Configure autonomous agent via conversation

**Features:**
- Full-screen chat interface with Claude
- BANT qualification framework:
  - **B**udget: Price range
  - **A**uthority: Decision maker (investment type)
  - **N**eed: Property criteria (beds, baths, location)
  - **T**imeline: How soon they're buying
- Real-time message streaming
- Automatic criteria extraction
- Visual review panel (slides in when ready)
- One-click agent creation

**UX Flow:**
1. AI greeting: "What type of properties are you targeting?"
2. User responds naturally
3. AI asks 3-5 follow-up questions
4. AI extracts criteria automatically
5. Visual card appears showing configuration
6. User reviews and confirms
7. Agent created → Success!

**Success Metric:** 70%+ completion rate

### 3. Autonomous Agent System (Backend)
**Purpose:** Monitor properties 24/7 without user intervention

**Features:**
- Background scheduler (checks every 4 hours)
- Smart matching algorithm (0-100 score)
- Configurable criteria:
  - ZIP codes (multiple)
  - Price range
  - Bedrooms/bathrooms
  - Property types
  - Deal quality (HOT/GOOD/FAIR)
  - Investment type (cash flow/appreciation/balanced)
- Duplicate detection
- Match history tracking

**Success Metric:** 95%+ uptime, <5 min latency

### 4. GoHighLevel Integration (Phase 3)
**Purpose:** Push matches directly to user's CRM

**Features:**
- Auto-create opportunities in GHL pipeline
- Map property data to custom fields
- Attach match score and reasons as notes
- Trigger workflows for notifications
- Update opportunity stages
- Link to property listing URL

**Success Metric:** 100% of matches delivered to GHL

### 5. Notification System
**Purpose:** Alert users instantly when matches found

**Channels:**
- ✅ GHL Workflow (primary - user configures)
- ✅ Email (via GHL or direct)
- ✅ SMS (via GHL or Twilio)
- 🔜 Slack integration
- 🔜 Mobile push (future)

**Content:**
- Property address
- Match score (0-100)
- Top 3-5 match reasons
- Price and key metrics
- Link to GHL opportunity

**Success Metric:** <2 min notification delivery

---

## User Stories

### Epic 1: First-Time Setup
**As a** GHL user
**I want to** configure a property search agent via conversation
**So that** I don't have to fill out complex forms

**Acceptance Criteria:**
- [ ] Landing page loads in <2 seconds
- [ ] AI responds to chat within 3 seconds
- [ ] Conversation completes in 3-5 exchanges
- [ ] Criteria auto-extracted and displayed visually
- [ ] Agent created with single button click
- [ ] Success confirmation shown

### Epic 2: Autonomous Monitoring
**As a** real estate investor
**I want** my agent to monitor properties automatically
**So that** I never miss an opportunity

**Acceptance Criteria:**
- [ ] Agent checks properties every 4 hours
- [ ] Matches are scored 0-100
- [ ] Duplicates are filtered out
- [ ] Match history is stored
- [ ] Agent can be paused/resumed
- [ ] Health monitoring shows agent status

### Epic 3: GHL Integration
**As a** GHL power user
**I want** property matches in my existing pipeline
**So that** I can manage everything in one place

**Acceptance Criteria:**
- [ ] Matches create opportunities automatically
- [ ] Property data maps to custom fields
- [ ] Match score included in notes
- [ ] Workflows trigger on new opportunities
- [ ] Opportunity links to listing URL
- [ ] No manual data entry required

### Epic 4: Match Quality
**As an** investor
**I want** high-quality, relevant matches
**So that** I don't waste time on bad leads

**Acceptance Criteria:**
- [ ] Matches meet all configured criteria
- [ ] Score reflects actual opportunity quality
- [ ] Match reasons are clear and specific
- [ ] False positive rate <10%
- [ ] User can provide feedback
- [ ] Agent learns from feedback (future)

---

## Technical Requirements

### Frontend (Next.js)
**Framework:** Next.js 14 (App Router)
**Language:** TypeScript
**Styling:** Tailwind CSS v3
**Animations:** Framer Motion
**Icons:** Lucide React
**Deployment:** Vercel

**Performance:**
- First Load JS: <150 KB
- Time to Interactive: <3 seconds
- Lighthouse Score: 90+

### Backend (FastAPI)
**Framework:** FastAPI
**Language:** Python 3.9+
**Database:** SQLite (dev), PostgreSQL (prod)
**Task Queue:** APScheduler
**Deployment:** Railway or Render

**Performance:**
- API Response: <500ms (p95)
- Agent Check: <30 seconds
- Concurrent Requests: 100+

### Core Modules (Python)
**Unchanged from V1:**
- Property scanner (homeharvest, scrapers)
- AI agent (Claude integration)
- Search agent (matching logic)
- Agent manager (lifecycle)
- Database (SQLite/PostgreSQL)
- GHL connector (API client)

### Infrastructure
**Production:**
- Frontend: Vercel (global CDN)
- Backend: Railway (US region)
- Database: Railway PostgreSQL
- Monitoring: Sentry
- Analytics: Plausible

---

## Success Metrics

### North Star Metric
**Active Agents Creating Value**
→ Number of agents that found at least 1 match in last 7 days

### Key Metrics

**Acquisition:**
- Landing page → Setup: 40%+
- Setup started → Completed: 70%+
- Setup completion time: <5 minutes (p90)

**Engagement:**
- Agents created per week
- Average matches per agent per month: 3-10
- User returns to create 2nd agent: 30%+

**Retention:**
- Active agents (checked in last 24h): 80%+
- Agents paused by user: <20%
- Agent uptime: 95%+

**Quality:**
- Match relevance (user feedback): 4+/5
- False positive rate: <10%
- Notification delivery: <5 min (p95)

---

## Competitive Analysis

### vs Redfin/Zillow Alerts
**Their Strength:** Brand recognition, comprehensive data
**Our Advantage:** AI-powered scoring, GHL integration, autonomous agents

### vs Property Scout Tools
**Their Strength:** Established user base
**Our Advantage:** AI setup (3 min vs 15 min), GHL-native, modern UI

### vs Building In-House
**Their Strength:** Full control
**Our Advantage:** $50/mo vs $10K+ development cost, instant setup

**Key Differentiator:** We're the ONLY tool that combines AI setup + GHL-native + autonomous agents.

---

## Pricing Strategy (Future)

### Freemium Model
**Free Tier:**
- 1 agent
- Check once per day
- Email notifications only
- 100 properties scanned

**Pro Tier ($49/mo):**
- 5 agents
- Check every 4 hours
- All notification channels
- Unlimited properties
- GHL integration
- Priority support

**Enterprise ($199/mo):**
- Unlimited agents
- Check every hour
- Custom integrations
- White-label option
- Dedicated support
- API access

---

## Roadmap

### Phase 1 (COMPLETE ✅)
- FastAPI backend with 21 endpoints
- Agent CRUD operations
- AI chat with Claude
- Property search

### Phase 2 (COMPLETE ✅)
- Next.js frontend
- Landing page
- AI setup wizard
- Production build

### Phase 3 (IN PROGRESS)
- GHL opportunity auto-creation
- Custom field mapping
- Workflow integration
- End-to-end testing

### Phase 4 (PLANNED)
- Production deployment
- Domain setup
- Monitoring
- User onboarding

### Phase 5 (FUTURE)
- User authentication
- Billing integration
- Agent feedback loop
- Mobile app
- Slack integration
- API marketplace

---

## Open Questions

1. **Authentication:** How do we handle user accounts? (Auth0, Supabase, or GHL OAuth?)
2. **Billing:** Stripe vs LemonSqueezy? When to implement?
3. **Property Data:** Continue with homeharvest or upgrade to MLS access?
4. **AI Cost:** How do we manage Claude API costs at scale?
5. **GHL Multi-Location:** How to handle agencies with multiple locations?

---

## Appendix

### Related Documents
- `ARCHITECTURE_V2.md` - Technical architecture
- `USER_JOURNEY_V2.md` - Detailed user experience
- `AGENTIC_SYSTEM_V2.md` - Agent system deep dive
- `MIGRATION_GUIDE.md` - Streamlit → Next.js changes

### Change Log
**v2.0 (Oct 2025):**
- Complete architecture overhaul (Next.js + FastAPI)
- Product strategy pivot (dashboard → intelligence layer)
- GHL-first approach
- AI-powered setup wizard

**v1.0 (Oct 2025):**
- Initial Streamlit dashboard
- 7-page interface
- Manual configuration
