"""
Agent Memory System
Provides short-term (working) and long-term (experiential) memory for agents
"""

import json
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from enum import Enum
from collections import deque


class MemoryType(Enum):
    """Types of memories an agent can store"""
    SHORT_TERM = "short_term"      # Current context, recent actions
    LONG_TERM = "long_term"         # Learned patterns, historical insights
    EPISODIC = "episodic"           # Specific past experiences/events
    SEMANTIC = "semantic"           # General knowledge/facts


class Memory:
    """Individual memory item"""

    def __init__(
        self,
        memory_type: MemoryType,
        content: Dict[str, Any],
        importance: float = 0.5,
        metadata: Optional[Dict[str, Any]] = None
    ):
        self.type = memory_type
        self.content = content
        self.importance = importance  # 0-1, how important to remember
        self.metadata = metadata or {}
        self.created_at = datetime.now()
        self.accessed_count = 0
        self.last_accessed = datetime.now()

    def access(self):
        """Mark memory as accessed (for recency tracking)"""
        self.accessed_count += 1
        self.last_accessed = datetime.now()

    def to_dict(self) -> Dict[str, Any]:
        """Serialize memory to dict"""
        return {
            "type": self.type.value,
            "content": self.content,
            "importance": self.importance,
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat(),
            "accessed_count": self.accessed_count,
            "last_accessed": self.last_accessed.isoformat()
        }


