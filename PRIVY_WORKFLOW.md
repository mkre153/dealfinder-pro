# Privy.pro CSV Import Workflow

**Last Updated:** October 14, 2025

Complete guide for importing Privy.pro property data with owner intelligence into DealFinder Pro.

---

## Overview

Privy.pro provides **owner intelligence** not available in standard MLS data:
- 🏚️ **Absentee owners** (mailing address ≠ property address)
- 💼 **LLC/Trust ownership** (investor activity indicators)
- 🔄 **Flip history** (previous ownership tracking)
- ⏰ **Motivated sellers** (long days on market)

This data is imported via CSV exports and enriches your property monitoring with investment signals.

---

## Privy.pro Account Setup

### Sign Up

**Pricing (2025):**
- **Agent Plan:** $37/month ($25/month annual)
  - Requires active MLS ID
  - Best value if you have license

- **Investor Plans:**
  - 1 State: $47/month ($32/month annual)
  - 3 States: $79/month ($53/month annual)
  - National: $149/month ($119/month annual)

**Sign Up:** https://www.privy.pro/pricing/

**Recommendation:** Start with 1-State plan ($47/month) to test data quality before committing annually.

---

## Weekly Workflow (15 minutes)

### Step 1: Search Privy for Properties

**Login:** https://app.privy.pro

**Search Criteria:**

For **Multi-Family Properties:**
```
Property Type: Multi-Family, Duplex, Triplex, Fourplex, Apartment
Location: San Diego County, CA (or specific ZIP codes)
Price Range: $800,000 - $3,000,000
# of Units: 2+
Status: Active
Days on Market: Any
```

For **Single Family Investment Properties:**
```
Property Type: Single Family
Location: Your target ZIP codes (92126-92131, etc.)
Price Range: $500,000 - $2,000,000
Beds/Baths: As needed
Status: Active
Days on Market: Any
```

**Tip:** Use advanced filters to target specific investment criteria.

### Step 2: Export CSV

1. After running search, click "Export" button
2. Download CSV to `/Users/mikekwak/Downloads/`
3. Rename for clarity: `privy-multifamily-2025-10-14.csv`

### Step 3: Import to DealFinder Pro

**Open Terminal:**

```bash
cd "/Users/mikekwak/Real Estate Valuation"

# Import and merge with existing data
python3 modules/privy_importer.py ~/Downloads/privy-multifamily-2025-10-14.csv --merge
```

**What This Does:**
- ✅ Parses 36 Privy CSV columns
- ✅ Detects absentee owners (mailing ≠ property address)
- ✅ Flags LLC/Trust ownership (investor activity)
- ✅ Identifies flip history (previous LLC owners)
- ✅ Marks motivated sellers (60+ days on market)
- ✅ Calculates investment intelligence bonus scores
- ✅ Merges with existing `data/latest_scan.json`
- ✅ Creates backup of previous scan data

**Output:**
```
🏠 Importing Privy CSV: privy-multifamily-2025-10-14.csv

✅ Imported 81 properties from Privy

📊 Investment Intelligence Summary:
   • Absentee Owners: 74
   • Investor-Owned: 48
   • Flip History: 17
   • Motivated Sellers (60+ DOM): 22

✅ Saved to data/latest_scan.json
```

### Step 4: Agent Auto-Processing

DealFinder Pro agents automatically scan the updated data:

**Every 4 Hours:**
1. Agents check `data/latest_scan.json` for new properties
2. Apply investment criteria filters
3. Calculate match scores with **Privy intelligence bonuses:**
   - Absentee owner: **+10 points**
   - LLC/Trust owned: **+5 points**
   - Flip history: **+5 points**
   - Motivated seller: **+5 points**
4. Create GHL opportunities for matches
5. Send notifications (email/SMS if configured)

### Step 5: Review Matches in GoHighLevel

**Check GHL Opportunities:**
1. Login to GoHighLevel
2. Navigate to "Opportunities" pipeline
3. See new properties with investment intelligence notes:
   ```
   Match Score: 87/100

   Match Reasons:
   • 📍 Exact ZIP match: 92128
   • 💰 Price $1,100,000 within budget
   • 🏚️ Absentee owner - easier to motivate
   • 💼 Investor-owned: RINEAR FAMILY REVOCABLE TRUST
   • ⏰ Motivated seller - 65 days on market
   ```

---

## Investment Intelligence Flags

### Absentee Owner Detection

**How It Works:**
```python
if mailing_address != property_address:
    absentee_owner = True
```

**Example:**
```
Property: 17604 Camino Ancho, San Diego 92128
Owner: RINEAR FAMILY REVOCABLE TRUST
Mailing: 6834 CAMINITO SUENO, CARLSBAD, CA 92009

🏚️ ABSENTEE OWNER (+10 pts)
```

**Why Valuable:**
- Owner doesn't live at property = investment property
- Easier to motivate for sale (no emotional attachment)
- Higher probability of accepting offers

### LLC/Trust Ownership

**Detection Keywords:**
- LLC, TRUST, INC, CORP, LP
- VENTURES, PROPERTIES, HOLDINGS, INVESTMENTS

**Example:**
```
Owner: GOG PROPERTIES LLC

💼 INVESTOR-OWNED (+5 pts)
```

**Why Valuable:**
- Professional investors, not emotional sellers
- May be wholesalers (potential buyers for your deals)
- Often have multiple properties (pipeline)

### Flip History

