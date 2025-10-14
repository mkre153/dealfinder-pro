"""
SDMLS (San Diego MLS) API Connector
RESO Web API 2.0 Integration via MLS Router

Official MLS data source for San Diego County properties.
Replaces web scraping with reliable, real-time MLS data.
"""

import os
import requests
import logging
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)


class SDMLSConnector:
    """
    San Diego MLS (SDMLS) API connector using RESO Web API 2.0 standard

    Provides access to official MLS listings data for San Diego County.
    Uses MLS Router API for real-time property data.

    Documentation: https://sdmls.com/nmsubscribers/data-access/
    Standard: RESO Web API 2.0 / Data Dictionary 2.0
    """

    def __init__(
        self,
        api_token: Optional[str] = None,
        api_url: Optional[str] = None,
        test_mode: bool = False
    ):
        """
        Initialize SDMLS connector

        Args:
            api_token: Bearer token for MLS Router API (or use SDMLS_API_TOKEN env var)
            api_url: MLS Router API base URL (or use SDMLS_API_URL env var)
            test_mode: If True, log requests but don't make actual API calls
        """
        self.api_token = api_token or os.getenv('SDMLS_API_TOKEN')
        self.api_url = api_url or os.getenv('SDMLS_API_URL', 'https://api.mlsrouter.com')
        self.test_mode = test_mode

        if not self.api_token and not test_mode:
            raise ValueError(
                "SDMLS API token not found. Set SDMLS_API_TOKEN in .env file. "
                "See SDMLS_API_SETUP.md for instructions on obtaining credentials."
            )

        self.headers = {
            'Authorization': f'Bearer {self.api_token}',
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }

        logger.info(f"SDMLS Connector initialized (test_mode={test_mode})")

    def test_connection(self) -> Dict:
        """
        Test API connection and credentials

        Returns:
            Dict with connection status and service metadata
        """
        if self.test_mode:
            logger.info("TEST MODE: Would test SDMLS API connection")
            return {
                'success': True,
                'test_mode': True,
                'message': 'Test mode - no actual API call made'
            }

        try:
            # Get API metadata endpoint (RESO standard)
            response = requests.get(
                f"{self.api_url}/odata/$metadata",
                headers=self.headers,
                timeout=10
            )

            response.raise_for_status()

            return {
                'success': True,
                'status_code': response.status_code,
                'message': 'Successfully connected to SDMLS MLS Router API',
                'api_url': self.api_url
            }

        except requests.exceptions.RequestException as e:
            logger.error(f"SDMLS connection test failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'message': 'Failed to connect to SDMLS API. Check credentials and network.'
            }

    def search_properties(
        self,
        zip_codes: Optional[List[str]] = None,
        city: Optional[str] = None,
        price_min: Optional[float] = None,
        price_max: Optional[float] = None,
        bedrooms_min: Optional[int] = None,
        bathrooms_min: Optional[float] = None,
        property_types: Optional[List[str]] = None,
        status: str = 'Active',
        days_back: int = 30,
        limit: int = 1000
    ) -> List[Dict]:
        """
        Search properties using RESO Web API OData filters

        Args:
            zip_codes: List of ZIP codes to search
            city: City name
            price_min: Minimum list price
            price_max: Maximum list price
            bedrooms_min: Minimum bedrooms
            bathrooms_min: Minimum bathrooms
            property_types: Property types (e.g., ['Residential', 'Condo'])
            status: Listing status (Active, Pending, Sold)
            days_back: Only return listings from last N days
            limit: Maximum results to return

        Returns:
            List of property dictionaries
        """
        if self.test_mode:
            logger.info(f"TEST MODE: Would search SDMLS properties with filters: "
                       f"zip_codes={zip_codes}, price_min={price_min}, status={status}")
            return self._get_mock_properties()

        try:
            # Build OData $filter query (RESO Web API 2.0 standard)
            filters = []

            # Status filter
            if status:
                filters.append(f"StandardStatus eq '{status}'")

            # Date filter (listings modified in last N days)
            if days_back:
                date_cutoff = (datetime.now() - timedelta(days=days_back)).strftime('%Y-%m-%dT%H:%M:%SZ')
                filters.append(f"ModificationTimestamp ge {date_cutoff}")

            # ZIP codes filter
            if zip_codes:
                zip_filter = ' or '.join([f"PostalCode eq '{z}'" for z in zip_codes])
                filters.append(f"({zip_filter})")

            # City filter
            if city:
                filters.append(f"City eq '{city}'")

            # Price filters
            if price_min:
                filters.append(f"ListPrice ge {price_min}")
            if price_max:
                filters.append(f"ListPrice le {price_max}")

            # Bedroom filter
            if bedrooms_min:
                filters.append(f"BedroomsTotal ge {bedrooms_min}")

            # Bathroom filter
            if bathrooms_min:
                filters.append(f"BathroomsTotalInteger ge {bathrooms_min}")

            # Property type filter
            if property_types:
                type_filter = ' or '.join([f"PropertyType eq '{pt}'" for pt in property_types])
                filters.append(f"({type_filter})")

            # Combine all filters
            filter_query = ' and '.join(filters) if filters else None

            # Build request parameters
            params = {
                '$top': limit,
                '$orderby': 'ModificationTimestamp desc'
            }

            if filter_query:
                params['$filter'] = filter_query

            # Make API request
            logger.info(f"Searching SDMLS properties with filter: {filter_query}")

            response = requests.get(
                f"{self.api_url}/odata/Property",
                headers=self.headers,
                params=params,
                timeout=30
            )

            response.raise_for_status()
            data = response.json()

            # Extract properties from OData response
            properties = data.get('value', [])

            logger.info(f"Found {len(properties)} properties from SDMLS")

            # Transform RESO fields to internal schema
            return [self._transform_property(prop) for prop in properties]

        except requests.exceptions.RequestException as e:
            logger.error(f"SDMLS property search failed: {e}")
            return []

    def get_property_details(self, listing_key: str) -> Optional[Dict]:
        """
        Get detailed information for a specific property by ListingKey

        Args:
            listing_key: Unique MLS listing key/ID

        Returns:
            Property details dictionary or None if not found
        """
        if self.test_mode:
            logger.info(f"TEST MODE: Would get property details for {listing_key}")
            return self._get_mock_properties()[0] if self._get_mock_properties() else None

        try:
            response = requests.get(
                f"{self.api_url}/odata/Property('{listing_key}')",
                headers=self.headers,
                timeout=10
            )

            response.raise_for_status()
            property_data = response.json()

            return self._transform_property(property_data)

        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to get property details for {listing_key}: {e}")
            return None

    def get_property_media(self, listing_key: str) -> List[Dict]:
        """
        Get media (photos, videos) for a specific property

        Args:
            listing_key: Unique MLS listing key/ID

        Returns:
            List of media objects with URLs
        """
        if self.test_mode:
            logger.info(f"TEST MODE: Would get media for listing {listing_key}")
            return []

        try:
            response = requests.get(
                f"{self.api_url}/odata/Media",
                headers=self.headers,
                params={'$filter': f"ResourceRecordKey eq '{listing_key}'"},
                timeout=10
            )

            response.raise_for_status()
            data = response.json()

            return data.get('value', [])

        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to get media for {listing_key}: {e}")
            return []

    def _transform_property(self, reso_property: Dict) -> Dict:
        """
        Transform RESO Web API property format to internal schema

        Maps RESO Data Dictionary 2.0 fields to DealFinder Pro format

        Args:
            reso_property: Raw property data from RESO API

        Returns:
            Normalized property dictionary
        """
        # RESO Data Dictionary 2.0 field mapping
        return {
            'data_source': 'sdmls_mls',
            'source_timestamp': datetime.now().isoformat(),

            # Unique identifiers
            'mls_number': reso_property.get('ListingKey'),  # Primary MLS ID
            'listing_id': reso_property.get('ListingId'),    # Alternative ID
            'property_id': reso_property.get('ParcelNumber'),

            # Address information (RESO standard fields)
            'street_address': reso_property.get('UnparsedAddress') or
                            f"{reso_property.get('StreetNumber', '')} {reso_property.get('StreetName', '')}".strip(),
            'city': reso_property.get('City'),
            'state': reso_property.get('StateOrProvince'),
            'zip_code': reso_property.get('PostalCode'),
            'county': reso_property.get('CountyOrParish'),
            'latitude': reso_property.get('Latitude'),
            'longitude': reso_property.get('Longitude'),

            # Price information
            'list_price': reso_property.get('ListPrice'),
            'original_list_price': reso_property.get('OriginalListPrice'),
            'price_per_sqft': reso_property.get('ListPricePerSquareFoot'),

            # Property characteristics
            'bedrooms': reso_property.get('BedroomsTotal'),
            'bathrooms': reso_property.get('BathroomsTotalInteger') or reso_property.get('BathroomsFull'),
            'bathrooms_full': reso_property.get('BathroomsFull'),
            'bathrooms_half': reso_property.get('BathroomsHalf'),
            'square_feet': reso_property.get('LivingArea') or reso_property.get('BuildingAreaTotal'),
            'lot_size_sqft': reso_property.get('LotSizeSquareFeet'),
            'lot_size_acres': reso_property.get('LotSizeAcres'),
            'year_built': reso_property.get('YearBuilt'),
            'property_type': reso_property.get('PropertyType'),
            'property_subtype': reso_property.get('PropertySubType'),
            'stories': reso_property.get('StoriesTotal'),

            # Listing information
            'listing_date': reso_property.get('ListingContractDate'),
            'on_market_date': reso_property.get('OnMarketDate'),
            'days_on_market': reso_property.get('DaysOnMarket') or reso_property.get('CumulativeDaysOnMarket'),
            'status': reso_property.get('StandardStatus'),
            'status_change_date': reso_property.get('StatusChangeTimestamp'),

            # Agent/Broker information
            'listing_agent_name': reso_property.get('ListAgentFullName'),
            'listing_agent_key': reso_property.get('ListAgentKey'),
            'listing_agent_phone': reso_property.get('ListAgentDirectPhone'),
            'listing_agent_email': reso_property.get('ListAgentEmail'),
            'listing_office_name': reso_property.get('ListOfficeName'),
            'listing_office_phone': reso_property.get('ListOfficePhone'),

            # Financial details
            'hoa_fee': reso_property.get('AssociationFee'),
            'hoa_fee_frequency': reso_property.get('AssociationFeeFrequency'),
            'tax_annual_amount': reso_property.get('TaxAnnualAmount'),
            'tax_assessed_value': reso_property.get('TaxAssessedValue'),
            'tax_year': reso_property.get('TaxYear'),

            # Property features
            'parking_total': reso_property.get('ParkingTotal'),
            'garage_spaces': reso_property.get('GarageSpaces'),
            'pool': reso_property.get('PoolPrivateYN'),
            'fireplace': reso_property.get('FireplacesTotal'),
            'view': reso_property.get('View'),

            # Descriptions
            'public_remarks': reso_property.get('PublicRemarks'),
            'private_remarks': reso_property.get('PrivateRemarks'),

            # Media
            'media_count': reso_property.get('MediaCount'),
            'photo_count': reso_property.get('PhotosCount'),
            'virtual_tour_url': reso_property.get('VirtualTourURLUnbranded'),

            # Additional RESO fields
            'architectural_style': reso_property.get('ArchitecturalStyle'),
            'heating': reso_property.get('Heating'),
            'cooling': reso_property.get('Cooling'),
            'roof': reso_property.get('Roof'),
            'construction_materials': reso_property.get('ConstructionMaterials'),

            # MLS Router specific
            'listing_url': f"https://sdmls.com/listing/{reso_property.get('ListingKey')}"
                          if reso_property.get('ListingKey') else None,

            # Raw data for debugging
            '_raw_reso_data': reso_property if os.getenv('DEBUG') == 'true' else None
        }

    def _get_mock_properties(self) -> List[Dict]:
        """Return mock properties for testing"""
        return [
            {
                'data_source': 'sdmls_mls',
                'source_timestamp': datetime.now().isoformat(),
                'mls_number': 'TEST123456',
                'street_address': '1234 Mock Street',
                'city': 'San Diego',
                'state': 'CA',
                'zip_code': '92130',
                'list_price': 1250000,
                'bedrooms': 4,
                'bathrooms': 3,
                'square_feet': 2800,
                'property_type': 'Residential',
                'status': 'Active',
                'days_on_market': 15,
                'listing_agent_name': 'Test Agent',
                'public_remarks': 'Beautiful test property (mock data)',
            }
        ]


