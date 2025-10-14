"""
Configuration Manager
Handles reading and writing config.json
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Any

class ConfigManager:
    """Manages application configuration"""

    def __init__(self, config_path: str = None):
        if config_path is None:
            # Default to config.json in parent directory
            dashboard_dir = Path(__file__).parent.parent
            project_root = dashboard_dir.parent
            config_path = project_root / 'config.json'

        self.config_path = str(config_path)

    def load_config(self) -> Dict:
        """Load configuration from JSON file"""
        try:
            with open(self.config_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return self._get_default_config()
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in config file: {e}")

    def save_config(self, config: Dict) -> bool:
        """Save configuration to JSON file"""
        try:
            with open(self.config_path, 'w') as f:
                json.dump(config, f, indent=2)
            return True
        except Exception as e:
            raise ValueError(f"Failed to save config: {e}")

    def get_search_locations(self) -> List[str]:
        """Get target search locations"""
        config = self.load_config()
        return config.get('search_criteria', {}).get('target_locations', [])

    def add_location(self, location: str) -> bool:
        """Add a new search location"""
        config = self.load_config()

        if 'search_criteria' not in config:
            config['search_criteria'] = {}

        if 'target_locations' not in config['search_criteria']:
            config['search_criteria']['target_locations'] = []

        locations = config['search_criteria']['target_locations']

        if location not in locations:
            locations.append(location)
            return self.save_config(config)

        return False  # Already exists

    def remove_location(self, location: str) -> bool:
        """Remove a search location"""
        config = self.load_config()

        locations = config.get('search_criteria', {}).get('target_locations', [])

        if location in locations:
            locations.remove(location)
            config['search_criteria']['target_locations'] = locations
            return self.save_config(config)

        return False  # Not found

    def update_price_range(self, min_price: int, max_price: int) -> bool:
        """Update price range"""
        config = self.load_config()

        if 'search_criteria' not in config:
            config['search_criteria'] = {}

        if 'price_range' not in config['search_criteria']:
            config['search_criteria']['price_range'] = {}

        config['search_criteria']['price_range']['min'] = min_price
        config['search_criteria']['price_range']['max'] = max_price

        return self.save_config(config)

    def get_price_range(self) -> Dict[str, int]:
        """Get current price range"""
        config = self.load_config()
        return config.get('search_criteria', {}).get('price_range', {'min': 200000, 'max': 2000000})

    def update_property_types(self, property_types: List[str]) -> bool:
        """Update property types filter"""
        config = self.load_config()

        if 'search_criteria' not in config:
            config['search_criteria'] = {}

        config['search_criteria']['property_types'] = property_types
        return self.save_config(config)

    def get_property_types(self) -> List[str]:
        """Get current property types"""
        config = self.load_config()
        return config.get('search_criteria', {}).get('property_types', [])

    def update_search_criteria(self, **kwargs) -> bool:
        """Update multiple search criteria at once"""
        config = self.load_config()

        if 'search_criteria' not in config:
            config['search_criteria'] = {}

        for key, value in kwargs.items():
            config['search_criteria'][key] = value

        return self.save_config(config)

    def get_search_criteria(self) -> Dict:
        """Get all search criteria"""
        config = self.load_config()
        return config.get('search_criteria', {})

    def get_ghl_config(self) -> Dict:
        """Get GHL configuration"""
        config = self.load_config()
        return config.get('gohighlevel', {})

    def _get_default_config(self) -> Dict:
        """Return default configuration"""
        return {
            "search_criteria": {
                "target_locations": [],
                "listing_type": "for_sale",
                "days_back": 30,
                "property_types": ["single_family", "multi_family", "condo", "townhouse"],
                "min_bedrooms": 2,
                "min_bathrooms": 2,
                "price_range": {
                    "min": 200000,
                    "max": 2000000
                }
            },
            "gohighlevel": {
                "enabled": True,
                "automation_rules": {
                    "min_score_for_opportunity": 75,
                    "hot_deal_threshold": 90
                }
            }
        }
