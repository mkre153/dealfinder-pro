# SDMLS (San Diego MLS) API Setup Guide

This guide will help you obtain API credentials for San Diego MLS (formerly Sandicor) to access official MLS data through the MLS Router API.

**Last Updated:** October 2025
**API Standard:** RESO Web API 2.0 / Data Dictionary 2.0
**Provider:** MLS Router (SDMLS-certified platform)

---

## Overview

San Diego MLS provides API access through **MLS Router**, a RESO Web API 2.0-certified platform that delivers real-time MLS data without replication delays.

**Benefits over web scraping:**
- ✅ Official MLS data (more accurate, more fields)
- ✅ Real-time updates (no lag)
- ✅ No CAPTCHA or rate limit issues
- ✅ Legal and compliant
- ✅ Includes all MLS listings for San Diego County
- ✅ 200+ data fields vs 20-30 from scraping

---

## Prerequisites

**You must have:**
1. An active SDMLS membership OR
2. Work through a broker with SDMLS membership
3. Your broker's approval for API access

**Cost estimate:** $50-100/month (may be included in your membership)

---

## Step-by-Step Setup Instructions

### Step 1: Contact SDMLS Data Access Department

**Option A: Online Request Form**
1. Visit: https://sdmls.com/nmsubscribers/data-access/
2. Click "Request Data Access" or "Apply for API Access"
3. Fill out the vendor application form

**Option B: Direct Contact**
- **Email:** support@sdmls.com
- **Phone:** (858) 795-4000
- **Subject:** "API Access Request for Property Data"

**In your request, mention:**
- You are an SDMLS member (or working through a member broker)
- You want access to **MLS Router API** (not legacy RETS)
- Purpose: Internal property search and analysis tool
- Expected usage: Low volume (monitoring 6 ZIP codes, ~500-1,000 properties)

### Step 2: Choose Access Tier

When SDMLS responds, they will offer access tiers:

**Recommended: Tiered Vendor Access Program**
- Best for small operations (1-2 clients)
- Lower monthly fees (~$25-50/month)
- May not require real-time (daily sync acceptable)
- Perfect for DealFinder Pro use case

**Alternative: Full Vendor Access**
- For larger operations or resellers
- Real-time data access
- Higher fees ($100-200/month + per-request fees)
- Only needed if monitoring 10,000+ properties

**Alternative: Direct Broker Access**
- If you're accessing for your own brokerage only
- May be included in your SDMLS membership
- Check with your broker admin

### Step 3: Sign Data Access Agreement

SDMLS will send you a **Broker Data Access Agreement**:

1. Review the terms (standard MLS data usage agreement)
2. Sign electronically or physically
3. Return to SDMLS

**Key terms to understand:**
- Data is for internal use only (not for public websites without IDX compliance)
- Cannot resell raw MLS data
- Must display listing agent attribution
- Must respect status changes (withdrawn, sold, etc.)

### Step 4: Receive API Credentials

After approval (~5-10 business days), you'll receive:

1. **MLS Router Vendor Dashboard** login
2. **API Bearer Token** (this is your SDMLS_API_TOKEN)
3. **API Documentation URL**
4. **Support contact information**

**Example credentials format:**
```
API Endpoint: https://api.mlsrouter.com
Bearer Token: eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9...
Organization ID: your-org-id
```

### Step 5: Add Credentials to DealFinder Pro

1. Open your `.env` file
2. Find the SDMLS section:
   ```bash
   # SDMLS (SAN DIEGO MLS) API - MLS Router
   SDMLS_API_TOKEN=
   ```

3. Paste your Bearer Token:
   ```bash
   SDMLS_API_TOKEN=eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.your_actual_token_here
   ```

4. Save the file

**IMPORTANT:** Never commit `.env` to version control! It's already in `.gitignore`.

### Step 6: Test the Connection

Run the test script to verify credentials:

```bash
cd "/Users/mikekwak/Real Estate Valuation"
python3 integrations/sdmls_connector.py
```

**Expected output (test mode):**
```
🏠 SDMLS MLS Router API Integration Test

Test 1: Connection Test
--------------------------------------------------
Result: {'success': True, 'test_mode': True, ...}

Test 2: Property Search
--------------------------------------------------
Found 1 properties (mock data)
...
✅ Test Mode Complete!
```

**To test with real credentials:**

Create a test script `test_sdmls_real.py`:

