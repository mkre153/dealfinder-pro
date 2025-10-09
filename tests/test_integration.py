"""
Integration Tests for DealFinder Pro
Tests complete workflows and module interactions
"""

import pytest
import sys
import os
from datetime import datetime
import json

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules.database import DatabaseManager
from modules.scraper import RealtorScraper
from modules.analyzer import PropertyAnalyzer
from modules.scorer import OpportunityScorer
from modules.reporter import ReportGenerator
from modules.notifier import Notifier
from integrations.ghl_connector import GoHighLevelConnector


# ========================================
# FIXTURES
# ========================================

@pytest.fixture
def test_config():
    """Load test configuration"""
    return {
        'databases': {
            'primary': {
                'type': 'sqlite',
                'database': ':memory:',  # In-memory database for testing
                'enabled': True
            }
        },
        'search_criteria': {
            'target_locations': ['90210'],
            'days_back': 7,
            'property_types': ['single_family'],
            'min_bedrooms': 2,
            'price_range': {'min': 200000, 'max': 1000000}
        },
        'scoring_weights': {
            'price_advantage': 30,
            'days_on_market': 20,
            'financial_returns': 25,
            'condition_price': 15,
            'location_quality': 10
        },
        'notifications': {
            'email': {
                'enabled': False  # Disable for tests
            },
            'sms': {
                'enabled': False
            }
        },
        'gohighlevel': {
            'enabled': False  # Disable for tests
        }
    }


