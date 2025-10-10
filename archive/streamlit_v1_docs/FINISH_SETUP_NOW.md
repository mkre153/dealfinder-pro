# Finish GHL Setup - Interactive Guide

**Estimated Time**: 30 minutes
**Current Progress**: 60% → 100%

Let's complete the setup so agents can create opportunities in GHL automatically!

---

## 🎯 What We'll Do

1. ✅ Check which custom fields you already have (5 min)
2. ✅ Create missing custom fields (10 min)
3. ✅ Create "Investment Properties" pipeline (10 min)
4. ✅ Get Pipeline & Stage IDs (3 min)
5. ✅ Create database tables (2 min)
6. ✅ Test full integration (5 min)

---

## Step 1: Check Existing Custom Fields (5 min)

You already have **43 custom fields** in your GHL account. Let's see which ones you have.

### Login to GHL
1. Go to: https://app.gohighlevel.com/
2. Login to **"Real Estate Valuation"** account

### Check Custom Fields
1. Click: **Settings** (left sidebar)
2. Click: **Custom Fields**
3. Select: **Opportunities** tab

### Compare with Required Fields

**For Opportunities - We Need:**
- [ ] `deal_score` (Number)
- [ ] `property_address` (Text)
- [ ] `list_price` (Currency)
- [ ] `est_profit` (Currency)
- [ ] `mls_id` (Text)
- [ ] `price_per_sqft` (Number)
- [ ] `below_market_pct` (Number)
- [ ] `days_on_market` (Number)
- [ ] `deal_quality` (Dropdown)
- [ ] `estimated_arv` (Currency)

**Check the box next to each field you already have.**

If you have similar field names (like "Deal Score" instead of "deal_score"), that's fine - we can use those!

---

## Step 2: Create Missing Custom Fields (10 min)

For each field you DON'T have, create it:

### For Opportunities

Still in **Settings → Custom Fields → Opportunities**:

Click **+ Add Custom Field** for each missing field:

#### Example: Create "deal_score"
1. Click **+ Add Custom Field**
2. **Field Label**: `Deal Score`
3. **Field Key**: `deal_score` (auto-generated)
4. **Field Type**: **Number**
5. **Placeholder**: `0-100`
6. Click **Save**

Repeat for all missing fields:

| Field Label | Field Type | Dropdown Options (if applicable) |
|-------------|-----------|----------------------------------|
| Deal Score | Number | - |
| Property Address | Text (Single Line) | - |
| List Price | Currency | - |
| Estimated Profit | Currency | - |
| MLS ID | Text (Single Line) | - |
| Price Per Sqft | Number | - |
| Below Market % | Number | - |
| Days On Market | Number | - |
| Deal Quality | Dropdown | HOT DEAL, GOOD, FAIR, PASS |
| Estimated ARV | Currency | - |

### For Contacts (Buyers)

Switch to **Contacts** tab:

Click **+ Add Custom Field** for each:

| Field Label | Field Type | Dropdown Options (if applicable) |
|-------------|-----------|----------------------------------|
| Budget Min | Currency | - |
| Budget Max | Currency | - |
| Location Preference | Text (Single Line) | - |
| Property Type Preference | Dropdown | Single Family, Multi-Family, Condo, Townhouse |
| Min Bedrooms | Number | - |
| Buyer Status | Dropdown | Active, Passive, On Hold |

**✅ When done, you'll have all required custom fields!**

---

## Step 3: Create "Investment Properties" Pipeline (10 min)

### Navigate to Pipelines
1. Click **Opportunities** (left sidebar)
2. Click **Pipelines** (top tab)

### Create New Pipeline
1. Click **+ Create Pipeline** (top right)
2. **Pipeline Name**: `Investment Properties`
3. Click **Create**

### Add Stages

You'll see your new empty pipeline. Now add stages:

1. Click **+ Add Stage** (or similar button)

Add these stages **in this order**:

1. **New Lead**
   - Stage Name: `New Lead`
   - Click Save

2. **Hot Lead**
   - Stage Name: `Hot Lead`
   - Click Save

3. **Priority Review**
   - Stage Name: `Priority Review`
   - Click Save

