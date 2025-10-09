#!/usr/bin/env python3
"""
Simple Agent Test - No Database or Scraper Dependencies
Shows AI-powered decision making in action
"""

import sys
import os

# Add current directory to path
sys.path.insert(0, os.getcwd())

# Manually load .env
env_path = os.path.join(os.getcwd(), '.env')
if os.path.exists(env_path):
    with open(env_path) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                os.environ[key.strip()] = value.strip()

from agents.llm_client import LLMClient

print("\n" + "=" * 70)
print("  🤖 INTELLIGENT AGENT DEMONSTRATION")
print("=" * 70)
print("\nThis shows how AI agents make intelligent decisions using Claude.\n")

# Initialize LLM
print("Initializing Claude AI...")
llm = LLMClient(provider="claude")
print(f"✓ Connected to {llm.model}\n")

# Test 1: Property Evaluation Decision
print("=" * 70)
print("TEST 1: Property Investment Decision")
print("=" * 70)
print("\nScenario: Agent evaluates a property deal\n")

property_data = {
    "address": "123 Investment Ave, Beverly Hills, CA 90210",
    "list_price": 850000,
    "estimated_value": 1050000,
    "rental_income": 4500,
    "days_on_market": 87,
    "condition": "Needs minor repairs",
    "neighborhood_rating": 8.5,
    "school_rating": 9.0,
    "price_reduction": 50000,
    "seller_motivation": "Estate sale - motivated seller"
}

print("Property Details:")
for key, value in property_data.items():
    print(f"  • {key.replace('_', ' ').title()}: {value}")

print("\n🤖 Agent is analyzing and making a decision...\n")

# Agent makes decision
decision = llm.make_decision(
    context=property_data,
    question="Should we pursue this investment property?",
    options=[
        "strong_buy - Make immediate offer",
        "buy - Worth pursuing but negotiate",
        "maybe - Need more information",
        "pass - Not a good fit"
    ],
    agent_role="Real Estate Investment Analyst"
)

print("─" * 70)
print("AGENT DECISION RESULTS")
print("─" * 70)
print(f"\n✅ Decision: {decision['decision']}")
print(f"🎯 Confidence: {decision['confidence']:.0%}")
print(f"\n💭 Reasoning:")
print(f"   {decision['reasoning']}\n")

if 'considerations' in decision:
    print("🔍 Key Considerations:")
    for consideration in decision['considerations']:
        print(f"   • {consideration}")

# Test 2: Market Analysis
print("\n\n" + "=" * 70)
print("TEST 2: Market Trend Analysis")
print("=" * 70)
print("\nScenario: Agent analyzes market data\n")

market_data = {
    "zip_code": "90210",
    "average_price": 1200000,
    "median_days_on_market": 45,
    "price_trend_6mo": "+8%",
    "inventory_level": "Low (2.1 months)",
    "recent_sales": [
        {"address": "456 Elm St", "price": 1150000, "days": 32},
        {"address": "789 Oak Ave", "price": 1300000, "days": 18},
        {"address": "321 Pine Dr", "price": 980000, "days": 67}
    ],
    "pending_listings": 12,
    "active_listings": 28
}

print("Market Data:")
print(f"  • ZIP Code: {market_data['zip_code']}")
print(f"  • Average Price: ${market_data['average_price']:,}")
print(f"  • Median Days on Market: {market_data['median_days_on_market']}")
print(f"  • 6-Month Trend: {market_data['price_trend_6mo']}")
print(f"  • Inventory: {market_data['inventory_level']}")
print(f"  • Recent Sales: {len(market_data['recent_sales'])} properties")

print("\n🤖 Agent is analyzing market patterns...\n")

# Agent analyzes data
analysis = llm.analyze_data(
    data=market_data,
    analysis_goal="Identify investment opportunities and market trends",
    agent_role="Market Research Analyst"
)

print("─" * 70)
print("AGENT ANALYSIS RESULTS")
print("─" * 70)

print(f"\n🎯 Analysis Confidence: {analysis['confidence']:.0%}\n")

print("💡 Key Insights:")
for i, insight in enumerate(analysis['insights'], 1):
    print(f"   {i}. {insight}")

print("\n📊 Patterns Identified:")
for i, pattern in enumerate(analysis['patterns'], 1):
    print(f"   {i}. {pattern}")

print("\n🎯 Recommendations:")
for i, rec in enumerate(analysis['recommendations'], 1):
    print(f"   {i}. {rec}")

