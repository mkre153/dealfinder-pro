# DealFinder Pro

**Automated Real Estate Investment Deal Discovery & Analysis Platform**

DealFinder Pro is an enterprise-grade automation system that finds undervalued real estate investment opportunities, analyzes them using advanced algorithms, and automatically syncs high-quality deals to your GoHighLevel CRM with intelligent buyer matching.

---

## Features

### Core Capabilities
- **Multi-Source Property Discovery**: Scrapes Realtor.com, integrates with MLS databases
- **Advanced Analysis Engine**: 100-point scoring system evaluating price, market position, financials, and more
- **Intelligent Buyer Matching**: Automatically matches properties to buyer criteria in GoHighLevel
- **Full GHL Integration**: Creates opportunities, triggers workflows, sends SMS alerts
- **Automated Reporting**: Daily Excel and HTML email reports with property analysis
- **Production-Ready**: Database connection pooling, error handling, logging, and monitoring

### Investment Analysis
- Price per sqft vs market comparison
- Days on market and seller motivation indicators
- Cap rate and cash-on-cash return calculations
- ARV (After Repair Value) estimation
- Flip profit potential analysis
- Distressed property detection

---

## Quick Start

### 1. Prerequisites

- **Python 3.9+**
- **PostgreSQL 13+** (or MySQL 8+)
- **GoHighLevel Account** (optional but recommended)
- **Chrome/Firefox** (for web scraping)

### 2. Installation

```bash
# Clone repository
git clone <repository-url>
cd "Real Estate Valuation"

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment template
cp .env.example .env

# Edit .env with your credentials
nano .env  # or use your preferred editor
```

### 3. Database Setup

```bash
# Create PostgreSQL database
createdb dealfinder

# Initialize schema
psql dealfinder < database/schema.sql

# (Optional) Load sample data
psql dealfinder < database/sample_data.sql
```

### 4. Configuration

Edit `config.json` to customize:

- **Target locations** (ZIP codes, cities)
- **Search criteria** (price range, bedrooms, property types)
- **Scoring weights** (customize what matters most)
- **GHL settings** (pipeline IDs, workflow IDs)
- **Notification preferences**

See `config.json` for detailed configuration options.

### 5. Environment Variables

Required variables in `.env`:

```bash
# Database
DB_USER=postgres
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=5432
DB_NAME=dealfinder

# GoHighLevel (if using GHL integration)
GHL_API_KEY=your_api_key
GHL_LOCATION_ID=your_location_id

# Email notifications
EMAIL_USERNAME=your_email@gmail.com
EMAIL_PASSWORD=your_app_password
```

See `.env.example` for all available options.

---

## Usage

### Daily Workflow (Recommended)

Run the complete automated workflow:

```bash
python main.py --full-workflow
```

This will:
1. Scrape properties from configured locations
2. Import from MLS (if configured)
3. Deduplicate and enrich data
4. Analyze and score all properties
5. Store in database
6. Import buyers from GoHighLevel
7. Match properties to buyers
8. Create GHL opportunities for high-scoring deals
9. Generate Excel and HTML reports
10. Send email and SMS notifications

### Testing Commands

```bash
# Test database connection
python main.py --test-db

# Test GoHighLevel connection
python main.py --test-ghl

# Test scraping a single ZIP code
python main.py --test-scrape 90210

# Analyze a single property
python main.py --analyze-property PROP_12345

# Generate reports from existing data
python main.py --generate-report
```

### Scheduling (Production)

**Using cron (Linux/Mac):**

```bash
# Edit crontab
crontab -e

# Add daily execution at 8 AM
0 8 * * * cd /path/to/Real\ Estate\ Valuation && /path/to/venv/bin/python main.py --full-workflow >> logs/cron.log 2>&1
```

**Using Task Scheduler (Windows):**

1. Open Task Scheduler
2. Create Basic Task
3. Set trigger: Daily at 8:00 AM
4. Action: Start Program
   - Program: `C:\path\to\venv\Scripts\python.exe`
   - Arguments: `main.py --full-workflow`
   - Start in: `C:\path\to\Real Estate Valuation`

**Using Python schedule library:**

```python
# Create scheduler.py
import schedule
import time
from main import DealFinderPro

def run_workflow():
    app = DealFinderPro()
    app.run_full_workflow()

schedule.every().day.at("08:00").do(run_workflow)

while True:
    schedule.run_pending()
    time.sleep(60)
```

---

## Architecture

### Module Structure

