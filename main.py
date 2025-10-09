#!/usr/bin/env python3
"""
DealFinder Pro - Real Estate Investment Automation Platform
Main orchestration script

Usage:
    python main.py --full-workflow                 # Run complete daily workflow
    python main.py --test-ghl                      # Test GHL connection
    python main.py --test-db                       # Test database connection
    python main.py --test-scrape 90210             # Test scraping single ZIP
    python main.py --analyze-property PROP123      # Analyze single property
    python main.py --generate-report               # Generate reports only
"""

import argparse
import logging
import sys
from datetime import datetime
from typing import Dict, List, Optional
import json
import os
from dotenv import load_dotenv

# Import all modules
from modules.database import DatabaseManager
from modules.scraper import RealtorScraper
from modules.data_enrichment import DataEnrichment
from modules.analyzer import PropertyAnalyzer
from modules.scorer import OpportunityScorer
from modules.reporter import ReportGenerator
from modules.sync_manager import SyncManager
from modules.notifier import Notifier

from integrations.ghl_connector import GoHighLevelConnector
from integrations.ghl_workflows import GHLWorkflowManager
from integrations.ghl_buyer_matcher import BuyerMatcher
from integrations.mls_connector import MLSConnector

# Load environment variables
load_dotenv()


class DealFinderPro:
    """Main application orchestrator"""

    def __init__(self, config_path: str = 'config.json'):
        """
        Initialize DealFinder Pro application

        Args:
            config_path: Path to configuration JSON file
        """
        # Load configuration
        self.config_path = config_path
        with open(config_path) as f:
            self.config = json.load(f)

        # Setup logging first
        self._setup_logging()

        # Initialize all modules
        self.logger.info("=" * 60)
        self.logger.info("Initializing DealFinder Pro...")
        self.logger.info("=" * 60)
        self._initialize_modules()

        self.logger.info("Initialization complete!")

    def _setup_logging(self):
        """Configure logging system with console and file handlers"""
        log_config = self.config.get('logging', {})
        level = getattr(logging, log_config.get('level', 'INFO'))

        # Create logs directory if needed
        os.makedirs('logs', exist_ok=True)

        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(level)

        # File handler (daily rotation)
        log_file = f"logs/app_{datetime.now().strftime('%Y%m%d')}.log"
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(level)

        # Formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        console_handler.setFormatter(formatter)
        file_handler.setFormatter(formatter)

        # Root logger configuration
        logging.basicConfig(
            level=level,
            handlers=[console_handler, file_handler]
        )

        self.logger = logging.getLogger(__name__)
        self.logger.info(f"Logging initialized - Level: {log_config.get('level', 'INFO')}")

    def _initialize_modules(self):
        """Initialize all system modules"""
        try:
            # Database
            self.logger.info("Initializing database...")
            db_config = self.config.get('databases', {}).get('primary', {})
            # Add database credentials from environment
            db_config['user'] = os.getenv('DB_USER', 'postgres')
            db_config['password'] = os.getenv('DB_PASSWORD', '')
            db_config['db_type'] = db_config.get('type', 'postgresql')
            self.db = DatabaseManager(db_config)

            # Scraper
            self.logger.info("Initializing scraper...")
            self.scraper = RealtorScraper(self.config)

            # Data enrichment
            self.logger.info("Initializing data enrichment...")
            self.enricher = DataEnrichment(self.config)

            # Analysis modules
            self.logger.info("Initializing analyzers...")
            self.analyzer = PropertyAnalyzer(self.db, self.config)
            self.scorer = OpportunityScorer(self.config)

            # Reporter
            self.logger.info("Initializing reporter...")
            self.reporter = ReportGenerator(self.config)

            # Notifier
            self.logger.info("Initializing notifier...")
            # Add email credentials from environment
            if 'notifications' not in self.config:
                self.config['notifications'] = {}
            if 'email' not in self.config['notifications']:
                self.config['notifications']['email'] = {}

            self.config['notifications']['email']['username'] = os.getenv('EMAIL_USERNAME', '')
            self.config['notifications']['email']['password'] = os.getenv('EMAIL_PASSWORD', '')

            self.notifier = Notifier(self.config)

            # GHL Integration (if enabled)
            if self.config.get('gohighlevel', {}).get('enabled', False):
                self.logger.info("Initializing GHL integration...")
                ghl_api_key = os.getenv('GHL_API_KEY')
                ghl_location_id = os.getenv('GHL_LOCATION_ID')

                if ghl_api_key and ghl_location_id:
                    self.ghl = GoHighLevelConnector(ghl_api_key, ghl_location_id)
                    self.ghl_workflows = GHLWorkflowManager(self.ghl, self.config)
                    self.buyer_matcher = BuyerMatcher(self.ghl, self.db, self.config)
                    self.sync_manager = SyncManager(self.db, self.ghl, self.config)
                    self.logger.info("GHL integration initialized")
                else:
                    self.logger.warning("GHL enabled but API credentials not found in environment")
                    self.ghl = None
            else:
                self.ghl = None
                self.logger.info("GHL integration disabled")

            # MLS Connector (if enabled)
            if self.config.get('databases', {}).get('mls_database', {}).get('enabled', False):
                self.logger.info("Initializing MLS connector...")
                self.mls = MLSConnector(self.config)
            else:
                self.mls = None
                self.logger.info("MLS integration disabled")

        except Exception as e:
            self.logger.error(f"Initialization failed: {e}", exc_info=True)
            raise

    def run_full_workflow(self):
        """Execute complete daily workflow"""
        self.logger.info("")
        self.logger.info("=" * 60)
        self.logger.info("Starting DealFinder Pro Full Workflow")
        self.logger.info("=" * 60)
        self.logger.info("")

        start_time = datetime.now()
        stats = {}

        try:
            # Step 1: Import from MLS (if configured)
            if self.mls:
                self.logger.info("Step 1: Importing from MLS database...")
                mls_properties = self._import_from_mls()
                stats['mls_imported'] = len(mls_properties)
            else:
                self.logger.info("Step 1: Skipping MLS import (not configured)")
                mls_properties = []
                stats['mls_imported'] = 0

            # Step 2: Scrape Realtor.com
            self.logger.info("")
            self.logger.info("Step 2: Scraping Realtor.com...")
            scraped_properties = self._scrape_properties()
            stats['scraped'] = len(scraped_properties)

            # Step 3: Merge and deduplicate
            self.logger.info("")
            self.logger.info("Step 3: Merging and deduplicating...")
            all_properties = mls_properties + scraped_properties
            unique_properties = self.enricher.deduplicate_properties(all_properties)
            stats['unique'] = len(unique_properties)
            stats['duplicates_removed'] = len(all_properties) - len(unique_properties)
            self.logger.info(f"Removed {stats['duplicates_removed']} duplicates")

            # Step 4: Analyze properties
            self.logger.info("")
            self.logger.info("Step 4: Analyzing properties...")
            analyzed_properties = self._analyze_properties(unique_properties)
            stats['analyzed'] = len(analyzed_properties)

            # Step 5: Store in database
            self.logger.info("")
            self.logger.info("Step 5: Storing in database...")
            self._store_properties(analyzed_properties)

            # Step 6: Import buyers from GHL
            if self.ghl:
                self.logger.info("")
                self.logger.info("Step 6: Importing buyers from GHL...")
                buyers_imported = self.sync_manager.sync_buyers_from_ghl()
                stats['buyers_imported'] = buyers_imported.get('imported', 0)
            else:
                stats['buyers_imported'] = 0

            # Step 7: Match properties to buyers
            if self.ghl:
                self.logger.info("")
                self.logger.info("Step 7: Matching properties to buyers...")
                match_stats = self._match_properties_to_buyers(analyzed_properties)
                stats['matches'] = match_stats
            else:
                stats['matches'] = {'total_matches': 0, 'notified_buyers': 0}

            # Step 8: Create GHL opportunities
            if self.ghl:
                self.logger.info("")
                self.logger.info("Step 8: Creating GHL opportunities...")
                ghl_stats = self._sync_to_ghl(analyzed_properties)
                stats['ghl'] = ghl_stats
            else:
                stats['ghl'] = {'opportunities_created': 0, 'workflows_triggered': 0, 'tasks_created': 0}

            # Step 9: Generate reports
            self.logger.info("")
            self.logger.info("Step 9: Generating reports...")
            excel_path = self._generate_reports(analyzed_properties, stats)

            # Step 10: Send notifications
            self.logger.info("")
            self.logger.info("Step 10: Sending notifications...")
            self._send_notifications(analyzed_properties, stats, excel_path)

            # Complete
            duration = (datetime.now() - start_time).total_seconds()
            stats['duration_seconds'] = duration

            self.logger.info("")
            self.logger.info("=" * 60)
            self.logger.info("Workflow Complete!")
            self.logger.info("=" * 60)
            self.logger.info(f"Duration: {duration:.1f} seconds")
            self.logger.info("")
            self.logger.info("Summary Statistics:")
            self.logger.info(f"  - Properties Scraped: {stats['scraped']}")
            self.logger.info(f"  - Unique Properties: {stats['unique']}")
            self.logger.info(f"  - Properties Analyzed: {stats['analyzed']}")
            self.logger.info(f"  - GHL Opportunities: {stats['ghl']['opportunities_created']}")
            self.logger.info(f"  - Buyer Matches: {stats['matches']['total_matches']}")
            self.logger.info("=" * 60)

            return stats

        except Exception as e:
            self.logger.error(f"Workflow failed: {e}", exc_info=True)
            self.notifier.send_error_alert(str(e))
            raise

    def _import_from_mls(self) -> List[Dict]:
        """Import properties from MLS database"""
        with self.mls.connect() as mls:
            properties = mls.fetch_new_listings(hours_back=24)
            self.logger.info(f"Imported {len(properties)} properties from MLS")
            return properties

    def _scrape_properties(self) -> List[Dict]:
        """Scrape properties from Realtor.com"""
        locations = self.config['search_criteria']['target_locations']
        days_back = self.config['search_criteria'].get('days_back', 30)
        all_properties = []

        for location in locations:
            try:
                self.logger.info(f"  Scraping: {location}")
                properties = self.scraper.scrape_zip_code(
                    zip_code=location,
                    days_back=days_back
                )
                all_properties.extend(properties)
                self.logger.info(f"    Found {len(properties)} properties")
            except Exception as e:
                self.logger.error(f"Failed to scrape {location}: {e}")

        self.logger.info(f"Total scraped: {len(all_properties)} properties")
        return all_properties

    def _analyze_properties(self, properties: List[Dict]) -> List[Dict]:
        """Analyze and score all properties"""
        analyzed = []

        self.logger.info(f"Analyzing {len(properties)} properties...")

        for i, prop in enumerate(properties, 1):
            try:
                # Analyze property
                analysis = self.analyzer.analyze_property(prop)

                # Merge analysis results into property data
                prop.update(analysis)

                analyzed.append(prop)

                # Log progress every 10 properties
                if i % 10 == 0:
                    self.logger.info(f"  Progress: {i}/{len(properties)}")

            except Exception as e:
                self.logger.warning(f"Failed to analyze property {prop.get('street_address')}: {e}")

        self.logger.info(f"Successfully analyzed {len(analyzed)}/{len(properties)} properties")
        return analyzed

    def _store_properties(self, properties: List[Dict]):
        """Store properties in database"""
        stored_count = 0
        for prop in properties:
            try:
                self.db.insert_property(prop)
                stored_count += 1
            except Exception as e:
                self.logger.warning(f"Failed to store property: {e}")

        self.logger.info(f"Stored {stored_count}/{len(properties)} properties in database")

    def _match_properties_to_buyers(self, properties: List[Dict]) -> Dict:
        """Match properties to GHL buyers"""
        total_matches = 0
        notified_buyers = 0

        # Filter to high-scoring properties
        min_score = self.config.get('gohighlevel', {}).get('automation_rules', {}).get('min_score_for_opportunity', 70)
        high_score_properties = [p for p in properties
                                if p.get('opportunity_score', 0) >= min_score]

        self.logger.info(f"Matching {len(high_score_properties)} high-scoring properties to buyers...")

        for prop in high_score_properties:
            try:
                matches = self.buyer_matcher.match_property_to_buyers(prop)

                if matches:
                    # Store matches in database
                    for buyer in matches:
                        self.db.insert_property_match(
                            property_id=prop.get('id'),
                            buyer_id=buyer['id'],
                            match_data={
                                'match_score': buyer['match_score'],
                                'match_reasons': json.dumps(buyer['match_reasons'])
                            }
                        )

                    # Notify matched buyers
                    notify_stats = self.buyer_matcher.notify_matched_buyers(prop, matches)
                    total_matches += len(matches)
                    notified_buyers += notify_stats.get('notified', 0)

            except Exception as e:
                self.logger.warning(f"Failed to match property: {e}")

        self.logger.info(f"Created {total_matches} matches, notified {notified_buyers} buyers")

        return {
            'total_matches': total_matches,
            'notified_buyers': notified_buyers
        }

    def _sync_to_ghl(self, properties: List[Dict]) -> Dict:
        """Sync high-scoring properties to GHL"""
        min_score = self.config.get('gohighlevel', {}).get('automation_rules', {}).get('min_score_for_opportunity', 75)
        hot_deal_threshold = self.config.get('gohighlevel', {}).get('automation_rules', {}).get('hot_deal_threshold', 90)

        high_score_props = [p for p in properties if p.get('opportunity_score', 0) >= min_score]

        self.logger.info(f"Syncing {len(high_score_props)} high-scoring properties to GHL...")

        opportunities_created = 0
        workflows_triggered = 0
        tasks_created = 0

        for prop in high_score_props:
            try:
                # Create opportunity
                opp_id = self.ghl_workflows.create_opportunity_from_property(prop)
                opportunities_created += 1

                # Create tasks
                task_ids = self.ghl_workflows.create_tasks_for_property(prop, opp_id)
                tasks_created += len(task_ids)

                # Trigger hot deal workflow if score >= threshold
                if prop.get('opportunity_score', 0) >= hot_deal_threshold:
                    self.ghl_workflows.trigger_hot_deal_workflow(prop, opp_id)
                    workflows_triggered += 1

                # Update database with GHL opportunity ID
                self.db.mark_property_synced(prop.get('property_id'), opp_id)

            except Exception as e:
                self.logger.warning(f"Failed to sync property to GHL: {e}")

        self.logger.info(f"GHL sync complete: {opportunities_created} opportunities, {workflows_triggered} workflows, {tasks_created} tasks")

        return {
            'opportunities_created': opportunities_created,
            'workflows_triggered': workflows_triggered,
            'tasks_created': tasks_created
        }

    def _generate_reports(self, properties: List[Dict], stats: Dict) -> str:
        """Generate email and Excel reports"""
        os.makedirs('reports', exist_ok=True)

        # Excel report
        excel_filename = f"dealfinder_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        excel_path = os.path.join('reports', excel_filename)
        self.reporter.generate_excel_report(properties, excel_path)
        self.logger.info(f"Excel report generated: {excel_path}")

        # HTML email report
        self.email_html = self.reporter.generate_daily_email_report(properties, stats)
        self.logger.info("Email HTML report generated")

        return excel_path

    def _send_notifications(self, properties: List[Dict], stats: Dict, excel_path: str):
        """Send email and SMS notifications"""
        # Daily email report
        self.notifier.send_daily_report(self.email_html, stats, excel_path)
        self.logger.info("Daily email report sent")

        # SMS for hot deals
        hot_deal_threshold = self.config.get('gohighlevel', {}).get('automation_rules', {}).get('hot_deal_threshold', 90)
        hot_deals = [p for p in properties if p.get('opportunity_score', 0) >= hot_deal_threshold]

        for deal in hot_deals:
            self.notifier.send_hot_deal_sms(deal)

        if hot_deals:
            self.logger.info(f"Sent SMS alerts for {len(hot_deals)} hot deals")

    # ========================================
    # CLI COMMAND METHODS
    # ========================================

    def test_ghl_connection(self):
        """Test GHL API connection"""
        if self.ghl:
            self.logger.info("Testing GHL connection...")
            result = self.ghl.test_connection()
            if result:
                self.logger.info("✅ GHL connection successful!")
                return True
            else:
                self.logger.error("❌ GHL connection failed")
                return False
        else:
            self.logger.error("GHL not configured")
            return False

    def test_database_connection(self):
        """Test database connection"""
        self.logger.info("Testing database connection...")
        result = self.db.test_connection()
        if result:
            self.logger.info("✅ Database connection successful!")
            return True
        else:
            self.logger.error("❌ Database connection failed")
            return False

    def run_test_scrape(self, zip_code: str):
        """Test scraping a single ZIP code"""
        self.logger.info(f"Test scraping ZIP code: {zip_code}")
        properties = self.scraper.scrape_zip_code(zip_code, days_back=7)
        self.logger.info(f"Found {len(properties)} properties")

        # Show samples
        if properties:
            self.logger.info("\nSample Properties:")
            for i, prop in enumerate(properties[:3], 1):
                self.logger.info(f"  {i}. {prop.get('street_address')} - ${prop.get('list_price', 0):,}")

        return properties

    def analyze_single_property(self, property_id: str):
        """Analyze a single property by ID"""
        self.logger.info(f"Analyzing property: {property_id}")

        # Fetch from database
        prop = self.db.get_property_by_id(property_id)

        if not prop:
            self.logger.error(f"Property not found: {property_id}")
            return None

        # Analyze
        analysis = self.analyzer.analyze_property(prop)
        prop.update(analysis)

        # Display results
        self.logger.info("\nAnalysis Results:")
        self.logger.info(f"  Address: {prop.get('street_address')}")
        self.logger.info(f"  Opportunity Score: {prop.get('opportunity_score')}/100")
        self.logger.info(f"  Deal Quality: {prop.get('deal_quality')}")
        self.logger.info(f"  Below Market: {prop.get('below_market_percentage', 0):.1f}%")
        self.logger.info(f"  Est. Profit: ${prop.get('estimated_profit', 0):,}")

        return prop

    def generate_reports_only(self):
        """Generate reports from existing database data"""
        self.logger.info("Generating reports from database...")

        # Fetch high-scoring properties
        properties = self.db.get_properties_by_score(min_score=60, limit=100)

        if not properties:
            self.logger.warning("No properties found in database")
            return

        # Generate reports
        stats = {'analyzed': len(properties)}
        excel_path = self._generate_reports(properties, stats)

        self.logger.info(f"Reports generated: {excel_path}")


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description='DealFinder Pro - Real Estate Investment Automation',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py --full-workflow                 Run complete daily workflow
  python main.py --test-ghl                      Test GHL connection
  python main.py --test-db                       Test database connection
  python main.py --test-scrape 90210             Test scraping single ZIP code
  python main.py --analyze-property PROP123      Analyze single property
  python main.py --generate-report               Generate reports only
        """
    )

    parser.add_argument('--config', default='config.json', help='Path to config file')
    parser.add_argument('--full-workflow', action='store_true', help='Run complete daily workflow')
    parser.add_argument('--test-ghl', action='store_true', help='Test GHL connection')
    parser.add_argument('--test-db', action='store_true', help='Test database connection')
    parser.add_argument('--test-scrape', type=str, metavar='ZIP', help='Test scraping (provide ZIP code)')
    parser.add_argument('--analyze-property', type=str, metavar='ID', help='Analyze single property by ID')
    parser.add_argument('--generate-report', action='store_true', help='Generate reports only')

    args = parser.parse_args()

    # Check if config file exists
    if not os.path.exists(args.config):
        print(f"Error: Config file not found: {args.config}")
        print("Please create config.json or specify --config path")
        sys.exit(1)

    # Initialize application
    try:
        app = DealFinderPro(config_path=args.config)
    except Exception as e:
        print(f"Error initializing application: {e}")
        sys.exit(1)

    # Execute command
    try:
        if args.full_workflow:
            app.run_full_workflow()

        elif args.test_ghl:
            app.test_ghl_connection()

        elif args.test_db:
            app.test_database_connection()

        elif args.test_scrape:
            app.run_test_scrape(args.test_scrape)

        elif args.analyze_property:
            app.analyze_single_property(args.analyze_property)

        elif args.generate_report:
            app.generate_reports_only()

        else:
            parser.print_help()

    except KeyboardInterrupt:
        print("\n\nOperation cancelled by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n\nError: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
