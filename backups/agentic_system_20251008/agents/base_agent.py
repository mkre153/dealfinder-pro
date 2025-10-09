"""
Base Agent Class
Foundation for all intelligent agents in the system
"""

import logging
from typing import Dict, List, Optional, Any, Callable
from datetime import datetime
from abc import ABC, abstractmethod

from .memory import AgentMemory, MemoryType
from .llm_client import LLMClient


class Tool:
    """Represents a tool/function the agent can use"""

    def __init__(self, name: str, function: Callable, description: str, parameters: Dict[str, str]):
        self.name = name
        self.function = function
        self.description = description
        self.parameters = parameters  # {param_name: param_description}

    def execute(self, **kwargs) -> Any:
        """Execute the tool with given parameters"""
        return self.function(**kwargs)

    def to_dict(self) -> Dict[str, Any]:
        """Serialize tool for LLM consumption"""
        return {
            "name": self.name,
            "description": self.description,
            "parameters": self.parameters
        }


class BaseAgent(ABC):
    """
    Base class for all intelligent agents

    Agents are autonomous entities that:
    - Have goals and objectives
    - Make decisions using LLM reasoning
    - Use tools to take actions
    - Remember past experiences (memory)
    - Learn from outcomes
    - Communicate with other agents
    """

    def __init__(
        self,
        name: str,
        role: str,
        goal: str,
        llm_client: LLMClient,
        db_manager=None,
        config: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize agent

        Args:
            name: Agent name (unique identifier)
            role: Agent role/specialty
            goal: Agent's primary goal
            llm_client: LLM client for reasoning
            db_manager: Database manager for persistence
            config: Agent-specific configuration
        """
        self.name = name
        self.role = role
        self.goal = goal
        self.llm = llm_client
        self.db = db_manager
        self.config = config or {}
        self.logger = logging.getLogger(f"{__name__}.{name}")

        # Initialize memory
        self.memory = AgentMemory(
            agent_name=name,
            db_manager=db_manager,
            short_term_capacity=self.config.get('short_term_capacity', 20),
            long_term_capacity=self.config.get('long_term_capacity', 1000)
        )

        # Tools available to this agent
        self.tools: Dict[str, Tool] = {}

        # Performance metrics
        self.metrics = {
            "decisions_made": 0,
            "tools_used": 0,
            "successful_outcomes": 0,
            "failed_outcomes": 0,
            "started_at": datetime.now()
        }

        self.logger.info(f"Agent initialized: {name} ({role})")

    @abstractmethod
    def execute_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a task (must be implemented by subclasses)

        Args:
            task: Task description and parameters

        Returns:
            Task result
        """
        pass

    def add_tool(self, name: str, function: Callable, description: str, parameters: Dict[str, str]):
        """
        Add a tool the agent can use

        Args:
            name: Tool name
            function: Python function to execute
            description: What the tool does
            parameters: Tool parameters {name: description}
        """
        tool = Tool(name, function, description, parameters)
        self.tools[name] = tool
        self.logger.debug(f"Added tool: {name}")

    def use_tool(self, tool_name: str, **kwargs) -> Any:
        """
        Use a tool

        Args:
            tool_name: Name of tool to use
            **kwargs: Tool parameters

        Returns:
            Tool execution result
        """
        if tool_name not in self.tools:
            raise ValueError(f"Tool not found: {tool_name}")

        tool = self.tools[tool_name]
        self.logger.info(f"Using tool: {tool_name} with params: {kwargs}")

        try:
            result = tool.execute(**kwargs)
            self.metrics["tools_used"] += 1

            # Remember tool usage
            self.memory.store(
                content={
                    "action": "tool_use",
                    "tool": tool_name,
                    "parameters": kwargs,
                    "result_summary": str(result)[:200],  # Store summary
                    "timestamp": datetime.now().isoformat()
                },
                memory_type=MemoryType.SHORT_TERM,
                importance=0.5
            )

            return result

        except Exception as e:
            self.logger.error(f"Tool execution failed: {tool_name} - {e}")
            raise

    def make_decision(
        self,
        context: Dict[str, Any],
        question: str,
        options: List[str],
        recall_relevant_memories: bool = True
    ) -> Dict[str, Any]:
        """
        Make a decision using LLM reasoning

        Args:
            context: Current context/situation
            question: Decision question
            options: Available options
            recall_relevant_memories: Whether to include past experiences

        Returns:
            Dict with 'decision', 'reasoning', 'confidence'
        """
        # Recall relevant past experiences
        relevant_memories = []
        if recall_relevant_memories:
            relevant_memories = self.memory.recall(question, limit=3)

        # Enhance context with memories
        enhanced_context = {
            **context,
            "relevant_past_experiences": [m['content'] for m in relevant_memories],
            "agent_goal": self.goal
        }

        # Use LLM to make decision
        decision = self.llm.make_decision(
            context=enhanced_context,
            question=question,
            options=options,
            agent_role=self.role
        )

        self.metrics["decisions_made"] += 1

        # Store decision in memory
        self.memory.store(
            content={
                "action": "decision",
                "question": question,
                "options": options,
                "decision": decision['decision'],
                "reasoning": decision['reasoning'],
                "confidence": decision['confidence'],
                "timestamp": datetime.now().isoformat()
            },
            memory_type=MemoryType.EPISODIC,
            importance=decision.get('confidence', 0.5)
        )

        self.logger.info(
            f"Decision made: {decision['decision']} "
            f"(confidence: {decision['confidence']:.2f})"
        )

        return decision

    def analyze(
        self,
        data: Dict[str, Any],
        analysis_goal: str,
        recall_relevant_memories: bool = True
    ) -> Dict[str, Any]:
        """
        Analyze data using LLM

        Args:
            data: Data to analyze
            analysis_goal: What to analyze for
            recall_relevant_memories: Include past learnings

        Returns:
            Dict with 'insights', 'patterns', 'recommendations'
        """
        # Recall relevant learnings
        relevant_memories = []
        if recall_relevant_memories:
            relevant_memories = self.memory.recall(analysis_goal, limit=5)

        # Enhance data with past learnings
        enhanced_data = {
            **data,
            "past_learnings": [m['content'] for m in relevant_memories]
        }

        # Use LLM for analysis
        analysis = self.llm.analyze_data(
            data=enhanced_data,
            analysis_goal=analysis_goal,
            agent_role=self.role
        )

        # Store analysis in memory
        self.memory.store(
            content={
                "action": "analysis",
                "goal": analysis_goal,
                "insights": analysis['insights'],
                "patterns": analysis['patterns'],
                "timestamp": datetime.now().isoformat()
            },
            memory_type=MemoryType.EPISODIC,
            importance=analysis.get('confidence', 0.5)
        )

        self.logger.info(f"Analysis complete: {len(analysis['insights'])} insights found")

        return analysis

    def learn_from_outcome(
        self,
        action: Dict[str, Any],
        outcome: Dict[str, Any],
        success: bool
    ):
        """
        Learn from an outcome (reinforcement learning)

        Args:
            action: Action that was taken
            outcome: Result of the action
            success: Whether outcome was successful
        """
        # Update metrics
        if success:
            self.metrics["successful_outcomes"] += 1
        else:
            self.metrics["failed_outcomes"] += 1

        # Extract learning
        learning_content = {
            "action": action,
            "outcome": outcome,
            "success": success,
            "learned_at": datetime.now().isoformat()
        }

        # Store as important long-term memory
        importance = 0.8 if success else 0.6  # Successes slightly more important
        self.memory.store(
            content=learning_content,
            memory_type=MemoryType.EPISODIC,
            importance=importance,
            metadata={"category": "outcome_learning"}
        )

        # If successful, try to identify the pattern
        if success:
            self._identify_success_pattern(action, outcome)

        self.logger.info(f"Learned from outcome: {'success' if success else 'failure'}")

    def _identify_success_pattern(self, action: Dict[str, Any], outcome: Dict[str, Any]):
        """
        Identify patterns in successful outcomes

        Args:
            action: Successful action
            outcome: Successful outcome
        """
        # Get similar past successful outcomes
        similar_successes = [
            m for m in self.memory.recall("successful outcomes", limit=10)
            if m['content'].get('success') is True
        ]

        if len(similar_successes) >= 3:
            # Use LLM to identify pattern
            try:
                pattern_analysis = self.llm.analyze_data(
                    data={
                        "recent_success": {"action": action, "outcome": outcome},
                        "past_successes": [m['content'] for m in similar_successes]
                    },
                    analysis_goal="Identify common patterns in successful outcomes",
                    agent_role=self.role
                )

                # Store discovered patterns
                for pattern in pattern_analysis.get('patterns', []):
                    self.memory.learn_pattern(
                        pattern_name=f"success_pattern_{datetime.now().timestamp()}",
                        insight=pattern,
                        evidence=similar_successes[:5],
                        confidence=pattern_analysis.get('confidence', 0.7)
                    )

            except Exception as e:
                self.logger.warning(f"Failed to identify success pattern: {e}")

    def get_learned_insights(self) -> List[Dict[str, Any]]:
        """Get all insights the agent has learned"""
        return self.memory.get_learned_patterns()

    def get_performance_summary(self) -> Dict[str, Any]:
        """Get agent performance metrics"""
        total_outcomes = self.metrics["successful_outcomes"] + self.metrics["failed_outcomes"]
        success_rate = (
            self.metrics["successful_outcomes"] / total_outcomes
            if total_outcomes > 0 else 0
        )

        runtime = datetime.now() - self.metrics["started_at"]

        return {
            "agent_name": self.name,
            "role": self.role,
            "runtime_hours": runtime.total_seconds() / 3600,
            "decisions_made": self.metrics["decisions_made"],
            "tools_used": self.metrics["tools_used"],
            "success_rate": success_rate,
            "total_outcomes": total_outcomes,
            "learned_patterns": len(self.get_learned_insights()),
            "memory_stats": self.memory.get_stats()
        }

    def consolidate_memory(self):
        """
        Consolidate important short-term memories to long-term
        (Should be called periodically, like during idle time)
        """
        consolidated = self.memory.consolidate_short_to_long(importance_threshold=0.7)
        self.logger.info(f"Consolidated {consolidated} memories to long-term storage")
        return consolidated

    def get_system_prompt(self) -> str:
        """
        Generate system prompt for LLM interactions
        (Can be overridden by subclasses)
        """
        return f"""You are {self.name}, a {self.role} agent in a real estate investment platform.

Your goal: {self.goal}

You make intelligent, data-driven decisions to achieve this goal. You learn from past experiences and adapt your strategies based on outcomes.

Always:
- Consider both short-term gains and long-term strategy
- Base decisions on data and past learnings
- Explain your reasoning clearly
- Assign confidence scores to your decisions
"""

    def __repr__(self) -> str:
        return f"<Agent {self.name} ({self.role})>"
