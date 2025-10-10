# Perplexity AI Integration - Technical Summary

## Overview

DealFinder Pro now features a **hybrid AI system** combining Claude (Anthropic) for conversational intelligence with Perplexity AI for real-time web search capabilities.

## Architecture

### Dual-AI System

```
User Query
    ↓
Claude AI (Decision Layer)
    ├─→ Internal Tools (Property Database)
    │   ├─ search_properties
    │   ├─ analyze_property
    │   ├─ get_market_insights
    │   ├─ compare_properties
    │   └─ calculate_roi
    │
    └─→ External Tool (Web Search)
        └─ web_search → Perplexity AI
            ├─ Market news
            ├─ Neighborhood data
            ├─ Current statistics
            ├─ Recent comparables
            └─ Regulations
```

### Smart Query Routing

Claude automatically decides which tools to use based on the user's question:

- **Database only:** "Show me 3 bedroom homes under $700K"
- **Web only:** "What's the latest real estate news in San Diego?"
- **Hybrid:** "Find properties in La Jolla and tell me about the schools"

## Files Created/Modified

### New Files

1. **`modules/perplexity_agent.py`** (300+ lines)
   - PerplexityAgent class for web search
   - 6 pre-built search methods:
     - `get_market_news()` - Recent market trends and news
     - `get_neighborhood_intelligence()` - Schools, crime, demographics
     - `get_comparable_sales()` - Recent sales data
     - `get_market_statistics()` - Current market metrics
     - `get_investment_forecast()` - Future outlook
     - `check_regulations()` - Zoning, rent control, taxes
   - Uses Perplexity sonar models (small/large/huge)
   - Automatic citation tracking

2. **`PERPLEXITY_INTEGRATION.md`** (this file)
   - Technical documentation
   - Setup instructions
   - Example use cases

### Modified Files

1. **`modules/ai_agent.py`**
   - Added Perplexity integration (line 12, 43)
   - New tool: `web_search` (lines 309-336)
   - Tool implementation: `_tool_web_search()` (lines 602-629)
   - Updated system prompt to mention web search capability

2. **`.env.example`**
   - Added PERPLEXITY_API_KEY configuration (lines 14-19)
   - Documentation on free tier and costs

3. **`requirements.txt`**
   - Added note about Perplexity using existing `requests` library (lines 51-52)
   - No new package dependencies needed

4. **`AI_ASSISTANT_GUIDE.md`**
   - New setup section for Perplexity (section 2)
   - New feature: Real-Time Web Search (section 7)
   - Updated cost breakdown for dual-AI system
   - Example hybrid queries

## Setup Instructions

### 1. Get Perplexity API Key

1. Visit https://www.perplexity.ai/settings/api
2. Sign up or log in
3. Navigate to API section
4. Create a new API key (starts with `pplx-...`)

**Free Tier:** $5 credit = 250-1,000 searches

### 2. Configure Environment

Add to `.env`:
```bash
PERPLEXITY_API_KEY=pplx-your-actual-key-here
```

### 3. Restart Dashboard

```bash
streamlit run dashboard/app.py
```

**Note:** Perplexity is optional. The AI Assistant works without it, but web search features will not be available.

## Technical Details

### Perplexity Models Used

| Model | Speed | Depth | Cost | Use Case |
|-------|-------|-------|------|----------|
| `sonar-small-128k-online` | Fast | Quick | ~$0.005 | Market news, quick facts |
| `sonar-large-128k-online` | Medium | Deep | ~$0.015 | Neighborhood analysis, statistics |
| `sonar-huge-128k-online` | Slow | Maximum | ~$0.030 | Comprehensive research |

### Search Domains

The system automatically selects the right model and prompting based on search type:

- **news** - Recent market trends, developments (last 30 days)
- **statistics** - Numerical data, market metrics, trends
- **neighborhood** - Schools, crime, demographics, amenities
- **comparables** - Recent sales (last 6 months)
- **regulations** - Zoning, rent control, taxes, HOA rules
- **general** - Other queries

### API Integration

```python
# Example: Get market news
from modules.perplexity_agent import PerplexityAgent

agent = PerplexityAgent()
result = agent.get_market_news("San Diego, CA", days=30)

print(result['answer'])
print(result['citations'])
```

### Error Handling

The system gracefully handles:
- Missing API key → Returns warning message, continues without web search
- API errors → Returns error message to user
- Rate limits → Caught and reported
- Invalid queries → Perplexity provides feedback

## Use Cases

### 1. Market Intelligence

**Query:** "What's happening in the San Diego real estate market?"

**Tools Used:** `web_search` (news)

**Result:** Recent news, trends, price movements with citations

---

### 2. Neighborhood Research

**Query:** "Tell me about schools and safety in Pacific Beach"

