"""
Property Search Endpoints
Manual property search and market insights
"""

from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
import logging

from api.models.schemas import (
    PropertySearchRequest,
    PropertySearchResponse,
    PropertyDetail,
    MarketInsightsResponse
)
from modules.ai_agent import AIPropertyAgent
import os

router = APIRouter()
logger = logging.getLogger(__name__)

# Initialize AI agent for property search functions
_ai_agent = None


def get_ai_agent() -> AIPropertyAgent:
    """Get or create AI agent singleton"""
    global _ai_agent
    if _ai_agent is None:
        api_key = os.getenv('ANTHROPIC_API_KEY')
        if not api_key:
            raise HTTPException(
                status_code=500,
                detail="ANTHROPIC_API_KEY not configured"
            )
        _ai_agent = AIPropertyAgent(api_key=api_key)
    return _ai_agent


@router.post("/search", response_model=PropertySearchResponse)
async def search_properties(request: PropertySearchRequest):
    """
    Search properties with filters

    Returns properties matching the specified criteria.
    Useful for manual browsing or preview before creating agent.
    """
    try:
        ai_agent = get_ai_agent()

        # Build filters dictionary
        filters = {}

        if request.price_min is not None:
            filters['min_price'] = request.price_min
        if request.price_max is not None:
            filters['max_price'] = request.price_max
        if request.city:
            filters['city'] = request.city
        if request.bedrooms_min is not None:
            filters['bedrooms'] = request.bedrooms_min
        if request.min_score is not None:
            filters['min_score'] = request.min_score

        # Execute search using AI agent's tool
        search_params = {
            "query": f"Search properties",
            "filters": filters,
            "limit": request.limit,
            "sort_by": request.sort_by
        }

        result = ai_agent._tool_search_properties(search_params)

        # Convert to PropertyDetail models
        properties = [
            PropertyDetail(
                address=prop.get('address', ''),
                city=prop.get('city'),
                state=prop.get('state'),
                zip_code=prop.get('zip_code'),
                price=prop.get('price'),
                bedrooms=prop.get('bedrooms'),
                bathrooms=prop.get('bathrooms'),
                square_feet=prop.get('sqft'),
                year_built=prop.get('year_built'),
                property_type=prop.get('property_type'),
                opportunity_score=prop.get('score'),
                deal_quality=prop.get('quality'),
                days_on_market=prop.get('days_on_market'),
                price_per_sqft=prop.get('price_per_sqft'),
                hoa_fee=prop.get('hoa_fee'),
                listing_url=prop.get('listing_url')
            )
            for prop in result.get('properties', [])
        ]

        return PropertySearchResponse(
            total_found=result.get('total_found', 0),
            returned=len(properties),
            properties=properties
        )

    except Exception as e:
        logger.error(f"Property search error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats", response_model=MarketInsightsResponse)
async def get_market_stats(
    location: Optional[str] = Query(None, description="City or area name")
):
    """
    Get market statistics and insights

    Returns pricing, inventory, and trend data for specified location
    or overall market.
    """
    try:
        ai_agent = get_ai_agent()

        # Get market insights using AI agent's tool
        params = {}
        if location:
            params['location'] = location

        result = ai_agent._tool_market_insights(params)

        return MarketInsightsResponse(
            location=result.get('location', 'All markets'),
            total_properties=result.get('total_properties', 0),
            pricing=result.get('pricing', {}),
            opportunity=result.get('opportunity', {}),
            market_dynamics=result.get('market_dynamics', {})
        )

    except Exception as e:
        logger.error(f"Market stats error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{property_address}", response_model=PropertyDetail)
async def get_property_details(property_address: str):
    """
    Get detailed information about specific property

    Returns full property details with opportunity score and insights.
    """
    try:
        ai_agent = get_ai_agent()

        # Analyze property using AI agent's tool
        params = {
            "property_address": property_address,
            "analysis_type": "full"
        }

        result = ai_agent._tool_analyze_property(params)

        if 'error' in result:
            raise HTTPException(status_code=404, detail=result['error'])

        prop = result.get('property', {})

        return PropertyDetail(
            address=prop.get('address', ''),
            city=prop.get('city'),
            state=prop.get('state'),
            zip_code=prop.get('zip_code'),
            price=prop.get('price'),
            bedrooms=prop.get('bedrooms'),
            bathrooms=prop.get('bathrooms'),
            square_feet=prop.get('sqft'),
            year_built=prop.get('year_built'),
            property_type=prop.get('property_type'),
            opportunity_score=prop.get('score'),
            deal_quality=prop.get('quality'),
            days_on_market=prop.get('days_on_market'),
            price_per_sqft=prop.get('price_per_sqft'),
            tax_assessed_value=prop.get('tax_assessed'),
            hoa_fee=prop.get('hoa_fee')
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Property details error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/hot-deals/list", response_model=PropertySearchResponse)
async def get_hot_deals(
    limit: int = Query(10, ge=1, le=50, description="Number of properties to return")
):
    """
    Get hottest deals currently available

    Returns properties with opportunity score >= 90 (HOT deals)
    """
    try:
        # Search for hot deals
        request = PropertySearchRequest(
            min_score=90,
            limit=limit,
            sort_by="opportunity_score"
        )

        return await search_properties(request)

    except Exception as e:
        logger.error(f"Hot deals error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