```
Real Estate Valuation/
├── main.py                          # Main orchestrator
├── config.json                      # Configuration
├── .env                            # Environment variables (not in git)
│
├── modules/                         # Core modules
│   ├── database.py                 # Database manager
│   ├── scraper.py                  # Realtor.com scraper
│   ├── data_enrichment.py          # Data cleaning & enrichment
│   ├── analyzer.py                 # Property analysis
│   ├── scorer.py                   # Opportunity scoring
│   ├── reporter.py                 # Report generation
│   ├── sync_manager.py             # GHL sync manager
│   └── notifier.py                 # Email/SMS notifications
│
├── integrations/                    # External integrations
│   ├── ghl_connector.py            # GoHighLevel API client
│   ├── ghl_workflows.py            # GHL workflow automation
│   ├── ghl_buyer_matcher.py        # Buyer matching engine
│   └── mls_connector.py            # MLS database connector
│
├── database/                        # Database files
│   ├── schema.sql                  # Database schema
│   └── migrations/                 # Schema migrations
│
├── templates/                       # Email templates
│   ├── daily_report.html           # Daily report template
│   └── property_card.html          # Property card template
│
├── tests/                          # Test suite
│   ├── test_integration.py         # Integration tests
│   └── test_units.py              # Unit tests
│
├── logs/                           # Application logs
├── reports/                        # Generated reports
└── backups/                        # Database backups
```

### Data Flow

1. **Acquisition**: Scraper → Raw property data
2. **Enrichment**: Data Enrichment → Cleaned, standardized data
3. **Analysis**: Analyzer + Scorer → Scored opportunities
4. **Storage**: Database Manager → PostgreSQL
5. **Matching**: Buyer Matcher → Property-buyer matches
6. **Sync**: GHL Workflows → Opportunities in GoHighLevel
7. **Reporting**: Report Generator → Excel + HTML reports
8. **Notification**: Notifier → Email + SMS alerts

---

## Configuration Guide

### Search Criteria

```json
"search_criteria": {
  "target_locations": ["90210", "Beverly Hills, CA"],
  "days_back": 30,
  "property_types": ["single_family", "multi_family"],
  "min_bedrooms": 3,
  "price_range": {
    "min": 200000,
    "max": 1000000
  }
}
```

### Scoring Weights

Customize what factors matter most (must total 100):

```json
"scoring_weights": {
  "price_advantage": 30,      # Below market pricing
  "days_on_market": 20,       # Seller motivation
  "financial_returns": 25,    # Cap rate, profit potential
  "condition_price": 15,      # Distressed indicators
  "location_quality": 10      # Area desirability
}
```

### GHL Automation Rules

```json
"automation_rules": {
  "auto_create_opportunity": true,
  "min_score_for_opportunity": 75,
  "hot_deal_threshold": 90,
  "auto_match_buyers": true,
  "auto_send_sms": true
}
```

---

## GoHighLevel Setup

See **[GHL_SETUP_GUIDE.md](GHL_SETUP_GUIDE.md)** for complete setup instructions including:

- API key generation
- Custom field creation
- Pipeline configuration
- Workflow setup
- Buyer profile management

---

## Database Schema

### Main Tables

**properties**: All discovered properties with analysis
- Property details (address, price, size, etc.)
- Analysis results (scores, metrics, recommendations)
- GHL sync status

**buyers**: Imported from GoHighLevel
- Contact information
- Budget and preferences
- Target locations and property types

**property_matches**: Property-buyer matches
- Match scores and reasons
- Notification tracking

**sync_logs**: Synchronization history
- Sync type, status, statistics
- Error tracking

See `database/schema.sql` for complete schema.

---

## Scoring System

DealFinder Pro uses a comprehensive 100-point scoring system:

### Score Components

1. **Price Advantage (30 points max)**
   - Compares price/sqft to market median
   - 20%+ below market = 30 points
   - 15-20% below = 25 points
   - 10-15% below = 20 points

2. **Days on Market (20 points max)**
   - Indicates seller motivation
   - 90+ days = 20 points
   - 60-89 days = 15 points
   - 30-59 days = 10 points

3. **Financial Returns (25 points max)**
   - Cap rate for rental properties
   - Flip profit potential
   - 10%+ cap rate = 25 points

4. **Condition/Price Indicators (15 points max)**
   - Price reductions
   - Distressed keywords
   - Below tax assessment

5. **Location Quality (10 points max)**
   - Area desirability
   - School ratings
   - Appreciation potential

### Deal Quality Classifications

