#!/usr/bin/env python3
"""
Example: Agent with GoHighLevel Integration
Shows how agents use your existing GHL API to make intelligent decisions
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from agents import LLMClient, BaseAgent, MemoryType
from integrations.ghl_connector import GoHighLevelConnector
from modules.database import DatabaseManager
from dotenv import load_dotenv
import json

load_dotenv()


class GHLIntelligentAgent(BaseAgent):
    """
    Agent that intelligently manages GoHighLevel opportunities

    Uses YOUR existing GHL API - no new setup needed!
    """

    def __init__(self, llm_client, db_manager, ghl_connector):
        super().__init__(
            name="ghl_intelligent_agent",
            role="GHL Integration Specialist",
            goal="Intelligently create and manage GHL opportunities for maximum conversion",
            llm_client=llm_client,
            db_manager=db_manager
        )

        self.ghl = ghl_connector

        # Add GHL functions as agent tools
        self._setup_ghl_tools()

    def _setup_ghl_tools(self):
        """Register GHL functions as tools the agent can use"""

        # Tool 1: Create opportunity
        self.add_tool(
            name="create_ghl_opportunity",
            function=self.ghl.create_opportunity,
            description="Create opportunity in GoHighLevel CRM",
            parameters={"opportunity_data": "Property and deal information"}
        )

        # Tool 2: Send SMS (if GHL supports it)
        if hasattr(self.ghl, 'send_sms'):
            self.add_tool(
                name="send_sms",
                function=self.ghl.send_sms,
                description="Send SMS via GoHighLevel",
                parameters={"contact_id": "Contact ID", "message": "Message text"}
            )

        # Tool 3: Trigger workflow (if GHL supports it)
        if hasattr(self.ghl, 'trigger_workflow'):
            self.add_tool(
                name="trigger_workflow",
                function=self.ghl.trigger_workflow,
                description="Trigger GHL workflow",
                parameters={"workflow_id": "Workflow ID", "contact_id": "Contact ID"}
            )

    def execute_task(self, task):
        """
        Intelligently handle GHL operations

        Args:
            task: Dict with 'type' and 'data'
                  type: 'evaluate_property', 'create_opportunity', 'match_buyer'
                  data: Property or buyer information

        Returns:
            Task execution result
        """
        task_type = task.get('type')

        print(f"\n{'='*60}")
        print(f"🤖 GHL Agent: {self.name}")
        print(f"📋 Task: {task_type}")
        print(f"{'='*60}\n")

        if task_type == 'evaluate_property':
            return self._evaluate_for_ghl(task['data'])

        elif task_type == 'create_opportunity':
            return self._create_smart_opportunity(task['data'])

        elif task_type == 'match_buyer':
            return self._match_to_buyer(task['data'])

        else:
            return {"error": f"Unknown task type: {task_type}"}

    def _evaluate_for_ghl(self, property_data):
        """
        Agent evaluates whether to create GHL opportunity

        Args:
            property_data: Property information

        Returns:
            Evaluation result with recommendation
        """
        print("Step 1: Agent evaluating property for GHL...")

        # Agent makes intelligent decision
        decision = self.make_decision(
            context={
                "property": property_data,
                "ghl_pipeline_capacity": "current_opportunities_count",  # Could query GHL
                "market_conditions": "current_market_state"
            },
            question="Should I create a GHL opportunity for this property?",
            options=[
                "yes - hot_lead (score 90+, immediate action)",
                "yes - regular_lead (score 75-89, standard follow-up)",
                "no - not_qualified (score <75, skip)"
            ]
        )

        print(f"   Decision: {decision['decision']}")
        print(f"   Confidence: {decision['confidence']:.0%}")
        print(f"   Reasoning: {decision['reasoning']}\n")

        return {
            "should_create": "yes" in decision['decision'],
            "stage": "hot_lead" if "hot" in decision['decision'] else "regular_lead",
            "confidence": decision['confidence'],
            "reasoning": decision['reasoning']
        }

    def _create_smart_opportunity(self, property_data):
        """
        Agent creates GHL opportunity with intelligent field mapping

        Args:
            property_data: Property information

        Returns:
            Creation result
        """
        print("Step 2: Agent creating GHL opportunity...")

        # First, decide which stage to use
        stage_decision = self.make_decision(
            context=property_data,
            question="Which GHL pipeline stage is most appropriate?",
            options=["new_lead", "hot_lead", "priority_review"]
        )

        print(f"   Chosen Stage: {stage_decision['decision']}")
        print(f"   Reason: {stage_decision['reasoning']}\n")

        # Prepare opportunity data
        opportunity_data = {
            "name": f"{property_data.get('address', 'Unknown')} - Score: {property_data.get('deal_score', 0)}",
            "monetaryValue": property_data.get('list_price', 0),
            "pipelineId": os.getenv('GHL_PIPELINE_ID', 'YOUR_PIPELINE_ID'),
            "pipelineStageId": self._get_stage_id(stage_decision['decision']),
            "status": "open",
            "customFields": {
                "property_address": property_data.get('address'),
                "deal_score": property_data.get('deal_score', 0),
                "list_price": property_data.get('list_price', 0),
                "est_profit": property_data.get('estimated_profit', 0),
                "mls_id": property_data.get('mls_id', 'N/A'),
                "price_per_sqft": property_data.get('price_per_sqft', 0),
                "below_market_pct": property_data.get('below_market_pct', 0),
                "days_on_market": property_data.get('days_on_market', 0),
                "deal_quality": property_data.get('deal_quality', 'GOOD'),
                "estimated_arv": property_data.get('estimated_arv', 0)
            }
        }

        # Use tool to create opportunity
        print("   Creating opportunity in GHL...")
        try:
            result = self.use_tool("create_ghl_opportunity", opportunity_data=opportunity_data)

            print(f"   ✅ Success! Opportunity ID: {result.get('id', 'N/A')}\n")

            # Store success in memory
            self.memory.store(
                content={
                    "action": "created_ghl_opportunity",
                    "property": property_data.get('address'),
                    "stage": stage_decision['decision'],
                    "opportunity_id": result.get('id'),
                    "success": True
                },
                memory_type=MemoryType.EPISODIC,
                importance=0.8
            )

            return {
                "success": True,
                "opportunity_id": result.get('id'),
                "stage": stage_decision['decision']
            }

        except Exception as e:
            print(f"   ❌ Failed: {e}\n")
            return {
                "success": False,
                "error": str(e)
            }

    def _match_to_buyer(self, data):
        """
        Agent matches property to buyer and decides outreach strategy

        Args:
            data: Dict with 'property' and 'buyer'

        Returns:
            Match result with recommended action
        """
        print("Step 3: Agent matching property to buyer...")

        property_data = data['property']
        buyer = data['buyer']

        # Agent analyzes match quality
        match_analysis = self.analyze(
            data={
                "property": property_data,
                "buyer_preferences": buyer,
                "buyer_history": buyer.get('past_interactions', [])
            },
            analysis_goal="Determine match quality and best outreach strategy"
        )

        print(f"   Match Insights:")
        for insight in match_analysis['insights'][:3]:
            print(f"      • {insight}")

        # Agent decides contact strategy
        contact_decision = self.make_decision(
            context={
                "match_analysis": match_analysis,
                "buyer_response_history": buyer.get('response_rate', 'unknown'),
                "time_of_day": "morning"  # Could get actual time
            },
            question="What's the best way to contact this buyer?",
            options=["sms_now", "email_now", "schedule_morning", "skip"]
        )

        print(f"\n   Contact Strategy: {contact_decision['decision']}")
        print(f"   Reasoning: {contact_decision['reasoning']}\n")

        return {
            "match_quality": match_analysis.get('confidence', 0),
            "insights": match_analysis['insights'],
            "contact_strategy": contact_decision['decision'],
            "contact_reasoning": contact_decision['reasoning']
        }

    def _get_stage_id(self, stage_name):
        """Map stage name to GHL stage ID"""
        stage_mapping = {
            "new_lead": os.getenv('GHL_STAGE_NEW', 'STAGE_ID_NEW'),
            "hot_lead": os.getenv('GHL_STAGE_HOT', 'STAGE_ID_HOT'),
            "priority_review": os.getenv('GHL_STAGE_PRIORITY', 'STAGE_ID_PRIORITY')
        }
        return stage_mapping.get(stage_name, stage_mapping['new_lead'])


def main():
    """Demo: Agent using GHL integration"""

    print("\n" + "="*60)
    print("   GHL Intelligent Agent Demo")
    print("="*60 + "\n")

    # Initialize LLM
    print("Initializing AI...")
    try:
        llm = LLMClient(provider="claude")
        print("✓ LLM initialized\n")
    except Exception as e:
        print(f"❌ Error: {e}")
        print("Make sure ANTHROPIC_API_KEY is set in .env")
        return

    # Initialize database
    print("Connecting to database...")
    try:
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
        print(f"⚠ Warning: Database not available: {e}\n")
        db = None

    # Initialize GHL connector (YOUR EXISTING INTEGRATION)
    print("Connecting to GoHighLevel...")
    try:
        ghl = GoHighLevelConnector(
            api_key=os.getenv('GHL_API_KEY'),
            location_id=os.getenv('GHL_LOCATION_ID')
        )
        print("✓ GHL connected\n")
    except Exception as e:
        print(f"❌ Error: {e}")
        print("Make sure GHL_API_KEY and GHL_LOCATION_ID are set in .env")
        print("\nYou can still run the demo - agent will make decisions without executing GHL actions.\n")
        ghl = None

    # Create agent
    print("Creating GHL Intelligent Agent...")
    agent = GHLIntelligentAgent(llm, db, ghl) if ghl else None

    if not agent:
        print("❌ Cannot create agent without GHL connection")
        return

    print(f"✓ Agent created: {agent.name}\n")

    # Test 1: Evaluate property
    print("\n" + "="*60)
    print("TEST 1: Should we create GHL opportunity?")
    print("="*60)

    test_property = {
        "address": "123 Sunset Blvd, Beverly Hills, CA 90210",
        "list_price": 1250000,
        "deal_score": 92,
        "estimated_profit": 185000,
        "mls_id": "MLS-2024-1234",
        "price_per_sqft": 425,
        "below_market_pct": 18,
        "days_on_market": 95,
        "deal_quality": "HOT DEAL",
        "estimated_arv": 1500000
    }

    evaluation = agent.execute_task({
        "type": "evaluate_property",
        "data": test_property
    })

    # Test 2: Create opportunity (if agent recommends)
    if evaluation.get('should_create'):
        print("\n" + "="*60)
        print("TEST 2: Creating GHL Opportunity")
        print("="*60)

        creation_result = agent.execute_task({
            "type": "create_opportunity",
            "data": test_property
        })

    # Test 3: Match to buyer
    print("\n" + "="*60)
    print("TEST 3: Matching to Buyer")
    print("="*60)

    test_buyer = {
        "id": "buyer_123",
        "name": "John Smith",
        "budget_min": 1000000,
        "budget_max": 1500000,
        "location_preference": "Beverly Hills, Bel Air",
        "property_type_preference": "Single Family",
        "response_rate": "high",
        "past_interactions": ["viewed 3 properties", "made 1 offer"]
    }

    match_result = agent.execute_task({
        "type": "match_buyer",
        "data": {
            "property": test_property,
            "buyer": test_buyer
        }
    })

    # Show agent performance
    print("\n" + "="*60)
    print("AGENT PERFORMANCE")
    print("="*60)

    performance = agent.get_performance_summary()
    print(f"\nDecisions Made: {performance['decisions_made']}")
    print(f"Tools Used: {performance['tools_used']}")
    print(f"Success Rate: {performance['success_rate']:.0%}")
    print(f"Memory Stats: {performance['memory_stats']['short_term_count']} short-term, {performance['memory_stats']['long_term_count']} long-term")

    print("\n" + "="*60)
    print("Demo complete!")
    print("="*60 + "\n")

    print("Agent used YOUR existing GHL API to:")
    print("✓ Make intelligent decisions about opportunity creation")
    print("✓ Choose appropriate pipeline stages")
    print("✓ Match properties to buyers")
    print("✓ Recommend contact strategies")
    print("\nNo new API setup required - agents enhance what you already have!")


if __name__ == "__main__":
    main()
