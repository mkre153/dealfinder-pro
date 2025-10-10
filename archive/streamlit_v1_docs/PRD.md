# Product Requirements Document (PRD)
## DealFinder Pro - Real Estate Investment Automation Platform

**Version:** 2.0
**Last Updated:** 2025-10-08
**Status:** Active Development
**Author:** Product Team

---

## 1. EXECUTIVE SUMMARY

### 1.1 Project Overview
**Project Name:** DealFinder Pro
**Purpose:** Automated undervalued property detection system for real estate brokers with full GoHighLevel (GHL) CRM integration

### 1.2 Target Users
- Real estate brokers and agents using GoHighLevel CRM
- Real estate investors seeking undervalued properties
- Real estate agencies managing buyer databases
- Property wholesalers looking for deal flow

### 1.3 Key Differentiators
✅ **24/7 Automated Monitoring** - Never miss a deal while you sleep
✅ **Custom Scoring Algorithm** - Proprietary multi-factor analysis (0-100 scale)
✅ **Seamless GHL Integration** - Full bidirectional CRM sync
✅ **Intelligent Buyer Matching** - Automatically match properties to buyers
✅ **Multi-Source Data Aggregation** - Web scraping + MLS + proprietary databases
✅ **Automated Workflow Triggers** - Hands-free lead nurturing
✅ **Real-time SMS Alerts** - Instant notifications for hot deals

### 1.4 Business Value Proposition
- **Time Savings:** 20+ hours/week saved on manual property screening
- **Competitive Advantage:** Be first to contact sellers on undervalued properties
- **Revenue Impact:** Find 3-5 additional deals per month
- **ROI:** System pays for itself with one deal ($5K-$20K commission)
- **Scalability:** Monitor unlimited markets simultaneously

---

## 2. PROBLEM STATEMENT

### 2.1 Current Pain Points

#### For Real Estate Brokers:
❌ **Manual Screening is Time-Consuming**
- Brokers spend 15-25 hours/week reviewing listings manually
- Analysis is inconsistent and subjective
- No standardized criteria for "good deals"

❌ **Good Deals Disappear Quickly**
- Best properties receive multiple offers within 24-48 hours
- By the time broker finds deal, it's often under contract
- Missing opportunities due to delayed awareness

❌ **Multi-Market Monitoring is Impossible**
- Can't manually track 5+ ZIP codes simultaneously
- Miss deals outside primary focus area
- No way to scale without hiring more staff

❌ **Data Fragmentation**
- Property data scattered across MLS, websites, spreadsheets
- Manual data entry into CRM leads to errors
- No single source of truth for property information

❌ **Lack of Buyer-Property Matching**
- Manually matching properties to buyer criteria is tedious
- Buyers receive irrelevant listings, causing frustration
- Missed opportunities when perfect match exists in database

❌ **No Automated Follow-Up**
- Hot leads require immediate action but get lost in pipeline
- No automated task creation for showings/follow-ups
- Workflows not triggered based on deal quality

### 2.2 Market Opportunity
- **TAM (Total Addressable Market):** 2.5M real estate agents in USA
- **SAM (Serviceable Addressable Market):** 150K investment-focused brokers
- **SOM (Serviceable Obtainable Market):** 5K GoHighLevel-using brokers (Year 1 target)

---

## 3. SOLUTION OVERVIEW

### 3.1 Core Capabilities

#### **A. Automated Property Discovery**
- Daily scraping of Realtor.com using HomeHarvest library
- Import from MLS databases (RETS/WebAPI)
- CSV/Excel import for proprietary data sources
- Duplicate detection and data deduplication
- Historical price tracking and trend analysis

#### **B. Intelligent Analysis Engine**
- Multi-factor scoring algorithm (0-100 scale)
- Customizable criteria and weights
- Below-market valuation detection
- Price reduction tracking
- Days-on-market analysis
- Cap rate and cash-on-cash return calculations
- Distressed property keyword detection

#### **C. GoHighLevel CRM Integration**
- **Opportunity Management:**
  - Auto-create opportunities for scored properties
  - Populate custom fields with property data
  - Assign to users based on territory/specialization
  - Move through pipeline stages automatically

- **Contact Management:**
  - Import buyer preferences from GHL
  - Match properties to buyer criteria
  - Add tags for segmentation
  - Update custom fields with match scores

- **Workflow Automation:**
  - Trigger "Hot Deal Alert" workflow for properties scoring >90
  - Trigger "Buyer Match" workflow when property meets criteria
  - Trigger "Showing Scheduled" workflow on calendar events
  - Trigger "Offer Submitted" workflow on status change

- **Task Automation:**
  - Create "Review Property" tasks for hot deals (due in 4 hours)
  - Create "Schedule Showing" tasks (due in 24 hours)
  - Create "Contact Buyer" tasks for matches (due in 8 hours)
  - Assign tasks based on user roles

- **Communication:**
  - Send SMS via GHL for deals scoring >90
  - Send SMS to matched buyers (max 3/day per contact)
  - Add notes to opportunities with analysis details
  - Respect quiet hours (9 PM - 8 AM) and opt-out preferences

#### **D. Buyer Matching Algorithm**
Intelligent scoring system that matches properties to GHL contacts:

**Match Criteria (100-point scale):**
- Budget alignment (40 points)
  - Perfect match: Property within buyer's min/max budget
  - Near match: Within 10% tolerance
- Location preference (30 points)
  - City/neighborhood match
  - Radius-based matching
- Property type (20 points)
  - Single family, multi-family, condo, etc.
- Bedroom/bathroom count (10 points)

**Match Threshold:** Only notify buyers with >70 match score

#### **E. Automated Reporting**
- **Daily Email Report (7:20 AM):**
  - Summary of new properties found
  - Top 10 deals ranked by score
  - Price reductions from yesterday
  - Properties moving to "Under Contract"
  - GHL sync status

- **Weekly Market Analysis (Sunday 8 AM):**
  - Market trends (avg price, inventory levels)
  - Best performing ZIP codes
  - Scoring algorithm performance review
  - ROI tracking (deals closed from system)

#### **F. Data Storage & Synchronization**
- PostgreSQL primary database
- Redis caching layer (optional)
- Bidirectional sync with GHL CRM
- CSV/Excel export for reporting
- Daily automated backups

---

## 4. USER STORIES

### 4.1 Broker Persona: "John - Investment Broker"
**Background:** 10-year veteran broker specializing in fix-and-flip properties, uses GoHighLevel for CRM, manages database of 200+ active investors

#### User Stories:

