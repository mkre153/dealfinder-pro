-- DealFinder Pro - Agent Memory Schema
-- Database schema for agentic system memory storage
-- Run with: psql dealfinder < database/agent_memory_schema.sql

-- ========================================
-- AGENT MEMORIES TABLE
-- ========================================
-- Stores agent memories for learning and pattern recognition
CREATE TABLE IF NOT EXISTS agent_memories (
    memory_id VARCHAR(255) PRIMARY KEY,
    agent_name VARCHAR(100) NOT NULL,
    memory_type VARCHAR(50) NOT NULL,  -- short_term, long_term, episodic, semantic
    content JSONB NOT NULL,
    importance DECIMAL(3,2),  -- 0.00 to 1.00
    metadata JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    accessed_count INTEGER DEFAULT 0,
    last_accessed TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_agent_memories_agent
    ON agent_memories(agent_name);

CREATE INDEX IF NOT EXISTS idx_agent_memories_type
    ON agent_memories(memory_type);

CREATE INDEX IF NOT EXISTS idx_agent_memories_importance
    ON agent_memories(importance DESC);

CREATE INDEX IF NOT EXISTS idx_agent_memories_created
    ON agent_memories(created_at DESC);

-- JSONB index for content search
CREATE INDEX IF NOT EXISTS idx_agent_memories_content
    ON agent_memories USING GIN (content);

-- ========================================
-- AGENT PERFORMANCE METRICS TABLE
-- ========================================
-- Tracks agent decision accuracy and performance over time
CREATE TABLE IF NOT EXISTS agent_performance (
    id SERIAL PRIMARY KEY,
    agent_name VARCHAR(100) NOT NULL,
    metric_date DATE DEFAULT CURRENT_DATE,
    decisions_made INTEGER DEFAULT 0,
    tools_used INTEGER DEFAULT 0,
    successful_outcomes INTEGER DEFAULT 0,
    failed_outcomes INTEGER DEFAULT 0,
    avg_confidence DECIMAL(4,3),
    learned_patterns_count INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Index for agent performance queries
CREATE INDEX IF NOT EXISTS idx_agent_performance_agent_date
    ON agent_performance(agent_name, metric_date DESC);

-- ========================================
-- AGENT COMMUNICATIONS TABLE
-- ========================================
-- Logs inter-agent communication for debugging and analysis
CREATE TABLE IF NOT EXISTS agent_communications (
    id SERIAL PRIMARY KEY,
    from_agent VARCHAR(100) NOT NULL,
    to_agent VARCHAR(100) NOT NULL,
    message_type VARCHAR(50) NOT NULL,
    content JSONB NOT NULL,
    priority INTEGER DEFAULT 0,
    status VARCHAR(20) DEFAULT 'pending',  -- pending, delivered, processed
    response JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    processed_at TIMESTAMP
);

-- Indexes for communication queries
CREATE INDEX IF NOT EXISTS idx_agent_comms_from
    ON agent_communications(from_agent);

CREATE INDEX IF NOT EXISTS idx_agent_comms_to
    ON agent_communications(to_agent);

CREATE INDEX IF NOT EXISTS idx_agent_comms_status
    ON agent_communications(status);

-- ========================================
-- HELPER FUNCTIONS
-- ========================================

-- Function to get agent's recent memories
CREATE OR REPLACE FUNCTION get_agent_recent_memories(
    p_agent_name VARCHAR(100),
    p_limit INTEGER DEFAULT 10
)
RETURNS TABLE (
    memory_id VARCHAR(255),
    memory_type VARCHAR(50),
    content JSONB,
    importance DECIMAL(3,2),
    created_at TIMESTAMP
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        m.memory_id,
        m.memory_type,
        m.content,
        m.importance,
        m.created_at
    FROM agent_memories m
    WHERE m.agent_name = p_agent_name
    ORDER BY m.created_at DESC
    LIMIT p_limit;
END;
$$ LANGUAGE plpgsql;

-- Function to get agent's learned patterns
CREATE OR REPLACE FUNCTION get_agent_learned_patterns(
    p_agent_name VARCHAR(100)
)
RETURNS TABLE (
    pattern_name TEXT,
    insight TEXT,
    confidence DECIMAL(3,2),
    created_at TIMESTAMP
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        m.content->>'pattern_name' as pattern_name,
        m.content->>'insight' as insight,
        (m.content->>'confidence')::DECIMAL(3,2) as confidence,
        m.created_at
    FROM agent_memories m
    WHERE m.agent_name = p_agent_name
        AND m.memory_type = 'semantic'
        AND m.metadata->>'category' = 'learned_pattern'
    ORDER BY confidence DESC, m.created_at DESC;
END;
$$ LANGUAGE plpgsql;

-- Function to clean old short-term memories (older than 7 days)
CREATE OR REPLACE FUNCTION cleanup_old_short_term_memories()
RETURNS INTEGER AS $$
DECLARE
    deleted_count INTEGER;
BEGIN
    DELETE FROM agent_memories
    WHERE memory_type = 'short_term'
        AND created_at < CURRENT_TIMESTAMP - INTERVAL '7 days';

    GET DIAGNOSTICS deleted_count = ROW_COUNT;
    RETURN deleted_count;
END;
$$ LANGUAGE plpgsql;

-- ========================================
-- SAMPLE DATA (Optional - for testing)
-- ========================================

-- Uncomment to insert sample data for testing
/*
INSERT INTO agent_memories (memory_id, agent_name, memory_type, content, importance, metadata)
VALUES
    (
        'test_memory_1',
        'market_analyst',
        'semantic',
        '{"pattern_name": "winter_market", "insight": "90210 properties close 60% faster in winter", "confidence": 0.85}',
        0.85,
        '{"category": "learned_pattern"}'
    ),
    (
        'test_memory_2',
        'deal_hunter',
        'episodic',
        '{"action": "evaluated_property", "property": "123 Main St", "decision": "pursue", "outcome": "success"}',
        0.90,
        '{"deal_id": "PROP_123"}'
    );
*/

-- ========================================
-- GRANTS (Adjust as needed)
-- ========================================

-- Grant permissions to dealfinder user (adjust username as needed)
-- GRANT SELECT, INSERT, UPDATE, DELETE ON agent_memories TO dealfinder_user;
-- GRANT SELECT, INSERT, UPDATE, DELETE ON agent_performance TO dealfinder_user;
-- GRANT SELECT, INSERT, UPDATE, DELETE ON agent_communications TO dealfinder_user;

-- ========================================
-- VERIFICATION
-- ========================================

-- Verify tables were created
SELECT
    table_name,
    (SELECT COUNT(*) FROM information_schema.columns WHERE table_name = t.table_name) as column_count
FROM information_schema.tables t
WHERE table_schema = 'public'
    AND table_name IN ('agent_memories', 'agent_performance', 'agent_communications')
ORDER BY table_name;

-- Verify indexes were created
SELECT
    indexname,
    tablename
FROM pg_indexes
WHERE tablename IN ('agent_memories', 'agent_performance', 'agent_communications')
ORDER BY tablename, indexname;

-- Show table sizes
SELECT
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
FROM pg_tables
WHERE tablename IN ('agent_memories', 'agent_performance', 'agent_communications')
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;

-- ========================================
-- MAINTENANCE
-- ========================================

-- Run cleanup monthly (can be automated with cron)
-- SELECT cleanup_old_short_term_memories();

-- Vacuum and analyze for performance
-- VACUUM ANALYZE agent_memories;
-- VACUUM ANALYZE agent_performance;
-- VACUUM ANALYZE agent_communications;

-- ========================================
-- COMPLETE
-- ========================================

\echo 'Agent memory schema created successfully!'
\echo 'Tables: agent_memories, agent_performance, agent_communications'
\echo 'Helper functions: get_agent_recent_memories(), get_agent_learned_patterns(), cleanup_old_short_term_memories()'