@pytest.fixture
def test_db(test_config):
    """Create test database"""
    db = DatabaseManager(test_config['databases']['primary'])

    # Create schema
    with db.get_connection() as conn:
        cursor = conn.cursor()

        # Properties table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS properties (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                property_id TEXT UNIQUE,
                street_address TEXT,
                city TEXT,
                state TEXT,
                zip_code TEXT,
                list_price INTEGER,
                bedrooms INTEGER,
                bathrooms REAL,
                square_feet INTEGER,
                property_type TEXT,
                days_on_market INTEGER,
                opportunity_score INTEGER,
                deal_quality TEXT,
                below_market_percentage REAL,
                estimated_profit INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Buyers table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS buyers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ghl_contact_id TEXT UNIQUE,
                first_name TEXT,
                last_name TEXT,
                email TEXT,
                phone TEXT,
                min_budget INTEGER,
                max_budget INTEGER,
                buyer_status TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Property matches table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS property_matches (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                property_id INTEGER,
                buyer_id INTEGER,
                match_score INTEGER,
                match_reasons TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        cursor.close()

    yield db

    # Cleanup
    db.close()


@pytest.fixture
def sample_property():
    """Sample property data for testing"""
    return {
        'property_id': 'TEST_PROP_001',
        'street_address': '123 Test Street',
        'city': 'Beverly Hills',
        'state': 'CA',
        'zip_code': '90210',
        'list_price': 750000,
        'bedrooms': 3,
        'bathrooms': 2.5,
        'square_feet': 2000,
        'lot_size': '5000 sqft',
        'property_type': 'Single Family',
        'year_built': 1990,
        'days_on_market': 60,
        'mls_number': 'MLS12345',
        'description': 'Great investment opportunity. Motivated seller.',
        'listing_url': 'https://www.realtor.com/test',
        'price_reduction_amount': 25000,
        'tax_assessment': 650000
    }


@pytest.fixture
def sample_buyer():
    """Sample buyer data for testing"""
    return {
        'ghl_contact_id': 'GHL_BUYER_001',
        'first_name': 'John',
        'last_name': 'Investor',
        'email': 'john@investor.com',
        'phone': '+15551234567',
        'min_budget': 500000,
        'max_budget': 1000000,
        'buyer_status': 'active'
    }


# ========================================
# DATABASE TESTS
# ========================================

class TestDatabase:
    """Test database operations"""

    def test_connection(self, test_db):
        """Test database connection"""
        assert test_db.test_connection() is True

    def test_insert_property(self, test_db, sample_property):
        """Test property insertion"""
        property_id = test_db.insert_property(sample_property)
        assert property_id > 0

        # Verify retrieval
        retrieved = test_db.get_property_by_id(sample_property['property_id'])
        assert retrieved is not None
        assert retrieved['street_address'] == sample_property['street_address']

    def test_upsert_buyer(self, test_db, sample_buyer):
        """Test buyer upsert"""
        buyer_id = test_db.upsert_buyer(sample_buyer)
        assert buyer_id > 0

        # Update same buyer
        sample_buyer['min_budget'] = 600000
        buyer_id_2 = test_db.upsert_buyer(sample_buyer)
        assert buyer_id_2 == buyer_id  # Should be same ID

        # Verify update
        buyers = test_db.get_active_buyers()
        assert len(buyers) == 1
        assert buyers[0]['min_budget'] == 600000

    def test_property_search(self, test_db, sample_property):
        """Test property search by criteria"""
        # Insert test properties
        test_db.insert_property(sample_property)

        sample_property_2 = sample_property.copy()
        sample_property_2['property_id'] = 'TEST_PROP_002'
        sample_property_2['zip_code'] = '90211'
        test_db.insert_property(sample_property_2)

        # Search by ZIP code
        results = test_db.get_properties_by_criteria({'zip_code': '90210'})
        assert len(results) == 1
        assert results[0]['property_id'] == 'TEST_PROP_001'


# ========================================
# ANALYZER TESTS
# ========================================

class TestAnalyzer:
    """Test property analysis"""

    def test_analysis_complete(self, test_db, test_config, sample_property):
        """Test complete property analysis"""
        analyzer = PropertyAnalyzer(test_db, test_config)
        scorer = OpportunityScorer(test_config)

        # Analyze property
        result = analyzer.analyze_property(sample_property)

        # Check required fields exist
        assert 'opportunity_score' in result
        assert 'deal_quality' in result
        assert 'investment_metrics' in result
        assert 'recommendation' in result

        # Verify score is valid
        assert 0 <= result['opportunity_score'] <= 100

        # Verify deal quality classification
        assert result['deal_quality'] in ['HOT DEAL', 'GOOD OPPORTUNITY', 'FAIR DEAL', 'PASS']

    def test_scorer_components(self, test_config):
        """Test individual scoring components"""
        scorer = OpportunityScorer(test_config)

        property_data = {
            'list_price': 500000,
            'square_feet': 2000,
            'days_on_market': 90,
            'price_reduction_amount': 20000,
            'description': 'Motivated seller, needs work, as-is'
        }

        market_data = {
            'median_price_per_sqft': 300
        }

        investment_metrics = {
            'cap_rate': 8.5,
            'estimated_profit': 100000
        }

        score, quality, breakdown = scorer.calculate_score(
            property_data, market_data, investment_metrics
        )

        # Verify breakdown has all components
        assert 'price_score' in breakdown
        assert 'dom_score' in breakdown
        assert 'financial_score' in breakdown
        assert 'condition_score' in breakdown
        assert 'location_score' in breakdown


# ========================================
# REPORTER TESTS
# ========================================

class TestReporter:
    """Test report generation"""

    def test_excel_report_generation(self, test_config, sample_property, tmp_path):
        """Test Excel report creation"""
        reporter = ReportGenerator(test_config)

        # Add analysis data
        sample_property['opportunity_score'] = 85
        sample_property['deal_quality'] = 'GOOD OPPORTUNITY'
        sample_property['below_market_percentage'] = 15.5
        sample_property['estimated_profit'] = 100000

        properties = [sample_property]

        # Generate report
        filepath = tmp_path / "test_report.xlsx"
        result = reporter.generate_excel_report(properties, str(filepath))

        assert os.path.exists(filepath)
        assert os.path.getsize(filepath) > 0

    def test_email_report_generation(self, test_config, sample_property):
        """Test HTML email generation"""
        reporter = ReportGenerator(test_config)

        sample_property['opportunity_score'] = 90
        sample_property['deal_quality'] = 'HOT DEAL'

        properties = [sample_property]
        stats = {'analyzed': 1, 'hot_deals': 1}

        html = reporter.generate_daily_email_report(properties, stats)

        assert html is not None
        assert len(html) > 0
        assert 'TEST_PROP_001' in html or '123 Test Street' in html


# ========================================
# NOTIFIER TESTS
# ========================================

class TestNotifier:
    """Test notification system"""

    def test_notifier_initialization(self, test_config):
        """Test notifier can initialize"""
        notifier = Notifier(test_config)
        assert notifier is not None

    def test_email_formatting(self, test_config, sample_property):
        """Test email message formatting"""
        notifier = Notifier(test_config)

        # Test hot deal SMS format (even though we won't send)
        # Just verify it doesn't crash
        try:
            # This won't actually send (SMS disabled in test config)
            notifier.send_hot_deal_sms(sample_property)
        except Exception as e:
            pytest.fail(f"SMS formatting failed: {e}")


# ========================================
# WORKFLOW INTEGRATION TESTS
# ========================================

class TestWorkflow:
    """Test complete workflow integration"""

    def test_property_lifecycle(self, test_db, test_config, sample_property):
        """Test complete property lifecycle"""
        # 1. Insert property
        property_id = test_db.insert_property(sample_property)
        assert property_id > 0

        # 2. Analyze property
        analyzer = PropertyAnalyzer(test_db, test_config)
        analysis = analyzer.analyze_property(sample_property)

        # 3. Update with analysis results
        sample_property.update(analysis)
        test_db.update_property(sample_property['property_id'], analysis)

        # 4. Retrieve and verify
        retrieved = test_db.get_property_by_id(sample_property['property_id'])
        assert retrieved['opportunity_score'] == analysis['opportunity_score']

    def test_buyer_matching_workflow(self, test_db, sample_property, sample_buyer):
        """Test buyer matching workflow"""
        # 1. Insert property
        prop_id = test_db.insert_property(sample_property)

        # 2. Insert buyer
        buyer_id = test_db.upsert_buyer(sample_buyer)

        # 3. Create match
        match_data = {
            'match_score': 85,
            'match_reasons': json.dumps(['Budget match', 'Location match'])
        }
        match_id = test_db.insert_property_match(prop_id, buyer_id, match_data)

        assert match_id > 0

        # 4. Retrieve matches
        matches = test_db.get_matches_for_property(prop_id)
        assert len(matches) == 1
        assert matches[0]['match_score'] == 85


# ========================================
# PERFORMANCE TESTS
# ========================================

class TestPerformance:
    """Test performance with larger datasets"""

    def test_bulk_insert_performance(self, test_db, sample_property):
        """Test bulk property insertion"""
        import time

        start = time.time()

        # Insert 100 properties
        for i in range(100):
            prop = sample_property.copy()
            prop['property_id'] = f'TEST_PROP_{i:03d}'
            prop['street_address'] = f'{i} Test Street'
            test_db.insert_property(prop)

        duration = time.time() - start

        # Should complete in reasonable time
        assert duration < 5.0  # Less than 5 seconds for 100 inserts

        # Verify count
        results = test_db.get_properties_by_criteria({})
        assert len(results) == 100


# ========================================
# ERROR HANDLING TESTS
# ========================================

class TestErrorHandling:
    """Test error handling and edge cases"""

    def test_invalid_property_data(self, test_db, test_config):
        """Test handling of invalid property data"""
        analyzer = PropertyAnalyzer(test_db, test_config)

        # Missing required fields
        invalid_property = {
            'property_id': 'INVALID_001'
            # Missing most required fields
        }

        # Should handle gracefully
        try:
            result = analyzer.analyze_property(invalid_property)
            # Should return some result even with bad data
            assert result is not None
        except Exception as e:
            # If it raises exception, it should be a known error type
            assert isinstance(e, (ValueError, KeyError))

    def test_database_duplicate_handling(self, test_db, sample_property):
        """Test duplicate property handling"""
        # Insert once
        id1 = test_db.insert_property(sample_property)

        # Try to insert again (should update, not error)
        id2 = test_db.insert_property(sample_property)

        # Should return same ID (update, not insert)
        assert id1 == id2

        # Verify only one record
        results = test_db.get_properties_by_criteria(
            {'property_id': sample_property['property_id']}
        )
        assert len(results) == 1


# ========================================
# RUN TESTS
# ========================================

if __name__ == '__main__':
    # Run with: python -m pytest tests/test_integration.py -v
    pytest.main([__file__, '-v', '--tb=short'])
