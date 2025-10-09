# DealFinder Pro - Agentic System Flowchart

## High-Level Architecture Flow

```
┌─────────────────────────────────────────────────────────────────────┐
│                         USER / SCHEDULER                             │
│                    (Triggers daily workflow)                         │
└────────────────────────────┬────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    AGENT COORDINATOR                                 │
│              (Central communication hub)                             │
│                                                                      │
│  • Manages all agents                                               │
│  • Routes messages between agents                                   │
│  • Resolves conflicts                                               │
│  • Maintains shared workspace                                       │
└────────┬─────────┬──────────┬──────────┬────────────────────────────┘
         │         │          │          │
         ▼         ▼          ▼          ▼
    ┌────────┐ ┌──────┐ ┌────────┐ ┌──────────┐
    │Market  │ │Deal  │ │Buyer   │ │Comm.     │
    │Analyst │ │Hunter│ │Matcher │ │Agent     │
    └────┬───┘ └───┬──┘ └───┬────┘ └────┬─────┘
         │         │        │           │
         └─────────┴────────┴───────────┘
                     │
                     ▼
         ┌───────────────────────┐
         │   AGENT MEMORY        │
         │  • Short-term         │
         │  • Long-term          │
         │  • Learned patterns   │
         └───────────┬───────────┘
                     │
                     ▼
         ┌───────────────────────┐
         │    AGENT TOOLS        │
         │  (Your existing code) │
         │  • GHL Connector      │
         │  • Database           │
         │  • Scraper            │
         │  • Analyzer           │
         └───────────────────────┘
```

---

## Detailed Decision Flow

### 1. Single Agent Decision Process

```
┌─────────────────────────────────────────────────────────────────┐
│                    TASK ARRIVES                                  │
│              (e.g., "Evaluate this property")                    │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           ▼
                ┌──────────────────────┐
                │   AGENT RECEIVES      │
                │       TASK            │
                └──────────┬───────────┘
                           │
                           ▼
        ┌──────────────────────────────────────┐
        │  Step 1: RECALL RELEVANT MEMORIES    │
        │  "Have I seen this before?"          │
        │                                      │
        │  Agent.memory.recall(query)          │
        │  Returns: Past experiences,          │
        │           learned patterns           │
        └──────────────────┬───────────────────┘
                           │
                           ▼
        ┌──────────────────────────────────────┐
        │  Step 2: GATHER CONTEXT              │
        │  "What tools/data do I need?"        │
        │                                      │
        │  - Current property data             │
        │  - Market conditions                 │
        │  - Past similar cases                │
        │  - Buyer demand                      │
        └──────────────────┬───────────────────┘
                           │
                           ▼
        ┌──────────────────────────────────────┐
        │  Step 3: LLM REASONING               │
        │  "What should I do?"                 │
        │                                      │
        │  llm.make_decision(                  │
        │      context = {...},                │
        │      question = "Should I...?",      │
        │      options = [...]                 │
        │  )                                   │
        │                                      │
        │  LLM analyzes all context and        │
        │  returns structured decision         │
        └──────────────────┬───────────────────┘
                           │
                           ▼
        ┌──────────────────────────────────────┐
        │  Step 4: DECISION OUTPUT             │
        │                                      │
        │  {                                   │
        │    "decision": "yes",                │
        │    "reasoning": "Property is...",    │
        │    "confidence": 0.87,               │
        │    "considerations": [...]           │
        │  }                                   │
        └──────────────────┬───────────────────┘
                           │
                           ▼
                    ┌──────────┐
                    │ High      │
                    │Confidence?│
                    └──┬────┬───┘
                  Yes  │    │ No
                       ▼    ▼
            ┌──────────────────────┐
            │ Execute               │ Review/
            │ Decision              │ Flag for
            │                       │ Human
            │ Use tools to          │
            │ take action           │
            └──────────┬────────────┘
                       │
                       ▼
        ┌──────────────────────────────────────┐
        │  Step 5: STORE IN MEMORY             │
        │  "Remember this for next time"       │
        │                                      │
        │  agent.memory.store(                 │
        │      content = {decision, context},  │
        │      importance = confidence         │
        │  )                                   │
        └──────────────────────────────────────┘
```

---

## 2. Multi-Agent Collaboration Flow

