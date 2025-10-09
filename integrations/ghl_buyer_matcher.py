"""
GoHighLevel Buyer Matcher
Intelligent buyer-property matching and automated notifications.
"""

from typing import Dict, List, Tuple, Optional
import logging
from datetime import datetime, timedelta


class BuyerMatcher:
    """Matches properties to buyers based on preferences and sends automated notifications"""

    def __init__(self, ghl_connector, db_manager, config: Dict):
        """
        Initialize buyer matcher

        Args:
            ghl_connector: GoHighLevelConnector instance
            db_manager: Database manager for caching and tracking
            config: Configuration dictionary
        """
        self.ghl = ghl_connector
        self.db = db_manager
        self.config = config
        self.logger = logging.getLogger(__name__)

        # Cache settings
        self.buyer_cache_duration = config.get("buyer_cache_duration_minutes", 60)
        self.max_sms_per_day = config.get("max_sms_per_buyer_per_day", 3)

    def fetch_active_buyers_from_ghl(self, use_cache: bool = True) -> List[Dict]:
        """
        Get all active buyers from GHL with optional caching

        Args:
            use_cache: If True, use cached buyers if available and fresh

        Returns:
            List of active buyer contact dictionaries
        """
        try:
            # Check cache if enabled
            if use_cache and self.db:
                cached_buyers = self._get_cached_buyers()
                if cached_buyers:
                    self.logger.info(f"Using cached buyers: {len(cached_buyers)} found")
                    return cached_buyers

            # Fetch from GHL
            self.logger.info("Fetching active buyers from GHL...")
            buyers = self.ghl.search_contacts(tags=["active_buyer"])

            # Cache in database if available
            if self.db and buyers:
                self._cache_buyers(buyers)

            self.logger.info(f"Fetched {len(buyers)} active buyers from GHL")
            return buyers

        except Exception as e:
            self.logger.error(f"Failed to fetch buyers: {e}")
            return []

    def _get_cached_buyers(self) -> Optional[List[Dict]]:
        """Get buyers from cache if fresh"""
        try:
            # This would interact with actual database
            # Placeholder for database query
            # Check if cache exists and is within cache_duration
            cache_timestamp = None  # Get from DB
            if cache_timestamp:
                age_minutes = (datetime.now() - cache_timestamp).total_seconds() / 60
                if age_minutes < self.buyer_cache_duration:
                    # Return cached buyers from DB
                    return None  # Would return actual cached data
            return None
        except Exception as e:
            self.logger.warning(f"Cache lookup failed: {e}")
            return None

    def _cache_buyers(self, buyers: List[Dict]):
        """Cache buyers in database"""
        try:
            # This would save to actual database
            # Placeholder for database insert/update
            self.logger.debug(f"Cached {len(buyers)} buyers")
        except Exception as e:
            self.logger.warning(f"Failed to cache buyers: {e}")

    def calculate_match_score(self, property_data: Dict, buyer: Dict) -> Tuple[int, List[str]]:
        """
        Calculate 0-100 match score between property and buyer

        Scoring breakdown:
        - Budget match (40 points): Price within buyer's range
        - Location match (30 points): City/ZIP match
        - Property type (20 points): Single family, multi-family, etc.
        - Bedrooms (10 points): Meets minimum requirement

        Args:
            property_data: Property information
            buyer: Buyer contact with preferences in custom fields

        Returns:
            Tuple of (score, list of match reasons)
        """
        score = 0
        reasons = []

        # Extract property details
        property_price = property_data.get("list_price", 0)
        property_city = property_data.get("city", "").lower()
        property_zip = property_data.get("zip_code", "")
        property_type = property_data.get("property_type", "").lower()
        property_bedrooms = property_data.get("bedrooms", 0)

        # Extract buyer preferences from custom fields
        buyer_custom_fields = buyer.get("customFields", {})
        budget_min = buyer_custom_fields.get("budget_min", 0)
        budget_max = buyer_custom_fields.get("budget_max", float('inf'))
        location_pref = buyer_custom_fields.get("location_preference", "").lower()
        property_type_pref = buyer_custom_fields.get("property_type_preference", "").lower()
        min_bedrooms = buyer_custom_fields.get("min_bedrooms", 0)

        # Convert string values to numbers if needed
        try:
            budget_min = float(budget_min) if budget_min else 0
            budget_max = float(budget_max) if budget_max else float('inf')
            min_bedrooms = int(min_bedrooms) if min_bedrooms else 0
        except (ValueError, TypeError):
            self.logger.warning(f"Invalid buyer preference values for {buyer.get('email', 'unknown')}")

        # 1. Budget Match (40 points)
        if budget_min <= property_price <= budget_max:
            score += 40
            reasons.append(f"Price ${property_price:,.0f} within budget (${budget_min:,.0f}-${budget_max:,.0f})")
        elif property_price < budget_min:
            # Still give partial points if property is cheaper
            score += 30
            reasons.append(f"Price ${property_price:,.0f} below budget")
        elif property_price <= budget_max * 1.1:
            # Partial points if slightly over budget (within 10%)
            score += 20
            reasons.append(f"Price ${property_price:,.0f} slightly above budget")

        # 2. Location Match (30 points)
        location_matches = []
        if location_pref:
            # Split multiple locations (e.g., "austin, dallas, houston")
            preferred_locations = [loc.strip() for loc in location_pref.split(",")]

            for pref_loc in preferred_locations:
                if pref_loc in property_city or pref_loc in property_zip:
                    score += 30
                    location_matches.append(pref_loc)
                    break

            if location_matches:
                reasons.append(f"Location match: {', '.join(location_matches)}")
        else:
            # No preference specified - give neutral score
            score += 15

        # 3. Property Type Match (20 points)
        if property_type_pref:
            property_type_prefs = [t.strip() for t in property_type_pref.split(",")]

            for pref_type in property_type_prefs:
                if pref_type in property_type or property_type in pref_type:
                    score += 20
                    reasons.append(f"Property type match: {property_type}")
                    break
        else:
            # No preference - neutral score
            score += 10

        # 4. Bedrooms Match (10 points)
        if property_bedrooms >= min_bedrooms:
            score += 10
            reasons.append(f"{property_bedrooms} bedrooms meets requirement ({min_bedrooms}+)")
        elif min_bedrooms == 0:
            # No requirement specified
            score += 5

        # Ensure score is within 0-100
        score = min(100, max(0, score))

        return score, reasons

    def match_property_to_buyers(self, property_data: Dict, min_score: int = 70) -> List[Dict]:
        """
        Match property to buyers and return top matches

        Args:
            property_data: Property information
            min_score: Minimum match score to include (default 70)

        Returns:
            List of top 5 matches sorted by score, each containing buyer and match info
        """
        buyers = self.fetch_active_buyers_from_ghl()

        if not buyers:
            self.logger.warning("No active buyers found")
            return []

        matches = []

        for buyer in buyers:
            score, reasons = self.calculate_match_score(property_data, buyer)

            if score >= min_score:
                matches.append({
                    "buyer": buyer,
                    "score": score,
                    "reasons": reasons,
                    "contact_id": buyer.get("id"),
                    "email": buyer.get("email"),
                    "name": f"{buyer.get('firstName', '')} {buyer.get('lastName', '')}".strip()
                })

        # Sort by score descending and take top 5
        matches.sort(key=lambda x: x["score"], reverse=True)
        top_matches = matches[:5]

        self.logger.info(
            f"Found {len(matches)} matches (score >= {min_score}) for {property_data.get('address')}. "
            f"Returning top {len(top_matches)}"
        )

        return top_matches

    def notify_matched_buyers(self, property_data: Dict, matched_buyers: List[Dict]) -> Dict:
        """
        Send notifications to matched buyers via SMS and workflows

        Args:
            property_data: Property information
            matched_buyers: List of matched buyer dictionaries from match_property_to_buyers

        Returns:
            Statistics dictionary with notified, skipped, errors
        """
        stats = {
            "total": len(matched_buyers),
            "notified": 0,
            "skipped": 0,
            "errors": []
        }

        property_id = property_data.get("id", "unknown")
        address = property_data.get("address", "Unknown Address")

        for match in matched_buyers:
            buyer = match["buyer"]
            contact_id = match["contact_id"]
            match_score = match["score"]
            reasons = match["reasons"]

            try:
                # Check SMS opt-in
                if not self.check_sms_opt_in(buyer):
                    self.logger.info(f"Skipping {contact_id} - no SMS opt-in")
                    stats["skipped"] += 1
                    continue

                # Check quiet hours
                if not self.check_quiet_hours():
                    self.logger.info(f"Skipping {contact_id} - quiet hours")
                    stats["skipped"] += 1
                    continue

                # Check daily SMS limit
                sms_count_today = self.get_sms_count_today(contact_id)
                if sms_count_today >= self.max_sms_per_day:
                    self.logger.info(f"Skipping {contact_id} - SMS limit reached ({sms_count_today}/{self.max_sms_per_day})")
                    stats["skipped"] += 1
                    continue

                # Send SMS
                sms_message = self._create_match_sms(property_data, match_score)
                self.ghl.send_sms(contact_id, sms_message)
                self._record_sms_sent(contact_id, property_id)

                # Trigger workflow if configured
                workflow_id = self.config.get("workflows", {}).get("property_match")
                if workflow_id:
                    custom_data = {
                        "property_address": address,
                        "match_score": match_score,
                        "list_price": property_data.get("list_price", 0),
                        "property_id": property_id
                    }
                    self.ghl.trigger_workflow(workflow_id, contact_id, custom_data)

                # Add tag
                tag = f"matched_{property_id}"
                self.ghl.add_contact_tags(contact_id, [tag])

                # Add note with match details
                note_text = f"""
PROPERTY MATCH - Score: {match_score}/100

Property: {address}
Price: ${property_data.get('list_price', 0):,.0f}

Match Reasons:
{chr(10).join(f'- {reason}' for reason in reasons)}

Deal Score: {property_data.get('deal_score', 0)}/100
                """.strip()
                self.ghl.add_note(contact_id, note_text)

                # Create follow-up task if configured
                if self.config.get("create_followup_tasks", True):
                    task_data = {
                        "title": f"Follow up with {match['name']} - Property Match",
                        "description": f"Matched buyer to {address}. Match score: {match_score}/100",
                        "assignedTo": self.config.get("default_assignee"),
                        "dueDate": (datetime.now() + timedelta(hours=4)).isoformat(),
                        "priority": "high" if match_score >= 85 else "medium"
                    }
                    self.ghl.create_task(task_data)

                stats["notified"] += 1
                self.logger.info(f"Notified buyer {contact_id} about {address} (score: {match_score})")

            except Exception as e:
                stats["errors"].append({
                    "buyer": match.get("name", "Unknown"),
                    "contact_id": contact_id,
                    "error": str(e)
                })
                self.logger.error(f"Failed to notify buyer {contact_id}: {e}")

        self.logger.info(
            f"Notification complete: {stats['notified']} notified, {stats['skipped']} skipped, "
            f"{len(stats['errors'])} errors out of {stats['total']}"
        )

        return stats

    def _create_match_sms(self, property_data: Dict, match_score: int) -> str:
        """
        Create SMS message for property match

        Args:
            property_data: Property information
            match_score: Match score

        Returns:
            SMS message text
        """
        address = property_data.get("address", "Unknown")
        price = property_data.get("list_price", 0)
        bedrooms = property_data.get("bedrooms", "?")
        bathrooms = property_data.get("bathrooms", "?")
        sqft = property_data.get("sqft", 0)

        message = (
            f"NEW PROPERTY MATCH ({match_score}% match)! "
            f"{address} - ${price:,.0f}. "
            f"{bedrooms}bd/{bathrooms}ba, {sqft:,.0f}sqft. "
            f"Reply YES for details or call to schedule showing."
        )

        # Ensure message is under SMS character limit (160 for single SMS)
        if len(message) > 160:
            message = (
                f"NEW MATCH ({match_score}%)! {address} - ${price:,.0f}. "
                f"{bedrooms}bd/{bathrooms}ba. Reply YES for info."
            )

        return message

    def check_sms_opt_in(self, contact: Dict) -> bool:
        """
        Verify contact has SMS opt-in

        Args:
            contact: Contact dictionary

        Returns:
            True if contact has SMS opt-in
        """
        tags = contact.get("tags", [])
        return "sms_opt_in" in tags or contact.get("dnd", False) is False

    def check_quiet_hours(self) -> bool:
        """
        Check if current time is outside quiet hours (9 PM - 8 AM)

        Returns:
            True if outside quiet hours (OK to send)
        """
        current_hour = datetime.now().hour
        return 8 <= current_hour < 21

    def get_sms_count_today(self, contact_id: str) -> int:
        """
        Get number of SMS messages sent to contact today

        Args:
            contact_id: GHL contact ID

        Returns:
            Count of SMS sent today
        """
        try:
            if not self.db:
                return 0

            # This would query actual database
            # Placeholder for database query
            # SELECT COUNT(*) FROM sms_log WHERE contact_id = ? AND date = TODAY
            return 0  # Would return actual count

        except Exception as e:
            self.logger.warning(f"Failed to get SMS count: {e}")
            return 0

    def _record_sms_sent(self, contact_id: str, property_id: str):
        """
        Record SMS sent in database for tracking

        Args:
            contact_id: GHL contact ID
            property_id: Property ID
        """
        try:
            if not self.db:
                return

            # This would insert into actual database
            # Placeholder for database insert
            # INSERT INTO sms_log (contact_id, property_id, sent_at) VALUES (?, ?, NOW())
            self.logger.debug(f"Recorded SMS sent to {contact_id} for property {property_id}")

        except Exception as e:
            self.logger.warning(f"Failed to record SMS: {e}")

    def update_buyer_preferences(self, contact_id: str, preferences: Dict) -> bool:
        """
        Update buyer preferences in GHL

        Args:
            contact_id: GHL contact ID
            preferences: Dictionary of preference fields to update

        Returns:
            True if successful
        """
        try:
            custom_fields = {}

            # Map preferences to custom field keys
            field_mapping = {
                "budget_min": "budget_min",
                "budget_max": "budget_max",
                "location_preference": "location_preference",
                "property_type_preference": "property_type_preference",
                "min_bedrooms": "min_bedrooms"
            }

            for pref_key, value in preferences.items():
                if pref_key in field_mapping:
                    custom_fields[field_mapping[pref_key]] = value

            if custom_fields:
                self.ghl.update_contact(contact_id, {"customFields": custom_fields})
                self.logger.info(f"Updated preferences for contact {contact_id}")
                return True

            return False

        except Exception as e:
            self.logger.error(f"Failed to update buyer preferences: {e}")
            return False
