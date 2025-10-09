"""
GoHighLevel Configuration Example

Copy this file to ghl_config.py and update with your actual GHL credentials and IDs.
DO NOT commit ghl_config.py to version control - add it to .gitignore
"""

# GHL API Credentials
GHL_CONFIG = {
    # API Authentication
    "api_key": "your_ghl_api_key_here",  # Get from GHL Settings > API
    "location_id": "your_location_id_here",  # Get from GHL account

    # Test Mode (set to True to log actions without making actual API calls)
    "test_mode": False,

    # Pipeline Configuration
    "pipeline_id": "your_pipeline_id",  # ID of your opportunities pipeline

    # Pipeline Stages (map stage names to GHL stage IDs)
    "stages": {
        "new_lead": "stage_id_1",           # Initial stage for new properties
        "priority_review": "stage_id_2",     # For hot deals (score >= 90)
        "showing_scheduled": "stage_id_3",   # After showing is scheduled
        "offer_submitted": "stage_id_4",     # Offer has been made
        "under_contract": "stage_id_5",      # Property under contract
        "closed_won": "stage_id_6",          # Deal closed successfully
        "closed_lost": "stage_id_7"          # Deal fell through
    },

    # Workflow IDs (automation workflows in GHL)
    "workflows": {
        "hot_deal_alert": "workflow_id_1",        # Triggered for score >= 90
        "property_match": "workflow_id_2",        # Triggered on buyer match
        "new_opportunity": "workflow_id_3",       # Triggered on new opportunity
        "showing_scheduled": "workflow_id_4"      # Triggered when showing scheduled
    },

    # Default assignee for opportunities and tasks
    "default_assignee": "user_id_here",  # GHL user ID

    # Territory-based assignment (optional)
    "territory_assignment": {
        "austin": "user_id_1",
        "dallas": "user_id_2",
        "houston": "user_id_3",
        "default": "user_id_default"
    },

    # Buyer Matching Configuration
    "buyer_cache_duration_minutes": 60,
    "max_sms_per_buyer_per_day": 3,
    "min_match_score": 70,
    "create_followup_tasks": True,

    # Notification Settings
    "quiet_hours_start": 21,  # 9 PM
    "quiet_hours_end": 8,     # 8 AM
    "sms_char_limit": 160,

    # Rate Limiting (GHL allows 100 req/min, we use 95 to be safe)
    "rate_limit": {
        "max_requests": 95,
        "time_window_seconds": 60
    },

    # Error Handling
    "retry_attempts": 3,
    "retry_backoff_seconds": [1, 2, 4],  # Exponential backoff

    # Logging
    "log_level": "INFO",
    "log_api_requests": True,
    "log_file": "logs/ghl_integration.log"
}


# Custom Field Mapping
# These should match your GHL custom field keys
CUSTOM_FIELDS = {
    # Contact/Buyer Fields
    "buyer": {
        "budget_min": "budget_min",
        "budget_max": "budget_max",
        "location_preference": "location_preference",
        "property_type_preference": "property_type_preference",
        "min_bedrooms": "min_bedrooms",
        "buyer_status": "buyer_status"
    },

    # Opportunity/Property Fields
    "opportunity": {
        "property_address": "property_address",
        "deal_score": "deal_score",
        "list_price": "list_price",
        "est_profit": "est_profit",
        "mls_id": "mls_id",
        "price_per_sqft": "price_per_sqft",
        "below_market_pct": "below_market_pct",
        "days_on_market": "days_on_market",
        "deal_quality": "deal_quality",
        "estimated_arv": "estimated_arv",
        "bedrooms": "bedrooms",
        "bathrooms": "bathrooms",
        "sqft": "sqft",
        "year_built": "year_built",
        "property_type": "property_type"
    }
}


# Tags Configuration
TAGS = {
    "automated": "automated",
    "dealfinder": "dealfinder",
    "hot_deal": "hot_deal",
    "good_deal": "good_deal",
    "potential": "potential",
    "active_buyer": "active_buyer",
    "sms_opt_in": "sms_opt_in",
    "email_opt_in": "email_opt_in"
}


def get_config():
    """Return GHL configuration dictionary"""
    return GHL_CONFIG


def get_custom_fields():
    """Return custom field mapping"""
    return CUSTOM_FIELDS


def get_tags():
    """Return tags configuration"""
    return TAGS


def validate_config():
    """
    Validate that all required configuration values are set

    Returns:
        Tuple[bool, List[str]]: (is_valid, list_of_errors)
    """
    errors = []

    # Check required fields
    if GHL_CONFIG["api_key"] == "your_ghl_api_key_here":
        errors.append("API key not configured")

    if GHL_CONFIG["location_id"] == "your_location_id_here":
        errors.append("Location ID not configured")

    if GHL_CONFIG["pipeline_id"] == "your_pipeline_id":
        errors.append("Pipeline ID not configured")

    # Check stage IDs
    for stage_name, stage_id in GHL_CONFIG["stages"].items():
        if stage_id.startswith("stage_id_"):
            errors.append(f"Stage '{stage_name}' ID not configured")

    # Check workflow IDs
    for workflow_name, workflow_id in GHL_CONFIG["workflows"].items():
        if workflow_id.startswith("workflow_id_"):
            errors.append(f"Workflow '{workflow_name}' ID not configured")

    is_valid = len(errors) == 0
    return is_valid, errors


if __name__ == "__main__":
    # Validate configuration when run directly
    is_valid, errors = validate_config()

    if is_valid:
        print("✓ GHL configuration is valid")
    else:
        print("✗ GHL configuration has errors:")
        for error in errors:
            print(f"  - {error}")
