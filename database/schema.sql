-- =====================================================
-- DealFinder Pro Database Schema
-- PostgreSQL 12+ Compatible
-- Version: 1.0
-- Last Updated: 2025-10-08
-- =====================================================

-- Enable UUID extension (optional for future use)
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- =====================================================
-- TABLE: properties
-- Stores all property listings and analysis results
-- =====================================================

CREATE TABLE IF NOT EXISTS properties (
    id SERIAL PRIMARY KEY,
    property_id VARCHAR(100) UNIQUE NOT NULL,
    mls_number VARCHAR(50),

    -- Address Information
    street_address VARCHAR(255) NOT NULL,
    city VARCHAR(100) NOT NULL,
    state VARCHAR(2) NOT NULL,
    zip_code VARCHAR(10) NOT NULL,
    county VARCHAR(100),
    latitude DECIMAL(10, 8),
    longitude DECIMAL(11, 8),

    -- Property Details
    property_type VARCHAR(50),  -- single_family, multi_family, condo, townhouse, etc.
    bedrooms INTEGER,
    bathrooms DECIMAL(3,1),
    square_feet INTEGER,
    lot_size_sqft INTEGER,
    year_built INTEGER,
    stories INTEGER,
    garage_spaces INTEGER,

    -- Financial Information
    list_price DECIMAL(12,2) NOT NULL,
    price_per_sqft DECIMAL(8,2),
    previous_price DECIMAL(12,2),
    price_reduction_amount DECIMAL(12,2),
    price_reduction_date TIMESTAMP,
    tax_assessed_value DECIMAL(12,2),
    annual_taxes DECIMAL(10,2),
    hoa_fee DECIMAL(8,2),

    -- Listing Information
    listing_date TIMESTAMP,
    days_on_market INTEGER,
    listing_agent_name VARCHAR(255),
    listing_agent_phone VARCHAR(20),
    listing_agent_email VARCHAR(255),
    listing_brokerage VARCHAR(255),

    -- Description & Features
    description TEXT,
    features TEXT[],  -- Array of features
    keywords TEXT[],  -- Extracted keywords for matching

    -- Analysis Results
    opportunity_score INTEGER,  -- 0-100 scale
    deal_quality VARCHAR(20),   -- HOT DEAL, GOOD OPPORTUNITY, FAIR DEAL, PASS
    below_market_percentage DECIMAL(5,2),
    estimated_market_value DECIMAL(12,2),
    estimated_profit DECIMAL(12,2),
    cap_rate DECIMAL(5,2),
    cash_on_cash_return DECIMAL(5,2),
    analysis_date TIMESTAMP,

    -- GHL Integration Fields
    ghl_opportunity_id VARCHAR(100),
    ghl_sync_status VARCHAR(20) DEFAULT 'pending',  -- pending, synced, failed
    ghl_sync_date TIMESTAMP,
    ghl_sync_error TEXT,

    -- Metadata
    data_source VARCHAR(50),  -- realtor, mls, csv, api
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for properties table
CREATE INDEX IF NOT EXISTS idx_properties_opportunity_score ON properties(opportunity_score DESC);
CREATE INDEX IF NOT EXISTS idx_properties_deal_quality ON properties(deal_quality);
CREATE INDEX IF NOT EXISTS idx_properties_days_on_market ON properties(days_on_market);
CREATE INDEX IF NOT EXISTS idx_properties_ghl_sync_status ON properties(ghl_sync_status);
CREATE INDEX IF NOT EXISTS idx_properties_created_at ON properties(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_properties_zip_code ON properties(zip_code);
CREATE INDEX IF NOT EXISTS idx_properties_city ON properties(city);
CREATE INDEX IF NOT EXISTS idx_properties_list_price ON properties(list_price);

-- Trigger to auto-update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_properties_updated_at
    BEFORE UPDATE ON properties
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- =====================================================
-- TABLE: buyers
-- Stores buyer information synced from GHL
-- =====================================================

CREATE TABLE IF NOT EXISTS buyers (
    id SERIAL PRIMARY KEY,
    ghl_contact_id VARCHAR(100) UNIQUE NOT NULL,

    -- Contact Information
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    email VARCHAR(255),
    phone VARCHAR(20),

    -- Buyer Preferences
    min_budget DECIMAL(12,2),
    max_budget DECIMAL(12,2),
    preferred_locations TEXT[],  -- Array of cities/ZIP codes
    property_types TEXT[],       -- Array of preferred property types
    min_bedrooms INTEGER,
    min_bathrooms DECIMAL(3,1),
    min_square_feet INTEGER,

    -- Status & Tags
    buyer_status VARCHAR(20) DEFAULT 'active',  -- active, passive, on_hold
    tags TEXT[],
    sms_opt_in BOOLEAN DEFAULT false,

    -- GHL Synchronization
    last_synced_at TIMESTAMP,

    -- Metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for buyers table
CREATE INDEX IF NOT EXISTS idx_buyers_buyer_status ON buyers(buyer_status);
CREATE INDEX IF NOT EXISTS idx_buyers_budget_range ON buyers(min_budget, max_budget);
CREATE INDEX IF NOT EXISTS idx_buyers_sms_opt_in ON buyers(sms_opt_in);
CREATE INDEX IF NOT EXISTS idx_buyers_email ON buyers(email);

-- Trigger to auto-update updated_at timestamp
CREATE TRIGGER update_buyers_updated_at
    BEFORE UPDATE ON buyers
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- =====================================================
-- TABLE: property_matches
-- Links properties to buyers with match scoring
-- =====================================================

CREATE TABLE IF NOT EXISTS property_matches (
    id SERIAL PRIMARY KEY,
    property_id INTEGER NOT NULL REFERENCES properties(id) ON DELETE CASCADE,
    buyer_id INTEGER NOT NULL REFERENCES buyers(id) ON DELETE CASCADE,

    -- Match Details
    match_score INTEGER NOT NULL,  -- 0-100 scale
    match_reasons TEXT[],

    -- Actions Taken
    sms_sent BOOLEAN DEFAULT false,
    sms_sent_at TIMESTAMP,
    workflow_triggered BOOLEAN DEFAULT false,
    workflow_triggered_at TIMESTAMP,
    task_created BOOLEAN DEFAULT false,
    task_id VARCHAR(100),

    -- Metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    UNIQUE(property_id, buyer_id)
);

-- Indexes for property_matches table
CREATE INDEX IF NOT EXISTS idx_property_matches_match_score ON property_matches(match_score DESC);
CREATE INDEX IF NOT EXISTS idx_property_matches_property_id ON property_matches(property_id);
CREATE INDEX IF NOT EXISTS idx_property_matches_buyer_id ON property_matches(buyer_id);
CREATE INDEX IF NOT EXISTS idx_property_matches_sms_sent ON property_matches(sms_sent);

-- =====================================================
-- TABLE: sync_logs
-- Tracks all synchronization operations
-- =====================================================

CREATE TABLE IF NOT EXISTS sync_logs (
    id SERIAL PRIMARY KEY,
    sync_type VARCHAR(50) NOT NULL,  -- ghl_export, ghl_import, mls_import, scrape, etc.
    status VARCHAR(20) NOT NULL,     -- success, failed, partial
    records_processed INTEGER DEFAULT 0,
    records_succeeded INTEGER DEFAULT 0,
    records_failed INTEGER DEFAULT 0,
    error_message TEXT,
    execution_time_seconds INTEGER,
    started_at TIMESTAMP NOT NULL,
    completed_at TIMESTAMP,

    -- Additional metadata
    metadata JSONB  -- For storing additional sync details
);

-- Indexes for sync_logs table
CREATE INDEX IF NOT EXISTS idx_sync_logs_sync_type ON sync_logs(sync_type);
CREATE INDEX IF NOT EXISTS idx_sync_logs_status ON sync_logs(status);
CREATE INDEX IF NOT EXISTS idx_sync_logs_started_at ON sync_logs(started_at DESC);

-- =====================================================
-- VIEWS
-- Convenient views for common queries
-- =====================================================

-- View: Hot Deals (score >= 90)
CREATE OR REPLACE VIEW vw_hot_deals AS
SELECT
    p.*,
    COUNT(pm.id) as matched_buyers
FROM properties p
LEFT JOIN property_matches pm ON p.id = pm.property_id
WHERE p.opportunity_score >= 90
GROUP BY p.id
ORDER BY p.opportunity_score DESC, p.created_at DESC;

-- View: Unsynced Properties (pending GHL sync)
CREATE OR REPLACE VIEW vw_unsynced_properties AS
SELECT *
FROM properties
WHERE ghl_sync_status = 'pending'
  AND opportunity_score >= 75
ORDER BY opportunity_score DESC, created_at DESC;

-- View: Active Buyers
CREATE OR REPLACE VIEW vw_active_buyers AS
SELECT *
FROM buyers
WHERE buyer_status = 'active'
ORDER BY created_at DESC;

-- View: Recent Matches (last 7 days)
CREATE OR REPLACE VIEW vw_recent_matches AS
SELECT
    pm.*,
    p.street_address,
    p.city,
    p.state,
    p.list_price,
    p.opportunity_score,
    b.first_name,
    b.last_name,
    b.email,
    b.phone
FROM property_matches pm
JOIN properties p ON pm.property_id = p.id
JOIN buyers b ON pm.buyer_id = b.id
WHERE pm.created_at >= CURRENT_TIMESTAMP - INTERVAL '7 days'
ORDER BY pm.match_score DESC, pm.created_at DESC;

-- View: Sync Statistics (daily summary)
CREATE OR REPLACE VIEW vw_sync_statistics AS
SELECT
    sync_type,
    DATE(started_at) as sync_date,
    COUNT(*) as sync_count,
    SUM(records_processed) as total_records,
    SUM(records_succeeded) as total_succeeded,
    SUM(records_failed) as total_failed,
    AVG(execution_time_seconds) as avg_execution_time
FROM sync_logs
GROUP BY sync_type, DATE(started_at)
ORDER BY sync_date DESC, sync_type;

-- =====================================================
-- FUNCTIONS
-- Utility functions for common operations
-- =====================================================

-- Function: Get properties by score range
CREATE OR REPLACE FUNCTION get_properties_by_score_range(
    min_score INTEGER,
    max_score INTEGER DEFAULT 100
)
RETURNS TABLE (
    id INTEGER,
    property_id VARCHAR(100),
    street_address VARCHAR(255),
    city VARCHAR(100),
    state VARCHAR(2),
    list_price DECIMAL(12,2),
    opportunity_score INTEGER,
    deal_quality VARCHAR(20)
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        p.id,
        p.property_id,
        p.street_address,
        p.city,
        p.state,
        p.list_price,
        p.opportunity_score,
        p.deal_quality
    FROM properties p
    WHERE p.opportunity_score >= min_score
      AND p.opportunity_score <= max_score
    ORDER BY p.opportunity_score DESC, p.created_at DESC;
END;
$$ LANGUAGE plpgsql;

-- Function: Get match count for property
CREATE OR REPLACE FUNCTION get_match_count(prop_id INTEGER)
RETURNS INTEGER AS $$
DECLARE
    match_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO match_count
    FROM property_matches
    WHERE property_id = prop_id;

    RETURN match_count;
END;
$$ LANGUAGE plpgsql;

-- =====================================================
-- INITIAL DATA
-- Sample data for testing (commented out for production)
-- =====================================================

-- Uncomment for testing:
-- INSERT INTO properties (property_id, street_address, city, state, zip_code, list_price, data_source)
-- VALUES ('TEST001', '123 Main St', 'Los Angeles', 'CA', '90210', 500000.00, 'manual');

-- =====================================================
-- GRANTS
-- Set appropriate permissions (adjust as needed)
-- =====================================================

-- Grant permissions to application user (replace 'dealfinder_app' with your user)
-- GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO dealfinder_app;
-- GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO dealfinder_app;
-- GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA public TO dealfinder_app;

-- =====================================================
-- SCHEMA VERSION TRACKING
-- =====================================================

CREATE TABLE IF NOT EXISTS schema_version (
    version VARCHAR(10) PRIMARY KEY,
    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    description TEXT
);

INSERT INTO schema_version (version, description)
VALUES ('1.0', 'Initial schema creation with properties, buyers, property_matches, and sync_logs tables')
ON CONFLICT (version) DO NOTHING;

-- =====================================================
-- COMMENTS
-- Documentation for tables and columns
-- =====================================================

COMMENT ON TABLE properties IS 'Stores all real estate property listings and analysis results';
COMMENT ON COLUMN properties.property_id IS 'Unique identifier for the property (external ID)';
COMMENT ON COLUMN properties.opportunity_score IS 'Calculated score from 0-100 indicating deal quality';
COMMENT ON COLUMN properties.ghl_sync_status IS 'Synchronization status with GoHighLevel CRM';

COMMENT ON TABLE buyers IS 'Stores buyer information synchronized from GoHighLevel CRM';
COMMENT ON COLUMN buyers.ghl_contact_id IS 'GoHighLevel contact ID (unique identifier)';
COMMENT ON COLUMN buyers.buyer_status IS 'Current status of buyer (active, passive, on_hold)';

COMMENT ON TABLE property_matches IS 'Links properties to buyers with match scoring and action tracking';
COMMENT ON COLUMN property_matches.match_score IS 'Match quality score from 0-100';

COMMENT ON TABLE sync_logs IS 'Tracks all data synchronization operations for monitoring and debugging';

-- =====================================================
-- END OF SCHEMA
-- =====================================================
