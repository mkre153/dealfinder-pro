# Archived Documentation - Streamlit v1.0

This folder contains documentation from the original Streamlit-based dashboard architecture (v1.0), which has been replaced by the modern Next.js + FastAPI architecture (v2.0).

## What Happened?

In October 2025, DealFinder Pro underwent a complete architectural transformation:

**From:** Streamlit monolithic dashboard (7 pages, form-based config, all-in-one app)
**To:** Next.js + FastAPI decoupled architecture (2-page wizard, AI-powered setup, GHL-first)

## Why Archive These Docs?

These documents are preserved for historical reference but are **no longer accurate** for the current system:

- **PRD.md** - Old product requirements (replaced by docs/PRD_V2.md)
- **DASHBOARD_QUICKSTART.md** - Streamlit dashboard guide (no longer exists)
- **PHASE2_COMPLETE.md** - Old phase completion docs
- **AGENT_SYSTEM_GUIDE.md** - Agent docs referencing Streamlit UI
- **AGENTIC_SYSTEM_*.md** - Old agent architecture docs
- Various setup and status files from v1 development

## Current Documentation

For up-to-date documentation, see:

- **Main README.md** - Project overview and quick start
- **START_HERE.md** - Getting started guide
- **docs/PRD_V2.md** - Current product requirements
- **docs/ARCHITECTURE_V2.md** - System architecture
- **docs/USER_JOURNEY_V2.md** - User experience
- **docs/MIGRATION_GUIDE.md** - V1 → V2 changes
- **docs/DOCUMENTATION_INDEX.md** - Master documentation index

## Migration Information

See **docs/MIGRATION_GUIDE.md** for:
- What changed in v2.0
- What stayed the same (core modules)
- How to migrate from v1
- Rollback instructions

## Core Business Logic

**Important:** While the UI changed completely, the core Python modules remain unchanged:
- `modules/ai_agent.py` - Claude integration
- `modules/search_agent.py` - Autonomous monitoring
- `modules/agent_manager.py` - Lifecycle management
- `modules/client_db.py` - Database operations
- `integrations/ghl_connector.py` - GoHighLevel API

These modules work identically in both architectures!

---

**Archived:** October 2025
**Reason:** Architecture migration to Next.js + FastAPI
**Replacement:** See current docs/ folder
