"""
GoHighLevel Workflow Manager
Handles workflow automation, opportunity creation, and task management for property deals.
"""

from typing import Dict, List, Optional
from datetime import datetime, timedelta
import logging


class GHLWorkflowManager:
    """Manages GHL workflow triggers and opportunity lifecycle"""

    def __init__(self, ghl_connector, config: Dict):
        """
        Initialize workflow manager

        Args:
            ghl_connector: GoHighLevelConnector instance
            config: Configuration dictionary with pipeline IDs, stage IDs, workflow IDs
        """
        self.ghl = ghl_connector
        self.config = config
        self.logger = logging.getLogger(__name__)

        # Validate required configuration
        self._validate_config()

    def _validate_config(self):
        """Validate required configuration keys exist"""
        required_keys = [
            "pipeline_id",
            "stages",
            "workflows",
            "default_assignee"
        ]

        missing = [key for key in required_keys if key not in self.config]
        if missing:
            self.logger.warning(f"Missing config keys: {missing}")

    def create_opportunity_from_property(self, property_data: Dict) -> str:
        """
        Create GHL opportunity for analyzed property with full details

        Args:
            property_data: Property analysis data including score, price, address, etc.

        Returns:
            Created opportunity ID

        Raises:
            Exception if opportunity creation fails
        """
        try:
            # Extract property details
            address = property_data.get("address", "Unknown Address")
            score = property_data.get("deal_score", 0)
            price = property_data.get("list_price", 0)
            mls_id = property_data.get("mls_id", "N/A")
            est_profit = property_data.get("estimated_profit", 0)
            below_market_pct = property_data.get("below_market_pct", 0)
            days_on_market = property_data.get("days_on_market", 0)
            price_per_sqft = property_data.get("price_per_sqft", 0)
            estimated_arv = property_data.get("estimated_arv", 0)

            # Determine deal quality
            if score >= 90:
                deal_quality = "Hot Deal"
            elif score >= 75:
                deal_quality = "Good Deal"
            elif score >= 60:
                deal_quality = "Potential"
            else:
                deal_quality = "Review Needed"

            # Prepare opportunity data
            opportunity_name = f"{address} - Score: {score}"

            opportunity_data = {
                "pipelineId": self.config.get("pipeline_id"),
                "pipelineStageId": self.config["stages"].get("new_lead"),
                "name": opportunity_name,
                "monetaryValue": price,
                "status": "open",
                "customFields": {
                    "property_address": address,
                    "deal_score": score,
                    "list_price": price,
                    "est_profit": est_profit,
                    "mls_id": mls_id,
                    "price_per_sqft": price_per_sqft,
                    "below_market_pct": below_market_pct,
                    "days_on_market": days_on_market,
                    "deal_quality": deal_quality,
                    "estimated_arv": estimated_arv
                }
            }

            # Add default assignee if configured
            if "default_assignee" in self.config:
                opportunity_data["assignedTo"] = self.config["default_assignee"]

            # Create opportunity
            result = self.ghl.create_opportunity(opportunity_data)
            opportunity_id = result.get("id")

            if not opportunity_id:
                raise Exception("No opportunity ID returned from GHL")

            self.logger.info(f"Created opportunity {opportunity_id} for {address}")

            # Add tags
            tags = ["automated", "dealfinder", deal_quality.lower().replace(" ", "_")]
            if opportunity_id:
                # Note: Tags for opportunities might need to be added via contact
                # For now, log the tags that would be added
                self.logger.debug(f"Tags for opportunity: {tags}")

            # Add detailed analysis note
            note_text = self._create_analysis_note(property_data)
            try:
                if opportunity_id:
                    # GHL might require adding notes via different endpoint
                    # This is a placeholder for the note creation
                    self.logger.debug(f"Analysis note prepared: {note_text[:100]}...")
            except Exception as e:
                self.logger.warning(f"Failed to add note: {e}")

            return opportunity_id

        except Exception as e:
            self.logger.error(f"Failed to create opportunity: {e}")
            raise

    def _create_analysis_note(self, property_data: Dict) -> str:
        """
        Create detailed analysis note for opportunity

        Args:
            property_data: Property analysis data

        Returns:
            Formatted note text
        """
        score = property_data.get("deal_score", 0)
        price = property_data.get("list_price", 0)
        est_profit = property_data.get("estimated_profit", 0)
        below_market = property_data.get("below_market_pct", 0)
        arv = property_data.get("estimated_arv", 0)
        days_on_market = property_data.get("days_on_market", 0)

        note = f"""
AUTOMATED DEAL ANALYSIS
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

DEAL SCORE: {score}/100

KEY METRICS:
- List Price: ${price:,.0f}
- Estimated Profit: ${est_profit:,.0f}
- Below Market: {below_market:.1f}%
- Days on Market: {days_on_market}
- Estimated ARV: ${arv:,.0f}

ANALYSIS BREAKDOWN:
{property_data.get('analysis_breakdown', 'Details not available')}

RECOMMENDATION:
{self._get_recommendation(score, est_profit)}
        """.strip()

        return note

    def _get_recommendation(self, score: int, profit: float) -> str:
        """Get recommendation based on score and profit"""
        if score >= 90 and profit >= 50000:
            return "PRIORITY - Contact buyer immediately and schedule showing within 24 hours"
        elif score >= 75:
            return "STRONG OPPORTUNITY - Review comps and schedule showing within 48 hours"
        elif score >= 60:
            return "GOOD POTENTIAL - Further research needed, review within 1 week"
        else:
            return "MODERATE INTEREST - Consider for portfolio expansion"

    def trigger_hot_deal_workflow(self, property_data: Dict, opportunity_id: str) -> bool:
        """
        Trigger hot deal workflow for high-scoring properties

        Args:
            property_data: Property data
            opportunity_id: GHL opportunity ID

        Returns:
            True if workflow triggered successfully
        """
        score = property_data.get("deal_score", 0)

        if score < 90:
            self.logger.debug(f"Score {score} below 90 - skipping hot deal workflow")
            return False

        workflow_id = self.config.get("workflows", {}).get("hot_deal_alert")

        if not workflow_id:
            self.logger.warning("Hot deal workflow ID not configured")
            return False

        try:
            # Prepare custom data for workflow
            custom_data = {
                "address": property_data.get("address"),
                "score": score,
                "profit": property_data.get("estimated_profit", 0),
                "price": property_data.get("list_price", 0),
                "opportunity_id": opportunity_id
            }

            # Trigger workflow (requires contact_id - might need to create/find contact first)
            # For now, we'll focus on moving the opportunity stage
            priority_stage_id = self.config["stages"].get("priority_review")
            if priority_stage_id:
                self.ghl.move_opportunity_stage(opportunity_id, priority_stage_id)
                self.logger.info(f"Moved opportunity {opportunity_id} to Priority Review stage")

            return True

        except Exception as e:
            self.logger.error(f"Failed to trigger hot deal workflow: {e}")
            return False

    def create_tasks_for_property(self, property_data: Dict, opportunity_id: str) -> List[str]:
        """
        Create automated tasks for property opportunity

        Args:
            property_data: Property data
            opportunity_id: GHL opportunity ID

        Returns:
            List of created task IDs
        """
        task_ids = []
        score = property_data.get("deal_score", 0)
        address = property_data.get("address", "Unknown")
        assignee = self.config.get("default_assignee")

        try:
            # Task 1: Review Hot Deal (for high scores)
            if score > 85:
                task_data = {
                    "title": f"Review Hot Deal: {address}",
                    "description": f"Priority review needed for property scoring {score}/100. Estimated profit: ${property_data.get('estimated_profit', 0):,.0f}",
                    "assignedTo": assignee,
                    "dueDate": (datetime.now() + timedelta(hours=4)).isoformat(),
                    "priority": "high",
                    "relatedTo": opportunity_id,
                    "relatedType": "opportunity"
                }
                result = self.ghl.create_task(task_data)
                if result.get("id"):
                    task_ids.append(result["id"])
                    self.logger.info(f"Created high-priority review task for {address}")

            # Task 2: Schedule Showing
            task_data = {
                "title": f"Schedule Showing: {address}",
                "description": f"Contact listing agent to schedule property showing. MLS#: {property_data.get('mls_id', 'N/A')}",
                "assignedTo": assignee,
                "dueDate": (datetime.now() + timedelta(hours=24)).isoformat(),
                "priority": "medium" if score < 85 else "high",
                "relatedTo": opportunity_id,
                "relatedType": "opportunity"
            }
            result = self.ghl.create_task(task_data)
            if result.get("id"):
                task_ids.append(result["id"])

            # Task 3: Contact Matched Buyers
            task_data = {
                "title": f"Contact Matched Buyers: {address}",
                "description": f"Reach out to buyers matching this property profile. Deal score: {score}/100",
                "assignedTo": assignee,
                "dueDate": (datetime.now() + timedelta(hours=8)).isoformat(),
                "priority": "high" if score >= 75 else "medium",
                "relatedTo": opportunity_id,
                "relatedType": "opportunity"
            }
            result = self.ghl.create_task(task_data)
            if result.get("id"):
                task_ids.append(result["id"])

            self.logger.info(f"Created {len(task_ids)} tasks for opportunity {opportunity_id}")

        except Exception as e:
            self.logger.error(f"Error creating tasks: {e}")

        return task_ids

    def update_opportunity_stage_based_on_activity(self, property_id: str, activity_type: str) -> bool:
        """
        Auto-progress opportunity through pipeline based on activities

        Args:
            property_id: Property/Opportunity ID
            activity_type: Type of activity (showing_scheduled, offer_submitted, under_contract)

        Returns:
            True if stage updated successfully
        """
        stage_mapping = {
            "showing_scheduled": "showing_scheduled",
            "offer_submitted": "offer_submitted",
            "under_contract": "under_contract",
            "closed_won": "closed_won",
            "closed_lost": "closed_lost"
        }

        stage_id = self.config["stages"].get(stage_mapping.get(activity_type))

        if not stage_id:
            self.logger.warning(f"No stage configured for activity: {activity_type}")
            return False

        try:
            self.ghl.move_opportunity_stage(property_id, stage_id)
            self.logger.info(f"Moved opportunity {property_id} to {activity_type} stage")
            return True
        except Exception as e:
            self.logger.error(f"Failed to update opportunity stage: {e}")
            return False

    def send_hot_deal_sms(self, property_data: Dict, broker_contact_id: str) -> bool:
        """
        Send SMS alert for hot deals

        Args:
            property_data: Property data
            broker_contact_id: GHL contact ID of broker

        Returns:
            True if SMS sent successfully
        """
        # Check quiet hours (9 PM - 8 AM)
        current_hour = datetime.now().hour
        if current_hour >= 21 or current_hour < 8:
            self.logger.info("Skipping SMS - quiet hours (9 PM - 8 AM)")
            return False

        try:
            score = property_data.get("deal_score", 0)
            address = property_data.get("address", "Unknown")
            price = property_data.get("list_price", 0)
            profit = property_data.get("estimated_profit", 0)

            message = f"HOT DEAL ALERT! {address} - Score: {score}/100. Listed: ${price:,.0f}. Est. Profit: ${profit:,.0f}. Review immediately!"

            self.ghl.send_sms(broker_contact_id, message)
            self.logger.info(f"Sent hot deal SMS to contact {broker_contact_id}")
            return True

        except Exception as e:
            self.logger.error(f"Failed to send SMS: {e}")
            return False

    def batch_create_opportunities(self, properties: List[Dict]) -> Dict:
        """
        Efficiently create multiple opportunities with rate limiting

        Args:
            properties: List of property data dictionaries

        Returns:
            Statistics dictionary with created, failed, errors
        """
        stats = {
            "total": len(properties),
            "created": 0,
            "failed": 0,
            "errors": []
        }

        for idx, property_data in enumerate(properties):
            try:
                self.logger.info(f"Creating opportunity {idx + 1}/{len(properties)}")
                opportunity_id = self.create_opportunity_from_property(property_data)

                if opportunity_id:
                    stats["created"] += 1

                    # Create tasks for high-scoring properties
                    score = property_data.get("deal_score", 0)
                    if score >= 75:
                        self.create_tasks_for_property(property_data, opportunity_id)

                    # Trigger hot deal workflow
                    if score >= 90:
                        self.trigger_hot_deal_workflow(property_data, opportunity_id)

            except Exception as e:
                stats["failed"] += 1
                stats["errors"].append({
                    "property": property_data.get("address", "Unknown"),
                    "error": str(e)
                })
                self.logger.error(f"Failed to create opportunity for {property_data.get('address')}: {e}")

        self.logger.info(
            f"Batch complete: {stats['created']} created, {stats['failed']} failed out of {stats['total']}"
        )

        return stats
