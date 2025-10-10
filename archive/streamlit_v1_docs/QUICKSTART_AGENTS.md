# Quick Start Guide - Agentic System

## Get Started in 5 Minutes

### Step 1: Install AI Dependencies

```bash
cd "/Users/mikekwak/Real Estate Valuation"

# Install AI/ML packages
pip install anthropic>=0.18.0 openai>=1.10.0

# Or update all requirements
pip install -r requirements.txt
```

### Step 2: Set Up API Keys

Add to your `.env` file:

```bash
# Choose at least one LLM provider

# Option 1: Claude (Recommended)
ANTHROPIC_API_KEY=sk-ant-your-key-here

# Option 2: OpenAI
OPENAI_API_KEY=sk-your-key-here

# Your existing keys
GHL_API_KEY=your-ghl-key
GHL_LOCATION_ID=your-location-id
```

**Get API Keys:**
- Claude: https://console.anthropic.com/
- OpenAI: https://platform.openai.com/api-keys

### Step 3: Set Up Agent Memory Database

```bash
# Create agent memory table
psql dealfinder << 'EOF'
CREATE TABLE IF NOT EXISTS agent_memories (
    memory_id VARCHAR(255) PRIMARY KEY,
    agent_name VARCHAR(100) NOT NULL,
    memory_type VARCHAR(50) NOT NULL,
    content JSONB NOT NULL,
    importance DECIMAL(3,2),
    metadata JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    accessed_count INTEGER DEFAULT 0,
    last_accessed TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_agent_memories_agent ON agent_memories(agent_name);
CREATE INDEX idx_agent_memories_type ON agent_memories(memory_type);
CREATE INDEX idx_agent_memories_importance ON agent_memories(importance DESC);
EOF
```

### Step 4: Run Your First Agent

```bash
# Run the basic agent example
python examples/agents/example_basic_agent.py
```

You should see output like:

```
============================================================
   DealFinder Pro - Basic Agent Example
============================================================

Initializing LLM client...
✓ LLM client initialized (Claude)

Initializing database...
✓ Database connected

Creating Property Evaluator Agent...
✓ Agent created: property_evaluator

============================================================
TEST 1: Evaluating a GOOD DEAL
============================================================

============================================================
🤖 Agent: property_evaluator
📋 Task: Evaluating property at 123 Main Street, Beverly Hills, CA 90210
============================================================

Step 1: Calculating ROI...
   ROI: 29.41%
   Estimated Profit: $250,000

Step 2: Making intelligent decision...
   Decision: STRONG_BUY
   Confidence: 92%
   Reasoning: This property presents an excellent investment opportunity...

Step 3: Analyzing property characteristics...
   Key Insights:
      • Property is significantly undervalued (17% below market)
      • High days on market (95 days) indicates motivated seller
      • Strong ROI potential of 29.41%

   Recommendations:
      • Make offer quickly before competition increases
      • Budget for cosmetic updates (~$50K)
      • Consider cash offer for faster closing

============================================================
✅ Evaluation complete!
============================================================
```

### Step 5: Understand What Just Happened

The agent:
1. ✅ Used AI (Claude/GPT) to make intelligent decisions
2. ✅ Analyzed property data and market conditions
3. ✅ Provided reasoning for its decisions
4. ✅ Stored its experiences in memory
5. ✅ Learned patterns for future use

---

## What's Next?

### Learn More

📖 **Read the Full Guide**: `AGENT_SYSTEM_GUIDE.md`
- Complete step-by-step tutorial
- All examples explained
- GHL integration guide
- Building custom agents

### Build Your First Real Agent

```bash
# Market Analyst Agent (coming next)
python examples/agents/market_analyst_agent.py

# Connect to GHL
python examples/agents/agent_with_ghl.py

# Multi-agent system
python examples/agents/multi_agent_workflow.py
```

### Integration Path

1. **Week 1**: Learn basics (this guide)
2. **Week 2**: Build Market Analyst agent
3. **Week 3**: Connect to GHL
4. **Week 4**: Deploy multi-agent system

---

## Troubleshooting

**Problem**: `ModuleNotFoundError: No module named 'anthropic'`

**Solution**:
```bash
pip install anthropic openai
```

**Problem**: `ANTHROPIC_API_KEY not found`

**Solution**:
```bash
# Add to .env
echo "ANTHROPIC_API_KEY=sk-ant-your-key" >> .env

# Reload
source .env  # Linux/Mac
# OR restart terminal
```

**Problem**: Agent makes weird decisions

**Solution**: Agents need training data. The more they run, the better they get!

```python
# Manually teach patterns
agent.memory.learn_pattern(
    pattern_name="good_deal_indicator",
    insight="Properties 15%+ below market with DOM > 60 are hot deals",
    evidence=[],
    confidence=0.9
)
```

---

## Quick Reference

### Create an Agent

```python
from agents import LLMClient, BaseAgent

llm = LLMClient(provider="claude")
agent = MyAgent(llm, db)
```

### Make a Decision

```python
decision = agent.make_decision(
    context={"property": data},
    question="Should I buy this property?",
    options=["yes", "no"]
)
```

### Use a Tool

```python
result = agent.use_tool("create_opportunity", property_data=data)
```

### Store Memory

```python
agent.memory.store(
    content={"learned": "something important"},
    memory_type=MemoryType.LONG_TERM,
    importance=0.8
)
```

---

## Support

- **Full Documentation**: `AGENT_SYSTEM_GUIDE.md`
- **Examples**: `examples/agents/`
- **Issues**: Check logs in `logs/` directory

**Ready to build intelligent agents? Let's go! 🚀**
