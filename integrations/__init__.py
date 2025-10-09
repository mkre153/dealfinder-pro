"""
GoHighLevel Integration Module

Provides complete API integration with GoHighLevel CRM including:
- Rate-limited API connector
- Workflow automation and opportunity management
- Intelligent buyer-property matching
- Automated notifications (SMS, Email, Workflows)

Usage:
    from integrations import GoHighLevelConnector, GHLWorkflowManager, BuyerMatcher

    # Initialize connector
    ghl = GoHighLevelConnector(api_key="your_key", location_id="your_location")

    # Test connection
    if ghl.test_connection():
        print("Connected to GHL successfully")

    # Initialize workflow manager
    config = {
        "pipeline_id": "pipeline_123",
        "stages": {
            "new_lead": "stage_1",
            "priority_review": "stage_2"
        },
        "workflows": {
            "hot_deal_alert": "workflow_123"
        }
    }
    workflow_mgr = GHLWorkflowManager(ghl, config)

    # Create opportunity from property
    property_data = {
        "address": "123 Main St",
        "deal_score": 95,
        "list_price": 250000,
        "estimated_profit": 75000
    }
    opp_id = workflow_mgr.create_opportunity_from_property(property_data)

    # Match buyers to property
    matcher = BuyerMatcher(ghl, db_manager, config)
    matches = matcher.match_property_to_buyers(property_data)
    matcher.notify_matched_buyers(property_data, matches)
"""

from .ghl_connector import (
    GoHighLevelConnector,
    GHLRateLimiter,
    GHLAPIError
)
from .ghl_workflows import GHLWorkflowManager
from .ghl_buyer_matcher import BuyerMatcher

__all__ = [
    'GoHighLevelConnector',
    'GHLRateLimiter',
    'GHLAPIError',
    'GHLWorkflowManager',
    'BuyerMatcher'
]

__version__ = '1.0.0'
