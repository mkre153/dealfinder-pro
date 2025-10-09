from typing import Dict, List, Optional, Tuple
import logging
from difflib import SequenceMatcher
import re
from datetime import datetime

class DataEnrichment:
    """Merges and enriches data from multiple sources"""

    def __init__(self, config: Dict):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.address_similarity_threshold = 0.90  # 90% similarity for duplicate detection
        self.logger.info("DataEnrichment initialized")

    def merge_property_data(self, source1: Dict, source2: Dict,
                           priority: str = "mls") -> Dict:
        """
        Merge two property records, resolving conflicts based on priority.

        Args:
            source1: First property dictionary
            source2: Second property dictionary
            priority: Which source wins on conflicts ("mls", "realtor", or "newest")

        Returns:
            Merged property dictionary
        """
        merged = {}

        # Determine which source has priority
        if priority == "mls":
            primary = source1 if source1.get('data_source') == 'mls' else source2
            secondary = source2 if source1.get('data_source') == 'mls' else source1
        elif priority == "realtor":
            primary = source1 if source1.get('data_source') == 'realtor_com' else source2
            secondary = source2 if source1.get('data_source') == 'realtor_com' else source1
        elif priority == "newest":
            # Use scrape_timestamp or listing_date to determine newest
            ts1 = source1.get('scrape_timestamp') or source1.get('listing_date', '')
            ts2 = source2.get('scrape_timestamp') or source2.get('listing_date', '')
            primary = source1 if ts1 >= ts2 else source2
            secondary = source1 if ts1 < ts2 else source2
        else:
            primary = source1
            secondary = source2

        # Merge all fields
        all_keys = set(list(source1.keys()) + list(source2.keys()))

        for key in all_keys:
            val1 = source1.get(key)
            val2 = source2.get(key)

            # If both have the value and they're the same, use it
            if val1 == val2:
                merged[key] = val1
                continue

            # Handle arrays/lists - combine them
            if isinstance(val1, list) and isinstance(val2, list):
                # Combine and deduplicate
                combined = val1 + val2
                merged[key] = list(set(combined)) if combined else []
                continue

            # For dates, use most recent
            if key in ('listing_date', 'scrape_timestamp', 'modification_timestamp'):
                if val1 and val2:
                    merged[key] = max(val1, val2)
                else:
                    merged[key] = val1 or val2
                continue

            # For all other fields, use priority source
            if primary.get(key) is not None:
                merged[key] = primary[key]
            elif secondary.get(key) is not None:
                merged[key] = secondary[key]

        # Add merge metadata
        merged['merged_from_sources'] = [
            source1.get('data_source', 'unknown'),
            source2.get('data_source', 'unknown')
        ]
        merged['merge_timestamp'] = datetime.now().isoformat()

        return merged

    def deduplicate_properties(self, properties: List[Dict]) -> List[Dict]:
        """
        Identify and merge duplicate properties.

        Deduplication strategy:
        1. Exact MLS number match
        2. Address fuzzy match (>90% similarity)
        3. Price + sqft + bedrooms exact match

        Args:
            properties: List of property dictionaries

        Returns:
            List of unique properties (duplicates merged)
        """
        self.logger.info("Deduplicating %d properties", len(properties))

        if not properties:
            return []

        unique_properties = []
        processed_indices = set()

        for i, prop in enumerate(properties):
            if i in processed_indices:
                continue

            # Find all duplicates of this property
            duplicates = [prop]
            processed_indices.add(i)

            for j in range(i + 1, len(properties)):
                if j in processed_indices:
                    continue

                if self._is_duplicate(prop, properties[j]):
                    duplicates.append(properties[j])
                    processed_indices.add(j)

            # Merge all duplicates
            if len(duplicates) == 1:
                unique_properties.append(prop)
            else:
                self.logger.debug("Found %d duplicates for property, merging", len(duplicates))
                merged = duplicates[0]
                for dup in duplicates[1:]:
                    merged = self.merge_property_data(merged, dup, priority="mls")
                unique_properties.append(merged)

        self.logger.info("Deduplication complete: %d unique properties (removed %d duplicates)",
                        len(unique_properties), len(properties) - len(unique_properties))

        return unique_properties

    def _is_duplicate(self, prop1: Dict, prop2: Dict) -> bool:
        """
        Determine if two properties are duplicates.

        Args:
            prop1: First property
            prop2: Second property

        Returns:
            True if properties are duplicates
        """
        # Strategy 1: Exact MLS number match
        mls1 = prop1.get('mls_number')
        mls2 = prop2.get('mls_number')
        if mls1 and mls2 and mls1 == mls2:
            return True

        # Strategy 2: Address fuzzy match (>90% similarity)
        addr1 = self.normalize_address(
            f"{prop1.get('street_address', '')} {prop1.get('city', '')} {prop1.get('state', '')} {prop1.get('zip_code', '')}"
        )
        addr2 = self.normalize_address(
            f"{prop2.get('street_address', '')} {prop2.get('city', '')} {prop2.get('state', '')} {prop2.get('zip_code', '')}"
        )

        if addr1 and addr2:
            similarity = self.calculate_address_similarity(addr1, addr2)
            if similarity >= self.address_similarity_threshold:
                return True

        # Strategy 3: Price + sqft + bedrooms exact match (same property likely)
        price1 = prop1.get('list_price')
        price2 = prop2.get('list_price')
        sqft1 = prop1.get('square_feet')
        sqft2 = prop2.get('square_feet')
        beds1 = prop1.get('bedrooms')
        beds2 = prop2.get('bedrooms')

        if all([price1, price2, sqft1, sqft2, beds1, beds2]):
            if price1 == price2 and sqft1 == sqft2 and beds1 == beds2:
                # Also check ZIP code matches to avoid false positives
                if prop1.get('zip_code') == prop2.get('zip_code'):
                    return True

        return False

    def normalize_address(self, address: str) -> str:
        """
        Standardize address format for comparison.

        Args:
            address: Raw address string

        Returns:
            Normalized address string
        """
        if not address:
            return ""

        # Convert to uppercase
        normalized = address.upper()

        # Remove extra whitespace
        normalized = re.sub(r'\s+', ' ', normalized).strip()

        # Common abbreviations
        abbreviations = {
            ' STREET': ' ST',
            ' AVENUE': ' AVE',
            ' ROAD': ' RD',
            ' DRIVE': ' DR',
            ' BOULEVARD': ' BLVD',
            ' LANE': ' LN',
            ' COURT': ' CT',
            ' CIRCLE': ' CIR',
            ' PLACE': ' PL',
            ' TERRACE': ' TER',
            ' PARKWAY': ' PKWY',
            ' NORTH': ' N',
            ' SOUTH': ' S',
            ' EAST': ' E',
            ' WEST': ' W',
            ' APARTMENT': ' APT',
            ' SUITE': ' STE',
            ' UNIT': ' UNIT',
        }

        for full, abbr in abbreviations.items():
            normalized = normalized.replace(full, abbr)

        # Remove punctuation
        normalized = re.sub(r'[.,#]', '', normalized)

        return normalized

    def calculate_address_similarity(self, addr1: str, addr2: str) -> float:
        """
        Calculate similarity score between two addresses.

        Args:
            addr1: First address (normalized)
            addr2: Second address (normalized)

        Returns:
            Similarity score (0.0 to 1.0)
        """
        if not addr1 or not addr2:
            return 0.0

        # Use SequenceMatcher for fuzzy matching
        return SequenceMatcher(None, addr1, addr2).ratio()

    def extract_keywords(self, description: str) -> List[str]:
        """
        Extract relevant keywords from listing description.

        Args:
            description: Property description text

        Returns:
            List of keywords found
        """
        if not description:
            return []

        description_lower = description.lower()

        # Keywords indicating potential deals or special situations
        keywords_to_find = {
            'motivated': ['motivated seller', 'motivated', 'must sell'],
            'as-is': ['as-is', 'as is', 'sold as is'],
            'fixer': ['fixer', 'fixer upper', 'fixer-upper', 'needs work', 'tlc'],
            'estate': ['estate sale', 'estate', 'probate'],
            'foreclosure': ['foreclosure', 'foreclosed', 'bank owned', 'reo'],
            'short_sale': ['short sale', 'shortsale'],
            'price_reduction': ['price reduction', 'reduced', 'price drop', 'price cut'],
            'distressed': ['distressed', 'distress sale'],
            'handyman': ['handyman special', 'handyman'],
            'investor': ['investor opportunity', 'investors welcome', 'investor special'],
            'cash_only': ['cash only', 'cash buyers only'],
            'no_hoa': ['no hoa', 'no homeowners association'],
            'pool': ['pool', 'swimming pool'],
            'waterfront': ['waterfront', 'water front', 'lake front', 'oceanfront'],
            'corner_lot': ['corner lot'],
            'cul_de_sac': ['cul de sac', 'cul-de-sac'],
        }

        found_keywords = []

        for category, phrases in keywords_to_find.items():
            for phrase in phrases:
                if phrase in description_lower:
                    found_keywords.append(category)
                    break  # Only add category once

        return found_keywords

    def enrich_with_external_data(self, property_data: Dict) -> Dict:
        """
        Add geocoding and other external data if missing.

        Args:
            property_data: Property dictionary

        Returns:
            Enriched property dictionary
        """
        enriched = property_data.copy()

        # Estimate missing square footage if possible
        if not enriched.get('square_feet') and enriched.get('bedrooms'):
            # Rough estimation: 800 sqft + 400 sqft per bedroom
            estimated_sqft = 800 + (enriched['bedrooms'] * 400)
            enriched['square_feet_estimated'] = estimated_sqft
            self.logger.debug("Estimated square feet: %d", estimated_sqft)

        # Calculate price per sqft if missing
        if not enriched.get('price_per_sqft'):
            price = enriched.get('list_price')
            sqft = enriched.get('square_feet')
            if price and sqft and sqft > 0:
                enriched['price_per_sqft'] = round(price / sqft, 2)

        # Add county from ZIP code if missing (would need ZIP to county mapping)
        if not enriched.get('county') and enriched.get('zip_code'):
            # Placeholder - would need actual ZIP to county database
            enriched['county'] = None

        # Add geocoding placeholder if lat/long missing
        if not enriched.get('latitude') or not enriched.get('longitude'):
            # Placeholder - would need geocoding API (Google, Mapbox, etc.)
            # For now, just log that geocoding is needed
            self.logger.debug("Geocoding needed for: %s", enriched.get('street_address'))

        # Extract keywords from description
        if enriched.get('description'):
            keywords = self.extract_keywords(enriched['description'])
            if keywords:
                enriched['keywords'] = keywords

        return enriched

    def validate_property_data(self, property_data: Dict) -> Tuple[bool, List[str]]:
        """
        Validate property data meets minimum requirements.

        Args:
            property_data: Property dictionary to validate

        Returns:
            Tuple of (is_valid, list_of_error_messages)
        """
        errors = []

        # Required fields
        required_fields = ['street_address', 'city', 'state', 'zip_code', 'list_price']

        for field in required_fields:
            if not property_data.get(field):
                errors.append(f"Missing required field: {field}")

        # Validate data ranges
        if property_data.get('list_price'):
            price = property_data['list_price']
            if price <= 0:
                errors.append(f"Invalid list_price: {price} (must be > 0)")
            elif price > 100000000:  # $100M sanity check
                errors.append(f"Suspiciously high list_price: {price}")

        if property_data.get('bedrooms'):
            beds = property_data['bedrooms']
            if beds < 0 or beds > 50:
                errors.append(f"Invalid bedrooms: {beds} (must be 0-50)")

        if property_data.get('bathrooms'):
            baths = property_data['bathrooms']
            if baths < 0 or baths > 50:
                errors.append(f"Invalid bathrooms: {baths} (must be 0-50)")

        if property_data.get('square_feet'):
            sqft = property_data['square_feet']
            if sqft <= 0 or sqft > 100000:
                errors.append(f"Invalid square_feet: {sqft} (must be 1-100000)")

        if property_data.get('year_built'):
            year = property_data['year_built']
            current_year = datetime.now().year
            if year < 1700 or year > current_year + 2:
                errors.append(f"Invalid year_built: {year}")

        # Validate ZIP code format (US ZIP codes)
        if property_data.get('zip_code'):
            zip_code = str(property_data['zip_code'])
            if not re.match(r'^\d{5}(-\d{4})?$', zip_code):
                errors.append(f"Invalid ZIP code format: {zip_code}")

        is_valid = len(errors) == 0

        if not is_valid:
            self.logger.warning("Property validation failed: %s", ', '.join(errors))

        return is_valid, errors

    def detect_price_reduction(self, current_property: Dict,
                              historical_property: Dict) -> Optional[Dict]:
        """
        Compare current vs historical price to detect reductions.

        Args:
            current_property: Current property data
            historical_property: Historical property data

        Returns:
            Dictionary with reduction details or None if no reduction
        """
        current_price = current_property.get('list_price')
        historical_price = historical_property.get('list_price')

        if not current_price or not historical_price:
            return None

        if current_price < historical_price:
            reduction_amount = historical_price - current_price
            reduction_percentage = (reduction_amount / historical_price) * 100

            reduction_info = {
                'amount': reduction_amount,
                'percentage': round(reduction_percentage, 2),
                'previous_price': historical_price,
                'current_price': current_price,
                'date': current_property.get('scrape_timestamp') or datetime.now().isoformat()
            }

            self.logger.info("Price reduction detected: $%d (%.2f%%)",
                           reduction_amount, reduction_percentage)

            return reduction_info

        return None
