"""
Agent CRUD Endpoints
Manages autonomous property search agents
"""

from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
import logging

from api.models.schemas import (
    AgentCreateRequest,
    AgentResponse,
    AgentUpdateRequest,
    MatchListResponse,
    MatchResponse,
    AgentStatus,
    MatchStatus,
    SystemStatusResponse
)
from modules.agent_manager import get_agent_manager
from modules.client_db import get_db

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/", response_model=AgentResponse, status_code=201)
async def create_agent(request: AgentCreateRequest):
    """
    Create new autonomous search agent

    This creates a client profile and autonomous agent that monitors
    properties 24/7 and sends matches to GoHighLevel.

    The agent runs perpetually every 4 hours until paused or cancelled.
    """
    try:
        db = get_db()
        agent_manager = get_agent_manager()

        # Create client first
        client_id = db.create_client(
            name=request.client_name,
            email=request.client_email,
            phone=request.client_phone,
            notes=f"Created via API - Investment type: {request.criteria.investment_type}"
        )

        logger.info(f"Created client {client_id} for {request.client_name}")

        # Build criteria dictionary
        criteria = request.criteria.dict(exclude_none=True)

        # Create agent
        agent_id = agent_manager.create_agent(
            client_id=client_id,
            criteria=criteria,
            notification_email=request.notification_email,
            notification_sms=request.notification_sms,
            notification_chat=request.notification_chat
        )

        logger.info(f"Created agent {agent_id} for client {client_id}")

        # Get agent status for response
        status = agent_manager.get_agent_status(agent_id)

        return AgentResponse(**status)

    except Exception as e:
        logger.error(f"Failed to create agent: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/", response_model=List[AgentResponse])
async def list_agents(
    status: Optional[AgentStatus] = Query(None, description="Filter by status"),
    client_id: Optional[str] = Query(None, description="Filter by client ID")
):
    """
    List all agents with optional filters

    Returns all agents accessible to the authenticated user.
    """
    try:
        agent_manager = get_agent_manager()

        # Get all active agents (can extend to support other statuses)
        agents = agent_manager.list_active_agents(client_id=client_id)

        # Filter by status if provided
        if status:
            agents = [a for a in agents if a.get('status') == status.value]

        return [AgentResponse(**agent) for agent in agents]

    except Exception as e:
        logger.error(f"Failed to list agents: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{agent_id}", response_model=AgentResponse)
async def get_agent(agent_id: str):
    """
    Get detailed status of specific agent

    Returns current status, match count, and criteria summary.
    """
    try:
        agent_manager = get_agent_manager()

        status = agent_manager.get_agent_status(agent_id)

        if not status:
            raise HTTPException(status_code=404, detail=f"Agent {agent_id} not found")

        return AgentResponse(**status)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get agent {agent_id}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.patch("/{agent_id}", response_model=AgentResponse)
async def update_agent(agent_id: str, request: AgentUpdateRequest):
    """
    Update agent status or settings

    Can pause/resume/cancel agents or update notification preferences.
    """
    try:
        agent_manager = get_agent_manager()

        # Verify agent exists
        status = agent_manager.get_agent_status(agent_id)
        if not status:
            raise HTTPException(status_code=404, detail=f"Agent {agent_id} not found")

        # Update status if provided
        if request.status:
            if request.status == AgentStatus.PAUSED:
                agent_manager.pause_agent(agent_id)
            elif request.status == AgentStatus.ACTIVE:
                agent_manager.resume_agent(agent_id)
            elif request.status == AgentStatus.CANCELLED:
                agent_manager.cancel_agent(agent_id)
            elif request.status == AgentStatus.COMPLETED:
                agent_manager.complete_agent(agent_id)

        # Get updated status
        updated_status = agent_manager.get_agent_status(agent_id)

        return AgentResponse(**updated_status)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update agent {agent_id}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{agent_id}")
async def delete_agent(agent_id: str):
    """
    Cancel/delete agent permanently

    Agent will stop monitoring and cannot be resumed.
    """
    try:
        agent_manager = get_agent_manager()

        # Verify agent exists
        status = agent_manager.get_agent_status(agent_id)
        if not status:
            raise HTTPException(status_code=404, detail=f"Agent {agent_id} not found")

        agent_manager.cancel_agent(agent_id)

        return {"message": f"Agent {agent_id} cancelled successfully"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete agent {agent_id}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{agent_id}/matches", response_model=MatchListResponse)
async def get_agent_matches(
    agent_id: str,
    status: Optional[MatchStatus] = Query(None, description="Filter by match status")
):
    """
    Get all matches found by agent

    Returns property matches with scores and reasons.
    """
    try:
        agent_manager = get_agent_manager()

        # Verify agent exists
        agent_status = agent_manager.get_agent_status(agent_id)
        if not agent_status:
            raise HTTPException(status_code=404, detail=f"Agent {agent_id} not found")

        # Get matches
        status_filter = status.value if status else None
        matches = agent_manager.get_agent_matches(agent_id, status=status_filter)

        # Format matches for response
        match_responses = []
        for match in matches:
            property_data = match.get('property_data', {})

            match_responses.append(MatchResponse(
                match_id=match['match_id'],
                agent_id=agent_id,
                property_address=match['property_address'],
                match_score=property_data.get('match_score', 0),
                match_reasons=property_data.get('match_reasons', []),
                property_data=property_data,
                status=match['status'],
                created_at=match['created_at'],
                notified_at=match.get('notified_at'),
                ghl_opportunity_id=match.get('ghl_opportunity_id')
            ))

        return MatchListResponse(
            agent_id=agent_id,
            total_matches=len(match_responses),
            matches=match_responses
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get matches for agent {agent_id}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{agent_id}/check")
async def force_check_agent(agent_id: str):
    """
    Force immediate property check for agent

    Useful for testing - normally agents check every 4 hours automatically.
    """
    try:
        agent_manager = get_agent_manager()

        # Verify agent exists
        status = agent_manager.get_agent_status(agent_id)
        if not status:
            raise HTTPException(status_code=404, detail=f"Agent {agent_id} not found")

        # Force check
        agent_manager._run_agent_check(agent_id)

        # Get updated status
        updated_status = agent_manager.get_agent_status(agent_id)

        return {
            "message": f"Agent {agent_id} check completed",
            "matches_found": updated_status.get('matches_found', 0),
            "new_matches": updated_status.get('new_matches', 0)
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to force check agent {agent_id}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/system/status", response_model=SystemStatusResponse)
async def get_system_status():
    """
    Get overall system status

    Returns statistics for all agents and matches.
    """
    try:
        agent_manager = get_agent_manager()
        status = agent_manager.get_system_status()

        return SystemStatusResponse(**status)

    except Exception as e:
        logger.error(f"Failed to get system status: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
