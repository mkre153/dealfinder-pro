"""
Data Import Manager
Handles CSV/Excel imports for external property data
"""

import pandas as pd
import logging
from typing import Dict, List, Tuple
from datetime import datetime

logger = logging.getLogger(__name__)


class DataImporter:
    """Manages external data imports"""

    def __init__(self):
        """Initialize data importer"""
        self.import_history = []

    def process_file(self, file, import_type: str = 'general') -> Dict:
        """
        Process uploaded CSV or Excel file

        Args:
            file: Streamlit UploadedFile object
            import_type: Type of import (general, mls, comps, tax_data)

        Returns:
            Result dict with success status and imported data
        """
        result = {
            'success': False,
            'message': '',
            'imported_count': 0,
            'errors': [],
            'data': []
        }

        try:
            # Read file based on extension
            filename = file.name.lower()

            if filename.endswith('.csv'):
                df = pd.read_csv(file)
            elif filename.endswith(('.xlsx', '.xls')):
                df = pd.read_excel(file)
            else:
                result['message'] = "Unsupported file format. Please upload CSV or Excel files."
                return result

            # Validate and process based on import type
            if import_type == 'mls':
                processed_data = self._process_mls_data(df)
            elif import_type == 'comps':
                processed_data = self._process_comparable_sales(df)
            elif import_type == 'tax_data':
                processed_data = self._process_tax_data(df)
            else:
                processed_data = self._process_general_data(df)

            result['success'] = True
            result['imported_count'] = len(processed_data)
            result['data'] = processed_data
            result['message'] = f"Successfully imported {len(processed_data)} properties"

            # Store in history
            self.import_history.append({
                'timestamp': datetime.now().isoformat(),
                'filename': file.name,
                'type': import_type,
                'count': len(processed_data)
            })

        except Exception as e:
            logger.error(f"Error processing file: {e}", exc_info=True)
            result['message'] = f"Error processing file: {str(e)}"
            result['errors'].append(str(e))

        return result

    def _process_mls_data(self, df: pd.DataFrame) -> List[Dict]:
        """Process MLS bulk export data"""
        properties = []

        # Define column mappings (flexible to handle various MLS formats)
        column_map = self._detect_column_mapping(df, {
            'address': ['address', 'street_address', 'property_address', 'full_address', 'FullStreetAddress'],
            'city': ['city', 'City', 'CITY'],
            'state': ['state', 'State', 'STATE', 'st'],
            'zip_code': ['zip', 'zip_code', 'zipcode', 'PostalCode', 'ZIP'],
            'list_price': ['price', 'list_price', 'asking_price', 'ListPrice', 'CurrentPrice'],
            'bedrooms': ['beds', 'bedrooms', 'BedsTotal', 'bed', 'br'],
            'bathrooms': ['baths', 'bathrooms', 'BathsTotal', 'bath', 'ba'],
            'square_feet': ['sqft', 'square_feet', 'LivingArea', 'size', 'sf'],
            'days_on_market': ['dom', 'days_on_market', 'DaysOnMarket', 'days_listed'],
            'property_type': ['type', 'property_type', 'PropertyType', 'prop_type'],
            'mls_id': ['mls', 'mls_id', 'mls_number', 'ListingId', 'mlsnum']
        })

        # Process each row
        for idx, row in df.iterrows():
            try:
                prop = {}

                # Map columns
                for standard_name, possible_columns in column_map.items():
                    for col in possible_columns:
                        if col in df.columns and pd.notna(row[col]):
                            prop[standard_name] = row[col]
                            break

                # Clean and validate
                if 'list_price' in prop:
                    prop['list_price'] = self._clean_price(prop['list_price'])

                if 'bedrooms' in prop:
                    prop['bedrooms'] = int(float(prop['bedrooms']))

                if 'bathrooms' in prop:
                    prop['bathrooms'] = float(prop['bathrooms'])

                if 'square_feet' in prop:
                    prop['square_feet'] = int(float(prop['square_feet']))

                # Add metadata
                prop['data_source'] = 'imported_mls'
                prop['import_date'] = datetime.now().isoformat()

                properties.append(prop)

            except Exception as e:
                logger.warning(f"Error processing row {idx}: {e}")
                continue

        return properties

    def _process_comparable_sales(self, df: pd.DataFrame) -> List[Dict]:
        """Process comparable sales data (for ARV calculations)"""
        comps = []

        column_map = self._detect_column_mapping(df, {
            'address': ['address', 'street_address', 'property_address'],
            'city': ['city'],
            'zip_code': ['zip', 'zip_code', 'zipcode'],
            'sold_price': ['sold_price', 'sale_price', 'price'],
            'sold_date': ['sold_date', 'sale_date', 'date'],
            'bedrooms': ['beds', 'bedrooms', 'bed'],
            'bathrooms': ['baths', 'bathrooms', 'bath'],
            'square_feet': ['sqft', 'square_feet', 'size'],
            'property_type': ['type', 'property_type']
        })

        for idx, row in df.iterrows():
            try:
                comp = {}

                for standard_name, possible_columns in column_map.items():
                    for col in possible_columns:
                        if col in df.columns and pd.notna(row[col]):
                            comp[standard_name] = row[col]
                            break

                # Add ARV flag
                comp['is_comparable_sale'] = True
                comp['data_source'] = 'imported_comps'
                comp['import_date'] = datetime.now().isoformat()

                comps.append(comp)

            except Exception as e:
                logger.warning(f"Error processing comp {idx}: {e}")
                continue

        return comps

    def _process_tax_data(self, df: pd.DataFrame) -> List[Dict]:
        """Process tax assessment data"""
        tax_records = []

        column_map = self._detect_column_mapping(df, {
            'address': ['address', 'street_address', 'property_address'],
            'city': ['city'],
            'zip_code': ['zip', 'zip_code'],
            'tax_assessed_value': ['assessed_value', 'tax_value', 'assessment'],
            'tax_year': ['tax_year', 'year'],
            'annual_taxes': ['annual_tax', 'taxes', 'property_tax']
        })

        for idx, row in df.iterrows():
            try:
                record = {}

                for standard_name, possible_columns in column_map.items():
                    for col in possible_columns:
                        if col in df.columns and pd.notna(row[col]):
                            record[standard_name] = row[col]
                            break

                record['data_source'] = 'imported_tax_data'
                record['import_date'] = datetime.now().isoformat()

                tax_records.append(record)

            except Exception as e:
                logger.warning(f"Error processing tax record {idx}: {e}")
                continue

        return tax_records

    def _process_general_data(self, df: pd.DataFrame) -> List[Dict]:
        """Process general property data"""
        # Convert DataFrame to list of dicts
        properties = df.to_dict('records')

        # Add metadata
        for prop in properties:
            prop['data_source'] = 'imported_general'
            prop['import_date'] = datetime.now().isoformat()

        return properties

    def _detect_column_mapping(self, df: pd.DataFrame, standard_mapping: Dict[str, List[str]]) -> Dict[str, List[str]]:
        """Detect which columns exist in the DataFrame"""
        detected = {}

        for standard_name, possible_names in standard_mapping.items():
            detected[standard_name] = [name for name in possible_names if name in df.columns]

        return detected

    def _clean_price(self, price) -> float:
        """Clean price value (remove $ , etc.)"""
        if isinstance(price, str):
            price = price.replace('$', '').replace(',', '').strip()

        try:
            return float(price)
        except:
            return 0.0

    def merge_with_existing(self, imported_data: List[Dict], existing_data: List[Dict]) -> List[Dict]:
        """Merge imported data with existing properties"""
        merged = existing_data.copy()

        for imported_prop in imported_data:
            # Try to find matching property by address
            address = imported_prop.get('address', '').lower().strip()

            if not address:
                # No address, add as new
                merged.append(imported_prop)
                continue

            # Look for match
            matched = False
            for existing_prop in merged:
                existing_address = existing_prop.get('address', '').lower().strip()

                if address == existing_address or self._addresses_similar(address, existing_address):
                    # Update existing property with imported data
                    # Prefer imported data for specific fields
                    if 'custom_arv' in imported_prop:
                        existing_prop['custom_arv'] = imported_prop['custom_arv']

                    if 'tax_assessed_value' in imported_prop:
                        existing_prop['tax_assessed_value'] = imported_prop['tax_assessed_value']

                    # Merge other fields
                    for key, value in imported_prop.items():
                        if key not in existing_prop or not existing_prop[key]:
                            existing_prop[key] = value

                    matched = True
                    break

            if not matched:
                # Add as new property
                merged.append(imported_prop)

        return merged

    def _addresses_similar(self, addr1: str, addr2: str) -> bool:
        """Check if two addresses are similar"""
        # Simple similarity check - can be enhanced
        # Remove common variations
        for word in ['street', 'st', 'avenue', 'ave', 'road', 'rd', 'drive', 'dr']:
            addr1 = addr1.replace(word, '').strip()
            addr2 = addr2.replace(word, '').strip()

        # Extract numbers
        nums1 = ''.join(c for c in addr1 if c.isdigit())
        nums2 = ''.join(c for c in addr2 if c.isdigit())

        # If numbers match, likely same address
        return nums1 == nums2 and nums1 != ''

    def get_import_history(self) -> List[Dict]:
        """Get import history"""
        return self.import_history

    def generate_template(self, import_type: str = 'mls') -> pd.DataFrame:
        """Generate a CSV template for import"""
        if import_type == 'mls':
            return pd.DataFrame(columns=[
                'address', 'city', 'state', 'zip_code', 'list_price',
                'bedrooms', 'bathrooms', 'square_feet', 'days_on_market',
                'property_type', 'mls_id'
            ])
        elif import_type == 'comps':
            return pd.DataFrame(columns=[
                'address', 'city', 'zip_code', 'sold_price', 'sold_date',
                'bedrooms', 'bathrooms', 'square_feet', 'property_type'
            ])
        elif import_type == 'tax_data':
            return pd.DataFrame(columns=[
                'address', 'city', 'zip_code', 'tax_assessed_value',
                'tax_year', 'annual_taxes'
            ])
        else:
            return pd.DataFrame(columns=[
                'address', 'city', 'zip_code', 'price', 'bedrooms',
                'bathrooms', 'square_feet', 'arv', 'notes'
            ])
