"""
AgentManager - Lifecycle Management for SearchAgents
Handles starting, stopping, scheduling, and monitoring of autonomous agents
"""

from typing import Dict, List, Optional
from datetime import datetime
import logging
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
import atexit

from modules.client_db import get_db
from modules.search_agent import SearchAgent

logger = logging.getLogger(__name__)


class AgentManager:
    """
    Manages lifecycle of all SearchAgents
    - Starts/stops agents
    - Schedules periodic checks
    - Monitors agent health
    - Coordinates notifications
    """

    def __init__(self):
        """Initialize agent manager with scheduler"""
        self.db = get_db()
        self.active_agents: Dict[str, SearchAgent] = {}
        self.scheduler = BackgroundScheduler()
        self.scheduler.start()

        # Shutdown scheduler on exit
        atexit.register(lambda: self.scheduler.shutdown())

        # Load and start all active agents from database
        self._load_active_agents()

        logger.info("AgentManager initialized")

    def _load_active_agents(self):
        """Load all active agents from database and start them"""
        active_agents = self.db.get_active_agents()

        for agent_data in active_agents:
            agent_id = agent_data['agent_id']
            try:
                self._start_agent(agent_id)
                logger.info(f"Loaded agent {agent_id} from database")
            except Exception as e:
                logger.error(f"Failed to load agent {agent_id}: {e}")

    def create_agent(self, client_id: str, criteria: Dict,
                    notification_email: bool = True,
                    notification_sms: bool = False,
                    notification_chat: bool = True) -> str:
        """
        Create and start a new autonomous search agent

        Args:
            client_id: Client ID from database
            criteria: Search criteria dictionary with:
                - zip_codes: List[str]
                - price_min: int
                - price_max: int
                - bedrooms_min: int
                - bathrooms_min: int
                - property_types: List[str]
                - deal_quality: List[str] (HOT, GOOD, FAIR)
                - min_score: int (default 80)
            notification_email: Enable email notifications
            notification_sms: Enable SMS notifications
            notification_chat: Enable in-app notifications

        Returns:
            agent_id: Unique agent identifier
        """
        # Create search criteria in database
        criteria_id = self.db.create_search_criteria(client_id, **criteria)

        # Create agent in database
        agent_id = self.db.create_agent(
            client_id=client_id,
            criteria_id=criteria_id,
            notification_email=notification_email,
            notification_sms=notification_sms,
            notification_chat=notification_chat
        )

        # Start the agent
        self._start_agent(agent_id)

        logger.info(f"Created and started agent {agent_id} for client {client_id}")

        return agent_id

    def _start_agent(self, agent_id: str):
        """
        Start an agent and schedule its periodic checks

        Args:
            agent_id: Agent ID to start
        """
        if agent_id in self.active_agents:
            logger.warning(f"Agent {agent_id} already running")
            return

        # Create SearchAgent instance
        agent = SearchAgent(agent_id)
        self.active_agents[agent_id] = agent

        # Schedule periodic checks (every 4 hours)
        self.scheduler.add_job(
            func=self._run_agent_check,
            trigger=IntervalTrigger(hours=4),
            id=agent_id,
            args=[agent_id],
            replace_existing=True
        )

        # Run initial check immediately
        self._run_agent_check(agent_id)

        logger.info(f"Agent {agent_id} started and scheduled for 4-hour checks")

    def _run_agent_check(self, agent_id: str):
        """
        Run a single check for an agent

        Args:
            agent_id: Agent ID to check
        """
        try:
            agent = self.active_agents.get(agent_id)
            if not agent:
                logger.warning(f"Agent {agent_id} not in active agents, skipping check")
                return

            logger.info(f"Running check for agent {agent_id}")

            # Check for matches
            matches = agent.check_for_matches()

            # Process any new matches
            if matches:
                new_count = agent.process_new_matches(matches)
                logger.info(f"Agent {agent_id}: Processed {new_count} new matches")
            else:
                logger.info(f"Agent {agent_id}: No new matches found")

        except Exception as e:
            logger.error(f"Error running check for agent {agent_id}: {e}", exc_info=True)

    def pause_agent(self, agent_id: str):
        """
        Pause an agent (stop scheduled checks)

        Args:
            agent_id: Agent ID to pause
        """
        if agent_id not in self.active_agents:
            logger.warning(f"Agent {agent_id} not active")
            return

        # Pause agent
        agent = self.active_agents[agent_id]
        agent.pause()

        # Remove from scheduler
        self.scheduler.remove_job(agent_id)

        # Remove from active agents
        del self.active_agents[agent_id]

        logger.info(f"Agent {agent_id} paused")

    def resume_agent(self, agent_id: str):
        """
        Resume a paused agent

        Args:
            agent_id: Agent ID to resume
        """
        # Update status in database
        self.db.update_agent_status(agent_id, 'active')

        # Start the agent
        self._start_agent(agent_id)

        logger.info(f"Agent {agent_id} resumed")

    def cancel_agent(self, agent_id: str):
        """
        Cancel an agent permanently (cannot be resumed)

        Args:
            agent_id: Agent ID to cancel
        """
        if agent_id in self.active_agents:
            # Remove from scheduler
            self.scheduler.remove_job(agent_id)

            # Cancel agent
            agent = self.active_agents[agent_id]
            agent.cancel()

            # Remove from active agents
            del self.active_agents[agent_id]
        else:
            # Just update database if not active
            self.db.update_agent_status(agent_id, 'cancelled')

        logger.info(f"Agent {agent_id} cancelled")

    def complete_agent(self, agent_id: str):
        """
        Mark agent as completed (property found, client satisfied)

        Args:
            agent_id: Agent ID to complete
        """
        if agent_id in self.active_agents:
            # Remove from scheduler
            self.scheduler.remove_job(agent_id)

            # Complete agent
            agent = self.active_agents[agent_id]
            agent.complete()

            # Remove from active agents
            del self.active_agents[agent_id]
        else:
            # Just update database if not active
            self.db.update_agent_status(agent_id, 'completed')

        logger.info(f"Agent {agent_id} completed")

    def get_agent_status(self, agent_id: str) -> Optional[Dict]:
        """
        Get status summary for an agent

        Args:
            agent_id: Agent ID

        Returns:
            Status dictionary or None if not found
        """
        agent = self.active_agents.get(agent_id)
        if agent:
            return agent.get_status_summary()

        # Try to get from database
        agent_data = self.db.get_agent(agent_id)
        if not agent_data:
            return None

        matches = self.db.get_agent_matches(agent_id)

        return {
            'agent_id': agent_id,
            'client_name': agent_data.get('client_name'),
            'status': agent_data.get('status'),
            'created_at': agent_data.get('created_at'),
            'last_check': agent_data.get('last_check'),
            'matches_found': len(matches),
            'new_matches': len([m for m in matches if m['status'] == 'new'])
        }

    def list_active_agents(self, client_id: Optional[str] = None) -> List[Dict]:
        """
        List all active agents, optionally filtered by client

        Args:
            client_id: Optional client ID filter

        Returns:
            List of agent status dictionaries
        """
        agents = self.db.get_active_agents(client_id=client_id)

        result = []
        for agent_data in agents:
            agent_id = agent_data['agent_id']
            status = self.get_agent_status(agent_id)
            if status:
                result.append(status)

        return result

    def get_agent_matches(self, agent_id: str, status: Optional[str] = None) -> List[Dict]:
        """
        Get matches for an agent

        Args:
            agent_id: Agent ID
            status: Optional status filter (new, sent, viewed, contacted, closed)

        Returns:
            List of matches
        """
        return self.db.get_agent_matches(agent_id, status=status)

    def update_match_status(self, match_id: str, status: str):
        """
        Update status of a match

        Args:
            match_id: Match ID
            status: New status (new, sent, viewed, contacted, closed)
        """
        self.db.update_match_status(match_id, status)
        logger.info(f"Match {match_id} status updated to {status}")

    def force_check_all(self):
        """Force immediate check for all active agents (useful for testing)"""
        logger.info(f"Force checking {len(self.active_agents)} active agents")

        for agent_id in list(self.active_agents.keys()):
            self._run_agent_check(agent_id)

    def get_system_status(self) -> Dict:
        """
        Get overall system status

        Returns:
            Dictionary with system-wide statistics
        """
        all_agents = self.db.get_active_agents()

        active_count = len([a for a in all_agents if a['status'] == 'active'])
        paused_count = len([a for a in all_agents if a['status'] == 'paused'])

        total_matches = 0
        new_matches = 0

        for agent in all_agents:
            matches = self.db.get_agent_matches(agent['agent_id'])
            total_matches += len(matches)
            new_matches += len([m for m in matches if m['status'] == 'new'])

        return {
            'active_agents': active_count,
            'paused_agents': paused_count,
            'total_matches': total_matches,
            'new_matches': new_matches,
            'scheduler_running': self.scheduler.running,
            'scheduled_jobs': len(self.scheduler.get_jobs())
        }


# Singleton instance
_manager_instance = None

def get_agent_manager() -> AgentManager:
    """Get singleton AgentManager instance"""
    global _manager_instance
    if _manager_instance is None:
        _manager_instance = AgentManager()
    return _manager_instance
