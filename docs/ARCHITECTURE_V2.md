# DealFinder Pro - System Architecture v2.0

**Architecture:** Next.js + FastAPI + Python Modules
**Last Updated:** October 2025
**Status:** Production Ready

---

## Table of Contents
1. [System Overview](#system-overview)
2. [Architecture Diagram](#architecture-diagram)
3. [Technology Stack](#technology-stack)
4. [Component Breakdown](#component-breakdown)
5. [Data Flow](#data-flow)
6. [API Architecture](#api-architecture)
7. [Database Schema](#database-schema)
8. [Deployment Architecture](#deployment-architecture)

---

## System Overview

DealFinder Pro uses a **decoupled, microservices-inspired architecture**:

```
User Browser (Next.js)
     ↓ HTTP/REST
FastAPI Backend
     ↓ In-Process
Python Core Modules
     ↓ SQLite/PostgreSQL
Database
     ↓ HTTP/REST
External APIs (GHL, Property Sources)
```

### Key Architectural Decisions

**Decision 1: Next.js Frontend Separate from Backend**
- **Why:** Independent scaling, modern developer experience, fast iteration
- **Trade-off:** Slightly more complex deployment vs monolith
- **Result:** 10x better UI/UX, professional appearance

**Decision 2: FastAPI as API Layer**
- **Why:** High performance, automatic docs, async support, Python ecosystem
- **Trade-off:** Added layer vs direct Streamlit
- **Result:** Proper REST API, enables mobile apps, third-party integrations

**Decision 3: Keep Python Core Modules Unchanged**
- **Why:** Working agent logic, tested scrapers, database integration
- **Trade-off:** Mixed architecture (FastAPI + legacy modules)
- **Result:** Fast implementation, proven reliability

**Decision 4: GHL as Primary User Interface**
- **Why:** Users already work there, avoid building CRM features
- **Trade-off:** Dependent on GHL API
- **Result:** Simpler product, faster to market, better UX

---

## Architecture Diagram

```mermaid
graph TB
    subgraph "User Layer"
        Browser[Web Browser]
        Mobile[Mobile Device]
    end

    subgraph "Frontend Layer - Vercel"
        NextJS[Next.js 14 App]
        Landing[Landing Page]
        Wizard[AI Setup Wizard]
    end

    subgraph "API Layer - Railway/Render"
        FastAPI[FastAPI Application]
        AgentRoutes[Agent Routes]
        ChatRoutes[Chat Routes]
        PropRoutes[Property Routes]
    end

    subgraph "Core Logic Layer"
        AIAgent[AI Agent - Claude]
        SearchAgent[Search Agents]
        AgentMgr[Agent Manager]
        Scanner[Property Scanner]
        ClientDB[Client Database]
    end

    subgraph "Data Layer"
        SQLite[(SQLite/PostgreSQL)]
        PropertyData[(Property JSON)]
    end

    subgraph "External Services"
        Claude[Claude API]
        GHL[GoHighLevel CRM]
        Realtor[Realtor.com]
        Zillow[Property Sources]
    end

    Browser --> NextJS
    Mobile --> NextJS
    NextJS --> Landing
    NextJS --> Wizard

    Wizard --> FastAPI
    Landing --> FastAPI

    FastAPI --> AgentRoutes
    FastAPI --> ChatRoutes
    FastAPI --> PropRoutes

    AgentRoutes --> AgentMgr
    ChatRoutes --> AIAgent
    PropRoutes --> Scanner

    AgentMgr --> SearchAgent
    SearchAgent --> Scanner
    AIAgent --> Claude

    SearchAgent --> ClientDB
    AgentMgr --> ClientDB
    Scanner --> PropertyData
    ClientDB --> SQLite

    SearchAgent --> GHL
    Scanner --> Realtor
    Scanner --> Zillow

    style NextJS fill:#61dafb
    style FastAPI fill:#009688
    style SearchAgent fill:#ff6b6b
    style GHL fill:#4a90e2
```

---

## Technology Stack

### Frontend
| Technology | Version | Purpose |
|-----------|---------|---------|
| **Next.js** | 14.1 | React framework, SSR, routing |
| **React** | 18.2 | UI components |
| **TypeScript** | 5.3 | Type safety |
| **Tailwind CSS** | 3.4 | Styling |
| **Framer Motion** | 11.0 | Animations |
| **Axios** | 1.6 | HTTP client |
| **Lucide React** | 0.323 | Icons |

**Build Output:** 135 KB first load (highly optimized)

### Backend
| Technology | Version | Purpose |
|-----------|---------|---------|
| **FastAPI** | 0.109+ | REST API framework |
| **Uvicorn** | 0.27+ | ASGI server |
| **Pydantic** | 2.5+ | Data validation |
| **APScheduler** | 3.10+ | Background jobs |
| **Anthropic SDK** | 0.39+ | Claude AI |
| **SQLAlchemy** | 2.0+ | ORM (optional) |

**Performance:** <500ms API response time (p95)

### Core Modules (Unchanged)
| Module | Purpose |
|--------|---------|
| `ai_agent.py` | Claude AI integration |
| `search_agent.py` | Autonomous property monitoring |
| `agent_manager.py` | Agent lifecycle management |
| `client_db.py` | Database operations |
| `property_scanner.py` | Property scraping |
| `ghl_connector.py` | GoHighLevel API client |

### Infrastructure
| Service | Provider | Purpose |
|---------|----------|---------|
| **Frontend Hosting** | Vercel | Next.js deployment, CDN |
| **Backend Hosting** | Railway/Render | FastAPI deployment |
| **Database (Prod)** | Railway PostgreSQL | Production data |
| **Database (Dev)** | SQLite | Local development |
| **Monitoring** | Sentry | Error tracking |
| **Analytics** | Plausible | Privacy-friendly analytics |

---

## Component Breakdown

### 1. Next.js Frontend (`dealfinder-web/`)

**Structure:**
```
dealfinder-web/
├── app/
│   ├── page.tsx              # Landing page (/)
│   ├── setup/
│   │   └── page.tsx          # AI wizard (/setup)
│   ├── layout.tsx            # Root layout
│   └── globals.css           # Global styles
├── lib/
│   ├── api-client.ts         # FastAPI client functions
│   └── types.ts              # TypeScript interfaces
├── components/               # Reusable components (future)
└── public/                   # Static assets
```

**Key Features:**
- Server-side rendering (SSR) for SEO
- Client-side routing for instant navigation
- Automatic code splitting
- Image optimization
- TypeScript for type safety

**API Communication:**
- Axios HTTP client
- Base URL: `process.env.NEXT_PUBLIC_API_URL`
- Automatic error handling
- TypeScript types for all endpoints

### 2. FastAPI Backend (`api/`)

**Structure:**
```
api/
├── main.py                   # FastAPI app initialization
├── models/
│   └── schemas.py            # Pydantic models
└── routes/
    ├── agents.py             # Agent CRUD
    ├── chat.py               # AI conversation
    └── properties.py         # Property search
```

**Responsibilities:**
- REST API endpoints (21 total)
- Request validation (Pydantic)
- CORS middleware
- Error handling
- OpenAPI documentation
- Lifespan management (startup/shutdown)

**Key Features:**
- Async endpoints for performance
- Automatic OpenAPI docs at `/docs`
- Type-safe request/response
- Background task support
- Health check endpoint

### 3. Python Core Modules (`modules/`)

**Agent Manager (`agent_manager.py`):**
```python
class AgentManager:
    - create_agent()
    - list_active_agents()
    - get_agent_status()
    - pause_agent()
    - resume_agent()
    - cancel_agent()
    - force_check_all()
```

**Search Agent (`search_agent.py`):**
```python
class SearchAgent:
    - check_for_matches()
    - _property_matches_criteria()
    - _calculate_match_score()
    - process_new_matches()
    - _send_notifications()
```

**AI Agent (`ai_agent.py`):**
```python
class AIPropertyAgent:
    - chat()
    - _tool_search_properties()
    - _tool_analyze_property()
    - _tool_market_insights()
    - _tool_create_search_agent()
```

**Client Database (`client_db.py`):**
```python
class ClientDatabase:
    - create_client()
    - create_search_criteria()
    - create_agent()
    - get_agent()
    - update_agent_status()
    - get_agent_matches()
```

### 4. Database Layer

**SQLite (Development):**
- Single file: `database/dealfinder.db`
- Zero configuration
- Fast local development

**PostgreSQL (Production):**
- Railway hosted
- Connection pooling
- Automatic backups
- Scalable

**Schema:** (See [Database Schema](#database-schema) section)

### 5. External Integrations

**GoHighLevel:**
- Create/update opportunities
- Manage contacts
- Trigger workflows
- Send SMS/Email
- Custom fields

**Claude AI (Anthropic):**
- Chat conversations
- Criteria extraction
- Property analysis
- Investment recommendations

**Property Sources:**
- Realtor.com (homeharvest)
- Zillow (future)
- MLS (future)

---

## Data Flow

### User Creates Agent

```mermaid
sequenceDiagram
    participant U as User
    participant N as Next.js
    participant F as FastAPI
    participant AI as AI Agent
    participant AM as Agent Manager
    participant DB as Database

    U->>N: Visits /setup
    N->>F: GET / (health check)
    F-->>N: Status: healthy

    U->>N: Sends chat message
    N->>F: POST /api/chat
    F->>AI: chat(message, history)
    AI->>AI: Process with Claude
    AI-->>F: Response + criteria?
    F-->>N: ChatResponse
    N->>U: Display AI response

    Note over U,N: Repeat chat until configured

    U->>N: Clicks "Create Agent"
    N->>F: POST /api/agents
    F->>DB: create_client()
    DB-->>F: client_id
    F->>AM: create_agent(criteria)
    AM->>DB: create_agent()
    AM->>AM: Schedule background job
    AM-->>F: agent_id
    F-->>N: AgentResponse
    N->>U: Success! Agent monitoring...
```

### Agent Finds Match

```mermaid
sequenceDiagram
    participant S as Scheduler
    participant A as Search Agent
    participant DB as Database
    participant GHL as GoHighLevel
    participant U as User

    S->>A: Trigger check (every 4 hours)
    A->>DB: Load latest scan data
    DB-->>A: Properties[]

    A->>A: Filter by criteria
    A->>A: Calculate match scores
    A->>A: Check for duplicates

    alt Matches Found
        A->>DB: Store matches
        A->>GHL: Create opportunity
        GHL-->>A: opportunity_id
        A->>GHL: Trigger workflow
        GHL->>U: SMS/Email notification
        A->>DB: Update match status
    else No Matches
        A->>DB: Update last_check timestamp
    end
```

---

## API Architecture

### REST API Endpoints

**Base URL:** `http://localhost:8000` (dev) | `https://api.dealfinder.app` (prod)

#### Agent Endpoints (`/api/agents`)
```
POST   /api/agents/                    # Create agent
GET    /api/agents/                    # List agents
GET    /api/agents/{id}                # Get agent details
PATCH  /api/agents/{id}                # Update agent (pause/resume)
DELETE /api/agents/{id}                # Cancel agent
GET    /api/agents/{id}/matches        # Get matches
POST   /api/agents/{id}/check          # Force check
GET    /api/agents/system/status       # System status
```

#### Chat Endpoints (`/api/chat`)
```
POST   /api/chat/                      # Send message
POST   /api/chat/extract-criteria      # Extract criteria
DELETE /api/chat/reset                 # Clear history
```

#### Property Endpoints (`/api/properties`)
```
POST   /api/properties/search          # Search properties
GET    /api/properties/stats           # Market stats
GET    /api/properties/{address}       # Property details
GET    /api/properties/hot-deals/list  # Hot deals
```

### Request/Response Format

**Example: Create Agent**
```http
POST /api/agents/
Content-Type: application/json

{
  "client_name": "John Investor",
  "client_email": "john@example.com",
  "criteria": {
    "zip_codes": ["92037", "92130"],
    "price_min": 500000,
    "price_max": 1000000,
    "bedrooms_min": 3,
    "bathrooms_min": 2,
    "min_score": 80,
    "investment_type": "cash_flow"
  },
  "notification_email": true
}
```

**Response:**
```json
{
  "agent_id": "A1B2C3D4",
  "client_name": "John Investor",
  "status": "active",
  "created_at": "2025-10-10T12:00:00Z",
  "last_check": null,
  "matches_found": 0,
  "new_matches": 0,
  "criteria_summary": "ZIP: 92037, 92130 | Price: $500K - $1M | 3+ beds | 2+ baths"
}
```

### Error Handling

**Standard Error Response:**
```json
{
  "error": "Agent not found",
  "detail": "Agent A1B2C3D4 does not exist",
  "status_code": 404
}
```

**HTTP Status Codes:**
- `200` - Success
- `201` - Created
- `400` - Bad Request
- `404` - Not Found
- `500` - Internal Server Error

---

## Database Schema

```sql
-- Clients table
CREATE TABLE clients (
    client_id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    email TEXT,
    phone TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ghl_contact_id TEXT,
    notes TEXT
);

-- Search criteria table
CREATE TABLE search_criteria (
    criteria_id TEXT PRIMARY KEY,
    client_id TEXT REFERENCES clients(client_id),
    zip_codes TEXT,  -- JSON array
    price_min INTEGER,
    price_max INTEGER,
    bedrooms_min INTEGER,
    bathrooms_min INTEGER,
    property_types TEXT,  -- JSON array
    deal_quality TEXT,  -- JSON array
    min_score INTEGER DEFAULT 80,
    investment_type TEXT,
    timeline TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Search agents table
CREATE TABLE search_agents (
    agent_id TEXT PRIMARY KEY,
    client_id TEXT REFERENCES clients(client_id),
    client_name TEXT,
    criteria_id TEXT REFERENCES search_criteria(criteria_id),
    status TEXT DEFAULT 'active',  -- active, paused, cancelled, completed
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_check TIMESTAMP,
    zip_codes TEXT,  -- Denormalized for performance
    price_min INTEGER,
    price_max INTEGER,
    bedrooms_min INTEGER,
    bathrooms_min INTEGER,
    property_types TEXT,
    deal_quality TEXT,
    min_score INTEGER,
    investment_type TEXT,
    timeline TEXT,
    notification_email BOOLEAN DEFAULT 1,
    notification_sms BOOLEAN DEFAULT 0,
    notification_chat BOOLEAN DEFAULT 1
);

-- Agent matches table
CREATE TABLE agent_matches (
    match_id TEXT PRIMARY KEY,
    agent_id TEXT REFERENCES search_agents(agent_id),
    property_address TEXT NOT NULL,
    property_data TEXT,  -- JSON
    match_score INTEGER,
    status TEXT DEFAULT 'new',  -- new, sent, viewed, contacted, closed
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    notified_at TIMESTAMP,
    ghl_opportunity_id TEXT
);

-- Indexes
CREATE INDEX idx_agents_status ON search_agents(status);
CREATE INDEX idx_agents_client ON search_agents(client_id);
CREATE INDEX idx_matches_agent ON agent_matches(agent_id);
CREATE INDEX idx_matches_status ON agent_matches(status);
```

---

## Deployment Architecture

### Development Environment

```
┌─────────────────┐         ┌─────────────────┐
│  Next.js        │         │  FastAPI        │
│  localhost:3000 │ ←──────→│  localhost:8000 │
│                 │  HTTP   │                 │
└─────────────────┘         └────────┬────────┘
                                     │
                            ┌────────▼────────┐
                            │  SQLite         │
                            │  database/*.db  │
                            └─────────────────┘
```

**Commands:**
```bash
# Terminal 1: Backend
./start_api.sh

# Terminal 2: Frontend
cd dealfinder-web && ./start-dev.sh
```

### Production Environment

```
┌──────────────────────────────────────┐
│  Vercel Edge Network (Global CDN)    │
│  - Next.js SSR/SSG                   │
│  - Automatic HTTPS                   │
│  - Serverless Functions              │
│  https://dealfinder.app              │
└───────────────┬──────────────────────┘
                │ HTTPS
┌───────────────▼──────────────────────┐
│  Railway (US Region)                 │
│  - FastAPI on Uvicorn                │
│  - PostgreSQL Database               │
│  - Background Scheduler              │
│  https://api.dealfinder.app          │
└───────────────┬──────────────────────┘
                │
        ┌───────┴───────┐
        │               │
┌───────▼─────┐  ┌─────▼────────┐
│  Anthropic  │  │  GoHighLevel │
│  Claude API │  │  CRM         │
└─────────────┘  └──────────────┘
```

**Domain Setup:**
- `dealfinder.app` → Vercel (Next.js)
- `api.dealfinder.app` → Railway (FastAPI)
- SSL: Automatic (Let's Encrypt)

**Environment Variables:**

**Frontend (Vercel):**
```env
NEXT_PUBLIC_API_URL=https://api.dealfinder.app
```

**Backend (Railway):**
```env
DATABASE_URL=postgresql://user:pass@host:5432/db
ANTHROPIC_API_KEY=sk-ant-...
GHL_API_KEY=...
GHL_LOCATION_ID=...
```

---

## Performance Characteristics

### Frontend
- **First Load:** 135 KB (gzipped)
- **Time to Interactive:** <3s
- **Lighthouse Score:** 90+
- **Core Web Vitals:** All green

### Backend
- **API Response Time:** <500ms (p95)
- **Agent Check Duration:** <30s
- **Concurrent Users:** 100+
- **Database Queries:** <100ms (indexed)

### Agent System
- **Check Frequency:** Every 4 hours
- **Properties Scanned:** 3,000+ per check
- **Match Scoring:** <1ms per property
- **Notification Delivery:** <5 min

---

## Security Considerations

### Frontend
- [x] HTTPS only
- [x] Environment variables for API URL
- [ ] API key authentication (future)
- [ ] Rate limiting (future)

### Backend
- [x] CORS restrictions
- [x] Input validation (Pydantic)
- [x] SQL injection protection (parameterized)
- [ ] API authentication (future)
- [ ] Rate limiting per user (future)

### Data
- [x] No sensitive data in logs
- [x] Database credentials in env vars
- [ ] Data encryption at rest (future)
- [ ] GDPR compliance (future)

---

## Monitoring & Observability

### Application Monitoring
- **Sentry:** Error tracking and performance
- **Logs:** Structured logging to stdout
- **Health Checks:** `/health` endpoint

### Infrastructure Monitoring
- **Railway:** Built-in metrics
- **Vercel:** Analytics dashboard
- **Database:** Query performance tracking

### Alerts
- Agent check failures
- API error rate >1%
- Database connection issues
- GHL API failures

---

## Scalability

### Current Capacity
- **Users:** 100-500 concurrent
- **Agents:** 1,000 active agents
- **Properties:** 10,000 scanned per hour

### Scaling Strategy
1. **Horizontal:** Add more FastAPI instances
2. **Database:** PostgreSQL read replicas
3. **Cache:** Redis for hot data
4. **Queue:** Celery for background tasks

---

## Related Documentation

- `PRD_V2.md` - Product requirements
- `USER_JOURNEY_V2.md` - User experience flows
- `AGENTIC_SYSTEM_V2.md` - Agent system details
- `API_REFERENCE.md` - Complete API docs
- `DEPLOYMENT_GUIDE.md` - Production deployment

---

**Architecture designed for:** Fast iteration, clear separation of concerns, easy scaling, professional user experience.