```
┌────────────────────────────────────────────────────────────────────┐
│                  NEW PROPERTY DISCOVERED                            │
│              "456 Sunset Blvd, $850K, 90210"                       │
└───────────────────────────┬────────────────────────────────────────┘
                            │
                            ▼
             ┌──────────────────────────────┐
             │    AGENT COORDINATOR         │
             │  "Which agents should        │
             │   handle this?"              │
             └──────────┬───────────────────┘
                        │
        ┌───────────────┼───────────────┐
        │               │               │
        ▼               ▼               ▼
┌───────────────┐ ┌──────────┐ ┌─────────────┐
│ MARKET        │ │  DEAL    │ │   BUYER     │
│ ANALYST       │ │  HUNTER  │ │  MATCHER    │
│ AGENT         │ │  AGENT   │ │   AGENT     │
└───────┬───────┘ └────┬─────┘ └──────┬──────┘
        │              │              │
        │ STEP 1       │              │
        ▼              │              │
┌───────────────────────┐             │
│ Analyze Market        │             │
│ "Is 90210 hot         │             │
│  right now?"          │             │
│                       │             │
│ Decision:             │             │
│ "Market cooling       │             │
│  but still strong"    │             │
└───────┬───────────────┘             │
        │                             │
        │ Send to Coordinator         │
        └─────────┐                   │
                  ▼                   │
        ┌─────────────────┐           │
        │  COORDINATOR    │           │
        │  Shares insight │           │
        │  with other     │           │
        │  agents         │           │
        └────────┬────────┘           │
                 │                    │
        ┌────────┴─────────┐          │
        │                  │          │
        ▼        STEP 2    ▼          │
┌────────────────────────────────┐    │
│ DEAL HUNTER receives           │    │
│ market insight                 │    │
│                                │    │
│ "Market cooling = prioritize   │    │
│  high DOM properties"          │    │
│                                │    │
│ Decision:                      │    │
│ "95 DOM + motivated seller     │    │
│  = PRIORITY DEAL"              │    │
│                                │    │
│ Recommendation:                │    │
│ "Create GHL opportunity"       │    │
└────────────┬───────────────────┘    │
             │                        │
             │ Send to Coordinator    │
             └──────────┐             │
                        ▼             │
              ┌─────────────────┐     │
              │  COORDINATOR    │     │
              │  Triggers next  │     │
              │  agent          │     │
              └────────┬────────┘     │
                       │              │
                       │   STEP 3     │
                       └──────────────┘
                                      │
                                      ▼
                        ┌──────────────────────────┐
                        │ BUYER MATCHER            │
                        │ "Find best buyers"       │
                        │                          │
                        │ Queries:                 │
                        │ - Buyer budget match     │
                        │ - Location preference    │
                        │ - Response history       │
                        │                          │
                        │ Finds:                   │
                        │ - John (95% match)       │
                        │ - Sarah (87% match)      │
                        │ - Mike (82% match)       │
                        └──────────┬───────────────┘
                                   │
                                   │ Send to Coordinator
                                   ▼
                        ┌─────────────────────┐
                        │  COORDINATOR        │
                        │  All agents have    │
                        │  provided input     │
                        │                     │
                        │  Final decision:    │
                        │  Execute workflow   │
                        └──────────┬──────────┘
                                   │
                                   ▼
                        ┌─────────────────────┐
                        │ EXECUTE ACTIONS     │
                        │                     │
                        │ 1. Create GHL opp   │
                        │ 2. Notify 3 buyers  │
                        │ 3. Set hot priority │
                        │ 4. Create tasks     │
                        └─────────────────────┘
```

---

## 3. Agent Memory System Flow

