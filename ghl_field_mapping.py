"""
GHL Custom Field Mapping
Maps our property data to actual GHL field keys
"""

# Opportunity (Property) Custom Fields
# Based on actual GHL field keys from the new sub-account
OPPORTUNITY_FIELD_MAPPING = {
    "deal_score": "dealscore",
    "property_address": "propertyaddress",
    "list_price": "list_price",
    "est_profit": "estprofit",
    "mls_id": "mls_id",
    "price_per_sqft": "price_per_sqft",
    "below_market_pct": "below_market_pct",
    "days_on_market": "days_on_market",  # Assuming this follows same pattern
    "deal_quality": "deal_quality",      # Assuming this follows same pattern
    "estimated_arv": "estimated_arv"     # Assuming this follows same pattern
}

def map_property_to_ghl(property_data):
    """
    Convert property data to GHL opportunity format with correct field keys

    Args:
        property_data: Dict with property information

    Returns:
        Dict formatted for GHL opportunity creation
    """
    custom_fields = {}

    # Map each field using the correct GHL field key
    field_mappings = {
        "deal_score": "dealscore",
        "address": "propertyaddress",
        "list_price": "list_price",
        "estimated_profit": "estprofit",
        "mls_id": "mls_id",
        "price_per_sqft": "price_per_sqft",
        "below_market_pct": "below_market_pct",
        "days_on_market": "days_on_market",
        "deal_quality": "deal_quality",
        "estimated_arv": "estimated_arv"
    }

    for source_key, ghl_key in field_mappings.items():
        if source_key in property_data:
            custom_fields[ghl_key] = property_data[source_key]

    return custom_fields


def create_opportunity_payload(property_data, pipeline_id, location_id, stage_id=None):
    """
    Create complete GHL opportunity payload ready for API submission

    Args:
        property_data: Dict with property information
        pipeline_id: GHL pipeline ID
        location_id: GHL location ID
        stage_id: Optional - GHL stage ID (if None, GHL auto-assigns to first stage)

    Returns:
        Complete opportunity payload dict
    """
    # Map custom fields
    custom_fields = map_property_to_ghl(property_data)

    # Build opportunity name
    address = property_data.get('address', property_data.get('property_address', 'Unknown Address'))
    deal_score = property_data.get('deal_score', 0)
    name = f"🏠 {address} - Score: {deal_score}"

    # Build payload
    payload = {
        "locationId": location_id,
        "pipelineId": pipeline_id,
        "name": name,
        "monetaryValue": property_data.get('list_price', 0),
        "status": "open",
        "customFields": custom_fields
    }

    # Add stage ID if provided
    if stage_id:
        payload["pipelineStageId"] = stage_id
    # Otherwise GHL will auto-assign to first stage

    return payload


# Contact (Buyer) Custom Fields
# These will be created similarly
CONTACT_FIELD_MAPPING = {
    "budget_min": "budget_min",
    "budget_max": "budget_max",
    "location_preference": "location_preference",
    "property_type_preference": "property_type_preference",
    "min_bedrooms": "min_bedrooms",
    "buyer_status": "buyer_status"
}
