"""
Scraper Runner
Wrapper for running scrapers from the dashboard
"""

import sys
from pathlib import Path
from typing import List, Dict, Any
import logging

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from modules.scraper import RealtorScraper

class ScraperRunner:
    """Runs scraping operations"""

    def __init__(self, config: Dict):
        self.config = config
        self.scraper = RealtorScraper(config)
        self.logger = logging.getLogger(__name__)

    def test_scrape(self, zip_code: str, days_back: int = 30) -> Dict[str, Any]:
        """
        Test scrape a single ZIP code

        Returns:
            Dict with 'success', 'properties', 'count', 'error' keys
        """
        try:
            properties = self.scraper.scrape_zip_code(
                zip_code=zip_code,
                days_back=days_back
            )

            return {
                'success': True,
                'properties': properties,
                'count': len(properties),
                'error': None
            }

        except Exception as e:
            return {
                'success': False,
                'properties': [],
                'count': 0,
                'error': str(e)
            }

    def scrape_multiple(self, zip_codes: List[str], days_back: int = 30) -> Dict[str, Any]:
        """
        Scrape multiple ZIP codes

        Returns:
            Dict with 'success', 'properties', 'count_by_zip', 'total_count', 'errors' keys
        """
        all_properties = []
        count_by_zip = {}
        errors = {}

        for zip_code in zip_codes:
            try:
                properties = self.scraper.scrape_zip_code(
                    zip_code=zip_code,
                    days_back=days_back
                )
                all_properties.extend(properties)
                count_by_zip[zip_code] = len(properties)

            except Exception as e:
                errors[zip_code] = str(e)
                count_by_zip[zip_code] = 0

        return {
            'success': len(errors) == 0,
            'properties': all_properties,
            'count_by_zip': count_by_zip,
            'total_count': len(all_properties),
            'errors': errors
        }

    def get_property_summary(self, properties: List[Dict]) -> Dict[str, Any]:
        """
        Generate summary statistics for properties

        Returns:
            Dict with summary stats
        """
        if not properties:
            return {
                'count': 0,
                'avg_price': 0,
                'min_price': 0,
                'max_price': 0,
                'cities': []
            }

        prices = [p.get('list_price', 0) for p in properties if p.get('list_price')]
        cities = list(set([p.get('city', 'Unknown') for p in properties if p.get('city')]))

        return {
            'count': len(properties),
            'avg_price': sum(prices) / len(prices) if prices else 0,
            'min_price': min(prices) if prices else 0,
            'max_price': max(prices) if prices else 0,
            'cities': cities
        }