```
┌─────────────────────────────────────────────────────────────┐
│                   AGENT EXPERIENCE CYCLE                     │
└─────────────────────────┬───────────────────────────────────┘
                          │
                          ▼
        ┌─────────────────────────────────────┐
        │  1. AGENT TAKES ACTION              │
        │                                     │
        │  Example:                           │
        │  - Create GHL opportunity           │
        │  - Match property to buyer          │
        │  - Send SMS notification            │
        └──────────────┬──────────────────────┘
                       │
                       │ Store in SHORT-TERM MEMORY
                       ▼
        ┌─────────────────────────────────────┐
        │  SHORT-TERM MEMORY                  │
        │  (Recent context, last 20 actions)  │
        │                                     │
        │  [                                  │
        │    {action: "created_opp",          │
        │     property: "123 Main",           │
        │     time: "2025-10-08 10:30"},      │
        │    {action: "matched_buyer",        │
        │     buyer: "John",                  │
        │     score: 95}                      │
        │  ]                                  │
        └──────────────┬──────────────────────┘
                       │
                       │ Time passes...
                       │ Outcome becomes known
                       ▼
        ┌─────────────────────────────────────┐
        │  2. OUTCOME RECEIVED                │
        │                                     │
        │  Example:                           │
        │  - Deal closed successfully         │
        │  - Buyer responded positively       │
        │  - Property sold in 18 days         │
        │                                     │
        │  Outcome: {                         │
        │    success: true,                   │
        │    days_to_close: 18,               │
        │    profit: $45,000                  │
        │  }                                  │
        └──────────────┬──────────────────────┘
                       │
                       │ Agent learns
                       ▼
        ┌─────────────────────────────────────┐
        │  3. LEARNING PROCESS                │
        │                                     │
        │  agent.learn_from_outcome(          │
        │      action = {...},                │
        │      outcome = {...},               │
        │      success = true                 │
        │  )                                  │
        │                                     │
        │  Agent identifies patterns:         │
        │  "Properties with 95 DOM +          │
        │   motivated seller close fast"      │
        └──────────────┬──────────────────────┘
                       │
                       │ Important learning?
                       ▼
                 ┌──────────┐
                 │Important?│
                 └──┬───┬───┘
              Yes   │   │ No (stays short-term)
                    ▼   │
        ┌──────────────────────────────────────┐
        │  CONSOLIDATE TO LONG-TERM MEMORY     │
        │                                      │
        │  memory.consolidate_short_to_long()  │
        │                                      │
        │  Moved to persistent storage         │
        └──────────────┬───────────────────────┘
                       │
                       ▼
        ┌─────────────────────────────────────┐
        │  LONG-TERM MEMORY                   │
        │  (Learned patterns, up to 1000)     │
        │                                     │
        │  Patterns:                          │
        │  {                                  │
        │    pattern: "high_dom_success",     │
        │    insight: "Properties DOM>90      │
        │             close 60% faster",      │
        │    confidence: 0.85,                │
        │    evidence: [deal1, deal2...]      │
        │  }                                  │
        └──────────────┬──────────────────────┘
                       │
                       │ Next decision needs this
                       ▼
        ┌─────────────────────────────────────┐
        │  4. MEMORY RECALL                   │
        │                                     │
        │  New property arrives with DOM=95   │
        │                                     │
        │  Agent recalls:                     │
        │  "I've seen this pattern before!    │
        │   High DOM = fast close"            │
        │                                     │
        │  Uses this to make better decision  │
        └─────────────────────────────────────┘
```

---

## 4. Agent Tools Integration Flow

```
┌────────────────────────────────────────────────────────────┐
│                   AGENT NEEDS TO ACT                        │
│            "Create GHL opportunity for property"            │
└──────────────────────────┬─────────────────────────────────┘
                           │
                           ▼
            ┌──────────────────────────────┐
            │  Agent checks available      │
            │  TOOLS                       │
            │                              │
            │  agent.tools = {             │
            │    "create_ghl_opp": func,   │
            │    "query_database": func,   │
            │    "send_sms": func          │
            │  }                           │
            └──────────────┬───────────────┘
                           │
                           ▼
            ┌──────────────────────────────┐
            │  Agent selects tool          │
            │  "create_ghl_opp"            │
            │                              │
            │  agent.use_tool(             │
            │      "create_ghl_opp",       │
            │      property_data={...}     │
            │  )                           │
            └──────────────┬───────────────┘
                           │
                           ▼
            ┌──────────────────────────────┐
            │  Tool executes               │
            │  (Your existing code!)       │
            │                              │
            │  ghl_connector.              │
            │    create_opportunity({...}) │
            │                              │
            │  Uses YOUR existing:         │
            │  - GHL_API_KEY               │
            │  - GHL_LOCATION_ID           │
            └──────────────┬───────────────┘
                           │
                           ▼
            ┌──────────────────────────────┐
            │  YOUR EXISTING GHL           │
            │  INTEGRATION                 │
            │                              │
            │  POST to GHL API:            │
            │  /opportunities              │
            │                              │
            │  Creates opportunity         │
            │  in your GHL account         │
            └──────────────┬───────────────┘
                           │
                           ▼
            ┌──────────────────────────────┐
            │  Result returned to agent    │
            │                              │
            │  {                           │
            │    "success": true,          │
            │    "opportunity_id": "123"   │
            │  }                           │
            └──────────────┬───────────────┘
                           │
                           ▼
            ┌──────────────────────────────┐
            │  Agent stores in memory      │
            │  "Remember I used this tool" │
            │                              │
            │  memory.store({              │
            │    action: "used_tool",      │
            │    tool: "create_ghl_opp",   │
            │    result: success           │
            │  })                          │
            └──────────────────────────────┘
```

---

## 5. Complete Workflow Example