# Standalone testing
if __name__ == "__main__":
    """Test SDMLS integration"""

    print("🏠 SDMLS MLS Router API Integration Test\n")

    # Test with test_mode=True (no credentials needed)
    connector = SDMLSConnector(test_mode=True)

    print("Test 1: Connection Test")
    print("-" * 50)
    result = connector.test_connection()
    print(f"Result: {result}\n")

    print("Test 2: Property Search")
    print("-" * 50)
    properties = connector.search_properties(
        zip_codes=['92130', '92131'],
        price_min=500000,
        price_max=1500000,
        bedrooms_min=3,
        status='Active'
    )
    print(f"Found {len(properties)} properties (mock data)\n")

    if properties:
        print("Sample property:")
        print(f"  Address: {properties[0].get('street_address')}")
        print(f"  Price: ${properties[0].get('list_price'):,}")
        print(f"  Beds/Baths: {properties[0].get('bedrooms')}/{properties[0].get('bathrooms')}")
        print(f"  MLS#: {properties[0].get('mls_number')}")

    print("\n" + "=" * 50)
    print("✅ Test Mode Complete!")
    print("=" * 50)
    print("\nTo use with real credentials:")
    print("1. Add SDMLS_API_TOKEN to .env file")
    print("2. Set test_mode=False")
    print("3. See SDMLS_API_SETUP.md for setup instructions")