- **90-100**: HOT DEAL (immediate action)
- **75-89**: GOOD OPPORTUNITY (strong potential)
- **60-74**: FAIR DEAL (worth reviewing)
- **0-59**: PASS (doesn't meet criteria)

---

## Reporting

### Daily Email Report

Includes:
- Summary statistics
- Top 10 properties by score
- Recent price reductions
- Market insights by ZIP code
- Workflow execution stats

### Excel Report

Three sheets:
1. **Top Deals**: Top 20 properties with key metrics
2. **All Properties**: Complete dataset with analysis
3. **Market Analysis**: Statistics grouped by ZIP code

Reports are saved to `reports/` directory and optionally attached to email.

---

## Troubleshooting

### Common Issues

**Database connection fails:**
```bash
# Check PostgreSQL is running
pg_isready

# Verify credentials in .env
cat .env | grep DB_

# Test connection
python main.py --test-db
```

**GHL API errors:**
```bash
# Verify API key and location ID
python main.py --test-ghl

# Check API key permissions in GHL settings
```

**Scraping fails:**
```bash
# Test single ZIP code
python main.py --test-scrape 90210

# Update Chrome/Firefox browser
# Check for Realtor.com site changes
```

**No properties found:**
- Adjust search criteria in `config.json`
- Increase `days_back` parameter
- Verify target locations are valid
- Check price range isn't too restrictive

### Logs

Check logs for detailed error information:

```bash
# View today's log
tail -f logs/app_$(date +%Y%m%d).log

# Search for errors
grep ERROR logs/app_*.log

# View last 100 lines
tail -100 logs/app_$(date +%Y%m%d).log
```

---

## Performance Optimization

### For Large Datasets

1. **Increase database connection pool:**
   ```json
   "databases": {
     "primary": {
       "max_connections": 20
     }
   }
   ```

2. **Batch processing:**
   ```json
   "performance": {
     "batch_size_analysis": 100,
     "database_batch_insert": 200
   }
   ```

3. **Concurrent scraping:**
   ```json
   "performance": {
     "max_concurrent_scrapes": 10
   }
   ```

### Reducing API Costs

- Cache market data (24 hour default)
- Limit GHL sync to high-scoring properties only
- Use local market estimates instead of external APIs

---

## Security Best Practices

1. **Never commit .env file**
   ```bash
   # Verify .env is in .gitignore
   git check-ignore .env
   ```

2. **Use environment variables for all secrets**

3. **Restrict database access**
   - Use read-only credentials for MLS
   - Create dedicated user for application

4. **Enable HTTPS for webhooks**

5. **Rotate API keys regularly**

6. **Backup database regularly**
   ```bash
   # Manual backup
   pg_dump dealfinder > backups/backup_$(date +%Y%m%d).sql

   # Automated backups (add to cron)
   0 2 * * * pg_dump dealfinder > /path/to/backups/backup_$(date +\%Y\%m\%d).sql
   ```

---

## Advanced Features

### Custom Scoring Rules

Modify `modules/scorer.py` to implement custom scoring logic:

```python
def _calculate_custom_score(self, property_data: Dict) -> int:
    """Your custom scoring logic"""
    score = 0
    # Your logic here
    return score
```

### Additional Data Sources

Add new scrapers in `modules/`:

```python
class ZillowScraper:
    def scrape_listings(self, location: str):
        # Implementation
        pass
```

Then import in `main.py` and add to workflow.

### Custom Notifications

Extend `modules/notifier.py`:

```python
def send_slack_notification(self, message: str):
    """Send notification to Slack"""
    # Implementation
    pass
```

---

## API Reference

See individual module docstrings for detailed API documentation:

```bash
# View module documentation
python -m pydoc modules.database
python -m pydoc modules.analyzer
python -m pydoc integrations.ghl_connector
```

---

## Testing

Run the test suite:

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=modules --cov=integrations

# Run specific test file
pytest tests/test_integration.py -v
```

---

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## Support

For issues, questions, or feature requests:

1. Check existing documentation
2. Search closed issues
3. Open a new issue with:
   - Detailed description
   - Steps to reproduce
   - Log excerpts
   - Configuration (sanitized)

---

## License

Proprietary - All Rights Reserved

---

## Changelog

### Version 1.0.0 (2024)
- Initial release
- Complete workflow automation
- GoHighLevel integration
- Advanced scoring system
- Buyer matching
- Automated reporting

---

## Roadmap

### Planned Features

- [ ] Mobile app for deal notifications
- [ ] Machine learning price prediction
- [ ] Neighborhood crime data integration
- [ ] School rating integration
- [ ] Walk score integration
- [ ] Multi-market expansion tools
- [ ] Comparative market analysis (CMA) generation
- [ ] Automated property valuation model (AVM)
- [ ] Integration with Zapier/Make
- [ ] REST API for custom integrations

---

**Built with ❤️ for Real Estate Investors**
