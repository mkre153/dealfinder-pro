"""
Scheduler Component
Manages automated property scanning with APScheduler
"""

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime
import logging
import json
from pathlib import Path
from typing import Dict, List, Callable, Optional

# Python 3.9 compatibility
import sys
if sys.version_info < (3, 10):
    from typing import Dict as dict, List as list

logger = logging.getLogger(__name__)


class PropertyScanner:
    """Manages scheduled property scanning"""

    def __init__(self, config_path: str = None):
        """Initialize scheduler with config"""
        if config_path is None:
            config_path = Path(__file__).parent.parent.parent / 'config.json'

        with open(config_path) as f:
            self.config = json.load(f)

        self.scheduler = BackgroundScheduler()
        self.scan_history = []
        self.is_running = False

    def start(self):
        """Start the scheduler"""
        if self.is_running:
            logger.warning("Scheduler already running")
            return

        # Get scan times from config
        schedule_config = self.config.get('scheduling', {})
        scan_times = schedule_config.get('scan_times', [])
        timezone = schedule_config.get('timezone', 'America/Los_Angeles')

        # Add jobs for each scan time
        for scan_time in scan_times:
            if scan_time.get('enabled', True):
                time_str = scan_time['time']
                hour, minute = map(int, time_str.split(':'))
                label = scan_time.get('label', f'Scan at {time_str}')

                self.scheduler.add_job(
                    self._run_scan,
                    CronTrigger(hour=hour, minute=minute, timezone=timezone),
                    id=f'scan_{time_str}',
                    name=label,
                    replace_existing=True
                )
                logger.info(f"Scheduled: {label} at {time_str}")

        self.scheduler.start()
        self.is_running = True
        logger.info("Scheduler started successfully")

    def stop(self):
        """Stop the scheduler"""
        if self.scheduler.running:
            self.scheduler.shutdown(wait=False)
            self.is_running = False
            logger.info("Scheduler stopped")

    def pause(self):
        """Pause all scheduled jobs"""
        self.scheduler.pause()
        logger.info("Scheduler paused")

    def resume(self):
        """Resume scheduled jobs"""
        self.scheduler.resume()
        logger.info("Scheduler resumed")

    def _run_scan(self):
        """Execute property scan (called by scheduler)"""
        logger.info("=" * 60)
        logger.info(f"Starting scheduled scan at {datetime.now()}")
        logger.info("=" * 60)

        scan_result = {
            'timestamp': datetime.now().isoformat(),
            'status': 'started',
            'properties_found': 0,
            'errors': []
        }

        try:
            # Import here to avoid circular imports
            from components.scraper_runner import ScraperRunner
            from modules.analyzer import PropertyAnalyzer
            from components.config_manager import ConfigManager

            config_mgr = ConfigManager()
            config = config_mgr.load_config()

            # Get target locations
            locations = config.get('search_criteria', {}).get('target_locations', [])
            days_back = config.get('search_criteria', {}).get('days_back', 30)

            # Run scraper
            scraper = ScraperRunner(config)
            all_properties = []

            for location in locations:
                try:
                    result = scraper.test_scrape(location, days_back)
                    if result['success']:
                        all_properties.extend(result['properties'])
                except Exception as e:
                    logger.error(f"Error scraping {location}: {e}")
                    scan_result['errors'].append(f"{location}: {str(e)}")

            # Analyze properties
            if all_properties:
                try:
                    # Score properties using simple scorer
                    from modules.simple_scorer import SimplePropertyScorer

                    scorer = SimplePropertyScorer(config)
                    scored_properties = scorer.score_properties(all_properties)

                    scan_result['properties_found'] = len(scored_properties)
                    scan_result['status'] = 'completed'

                    # Store in temporary file for dashboard to pick up
                    # (Can't directly modify session state from background thread)
                    temp_file = Path(__file__).parent.parent.parent / 'data' / 'latest_scan.json'
                    temp_file.parent.mkdir(exist_ok=True)

                    with open(temp_file, 'w') as f:
                        json.dump({
                            'timestamp': scan_result['timestamp'],
                            'properties': scored_properties
                        }, f, indent=2)

                    logger.info(f"Scan completed: {len(scored_properties)} properties found and scored")
                    logger.info(f"Results saved to: {temp_file}")

                except Exception as e:
                    logger.error(f"Error analyzing properties: {e}")
                    scan_result['errors'].append(f"Analysis error: {str(e)}")
                    scan_result['status'] = 'completed_with_errors'
            else:
                scan_result['status'] = 'completed'
                logger.info("Scan completed: No properties found")

            # Send notifications
            try:
                from components.notifier import NotificationManager
                notifier = NotificationManager()

                if all_properties:
                    # Filter for qualified deals
                    qualified = [p for p in all_properties
                                if self._is_qualified_deal(p, config)]

                    if qualified:
                        notifier.send_scan_summary(qualified)

            except Exception as e:
                logger.error(f"Error sending notifications: {e}")
                scan_result['errors'].append(f"Notification error: {str(e)}")

        except Exception as e:
            logger.error(f"Scan failed: {e}", exc_info=True)
            scan_result['status'] = 'failed'
            scan_result['errors'].append(str(e))

        # Store scan history
        self.scan_history.append(scan_result)

        # Keep only last 50 scans
        if len(self.scan_history) > 50:
            self.scan_history = self.scan_history[-50:]

        logger.info(f"Scan {scan_result['status']}")
        logger.info("=" * 60)

        return scan_result

    def _is_qualified_deal(self, property_data: Dict, config: Dict) -> bool:
        """Check if property meets qualification criteria"""
        criteria = config.get('undervalued_criteria', {})

        # Check price range
        price_range = config.get('search_criteria', {}).get('price_range', {})
        list_price = property_data.get('list_price', 0)

        if list_price < price_range.get('min', 0) or list_price > price_range.get('max', float('inf')):
            return False

        # Check days on market
        dom = property_data.get('days_on_market', 0)
        min_dom = criteria.get('days_on_market_minimum', 30)

        if dom < min_dom:
            return False

        # If has opportunity score, check that
        if 'opportunity_score' in property_data:
            min_score = criteria.get('min_opportunity_score', 75)
            if property_data['opportunity_score'] < min_score:
                return False

        return True

    def get_next_run_time(self) -> str:
        """Get the next scheduled run time"""
        if not self.scheduler.running:
            return "Scheduler not running"

        jobs = self.scheduler.get_jobs()
        if not jobs:
            return "No jobs scheduled"

        next_run = min(job.next_run_time for job in jobs if job.next_run_time)
        return next_run.strftime("%Y-%m-%d %H:%M:%S %Z")

    def get_scheduled_jobs(self) -> List[Dict]:
        """Get list of all scheduled jobs"""
        jobs = []
        for job in self.scheduler.get_jobs():
            jobs.append({
                'id': job.id,
                'name': job.name,
                'next_run': job.next_run_time.isoformat() if job.next_run_time else None,
                'trigger': str(job.trigger)
            })
        return jobs

    def get_scan_history(self, limit: int = 10) -> List[Dict]:
        """Get recent scan history"""
        return self.scan_history[-limit:]

    def run_manual_scan(self) -> Dict:
        """Run an immediate manual scan"""
        logger.info("Running manual scan...")
        return self._run_scan()

    def update_schedule(self, scan_times: List[Dict]):
        """Update the scan schedule"""
        # Remove existing jobs
        self.scheduler.remove_all_jobs()

        # Update config
        config_path = Path(__file__).parent.parent.parent / 'config.json'
        with open(config_path) as f:
            config = json.load(f)

        config['scheduling']['scan_times'] = scan_times

        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)

        # Restart scheduler if running
        if self.is_running:
            self.stop()
            self.__init__()  # Reload config
            self.start()

        logger.info("Schedule updated")


# Global scheduler instance
_scheduler_instance = None


def get_scheduler() -> PropertyScanner:
    """Get or create global scheduler instance"""
    global _scheduler_instance
    if _scheduler_instance is None:
        _scheduler_instance = PropertyScanner()
    return _scheduler_instance


def start_scheduler():
    """Start the global scheduler"""
    scheduler = get_scheduler()
    if not scheduler.is_running:
        scheduler.start()
    return scheduler


def stop_scheduler():
    """Stop the global scheduler"""
    scheduler = get_scheduler()
    scheduler.stop()