class AgentMemory:
    """
    Agent memory system with short-term and long-term storage

    Short-term memory: Limited capacity, recent context (like working memory)
    Long-term memory: Unlimited, persistent learnings (like human long-term memory)
    """

    def __init__(
        self,
        agent_name: str,
        db_manager=None,
        short_term_capacity: int = 20,
        long_term_capacity: int = 1000
    ):
        """
        Initialize agent memory

        Args:
            agent_name: Name of the agent (for DB storage)
            db_manager: Database manager for persistent storage
            short_term_capacity: Max items in short-term memory
            long_term_capacity: Max items in long-term memory
        """
        self.agent_name = agent_name
        self.db = db_manager
        self.logger = logging.getLogger(f"{__name__}.{agent_name}")

        # Short-term memory (deque for efficient FIFO)
        self.short_term = deque(maxlen=short_term_capacity)

        # Long-term memory (dict for fast lookup)
        self.long_term: Dict[str, Memory] = {}
        self.long_term_capacity = long_term_capacity

        # Load persistent memories from database
        self._load_from_database()

    def store(
        self,
        content: Dict[str, Any],
        memory_type: MemoryType = MemoryType.SHORT_TERM,
        importance: float = 0.5,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Store a memory

        Args:
            content: Memory content (dict with any structure)
            memory_type: Type of memory
            importance: Importance score (0-1)
            metadata: Additional metadata

        Returns:
            Memory ID
        """
        memory = Memory(
            memory_type=memory_type,
            content=content,
            importance=importance,
            metadata=metadata or {}
        )

        # Generate unique ID
        memory_id = f"{self.agent_name}_{memory_type.value}_{datetime.now().timestamp()}"

        if memory_type == MemoryType.SHORT_TERM:
            self.short_term.append((memory_id, memory))
            self.logger.debug(f"Stored short-term memory: {memory_id}")

        else:  # Long-term, Episodic, or Semantic
            # If at capacity, remove least important/accessed memory
            if len(self.long_term) >= self.long_term_capacity:
                self._evict_least_important()

            self.long_term[memory_id] = memory
            self.logger.debug(f"Stored long-term memory: {memory_id}")

            # Persist to database
            if self.db:
                self._save_to_database(memory_id, memory)

        return memory_id

    def recall(
        self,
        query: str,
        memory_type: Optional[MemoryType] = None,
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Recall memories relevant to a query

        Args:
            query: Query string (semantic search)
            memory_type: Filter by memory type (optional)
            limit: Max memories to return

        Returns:
            List of relevant memories
        """
        relevant_memories = []

        # Search short-term memory
        if memory_type is None or memory_type == MemoryType.SHORT_TERM:
            for memory_id, memory in self.short_term:
                if self._is_relevant(query, memory):
                    memory.access()
                    relevant_memories.append({
                        "id": memory_id,
                        "content": memory.content,
                        "type": memory.type.value,
                        "importance": memory.importance,
                        "relevance": self._calculate_relevance(query, memory)
                    })

        # Search long-term memory
        if memory_type is None or memory_type != MemoryType.SHORT_TERM:
            for memory_id, memory in self.long_term.items():
                if memory_type and memory.type != memory_type:
                    continue

                if self._is_relevant(query, memory):
                    memory.access()
                    relevant_memories.append({
                        "id": memory_id,
                        "content": memory.content,
                        "type": memory.type.value,
                        "importance": memory.importance,
                        "relevance": self._calculate_relevance(query, memory)
                    })

        # Sort by relevance * importance and limit
        relevant_memories.sort(
            key=lambda m: m['relevance'] * m['importance'],
            reverse=True
        )

        self.logger.info(f"Recalled {len(relevant_memories[:limit])} memories for query: {query}")
        return relevant_memories[:limit]

    def _is_relevant(self, query: str, memory: Memory) -> bool:
        """
        Simple relevance check (keyword matching)
        In production, would use semantic similarity (embeddings)
        """
        query_lower = query.lower()
        content_str = json.dumps(memory.content).lower()

        # Simple keyword matching
        query_words = set(query_lower.split())
        content_words = set(content_str.split())

        # Check for word overlap
        overlap = query_words & content_words
        return len(overlap) > 0

    def _calculate_relevance(self, query: str, memory: Memory) -> float:
        """
        Calculate relevance score (0-1)
        Simple implementation - would use embeddings in production
        """
        query_lower = query.lower()
        content_str = json.dumps(memory.content).lower()

        query_words = set(query_lower.split())
        content_words = set(content_str.split())

        if not query_words:
            return 0.0

        overlap = query_words & content_words
        return len(overlap) / len(query_words)

    def _evict_least_important(self):
        """Remove least important/accessed memory to make room"""
        if not self.long_term:
            return

        # Score = importance * recency factor
        def memory_score(item):
            memory_id, memory = item
            days_since_access = (datetime.now() - memory.last_accessed).days
            recency_factor = 1.0 / (1 + days_since_access)  # Decay over time
            return memory.importance * recency_factor

        # Find and remove lowest scoring memory
        least_important = min(self.long_term.items(), key=memory_score)
        memory_id = least_important[0]

        del self.long_term[memory_id]
        self.logger.debug(f"Evicted memory: {memory_id}")

    def consolidate_short_to_long(self, importance_threshold: float = 0.7):
        """
        Move important short-term memories to long-term
        (Like sleep consolidation in human memory)

        Args:
            importance_threshold: Min importance to consolidate
        """
        consolidated_count = 0

        for memory_id, memory in list(self.short_term):
            if memory.importance >= importance_threshold:
                # Promote to long-term
                self.long_term[memory_id] = memory
                self.logger.info(f"Consolidated to long-term: {memory_id}")
                consolidated_count += 1

                # Save to database
                if self.db:
                    self._save_to_database(memory_id, memory)

        return consolidated_count

    def get_recent_context(self, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Get recent short-term memories (current context)

        Args:
            limit: Max memories to return

        Returns:
            List of recent memories
        """
        recent = list(self.short_term)[-limit:]
        return [
            {
                "id": memory_id,
                "content": memory.content,
                "created_at": memory.created_at.isoformat()
            }
            for memory_id, memory in recent
        ]

    def learn_pattern(
        self,
        pattern_name: str,
        insight: str,
        evidence: List[Any],
        confidence: float
    ) -> str:
        """
        Store a learned pattern/insight

        Args:
            pattern_name: Name of the pattern
            insight: The insight/learning
            evidence: Supporting evidence
            confidence: Confidence in pattern (0-1)

        Returns:
            Memory ID
        """
        return self.store(
            content={
                "pattern_name": pattern_name,
                "insight": insight,
                "evidence": evidence,
                "confidence": confidence,
                "learned_at": datetime.now().isoformat()
            },
            memory_type=MemoryType.SEMANTIC,
            importance=confidence,  # High confidence = high importance
            metadata={"category": "learned_pattern"}
        )

    def get_learned_patterns(self) -> List[Dict[str, Any]]:
        """Get all learned patterns"""
        patterns = []

        for memory_id, memory in self.long_term.items():
            if (memory.type == MemoryType.SEMANTIC and
                memory.metadata.get("category") == "learned_pattern"):
                patterns.append({
                    "id": memory_id,
                    **memory.content
                })

        # Sort by confidence
        patterns.sort(key=lambda p: p.get('confidence', 0), reverse=True)
        return patterns

    def _save_to_database(self, memory_id: str, memory: Memory):
        """Persist memory to database"""
        if not self.db:
            return

        try:
            # Store in agent_memories table
            self.db.execute_query(
                """
                INSERT INTO agent_memories (memory_id, agent_name, memory_type, content, importance, metadata, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (memory_id) DO UPDATE SET
                    content = EXCLUDED.content,
                    importance = EXCLUDED.importance,
                    metadata = EXCLUDED.metadata
                """,
                (
                    memory_id,
                    self.agent_name,
                    memory.type.value,
                    json.dumps(memory.content),
                    memory.importance,
                    json.dumps(memory.metadata),
                    memory.created_at
                )
            )
        except Exception as e:
            self.logger.error(f"Failed to save memory to database: {e}")

    def _load_from_database(self):
        """Load persistent memories from database"""
        if not self.db:
            return

        try:
            rows = self.db.fetch_all(
                """
                SELECT memory_id, memory_type, content, importance, metadata, created_at
                FROM agent_memories
                WHERE agent_name = %s
                ORDER BY created_at DESC
                LIMIT %s
                """,
                (self.agent_name, self.long_term_capacity)
            )

            for row in rows:
                memory = Memory(
                    memory_type=MemoryType(row['memory_type']),
                    content=json.loads(row['content']),
                    importance=row['importance'],
                    metadata=json.loads(row['metadata'])
                )
                memory.created_at = row['created_at']

                self.long_term[row['memory_id']] = memory

            self.logger.info(f"Loaded {len(rows)} memories from database")

        except Exception as e:
            self.logger.warning(f"Could not load memories from database: {e}")

    def clear_short_term(self):
        """Clear short-term memory"""
        self.short_term.clear()
        self.logger.info("Cleared short-term memory")

    def get_stats(self) -> Dict[str, Any]:
        """Get memory statistics"""
        return {
            "agent_name": self.agent_name,
            "short_term_count": len(self.short_term),
            "short_term_capacity": self.short_term.maxlen,
            "long_term_count": len(self.long_term),
            "long_term_capacity": self.long_term_capacity,
            "learned_patterns": len(self.get_learned_patterns())
        }
