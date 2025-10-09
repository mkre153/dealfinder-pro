"""
Agent Coordinator
Manages communication and coordination between multiple agents
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
from collections import defaultdict
import json


class Message:
    """Message passed between agents"""

    def __init__(
        self,
        from_agent: str,
        to_agent: str,
        message_type: str,
        content: Dict[str, Any],
        priority: int = 0
    ):
        self.from_agent = from_agent
        self.to_agent = to_agent
        self.message_type = message_type
        self.content = content
        self.priority = priority  # Higher = more urgent
        self.timestamp = datetime.now()
        self.status = "pending"  # pending, delivered, processed
        self.response: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "from": self.from_agent,
            "to": self.to_agent,
            "type": self.message_type,
            "content": self.content,
            "priority": self.priority,
            "timestamp": self.timestamp.isoformat(),
            "status": self.status
        }


class AgentCoordinator:
    """
    Coordinates communication and collaboration between agents

    Provides:
    - Message passing between agents
    - Shared workspace (blackboard pattern)
    - Conflict resolution
    - Resource allocation
    """

    def __init__(self, db_manager=None):
        """
        Initialize coordinator

        Args:
            db_manager: Database manager for logging
        """
        self.db = db_manager
        self.logger = logging.getLogger(__name__)

        # Registry of active agents
        self.agents: Dict[str, Any] = {}

        # Message queues for each agent
        self.message_queues: Dict[str, List[Message]] = defaultdict(list)

        # Shared workspace (blackboard) for inter-agent data
        self.workspace: Dict[str, Any] = {}

        # Message history for debugging
        self.message_history: List[Message] = []

        # Coordination metrics
        self.metrics = {
            "messages_sent": 0,
            "messages_processed": 0,
            "collaborations": 0
        }

        self.logger.info("Agent Coordinator initialized")

    def register_agent(self, agent):
        """
        Register an agent with the coordinator

        Args:
            agent: Agent instance
        """
        self.agents[agent.name] = agent
        self.message_queues[agent.name] = []
        self.logger.info(f"Registered agent: {agent.name}")

    def unregister_agent(self, agent_name: str):
        """Unregister an agent"""
        if agent_name in self.agents:
            del self.agents[agent_name]
            del self.message_queues[agent_name]
            self.logger.info(f"Unregistered agent: {agent_name}")

    def send_message(
        self,
        from_agent: str,
        to_agent: str,
        message_type: str,
        content: Dict[str, Any],
        priority: int = 0,
        wait_for_response: bool = False,
        timeout: int = 30
    ) -> Optional[Dict[str, Any]]:
        """
        Send message from one agent to another

        Args:
            from_agent: Sender agent name
            to_agent: Recipient agent name
            message_type: Type of message (question, request, notification, etc.)
            content: Message content
            priority: Message priority (higher = more urgent)
            wait_for_response: Whether to wait for response
            timeout: Response timeout in seconds

        Returns:
            Response if wait_for_response=True, else None
        """
        # Validate agents exist
        if to_agent not in self.agents:
            raise ValueError(f"Agent not found: {to_agent}")

        # Create message
        message = Message(
            from_agent=from_agent,
            to_agent=to_agent,
            message_type=message_type,
            content=content,
            priority=priority
        )

        # Add to recipient's queue (sorted by priority)
        self.message_queues[to_agent].append(message)
        self.message_queues[to_agent].sort(key=lambda m: -m.priority)

        # Store in history
        self.message_history.append(message)
        self.metrics["messages_sent"] += 1

        self.logger.info(
            f"Message sent: {from_agent} → {to_agent} ({message_type})"
        )

        # Optionally wait for response
        if wait_for_response:
            return self._wait_for_response(message, timeout)

        return None

    def get_messages(self, agent_name: str, limit: int = 10) -> List[Message]:
        """
        Get pending messages for an agent

        Args:
            agent_name: Agent name
            limit: Max messages to return

        Returns:
            List of pending messages
        """
        if agent_name not in self.message_queues:
            return []

        messages = self.message_queues[agent_name][:limit]
        return messages

    def mark_message_processed(
        self,
        agent_name: str,
        message: Message,
        response: Optional[Dict[str, Any]] = None
    ):
        """
        Mark a message as processed

        Args:
            agent_name: Agent that processed the message
            message: The message
            response: Optional response data
        """
        message.status = "processed"
        message.response = response

        # Remove from queue
        if message in self.message_queues[agent_name]:
            self.message_queues[agent_name].remove(message)

        self.metrics["messages_processed"] += 1

        self.logger.debug(f"Message processed by {agent_name}")

    def broadcast_message(
        self,
        from_agent: str,
        message_type: str,
        content: Dict[str, Any],
        exclude_agents: Optional[List[str]] = None
    ):
        """
        Broadcast message to all agents

        Args:
            from_agent: Sender
            message_type: Message type
            content: Message content
            exclude_agents: Agents to exclude from broadcast
        """
        exclude_agents = exclude_agents or []

        for agent_name in self.agents:
            if agent_name != from_agent and agent_name not in exclude_agents:
                self.send_message(
                    from_agent=from_agent,
                    to_agent=agent_name,
                    message_type=message_type,
                    content=content
                )

        self.logger.info(f"Broadcast from {from_agent} to {len(self.agents) - 1} agents")

    def request_collaboration(
        self,
        requesting_agent: str,
        task: Dict[str, Any],
        required_roles: List[str]
    ) -> List[str]:
        """
        Request collaboration from agents with specific roles

        Args:
            requesting_agent: Agent requesting help
            task: Task description
            required_roles: Roles needed for collaboration

        Returns:
            List of agent names that can collaborate
        """
        collaborators = []

        for agent_name, agent in self.agents.items():
            if agent_name == requesting_agent:
                continue

            if agent.role in required_roles:
                # Send collaboration request
                self.send_message(
                    from_agent=requesting_agent,
                    to_agent=agent_name,
                    message_type="collaboration_request",
                    content={
                        "task": task,
                        "requesting_agent": requesting_agent
                    },
                    priority=5  # High priority
                )
                collaborators.append(agent_name)

        self.metrics["collaborations"] += 1
        self.logger.info(
            f"Collaboration requested by {requesting_agent}: "
            f"{len(collaborators)} agents involved"
        )

        return collaborators

    def set_workspace_data(self, key: str, value: Any):
        """
        Store data in shared workspace

        Args:
            key: Data key
            value: Data value
        """
        self.workspace[key] = {
            "value": value,
            "updated_at": datetime.now(),
            "updated_by": None
        }
        self.logger.debug(f"Workspace updated: {key}")

    def get_workspace_data(self, key: str) -> Optional[Any]:
        """
        Get data from shared workspace

        Args:
            key: Data key

        Returns:
            Data value or None
        """
        data = self.workspace.get(key)
        return data['value'] if data else None

    def get_all_workspace_data(self) -> Dict[str, Any]:
        """Get all workspace data"""
        return {k: v['value'] for k, v in self.workspace.items()}

    def resolve_conflict(
        self,
        conflicting_agents: List[str],
        conflict_data: Dict[str, Any],
        resolution_strategy: str = "vote"
    ) -> Dict[str, Any]:
        """
        Resolve conflicts between agents

        Args:
            conflicting_agents: Agents in conflict
            conflict_data: Description of conflict
            resolution_strategy: How to resolve (vote, priority, consensus)

        Returns:
            Resolution decision
        """
        self.logger.warning(
            f"Conflict resolution needed: {len(conflicting_agents)} agents"
        )

        if resolution_strategy == "priority":
            # Use agent with highest priority/experience
            most_experienced = max(
                conflicting_agents,
                key=lambda name: self.agents[name].metrics.get("decisions_made", 0)
            )
            resolution = {
                "strategy": "priority",
                "chosen_agent": most_experienced,
                "reason": "Most experienced agent"
            }

        elif resolution_strategy == "vote":
            # Majority vote
            votes = {}
            for agent_name in self.agents:
                if agent_name not in conflicting_agents:
                    # Get vote from non-conflicting agents
                    response = self.send_message(
                        from_agent="coordinator",
                        to_agent=agent_name,
                        message_type="vote_request",
                        content=conflict_data,
                        wait_for_response=True,
                        timeout=10
                    )
                    if response:
                        vote = response.get('vote')
                        votes[vote] = votes.get(vote, 0) + 1

            winning_vote = max(votes, key=votes.get) if votes else None
            resolution = {
                "strategy": "vote",
                "winner": winning_vote,
                "votes": votes
            }

        else:  # consensus
            resolution = {
                "strategy": "consensus",
                "status": "pending",
                "message": "Agents must reach consensus"
            }

        return resolution

    def get_coordination_stats(self) -> Dict[str, Any]:
        """Get coordination statistics"""
        return {
            "registered_agents": len(self.agents),
            "messages_sent": self.metrics["messages_sent"],
            "messages_processed": self.metrics["messages_processed"],
            "collaborations": self.metrics["collaborations"],
            "pending_messages": sum(len(q) for q in self.message_queues.values()),
            "workspace_items": len(self.workspace)
        }

    def get_agent_communication_graph(self) -> Dict[str, Any]:
        """
        Get communication graph (who talks to whom)

        Returns:
            Graph data structure
        """
        graph = defaultdict(lambda: defaultdict(int))

        for message in self.message_history:
            graph[message.from_agent][message.to_agent] += 1

        return dict(graph)

    def _wait_for_response(self, message: Message, timeout: int) -> Optional[Dict[str, Any]]:
        """Wait for message response (simplified - would use async in production)"""
        import time
        start_time = time.time()

        while time.time() - start_time < timeout:
            if message.status == "processed" and message.response:
                return message.response
            time.sleep(0.1)

        self.logger.warning(f"Message response timeout: {message.message_type}")
        return None

    def __repr__(self) -> str:
        return f"<AgentCoordinator: {len(self.agents)} agents registered>"
