"""
Schema Mapper Module for DealFinder Pro
Maps external data sources to internal database schema.

Handles field mapping, type conversion, validation, and data normalization.
"""

import json
import logging
from typing import Dict, Any, List, Tuple, Optional
from datetime import datetime
import re

logger = logging.getLogger(__name__)


class SchemaMapperError(Exception):
    """Custom exception for schema mapping errors"""
    pass


class SchemaMapper:
    """
    Maps external data sources to internal database schema.

    Supports multiple data sources:
    - Realtor.com (HomeHarvest)
    - MLS databases
    - CSV imports
    - Manual data entry
    """

    def __init__(self, mapping_file_path: str):
        """
        Initialize schema mapper with field mapping configuration.

        Args:
            mapping_file_path: Path to JSON mapping configuration file
        """
        self.mapping_file_path = mapping_file_path
        self.mappings = {}
        self.required_fields = [
            'property_id',
            'street_address',
            'city',
            'state',
            'zip_code',
            'list_price'
        ]

        try:
            self._load_mappings()
            logger.info(f"Schema mapper initialized with {len(self.mappings)} source types")
        except Exception as e:
            logger.error(f"Failed to initialize schema mapper: {e}")
            raise SchemaMapperError(f"Initialization failed: {e}")

    def _load_mappings(self):
        """Load field mapping configuration from JSON file"""
        try:
            with open(self.mapping_file_path, 'r') as f:
                config = json.load(f)
                self.mappings = config.get('mappings', {})

                # Allow configuration to override required fields
                if 'required_fields' in config:
                    self.required_fields = config['required_fields']

                logger.info(f"Loaded mappings for sources: {list(self.mappings.keys())}")

        except FileNotFoundError:
            logger.warning(f"Mapping file not found: {self.mapping_file_path}")
            logger.info("Using default mappings")
            self._create_default_mappings()
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in mapping file: {e}")
            raise SchemaMapperError(f"Invalid mapping file: {e}")

    def _create_default_mappings(self):
        """Create default field mappings for common sources"""
        self.mappings = {
            'realtor': {
                'property_id': 'property_id',
                'mls_number': 'mls',
                'street_address': 'full_street_line',
                'city': 'city',
                'state': 'state_code',
                'zip_code': 'postal_code',
                'latitude': 'lat',
                'longitude': 'lon',
                'property_type': 'type',
                'bedrooms': 'beds',
                'bathrooms': 'baths',
                'square_feet': 'sqft',
                'lot_size_sqft': 'lot_sqft',
                'year_built': 'year_built',
                'list_price': 'list_price',
                'price_per_sqft': 'price_per_sqft',
                'listing_date': 'list_date',
                'days_on_market': 'days_on_mls',
                'description': 'description',
                'listing_agent_name': 'agent_name',
                'listing_agent_phone': 'agent_phone',
                'listing_agent_email': 'agent_email',
                'data_source': lambda x: 'realtor'
            },
            'mls': {
                'property_id': 'ListingKey',
                'mls_number': 'ListingId',
                'street_address': 'UnparsedAddress',
                'city': 'City',
                'state': 'StateOrProvince',
                'zip_code': 'PostalCode',
                'latitude': 'Latitude',
                'longitude': 'Longitude',
                'property_type': 'PropertyType',
                'bedrooms': 'BedroomsTotal',
                'bathrooms': 'BathroomsTotalInteger',
                'square_feet': 'LivingArea',
                'lot_size_sqft': 'LotSizeSquareFeet',
                'year_built': 'YearBuilt',
                'list_price': 'ListPrice',
                'listing_date': 'ListingContractDate',
                'days_on_market': 'DaysOnMarket',
                'description': 'PublicRemarks',
                'listing_agent_name': 'ListAgentFullName',
                'listing_agent_phone': 'ListAgentDirectPhone',
                'listing_agent_email': 'ListAgentEmail',
                'tax_assessed_value': 'TaxAssessedValue',
                'annual_taxes': 'TaxAnnualAmount',
                'data_source': lambda x: 'mls'
            },
            'csv': {
                # Generic CSV mapping - use common column names
                'property_id': ['property_id', 'id', 'PropertyID', 'ID'],
                'mls_number': ['mls', 'mls_number', 'MLS', 'MLS_Number'],
                'street_address': ['address', 'street_address', 'Address', 'FullAddress'],
                'city': ['city', 'City'],
                'state': ['state', 'State'],
                'zip_code': ['zip', 'zip_code', 'postal_code', 'ZipCode'],
                'bedrooms': ['beds', 'bedrooms', 'Beds', 'Bedrooms'],
                'bathrooms': ['baths', 'bathrooms', 'Baths', 'Bathrooms'],
                'square_feet': ['sqft', 'square_feet', 'SqFt', 'SquareFeet'],
                'list_price': ['price', 'list_price', 'Price', 'ListPrice'],
                'data_source': lambda x: 'csv'
            }
        }

    def map_fields(self, source_data: Dict[str, Any], source_type: str) -> Dict[str, Any]:
        """
        Transform external fields to internal schema.

        Args:
            source_data: Raw data from external source
            source_type: Type of data source ('realtor', 'mls', 'csv', etc.)

        Returns:
            Dictionary with mapped fields matching internal schema

        Raises:
            SchemaMapperError: If source type not found or mapping fails
        """
        if source_type not in self.mappings:
            raise SchemaMapperError(f"Unknown source type: {source_type}")

        mapping = self.mappings[source_type]
        mapped_data = {}

        for internal_field, external_field in mapping.items():
            try:
                if callable(external_field):
                    # Field is a function/lambda
                    mapped_data[internal_field] = external_field(source_data)
                elif isinstance(external_field, list):
                    # Try multiple possible field names (for CSV)
                    for field_name in external_field:
                        if field_name in source_data:
                            mapped_data[internal_field] = source_data[field_name]
                            break
                elif external_field in source_data:
                    # Direct field mapping
                    value = source_data[external_field]
                    # Convert value to appropriate type
                    mapped_data[internal_field] = self._convert_type(internal_field, value)

            except Exception as e:
                logger.warning(f"Failed to map field {internal_field}: {e}")
                continue

        # Apply defaults for missing fields
        mapped_data = self._apply_defaults(mapped_data)

        # Validate and clean data
        mapped_data = self._validate_and_clean(mapped_data)

        logger.debug(f"Mapped {len(mapped_data)} fields from {source_type}")
        return mapped_data

    def _convert_type(self, field_name: str, value: Any) -> Any:
        """
        Convert value to appropriate data type based on field name.

        Args:
            field_name: Internal field name
            value: Value to convert

        Returns:
            Converted value
        """
        if value is None or value == '':
            return None

        try:
            # Integer fields
            if field_name in ['bedrooms', 'year_built', 'stories', 'garage_spaces',
                             'square_feet', 'lot_size_sqft', 'days_on_market',
                             'opportunity_score']:
                return int(float(value))

            # Decimal fields
            elif field_name in ['bathrooms', 'list_price', 'price_per_sqft',
                               'previous_price', 'price_reduction_amount',
                               'tax_assessed_value', 'annual_taxes', 'hoa_fee',
                               'below_market_percentage', 'estimated_market_value',
                               'estimated_profit', 'cap_rate', 'cash_on_cash_return',
                               'latitude', 'longitude']:
                return float(value)

            # Boolean fields
            elif field_name in ['sms_opt_in']:
                if isinstance(value, bool):
                    return value
                return str(value).lower() in ['true', '1', 'yes', 't', 'y']

            # Timestamp fields
            elif field_name in ['listing_date', 'price_reduction_date', 'analysis_date',
                               'ghl_sync_date', 'last_synced_at']:
                if isinstance(value, datetime):
                    return value
                # Try to parse common date formats
                return self._parse_date(value)

            # Array fields
            elif field_name in ['features', 'keywords', 'tags',
                               'preferred_locations', 'property_types', 'match_reasons']:
                if isinstance(value, list):
                    return value
                elif isinstance(value, str):
                    # Split comma-separated string
                    return [item.strip() for item in value.split(',') if item.strip()]
                return []

            # String fields (default)
            else:
                return str(value).strip() if value else None

        except Exception as e:
            logger.warning(f"Type conversion failed for {field_name}={value}: {e}")
            return None

    def _parse_date(self, date_string: str) -> Optional[datetime]:
        """
        Parse date string in various formats.

        Args:
            date_string: Date string to parse

        Returns:
            datetime object or None
        """
        if not date_string:
            return None

        # Common date formats
        formats = [
            '%Y-%m-%d',
            '%Y-%m-%d %H:%M:%S',
            '%m/%d/%Y',
            '%m/%d/%Y %H:%M:%S',
            '%Y-%m-%dT%H:%M:%S',
            '%Y-%m-%dT%H:%M:%S.%f',
            '%Y-%m-%dT%H:%M:%SZ',
        ]

        for fmt in formats:
            try:
                return datetime.strptime(date_string, fmt)
            except ValueError:
                continue

        logger.warning(f"Could not parse date: {date_string}")
        return None

    def _apply_defaults(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Apply default values for missing fields.

        Args:
            data: Mapped data dictionary

        Returns:
            Data with defaults applied
        """
        defaults = {
            'ghl_sync_status': 'pending',
            'buyer_status': 'active',
            'sms_opt_in': False,
            'sms_sent': False,
            'workflow_triggered': False,
            'task_created': False
        }

        for field, default_value in defaults.items():
            if field not in data or data[field] is None:
                data[field] = default_value

        return data

    def _validate_and_clean(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate and clean mapped data.

        Args:
            data: Mapped data dictionary

        Returns:
            Cleaned and validated data
        """
        # Clean string fields
        string_fields = ['street_address', 'city', 'state', 'zip_code', 'county',
                        'property_type', 'deal_quality', 'description',
                        'first_name', 'last_name', 'email', 'phone']

        for field in string_fields:
            if field in data and data[field]:
                data[field] = str(data[field]).strip()

        # Normalize state code to uppercase 2-letter
        if 'state' in data and data['state']:
            data['state'] = data['state'].upper()[:2]

        # Normalize property type
        if 'property_type' in data and data['property_type']:
            data['property_type'] = self._normalize_property_type(data['property_type'])

        # Validate price ranges
        if 'list_price' in data and data['list_price']:
            if data['list_price'] < 0:
                logger.warning(f"Invalid list_price: {data['list_price']}")
                data['list_price'] = None

        # Validate score ranges (0-100)
        for score_field in ['opportunity_score', 'match_score']:
            if score_field in data and data[score_field] is not None:
                data[score_field] = max(0, min(100, data[score_field]))

        return data

    def _normalize_property_type(self, prop_type: str) -> str:
        """
        Normalize property type to standard values.

        Args:
            prop_type: Raw property type string

        Returns:
            Normalized property type
        """
        prop_type = prop_type.lower().strip()

        type_mapping = {
            'single family': 'single_family',
            'single-family': 'single_family',
            'sfh': 'single_family',
            'house': 'single_family',
            'multi family': 'multi_family',
            'multi-family': 'multi_family',
            'multifamily': 'multi_family',
            'duplex': 'multi_family',
            'triplex': 'multi_family',
            'fourplex': 'multi_family',
            'condo': 'condo',
            'condominium': 'condo',
            'townhouse': 'townhouse',
            'townhome': 'townhouse',
            'town house': 'townhouse',
            'apartment': 'apartment',
            'land': 'land',
            'lot': 'land',
            'commercial': 'commercial',
        }

        return type_mapping.get(prop_type, prop_type)

    def validate_required_fields(self, data: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Check if all required fields are present.

        Args:
            data: Data dictionary to validate

        Returns:
            Tuple of (is_valid, list_of_missing_fields)
        """
        missing_fields = []

        for field in self.required_fields:
            if field not in data or data[field] is None or data[field] == '':
                missing_fields.append(field)

        is_valid = len(missing_fields) == 0

        if not is_valid:
            logger.warning(f"Missing required fields: {missing_fields}")

        return is_valid, missing_fields

    def normalize_address(self, address_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Standardize address format and extract components.

        Args:
            address_data: Raw address data

        Returns:
            Normalized address components
        """
        normalized = {}

        # Extract street address
        if 'street_address' in address_data:
            street = address_data['street_address']
            # Clean up extra whitespace
            street = re.sub(r'\s+', ' ', street).strip()
            normalized['street_address'] = street

        # Extract and normalize city
        if 'city' in address_data:
            city = str(address_data['city']).strip().title()
            normalized['city'] = city

        # Extract and normalize state
        if 'state' in address_data:
            state = str(address_data['state']).strip().upper()
            # Convert full state name to abbreviation if needed
            state = self._normalize_state(state)
            normalized['state'] = state

        # Extract and normalize ZIP code
        if 'zip_code' in address_data:
            zip_code = str(address_data['zip_code']).strip()
            # Extract 5-digit ZIP from ZIP+4 format
            zip_match = re.match(r'(\d{5})', zip_code)
            if zip_match:
                normalized['zip_code'] = zip_match.group(1)
            else:
                normalized['zip_code'] = zip_code

        # Geocoding fields
        if 'latitude' in address_data:
            normalized['latitude'] = address_data['latitude']
        if 'longitude' in address_data:
            normalized['longitude'] = address_data['longitude']

        return normalized

    def _normalize_state(self, state: str) -> str:
        """
        Convert full state name to 2-letter abbreviation.

        Args:
            state: State name or abbreviation

        Returns:
            2-letter state abbreviation
        """
        if len(state) == 2:
            return state.upper()

        # Map of full state names to abbreviations
        state_map = {
            'ALABAMA': 'AL', 'ALASKA': 'AK', 'ARIZONA': 'AZ', 'ARKANSAS': 'AR',
            'CALIFORNIA': 'CA', 'COLORADO': 'CO', 'CONNECTICUT': 'CT', 'DELAWARE': 'DE',
            'FLORIDA': 'FL', 'GEORGIA': 'GA', 'HAWAII': 'HI', 'IDAHO': 'ID',
            'ILLINOIS': 'IL', 'INDIANA': 'IN', 'IOWA': 'IA', 'KANSAS': 'KS',
            'KENTUCKY': 'KY', 'LOUISIANA': 'LA', 'MAINE': 'ME', 'MARYLAND': 'MD',
            'MASSACHUSETTS': 'MA', 'MICHIGAN': 'MI', 'MINNESOTA': 'MN', 'MISSISSIPPI': 'MS',
            'MISSOURI': 'MO', 'MONTANA': 'MT', 'NEBRASKA': 'NE', 'NEVADA': 'NV',
            'NEW HAMPSHIRE': 'NH', 'NEW JERSEY': 'NJ', 'NEW MEXICO': 'NM', 'NEW YORK': 'NY',
            'NORTH CAROLINA': 'NC', 'NORTH DAKOTA': 'ND', 'OHIO': 'OH', 'OKLAHOMA': 'OK',
            'OREGON': 'OR', 'PENNSYLVANIA': 'PA', 'RHODE ISLAND': 'RI', 'SOUTH CAROLINA': 'SC',
            'SOUTH DAKOTA': 'SD', 'TENNESSEE': 'TN', 'TEXAS': 'TX', 'UTAH': 'UT',
            'VERMONT': 'VT', 'VIRGINIA': 'VA', 'WASHINGTON': 'WA', 'WEST VIRGINIA': 'WV',
            'WISCONSIN': 'WI', 'WYOMING': 'WY'
        }

        return state_map.get(state.upper(), state.upper()[:2])

    def add_custom_mapping(self, source_type: str, mapping: Dict[str, Any]):
        """
        Add or update custom field mapping for a data source.

        Args:
            source_type: Name of the data source
            mapping: Field mapping dictionary
        """
        self.mappings[source_type] = mapping
        logger.info(f"Added custom mapping for source type: {source_type}")

    def get_mapping_info(self, source_type: str) -> Optional[Dict[str, Any]]:
        """
        Get mapping configuration for a specific source type.

        Args:
            source_type: Data source type

        Returns:
            Mapping dictionary or None
        """
        return self.mappings.get(source_type)

    def list_source_types(self) -> List[str]:
        """
        Get list of available source types.

        Returns:
            List of source type names
        """
        return list(self.mappings.keys())
