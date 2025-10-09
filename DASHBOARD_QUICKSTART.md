# 🚀 Dashboard Quick Start Guide

## Launch the Dashboard (One Command!)

```bash
./run_dashboard.sh
```

**Or manually:**
```bash
python3 -m streamlit run dashboard/app.py
```

The dashboard will automatically open in your browser at `http://localhost:8501`

---

## 🎯 What You Can Do

### 1. Configure Search Areas (2 minutes)
- Go to **🔧 Configuration** page
- Add ZIP codes (e.g., "90210", "33139", "78701")
- Or click Quick Add buttons for popular cities
- Set price range and property criteria
- Click "Save"

### 2. Find Properties (5 minutes)
- Go to **🔍 Scraper** page
- **Test Scrape:** Enter one ZIP code → Click "Run Test"
- **Full Scrape:** Click "Run Full Scrape" for all areas
- Download results as CSV

### 3. Browse Results
- Go to **📊 Properties** page
- View in table or card mode
- Filter by price, city, bedrooms
- Click "Analyze" on any property

### 4. Test AI Agent
- Go to **🤖 Agent Control** page
- Property auto-loads or enter manually
- Click "Analyze with AI Agent"
- See decision, confidence, and reasoning
- Generate GHL opportunity payload

---

## 📋 Dashboard Pages

| Page | What It Does |
|------|--------------|
| 🏠 **Home** | Dashboard overview and quick actions |
| 🔧 **Configuration** | Manage search areas and criteria |
| 🔍 **Scraper** | Find properties from Realtor.com |
| 📊 **Properties** | Browse and filter results |
| 🤖 **Agent Control** | AI analysis and GHL integration |

---

## 🎨 Features Highlights

### Smart Configuration
- Drag-and-drop ZIP code management
- Price range sliders
- Multi-select property types
- One-click quick-add for popular cities

### Real-Time Scraping
- Live progress updates
- Results counter
- Error handling
- Instant CSV download

### Intelligent Filtering
- Price range slider
- City dropdown
- Minimum bedrooms/bathrooms
- Multiple sort options

### AI-Powered Analysis
- Claude AI evaluation
- Confidence scoring (0-100%)
- Detailed reasoning
- Investment recommendations

### GHL Integration
- Automatic field mapping
- Opportunity payload generation
- JSON download
- Ready for manual creation

---

## 💡 Quick Tips

**Starting Out:**
1. Add 2-3 ZIP codes in Configuration
2. Test scrape one ZIP first
3. If it works, run full scrape
4. Browse and filter results
5. Test AI agent on interesting properties

**Best Practices:**
- Start with 7-14 days back (faster)
- Use specific ZIP codes (better results)
- Download interesting results (save for later)
- Test agent on multiple properties (see patterns)

**Performance:**
- Scraping takes time (rate limits = 2 sec between requests)
- 5 ZIP codes ≈ 5-10 minutes scraping
- Results load instantly once scraped
- Dashboard is fast and responsive

---

## 🔧 Configuration Examples

### Beverly Hills Focus
```
ZIP Codes: 90210, 90211
Price Range: $1M - $5M
Property Types: Single Family, Condo
Min Beds/Baths: 3/2
```

### Miami Beach Investment
```
ZIP Codes: 33139, 33140, 33141
Price Range: $500K - $2M
Property Types: Condo, Townhouse
Min Beds/Baths: 2/2
```

### Austin Starter Homes
```
ZIP Codes: 78701, 78702, 78703
Price Range: $300K - $800K
Property Types: Single Family, Townhouse
Min Beds/Baths: 2/1
```

---

## 🐛 Troubleshooting

### Dashboard won't start
```bash
# Install Streamlit
pip3 install streamlit

# Try manual command
cd "/Users/mikekwak/Real Estate Valuation"
python3 -m streamlit run dashboard/app.py
```

### No properties found
- Check ZIP codes are valid
- Try different days back (30 instead of 7)
- Verify Realtor.com has listings in that area
- Check terminal for error messages

### AI analysis fails
- Verify ANTHROPIC_API_KEY in .env
- Check API key is valid and has credits
- Look at error message for details

### Scraping is slow
- This is normal! Rate limits = 2 seconds between requests
- Start with fewer ZIP codes or days back
- Results are worth the wait!

---

## 🎉 You're Ready!

**Launch command:**
```bash
./run_dashboard.sh
```

**Or:**
```bash
python3 -m streamlit run dashboard/app.py
```

**Then:**
1. Configure your areas
2. Scrape some properties
3. Let the AI agent help you find great deals!

---

**Happy Deal Finding! 🏠💰**
