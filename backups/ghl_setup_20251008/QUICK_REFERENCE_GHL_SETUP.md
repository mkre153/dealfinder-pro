# Quick Reference: GHL Setup for Agents

**Account**: "Real Estate Valuation" (your FIRST and ONLY GHL)
**Purpose**: Connect agents to GHL for automated CRM

---

## 📋 Checklist

### Get Credentials
- [ ] GHL API Key from "Real Estate Valuation" account
- [ ] GHL Location ID from "Real Estate Valuation" account
- [ ] Claude API key from console.anthropic.com

### Create .env
- [ ] Copy: `cp .env.example .env`
- [ ] Add GHL_API_KEY
- [ ] Add GHL_LOCATION_ID
- [ ] Add ANTHROPIC_API_KEY
- [ ] Add database credentials

### GHL Configuration
- [ ] Create custom fields (Opportunities): deal_score, property_address, list_price, etc.
- [ ] Create custom fields (Contacts): budget_min, budget_max, etc.
- [ ] Create pipeline: "Investment Properties"
- [ ] Add stages: New Lead, Hot Lead, Priority Review, etc.
- [ ] Copy Pipeline ID to .env
- [ ] Copy Stage IDs to .env

### Local Setup
- [ ] Run: `pip install anthropic openai`
- [ ] Run: `psql dealfinder < database/agent_memory_schema.sql`

### Test
- [ ] Run: `python main.py --test-ghl` → ✅ Success
- [ ] Run: `python examples/agents/agent_ghl_integration.py` → Creates opportunity
- [ ] Check GHL dashboard → See test opportunity

---

## 🔑 Where to Get What

| What You Need | Where to Get It |
|---------------|-----------------|
| GHL API Key | GHL → Settings → Integrations → API Key |
| GHL Location ID | GHL → Settings → Business Profile → Location ID |
| Claude API Key | https://console.anthropic.com/ → Get API Keys |
| Pipeline ID | GHL → Opportunities → Pipelines → (copy from URL) |
| Stage IDs | GHL → Click each stage → (copy from URL) |

---

## 💻 Commands

```bash
# Create .env
cp .env.example .env

# Install dependencies
pip install anthropic openai

# Create database tables
psql dealfinder < database/agent_memory_schema.sql

# Test GHL connection
python main.py --test-ghl

# Test agent + GHL
python examples/agents/agent_ghl_integration.py
```

---

## 📄 .env Template

```bash
# GHL - "Real Estate Valuation" Account
GHL_API_KEY=your_api_key_here
GHL_LOCATION_ID=your_location_id_here
GHL_PIPELINE_ID=your_pipeline_id
GHL_STAGE_NEW=new_stage_id
GHL_STAGE_HOT=hot_stage_id
GHL_STAGE_PRIORITY=priority_stage_id

# LLM
ANTHROPIC_API_KEY=sk-ant-your-key

# Database
DB_USER=postgres
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=5432
DB_NAME=dealfinder
```

---

## 🏗️ GHL Custom Fields

### For Opportunities
- `deal_score` (Number)
- `property_address` (Text)
- `list_price` (Currency)
- `est_profit` (Currency)
- `mls_id` (Text)
- `price_per_sqft` (Number)
- `below_market_pct` (Number)
- `days_on_market` (Number)
- `deal_quality` (Dropdown: HOT DEAL, GOOD, FAIR, PASS)
- `estimated_arv` (Currency)

### For Contacts/Buyers
- `budget_min` (Currency)
- `budget_max` (Currency)
- `location_preference` (Text)
- `property_type_preference` (Dropdown)
- `min_bedrooms` (Number)
- `buyer_status` (Dropdown: Active, Passive, On Hold)

---

## 🔧 Troubleshooting

| Error | Fix |
|-------|-----|
| "GHL_API_KEY not found" | Check .env file exists, check variable name |
| "Authentication failed" | Regenerate API key in GHL, copy entire key |
| "Custom field not found" | Create field in GHL, restart script |
| "Pipeline not found" | Check Pipeline ID in .env matches GHL |

---

## 📚 Documentation

- **START_HERE.md** - Read this first
- **SETUP_REAL_ESTATE_VALUATION_GHL.md** - Complete setup guide
- **GHL_INTEGRATION_SUMMARY.md** - How agents + GHL work

---

**Next Step**: Open `START_HERE.md` or `SETUP_REAL_ESTATE_VALUATION_GHL.md`
