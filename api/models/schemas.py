"""
Pydantic Models for API Request/Response Schemas
"""

from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


# ========================================
# ENUMS
# ========================================

class AgentStatus(str, Enum):
    ACTIVE = "active"
    PAUSED = "paused"
    CANCELLED = "cancelled"
    COMPLETED = "completed"


class DealQuality(str, Enum):
    HOT = "HOT"
    GOOD = "GOOD"
    FAIR = "FAIR"


class InvestmentType(str, Enum):
    CASH_FLOW = "cash_flow"
    APPRECIATION = "appreciation"
    BALANCED = "balanced"


class MatchStatus(str, Enum):
    NEW = "new"
    SENT = "sent"
    VIEWED = "viewed"
    CONTACTED = "contacted"
    CLOSED = "closed"


# ========================================
# AGENT SCHEMAS
# ========================================

class AgentCriteriaCreate(BaseModel):
    """Search criteria for creating agent"""
    zip_codes: Optional[List[str]] = Field(None, description="Target ZIP codes")
    price_min: Optional[int] = Field(None, ge=0, description="Minimum price")
    price_max: Optional[int] = Field(None, ge=0, description="Maximum price")
    bedrooms_min: Optional[int] = Field(None, ge=0, description="Minimum bedrooms")
    bathrooms_min: Optional[int] = Field(None, ge=0, description="Minimum bathrooms")
    property_types: Optional[List[str]] = Field(None, description="Property types (e.g., Single Family, Condo)")
    deal_quality: Optional[List[DealQuality]] = Field(None, description="Required deal quality levels")
    min_score: Optional[int] = Field(80, ge=0, le=100, description="Minimum opportunity score (0-100)")
    investment_type: Optional[InvestmentType] = Field(None, description="Investment strategy")
    timeline: Optional[str] = Field(None, description="Purchase timeline")

    class Config:
        use_enum_values = True


class ClientCreate(BaseModel):
    """Client creation request"""
    name: str = Field(..., min_length=1, description="Client full name")
    email: Optional[EmailStr] = Field(None, description="Client email")
    phone: Optional[str] = Field(None, description="Client phone")
    notes: Optional[str] = Field(None, description="Additional notes")


class ClientResponse(BaseModel):
    """Client response"""
    client_id: str
    name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    created_at: datetime
    ghl_contact_id: Optional[str] = None


class AgentCreateRequest(BaseModel):
    """Request to create autonomous search agent"""
    client_name: str = Field(..., min_length=1, description="Client name")
    client_email: Optional[EmailStr] = Field(None, description="Client email")
    client_phone: Optional[str] = Field(None, description="Client phone")
    criteria: AgentCriteriaCreate
    notification_email: bool = Field(True, description="Enable email notifications")
    notification_sms: bool = Field(False, description="Enable SMS notifications")
    notification_chat: bool = Field(True, description="Enable in-app notifications")
    ghl_api_key: Optional[str] = Field(None, description="GoHighLevel API key (if user has own account)")
    ghl_location_id: Optional[str] = Field(None, description="GoHighLevel location ID")


class AgentResponse(BaseModel):
    """Agent status response"""
    agent_id: str
    client_name: str
    status: AgentStatus
    created_at: datetime
    last_check: Optional[datetime] = None
    matches_found: int
    new_matches: int
    criteria_summary: str

    class Config:
        use_enum_values = True


class AgentUpdateRequest(BaseModel):
    """Request to update agent"""
    status: Optional[AgentStatus] = None
    notification_email: Optional[bool] = None
    notification_sms: Optional[bool] = None

    class Config:
        use_enum_values = True


# ========================================
# PROPERTY SCHEMAS
# ========================================

class PropertySearchRequest(BaseModel):
    """Property search request"""
    zip_codes: Optional[List[str]] = None
    city: Optional[str] = None
    price_min: Optional[int] = Field(None, ge=0)
    price_max: Optional[int] = Field(None, ge=0)
    bedrooms_min: Optional[int] = Field(None, ge=0)
    bathrooms_min: Optional[int] = Field(None, ge=0)
    min_score: Optional[int] = Field(None, ge=0, le=100)
    deal_quality: Optional[List[DealQuality]] = None
    limit: int = Field(10, ge=1, le=100)
    sort_by: str = Field("opportunity_score", description="Sort field")

    class Config:
        use_enum_values = True


class PropertyDetail(BaseModel):
    """Property details response"""
    address: str
    city: Optional[str] = None
    state: Optional[str] = None
    zip_code: Optional[str] = None
    price: Optional[int] = None
    bedrooms: Optional[int] = None
    bathrooms: Optional[float] = None
    square_feet: Optional[int] = None
    lot_size: Optional[float] = None
    year_built: Optional[int] = None
    property_type: Optional[str] = None
    opportunity_score: Optional[int] = None
    deal_quality: Optional[str] = None
    days_on_market: Optional[int] = None
    price_per_sqft: Optional[float] = None
    tax_assessed_value: Optional[int] = None
    hoa_fee: Optional[int] = None
    listing_url: Optional[str] = None


class PropertySearchResponse(BaseModel):
    """Property search response"""
    total_found: int
    returned: int
    properties: List[PropertyDetail]


class MarketInsightsResponse(BaseModel):
    """Market insights response"""
    location: str
    total_properties: int
    pricing: Dict[str, float]
    opportunity: Dict[str, Any]
    market_dynamics: Dict[str, Any]


# ========================================
# AI CHAT SCHEMAS
# ========================================

class ChatMessage(BaseModel):
    """Single chat message"""
    role: str = Field(..., description="Message role (user or assistant)")
    content: str = Field(..., description="Message content")
    timestamp: Optional[datetime] = None


class ChatRequest(BaseModel):
    """Chat request"""
    message: str = Field(..., min_length=1, description="User message")
    conversation_history: Optional[List[ChatMessage]] = Field(None, description="Previous messages")
    context: Optional[Dict[str, Any]] = Field(None, description="Additional context")


class ChatResponse(BaseModel):
    """Chat response"""
    message: str
    agent_configured: bool = Field(False, description="True if agent configuration detected")
    suggested_criteria: Optional[AgentCriteriaCreate] = Field(None, description="Extracted criteria if configured")
    requires_clarification: bool = Field(False, description="True if AI needs more info")


# ========================================
# MATCH SCHEMAS
# ========================================

class MatchResponse(BaseModel):
    """Property match response"""
    match_id: str
    agent_id: str
    property_address: str
    match_score: int
    match_reasons: List[str]
    property_data: PropertyDetail
    status: MatchStatus
    created_at: datetime
    notified_at: Optional[datetime] = None
    ghl_opportunity_id: Optional[str] = None

    class Config:
        use_enum_values = True


class MatchListResponse(BaseModel):
    """List of matches"""
    agent_id: str
    total_matches: int
    matches: List[MatchResponse]


# ========================================
# SYSTEM SCHEMAS
# ========================================

class SystemStatusResponse(BaseModel):
    """System status response"""
    active_agents: int
    paused_agents: int
    total_matches: int
    new_matches: int
    scheduler_running: bool
    scheduled_jobs: int


class ErrorResponse(BaseModel):
    """Error response"""
    error: str
    detail: Optional[str] = None
    status_code: int