# Test 3: Buyer Communication
print("\n\n" + "=" * 70)
print("TEST 3: Personalized Buyer Message")
print("=" * 70)
print("\nScenario: Agent creates personalized message for buyer\n")

buyer_profile = {
    "name": "Sarah Johnson",
    "budget_max": 950000,
    "location_preference": "Beverly Hills, West Hollywood",
    "property_type": "Single Family",
    "min_bedrooms": 3,
    "priorities": ["Good schools", "Low maintenance", "Modern kitchen"],
    "past_views": 5,
    "engagement_level": "High - responded to 4/5 listings"
}

matched_property = {
    "address": "456 Sunset Blvd, Beverly Hills",
    "price": 895000,
    "bedrooms": 4,
    "bathrooms": 3,
    "sqft": 2400,
    "school_rating": 9,
    "features": ["Renovated kitchen 2023", "New HVAC", "Low HOA"],
    "deal_score": 88
}

print("Buyer Profile:")
print(f"  • Name: {buyer_profile['name']}")
print(f"  • Budget: Up to ${buyer_profile['budget_max']:,}")
print(f"  • Looking for: {buyer_profile['property_type']}")
print(f"  • Priorities: {', '.join(buyer_profile['priorities'])}")
print(f"  • Engagement: {buyer_profile['engagement_level']}")

print("\nMatched Property:")
print(f"  • Address: {matched_property['address']}")
print(f"  • Price: ${matched_property['price']:,}")
print(f"  • Size: {matched_property['bedrooms']} bed, {matched_property['bathrooms']} bath, {matched_property['sqft']:,} sqft")
print(f"  • Deal Score: {matched_property['deal_score']}/100")

print("\n🤖 Agent is crafting personalized message...\n")

# Agent generates message
message = llm.generate_message(
    recipient_context={
        "buyer": buyer_profile,
        "property": matched_property
    },
    message_goal="Notify buyer about perfectly matched property and encourage immediate viewing",
    tone="professional but enthusiastic"
)

print("─" * 70)
print("AGENT-GENERATED MESSAGE")
print("─" * 70)
print(f"\n{message}\n")

# Summary
print("\n" + "=" * 70)
print("  ✅ DEMONSTRATION COMPLETE")
print("=" * 70)

print("\n🎉 What You Just Saw:\n")
print("1. ✅ Agent made intelligent investment decision")
print("   → Analyzed property details")
print("   → Provided reasoning and confidence level")
print("   → Identified key considerations")

print("\n2. ✅ Agent analyzed market data")
print("   → Identified patterns and trends")
print("   → Generated actionable insights")
print("   → Provided specific recommendations")

print("\n3. ✅ Agent created personalized communication")
print("   → Tailored message to buyer's preferences")
print("   → Highlighted relevant property features")
print("   → Professional and compelling copy")

print("\n" + "=" * 70)
print("  🧠 HOW THIS WORKS")
print("=" * 70)

print("\nThe agent uses Claude AI (Anthropic) to:")
print("  • Understand context and nuance")
print("  • Make data-driven decisions")
print("  • Explain its reasoning")
print("  • Learn patterns from data")
print("  • Generate human-quality text")

print("\n💡 In production, agents can:")
print("  • Automatically evaluate 100s of properties daily")
print("  • Create GHL opportunities for good deals")
print("  • Match properties to buyers instantly")
print("  • Send personalized messages at scale")
print("  • Learn from which decisions lead to closings")

print("\n" + "=" * 70)
print("  NEXT STEPS")
print("=" * 70)

print("\n1. Finish GHL Setup (~30 min)")
print("   → Create custom fields")
print("   → Set up pipeline")
print("   → See agents create opportunities automatically")

print("\n2. Test GHL Integration")
print("   → python examples/agents/agent_ghl_integration.py")
print("   → Watch agent create real opportunity in GHL")

print("\n3. Build Custom Agents")
print("   → Market Analyst Agent")
print("   → Deal Hunter Agent")
print("   → Buyer Matchmaker Agent")

print("\n📚 Documentation:")
print("   → YOUR_SETUP_STATUS.md (your progress)")
print("   → AGENT_SYSTEM_GUIDE.md (complete tutorial)")
print("   → SETUP_COMPLETE_SUMMARY.md (overview)")

print("\n" + "=" * 70)
print("  🚀 Claude AI is working perfectly!")
print("  Ready to build intelligent real estate automation!")
print("=" * 70 + "\n")
