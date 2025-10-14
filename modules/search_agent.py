"""
SearchAgent - Autonomous Property Monitoring
Continuously monitors new property scans for matches based on client criteria
"""

import json
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import logging
from dotenv import load_dotenv

from modules.client_db import get_db
from integrations.ghl_connector import GoHighLevelConnector
from integrations.ghl_buyer_matcher import BuyerMatcher

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)


class SearchAgent:
    """
    Autonomous agent that monitors property scans for specific client criteria
    Runs perpetually until property found or client cancels
    """

    def __init__(self, agent_id: str):
        """
        Initialize search agent from database

        Args:
            agent_id: Unique agent identifier
        """
        self.agent_id = agent_id
        self.db = get_db()

        # Load agent data from database
        agent_data = self.db.get_agent(agent_id)
        if not agent_data:
            raise ValueError(f"Agent {agent_id} not found in database")

        self.client_id = agent_data['client_id']
        self.client_name = agent_data['client_name']
        self.criteria_id = agent_data['criteria_id']
        self.status = agent_data['status']

        # Parse search criteria
        self.criteria = {
            'zip_codes': agent_data.get('zip_codes', []),
            'price_min': agent_data.get('price_min'),
            'price_max': agent_data.get('price_max'),
            'bedrooms_min': agent_data.get('bedrooms_min'),
            'bathrooms_min': agent_data.get('bathrooms_min'),
            'property_types': agent_data.get('property_types', []),
            'deal_quality': agent_data.get('deal_quality', []),
            'min_score': agent_data.get('min_score', 80),
            'investment_type': agent_data.get('investment_type'),
            'timeline': agent_data.get('timeline')
        }

        # Notification preferences
        self.notify_email = bool(agent_data.get('notification_email', 1))
        self.notify_sms = bool(agent_data.get('notification_sms', 0))
        self.notify_chat = bool(agent_data.get('notification_chat', 1))

        # GHL integration (optional)
        self.ghl_connector = None
        self.buyer_matcher = None
        try:
            # Get GHL credentials from environment
            ghl_api_key = os.getenv('GHL_API_KEY')
            ghl_location_id = os.getenv('GHL_LOCATION_ID')

            if ghl_api_key and ghl_location_id:
                self.ghl_connector = GoHighLevelConnector(
                    api_key=ghl_api_key,
                    location_id=ghl_location_id,
                    test_mode=False
                )
                # Get GHL contact ID from client data
                client_data = self.db.get_client(self.client_id)
                self.ghl_contact_id = client_data.get('ghl_contact_id') if client_data else None
                logger.info(f"GHL integration enabled for agent {self.agent_id}")
            else:
                logger.warning(f"GHL credentials not found in environment variables")
        except Exception as e:
            logger.warning(f"GHL integration not available: {e}")

        # Property scan data path
        self.scan_path = Path(__file__).parent.parent / 'data' / 'latest_scan.json'
        self.last_scan_timestamp = None

    def check_for_matches(self) -> List[Dict]:
        """
        Check latest property scan for matches

        Returns:
            List of matching properties with scores
        """
        if self.status != 'active':
            logger.info(f"Agent {self.agent_id} is {self.status}, skipping check")
            return []

        # Load latest properties
        properties = self._load_latest_properties()
        if not properties:
            logger.warning(f"No properties found in scan for agent {self.agent_id}")
            return []

        logger.info(f"Agent {self.agent_id}: Checking {len(properties)} properties")

        # Filter and score properties
        matches = []
        for prop in properties:
            if self._property_matches_criteria(prop):
                match_score, reasons = self._calculate_match_score(prop)

                if match_score >= self.criteria['min_score']:
                    matches.append({
                        'property': prop,
                        'match_score': match_score,
                        'match_reasons': reasons
                    })

        # Sort by match score (highest first)
        matches.sort(key=lambda x: x['match_score'], reverse=True)

        logger.info(f"Agent {self.agent_id}: Found {len(matches)} matches")

        # Update agent last check timestamp
        self.db.update_agent_last_check(self.agent_id)

        return matches

    def _load_latest_properties(self) -> List[Dict]:
        """Load properties from latest scan file"""
        try:
            if not self.scan_path.exists():
                logger.error(f"Scan file not found: {self.scan_path}")
                return []

            with open(self.scan_path, 'r') as f:
                data = json.load(f)

            # Always return properties on first check
            scan_timestamp = data.get('scan_timestamp')
            if self.last_scan_timestamp is not None and scan_timestamp == self.last_scan_timestamp:
                logger.debug(f"Agent {self.agent_id}: Scan unchanged since last check")
                return []

            self.last_scan_timestamp = scan_timestamp
            return data.get('properties', [])

        except Exception as e:
            logger.error(f"Error loading properties: {e}")
            return []

    def _property_matches_criteria(self, prop: Dict) -> bool:
        """
        Check if property matches basic criteria (filters before scoring)

        Args:
            prop: Property data dictionary

        Returns:
            True if property passes basic filters
        """
        # ZIP code filter
        if self.criteria['zip_codes']:
            prop_zip = str(prop.get('zip_code', ''))
            if prop_zip not in self.criteria['zip_codes']:
                return False

        # Price range filter
        price = prop.get('list_price') or prop.get('price', 0)
        if self.criteria['price_min'] and price < self.criteria['price_min']:
            return False
        if self.criteria['price_max'] and price > self.criteria['price_max']:
            return False

        # Bedrooms filter
        bedrooms = prop.get('bedrooms', 0)
        if self.criteria['bedrooms_min'] and bedrooms < self.criteria['bedrooms_min']:
            return False

        # Bathrooms filter
        bathrooms = prop.get('bathrooms', 0)
        if self.criteria['bathrooms_min'] and bathrooms < self.criteria['bathrooms_min']:
            return False

        # Property type filter
        if self.criteria['property_types']:
            prop_type = prop.get('property_type', '')
            if prop_type not in self.criteria['property_types']:
                return False

        # Deal quality filter (HOT, GOOD, FAIR)
        if self.criteria['deal_quality']:
            quality = prop.get('deal_quality', '')
            if quality not in self.criteria['deal_quality']:
                return False

        return True

    def _calculate_match_score(self, prop: Dict) -> Tuple[int, List[str]]:
        """
        Calculate 0-100 match score for property

        Args:
            prop: Property data dictionary

        Returns:
            (score, reasons) tuple
        """
        score = 0
        reasons = []

        # Start with property's opportunity score (0-100)
        opp_score = prop.get('opportunity_score', 0)
        score += min(opp_score, 40)  # Max 40 points from opportunity score

        if opp_score >= 90:
            reasons.append(f"🔥 HOT DEAL - {opp_score}/100 opportunity score")
        elif opp_score >= 80:
            reasons.append(f"✨ GOOD DEAL - {opp_score}/100 opportunity score")

        # Location precision match (30 points max)
        prop_zip = str(prop.get('zip_code', ''))
        if prop_zip in self.criteria['zip_codes']:
            score += 30
            reasons.append(f"📍 Exact ZIP match: {prop_zip}")

        # Price positioning (15 points max)
        price = prop.get('list_price') or prop.get('price', 0)
        if self.criteria['price_min'] and self.criteria['price_max']:
            price_range = self.criteria['price_max'] - self.criteria['price_min']
            price_midpoint = self.criteria['price_min'] + (price_range / 2)

            # Closer to midpoint = higher score
            price_deviation = abs(price - price_midpoint) / price_range
            price_score = max(0, 15 - (price_deviation * 15))
            score += price_score

            reasons.append(f"💰 Price ${price:,.0f} within budget")

        # Property characteristics match (15 points max)
        bedrooms = prop.get('bedrooms', 0)
        bathrooms = prop.get('bathrooms', 0)

        if bedrooms >= self.criteria.get('bedrooms_min', 0):
            score += 8
            reasons.append(f"🛏️ {bedrooms} bedrooms")

        if bathrooms >= self.criteria.get('bathrooms_min', 0):
            score += 7
            reasons.append(f"🚿 {bathrooms} bathrooms")

        # Investment metrics bonus (bonus points, can exceed 100)
        if self.criteria.get('investment_type') == 'cash_flow':
            monthly_cashflow = prop.get('monthly_cashflow', 0)
            if monthly_cashflow > 500:
                score += 10
                reasons.append(f"💸 Strong cash flow: ${monthly_cashflow:,.0f}/mo")

        if self.criteria.get('investment_type') == 'appreciation':
            appreciation_potential = prop.get('appreciation_potential', 0)
            if appreciation_potential > 15:
                score += 10
                reasons.append(f"📈 High appreciation potential: {appreciation_potential}%")

        # Market timing bonus
        days_on_market = prop.get('days_on_market', 0)
        if days_on_market > 60:
            score += 5
            reasons.append(f"⏰ Motivated seller - {days_on_market} days on market")

        return min(score, 100), reasons

    def process_new_matches(self, matches: List[Dict]) -> int:
        """
        Process newly found matches - store in DB and send notifications

        Args:
            matches: List of matching properties

        Returns:
            Number of new matches processed
        """
        if not matches:
            return 0

        new_matches_count = 0

        for match in matches:
            prop = match['property']
            address = prop.get('address', 'Unknown Address')

            # Check if we've already matched this property
            existing_matches = self.db.get_agent_matches(self.agent_id)
            if any(m['property_address'] == address for m in existing_matches):
                logger.debug(f"Property {address} already matched, skipping")
                continue

            # Store match in database
            match_id = self.db.add_match(
                agent_id=self.agent_id,
                property_address=address,
                property_data={
                    **prop,
                    'match_score': match['match_score'],
                    'match_reasons': match['match_reasons']
                }
            )

            logger.info(f"New match {match_id}: {address} (score: {match['match_score']})")

            # Send notifications
            self._send_notifications(match)

            # Mark as notified
            self.db.mark_match_notified(match_id)

            new_matches_count += 1

        return new_matches_count

    def _send_notifications(self, match: Dict):
        """
        Send notifications about new match via configured channels

        Args:
            match: Match data with property and score
        """
        prop = match['property']
        score = match['match_score']
        reasons = match['match_reasons']

        address = prop.get('address', 'Unknown')
        price = prop.get('price', 0)

        # Build notification message
        message = f"""
🏠 NEW PROPERTY MATCH ({score}/100)

{address}
💰 ${price:,.0f}

Match Reasons:
{chr(10).join(f"  • {r}" for r in reasons[:5])}

View details in DealFinder Pro dashboard.
        """.strip()

        # Email notification
        if self.notify_email and self.ghl_connector and self.ghl_contact_id:
            try:
                self.ghl_connector.send_email(
                    contact_id=self.ghl_contact_id,
                    subject=f"🏠 New Property Match: {address}",
                    body=message
                )
                logger.info(f"Sent email notification for {address}")
            except Exception as e:
                logger.error(f"Failed to send email: {e}")

        # SMS notification
        if self.notify_sms and self.ghl_connector and self.ghl_contact_id:
            try:
                # Shorter SMS version
                sms_message = f"🏠 New Match ({score}/100): {address} - ${price:,.0f}. Check dashboard for details."
                self.ghl_connector.send_sms(
                    contact_id=self.ghl_contact_id,
                    message=sms_message
                )
                logger.info(f"Sent SMS notification for {address}")
            except Exception as e:
                logger.error(f"Failed to send SMS: {e}")

        # In-app notification (stored for dashboard display)
        if self.notify_chat:
            # This is handled by storing in agent_matches table
            logger.info(f"In-app notification ready for {address}")

    def get_status_summary(self) -> Dict:
        """
        Get current status summary of this agent

        Returns:
            Dictionary with agent status information
        """
        agent_data = self.db.get_agent(self.agent_id)
        matches = self.db.get_agent_matches(self.agent_id)

        return {
            'agent_id': self.agent_id,
            'client_name': self.client_name,
            'status': self.status,
            'created_at': agent_data['created_at'],
            'last_check': agent_data.get('last_check'),
            'matches_found': len(matches),
            'new_matches': len([m for m in matches if m['status'] == 'new']),
            'criteria_summary': self._get_criteria_summary()
        }

    def _get_criteria_summary(self) -> str:
        """Generate human-readable criteria summary"""
        parts = []

        if self.criteria['zip_codes']:
            parts.append(f"ZIP: {', '.join(self.criteria['zip_codes'])}")

        if self.criteria['price_min'] or self.criteria['price_max']:
            price_min = f"${self.criteria['price_min']:,.0f}" if self.criteria['price_min'] else "Any"
            price_max = f"${self.criteria['price_max']:,.0f}" if self.criteria['price_max'] else "Any"
            parts.append(f"Price: {price_min} - {price_max}")

        if self.criteria['bedrooms_min']:
            parts.append(f"{self.criteria['bedrooms_min']}+ beds")

        if self.criteria['bathrooms_min']:
            parts.append(f"{self.criteria['bathrooms_min']}+ baths")

        if self.criteria['deal_quality']:
            parts.append(f"Quality: {', '.join(self.criteria['deal_quality'])}")

        return " | ".join(parts)

    def pause(self):
        """Pause this agent (stop checking for new properties)"""
        self.db.update_agent_status(self.agent_id, 'paused')
        self.status = 'paused'
        logger.info(f"Agent {self.agent_id} paused")

    def resume(self):
        """Resume this agent"""
        self.db.update_agent_status(self.agent_id, 'active')
        self.status = 'active'
        logger.info(f"Agent {self.agent_id} resumed")

    def cancel(self):
        """Cancel this agent (stop and mark as cancelled)"""
        self.db.update_agent_status(self.agent_id, 'cancelled')
        self.status = 'cancelled'
        logger.info(f"Agent {self.agent_id} cancelled")

    def complete(self):
        """Mark agent as completed (property found, client satisfied)"""
        self.db.update_agent_status(self.agent_id, 'completed')
        self.status = 'completed'
        logger.info(f"Agent {self.agent_id} completed")