4. **Showing Scheduled**
   - Stage Name: `Showing Scheduled`
   - Click Save

5. **Offer Submitted**
   - Stage Name: `Offer Submitted`
   - Click Save

6. **Under Contract**
   - Stage Name: `Under Contract`
   - Click Save

7. **Closed Won**
   - Stage Name: `Closed Won`
   - Click Save

8. **Closed Lost**
   - Stage Name: `Closed Lost`
   - Click Save

**✅ You should now have 8 stages in your pipeline!**

---

## Step 4: Get Pipeline & Stage IDs (3 min)

Now we need to copy the IDs to your `.env` file.

### Get Pipeline ID

1. You should still be viewing your "Investment Properties" pipeline
2. Look at the browser address bar URL
3. It will look like:
   ```
   https://app.gohighlevel.com/location/aCyEjbERq92wlaVNIQuH/opportunities/pipelines/YOUR_PIPELINE_ID/stages
   ```
4. Copy the Pipeline ID (the long string after `/pipelines/`)

**Write it here**: _______________________

### Get Stage IDs

For each stage, click on it and copy the ID from the URL:

1. Click **New Lead** stage
2. URL changes to: `.../stages/STAGE_ID_HERE`
3. Copy that stage ID

**Write them here**:
- New Lead: _______________________
- Hot Lead: _______________________
- Priority Review: _______________________
- Showing Scheduled: _______________________
- Offer Submitted: _______________________
- Under Contract: _______________________
- Closed Won: _______________________
- Closed Lost: _______________________

### Add to .env File

Now let's add these to your `.env` file. I'll help you with this!

---

## Step 5: Create Database Tables (2 min)

This creates the tables where agents store what they learn.

### Run SQL Command

```bash
cd "/Users/mikekwak/Real Estate Valuation"
psql dealfinder < database/agent_memory_schema.sql
```

**Expected output**:
```
CREATE TABLE
CREATE INDEX
CREATE FUNCTION
...
Agent memory schema created successfully!
```

**If you get an error about database**:
- Make sure PostgreSQL is running
- Make sure database "dealfinder" exists
- You may need to add your postgres password to `.env`

**✅ When successful, agents can store memories!**

---

## Step 6: Test Full Integration (5 min)

Now for the exciting part - watch an agent create a real opportunity in GHL!

### Run the GHL Integration Test

```bash
cd "/Users/mikekwak/Real Estate Valuation"
python examples/agents/agent_ghl_integration.py
```

**What should happen**:
1. Agent evaluates test property
2. Makes decision to create opportunity
3. Chooses pipeline stage (likely "Hot Lead")
4. Creates opportunity in GHL
5. Shows success message with opportunity ID

### Verify in GHL Dashboard

1. Go back to GHL in your browser
2. Click **Opportunities**
3. Select **"Investment Properties"** pipeline
4. You should see a new opportunity:
   - **Name**: "123 Sunset Blvd, Beverly Hills, CA 90210 - Score: 92"
   - **Stage**: Hot Lead
   - **Custom Fields**: Populated with property data

**✅ If you see it, setup is COMPLETE!** 🎉

---

## Troubleshooting

### "Pipeline not found"
- Double-check Pipeline ID in `.env`
- Make sure you copied the entire ID

### "Stage not found"
- Double-check Stage IDs in `.env`
- Each stage needs its own ID

### "Custom field not found"
- Make sure field keys match exactly
- Check spelling (deal_score vs dealScore)

### "Database connection failed"
- Add DB_PASSWORD to `.env`
- Make sure PostgreSQL is running

---

## After Successful Test

You'll have:
- ✅ Intelligent agents working
- ✅ GHL opportunities created automatically
- ✅ Custom fields populated with property data
- ✅ Correct pipeline stages selected
- ✅ Agent memory stored in database

**Next**: Build custom agents for your specific workflow!

---

## Need Help?

Pause here and let me know:
- Which step you're on
- What you're seeing
- Any errors or questions

I'll help you through it!

---

**Let's do this! Ready to create your first auto-generated GHL opportunity?** 🚀