```
DAY 1: NEW PROPERTY FOUND
┌─────────────────────────────────────────────────────────────────┐
│  Scraper finds: "789 Dream St, $750K, 90210, 88 DOM"          │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
         ┌───────────────────────────────┐
         │  COORDINATOR receives         │
         │  Triggers: Market Analyst     │
         └───────────┬───────────────────┘
                     │
                     ▼
         ┌───────────────────────────────────────┐
         │  MARKET ANALYST AGENT                 │
         │                                       │
         │  1. Recalls: "90210 in winter"       │
         │     Memory: "Strong market"          │
         │                                       │
         │  2. Uses tool: query_database        │
         │     Gets: Recent 90210 sales         │
         │                                       │
         │  3. LLM Decision:                    │
         │     "Market strong, DOM high         │
         │      = motivated seller"             │
         │                                       │
         │  4. Recommends: "Pursue deal"        │
         │     Confidence: 0.89                 │
         └───────────┬───────────────────────────┘
                     │
                     │ Send to Deal Hunter
                     ▼
         ┌───────────────────────────────────────┐
         │  DEAL HUNTER AGENT                    │
         │                                       │
         │  1. Receives market insight           │
         │                                       │
         │  2. Uses tool: analyze_property       │
         │     Score: 88/100                     │
         │                                       │
         │  3. LLM Decision:                     │
         │     "Strong deal, create opp"         │
         │                                       │
         │  4. Uses tool: create_ghl_opp         │
         │     Stage: "hot_lead"                 │
         └───────────┬───────────────────────────┘
                     │
                     │ Notify Buyer Matcher
                     ▼
         ┌───────────────────────────────────────┐
         │  BUYER MATCHER AGENT                  │
         │                                       │
         │  1. Uses tool: get_buyers_from_ghl    │
         │     Returns: 50 active buyers         │
         │                                       │
         │  2. For each buyer:                   │
         │     LLM Decision: "Match quality?"    │
         │                                       │
         │  3. Top matches:                      │
         │     - John: 95% match                 │
         │     - Sarah: 87% match                │
         │                                       │
         │  4. Uses tool: send_sms               │
         │     Personalized messages sent        │
         └───────────┬───────────────────────────┘
                     │
                     │ All actions stored in memory
                     ▼
         ┌───────────────────────────────────────┐
         │  SHORT-TERM MEMORY                    │
         │  All agents store their actions       │
         └───────────────────────────────────────┘


DAY 15: OUTCOME RECEIVED
┌─────────────────────────────────────────────────────────────────┐
│  Property sold! John made offer, closed in 12 days, $42K profit │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
         ┌───────────────────────────────────────┐
         │  ALL AGENTS LEARN                     │
         │                                       │
         │  Market Analyst learns:               │
         │  "90210 winter = strong"              │
         │                                       │
         │  Deal Hunter learns:                  │
         │  "High DOM (88) + score 88 = success" │
         │                                       │
         │  Buyer Matcher learns:                │
         │  "John responds to 90210 props"       │
         │  "SMS morning = best"                 │
         └───────────┬───────────────────────────┘
                     │
                     │ Consolidate to long-term
                     ▼
         ┌───────────────────────────────────────┐
         │  LONG-TERM MEMORY                     │
         │  Patterns stored in database          │
         │                                       │
         │  Next time similar property appears,  │
         │  agents recall these patterns and     │
         │  make even better decisions!          │
         └───────────────────────────────────────┘
```

---

## 6. API Requirements Flowchart

```
┌─────────────────────────────────────────────────────────┐
│              WHAT APIs DO YOU NEED?                      │
└─────────────────────────┬───────────────────────────────┘
                          │
          ┌───────────────┴────────────────┐
          │                                │
          ▼                                ▼
┌──────────────────────┐      ┌──────────────────────────┐
│  REQUIRED (NEW)      │      │  ALREADY HAVE            │
│                      │      │  (Use as-is)             │
│  LLM API             │      │                          │
│  ├─ Claude OR        │      │  GHL API                 │
│  └─ OpenAI           │      │  ├─ create_opportunity   │
│                      │      │  ├─ send_sms             │
│  Purpose:            │      │  └─ trigger_workflow     │
│  - Agent reasoning   │      │                          │
│  - Decision making   │      │  Database                │
│  - Analysis          │      │  ├─ PostgreSQL           │
│                      │      │  └─ Property queries     │
│  Cost:               │      │                          │
│  $0.01-0.10/decision │      │  All existing modules    │
│                      │      │  become agent TOOLS      │
└──────────────────────┘      └──────────────────────────┘
           │                               │
           └───────────┬───────────────────┘
                       │
                       ▼
           ┌───────────────────────┐
           │   .env FILE           │
           │                       │
           │   # NEW              │
           │   ANTHROPIC_API_KEY   │
           │                       │
           │   # EXISTING          │
           │   GHL_API_KEY         │
           │   GHL_LOCATION_ID     │
           │   DB_PASSWORD         │
           └───────────────────────┘
```

---

## Summary

**The agentic system works in 4 layers:**

1. **Intelligence Layer** (LLM) - Makes decisions
2. **Agent Layer** (Base Agent) - Executes tasks with memory
3. **Coordination Layer** (Coordinator) - Multi-agent communication
4. **Tool Layer** (Your existing code) - Takes actions

**Key Point**: Agents are a smart wrapper around your existing integrations. They decide WHEN and HOW to use what you've already built!
