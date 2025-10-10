"""
AI Chat Endpoints
Conversational interface for agent configuration using Claude
"""

from fastapi import APIRouter, HTTPException
from typing import Dict, Any
import logging
import re
import json

from api.models.schemas import (
    ChatRequest,
    ChatResponse,
    AgentCriteriaCreate
)
from modules.ai_agent import AIPropertyAgent
import os

router = APIRouter()
logger = logging.getLogger(__name__)

# Initialize AI agent globally (singleton)
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


@router.post("/", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Chat with AI assistant for property search and agent configuration

    The AI uses the BANT framework to qualify needs and extract criteria.
    When criteria is fully defined, it returns suggested_criteria for review.

    Flow:
    1. User starts conversation
    2. AI asks qualifying questions (BANT framework)
    3. AI extracts criteria from conversation
    4. Returns agent_configured=True with suggested_criteria
    5. Frontend shows visual review card
    6. User approves → calls POST /api/agents
    """
    try:
        ai_agent = get_ai_agent()

        # Build conversation context
        context = request.context or {}

        # Add conversation history if provided
        if request.conversation_history:
            # Restore conversation history to AI agent
            ai_agent.conversation_history = [
                {"role": msg.role, "content": msg.content}
                for msg in request.conversation_history
            ]

        # Get AI response
        response_text = ai_agent.chat(request.message, context=context)

        # Try to detect if AI has configured criteria
        # Look for specific patterns or JSON in response
        agent_configured = False
        suggested_criteria = None

        # Check if response contains configuration intent
        # The AI will naturally say phrases like:
        # - "Based on your requirements, I've configured..."
        # - "Here's what I recommend..."
        # - "Let me set up an agent for you..."

        config_indicators = [
            "i've configured",
            "i've set up",
            "here's the configuration",
            "recommended criteria",
            "agent configuration",
            "search criteria",
            "let me create an agent"
        ]

        response_lower = response_text.lower()
        if any(indicator in response_lower for indicator in config_indicators):
            agent_configured = True

            # Try to extract criteria from conversation
            suggested_criteria = _extract_criteria_from_conversation(
                ai_agent.conversation_history
            )

        # Determine if AI needs more information
        requires_clarification = _needs_clarification(response_text)

        return ChatResponse(
            message=response_text,
            agent_configured=agent_configured,
            suggested_criteria=suggested_criteria,
            requires_clarification=requires_clarification
        )

    except Exception as e:
        logger.error(f"Chat error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/extract-criteria", response_model=AgentCriteriaCreate)
async def extract_criteria(request: ChatRequest):
    """
    Extract agent criteria from conversation history

    Used when frontend detects configuration is ready but AI didn't
    automatically extract it. Returns structured criteria object.
    """
    try:
        # Extract criteria from conversation messages
        criteria = _extract_criteria_from_conversation(
            [{"role": msg.role, "content": msg.content} for msg in request.conversation_history]
        )

        if not criteria:
            raise HTTPException(
                status_code=400,
                detail="Could not extract criteria from conversation"
            )

        return criteria

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Criteria extraction error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/reset")
async def reset_chat():
    """
    Reset chat history

    Clears the conversation and starts fresh.
    """
    try:
        ai_agent = get_ai_agent()
        ai_agent.clear_history()

        return {"message": "Chat history cleared"}

    except Exception as e:
        logger.error(f"Reset error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


# ========================================
# HELPER FUNCTIONS
# ========================================

def _extract_criteria_from_conversation(messages: list) -> AgentCriteriaCreate:
    """
    Extract structured criteria from conversation history

    Looks for mentions of:
    - Price ranges
    - ZIP codes / locations
    - Bedrooms/bathrooms
    - Investment type
    - Timeline
    """
    criteria = {}

    # Combine all message content
    conversation_text = " ".join([
        msg.get("content", "") for msg in messages
        if msg.get("role") == "user"
    ])

    # Extract price range
    price_patterns = [
        r'\$?(\d+)k?\s*(?:-|to)\s*\$?(\d+)k?',  # $500K-$1M or 500-1000
        r'under\s*\$?(\d+)k?',  # under $1M
        r'up\s*to\s*\$?(\d+)k?',  # up to $1M
    ]

    for pattern in price_patterns:
        match = re.search(pattern, conversation_text, re.IGNORECASE)
        if match:
            if len(match.groups()) == 2:
                min_price = int(match.group(1).replace(',', ''))
                max_price = int(match.group(2).replace(',', ''))
                # Convert K to actual numbers
                if min_price < 10000:
                    min_price *= 1000
                if max_price < 10000:
                    max_price *= 1000
                criteria['price_min'] = min_price
                criteria['price_max'] = max_price
            elif 'under' in conversation_text.lower() or 'up to' in conversation_text.lower():
                max_price = int(match.group(1).replace(',', ''))
                if max_price < 10000:
                    max_price *= 1000
                criteria['price_max'] = max_price
            break

    # Extract bedrooms/bathrooms
    bed_match = re.search(r'(\d+)\+?\s*(?:bed|bedroom)', conversation_text, re.IGNORECASE)
    if bed_match:
        criteria['bedrooms_min'] = int(bed_match.group(1))

    bath_match = re.search(r'(\d+(?:\.\d+)?)\+?\s*(?:bath|bathroom)', conversation_text, re.IGNORECASE)
    if bath_match:
        criteria['bathrooms_min'] = float(bath_match.group(1))

    # Extract ZIP codes (more sophisticated pattern)
    zip_pattern = r'\b(\d{5})\b'
    zip_matches = re.findall(zip_pattern, conversation_text)
    if zip_matches:
        criteria['zip_codes'] = list(set(zip_matches))  # Deduplicate

    # Extract locations (cities/neighborhoods) - convert to ZIP codes if possible
    # For now, log these for manual mapping
    location_keywords = ['la jolla', 'pacific beach', 'downtown', 'carmel valley', 'scripps ranch']
    mentioned_locations = [loc for loc in location_keywords if loc in conversation_text.lower()]

    # Map common locations to ZIP codes (San Diego area)
    location_to_zips = {
        'la jolla': ['92037', '92093'],
        'pacific beach': ['92109'],
        'downtown': ['92101'],
        'carmel valley': ['92130'],
        'scripps ranch': ['92131'],
    }

    if mentioned_locations and not criteria.get('zip_codes'):
        zip_codes = []
        for location in mentioned_locations:
            zip_codes.extend(location_to_zips.get(location, []))
        if zip_codes:
            criteria['zip_codes'] = zip_codes

    # Extract investment type
    if 'cash flow' in conversation_text.lower():
        criteria['investment_type'] = 'cash_flow'
    elif 'appreciation' in conversation_text.lower():
        criteria['investment_type'] = 'appreciation'
    elif 'balanced' in conversation_text.lower():
        criteria['investment_type'] = 'balanced'

    # Extract deal quality preference
    deal_qualities = []
    if 'hot deal' in conversation_text.lower() or 'best deal' in conversation_text.lower():
        deal_qualities.append('HOT')
    if 'good deal' in conversation_text.lower():
        deal_qualities.append('GOOD')

    if deal_qualities:
        criteria['deal_quality'] = deal_qualities

    # Set default min_score if not specified
    if 'deal_quality' in criteria or 'investment_type' in criteria:
        criteria['min_score'] = 85  # Higher threshold for investment-focused searches
    else:
        criteria['min_score'] = 80

    # Only return if we have meaningful criteria
    if len(criteria) >= 2:  # At least 2 criteria extracted
        return AgentCriteriaCreate(**criteria)

    return None


def _needs_clarification(response_text: str) -> bool:
    """
    Determine if AI response is asking for clarification

    Returns True if response contains questions
    """
    question_indicators = ['?', 'what', 'which', 'where', 'when', 'how', 'could you']

    response_lower = response_text.lower()
    return any(indicator in response_lower for indicator in question_indicators)
