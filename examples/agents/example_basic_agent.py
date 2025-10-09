#!/usr/bin/env python3
"""
Example 1: Basic Agent Usage
Demonstrates how to create and use a simple intelligent agent
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from agents import LLMClient, BaseAgent, MemoryType
from modules.database import DatabaseManager
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class PropertyEvaluatorAgent(BaseAgent):
    """
    Simple agent that evaluates properties for investment potential
    """

    def __init__(self, llm_client, db_manager):
        super().__init__(
            name="property_evaluator",
            role="Property Investment Evaluator",
            goal="Determine if properties are good investment opportunities",
            llm_client=llm_client,
            db_manager=db_manager
        )

        # Add a tool for the agent to use
        self.add_tool(
            name="calculate_roi",
            function=self._calculate_roi,
            description="Calculate return on investment",
            parameters={
                "purchase_price": "Property purchase price",
                "estimated_value": "Estimated property value after improvements"
            }
        )

    def _calculate_roi(self, purchase_price, estimated_value):
        """Calculate simple ROI"""
        roi = ((estimated_value - purchase_price) / purchase_price) * 100
        return {
            "roi_percentage": round(roi, 2),
            "profit": estimated_value - purchase_price
        }

    def execute_task(self, task):
        """
        Evaluate a property and decide whether to pursue it

        Args:
            task: Dict with property information

        Returns:
            Evaluation result
        """
        property_data = task.get('property')

        print(f"\n{'='*60}")
        print(f"🤖 Agent: {self.name}")
        print(f"📋 Task: Evaluating property at {property_data.get('address')}")
        print(f"{'='*60}\n")

        # Step 1: Calculate ROI using tool
        print("Step 1: Calculating ROI...")
        roi = self.use_tool(
            "calculate_roi",
            purchase_price=property_data.get('list_price'),
            estimated_value=property_data.get('estimated_value', property_data.get('list_price') * 1.15)
        )
        print(f"   ROI: {roi['roi_percentage']}%")
        print(f"   Estimated Profit: ${roi['profit']:,}\n")

        # Step 2: Make decision using LLM
        print("Step 2: Making intelligent decision...")
        decision = self.make_decision(
            context={
                **property_data,
                "roi": roi,
                "agent_goal": self.goal
            },
            question="Should we pursue this property investment?",
            options=["strong_buy", "buy", "hold", "pass"],
            recall_relevant_memories=True
        )

        print(f"   Decision: {decision['decision'].upper()}")
        print(f"   Confidence: {decision['confidence']:.0%}")
        print(f"   Reasoning: {decision['reasoning']}\n")

        # Step 3: Analyze property characteristics
        print("Step 3: Analyzing property characteristics...")
        analysis = self.analyze(
            data=property_data,
            analysis_goal="Identify key investment factors and risks"
        )

        print(f"   Key Insights:")
        for insight in analysis['insights'][:3]:
            print(f"      • {insight}")

        print(f"\n   Recommendations:")
        for rec in analysis['recommendations'][:3]:
            print(f"      • {rec}")

        # Final result
        result = {
            "property": property_data['address'],
            "decision": decision['decision'],
            "confidence": decision['confidence'],
            "roi": roi,
            "insights": analysis['insights'],
            "recommendations": analysis['recommendations']
        }

        print(f"\n{'='*60}")
        print(f"✅ Evaluation complete!")
        print(f"{'='*60}\n")

        return result


def main():
    """Run the example"""

    print("\n" + "="*60)
    print("   DealFinder Pro - Basic Agent Example")
    print("="*60 + "\n")

    # Initialize LLM client
    print("Initializing LLM client...")
    try:
        llm = LLMClient(provider="claude", model="claude-3-5-sonnet-20241022")
        print("✓ LLM client initialized (Claude)\n")
    except Exception as e:
        print(f"⚠ Warning: Could not initialize Claude, trying OpenAI...")
        try:
            llm = LLMClient(provider="openai")
            print("✓ LLM client initialized (OpenAI)\n")
        except Exception as e2:
            print(f"❌ Error: Could not initialize any LLM provider")
            print(f"   Make sure ANTHROPIC_API_KEY or OPENAI_API_KEY is set in .env")
            return

    # Initialize database (optional for this example)
    print("Initializing database...")
    try:
        # Use your existing database config
        db_config = {
            "type": "postgresql",
            "host": os.getenv("DB_HOST", "localhost"),
            "port": int(os.getenv("DB_PORT", 5432)),
            "database": os.getenv("DB_NAME", "dealfinder"),
            "user": os.getenv("DB_USER", "postgres"),
            "password": os.getenv("DB_PASSWORD", "")
        }
        db = DatabaseManager(db_config)
        print("✓ Database connected\n")
    except Exception as e:
        print(f"⚠ Warning: Database not available, agent will work without persistence")
        print(f"   Error: {e}\n")
        db = None

    # Create agent
    print("Creating Property Evaluator Agent...")
    agent = PropertyEvaluatorAgent(llm_client=llm, db_manager=db)
    print(f"✓ Agent created: {agent.name}\n")

    # Test property 1: Good deal
    print("\n" + "="*60)
    print("TEST 1: Evaluating a GOOD DEAL")
    print("="*60)

    test_property_1 = {
        "property": {
            "address": "123 Main Street, Beverly Hills, CA 90210",
            "list_price": 850000,
            "estimated_value": 1100000,
            "bedrooms": 4,
            "bathrooms": 3,
            "square_feet": 2400,
            "days_on_market": 95,
            "price_per_sqft": 354,
            "market_avg_price_per_sqft": 425,
            "below_market_pct": 17,
            "condition": "Needs cosmetic updates",
            "description": "Motivated seller, as-is sale, great location"
        }
    }

    result_1 = agent.execute_task(test_property_1)

    # Test property 2: Risky deal
    print("\n" + "="*60)
    print("TEST 2: Evaluating a RISKY DEAL")
    print("="*60)

    test_property_2 = {
        "property": {
            "address": "456 Oak Avenue, Los Angeles, CA 90001",
            "list_price": 450000,
            "estimated_value": 475000,
            "bedrooms": 2,
            "bathrooms": 1,
            "square_feet": 900,
            "days_on_market": 15,
            "price_per_sqft": 500,
            "market_avg_price_per_sqft": 480,
            "below_market_pct": -4,  # Above market!
            "condition": "Poor, major foundation issues",
            "description": "Needs extensive repairs, sold as-is"
        }
    }

    result_2 = agent.execute_task(test_property_2)

    # Show agent performance
    print("\n" + "="*60)
    print("AGENT PERFORMANCE SUMMARY")
    print("="*60)

    performance = agent.get_performance_summary()
    print(f"\nAgent: {performance['agent_name']}")
    print(f"Role: {performance['role']}")
    print(f"Runtime: {performance['runtime_hours']:.2f} hours")
    print(f"Decisions Made: {performance['decisions_made']}")
    print(f"Tools Used: {performance['tools_used']}")
    print(f"\nMemory Statistics:")
    print(f"   Short-term memories: {performance['memory_stats']['short_term_count']}")
    print(f"   Long-term memories: {performance['memory_stats']['long_term_count']}")

    # Show what the agent learned
    print("\n" + "="*60)
    print("WHAT THE AGENT LEARNED")
    print("="*60 + "\n")

    memories = agent.memory.get_recent_context(limit=5)
    print("Recent experiences:")
    for i, memory in enumerate(memories, 1):
        content = memory['content']
        if 'decision' in content:
            print(f"{i}. Made decision: {content['decision']}")
        elif 'action' in content:
            print(f"{i}. Performed action: {content['action']}")

    print("\n" + "="*60)
    print("Example complete!")
    print("="*60 + "\n")

    print("Next steps:")
    print("1. Try modifying the test properties to see different decisions")
    print("2. Check example_agent_learning.py to see how agents learn from outcomes")
    print("3. Check example_multi_agent.py to see agents working together")
    print()


if __name__ == "__main__":
    main()