```python
from integrations.sdmls_connector import SDMLSConnector

# Initialize with real credentials (test_mode=False)
connector = SDMLSConnector(test_mode=False)

# Test connection
print("Testing SDMLS connection...")
result = connector.test_connection()
print(f"Connection: {result}")

# Search properties in your target ZIP codes
print("\nSearching properties in target areas...")
properties = connector.search_properties(
    zip_codes=['92126', '92127', '92128', '92129', '92130', '92131'],
    price_min=500000,
    price_max=2000000,
    bedrooms_min=3,
    bathrooms_min=2,
    property_types=['Residential'],
    status='Active',
    limit=10
)

print(f"\nFound {len(properties)} properties")

if properties:
    print("\nFirst property:")
    p = properties[0]
    print(f"  MLS#: {p.get('mls_number')}")
    print(f"  Address: {p.get('street_address')}, {p.get('city')}")
    print(f"  Price: ${p.get('list_price'):,}")
    print(f"  Beds/Baths: {p.get('bedrooms')}/{p.get('bathrooms')}")
    print(f"  Sqft: {p.get('square_feet'):,}")
    print(f"  DOM: {p.get('days_on_market')} days")
```

Run it:
```bash
python3 test_sdmls_real.py
```

If successful, you'll see real San Diego MLS listings!

---

## Troubleshooting

### Error: "SDMLS API token not found"
- Check that SDMLS_API_TOKEN is set in `.env`
- Make sure there's no space before or after the token
- Verify you're running from the correct directory

### Error: "401 Unauthorized"
- Token expired or invalid
- Request new token from MLS Router dashboard
- Check that token is complete (they're usually 500+ characters)

### Error: "403 Forbidden"
- Your account doesn't have permission for requested data
- Contact SDMLS to verify your access tier
- May need to upgrade from limited to full access

### Error: "Connection timeout"
- Check internet connection
- Verify API endpoint URL is correct
- SDMLS servers may be down (rare) - check status page

### No properties returned
- Filters may be too strict
- Try removing filters one by one
- Verify ZIP codes are in San Diego County
- Check that status='Active' has active listings

---

## Cost Breakdown

Based on SDMLS Tiered Vendor Access Program:

**Setup Costs:**
- Application fee: $0 (free)
- Setup fee: $0 - $100 (one-time, if applicable)

**Monthly Costs:**
- Vendor access fee: $25 - $100/month
- Per-request fees: Usually included OR ~$0.001-0.01 per call
- Minimum commitment: Usually none or 3-6 months

**For your use case (6 ZIP codes, ~1,000 properties):**
- Estimated: **$50-75/month total**
- May be **$0 additional** if included in your broker's MLS plan

**Annual cost:** ~$600-900/year vs $0 for scraping

**Value:**
- 200+ data fields vs 20-30 from scraping
- Real-time updates vs daily scraping
- No CAPTCHA blocks or rate limits
- Official, legally compliant data
- Better property photos and agent info
- Historical data and status changes

**ROI:** Worth it if you're serious about property monitoring and want reliable, accurate data.

---

## Alternative: Continue Using HomeHarvest Scraper

If SDMLS API access is too expensive or takes too long:

**You can continue using your current setup:**
- `modules/scraper.py` - HomeHarvest library scrapes Realtor.com
- Cost: $0/month
- Reliability: Good (but fragile)
- Data quality: Acceptable (20-30 fields)

**Hybrid approach (recommended):**
- Use SDMLS API for critical North San Diego monitoring
- Use HomeHarvest for other markets (Las Vegas, etc.)
- Get best of both worlds

---

## Next Steps

1. ✅ Contact SDMLS data access department (today)
2. ⏳ Wait for approval (5-10 business days)
3. ✅ Receive credentials
4. ✅ Add to `.env` file
5. ✅ Test connection
6. ✅ Replace scraper with MLS API in production

---

## Support

**SDMLS Technical Support:**
- Email: support@sdmls.com
- Phone: (858) 795-4000
- Hours: Monday-Friday 8am-5pm PT

**MLS Router Support:**
- Documentation: https://mlsrouter.com/docs
- Email: Check your vendor dashboard for support contact

**DealFinder Pro (Internal):**
- See `integrations/sdmls_connector.py` for code
- See `CLAUDE.md` for architecture documentation
- Test mode: Set `test_mode=True` to test without credentials

---

**Questions?** Update this file as you learn more about SDMLS API access!
