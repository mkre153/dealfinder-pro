"""
Privy.pro CSV Importer
Imports property data from Privy.pro CSV exports with owner intelligence
"""

import csv
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional
from pathlib import Path

logger = logging.getLogger(__name__)


class PrivyImporter:
    """
    Import and enrich property data from Privy.pro CSV exports

    Privy provides unique owner intelligence not available in standard MLS data:
    - Absentee owner detection (mailing address != property address)
    - LLC/Trust ownership (investor activity indicators)
    - Previous ownership history (flip detection)
    - Business names (institutional buyers)
    """

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def import_csv(self, csv_path: str) -> List[Dict]:
        """
        Import properties from Privy CSV export

        Args:
            csv_path: Path to Privy CSV file

        Returns:
            List of normalized property dictionaries with investment intelligence
        """
        self.logger.info(f"Importing Privy CSV from: {csv_path}")

        properties = []

        try:
            with open(csv_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)

                for row_num, row in enumerate(reader, start=2):  # Start at 2 (header is row 1)
                    try:
                        property_data = self._transform_row(row)
                        if property_data:
                            properties.append(property_data)
                    except Exception as e:
                        self.logger.error(f"Error processing row {row_num}: {e}")
                        continue

            self.logger.info(f"Successfully imported {len(properties)} properties from Privy CSV")
            return properties

        except FileNotFoundError:
            self.logger.error(f"Privy CSV file not found: {csv_path}")
            raise
        except Exception as e:
            self.logger.error(f"Error reading Privy CSV: {e}")
            raise

    def _transform_row(self, row: Dict) -> Optional[Dict]:
        """
        Transform Privy CSV row to internal property schema

        Args:
            row: CSV row dictionary

        Returns:
            Normalized property dictionary with investment intelligence
        """
        # Skip if missing critical fields
        if not row.get('Street') or not row.get('Price'):
            return None

        # Basic property data
        property_data = {
            'data_source': 'privy_pro',
            'import_timestamp': datetime.now().isoformat(),

            # Property identifiers
            'street_address': row.get('Street', '').strip(),
            'city': row.get('City', '').strip(),
            'state': row.get('State', '').strip(),
            'zip_code': row.get('Zip', '').strip(),

            # Price information
            'list_price': self._safe_float(row.get('Price')),
            'price_per_sqft': self._safe_float(row.get('$ Sq Ft')),

            # Property characteristics
            'bedrooms': self._safe_int(row.get('Beds')),
            'bathrooms': self._safe_float(row.get('Baths')),
            'square_feet': self._safe_int(row.get('Sq Ft')),
            'lot_size_sqft': self._safe_int(row.get('Lot Sq Ft')),
            'year_built': self._safe_int(row.get('Built')),
            'property_type': row.get('Property Type', '').strip(),
            'garage_spaces': self._safe_int(row.get('Garages')),
            'stories': self._safe_int(row.get('Levels')),

            # Multi-family specific
            'units': self._safe_int(row.get('# of Units')),
            'basement_sqft': self._safe_int(row.get('Basement Sq Ft')),

            # Listing information
            'status': row.get('Status', '').strip(),
            'listing_date': row.get('Date', '').strip(),
            'days_on_market': self._safe_int(row.get('DOM')),

            # Privy specific
            'privy_cma_url': row.get('Privy CMA URL', '').strip(),
        }

        # Owner intelligence (unique to Privy)
        owner_data = self._extract_owner_intelligence(row)
        property_data.update(owner_data)

        # Calculate investment intelligence flags
        investment_flags = self._calculate_investment_flags(property_data, row)
        property_data.update(investment_flags)

        # Generate full address for matching
        property_data['address'] = f"{property_data['street_address']}, {property_data['city']}, {property_data['state']} {property_data['zip_code']}"

        return property_data

    def _extract_owner_intelligence(self, row: Dict) -> Dict:
        """
        Extract owner information unique to Privy exports

        Args:
            row: CSV row dictionary

        Returns:
            Owner intelligence dictionary
        """
        owner_info = {}

        # Current owner 1
        owner1_parts = []
        if row.get('Owner 1 First Name'):
            owner1_parts.append(row['Owner 1 First Name'])
        if row.get('Owner 1 Middle Name'):
            owner1_parts.append(row['Owner 1 Middle Name'])
        if row.get('Owner 1 Last Name'):
            owner1_parts.append(row['Owner 1 Last Name'])
        if row.get('Owner 1 Suffix'):
            owner1_parts.append(row['Owner 1 Suffix'])

        owner1_name = ' '.join(owner1_parts).strip() if owner1_parts else ''
        owner1_business = row.get('Owner 1 Business Name', '').strip()

        # Current owner 2
        owner2_parts = []
        if row.get('Owner 2 First Name'):
            owner2_parts.append(row['Owner 2 First Name'])
        if row.get('Owner 2 Middle Name'):
            owner2_parts.append(row['Owner 2 Middle Name'])
        if row.get('Owner 2 Last Name'):
            owner2_parts.append(row['Owner 2 Last Name'])
        if row.get('Owner 2 Suffix'):
            owner2_parts.append(row['Owner 2 Suffix'])

        owner2_name = ' '.join(owner2_parts).strip() if owner2_parts else ''
        owner2_business = row.get('Owner 2 Business Name', '').strip()

        # Combine owner info
        if owner1_business:
            owner_info['owner_name'] = owner1_business
        elif owner1_name:
            owner_info['owner_name'] = owner1_name
            if owner2_business:
                owner_info['owner_name_2'] = owner2_business
            elif owner2_name:
                owner_info['owner_name_2'] = owner2_name
        else:
            owner_info['owner_name'] = 'Unknown'

        # Mailing address (key for absentee owner detection)
        mailing_parts = []
        if row.get('Mailing Street'):
            mailing_parts.append(row['Mailing Street'])
        if row.get('Mailing City'):
            mailing_parts.append(row['Mailing City'])
        if row.get('Mailing State'):
            mailing_parts.append(row['Mailing State'])
        if row.get('Mailing Zip'):
            mailing_parts.append(row['Mailing Zip'])

        if mailing_parts:
            owner_info['owner_mailing_address'] = ', '.join(mailing_parts)
        else:
            owner_info['owner_mailing_address'] = None

        # Previous ownership (flip detection)
        prev_owner_1 = row.get('Previous Owner 1 Full Name', '').strip()
        prev_owner_2 = row.get('Previous Owner 2 Full Name', '').strip()

        if prev_owner_1:
            owner_info['previous_owner'] = prev_owner_1
            if prev_owner_2:
                owner_info['previous_owner_2'] = prev_owner_2

        return owner_info

    def _calculate_investment_flags(self, property_data: Dict, row: Dict) -> Dict:
        """
        Calculate investment intelligence flags based on owner data

        Args:
            property_data: Normalized property data
            row: Original CSV row

        Returns:
            Investment flags dictionary
        """
        flags = {}

        # Absentee owner detection
        property_address = f"{row.get('Street', '')}, {row.get('City', '')}, {row.get('State', '')} {row.get('Zip', '')}"
        mailing_address = property_data.get('owner_mailing_address', '')

        if mailing_address and property_address.lower() not in mailing_address.lower():
            flags['absentee_owner'] = True
            flags['investment_signals'] = flags.get('investment_signals', [])
            flags['investment_signals'].append('absentee_owner')
        else:
            flags['absentee_owner'] = False

        # LLC/Trust ownership (investor indicator)
        owner_name = property_data.get('owner_name', '').upper()
        owner_keywords = ['LLC', 'TRUST', 'INC', 'CORP', 'LP', 'VENTURES', 'PROPERTIES', 'HOLDINGS', 'INVESTMENTS']

        if any(keyword in owner_name for keyword in owner_keywords):
            flags['investor_owned'] = True
            flags['investment_signals'] = flags.get('investment_signals', [])
            flags['investment_signals'].append('investor_owned')
        else:
            flags['investor_owned'] = False

        # Flip history (previous LLC/Trust ownership)
        previous_owner = property_data.get('previous_owner', '').upper()
        if previous_owner and any(keyword in previous_owner for keyword in owner_keywords):
            flags['flip_history'] = True
            flags['investment_signals'] = flags.get('investment_signals', [])
            flags['investment_signals'].append('flip_history')
        else:
            flags['flip_history'] = False

        # Motivated seller (long DOM)
        dom = property_data.get('days_on_market', 0)
        if dom and dom >= 60:
            flags['motivated_seller'] = True
            flags['investment_signals'] = flags.get('investment_signals', [])
            flags['investment_signals'].append('motivated_seller')
        else:
            flags['motivated_seller'] = False

        # Calculate bonus opportunity score
        bonus_score = 0
        if flags['absentee_owner']:
            bonus_score += 10
        if flags['investor_owned']:
            bonus_score += 5
        if flags['flip_history']:
            bonus_score += 5
        if flags['motivated_seller']:
            bonus_score += 8

        flags['privy_intelligence_bonus'] = bonus_score

        # Initialize investment_signals if not set
        if 'investment_signals' not in flags:
            flags['investment_signals'] = []

        return flags

    def _safe_int(self, value: Optional[str]) -> Optional[int]:
        """Safely convert value to integer"""
        if not value or value == '':
            return None
        try:
            # Remove commas and convert
            clean_value = str(value).replace(',', '').strip()
            return int(float(clean_value))
        except (ValueError, TypeError):
            return None

    def _safe_float(self, value: Optional[str]) -> Optional[float]:
        """Safely convert value to float"""
        if not value or value == '':
            return None
        try:
            # Remove commas, dollar signs, and convert
            clean_value = str(value).replace(',', '').replace('$', '').strip()
            return float(clean_value)
        except (ValueError, TypeError):
            return None

    def merge_with_existing(self, privy_properties: List[Dict],
                           existing_scan_path: str = None) -> Dict:
        """
        Merge Privy properties with existing scan data

        Args:
            privy_properties: List of properties from Privy import
            existing_scan_path: Path to existing latest_scan.json (default: data/latest_scan.json)

        Returns:
            Merged scan data dictionary
        """
        if existing_scan_path is None:
            existing_scan_path = Path(__file__).parent.parent / 'data' / 'latest_scan.json'
        else:
            existing_scan_path = Path(existing_scan_path)

        # Load existing data if available
        existing_properties = []
        if existing_scan_path.exists():
            try:
                with open(existing_scan_path, 'r') as f:
                    existing_data = json.load(f)
                    existing_properties = existing_data.get('properties', [])
                self.logger.info(f"Loaded {len(existing_properties)} existing properties")
            except Exception as e:
                self.logger.warning(f"Could not load existing scan data: {e}")

        # Merge properties (Privy data takes precedence for duplicates)
        merged_properties = {}

        # Add existing properties
        for prop in existing_properties:
            address_key = prop.get('address', '').lower()
            if address_key:
                merged_properties[address_key] = prop

        # Add/update with Privy properties
        for prop in privy_properties:
            address_key = prop.get('address', '').lower()
            if address_key:
                if address_key in merged_properties:
                    # Merge: keep existing data but add Privy intelligence
                    existing_prop = merged_properties[address_key]
                    existing_prop['owner_name'] = prop.get('owner_name')
                    existing_prop['owner_mailing_address'] = prop.get('owner_mailing_address')
                    existing_prop['previous_owner'] = prop.get('previous_owner')
                    existing_prop['absentee_owner'] = prop.get('absentee_owner')
                    existing_prop['investor_owned'] = prop.get('investor_owned')
                    existing_prop['flip_history'] = prop.get('flip_history')
                    existing_prop['motivated_seller'] = prop.get('motivated_seller')
                    existing_prop['investment_signals'] = prop.get('investment_signals', [])
                    existing_prop['privy_intelligence_bonus'] = prop.get('privy_intelligence_bonus', 0)
                    existing_prop['privy_cma_url'] = prop.get('privy_cma_url')

                    # Update opportunity score with Privy bonus
                    if 'opportunity_score' in existing_prop:
                        existing_prop['opportunity_score'] = min(
                            100,
                            existing_prop['opportunity_score'] + prop.get('privy_intelligence_bonus', 0)
                        )
                else:
                    # New property from Privy
                    merged_properties[address_key] = prop

        # Convert back to list
        final_properties = list(merged_properties.values())

        # Create merged scan data
        merged_data = {
            'scan_timestamp': datetime.now().isoformat(),
            'property_count': len(final_properties),
            'data_sources': ['privy_pro', 'realtor_com'],  # Update based on actual sources
            'privy_import_count': len(privy_properties),
            'properties': final_properties
        }

        self.logger.info(f"Merged data: {len(final_properties)} total properties "
                        f"({len(privy_properties)} from Privy)")

        return merged_data

    def save_to_scan_file(self, scan_data: Dict, output_path: str = None):
        """
        Save merged data to latest_scan.json

        Args:
            scan_data: Merged scan data dictionary
            output_path: Output path (default: data/latest_scan.json)
        """
        if output_path is None:
            output_path = Path(__file__).parent.parent / 'data' / 'latest_scan.json'
        else:
            output_path = Path(output_path)

        # Create backup of existing file
        if output_path.exists():
            backup_path = output_path.parent / f"latest_scan_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            try:
                import shutil
                shutil.copy2(output_path, backup_path)
                self.logger.info(f"Created backup: {backup_path}")
            except Exception as e:
                self.logger.warning(f"Could not create backup: {e}")

        # Save merged data
        try:
            with open(output_path, 'w') as f:
                json.dump(scan_data, f, indent=2, default=str)
            self.logger.info(f"Saved {scan_data['property_count']} properties to {output_path}")
        except Exception as e:
            self.logger.error(f"Error saving scan file: {e}")
            raise


