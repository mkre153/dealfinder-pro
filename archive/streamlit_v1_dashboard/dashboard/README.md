# 🏠 DealFinder Pro - Web Dashboard

Professional web dashboard for managing your AI-powered real estate investment platform.

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install streamlit plotly pandas
```

Or use the requirements file:
```bash
pip install -r dashboard/requirements_dashboard.txt
```

### 2. Run Dashboard
```bash
cd "/Users/mikekwak/Real Estate Valuation"
streamlit run dashboard/app.py
```

The dashboard will automatically open in your browser at `http://localhost:8501`

---

## 📋 Features

### 🔧 Configuration Page
- **Manage Search Areas:** Add/remove ZIP codes with one click
- **Set Search Criteria:** Price ranges, bedrooms, bathrooms, property types
- **System Settings:** GHL thresholds, scraping settings
- **Quick Add:** Popular areas (Beverly Hills, Miami, Austin, Seattle)

### 🔍 Scraper Control
- **Test Scrape:** Test single ZIP code before full run
- **Full Workflow:** Scrape all configured locations
- **Real-time Progress:** See scraping progress live
- **Download Results:** Export to CSV immediately

### 📊 Property Browser
- **View All Properties:** Table or card view
- **Filter & Sort:** By price, location, bedrooms, etc.
- **Property Details:** Full information with photos
- **Quick Actions:** Analyze with AI or view listing

### 🤖 Agent Control Center
- **AI Analysis:** Get intelligent property evaluation
- **Decision Making:** See agent reasoning and confidence
- **GHL Integration:** Generate opportunity payloads
- **Test Properties:** Use test data or real properties

---

## 🎯 Usage Guide

### Basic Workflow

1. **Configure Your Areas** (🔧 Configuration)
   - Add ZIP codes or cities you want to monitor
   - Set price range and property criteria
   - Save settings

2. **Scrape Properties** (🔍 Scraper)
   - Test scrape one area first
   - Run full workflow for all areas
   - Download results

3. **Browse Results** (📊 Properties)
   - Filter by price, location, size
   - View property details
   - Select properties for analysis

4. **Analyze with AI** (🤖 Agent Control)
   - Get AI evaluation
   - See confidence scores
   - Generate GHL opportunities

---

## 🛠️ Configuration

### Required Environment Variables

Create `.env` file in project root with:

```bash
# AI Agent
ANTHROPIC_API_KEY=your_claude_api_key

# GHL Integration (optional)
GHL_API_KEY=your_ghl_api_key
GHL_LOCATION_ID=your_location_id
GHL_PIPELINE_ID=your_pipeline_id

# Database (optional)
DB_USER=postgres
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=5432
DB_NAME=dealfinder
```

### Config.json

The dashboard manages `config.json` automatically. You can also edit it manually:

```json
{
  "search_criteria": {
    "target_locations": ["90210", "90211"],
    "price_range": {
      "min": 200000,
      "max": 2000000
    },
    "min_bedrooms": 2,
    "min_bathrooms": 2,
    "days_back": 30
  }
}
```

---

## 📊 Dashboard Components

### Components Directory
- `config_manager.py` - Reads/writes config.json
- `scraper_runner.py` - Runs scraping operations

### Pages Directory
- `1_🔧_Configuration.py` - Configuration interface
- `2_🔍_Scraper.py` - Scraping control
- `3_📊_Properties.py` - Property browser
- `4_🤖_Agent_Control.py` - AI agent testing

---

## 🎨 Features in Detail

### Configuration Page

**Search Areas Management:**
- Add single ZIP code
- Add city name with state
- Remove locations with one click
- Quick-add popular metro areas

**Search Criteria:**
- Price range sliders
- Bedroom/bathroom minimums
- Days back (7, 14, 30, 60, 90)
- Property type multi-select

**System Settings:**
- GHL opportunity thresholds
- Scraping rate limits
- Hot deal alerts

### Scraper Page

**Test Scrape:**
- Enter any ZIP code
- Choose days back
- See results instantly
- Download as CSV

**Full Workflow:**
- Scrapes all configured locations
- Real-time progress bar
- Results by location
- Combined download

### Property Browser

**Table View:**
- Sortable columns
- Price formatting
- Pagination
- Export filtered results

**Card View:**
- Property photos
- Key metrics
- Quick actions
- Direct links to listings

**Filters:**
- Price range slider
- City dropdown
- Minimum bedrooms
- Sort options

### Agent Control

**Property Input:**
- Manual entry form
- JSON import
- Load from browser

**AI Analysis:**
- Claude AI evaluation
- Confidence scoring
- Detailed reasoning
- Investment recommendation

**GHL Integration:**
- Generate opportunity payload
- Field mapping
- Download for manual creation
- Auto-formatting

---

## 💡 Tips & Tricks

### Best Practices

1. **Start Small:** Test scrape one ZIP before running full workflow
2. **Use Filters:** Narrow results to find best deals
3. **Save Often:** Download interesting results
4. **Test Agent:** Try different properties to see AI reasoning

### Performance

- Scraping takes time (rate limits)
- Start with 7-14 days back for testing
- Use specific ZIP codes for better results
- Download results to avoid re-scraping

### Troubleshooting

**Dashboard won't start:**
```bash
# Check if Streamlit is installed
pip install streamlit

# Try running from project root
cd "/Users/mikekwak/Real Estate Valuation"
streamlit run dashboard/app.py
```

**Properties not showing:**
- Run scraper first
- Check scraper page for errors
- Verify ZIP codes in configuration

**AI analysis failing:**
- Check ANTHROPIC_API_KEY in .env
- Ensure API key is valid
- Check error messages in terminal

---

## 🔄 Updates & Maintenance

### Clear Cache
```bash
streamlit cache clear
```

### Update Dependencies
```bash
pip install --upgrade streamlit plotly pandas
```

### Reset Configuration
Delete `config.json` and restart dashboard - it will create a new one with defaults.

---

## 📚 Additional Resources

- **Main Documentation:** See project root README.md
- **Agent System:** See AGENT_SYSTEM_GUIDE.md
- **GHL Setup:** See SETUP_COMPLETE_FINAL.md

---

## 🎉 You're Ready!

Run the dashboard and start finding great deals:
```bash
streamlit run dashboard/app.py
```

**Happy Deal Finding! 🏠💰**