**How It Works:**
```python
if previous_owner contains ["LLC", "TRUST", "INC"]:
    flip_history = True
```

**Example:**
```
Current Owner: GOG PROPERTIES LLC
Previous Owner: SOCAL METRO HOLDINGS LLC

🔄 FLIP HISTORY (+5 pts)
```

**Why Valuable:**
- Recent flip = check comp values carefully
- Possible overpriced renovation
- Track active flippers in market

### Motivated Seller

**Detection:**
```python
if days_on_market >= 60:
    motivated_seller = True
```

**Example:**
```
Days on Market: 127

⏰ MOTIVATED SELLER (+5 pts)
```

**Why Valuable:**
- Long DOM = price reduction likely
- More negotiating leverage
- Seller may accept creative offers

---

## Advanced Usage

### Preview Import (Dry Run)

Test import without modifying data:

```bash
python3 modules/privy_importer.py ~/Downloads/privy-export.csv --dry-run
```

Shows investment intelligence summary without saving.

### Custom Output Path

Save to different location:

```bash
python3 modules/privy_importer.py ~/Downloads/privy-export.csv \
  --merge \
  --output /custom/path/scan.json
```

### Standalone Import (No Merge)

Replace existing data entirely:

```bash
python3 modules/privy_importer.py ~/Downloads/privy-export.csv
```

**Warning:** This overwrites `data/latest_scan.json` without backup merge.

---

## Data Fields Imported

### From Privy CSV (36 columns):

**Property Basics:**
- Street, City, State, Zip
- Price, Sq Ft, Price/Sq Ft
- Beds, Baths, Garages, Levels
- Lot Size, Year Built
- Property Type, Status
- Days on Market (DOM)

**Multi-Family Specific:**
- # of Units
- Basement Sq Ft

**Owner Intelligence (Unique to Privy):**
- Owner 1 & 2 Names (First, Last, Middle, Suffix)
- Owner Business Names
- Mailing Address (key for absentee detection!)
- Previous Owner 1 & 2 (flip detection)

**Additional:**
- Privy CMA URL (link to analysis)

---

## Troubleshooting

### Import Errors

**"File not found"**
```bash
# Check file path
ls -lh ~/Downloads/privy-*.csv

# Use absolute path
python3 modules/privy_importer.py "/Users/mikekwak/Downloads/privy-export.csv"
```

**"No properties imported"**
- CSV may have wrong format
- Check that CSV has header row
- Verify columns match Privy export format

### Missing Investment Flags

**All properties show `absentee_owner: false`:**
- Privy CSV may not include mailing addresses
- Run full property search (not saved search)
- Enable "Owner Info" in export options

**No investor ownership detected:**
- Owner names missing from CSV
- Privy account may not have access to owner data
- Upgrade to higher tier plan if needed

### Backup Recovery

If import goes wrong:

```bash
cd "/Users/mikekwak/Real Estate Valuation/data"

# List backups
ls -lt latest_scan_backup_*.json

# Restore from backup
cp latest_scan_backup_20251014_152901.json latest_scan.json
```

---

## Integration with SDMLS API

**When SDMLS API is approved:**

Privy and SDMLS complement each other:

| Data Type | SDMLS MLS API | Privy.pro |
|-----------|---------------|-----------|
| MLS Fields | 200+ | 36 |
| Owner Info | ❌ | ✅ |
| Mailing Address | ❌ | ✅ |
| Previous Owners | ❌ | ✅ |
| Automation | ✅ API | ⚠️ Manual CSV |
| Cost | $50-100/mo | $37-47/mo |

**Recommended: Keep Both**

1. **SDMLS API:** Automated daily scans, full MLS data
2. **Privy CSV:** Weekly owner intelligence supplement

**Workflow:**
- **Monday:** Import Privy CSV (owner intelligence)
- **Daily:** SDMLS API auto-scans (property updates)
- **Result:** Best of both worlds!

---

## ROI Analysis

**Monthly Cost:** $37-47

**Value Provided:**
- ✅ 91% absentee owner detection (74 out of 81 properties)
- ✅ 59% investor ownership identification (48/81)
- ✅ 21% flip history tracking (17/81)
- ✅ 27% motivated seller alerts (22/81)

**Time Savings:**
- Manual owner research: 10-15 min per property
- 81 properties × 12 min = **16 hours saved**
- **Weekly import: 15 minutes**

**Competitive Advantage:**
- Target absentee owners first (higher conversion)
- Track investor activity (market intelligence)
- Identify flips (avoid overpaying)
- Find motivated sellers (better deals)

---

## Weekly Checklist

**Every Monday (15 minutes):**

- [ ] Login to Privy.pro
- [ ] Run property search (multi-family or target criteria)
- [ ] Export CSV
- [ ] Import to DealFinder Pro: `python3 modules/privy_importer.py ~/Downloads/privy-export.csv --merge`
- [ ] Review investment intelligence summary
- [ ] Check GHL for new opportunities

**Optional - Monthly:**
- [ ] Review Privy account (check billing, usage)
- [ ] Adjust search criteria based on market
- [ ] Archive old CSV exports

---

## Support

**Privy.pro Support:**
- Website: https://www.privy.pro
- Help: Check vendor dashboard for support contact

**DealFinder Pro:**
- Import Script: `modules/privy_importer.py`
- Documentation: This file
- Search Agent: `modules/search_agent.py:261-274` (Privy intelligence scoring)

---

**Questions? Update this file as you learn more workflows!**
