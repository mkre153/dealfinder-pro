from homeharvest import scrape_property
from typing import Dict, List, Optional
import logging
import time
import json
from datetime import datetime, timedelta
import pandas as pd

class RealtorScraper:
    """Scrapes Realtor.com using HomeHarvest library"""

    def __init__(self, config: Dict):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.rate_limit_delay = config.get('scraping', {}).get('rate_limit_delay', 1.0)
        self.max_retries = config.get('scraping', {}).get('max_retries', 3)
        self.logger.info("RealtorScraper initialized with rate limit delay: %s seconds", self.rate_limit_delay)

    def scrape_zip_code(self, zip_code: str, listing_type: str = "for_sale",
                        days_back: int = 30) -> List[Dict]:
        """
        Scrape properties from a single ZIP code using HomeHarvest.

        Args:
            zip_code: ZIP code to scrape
            listing_type: Type of listings ("for_sale", "sold", "for_rent")
            days_back: Number of days to look back for listings

        Returns:
            List of property dictionaries
        """
        self.logger.info("Scraping ZIP code: %s (type: %s, days_back: %d)",
                        zip_code, listing_type, days_back)

        for attempt in range(1, self.max_retries + 1):
            try:
                # Use HomeHarvest scrape_property function
                df = scrape_property(
                    location=zip_code,
                    listing_type=listing_type,
                    past_days=days_back
                )

                if df is None or df.empty:
                    self.logger.warning("No properties found for ZIP code: %s", zip_code)
                    return []

                # Convert DataFrame to list of dictionaries
                raw_properties = df.to_dict('records')

                # Extract and transform property details
                properties = []
                for raw_data in raw_properties:
                    try:
                        property_data = self.extract_property_details(raw_data)
                        properties.append(property_data)
                    except Exception as e:
                        self.logger.error("Error extracting property details: %s", str(e))
                        continue

                self.logger.info("Successfully scraped %d properties from ZIP %s",
                               len(properties), zip_code)
                return properties

            except Exception as e:
                error_msg = str(e)

                # Check for CAPTCHA
                if self.detect_captcha(error_msg):
                    self.logger.error("CAPTCHA detected for ZIP %s. Manual intervention required.",
                                    zip_code)
                    raise RuntimeError(f"CAPTCHA detected for ZIP {zip_code}")

                self.logger.warning("Attempt %d/%d failed for ZIP %s: %s",
                                  attempt, self.max_retries, zip_code, error_msg)

                if attempt < self.max_retries:
                    # Exponential backoff
                    wait_time = self.rate_limit_delay * (2 ** (attempt - 1))
                    self.logger.info("Retrying in %s seconds...", wait_time)
                    time.sleep(wait_time)
                else:
                    self.logger.error("Failed to scrape ZIP %s after %d attempts",
                                    zip_code, self.max_retries)
                    raise

        return []

    def scrape_multiple_locations(self, locations: List[str]) -> List[Dict]:
        """
        Scrape properties from multiple ZIP codes or cities.

        Args:
            locations: List of ZIP codes or city names

        Returns:
            Aggregated list of property dictionaries
        """
        self.logger.info("Scraping %d locations", len(locations))
        all_properties = []

        for i, location in enumerate(locations, 1):
            self.logger.info("Processing location %d/%d: %s", i, len(locations), location)

            try:
                properties = self.scrape_zip_code(location)
                all_properties.extend(properties)

                # Rate limiting between locations
                if i < len(locations):
                    self.logger.debug("Rate limiting: waiting %s seconds", self.rate_limit_delay)
                    time.sleep(self.rate_limit_delay)

            except Exception as e:
                self.logger.error("Failed to scrape location %s: %s", location, str(e))
                continue

        self.logger.info("Total properties scraped from all locations: %d", len(all_properties))
        return all_properties

    def scrape_city(self, city: str, state: str, days_back: int = 30) -> List[Dict]:
        """
        Scrape properties by city name instead of ZIP code.

        Args:
            city: City name
            state: State abbreviation (e.g., "CA")
            days_back: Number of days to look back

        Returns:
            List of property dictionaries
        """
        location = f"{city}, {state}"
        self.logger.info("Scraping city: %s", location)

        return self.scrape_zip_code(location, days_back=days_back)

    def extract_property_details(self, raw_data: Dict) -> Dict:
        """
        Transform HomeHarvest output to internal schema.

        Args:
            raw_data: Raw property data from HomeHarvest

        Returns:
            Normalized property dictionary
        """
        # HomeHarvest returns different field names, normalize them
        property_data = {
            'data_source': 'realtor_com',
            'scrape_timestamp': datetime.now().isoformat(),

            # Property identifiers
            'mls_number': raw_data.get('mls_id') or raw_data.get('mls'),
            'property_id': raw_data.get('property_id'),

            # Address information
            'street_address': raw_data.get('street') or raw_data.get('full_street_line') or raw_data.get('address'),
            'city': raw_data.get('city'),
            'state': raw_data.get('state'),
            'zip_code': raw_data.get('zip_code') or raw_data.get('postal_code'),
            'county': raw_data.get('county'),
            'latitude': raw_data.get('latitude'),
            'longitude': raw_data.get('longitude'),

            # Price information
            'list_price': self._safe_float(raw_data.get('list_price') or raw_data.get('price')),
            'price_per_sqft': self._safe_float(raw_data.get('price_per_sqft')),

            # Property characteristics
            'bedrooms': self._safe_int(raw_data.get('beds') or raw_data.get('bedrooms')),
            'bathrooms': self._safe_float(raw_data.get('baths') or raw_data.get('bathrooms')),
            'square_feet': self._safe_int(raw_data.get('sqft') or raw_data.get('square_feet')),
            'lot_size_sqft': self._safe_int(raw_data.get('lot_sqft') or raw_data.get('lot_size')),
            'year_built': self._safe_int(raw_data.get('year_built')),
            'property_type': raw_data.get('property_type') or raw_data.get('type'),
            'stories': self._safe_int(raw_data.get('stories')),

            # Listing information
            'listing_date': raw_data.get('list_date') or raw_data.get('listing_date'),
            'days_on_market': self._safe_int(raw_data.get('days_on_mls') or raw_data.get('days_on_market')),
            'status': raw_data.get('status'),

            # Agent information
            'listing_agent_name': raw_data.get('agent_name') or raw_data.get('listing_agent'),
            'listing_agent_phone': raw_data.get('agent_phone'),
            'broker_name': raw_data.get('broker_name'),

            # Property details
            'description': raw_data.get('description') or raw_data.get('text'),
            'hoa_fee': self._safe_float(raw_data.get('hoa_fee')),
            'parking_garage': self._safe_int(raw_data.get('parking_garage') or raw_data.get('garage')),

            # Photos and media
            'photo_count': self._safe_int(raw_data.get('photo_count')),
            'primary_photo': raw_data.get('primary_photo') or raw_data.get('thumbnail'),
            'photos': raw_data.get('photos', []),

            # Tax information
            'tax_assessed_value': self._safe_float(raw_data.get('assessed_value')),
            'annual_taxes': self._safe_float(raw_data.get('tax_amount') or raw_data.get('annual_taxes')),

            # URLs
            'listing_url': raw_data.get('property_url') or raw_data.get('url'),
        }

        # Remove None values to keep data clean
        property_data = {k: v for k, v in property_data.items() if v is not None}

        return property_data

    def _safe_int(self, value) -> Optional[int]:
        """Safely convert value to int"""
        if value is None or value == '':
            return None
        try:
            return int(float(value))
        except (ValueError, TypeError):
            return None

    def _safe_float(self, value) -> Optional[float]:
        """Safely convert value to float"""
        if value is None or value == '':
            return None
        try:
            return float(value)
        except (ValueError, TypeError):
            return None

    def detect_captcha(self, response: str) -> bool:
        """
        Check if CAPTCHA page was returned.

        Args:
            response: Response string or error message

        Returns:
            True if CAPTCHA detected
        """
        captcha_indicators = [
            'captcha',
            'recaptcha',
            'bot detection',
            'automated access',
            'verify you are human'
        ]

        response_lower = str(response).lower()
        return any(indicator in response_lower for indicator in captcha_indicators)

    def save_raw_data(self, properties: List[Dict], filepath: str):
        """
        Save scraped properties to JSON file for backup.

        Args:
            properties: List of property dictionaries
            filepath: Path to save JSON file
        """
        try:
            data = {
                'scrape_timestamp': datetime.now().isoformat(),
                'property_count': len(properties),
                'properties': properties
            }

            with open(filepath, 'w') as f:
                json.dump(data, f, indent=2, default=str)

            self.logger.info("Saved %d properties to %s", len(properties), filepath)

        except Exception as e:
            self.logger.error("Failed to save raw data to %s: %s", filepath, str(e))
            raise