def main():
    """Command-line interface for Privy CSV import"""
    import sys
    import argparse

    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    parser = argparse.ArgumentParser(description='Import Privy.pro CSV exports')
    parser.add_argument('csv_file', help='Path to Privy CSV file')
    parser.add_argument('--merge', action='store_true',
                       help='Merge with existing latest_scan.json')
    parser.add_argument('--output', help='Output path (default: data/latest_scan.json)')
    parser.add_argument('--dry-run', action='store_true',
                       help='Import but do not save (preview only)')

    args = parser.parse_args()

    # Import CSV
    importer = PrivyImporter()

    print(f"\n🏠 Importing Privy CSV: {args.csv_file}\n")

    try:
        properties = importer.import_csv(args.csv_file)

        print(f"✅ Imported {len(properties)} properties from Privy\n")

        # Show investment intelligence summary
        absentee_count = sum(1 for p in properties if p.get('absentee_owner'))
        investor_count = sum(1 for p in properties if p.get('investor_owned'))
        flip_count = sum(1 for p in properties if p.get('flip_history'))
        motivated_count = sum(1 for p in properties if p.get('motivated_seller'))

        print("📊 Investment Intelligence Summary:")
        print(f"   • Absentee Owners: {absentee_count}")
        print(f"   • Investor-Owned: {investor_count}")
        print(f"   • Flip History: {flip_count}")
        print(f"   • Motivated Sellers (60+ DOM): {motivated_count}\n")

        # Merge if requested
        if args.merge:
            print("🔄 Merging with existing property data...")
            merged_data = importer.merge_with_existing(properties, args.output)
            print(f"✅ Total properties after merge: {merged_data['property_count']}\n")
        else:
            merged_data = {
                'scan_timestamp': datetime.now().isoformat(),
                'property_count': len(properties),
                'data_sources': ['privy_pro'],
                'privy_import_count': len(properties),
                'properties': properties
            }

        # Save unless dry run
        if args.dry_run:
            print("🔍 DRY RUN - No files saved")
            print(f"\nSample property with investment intelligence:")
            for prop in properties:
                if prop.get('investment_signals'):
                    print(f"\n  Address: {prop['address']}")
                    print(f"  Price: ${prop['list_price']:,.0f}")
                    print(f"  Owner: {prop.get('owner_name')}")
                    if prop.get('absentee_owner'):
                        print(f"  🏚️  Absentee Owner (mailing: {prop.get('owner_mailing_address')})")
                    if prop.get('investor_owned'):
                        print(f"  💼 Investor-Owned")
                    if prop.get('flip_history'):
                        print(f"  🔄 Flip History (prev: {prop.get('previous_owner')})")
                    if prop.get('motivated_seller'):
                        print(f"  ⏰ Motivated Seller ({prop.get('days_on_market')} DOM)")
                    print(f"  Bonus Score: +{prop.get('privy_intelligence_bonus', 0)}")
                    break
        else:
            importer.save_to_scan_file(merged_data, args.output)
            print(f"✅ Saved to {args.output or 'data/latest_scan.json'}")

        print("\n🎉 Import complete!")

    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
