"""
Sync Manager Module for DealFinder Pro
Manages bidirectional synchronization between database and GoHighLevel CRM.

Handles:
- Property export to GHL opportunities
- Buyer import from GHL contacts
- Conflict resolution
- Sync logging and error handling
"""

import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
import time

logger = logging.getLogger(__name__)


class SyncError(Exception):
    """Custom exception for sync operations"""
    pass


class SyncManager:
    """
    Manages bidirectional sync between local database and GoHighLevel CRM.

    Supports:
    - Exporting properties to GHL as opportunities
    - Importing buyers from GHL contacts
    - Conflict resolution strategies
    - Retry logic and error handling
    """

    def __init__(self, db_manager, ghl_connector, config: Dict[str, Any]):
        """
        Initialize sync manager.

        Args:
            db_manager: DatabaseManager instance
            ghl_connector: GoHighLevelConnector instance
            config: Sync configuration including:
                - conflict_resolution: 'ghl_wins', 'db_wins', 'newest_wins', 'manual'
                - sync_threshold_score: Minimum score for GHL sync (default: 75)
                - batch_size: Number of records per batch (default: 50)
                - retry_attempts: Number of retries on failure (default: 3)
        """
        self.db = db_manager
        self.ghl = ghl_connector
        self.config = config
        self.conflict_resolution = config.get('conflict_resolution', 'ghl_wins')
        self.sync_threshold = config.get('sync_threshold_score', 75)
        self.batch_size = config.get('batch_size', 50)
        self.retry_attempts = config.get('retry_attempts', 3)

        logger.info(f"SyncManager initialized with strategy: {self.conflict_resolution}")

    def sync_properties_to_ghl(self, min_score: Optional[int] = None) -> Dict[str, Any]:
        """
        Export high-scoring properties to GHL as opportunities.

        Args:
            min_score: Minimum opportunity score (overrides config default)

        Returns:
            Dictionary with sync statistics:
                - total_processed: Total properties processed
                - created: Number of opportunities created
                - updated: Number of opportunities updated
                - failed: Number of failures
                - errors: List of error messages
        """
        start_time = datetime.now()
        stats = {
            'total_processed': 0,
            'created': 0,
            'updated': 0,
            'failed': 0,
            'errors': []
        }

        try:
            # Get unsynced properties from database
            threshold = min_score if min_score is not None else self.sync_threshold
            properties = self.db.get_unsynced_properties()

            logger.info(f"Starting property sync: {len(properties)} properties to process")

            for prop in properties:
                stats['total_processed'] += 1

                try:
                    # Check if opportunity already exists in GHL
                    if prop.get('ghl_opportunity_id'):
                        # Update existing opportunity
                        success = self._update_ghl_opportunity(prop)
                        if success:
                            stats['updated'] += 1
                        else:
                            stats['failed'] += 1
                    else:
                        # Create new opportunity
                        opportunity_id = self._create_ghl_opportunity(prop)
                        if opportunity_id:
                            # Mark as synced in database
                            self.db.mark_property_synced(
                                prop['property_id'],
                                opportunity_id
                            )
                            stats['created'] += 1
                        else:
                            stats['failed'] += 1

                except Exception as e:
                    error_msg = f"Failed to sync property {prop.get('property_id')}: {e}"
                    logger.error(error_msg)
                    stats['errors'].append(error_msg)
                    stats['failed'] += 1

                    # Update property sync status to failed
                    self.db.update_property(prop['property_id'], {
                        'ghl_sync_status': 'failed',
                        'ghl_sync_error': str(e)
                    })

                # Rate limiting: small delay between requests
                time.sleep(0.1)

            # Calculate execution time
            execution_time = (datetime.now() - start_time).total_seconds()

            # Log sync operation
            self.log_sync_operation(
                sync_type='property_export_to_ghl',
                stats={**stats, 'execution_time_seconds': int(execution_time)},
                status='success' if stats['failed'] == 0 else 'partial'
            )

            logger.info(f"Property sync complete: {stats}")
            return stats

        except Exception as e:
            logger.error(f"Property sync failed: {e}")
            stats['errors'].append(str(e))

            # Log failed sync
            self.log_sync_operation(
                sync_type='property_export_to_ghl',
                stats=stats,
                status='failed'
            )

            raise SyncError(f"Property sync failed: {e}")

    def _create_ghl_opportunity(self, property_data: Dict[str, Any]) -> Optional[str]:
        """
        Create opportunity in GHL from property data.

        Args:
            property_data: Property dictionary

        Returns:
            GHL opportunity ID or None on failure
        """
        try:
            # Prepare opportunity data
            opportunity = {
                'name': f"{property_data['street_address']}, {property_data['city']}",
                'pipelineId': self.config.get('ghl_pipeline_id'),
                'pipelineStageId': self.config.get('ghl_new_lead_stage_id'),
                'status': 'open',
                'monetaryValue': property_data.get('list_price'),
                'customFields': self._map_property_to_ghl_fields(property_data),
                'tags': self._generate_property_tags(property_data)
            }

            # Create opportunity via GHL API
            response = self.ghl.create_opportunity(opportunity)

            if response and 'id' in response:
                opportunity_id = response['id']
                logger.info(f"Created GHL opportunity: {opportunity_id}")

                # Add notes with analysis details
                self._add_opportunity_notes(opportunity_id, property_data)

                return opportunity_id

            return None

        except Exception as e:
            logger.error(f"Failed to create GHL opportunity: {e}")
            return None

    def _update_ghl_opportunity(self, property_data: Dict[str, Any]) -> bool:
        """
        Update existing GHL opportunity.

        Args:
            property_data: Property dictionary

        Returns:
            True if successful
        """
        try:
            opportunity_id = property_data.get('ghl_opportunity_id')
            if not opportunity_id:
                return False

            # Prepare update data
            updates = {
                'monetaryValue': property_data.get('list_price'),
                'customFields': self._map_property_to_ghl_fields(property_data)
            }

            # Update via GHL API
            response = self.ghl.update_opportunity(opportunity_id, updates)

            if response:
                logger.info(f"Updated GHL opportunity: {opportunity_id}")
                return True

            return False

        except Exception as e:
            logger.error(f"Failed to update GHL opportunity: {e}")
            return False

    def _map_property_to_ghl_fields(self, property_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Map property data to GHL custom fields.

        Args:
            property_data: Property dictionary

        Returns:
            Dictionary of GHL custom field values
        """
        return {
            'property_address': f"{property_data.get('street_address')}, {property_data.get('city')}, {property_data.get('state')} {property_data.get('zip_code')}",
            'deal_score': property_data.get('opportunity_score'),
            'list_price': property_data.get('list_price'),
            'est_profit': property_data.get('estimated_profit'),
            'mls_id': property_data.get('mls_number'),
            'price_per_sqft': property_data.get('price_per_sqft'),
            'below_market_pct': property_data.get('below_market_percentage'),
            'days_on_market': property_data.get('days_on_market'),
            'deal_quality': property_data.get('deal_quality'),
            'estimated_arv': property_data.get('estimated_market_value'),
            'bedrooms': property_data.get('bedrooms'),
            'bathrooms': property_data.get('bathrooms'),
            'square_feet': property_data.get('square_feet'),
            'property_type': property_data.get('property_type'),
        }

    def _generate_property_tags(self, property_data: Dict[str, Any]) -> List[str]:
        """
        Generate tags for property based on characteristics.

        Args:
            property_data: Property dictionary

        Returns:
            List of tag strings
        """
        tags = ['automated', 'dealfinder']

        # Add score-based tags
        score = property_data.get('opportunity_score', 0)
        if score >= 90:
            tags.append('hot_deal')
        elif score >= 75:
            tags.append('good_opportunity')

        # Add property type tag
        if property_data.get('property_type'):
            tags.append(property_data['property_type'].lower().replace(' ', '_'))

        # Add price reduction tag
        if property_data.get('price_reduction_amount', 0) > 0:
            tags.append('price_reduced')

        return tags

    def _add_opportunity_notes(self, opportunity_id: str, property_data: Dict[str, Any]):
        """
        Add analysis notes to GHL opportunity.

        Args:
            opportunity_id: GHL opportunity ID
            property_data: Property dictionary
        """
        try:
            notes = f"""
Property Analysis Summary:
- Opportunity Score: {property_data.get('opportunity_score')}/100
- Deal Quality: {property_data.get('deal_quality')}
- Below Market: {property_data.get('below_market_percentage')}%
- Estimated Profit: ${property_data.get('estimated_profit', 0):,.0f}
- Days on Market: {property_data.get('days_on_market')}
- Cap Rate: {property_data.get('cap_rate')}%

Property Details:
- Address: {property_data.get('street_address')}
- City: {property_data.get('city')}, {property_data.get('state')} {property_data.get('zip_code')}
- Type: {property_data.get('property_type')}
- Beds/Baths: {property_data.get('bedrooms')}/{property_data.get('bathrooms')}
- Square Feet: {property_data.get('square_feet'):,}
- List Price: ${property_data.get('list_price', 0):,.0f}

Data Source: {property_data.get('data_source')}
Added: {datetime.now().strftime('%Y-%m-%d %H:%M')}
            """.strip()

            self.ghl.add_note_to_opportunity(opportunity_id, notes)

        except Exception as e:
            logger.warning(f"Failed to add notes to opportunity: {e}")

    def sync_buyers_from_ghl(self) -> Dict[str, Any]:
        """
        Import buyers from GHL contacts with 'active_buyer' tag.

        Returns:
            Dictionary with sync statistics:
                - total_processed: Total contacts processed
                - created: Number of buyers created
                - updated: Number of buyers updated
                - failed: Number of failures
                - errors: List of error messages
        """
        start_time = datetime.now()
        stats = {
            'total_processed': 0,
            'created': 0,
            'updated': 0,
            'failed': 0,
            'errors': []
        }

        try:
            # Fetch contacts with 'active_buyer' tag from GHL
            contacts = self.ghl.get_contacts_by_tag('active_buyer')

            logger.info(f"Starting buyer sync: {len(contacts)} contacts to process")

            for contact in contacts:
                stats['total_processed'] += 1

                try:
                    # Map GHL contact to buyer data
                    buyer_data = self._map_ghl_contact_to_buyer(contact)

                    # Upsert buyer in database
                    buyer_id = self.db.upsert_buyer(buyer_data)

                    if buyer_id:
                        # Check if this was an insert or update
                        # (upsert_buyer doesn't distinguish, so we'll count as updated)
                        stats['updated'] += 1
                    else:
                        stats['failed'] += 1

                except Exception as e:
                    error_msg = f"Failed to sync buyer {contact.get('id')}: {e}"
                    logger.error(error_msg)
                    stats['errors'].append(error_msg)
                    stats['failed'] += 1

                # Rate limiting
                time.sleep(0.05)

            # Calculate execution time
            execution_time = (datetime.now() - start_time).total_seconds()

            # Log sync operation
            self.log_sync_operation(
                sync_type='buyer_import_from_ghl',
                stats={**stats, 'execution_time_seconds': int(execution_time)},
                status='success' if stats['failed'] == 0 else 'partial'
            )

            logger.info(f"Buyer sync complete: {stats}")
            return stats

        except Exception as e:
            logger.error(f"Buyer sync failed: {e}")
            stats['errors'].append(str(e))

            # Log failed sync
            self.log_sync_operation(
                sync_type='buyer_import_from_ghl',
                stats=stats,
                status='failed'
            )

            raise SyncError(f"Buyer sync failed: {e}")

    def _map_ghl_contact_to_buyer(self, contact: Dict[str, Any]) -> Dict[str, Any]:
        """
        Map GHL contact data to buyer schema.

        Args:
            contact: GHL contact dictionary

        Returns:
            Buyer data dictionary
        """
        custom_fields = contact.get('customFields', {})

        buyer_data = {
            'ghl_contact_id': contact['id'],
            'first_name': contact.get('firstName'),
            'last_name': contact.get('lastName'),
            'email': contact.get('email'),
            'phone': contact.get('phone'),
            'min_budget': self._parse_numeric(custom_fields.get('budget_min')),
            'max_budget': self._parse_numeric(custom_fields.get('budget_max')),
            'preferred_locations': self._parse_array(custom_fields.get('location_preference')),
            'property_types': self._parse_array(custom_fields.get('property_type_preference')),
            'min_bedrooms': self._parse_numeric(custom_fields.get('min_bedrooms')),
            'min_bathrooms': self._parse_numeric(custom_fields.get('min_bathrooms')),
            'buyer_status': custom_fields.get('buyer_status', 'active').lower(),
            'tags': contact.get('tags', []),
            'sms_opt_in': 'sms_opt_in' in contact.get('tags', []),
            'last_synced_at': datetime.now()
        }

        return buyer_data

    def _parse_numeric(self, value: Any) -> Optional[float]:
        """Parse numeric value from string or number"""
        if value is None or value == '':
            return None
        try:
            return float(value)
        except (ValueError, TypeError):
            return None

    def _parse_array(self, value: Any) -> List[str]:
        """Parse array value from string or list"""
        if isinstance(value, list):
            return value
        elif isinstance(value, str):
            return [item.strip() for item in value.split(',') if item.strip()]
        return []

    def handle_sync_conflict(
        self,
        db_record: Dict[str, Any],
        ghl_record: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Resolve sync conflicts based on configured strategy.

        Args:
            db_record: Record from local database
            ghl_record: Record from GoHighLevel

        Returns:
            Resolved record (winning version)
        """
        if self.conflict_resolution == 'ghl_wins':
            logger.debug("Conflict resolved: GHL wins")
            return ghl_record

        elif self.conflict_resolution == 'db_wins':
            logger.debug("Conflict resolved: DB wins")
            return db_record

        elif self.conflict_resolution == 'newest_wins':
            # Compare timestamps
            db_timestamp = db_record.get('updated_at') or db_record.get('created_at')
            ghl_timestamp = ghl_record.get('dateUpdated') or ghl_record.get('dateAdded')

            if ghl_timestamp and db_timestamp:
                if isinstance(ghl_timestamp, str):
                    ghl_timestamp = datetime.fromisoformat(ghl_timestamp.replace('Z', '+00:00'))
                if isinstance(db_timestamp, str):
                    db_timestamp = datetime.fromisoformat(db_timestamp)

                if ghl_timestamp > db_timestamp:
                    logger.debug("Conflict resolved: GHL is newer")
                    return ghl_record
                else:
                    logger.debug("Conflict resolved: DB is newer")
                    return db_record

            # Default to GHL if timestamps unavailable
            return ghl_record

        elif self.conflict_resolution == 'manual':
            logger.warning("Manual conflict resolution required")
            # In production, this would queue for manual review
            # For now, default to GHL
            return ghl_record

        else:
            logger.error(f"Unknown conflict resolution strategy: {self.conflict_resolution}")
            return ghl_record

    def log_sync_operation(
        self,
        sync_type: str,
        stats: Dict[str, Any],
        status: str = 'success'
    ):
        """
        Log sync operation to database.

        Args:
            sync_type: Type of sync operation
            stats: Statistics dictionary
            status: 'success', 'failed', or 'partial'
        """
        try:
            sync_data = {
                'sync_type': sync_type,
                'status': status,
                'records_processed': stats.get('total_processed', 0),
                'records_succeeded': stats.get('created', 0) + stats.get('updated', 0),
                'records_failed': stats.get('failed', 0),
                'error_message': '; '.join(stats.get('errors', [])) if stats.get('errors') else None,
                'execution_time_seconds': stats.get('execution_time_seconds', 0),
                'started_at': datetime.now(),
                'completed_at': datetime.now()
            }

            self.db.log_sync(sync_data)

        except Exception as e:
            logger.error(f"Failed to log sync operation: {e}")

    def get_sync_statistics(self, days_back: int = 7) -> Dict[str, Any]:
        """
        Get sync statistics for recent operations.

        Args:
            days_back: Number of days to analyze

        Returns:
            Statistics dictionary
        """
        try:
            # This would query the sync_logs table for recent history
            # Implementation depends on database query capabilities
            stats = {
                'period_days': days_back,
                'total_syncs': 0,
                'successful_syncs': 0,
                'failed_syncs': 0,
                'total_records_processed': 0,
                'average_execution_time': 0
            }

            # Query sync logs (simplified)
            # In production, this would be a more complex query
            logger.info(f"Sync statistics for last {days_back} days: {stats}")

            return stats

        except Exception as e:
            logger.error(f"Failed to get sync statistics: {e}")
            return {}