**US-001: Daily Deal Discovery**
**As a** real estate broker,
**I want to** automatically scan new listings every morning,
**So that** I'm aware of opportunities before my competitors.

**Acceptance Criteria:**
- Script runs at 5:30 AM daily without manual intervention
- Scrapes target ZIP codes (configurable in config.json)
- Imports data from MLS database if connected
- Completes within 90 minutes
- Sends completion notification

---

**US-002: Hot Deal Notifications**
**As a** real estate broker,
**I want to** receive immediate SMS alerts for properties scoring >90,
**So that** I can act quickly on the best opportunities.

**Acceptance Criteria:**
- SMS sent within 5 minutes of property discovery
- Message includes address, price, score, estimated profit
- Link to GHL opportunity record
- Respects quiet hours (9 PM - 8 AM)
- Maximum 5 SMS per day (avoid alert fatigue)

---

**US-003: Automatic GHL Opportunity Creation**
**As a** real estate broker using GoHighLevel,
**I want** properties to automatically create opportunities in my pipeline,
**So that** I don't have to manually enter data.

**Acceptance Criteria:**
- Opportunity created for properties scoring >75
- Custom fields populated (address, price, score, MLS#, etc.)
- Assigned to correct user based on territory
- Placed in "New Lead" pipeline stage
- Tags added (e.g., "hot_deal", "undervalued", "automated")

---

**US-004: Buyer Matching & Notification**
**As a** real estate broker with a buyer database,
**I want** the system to automatically match properties to buyers,
**So that** I can quickly connect buyers with relevant listings.

**Acceptance Criteria:**
- System searches GHL contacts with "active_buyer" tag
- Calculates match score based on budget, location, property type
- Only matches with score >70 are acted upon
- SMS sent to buyer via GHL (requires SMS opt-in tag)
- Contact tagged with "matched_[property_id]" for tracking
- Task created: "Follow up with [buyer_name]"

---

**US-005: Workflow Automation**
**As a** real estate broker using GHL workflows,
**I want** hot deals to trigger my follow-up workflows,
**So that** my lead nurturing happens automatically.

**Acceptance Criteria:**
- Properties scoring >90 trigger "Hot Deal Alert" workflow
- Matched buyers trigger "Property Match Notification" workflow
- Workflow IDs configurable in config.json
- Workflow triggers logged in database
- Failures retry 3 times before alerting

---

**US-006: Task Automation**
**As a** real estate broker,
**I want** tasks automatically created for high-priority properties,
**So that** I never forget to follow up.

**Acceptance Criteria:**
- Task 1: "Review Hot Deal" (due in 4 hours) for score >85
- Task 2: "Schedule Showing" (due in 24 hours)
- Task 3: "Contact Matched Buyers" (due in 8 hours)
- Tasks assigned based on user role (broker vs. coordinator)
- Tasks linked to opportunity record
- High priority flag for score >90

---

**US-007: Daily Email Report**
**As a** real estate broker,
**I want** a daily summary email of new properties,
**So that** I can review opportunities over coffee each morning.

**Acceptance Criteria:**
- Email sent at 7:20 AM daily
- Includes top 10 properties ranked by score
- Shows property photos, key stats, analysis summary
- Links to GHL opportunity records
- Includes price reductions from previous day
- Summary statistics (total properties, avg score, GHL sync status)

---

**US-008: MLS Database Integration**
**As a** real estate broker with MLS access,
**I want** to import data from my MLS database,
**So that** I have complete and accurate property information.

**Acceptance Criteria:**
- Supports SQL Server, PostgreSQL, MySQL connections
- Field mapping configurable (mls_field_mapping.json)
- Runs hourly sync to catch new listings
- Merges MLS data with web-scraped data
- MLS data takes precedence in conflicts
- Logs sync errors without crashing

---

**US-009: Customizable Scoring Criteria**
**As a** real estate broker with specific investment criteria,
**I want** to customize scoring weights and thresholds,
**So that** the system matches my investment strategy.

**Acceptance Criteria:**
- Weights configurable in config.json
- Criteria include: price advantage, days on market, financial returns, condition, location
- Changes take effect on next run (no code changes needed)
- Validation prevents weights from exceeding 100 total
- Documentation explains each criterion

---

**US-010: Pipeline Stage Automation**
**As a** real estate broker,
**I want** opportunities to move through pipeline stages automatically,
**So that** my pipeline reflects current status without manual updates.

**Acceptance Criteria:**
- "Showing Scheduled" activity → moves to "Showing Scheduled" stage
- "Offer Submitted" activity → moves to "Offer Submitted" stage
- "Under Contract" status → moves to "Under Contract" stage
- Stage progression logged in GHL notes
- Manual overrides preserved (no re-assignment if broker moved manually)

---

## 5. TECHNICAL REQUIREMENTS

### 5.1 Technology Stack

#### **Core Dependencies:**
```
Python 3.10+
homeharvest==1.0.0        # Realtor.com scraping
requests==2.31.0          # HTTP client for APIs
psycopg2-binary==2.9.9    # PostgreSQL adapter
redis==5.0.1              # Caching layer (optional)
python-dotenv==1.0.0      # Environment variable management
schedule==1.2.0           # Task scheduling
pandas==2.1.3             # Data manipulation
numpy==1.26.2             # Numerical computations
jinja2==3.1.2             # Email template rendering
openpyxl==3.1.2           # Excel export
sqlalchemy==2.0.23        # Database ORM
alembic==1.13.0           # Database migrations
pytest==7.4.3             # Testing framework
```

#### **GoHighLevel Integration:**
```python
# Official GHL API v2
# Documentation: https://highlevel.stoplight.io/docs/integrations/
# Base URL: https://rest.gohighlevel.com/v1/
# Authentication: Bearer token (API key)
# Rate Limit: 100 requests/minute
```

#### **Database Support:**
**Supported SQL Databases:**
- PostgreSQL 12+ (recommended)
- MySQL 8.0+ / MariaDB 10.5+
- Microsoft SQL Server 2019+
- SQLite 3.35+ (development/testing only)

**Supported NoSQL:**
- Redis 6.0+ (caching layer)
- MongoDB 5.0+ (alternative to PostgreSQL)

**Cloud Database Support:**
- AWS RDS (PostgreSQL, MySQL, SQL Server)
- Google Cloud SQL
- Azure SQL Database
- Heroku Postgres

### 5.2 System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     DATA SOURCES                             │
├─────────────────────────────────────────────────────────────┤
│  Realtor.com   │   MLS Database   │   CSV Imports  │   APIs  │
└────────┬────────────────┬────────────────┬─────────────┬─────┘
         │                │                │             │
         ▼                ▼                ▼             ▼
┌─────────────────────────────────────────────────────────────┐
│                  DATA INGESTION LAYER                        │
├─────────────────────────────────────────────────────────────┤
│  scraper.py  │  mls_connector.py  │  csv_importer.py         │
└────────┬────────────────┬────────────────┬──────────────────┘
         │                │                │
         └────────────────┴────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│                DATA PROCESSING LAYER                         │
├─────────────────────────────────────────────────────────────┤
│  • Deduplication  • Data Enrichment  • Validation            │
│  • Field Mapping  • Price History    • Normalization         │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                 ANALYSIS ENGINE                              │
├─────────────────────────────────────────────────────────────┤
│  analyzer.py  │  scorer.py  │  valuation_model.py            │
│  • Market comparison  • Scoring algorithm  • ROI calculations │
└────────┬──────────────────────────────────────┬─────────────┘
         │                                      │
         ▼                                      ▼
┌──────────────────────────┐      ┌─────────────────────────┐
│   PRIMARY DATABASE       │      │   CACHE LAYER (Redis)   │
│   (PostgreSQL)           │◄────►│   • API responses        │
│   • Properties           │      │   • Market data          │
│   • Analysis results     │      │   • GHL contact cache    │
│   • Sync logs            │      └─────────────────────────┘
└────────┬─────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────────┐
│              GOHIGHLEVEL INTEGRATION LAYER                   │
├─────────────────────────────────────────────────────────────┤
│  ghl_connector.py  │  ghl_workflows.py  │  ghl_buyer_matcher.py│
│  • Rate limiting (100 req/min)  • Error handling             │
│  • Retry logic  • Field mapping  • Bidirectional sync        │
└────────┬────────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────────┐
│                   GOHIGHLEVEL CRM                            │
├─────────────────────────────────────────────────────────────┤
│  Opportunities  │  Contacts  │  Tasks  │  Workflows  │  SMS  │
└─────────────────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────────┐
│               NOTIFICATION LAYER                             │
├─────────────────────────────────────────────────────────────┤
│  notifier.py  │  reporter.py                                 │
│  • Email (SMTP)  • SMS (via GHL)  • Slack webhooks           │
│  • Daily reports  • Alert routing  • Template rendering      │
└─────────────────────────────────────────────────────────────┘
```

### 5.3 Data Models

#### **A. Properties Table** (PostgreSQL)
```sql
CREATE TABLE properties (
    id SERIAL PRIMARY KEY,
    property_id VARCHAR(100) UNIQUE NOT NULL,  -- Unique identifier
    mls_number VARCHAR(50),

    -- Address
    street_address VARCHAR(255) NOT NULL,
    city VARCHAR(100) NOT NULL,
    state VARCHAR(2) NOT NULL,
    zip_code VARCHAR(10) NOT NULL,
    county VARCHAR(100),
    latitude DECIMAL(10, 8),
    longitude DECIMAL(11, 8),

    -- Property Details
    property_type VARCHAR(50),  -- single_family, multi_family, condo, etc.
    bedrooms INTEGER,
    bathrooms DECIMAL(3,1),
    square_feet INTEGER,
    lot_size_sqft INTEGER,
    year_built INTEGER,
    stories INTEGER,
    garage_spaces INTEGER,

    -- Financial
    list_price DECIMAL(12,2) NOT NULL,
    price_per_sqft DECIMAL(8,2),
    previous_price DECIMAL(12,2),
    price_reduction_amount DECIMAL(12,2),
    price_reduction_date TIMESTAMP,
    tax_assessed_value DECIMAL(12,2),
    annual_taxes DECIMAL(10,2),
    hoa_fee DECIMAL(8,2),

    -- Listing Info
    listing_date TIMESTAMP,
    days_on_market INTEGER,
    listing_agent_name VARCHAR(255),
    listing_agent_phone VARCHAR(20),
    listing_agent_email VARCHAR(255),
    listing_brokerage VARCHAR(255),

    -- Description
    description TEXT,
    features TEXT[],  -- Array of features
    keywords TEXT[],  -- Extracted keywords

    -- Analysis
    opportunity_score INTEGER,  -- 0-100
    deal_quality VARCHAR(20),   -- HOT DEAL, GOOD, FAIR, PASS
    below_market_percentage DECIMAL(5,2),
    estimated_market_value DECIMAL(12,2),
    estimated_profit DECIMAL(12,2),
    cap_rate DECIMAL(5,2),
    cash_on_cash_return DECIMAL(5,2),
    analysis_date TIMESTAMP,

    -- GHL Integration
    ghl_opportunity_id VARCHAR(100),
    ghl_sync_status VARCHAR(20),  -- pending, synced, failed
    ghl_sync_date TIMESTAMP,
    ghl_sync_error TEXT,

    -- Metadata
    data_source VARCHAR(50),  -- realtor, mls, csv
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    INDEX idx_opportunity_score (opportunity_score DESC),
    INDEX idx_deal_quality (deal_quality),
    INDEX idx_days_on_market (days_on_market),
    INDEX idx_ghl_sync_status (ghl_sync_status),
    INDEX idx_created_at (created_at DESC)
);
```

#### **B. Buyers Table** (Synced from GHL)
```sql
CREATE TABLE buyers (
    id SERIAL PRIMARY KEY,
    ghl_contact_id VARCHAR(100) UNIQUE NOT NULL,

    -- Contact Info
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    email VARCHAR(255),
    phone VARCHAR(20),

    -- Preferences
    min_budget DECIMAL(12,2),
    max_budget DECIMAL(12,2),
    preferred_locations TEXT[],  -- Array of cities/ZIP codes
    property_types TEXT[],       -- Array of preferred types
    min_bedrooms INTEGER,
    min_bathrooms DECIMAL(3,1),
    min_square_feet INTEGER,

    -- Status
    buyer_status VARCHAR(20),  -- active, passive, on_hold
    tags TEXT[],
    sms_opt_in BOOLEAN DEFAULT false,

    -- GHL Sync
    last_synced_at TIMESTAMP,

    -- Metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    INDEX idx_buyer_status (buyer_status),
    INDEX idx_budget_range (min_budget, max_budget)
);
```

#### **C. Property Matches Table**
```sql
CREATE TABLE property_matches (
    id SERIAL PRIMARY KEY,
    property_id INTEGER REFERENCES properties(id),
    buyer_id INTEGER REFERENCES buyers(id),

    -- Match Details
    match_score INTEGER,  -- 0-100
    match_reasons TEXT[],

    -- Actions Taken
    sms_sent BOOLEAN DEFAULT false,
    sms_sent_at TIMESTAMP,
    workflow_triggered BOOLEAN DEFAULT false,
    workflow_triggered_at TIMESTAMP,
    task_created BOOLEAN DEFAULT false,
    task_id VARCHAR(100),

    -- Metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    UNIQUE(property_id, buyer_id),
    INDEX idx_match_score (match_score DESC),
    INDEX idx_property_id (property_id),
    INDEX idx_buyer_id (buyer_id)
);
```

#### **D. Sync Log Table**
```sql
CREATE TABLE sync_logs (
    id SERIAL PRIMARY KEY,
    sync_type VARCHAR(50),  -- ghl_export, ghl_import, mls_import, etc.
    status VARCHAR(20),     -- success, failed, partial
    records_processed INTEGER,
    records_succeeded INTEGER,
    records_failed INTEGER,
    error_message TEXT,
    execution_time_seconds INTEGER,
    started_at TIMESTAMP,
    completed_at TIMESTAMP,

    INDEX idx_sync_type (sync_type),
    INDEX idx_status (status),
    INDEX idx_started_at (started_at DESC)
);
```

### 5.4 GoHighLevel API Integration

#### **Authentication**
```python
import requests

class GoHighLevelConnector:
    def __init__(self, api_key, location_id):
        self.api_key = api_key
        self.location_id = location_id
        self.base_url = "https://rest.gohighlevel.com/v1"
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        self.rate_limiter = GHLRateLimiter(max_requests=95, time_window=60)

    def _request(self, method, endpoint, **kwargs):
        """Wrapper for all API requests with rate limiting and error handling"""
        self.rate_limiter.wait_if_needed()

        url = f"{self.base_url}/{endpoint}"

        try:
            response = requests.request(method, url, headers=self.headers, **kwargs)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as e:
            if response.status_code == 429:  # Rate limit exceeded
                retry_after = int(response.headers.get('Retry-After', 60))
                time.sleep(retry_after)
                return self._request(method, endpoint, **kwargs)  # Retry
            else:
                raise GHLAPIError(f"API request failed: {e}")
```

#### **Key GHL Endpoints**

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/contacts/` | GET | Search/list contacts (buyers) |
| `/contacts/` | POST | Create new contact |
| `/contacts/{id}` | PUT | Update contact |
| `/contacts/{id}/tags` | POST | Add tags to contact |
| `/opportunities/` | POST | Create opportunity |
| `/opportunities/{id}` | PUT | Update opportunity |
| `/opportunities/pipelines` | GET | Get pipeline stages |
| `/tasks/` | POST | Create task |
| `/workflows/{id}/subscribe` | POST | Add contact to workflow |
| `/conversations/messages` | POST | Send SMS |
| `/custom-fields/` | GET | Get custom field definitions |

#### **GHL Custom Fields Setup**

**Contact Custom Fields (must be created in GHL first):**
```json
{
  "customFields": [
    {
      "key": "budget_min",
      "name": "Minimum Budget",
      "dataType": "NUMERICAL",
      "fieldType": "LARGE_TEXT"
    },
    {
      "key": "budget_max",
      "name": "Maximum Budget",
      "dataType": "NUMERICAL",
      "fieldType": "LARGE_TEXT"
    },
    {
      "key": "location_preference",
      "name": "Preferred Location",
      "dataType": "TEXT",
      "fieldType": "LARGE_TEXT"
    },
    {
      "key": "property_type_preference",
      "name": "Property Type",
      "dataType": "TEXT",
      "fieldType": "DROPDOWN",
      "options": ["Single Family", "Multi Family", "Condo", "Townhouse", "Any"]
    },
    {
      "key": "min_bedrooms",
      "name": "Minimum Bedrooms",
      "dataType": "NUMERICAL",
      "fieldType": "DROPDOWN",
      "options": ["1", "2", "3", "4", "5+"]
    },
    {
      "key": "buyer_status",
      "name": "Buyer Status",
      "dataType": "TEXT",
      "fieldType": "DROPDOWN",
      "options": ["Active", "Passive", "On Hold"]
    }
  ]
}
```

**Opportunity Custom Fields:**
```json
{
  "customFields": [
    {
      "key": "property_address",
      "name": "Property Address",
      "dataType": "TEXT",
      "fieldType": "LARGE_TEXT"
    },
    {
      "key": "deal_score",
      "name": "Opportunity Score",
      "dataType": "NUMERICAL",
      "fieldType": "TEXT"
    },
    {
      "key": "list_price",
      "name": "List Price",
      "dataType": "MONETARY",
      "fieldType": "TEXT"
    },
    {
      "key": "est_profit",
      "name": "Estimated Profit",
      "dataType": "MONETARY",
      "fieldType": "TEXT"
    },
    {
      "key": "mls_id",
      "name": "MLS Number",
      "dataType": "TEXT",
      "fieldType": "TEXT"
    },
    {
      "key": "price_per_sqft",
      "name": "Price Per SqFt",
      "dataType": "MONETARY",
      "fieldType": "TEXT"
    },
    {
      "key": "below_market_pct",
      "name": "Below Market %",
      "dataType": "NUMERICAL",
      "fieldType": "TEXT"
    },
    {
      "key": "days_on_market",
      "name": "Days on Market",
      "dataType": "NUMERICAL",
      "fieldType": "TEXT"
    },
    {
      "key": "deal_quality",
      "name": "Deal Quality",
      "dataType": "TEXT",
      "fieldType": "DROPDOWN",
      "options": ["HOT DEAL", "GOOD OPPORTUNITY", "FAIR DEAL", "PASS"]
    },
    {
      "key": "estimated_arv",
      "name": "Estimated ARV",
      "dataType": "MONETARY",
      "fieldType": "TEXT"
    }
  ]
}
```

### 5.5 Scoring Algorithm

#### **Opportunity Score Calculation (0-100 scale)**

```python
def calculate_opportunity_score(property_data, market_data, config):
    """
    Calculate opportunity score based on multiple factors

    Returns: (score, breakdown_dict)
    """

    weights = config['scoring_weights']

    # Factor 1: Price Advantage (30 points)
    price_per_sqft = property_data['list_price'] / property_data['square_feet']
    market_avg_price_per_sqft = market_data['avg_price_per_sqft']
    price_advantage_pct = ((market_avg_price_per_sqft - price_per_sqft) / market_avg_price_per_sqft) * 100

    if price_advantage_pct >= 20:
        price_score = 30
    elif price_advantage_pct >= 15:
        price_score = 25
    elif price_advantage_pct >= 10:
        price_score = 20
    elif price_advantage_pct >= 5:
        price_score = 10
    else:
        price_score = 0

    # Factor 2: Days on Market (20 points)
    dom = property_data['days_on_market']
    if dom >= 90:
        dom_score = 20
    elif dom >= 60:
        dom_score = 15
    elif dom >= 30:
        dom_score = 10
    else:
        dom_score = 5

    # Factor 3: Financial Returns (25 points)
    # Cap rate calculation (for investment properties)
    if property_data.get('estimated_rental_income'):
        annual_rental_income = property_data['estimated_rental_income'] * 12
        annual_expenses = property_data['annual_taxes'] + (property_data.get('hoa_fee', 0) * 12)
        noi = annual_rental_income - annual_expenses
        cap_rate = (noi / property_data['list_price']) * 100

        if cap_rate >= 10:
            financial_score = 25
        elif cap_rate >= 8:
            financial_score = 20
        elif cap_rate >= 6:
            financial_score = 15
        else:
            financial_score = 10
    else:
        # For flip properties, use ARV-based calculation
        estimated_arv = property_data.get('estimated_arv', property_data['list_price'] * 1.15)
        estimated_rehab_cost = property_data.get('estimated_rehab', property_data['list_price'] * 0.1)
        potential_profit = estimated_arv - property_data['list_price'] - estimated_rehab_cost
        profit_percentage = (potential_profit / property_data['list_price']) * 100

        if profit_percentage >= 25:
            financial_score = 25
        elif profit_percentage >= 20:
            financial_score = 20
        elif profit_percentage >= 15:
            financial_score = 15
        else:
            financial_score = 10

    # Factor 4: Condition/Price Indicators (15 points)
    condition_score = 0

    # Price reductions indicate motivated seller
    if property_data.get('price_reduction_amount', 0) >= 20000:
        condition_score += 5
    elif property_data.get('price_reduction_amount', 0) >= 10000:
        condition_score += 3

    # Distressed keywords in description
    distressed_keywords = config['undervalued_criteria']['distressed_keywords']
    description = property_data.get('description', '').lower()
    keywords_found = [kw for kw in distressed_keywords if kw in description]

    if len(keywords_found) >= 3:
        condition_score += 10
    elif len(keywords_found) >= 1:
        condition_score += 5

    # Factor 5: Location Quality (10 points)
    location_score = 0

    # School ratings, crime rates, appreciation trends
    # (Would integrate with external APIs like Zillow, Census data)
    if property_data.get('school_rating', 0) >= 8:
        location_score += 5

    if property_data.get('crime_rate_percentile', 50) <= 30:  # Lower crime
        location_score += 5

    # Calculate total weighted score
    total_score = (
        (price_score / 30) * weights['price_advantage'] +
        (dom_score / 20) * weights['days_on_market'] +
        (financial_score / 25) * weights['financial_returns'] +
        (condition_score / 15) * weights['condition_price'] +
        (location_score / 10) * weights['location_quality']
    )

    # Round to integer
    total_score = int(round(total_score))

    # Determine deal quality
    if total_score >= 90:
        deal_quality = "HOT DEAL"
    elif total_score >= 75:
        deal_quality = "GOOD OPPORTUNITY"
    elif total_score >= 60:
        deal_quality = "FAIR DEAL"
    else:
        deal_quality = "PASS"

    breakdown = {
        "price_score": price_score,
        "price_advantage_pct": round(price_advantage_pct, 2),
        "dom_score": dom_score,
        "financial_score": financial_score,
        "condition_score": condition_score,
        "location_score": location_score,
        "deal_quality": deal_quality,
        "total_score": total_score
    }

    return total_score, deal_quality, breakdown
```

---

## 6. FUNCTIONAL REQUIREMENTS

### 6.1 Property Scraping Module

**Module:** `modules/scraper.py`

**Requirements:**
- FR-001: System shall scrape properties from Realtor.com using HomeHarvest library
- FR-002: System shall support multiple simultaneous searches (different ZIP codes)
- FR-003: System shall extract: address, price, bedrooms, bathrooms, sqft, DOM, photos, description
- FR-004: System shall handle pagination (up to 500 results per search)
- FR-005: System shall implement retry logic (3 attempts) for failed requests
- FR-006: System shall respect rate limits (max 1 request per second)
- FR-007: System shall log all scraping activities
- FR-008: System shall detect and handle CAPTCHA/blocking scenarios

### 6.2 Database Integration Module

**Module:** `modules/database.py`

**Requirements:**
- FR-009: System shall support PostgreSQL, MySQL, SQL Server, SQLite
- FR-010: System shall use connection pooling (max 5 connections)
- FR-011: System shall implement automatic retry for transient errors
- FR-012: System shall support MLS database connections via ODBC/JDBC
- FR-013: System shall execute field mapping from config files
- FR-014: System shall detect and merge duplicate properties
- FR-015: System shall track price changes over time
- FR-016: System shall backup database daily to specified path

### 6.3 Analysis Engine Module

**Module:** `modules/analyzer.py` and `modules/scorer.py`

**Requirements:**
- FR-017: System shall calculate opportunity score (0-100) for each property
- FR-018: System shall compare property price to market average
- FR-019: System shall detect price reductions
- FR-020: System shall calculate cap rate for rental properties
- FR-021: System shall estimate ARV (After Repair Value) for flips
- FR-022: System shall identify distressed property keywords
- FR-023: System shall classify deals as: HOT DEAL, GOOD, FAIR, PASS
- FR-024: System shall provide score breakdown with explanation

### 6.4 GoHighLevel Integration Module

**Module:** `integrations/ghl_connector.py`

**Requirements:**
- FR-025: System shall authenticate with GHL API using Bearer token
- FR-026: System shall create opportunities for properties scoring >75
- FR-027: System shall populate all opportunity custom fields
- FR-028: System shall assign opportunities to users based on territory
- FR-029: System shall import contacts with "active_buyer" tag
- FR-030: System shall calculate buyer match score (0-100)
- FR-031: System shall trigger workflows based on score thresholds
- FR-032: System shall send SMS via GHL API
- FR-033: System shall create tasks and assign to users
- FR-034: System shall add tags to contacts for tracking
- FR-035: System shall add notes to opportunities with analysis details
- FR-036: System shall update opportunity pipeline stages
- FR-037: System shall implement rate limiting (95 requests/minute)
- FR-038: System shall retry failed API calls (3 attempts with exponential backoff)
- FR-039: System shall log all GHL API interactions
- FR-040: System shall validate GHL setup (pipelines, stages, custom fields exist)

### 6.5 Buyer Matching Module

**Module:** `integrations/ghl_buyer_matcher.py`

**Requirements:**
- FR-041: System shall fetch buyers from GHL with "active_buyer" tag
- FR-042: System shall cache buyer data in Redis (1 hour TTL)
- FR-043: System shall match properties based on: budget, location, property type, bedrooms
- FR-044: System shall assign weighted match score (budget 40%, location 30%, type 20%, bedrooms 10%)
- FR-045: System shall only act on matches scoring >70
- FR-046: System shall limit SMS to 3 per day per contact
- FR-047: System shall respect SMS opt-in status
- FR-048: System shall respect quiet hours (9 PM - 8 AM)
- FR-049: System shall tag contacts with "matched_[property_id]"
- FR-050: System shall log all matches in database

### 6.6 Notification Module

**Module:** `modules/notifier.py` and `modules/reporter.py`

**Requirements:**
- FR-051: System shall send daily email report at configured time
- FR-052: System shall send SMS via GHL for properties scoring >90
- FR-053: System shall include top 10 properties in email report
- FR-054: System shall render HTML email templates
- FR-055: System shall include property photos in email
- FR-056: System shall send Slack webhook notifications (optional)
- FR-057: System shall send error alert emails for critical failures
- FR-058: System shall generate weekly market analysis report
- FR-059: System shall export reports to Excel format

### 6.7 Scheduling & Orchestration

**Module:** `main.py`

**Requirements:**
- FR-060: System shall run automated daily workflow at configured time
- FR-061: System shall execute tasks in correct order: scrape → analyze → sync → notify
- FR-062: System shall support manual execution with command-line flags
- FR-063: System shall log execution time for each module
- FR-064: System shall continue execution if non-critical module fails
- FR-065: System shall send summary email after each run
- FR-066: System shall support "test mode" without GHL sync

---

## 7. NON-FUNCTIONAL REQUIREMENTS

### 7.1 Performance
- NFR-001: Full workflow execution shall complete within 90 minutes
- NFR-002: Single property analysis shall complete within 2 seconds
- NFR-003: GHL API requests shall complete within 5 seconds (with retries)
- NFR-004: Database queries shall use indexes for optimal performance
- NFR-005: System shall support analysis of 1000+ properties per run

### 7.2 Reliability
- NFR-006: System shall have 99% uptime for scheduled runs
- NFR-007: System shall retry failed operations 3 times before alerting
- NFR-008: System shall log all errors with stack traces
- NFR-009: System shall gracefully handle API rate limits
- NFR-010: System shall not lose data during crashes (transaction safety)

### 7.3 Security
- NFR-011: API keys shall be stored in environment variables, never code
- NFR-012: Database passwords shall be encrypted at rest
- NFR-013: System shall use HTTPS for all API communications
- NFR-014: System shall validate all user inputs to prevent injection
- NFR-015: System shall implement role-based access control (future)

### 7.4 Scalability
- NFR-016: System shall support monitoring 50+ ZIP codes simultaneously
- NFR-017: System shall handle 10,000+ properties in database
- NFR-018: System shall support multiple concurrent users (future)
- NFR-019: Database shall support horizontal scaling (replicas)

### 7.5 Maintainability
- NFR-020: Code shall follow PEP 8 style guidelines
- NFR-021: All modules shall have docstrings and type hints
- NFR-022: Configuration shall be externalized (config.json, .env)
- NFR-023: System shall have unit tests for all critical functions
- NFR-024: System shall have integration tests for GHL API

### 7.6 Usability
- NFR-025: Installation shall be possible with single setup script
- NFR-026: Configuration shall be possible without code changes
- NFR-027: Error messages shall be clear and actionable
- NFR-028: Reports shall be visually appealing and easy to read
- NFR-029: System shall provide setup validation before first run

### 7.7 Compliance
- NFR-030: System shall comply with TCPA (SMS opt-in requirements)
- NFR-031: System shall honor SMS opt-out requests immediately
- NFR-032: System shall provide data export/deletion capabilities (GDPR/CCPA)
- NFR-033: System shall log all SMS communications for audit

---

## 8. WORKFLOW AUTOMATION

### 8.1 Daily Automated Workflow

**Schedule:** Daily at 5:30 AM

```
5:30 AM  → START: Initialize system
5:31 AM  → Import from MLS database (if configured)
5:45 AM  → Scrape new listings from Realtor.com (HomeHarvest)
6:00 AM  → Merge data sources and deduplicate
6:05 AM  → Detect price reductions since yesterday
6:10 AM  → Fetch market data for comparison
6:15 AM  → Run analysis engine on all new/updated properties
6:30 AM  → Calculate opportunity scores
6:35 AM  → Classify deals (HOT DEAL, GOOD, FAIR, PASS)
6:40 AM  → Filter properties scoring >75

6:45 AM  → GHL BUYER IMPORT
           ├─ Fetch all contacts with "active_buyer" tag
           ├─ Update buyers table in database
           └─ Cache in Redis (1 hour TTL)

6:50 AM  → PROPERTY-BUYER MATCHING
           ├─ For each property scoring >75:
           │   ├─ Calculate match scores for all buyers
           │   ├─ Filter matches with score >70
           │   └─ Save to property_matches table
           └─ Log match statistics

7:00 AM  → GHL OPPORTUNITY CREATION
           ├─ For each property scoring >75:
           │   ├─ Create opportunity in GHL
           │   ├─ Set pipeline stage to "New Lead"
           │   ├─ Populate custom fields
           │   ├─ Assign to user based on territory
           │   ├─ Add tags ("automated", "dealfinder")
           │   └─ Add note with analysis details
           └─ Log: X opportunities created

7:05 AM  → HOT DEAL WORKFLOWS (Score >90)
           ├─ For each HOT DEAL:
           │   ├─ Trigger "Hot Deal Alert" GHL workflow
           │   ├─ Send SMS to broker via GHL
           │   ├─ Move opportunity to "Priority Review" stage
           │   ├─ Create task "Review Hot Deal" (due 4 hours)
           │   └─ Send Slack webhook notification
           └─ Log: X hot deals processed

7:10 AM  → BUYER NOTIFICATION
           ├─ For each property match (score >70):
           │   ├─ Check: SMS opt-in = true
           │   ├─ Check: SMS count today < 3
           │   ├─ Check: Not in quiet hours
           │   ├─ Send SMS to buyer via GHL
           │   ├─ Trigger "Property Match" workflow
           │   ├─ Add tag "matched_[property_id]"
           │   ├─ Create task "Follow up with [buyer]" (due 8 hours)
           │   └─ Add note with match details
           └─ Log: X buyers notified

7:15 AM  → TASK CREATION
           ├─ For each property scoring >85:
           │   ├─ Task 1: "Review Hot Deal" (assigned to broker, due 4h)
           │   ├─ Task 2: "Schedule Showing" (assigned to coordinator, due 24h)
           │   └─ Task 3: "Contact X Buyers" (assigned to broker, due 8h)
           └─ Log: X tasks created

7:20 AM  → EMAIL REPORT GENERATION
           ├─ Generate HTML email with Jinja2 template
           ├─ Include top 10 properties (sorted by score)
           ├─ Include property photos
           ├─ Include price reductions
           ├─ Include GHL sync summary
           ├─ Include market statistics
           └─ Send email via SMTP

7:25 AM  → DATABASE MAINTENANCE
           ├─ Update property sync status
           ├─ Archive old properties (>365 days)
           ├─ Vacuum database
           └─ Generate backup

7:30 AM  → REPORTING & LOGGING
           ├─ Generate execution summary
           ├─ Log to sync_logs table
           ├─ Calculate performance metrics
           └─ Send completion email

7:35 AM  → END: Cleanup and exit
```

### 8.2 Hourly Quick Sync

**Schedule:** Every hour (on the hour)

```
XX:00  → Quick sync with MLS database
XX:05  → Check for new GHL contacts (buyers)
XX:10  → Update opportunity stages based on activities
XX:15  → Send any pending SMS (from queue)
XX:20  → Check for workflow trigger failures and retry
XX:25  → Update Redis cache
XX:30  → Complete
```

### 8.3 Weekly Market Analysis

**Schedule:** Sunday at 8:00 AM

```
8:00 AM  → Generate market trends report
8:15 AM  → Calculate scoring algorithm performance
8:30 AM  → ROI tracking (deals closed vs. found)
8:45 AM  → Send weekly summary email
9:00 AM  → Complete
```

---

## 9. ERROR HANDLING & EDGE CASES

### 9.1 GHL API Errors

| Error | Handling Strategy |
|-------|-------------------|
| **401 Unauthorized** | Alert admin immediately, stop execution |
| **429 Rate Limit** | Wait for Retry-After header, then retry |
| **404 Not Found** | Log error, skip record, continue processing |
| **500 Server Error** | Retry 3 times with exponential backoff, then alert |
| **Network Timeout** | Retry 3 times, then log and continue |
| **Invalid Field** | Log field name, skip field update, continue |

### 9.2 Scraping Errors

| Error | Handling Strategy |
|-------|-------------------|
| **CAPTCHA Detected** | Stop scraping, send alert, require manual intervention |
| **IP Blocked** | Rotate user agent, add delay, retry; if fails, use proxy |
| **No Results Found** | Log warning (may be normal), continue workflow |
| **Malformed HTML** | Log error, skip property, continue |
| **Timeout** | Retry 3 times with increasing timeout, then skip |

### 9.3 Database Errors

| Error | Handling Strategy |
|-------|-------------------|
| **Connection Failed** | Retry 5 times, then alert and stop |
| **Duplicate Key** | Update existing record instead of insert |
| **Constraint Violation** | Log error with details, skip record |
| **Transaction Deadlock** | Rollback, wait 1 second, retry |
| **Disk Full** | Alert admin, stop execution immediately |

### 9.4 Data Quality Issues

| Issue | Handling Strategy |
|-------|-------------------|
| **Missing Required Field** | Log warning, use default value or skip property |
| **Invalid Price** | Flag for manual review, exclude from analysis |
| **Invalid Address** | Attempt geocoding, if fails, flag for review |
| **Extreme Outlier** | Flag for manual review (e.g., $1 price) |
| **Duplicate Property** | Merge data, keep most recent, log conflict |

---

## 10. DEPLOYMENT & INSTALLATION

### 10.1 System Requirements

**Hardware:**
- CPU: 2+ cores recommended
- RAM: 4GB minimum, 8GB recommended
- Disk: 20GB minimum (for database and logs)
- Network: Stable internet connection

**Software:**
- Python 3.10 or higher
- PostgreSQL 12+ (or MySQL/SQL Server)
- Redis 6.0+ (optional, for caching)
- pip (Python package manager)
- git (for cloning repository)

**Operating Systems:**
- Ubuntu 20.04+ (recommended)
- macOS 11+ (Big Sur or later)
- Windows 10/11 (with WSL2 recommended)

### 10.2 Installation Steps

```bash
# 1. Clone repository
git clone https://github.com/yourusername/dealfinder-pro.git
cd dealfinder-pro

# 2. Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set up PostgreSQL database
sudo -u postgres createdb dealfinder
sudo -u postgres psql dealfinder < database/schema.sql

# 5. Copy environment template
cp .env.example .env

# 6. Configure environment variables
nano .env  # Edit with your API keys and settings

# 7. Validate GHL setup
python main.py --validate-ghl-setup

# 8. Run test scrape
python main.py --test-scrape --zip-code "90210"

# 9. Test GHL connection
python main.py --test-ghl

# 10. Run full workflow (test mode, no GHL sync)
python main.py --test-mode

# 11. Schedule daily runs (using cron)
crontab -e
# Add: 30 5 * * * /path/to/venv/bin/python /path/to/main.py --full-workflow
```

### 10.3 Configuration Checklist

**Before first run, complete:**

- [ ] PostgreSQL database created and schema applied
- [ ] `.env` file created with all API keys
- [ ] GHL API key obtained (Settings → API → Create API Key)
- [ ] GHL Location ID identified
- [ ] GHL Pipeline created (e.g., "Investment Properties")
- [ ] GHL Pipeline stages created (New Lead, Contacted, Showing, etc.)
- [ ] GHL Contact custom fields created (budget_min, budget_max, etc.)
- [ ] GHL Opportunity custom fields created (deal_score, property_address, etc.)
- [ ] GHL Workflows created and IDs configured
- [ ] Email SMTP settings configured
- [ ] Target ZIP codes added to config.json
- [ ] Scoring weights customized (if needed)
- [ ] Test run completed successfully
- [ ] GHL setup validation passed

---

## 11. TESTING STRATEGY

### 11.1 Unit Tests

**Files:** `tests/test_*.py`

**Coverage Requirements:**
- Scoring algorithm: 100% code coverage
- GHL connector: 90% code coverage
- Database operations: 90% code coverage
- Buyer matching: 95% code coverage

**Key Test Cases:**
```python
# tests/test_scorer.py
def test_score_calculation_hot_deal():
    """Property with 20% below market + 90 DOM = 90+ score"""

def test_score_calculation_fair_deal():
    """Property with 5% below market + 20 DOM = 60-75 score"""

# tests/test_ghl_connector.py
def test_create_opportunity_success():
    """Verify opportunity creation with all fields"""

def test_rate_limiting():
    """Verify rate limiter prevents >100 req/min"""

def test_retry_on_500_error():
    """Verify 3 retries on server error"""

# tests/test_buyer_matcher.py
def test_perfect_budget_match():
    """Property $400K, buyer $350K-$450K = 40 points"""

def test_location_match():
    """Property in Beverly Hills, buyer prefers Beverly Hills = 30 points"""
```

### 11.2 Integration Tests

**Requirements:**
- GHL test account required
- Separate test database
- Mock data for properties and buyers

**Test Scenarios:**
1. End-to-end workflow: Scrape → Analyze → GHL Sync → Notify
2. GHL opportunity creation with all custom fields
3. Buyer matching and SMS sending
4. Workflow trigger verification
5. Database rollback on GHL API failure

### 11.3 Performance Tests

**Benchmarks:**
- Analyze 1000 properties in <5 minutes
- GHL opportunity creation: <2 seconds per property
- Buyer matching for 100 buyers: <10 seconds per property
- Database query response: <100ms for property search

---

## 12. MONITORING & MAINTENANCE

### 12.1 Key Metrics to Track

**Daily:**
- Properties scraped
- Properties analyzed
- Opportunities created in GHL
- Buyers matched
- SMS sent
- Workflows triggered
- Tasks created
- Errors encountered
- Execution time per module
- GHL API rate limit usage

**Weekly:**
- Hot deals found (score >90)
- Conversion rate (opportunities → closed deals)
- Scoring algorithm accuracy
- Average match score
- System uptime percentage

### 12.2 Alerting Rules

**Critical Alerts (page immediately):**
- Workflow execution failure (no recovery)
- GHL API authentication failure
- Database connection lost
- Zero properties found for 3 consecutive days

**Warning Alerts (email):**
- Scraping CAPTCHA detected
- GHL rate limit exceeded (>90 req/min)
- Execution time >120 minutes
- Low match rate (<10% of properties matched)

### 12.3 Maintenance Tasks

**Daily:**
- Review error logs
- Verify GHL sync status
- Check execution summary email

**Weekly:**
- Review scoring algorithm performance
- Analyze buyer match accuracy
- Check database disk usage
- Review weekly market analysis report

**Monthly:**
- Update HomeHarvest library
- Rotate API keys (security best practice)
- Backup database offsite
- Review and tune scoring weights
- Clean up archived data (>1 year old)

---

## 13. FUTURE ENHANCEMENTS (Phase 2+)

### 13.1 Machine Learning Enhancements
- **Predictive Scoring:** Use ML to predict property appreciation
- **Smart Weights:** Automatically tune scoring weights based on closed deals
- **Image Analysis:** Analyze property photos to assess condition
- **NLP for Descriptions:** Extract insights from listing descriptions

### 13.2 Advanced Features
- **Mobile App:** iOS/Android app for brokers
- **Voice Alerts:** Twilio voice calls for ultra-hot deals
- **Comparative Market Analysis:** Automated CMA generation
- **Predictive Analytics:** Forecast market trends
- **Multi-User Support:** Team access with role-based permissions
- **White Label:** Resell to other brokerages

### 13.3 Integration Expansions
- **Zillow/Realtor APIs:** Direct API integration (paid)
- **PropStream/BatchLeads:** Integrate skip tracing data
- **Zapier Integration:** Connect to 3000+ apps
- **CRM Expansion:** Salesforce, HubSpot connectors
- **Accounting Integration:** QuickBooks, Xero

### 13.4 Automation Improvements
- **AI Chatbot:** Answer buyer questions about properties
- **Auto-Scheduling:** Schedule showings via Calendly integration
- **Offer Generation:** Auto-generate purchase agreements
- **Document Signing:** DocuSign integration

---

## 14. SUCCESS CRITERIA

### 14.1 Launch Metrics (First 30 Days)

**Technical:**
- [ ] 99% uptime for scheduled runs
- [ ] <5% error rate across all modules
- [ ] Average execution time <90 minutes
- [ ] GHL sync success rate >95%

**Business:**
- [ ] 100+ properties analyzed
- [ ] 10+ hot deals identified (score >90)
- [ ] 50+ GHL opportunities created
- [ ] 100+ buyer matches
- [ ] 1 deal closed from system

### 14.2 Success Indicators (First 90 Days)

**ROI:**
- [ ] 3-5 additional deals closed
- [ ] $15K-$50K in additional commission
- [ ] 20+ hours/week time savings
- [ ] System pays for itself 10x

**User Satisfaction:**
- [ ] Broker actively checks daily reports
- [ ] Buyers respond positively to matches (>30% engagement)
- [ ] System alerts lead to immediate action
- [ ] Broker recommends system to colleagues

---

## 15. GLOSSARY

| Term | Definition |
|------|------------|
| **GHL** | GoHighLevel - CRM platform for agencies and brokers |
| **Opportunity** | Sales opportunity/lead in GHL CRM |
| **Pipeline** | Sales workflow stages in GHL (e.g., New Lead → Closed Won) |
| **Workflow** | Automated sequence in GHL triggered by events |
| **MLS** | Multiple Listing Service - industry database of properties |
| **DOM** | Days on Market - how long property has been listed |
| **ARV** | After Repair Value - estimated value after renovations |
| **Cap Rate** | Capitalization rate - annual ROI for rental properties |
| **HOT DEAL** | Property scoring 90+ on opportunity scale |
| **HomeHarvest** | Python library for scraping real estate listings |
| **RETS** | Real Estate Transaction Standard - MLS data format |

---

## 16. APPENDIX

### 16.1 Reference Links

**GoHighLevel:**
- API Documentation: https://highlevel.stoplight.io/docs/integrations/
- Developer Community: https://www.facebook.com/groups/gohighlevel
- Support: https://support.gohighlevel.com/

**HomeHarvest:**
- GitHub: https://github.com/Bunsly/HomeHarvest
- Documentation: https://github.com/Bunsly/HomeHarvest/wiki

**Real Estate Data:**
- Realtor.com: https://www.realtor.com/
- Zillow Research: https://www.zillow.com/research/

### 16.2 Contact Information

**Project Lead:** [Your Name]
**Email:** [your.email@example.com]
**Support:** Create issue on GitHub repository

---

**Document End**

*This PRD is a living document and will be updated as requirements evolve.*
