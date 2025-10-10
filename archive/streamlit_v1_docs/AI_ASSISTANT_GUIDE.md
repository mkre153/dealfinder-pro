# 🤖 AI Assistant Guide

## Overview

The AI Assistant is a conversational interface powered by Claude (Anthropic) that transforms how you interact with DealFinder Pro. Instead of manually filtering and browsing properties, you can simply ask questions in natural language and get intelligent, context-aware responses.

## Setup

### 1. Get an Anthropic API Key (Required)

1. Visit [Anthropic Console](https://console.anthropic.com/)
2. Sign up or log in
3. Navigate to API Keys section
4. Create a new API key
5. Copy the key (it starts with `sk-ant-...`)

### 2. Get a Perplexity API Key (Optional but Recommended)

The AI Assistant now includes **Perplexity AI** for real-time web search capabilities!

1. Visit [Perplexity Settings](https://www.perplexity.ai/settings/api)
2. Sign up or log in
3. Navigate to API section
4. Create a new API key
5. Copy the key (it starts with `pplx-...`)

**Free Tier:** $5 credit (enough for 250-1,000 searches)

**What Perplexity Enables:**
- 📰 Real-time market news and trends
- 🏘️ Neighborhood intelligence (schools, crime, demographics)
- 📊 Current market statistics beyond our database
- 📍 Recent comparable sales
- ⚖️ Local regulations and zoning information

### 3. Configure Your Environment

Add your API keys to the `.env` file:

```bash
# Open or create .env file
ANTHROPIC_API_KEY=sk-ant-api03-your-actual-key-here
PERPLEXITY_API_KEY=pplx-your-actual-key-here  # Optional but recommended
```

**Important:** Never commit your `.env` file to git. It's already in `.gitignore`.

**Note:** The AI Assistant works with just the Anthropic key (Claude). Perplexity is optional but adds real-time web search capabilities.

### 4. Restart the Dashboard

```bash
streamlit run dashboard/app.py
```

The AI Assistant page should now be available in the sidebar: **🤖 AI Assistant**

## Features

### 1. Natural Language Property Search

Instead of using filters, just ask:

```
"Show me 3 bedroom homes under $700K in La Jolla"
"Find properties with high cash flow potential"
"What are the best deals this week?"
"Properties that have been on market for 60+ days"
```

The AI understands:
- Price ranges ($500K-$1M, under $800K, etc.)
- Locations (cities, neighborhoods)
- Property specs (bedrooms, bathrooms, sqft)
- Investment criteria (cash flow, appreciation, below market)
- Time frames (this week, new today, etc.)

### 2. Deep Property Analysis

Get detailed insights on any property:

```
"Analyze 1234 Ocean View Dr"
"Why is this property a good deal?"
"What are the risks with this property?"
"Tell me more about the first property"
```

AI provides:
- ✅ **Strengths:** Why it's a good opportunity
- ⚠️ **Risks:** Potential concerns
- 📊 **Score Breakdown:** How the 0-100 score is calculated
- 💰 **Investment Analysis:** ROI, cash flow, appreciation potential
- 🏘️ **Market Context:** How it compares to similar properties

### 3. Market Insights

Understand market trends and statistics:

```
"What's happening in the San Diego market?"
"Compare San Diego vs Las Vegas"
"Which neighborhoods have the best deals?"
"Show me price trends"
"What's the average price per sqft in Pacific Beach?"
```

AI analyzes:
- Current inventory levels
- Price trends
- Days on market statistics
- Neighborhood comparisons
- Deal availability by area

### 4. Property Comparisons

Compare multiple properties side-by-side:

```
"Compare 1234 Main St and 5678 Ocean Ave"
"Show me the top 3 deals and compare them"
"Which is a better investment: property A or B?"
```

### 5. Investment Calculations

Get detailed ROI analysis:

```
"Calculate ROI for property at 1234 Main St"
"If I buy this for $600K with 20% down, what's my return?"
"What's my monthly cash flow with this property?"
```

AI calculates:
- Cash-on-cash return
- Cap rate
- Monthly cash flow
- Break-even rent
- 5-year appreciation estimates

### 6. Configuration via Chat

Update your preferences conversationally:

```
"Set my budget to $500K-$1M"
"Only show me properties over 15% below market"
"I'm looking for rental properties in San Diego"
"Change my minimum score to 75"
```

### 7. Real-Time Web Search (Perplexity AI)

**NEW:** When you have Perplexity configured, the AI can search the web for current information:

```
"What's the latest real estate news in San Diego?"
"Tell me about schools in La Jolla"
"What are the crime rates in Pacific Beach?"
"Find recent comparable sales near 1234 Main St"
"What are the short-term rental regulations in San Diego?"
"Is the market trending up or down this month?"
```

The AI intelligently decides when to:
- **Search our database** - For property listings, scores, and internal data
- **Search the web** - For real-time news, neighborhood data, market trends
- **Both** - Combine internal listings with external market intelligence

**Example Hybrid Query:**
```
You: "Show me properties in Pacific Beach and tell me about the neighborhood"

AI: [Searches database for properties]
    [Searches web for neighborhood info]

    "I found 23 properties in Pacific Beach ranging from $650K to $1.2M...

    About Pacific Beach:
    - School Rating: 7/10 average (based on GreatSchools)
    - Crime: 15% below San Diego average
    - Walkability: 89/100 (Very Walkable)
    - Popular for young professionals and beach lovers
    - Strong vacation rental market

    Sources: GreatSchools.org, NeighborhoodScout.com, Walk Score"
```

## Quick Actions

The AI Assistant page includes quick action buttons for common tasks:

- 🔥 **Show Hot Deals** - Immediately see the highest-scored properties
- 📊 **Market Overview** - Get a snapshot of current market conditions
- 💡 **Investment Tips** - Learn what to look for in investment properties
- 🏘️ **Best Neighborhoods** - Find areas with the most opportunities

## Example Conversations

### Example 1: First-Time Investor

```
You: I'm looking for my first investment property

AI: Great! Let's find you the perfect investment. A few questions:
    1. What's your budget range?
    2. Preferred location (San Diego, Las Vegas, or both)?
    3. Property type (single-family, condo, multi-unit)?
    4. Investment strategy (flip, rental, long-term hold)?

You: $500K-$800K, San Diego, rental income

AI: ✅ Searching for rental properties in San Diego ($500K-$800K)...

    Found 47 properties! Here are the top 3 by rental yield:

    🏠 1. 3BR Condo - North Park - $625K
       💰 Est. rent: $3,400/mo (6.5% yield)
       📊 Score: 68/100 (FAIR)
       🔍 [View Details]

    [Properties 2 & 3...]

    Want to see more or dive deeper into any of these?
```

### Example 2: Property Analysis

```
You: Analyze 1234 Ocean View Dr

AI: 📊 Deep Dive: 1234 Ocean View Dr, La Jolla

    **Quick Stats:**
    • Listed: $875K | Tax Assessed: $920K (5% below)
    • 3 bed | 2 bath | 1,650 sqft
    • Days on market: 67 (motivated seller!)
    • Opportunity Score: 71/100 (FAIR)

    **Why This Could Be a Good Deal:**
    ✅ 5% below tax assessed value
    ✅ 67 days on market (seller likely negotiable)
    ✅ Price/sqft $530 vs area avg $615 (14% below)
    ✅ Strong rental area ($4,200/mo potential)

    **Risks to Consider:**
    ⚠️ HOA: $450/mo (impacts cash flow)
    ⚠️ Built 1975 (may need updates)
    ⚠️ No recent comps (limited data)

    **Investment Analysis:**
    • Cash-on-cash return: 7.2%
    • Cap rate: 4.8%
    • Break-even: $3,650/mo

    **Recommendation:** Worth pursuing. Start negotiation at $825K.
```

### Example 3: Market Research

```
You: What's the best neighborhood for investment in San Diego?

AI: Based on current data, here are the top 3 neighborhoods for investment:

    **1. North Park** - Best Overall Value
    • Median: $650K (most affordable)
    • Average score: 45/100
    • Strong rental demand
    • 23 active listings
    • Growing area with good appreciation potential

    **2. Pacific Beach** - Highest Rental Yield
    • Median: $825K
    • High vacation rental demand
    • Beach proximity = premium rents
    • 18 active listings

    **3. Point Loma** - Long-term Appreciation
    • Median: $1.1M (higher entry)
    • Limited inventory (exclusive)
    • Stable, established neighborhood
    • 12 active listings

    **Recommendation:** For your budget, North Park offers the best balance
    of affordability and investment potential. Want to see listings there?
```

## Tips for Best Results

### Be Specific
❌ "Show me properties"
✅ "Show me 3 bedroom homes under $700K in La Jolla"

### Ask Follow-up Questions
The AI remembers context, so you can continue the conversation:
```
You: Show me properties in La Jolla
AI: [Shows results]
You: What about Point Loma?  ← AI remembers your criteria
You: Compare the first property from each  ← AI remembers both searches
```

### Use Natural Language
You don't need to use exact field names or technical terms. The AI understands:
- "cheap" → low price
- "motivated seller" → high days on market
- "good deal" → high opportunity score
- "positive cash flow" → rental income analysis

### Iterate and Refine
```
You: Show me condos in San Diego
AI: [Shows 500 results]
You: Under $600K
AI: [Shows 120 results]
You: In Downtown or Little Italy
AI: [Shows 15 results] ← Narrowed down perfectly
```

## Limitations

### Current Limitations:
1. **Historical Data:** AI analyzes current scan data only. For trends over time, use the Analytics page.
2. **External Data:** Cannot access MLS directly or pull real-time property updates.
3. **Document Analysis:** Cannot read property inspection reports or documents.
4. **Legal Advice:** Provides investment analysis only, not legal or tax advice.

### Coming Soon:
- 🔄 **Proactive Alerts:** AI will notify you when matching properties appear
- 📸 **Photo Analysis:** AI will analyze property photos for condition assessment
- 📈 **Predictive Analytics:** Price movement predictions
- 🤝 **Multi-property Portfolio Analysis:** Evaluate your entire portfolio

## Cost

The AI Assistant uses two APIs that charge based on usage:

### Claude AI (Anthropic) - Required
- **Average conversation:** $0.01-0.05 (very affordable)
- **Heavy usage (100 conversations):** ~$2-5/month
- **Model:** Claude 3.5 Sonnet
- **Use:** All conversational AI, property analysis, recommendations

### Perplexity AI - Optional
- **Average search:** $0.005-0.02 per query
- **Quick searches (sonar-small):** ~$0.005
- **Deep searches (sonar-large):** ~$0.015
- **Free tier:** $5 credit (250-1,000 searches)
- **Use:** Real-time web search, market news, neighborhood data

### Combined Usage Examples:
- **Basic conversation** (no web search): $0.01-0.03
- **Conversation + 1 web search**: $0.015-0.05
- **Heavy day (20 conversations, 5 searches)**: $0.50-1.00

**Budget tip:** Both services have no subscription - you only pay for what you use. Most users spend under $5/month for regular use.

## Privacy & Security

- **Your data:** Property data stays local, never sent to Anthropic
- **Conversations:** Not stored permanently (only in current session)
- **API key:** Stored securely in `.env` (not in code or git)

## Troubleshooting

### "ANTHROPIC_API_KEY not configured"
- Make sure your `.env` file exists and contains `ANTHROPIC_API_KEY=sk-ant-...`
- Restart the dashboard after adding the key
- Check that the key is valid (starts with `sk-ant-`)

### "Error: 401 Unauthorized"
- Your API key may be invalid or expired
- Check your Anthropic Console for key status
- Generate a new key if needed

### "Slow responses"
- Normal: AI analysis takes 2-5 seconds
- Check your internet connection
- Complex queries (e.g., analyzing many properties) take longer

### "No properties found"
- Make sure you've run a scan first (Command Center → Run Scan Now)
- Check that properties are loaded in session state
- Try restarting the dashboard

## Support

- **Documentation:** [Claude API Docs](https://docs.anthropic.com/)
- **Issues:** [GitHub Issues](https://github.com/anthropics/claude-code/issues)
- **API Status:** [Anthropic Status](https://status.anthropic.com/)

---

**Pro Tip:** The AI Assistant gets better the more you use it. It learns your preferences and adapts to your investment style. Start with simple questions and gradually explore more complex analysis!