**Tools Used:** `web_search` (neighborhood)

**Result:** School ratings, crime stats, demographics, walkability

---

### 3. Hybrid Property Discovery

**Query:** "Show me 3BR homes in La Jolla under $1M and tell me about the area"

**Tools Used:** `search_properties` + `web_search` (neighborhood)

**Result:** Property listings from database + neighborhood intelligence from web

---

### 4. Investment Due Diligence

**Query:** "Find properties in Point Loma, analyze the best one, and tell me about rental regulations"

**Tools Used:** `search_properties` + `analyze_property` + `web_search` (regulations)

**Result:** Complete investment package with properties, analysis, and legal context

---

### 5. Market Comparison

**Query:** "Compare the San Diego and Las Vegas markets"

**Tools Used:** `get_market_insights` (both locations) + `web_search` (statistics)

**Result:** Database stats + current web data for comprehensive comparison

## Cost Analysis

### Typical Usage Patterns

| Activity | Claude Cost | Perplexity Cost | Total |
|----------|-------------|-----------------|-------|
| Simple property search | $0.01 | $0 | $0.01 |
| Property + neighborhood | $0.02 | $0.015 | $0.035 |
| Market research | $0.03 | $0.015 | $0.045 |
| Investment analysis | $0.04 | $0.02 | $0.06 |

### Monthly Estimates

| Usage Level | Conversations/Month | Searches/Month | Total Cost |
|-------------|---------------------|----------------|------------|
| Light | 20 | 10 | $0.50-1.00 |
| Moderate | 50 | 25 | $1.50-2.50 |
| Heavy | 100 | 50 | $3.00-5.00 |
| Power User | 200 | 100 | $6.00-10.00 |

**ROI:** If the AI helps you find even one good deal, it pays for itself 1000x over.

## Testing

### Manual Testing Checklist

To test the integration:

1. **Without Perplexity key:**
   - [ ] AI Assistant loads successfully
   - [ ] Property searches work
   - [ ] Web search queries show warning about missing key

2. **With Perplexity key:**
   - [ ] Ask: "What's the latest real estate news in San Diego?"
   - [ ] Ask: "Tell me about schools in La Jolla"
   - [ ] Ask: "Show me properties in Pacific Beach and tell me about crime rates"
   - [ ] Verify citations appear in responses
   - [ ] Check that responses are current (last 30 days)

### Example Test Queries

```python
# Test 1: Pure web search
"What are short-term rental regulations in San Diego?"

# Test 2: Hybrid query
"Find 3BR homes in Point Loma and tell me about the neighborhood"

# Test 3: Market analysis
"Compare current market conditions in San Diego vs Las Vegas"

# Test 4: Neighborhood intelligence
"What are the best schools near La Jolla?"

# Test 5: Recent comparables
"Find recent sales near 1234 Ocean View Dr, La Jolla"
```

## Future Enhancements

### Phase 2 (Planned)
- Automatic neighborhood scoring based on web data
- Property image analysis (Claude Vision + Perplexity context)
- Predictive analytics using web trends
- Automated market reports combining database + web data

### Phase 3 (Ideas)
- Vector database for semantic property search
- Multi-property portfolio analysis
- Custom alerts based on web news + database matches
- Integration with Google Maps API for location intelligence

## Troubleshooting

### "PERPLEXITY_API_KEY not configured"
- Add key to `.env` file
- Restart dashboard
- AI will work for database queries, but web search will be unavailable

### "Error querying Perplexity"
- Check API key is valid
- Verify you have credits remaining
- Check Perplexity API status: https://status.perplexity.ai/

### Slow responses
- Perplexity searches take 2-10 seconds (normal)
- Deep searches (`sonar-large`) are slower but more comprehensive
- Use quick searches for faster results

### No citations returned
- Some queries may not have sources
- Try rephrasing query to be more specific
- Check Perplexity response format

## Security & Privacy

### Data Handling
- **Property data:** Stays local, never sent to Perplexity
- **User queries:** Sent to Claude and Perplexity (required for AI)
- **API keys:** Stored in `.env` (gitignored, never committed)
- **Conversations:** Stored in session state only (cleared on restart)

### Best Practices
- Never commit `.env` to git
- Rotate API keys periodically
- Monitor usage for unexpected spikes
- Review citations before relying on data

## Credits

- **Claude AI:** Anthropic (https://www.anthropic.com)
- **Perplexity AI:** Perplexity (https://www.perplexity.ai)
- **Integration:** Built for DealFinder Pro
- **Date:** October 2025

---

**Questions?** See `AI_ASSISTANT_GUIDE.md` for user-facing documentation or check the inline code comments in `modules/perplexity_agent.py` and `modules/ai_agent.py`.
