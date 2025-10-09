# DealFinder Pro - Agentic System Guide
## Step-by-Step Learning & Usage Guide

**Version:** 1.0
**Last Updated:** 2025-10-08
**Status:** Learning Guide

---

## Table of Contents
1. [Introduction](#introduction)
2. [Understanding the Agentic System](#understanding)
3. [Setup & Configuration](#setup)
4. [Core Concepts](#core-concepts)
5. [Step-by-Step Examples](#examples)
6. [GHL Integration](#ghl-integration)
7. [Building Custom Agents](#custom-agents)
8. [Multi-Agent Workflows](#workflows)
9. [Troubleshooting](#troubleshooting)

---

## Introduction

### What is an Agentic System?

**Your Current System (Procedural Automation)**:
```python
# Fixed sequence, no intelligence
scrape_properties() → analyze() → sync_to_ghl() → notify()
```

**Agentic System (Autonomous Intelligence)**:
```python
# Agents make intelligent decisions
Market_Agent.decide_where_to_search()  # "Focus on ZIP 90210 today"
Deal_Hunter.find_best_properties()     # "These 3 properties are hot"
Buyer_Matcher.intelligently_match()    # "John is perfect for this deal"
Communication_Agent.optimize_outreach() # "Contact John at 10:30 AM via SMS"
```

### Key Differences

| Procedural Automation | Agentic System |
|----------------------|----------------|
| Fixed rules | Context-aware decisions |
| Static configuration | Dynamic adaptation |
| No learning | Learns from outcomes |
| Sequential execution | Coordinated collaboration |
| One-size-fits-all | Personalized actions |

---

## Understanding the Agentic System

### Architecture Overview

```
┌─────────────────────────────────────────────────────────┐
│                   AGENT COORDINATOR                      │
│            (Multi-agent communication hub)               │
└────────────┬──────────────┬──────────────┬─────────────┘
             │              │              │
        ┌────▼────┐    ┌───▼────┐   ┌────▼─────┐
        │ Market  │    │  Deal  │   │  Buyer   │
        │Analyst  │    │ Hunter │   │ Matcher  │
        │ Agent   │    │ Agent  │   │  Agent   │
        └────┬────┘    └───┬────┘   └────┬─────┘
             │             │              │
        Uses LLM      Uses LLM        Uses LLM
        for decisions for decisions   for decisions
             │             │              │
        ┌────▼─────────────▼──────────────▼─────┐
        │         AGENT MEMORY SYSTEM            │
        │  Short-term: Current context           │
        │  Long-term: Learned patterns          │
        └────┬───────────────────────────────────┘
             │
        ┌────▼────────────────────────────────────┐
        │          AGENT TOOLS                     │
        │  - Database queries                      │
        │  - GHL API calls                         │
        │  - Property scraping                     │
        │  - Data analysis                         │
        └──────────────────────────────────────────┘
```

### Core Components

1. **LLM Client** (`agents/llm_client.py`)
   - Provides AI reasoning to agents
   - Supports Claude and GPT-4
   - Structured decision-making

2. **Agent Memory** (`agents/memory.py`)
   - Short-term: Current context (recent actions)
   - Long-term: Learned patterns and insights
   - Pattern recognition and retrieval

3. **Base Agent** (`agents/base_agent.py`)
   - Foundation all agents inherit from
   - Decision-making capabilities
   - Tool usage
   - Learning from outcomes

4. **Agent Coordinator** (`agents/coordinator.py`)
   - Inter-agent communication
   - Shared workspace
   - Conflict resolution

---

## Setup & Configuration

### Step 1: Install Dependencies

```bash
# Navigate to your project
cd "/Users/mikekwak/Real Estate Valuation"

# Install AI/ML dependencies
pip install anthropic openai chromadb  # LLM providers and vector DB

# Or add to requirements.txt
echo "anthropic>=0.18.0" >> requirements.txt
echo "openai>=1.10.0" >> requirements.txt
echo "chromadb>=0.4.0" >> requirements.txt  # Optional: for semantic memory

pip install -r requirements.txt
```

### Step 2: Configure Environment Variables

Add to your `.env` file:

```bash
# LLM Provider (choose one or both)
ANTHROPIC_API_KEY=sk-ant-your-key-here
OPENAI_API_KEY=sk-your-key-here

# Existing GHL credentials
GHL_API_KEY=your-ghl-api-key
GHL_LOCATION_ID=your-location-id

# Database (already configured)
DB_USER=postgres
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=5432
DB_NAME=dealfinder
```

### Step 3: Database Setup (Agent Memory Storage)

```bash
# Create agent memory table
psql dealfinder << EOF
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

---

## Core Concepts

### 1. Agent Memory

**How it works**:

```python
from agents import AgentMemory, MemoryType

# Initialize memory
memory = AgentMemory(
    agent_name="market_analyst",
    db_manager=db,
    short_term_capacity=20,   # Recent context
    long_term_capacity=1000   # Learned patterns
)

# Store short-term memory (current context)
memory.store(
    content={"action": "analyzed_property", "property_id": "PROP_123"},
    memory_type=MemoryType.SHORT_TERM,
    importance=0.5
)

# Store long-term learning
memory.learn_pattern(
    pattern_name="hot_zip_indicator",
    insight="ZIP 90210 properties close 60% faster in winter",
    evidence=[deal1, deal2, deal3],
    confidence=0.85
)

# Recall relevant memories
memories = memory.recall("How to score properties in winter?", limit=5)
# Returns: [
#   {"content": {"insight": "ZIP 90210 properties close 60% faster in winter"}, ...},
#   ...
# ]
```

**Key Methods**:
- `store()` - Store a memory
- `recall()` - Find relevant memories
- `learn_pattern()` - Store learned insights
- `get_learned_patterns()` - Get all learnings
- `consolidate_short_to_long()` - Move important memories to long-term

### 2. LLM-Powered Decision Making

**How it works**:

```python
from agents import LLMClient

# Initialize LLM client
llm = LLMClient(provider="claude", model="claude-3-5-sonnet-20241022")

# Make a decision
decision = llm.make_decision(
    context={
        "property_price": 500000,
        "market_avg_price": 550000,
        "days_on_market": 95,
        "price_reductions": 2
    },
    question="Should we create a GHL opportunity for this property?",
    options=["yes", "no"],
    agent_role="Market Analyst"
)

# Returns:
# {
#   "decision": "yes",
#   "reasoning": "Property is 9% below market with 95 DOM and 2 price reductions...",
#   "confidence": 0.87,
#   "considerations": [
#       "Below market pricing indicates motivated seller",
#       "High DOM suggests urgency",
#       "Multiple reductions show flexibility"
#   ]
# }
```

**Key Methods**:
- `make_decision()` - Make structured decisions
- `analyze_data()` - Analyze data for insights
- `generate_message()` - Create personalized messages
- `generate_structured_response()` - Get JSON responses

### 3. Agent Tools

**How it works**:

```python
from agents import BaseAgent

class MarketAnalystAgent(BaseAgent):
    def __init__(self, llm_client, db_manager, ghl_connector):
        super().__init__(
            name="market_analyst",
            role="Market Analysis Expert",
            goal="Identify market trends and optimize deal scoring",
            llm_client=llm_client,
            db_manager=db_manager
        )

        # Add tools the agent can use
        self.add_tool(
            name="query_database",
            function=self._query_database,
            description="Query property database for market data",
            parameters={"query": "SQL query string"}
        )

        self.add_tool(
            name="create_ghl_opportunity",
            function=ghl_connector.create_opportunity,
            description="Create opportunity in GoHighLevel",
            parameters={"property_data": "Property information dict"}
        )

    def _query_database(self, query):
        return self.db.execute_query(query)

    # Agent can now use tools
    def analyze_market(self, zip_code):
        # Use tool to get data
        data = self.use_tool("query_database", query=f"SELECT * FROM properties WHERE zip_code='{zip_code}'")

        # Use LLM to analyze
        analysis = self.analyze(data, "Identify market trends")

        return analysis
```

---

## Step-by-Step Examples

### Example 1: Basic Agent Usage

```python
#!/usr/bin/env python3
"""
Example 1: Creating and using a simple agent
"""

from agents import LLMClient, AgentMemory, BaseAgent
from modules.database import DatabaseManager

# 1. Initialize components
db = DatabaseManager(your_db_config)
llm = LLMClient(provider="claude")

# 2. Create a simple agent
class SimpleAgent(BaseAgent):
    def execute_task(self, task):
        # Make a decision
        decision = self.make_decision(
            context=task,
            question="What action should I take?",
            options=["proceed", "skip", "investigate_further"]
        )
        return decision

# 3. Initialize agent
agent = SimpleAgent(
    name="test_agent",
    role="Property Evaluator",
    goal="Evaluate properties for investment potential",
    llm_client=llm,
    db_manager=db
)

# 4. Use the agent
task = {
    "property_address": "123 Main St, Beverly Hills",
    "list_price": 1200000,
    "bedrooms": 4,
    "days_on_market": 65
}

result = agent.execute_task(task)
print(f"Agent decision: {result['decision']}")
print(f"Reasoning: {result['reasoning']}")
print(f"Confidence: {result['confidence']}")
```

### Example 2: Agent Learning from Outcomes

```python
#!/usr/bin/env python3
"""
Example 2: Agent learning from successful/failed outcomes
"""

# Agent takes action
action = {
    "action_type": "create_ghl_opportunity",
    "property_id": "PROP_123",
    "deal_score": 85
}

# Outcome (simulated - would come from actual GHL/sales data)
outcome = {
    "opportunity_created": True,
    "buyer_interested": True,
    "showing_scheduled": True,
    "deal_closed": True,  # Success!
    "days_to_close": 18,
    "profit": 45000
}

# Agent learns from this success
agent.learn_from_outcome(
    action=action,
    outcome=outcome,
    success=True
)

# Later, agent recalls this learning
memories = agent.memory.recall("properties with score 85", limit=3)
# Agent will remember this successful pattern

# Get all learned insights
insights = agent.get_learned_insights()
for insight in insights:
    print(f"Pattern: {insight['insight']}")
    print(f"Confidence: {insight['confidence']}")
```

### Example 3: Multi-Agent Coordination

```python
#!/usr/bin/env python3
"""
Example 3: Multiple agents working together
"""

from agents import AgentCoordinator

# 1. Create coordinator
coordinator = AgentCoordinator(db_manager=db)

# 2. Create and register agents
market_analyst = MarketAnalystAgent(llm, db, ghl)
deal_hunter = DealHunterAgent(llm, db)
buyer_matcher = BuyerMatcherAgent(llm, db, ghl)

coordinator.register_agent(market_analyst)
coordinator.register_agent(deal_hunter)
coordinator.register_agent(buyer_matcher)

# 3. Deal Hunter asks Market Analyst for advice
coordinator.send_message(
    from_agent="deal_hunter",
    to_agent="market_analyst",
    message_type="question",
    content={
        "question": "Is ZIP code 90210 hot right now?",
        "context": {"season": "winter", "inventory": 45}
    },
    priority=5
)

# 4. Market Analyst processes message
messages = coordinator.get_messages("market_analyst")
for message in messages:
    # Analyze and respond
    response = market_analyst.analyze_market(message.content['context'])

    coordinator.mark_message_processed(
        agent_name="market_analyst",
        message=message,
        response=response
    )

# 5. Agents collaborate on a property
property_data = {
    "address": "456 Sunset Blvd",
    "zip_code": "90210",
    "price": 850000
}

# Request collaboration
collaborators = coordinator.request_collaboration(
    requesting_agent="deal_hunter",
    task={"evaluate_property": property_data},
    required_roles=["Market Analysis Expert", "Buyer Matching Expert"]
)

print(f"Collaborating agents: {collaborators}")
```

---

## GHL Integration

### Step 1: Connect Agent to GHL Connector

```python
#!/usr/bin/env python3
"""
Connecting agents to GoHighLevel
"""

from integrations.ghl_connector import GoHighLevelConnector
from agents import LLMClient, BaseAgent

# 1. Initialize GHL connector (your existing integration)
ghl = GoHighLevelConnector(
    api_key=os.getenv('GHL_API_KEY'),
    location_id=os.getenv('GHL_LOCATION_ID')
)

# 2. Create agent with GHL tools
class GHLAgent(BaseAgent):
    def __init__(self, llm_client, db_manager, ghl_connector):
        super().__init__(
            name="ghl_agent",
            role="GHL Integration Specialist",
            goal="Optimize GHL opportunity creation and buyer outreach",
            llm_client=llm_client,
            db_manager=db_manager
        )

        self.ghl = ghl_connector

        # Add GHL tools
        self.add_tool(
            name="create_opportunity",
            function=self.ghl.create_opportunity,
            description="Create opportunity in GHL pipeline",
            parameters={"opportunity_data": "dict"}
        )

        self.add_tool(
            name="send_sms",
            function=self.ghl.send_sms,
            description="Send SMS to contact",
            parameters={"contact_id": "str", "message": "str"}
        )

        self.add_tool(
            name="trigger_workflow",
            function=self.ghl.trigger_workflow,
            description="Trigger GHL workflow",
            parameters={"workflow_id": "str", "contact_id": "str"}
        )

    def execute_task(self, task):
        """Intelligently handle GHL operations"""

        if task['type'] == 'create_opportunity':
            # Agent decides whether to create opportunity
            decision = self.make_decision(
                context=task['property_data'],
                question="Should I create a GHL opportunity?",
                options=["yes", "no"]
            )

            if decision['decision'] == 'yes':
                # Agent decides best pipeline stage
                stage_decision = self.make_decision(
                    context=task['property_data'],
                    question="Which pipeline stage is most appropriate?",
                    options=["new_lead", "hot_lead", "priority_review"]
                )

                # Create opportunity using tool
                opp_data = {
                    **task['property_data'],
                    "pipelineStageId": stage_decision['decision']
                }

                result = self.use_tool("create_opportunity", opportunity_data=opp_data)

                # Learn from this action
                self.memory.store(
                    content={
                        "action": "created_opportunity",
                        "property": task['property_data']['address'],
                        "stage": stage_decision['decision'],
                        "reasoning": stage_decision['reasoning']
                    },
                    memory_type=MemoryType.EPISODIC,
                    importance=0.7
                )

                return result

        return None

# 3. Use the agent
agent = GHLAgent(llm, db, ghl)

property = {
    "type": "create_opportunity",
    "property_data": {
        "address": "789 Hollywood Blvd",
        "list_price": 950000,
        "deal_score": 88,
        "below_market_pct": 12,
        "days_on_market": 78
    }
}

result = agent.execute_task(property)
print(f"GHL Opportunity created: {result}")
```

### Step 2: Intelligent Buyer Matching with GHL

```python
#!/usr/bin/env python3
"""
Agent-powered buyer matching with GHL integration
"""

class SmartBuyerMatcherAgent(BaseAgent):
    def __init__(self, llm_client, db_manager, ghl_connector):
        super().__init__(
            name="smart_buyer_matcher",
            role="Intelligent Buyer Matching Specialist",
            goal="Match properties to buyers with personalized outreach",
            llm_client=llm_client,
            db_manager=db_manager
        )

        self.ghl = ghl_connector

        # Add tools
        self.add_tool(
            name="get_buyers",
            function=self._get_buyers_from_ghl,
            description="Fetch buyers from GHL",
            parameters={}
        )

        self.add_tool(
            name="send_personalized_sms",
            function=self._send_smart_sms,
            description="Send personalized SMS via GHL",
            parameters={"buyer": "dict", "property": "dict"}
        )

    def _get_buyers_from_ghl(self):
        return self.ghl.search_contacts(tags=["active_buyer"])

    def _send_smart_sms(self, buyer, property):
        # Agent generates personalized message
        message = self.llm.generate_message(
            recipient_context={
                "name": buyer.get('firstName'),
                "budget": buyer.get('customFields', {}).get('budget_max'),
                "location_pref": buyer.get('customFields', {}).get('location_preference'),
                "past_interactions": buyer.get('tags', [])
            },
            message_goal=f"Notify about new property at {property['address']}",
            tone="professional but urgent"
        )

        # Send via GHL
        return self.ghl.send_sms(buyer['id'], message)

    def execute_task(self, task):
        """Match property to buyers intelligently"""

        property_data = task['property']

        # Get buyers
        buyers = self.use_tool("get_buyers")

        # Agent analyzes each buyer
        matches = []
        for buyer in buyers:
            # Agent decides if this is a good match
            match_decision = self.make_decision(
                context={
                    "property": property_data,
                    "buyer_budget": buyer.get('customFields', {}).get('budget_max'),
                    "buyer_location_pref": buyer.get('customFields', {}).get('location_preference'),
                    "buyer_property_type_pref": buyer.get('customFields', {}).get('property_type_preference')
                },
                question="Is this property a good match for this buyer?",
                options=["excellent_match", "good_match", "poor_match"]
            )

            if match_decision['decision'] in ['excellent_match', 'good_match']:
                # Agent decides when to contact
                timing_decision = self.make_decision(
                    context={
                        "buyer_response_history": buyer.get('tags', []),
                        "current_time": datetime.now().hour
                    },
                    question="What's the best time to contact this buyer?",
                    options=["now", "morning", "afternoon", "evening"]
                )

                matches.append({
                    "buyer": buyer,
                    "match_quality": match_decision['decision'],
                    "reasoning": match_decision['reasoning'],
                    "best_contact_time": timing_decision['decision']
                })

        # Send messages to top matches
        for match in matches[:3]:  # Top 3 matches
            if match['best_contact_time'] == 'now':
                self.use_tool("send_personalized_sms", buyer=match['buyer'], property=property_data)

        return matches

# Use the agent
buyer_matcher = SmartBuyerMatcherAgent(llm, db, ghl)

result = buyer_matcher.execute_task({
    "property": {
        "address": "321 Pacific Ave",
        "list_price": 1100000,
        "bedrooms": 3,
        "zip_code": "90210",
        "deal_score": 92
    }
})

print(f"Found {len(result)} matches")
for match in result:
    print(f"- {match['buyer']['firstName']}: {match['match_quality']} ({match['reasoning']})")
```

---

## Building Custom Agents

### Template for Custom Agent

```python
#!/usr/bin/env python3
"""
Template for creating custom agents
"""

from agents import BaseAgent, MemoryType

class MyCustomAgent(BaseAgent):
    """
    Your custom agent description
    """

    def __init__(self, llm_client, db_manager, **kwargs):
        super().__init__(
            name="my_custom_agent",
            role="Your Agent Role",
            goal="What this agent aims to achieve",
            llm_client=llm_client,
            db_manager=db_manager,
            config=kwargs
        )

        # Add agent-specific tools
        self._setup_tools()

        # Load any agent-specific configuration
        self._load_config()

    def _setup_tools(self):
        """Setup tools this agent can use"""
        self.add_tool(
            name="tool_name",
            function=self._tool_function,
            description="What this tool does",
            parameters={"param1": "description"}
        )

    def _tool_function(self, param1):
        """Implementation of tool"""
        # Your tool logic here
        pass

    def _load_config(self):
        """Load agent-specific configuration"""
        # Load any custom config
        pass

    def execute_task(self, task):
        """
        Main task execution method

        Args:
            task: Task to execute

        Returns:
            Task result
        """
        # 1. Understand the task
        task_type = task.get('type')

        # 2. Recall relevant past experiences
        memories = self.memory.recall(f"tasks like {task_type}", limit=5)

        # 3. Make decision
        decision = self.make_decision(
            context={
                **task,
                "past_experiences": memories
            },
            question="What's the best approach for this task?",
            options=["approach_a", "approach_b", "approach_c"]
        )

        # 4. Execute chosen approach
        result = self._execute_approach(decision['decision'], task)

        # 5. Store result in memory
        self.memory.store(
            content={
                "task": task,
                "decision": decision,
                "result": result
            },
            memory_type=MemoryType.EPISODIC,
            importance=0.7
        )

        return result

    def _execute_approach(self, approach, task):
        """Execute the chosen approach"""
        if approach == "approach_a":
            # Implementation
            pass
        elif approach == "approach_b":
            # Implementation
            pass
        else:
            # Implementation
            pass

        return {"status": "completed"}
```

---

## Multi-Agent Workflows

### Complete Workflow Example

```python
#!/usr/bin/env python3
"""
Complete multi-agent workflow for property evaluation and GHL sync
"""

from agents import AgentCoordinator, LLMClient
from modules.database import DatabaseManager
from integrations.ghl_connector import GoHighLevelConnector

# Initialize
db = DatabaseManager(config)
ghl = GoHighLevelConnector(api_key, location_id)
llm = LLMClient(provider="claude")
coordinator = AgentCoordinator(db_manager=db)

# Create agents
market_analyst = MarketAnalystAgent(llm, db, ghl)
deal_hunter = DealHunterAgent(llm, db)
buyer_matcher = SmartBuyerMatcherAgent(llm, db, ghl)
ghl_agent = GHLAgent(llm, db, ghl)

# Register all agents
for agent in [market_analyst, deal_hunter, buyer_matcher, ghl_agent]:
    coordinator.register_agent(agent)

# Workflow: New property found
new_property = {
    "address": "999 Dream St",
    "list_price": 750000,
    "zip_code": "90210",
    "bedrooms": 4,
    "days_on_market": 88
}

# Step 1: Market Analyst evaluates market conditions
market_analysis = market_analyst.analyze_market(new_property['zip_code'])

# Step 2: Deal Hunter evaluates property
deal_evaluation = deal_hunter.execute_task({
    "type": "evaluate_deal",
    "property": new_property,
    "market_analysis": market_analysis
})

# Step 3: If good deal, create GHL opportunity
if deal_evaluation['recommendation'] == 'proceed':
    ghl_result = ghl_agent.execute_task({
        "type": "create_opportunity",
        "property_data": {
            **new_property,
            "deal_score": deal_evaluation['score']
        }
    })

    # Step 4: Find and notify matching buyers
    matches = buyer_matcher.execute_task({
        "property": new_property
    })

    print(f"✅ Workflow complete:")
    print(f"   - Market Analysis: {market_analysis['insights'][0]}")
    print(f"   - Deal Score: {deal_evaluation['score']}")
    print(f"   - GHL Opportunity: Created")
    print(f"   - Buyers Notified: {len(matches)}")
```

---

## Troubleshooting

### Common Issues

**Issue 1: LLM API Key Not Found**
```bash
# Error: ANTHROPIC_API_KEY not found
# Solution: Add to .env
echo "ANTHROPIC_API_KEY=sk-ant-your-key" >> .env
source .env  # Reload environment
```

**Issue 2: Agent Memory Not Persisting**
```python
# Check if database table exists
db.execute_query("SELECT COUNT(*) FROM agent_memories")

# If table doesn't exist, run schema:
# (See Step 3 in Setup section)
```

**Issue 3: Agent Makes Poor Decisions**
```python
# Agents learn from outcomes - need training data
# Manually teach agent good patterns:

agent.memory.learn_pattern(
    pattern_name="high_dom_indicator",
    insight="Properties with DOM > 90 in winter are motivated sellers",
    evidence=[successful_deal1, successful_deal2],
    confidence=0.9
)
```

**Issue 4: GHL Integration Fails**
```python
# Test GHL connection
ghl.test_connection()

# Check agent has GHL tools
print(agent.tools.keys())  # Should show GHL tools

# Verify agent uses tools correctly
result = agent.use_tool("create_opportunity", opportunity_data=test_data)
```

---

## Next Steps

### Week 1: Learn the Basics
- [ ] Run Example 1 (Basic Agent Usage)
- [ ] Run Example 2 (Agent Learning)
- [ ] Explore agent memory system
- [ ] Test LLM decision-making

### Week 2: GHL Integration
- [ ] Connect agent to GHL
- [ ] Test opportunity creation
- [ ] Test buyer matching
- [ ] Monitor agent decisions

### Week 3: Build Custom Agents
- [ ] Create Market Analyst agent
- [ ] Create Deal Hunter agent
- [ ] Create Buyer Matchmaker agent
- [ ] Test multi-agent coordination

### Week 4: Production Deployment
- [ ] Integrate agents into main.py workflow
- [ ] Set up agent monitoring
- [ ] Train agents with historical data
- [ ] Deploy and optimize

---

## Resources

- **LLM Client Docs**: `agents/llm_client.py` - Docstrings for all methods
- **Base Agent Docs**: `agents/base_agent.py` - Agent capabilities
- **Memory System Docs**: `agents/memory.py` - Memory management
- **Your Existing Code**: All existing modules work as agent tools!

---

**Ready to build intelligent agents? Start with Example 1 and work your way up!**
