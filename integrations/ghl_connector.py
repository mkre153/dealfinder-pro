"""
GoHighLevel API Connector (v2 API)
Handles all direct API communication with GHL v2 API with rate limiting and error handling.
Base URL: https://services.leadconnectorhq.com
"""

import requests
import time
from collections import deque
from typing import Dict, List, Optional, Any
import logging
from datetime import datetime, timedelta


class GHLRateLimiter:
    """Prevents exceeding 100 requests/minute by tracking request timestamps"""

    def __init__(self, max_requests: int = 95, time_window: int = 60):
        """
        Initialize rate limiter

        Args:
            max_requests: Maximum requests allowed in time window (default 95 to be safe)
            time_window: Time window in seconds (default 60 for 1 minute)
        """
        self.requests = deque()
        self.max_requests = max_requests
        self.time_window = time_window
        self.logger = logging.getLogger(__name__)

    def wait_if_needed(self):
        """Wait if we've hit the rate limit, removing expired timestamps"""
        now = time.time()

        # Remove requests outside the time window
        while self.requests and (now - self.requests[0]) > self.time_window:
            self.requests.popleft()

        # If at limit, calculate sleep time
        if len(self.requests) >= self.max_requests:
            oldest_request = self.requests[0]
            sleep_time = self.time_window - (now - oldest_request) + 0.1  # Add 100ms buffer
            if sleep_time > 0:
                self.logger.warning(f"Rate limit reached. Sleeping for {sleep_time:.2f} seconds")
                time.sleep(sleep_time)
                # Clean up old requests after sleep
                now = time.time()
                while self.requests and (now - self.requests[0]) > self.time_window:
                    self.requests.popleft()

        # Track this request
        self.requests.append(now)

    def get_remaining_requests(self) -> int:
        """Get number of requests remaining in current window"""
        now = time.time()
        # Remove expired requests
        while self.requests and (now - self.requests[0]) > self.time_window:
            self.requests.popleft()
        return max(0, self.max_requests - len(self.requests))


class GHLAPIError(Exception):
    """Custom exception for GHL API errors"""

    def __init__(self, message: str, status_code: int = None, response: Dict = None):
        self.message = message
        self.status_code = status_code
        self.response = response
        super().__init__(self.message)


class GoHighLevelConnector:
    """Main GHL API client with comprehensive error handling and rate limiting"""

    def __init__(self, api_key: str, location_id: str, test_mode: bool = False):
        """
        Initialize GHL connector (v2 API)

        Args:
            api_key: GHL API key (Private Integration Token - PIT)
            location_id: GHL location ID
            test_mode: If True, log actions but don't make actual API calls
        """
        self.api_key = api_key
        self.location_id = location_id
        self.base_url = "https://services.leadconnectorhq.com"
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "Version": "2021-07-28"
        }
        self.rate_limiter = GHLRateLimiter()
        self.test_mode = test_mode
        self.logger = logging.getLogger(__name__)

        if test_mode:
            self.logger.info("GHL Connector initialized in TEST MODE - no actual API calls will be made")

    def _request(self, method: str, endpoint: str, retry_count: int = 3, **kwargs) -> Dict:
        """
        Make HTTP request with rate limiting and error handling

        Args:
            method: HTTP method (GET, POST, PUT, DELETE)
            endpoint: API endpoint (without base URL)
            retry_count: Number of retries for server errors
            **kwargs: Additional arguments for requests library

        Returns:
            Response data as dictionary

        Raises:
            GHLAPIError: For API errors
        """
        url = f"{self.base_url}{endpoint}"

        # Test mode - log and return mock response
        if self.test_mode:
            self.logger.info(f"[TEST MODE] {method} {url}")
            self.logger.debug(f"[TEST MODE] Data: {kwargs.get('json', {})}")
            return {"test_mode": True, "message": "No actual API call made"}

        # Wait for rate limiter
        self.rate_limiter.wait_if_needed()

        for attempt in range(retry_count):
            try:
                self.logger.debug(f"API Request: {method} {url} (attempt {attempt + 1}/{retry_count})")

                response = requests.request(
                    method=method,
                    url=url,
                    headers=self.headers,
                    timeout=30,
                    **kwargs
                )

                # Handle specific status codes
                if response.status_code == 401:
                    raise GHLAPIError(
                        "Authentication failed - invalid API key",
                        status_code=401,
                        response=response.json() if response.text else {}
                    )

                if response.status_code == 429:
                    # Rate limit exceeded - check Retry-After header
                    retry_after = int(response.headers.get('Retry-After', 60))
                    self.logger.warning(f"Rate limit exceeded. Waiting {retry_after} seconds")
                    time.sleep(retry_after)
                    continue

                if response.status_code == 404:
                    raise GHLAPIError(
                        f"Resource not found: {endpoint}",
                        status_code=404,
                        response=response.json() if response.text else {}
                    )

                if response.status_code >= 500:
                    # Server error - retry
                    if attempt < retry_count - 1:
                        wait_time = (2 ** attempt) * 1  # Exponential backoff: 1s, 2s, 4s
                        self.logger.warning(f"Server error {response.status_code}. Retrying in {wait_time}s")
                        time.sleep(wait_time)
                        continue
                    else:
                        raise GHLAPIError(
                            f"Server error after {retry_count} attempts",
                            status_code=response.status_code,
                            response=response.json() if response.text else {}
                        )

                # Check for success
                if response.status_code >= 400:
                    raise GHLAPIError(
                        f"API error: {response.status_code}",
                        status_code=response.status_code,
                        response=response.json() if response.text else {}
                    )

                # Success
                result = response.json() if response.text else {}
                self.logger.debug(f"API Response: {response.status_code}")
                return result

            except requests.exceptions.RequestException as e:
                if attempt < retry_count - 1:
                    wait_time = (2 ** attempt) * 1
                    self.logger.warning(f"Request exception: {e}. Retrying in {wait_time}s")
                    time.sleep(wait_time)
                    continue
                else:
                    raise GHLAPIError(f"Request failed after {retry_count} attempts: {str(e)}")

        raise GHLAPIError(f"Request failed after {retry_count} attempts")

    def test_connection(self) -> bool:
        """
        Validate API key and connection (v2 API)

        Returns:
            True if connection is valid
        """
        try:
            if self.test_mode:
                self.logger.info("[TEST MODE] Connection test - simulated success")
                return True

            # Test by getting location details
            self._request("GET", f"/locations/{self.location_id}")
            self.logger.info("GHL v2 connection test successful")
            return True
        except GHLAPIError as e:
            self.logger.error(f"GHL connection test failed: {e.message}")
            return False

    # CONTACT MANAGEMENT

    def get_contacts(self, filters: Dict = None, limit: int = 100, offset: int = 0) -> List[Dict]:
        """
        Get contacts with optional filters

        Args:
            filters: Query parameters for filtering
            limit: Maximum number of results (default 100)
            offset: Pagination offset

        Returns:
            List of contact dictionaries
        """
        params = {
            "locationId": self.location_id,
            "limit": limit,
            "skip": offset
        }

        if filters:
            params.update(filters)

        response = self._request("GET", "/contacts/", params=params)
        return response.get("contacts", [])

    def search_contacts(self, tags: List[str] = None, custom_fields: Dict = None) -> List[Dict]:
        """
        Advanced contact search by tags and custom fields

        Args:
            tags: List of tags to filter by
            custom_fields: Dictionary of custom field key-value pairs

        Returns:
            List of matching contacts
        """
        all_contacts = []
        offset = 0
        limit = 100

        while True:
            contacts = self.get_contacts(limit=limit, offset=offset)

            if not contacts:
                break

            # Filter by tags
            if tags:
                contacts = [c for c in contacts if any(tag in c.get("tags", []) for tag in tags)]

            # Filter by custom fields
            if custom_fields:
                filtered = []
                for contact in contacts:
                    contact_custom_fields = contact.get("customFields", {})
                    match = all(
                        contact_custom_fields.get(key) == value
                        for key, value in custom_fields.items()
                    )
                    if match:
                        filtered.append(contact)
                contacts = filtered

            all_contacts.extend(contacts)

            # Check if we got fewer than limit (last page)
            if len(contacts) < limit:
                break

            offset += limit

        return all_contacts

    def create_contact(self, contact_data: Dict) -> Dict:
        """
        Create new contact

        Args:
            contact_data: Contact information (firstName, lastName, email, phone, etc.)

        Returns:
            Created contact with ID
        """
        contact_data["locationId"] = self.location_id
        response = self._request("POST", "/contacts/", json=contact_data)
        return response.get("contact", response)

    def update_contact(self, contact_id: str, updates: Dict) -> Dict:
        """
        Update existing contact

        Args:
            contact_id: GHL contact ID
            updates: Fields to update

        Returns:
            Updated contact data
        """
        response = self._request("PUT", f"/contacts/{contact_id}", json=updates)
        return response.get("contact", response)

    def add_contact_tags(self, contact_id: str, tags: List[str]) -> bool:
        """
        Add tags to contact

        Args:
            contact_id: GHL contact ID
            tags: List of tag names

        Returns:
            True if successful
        """
        try:
            self._request("POST", f"/contacts/{contact_id}/tags", json={"tags": tags})
            return True
        except GHLAPIError:
            return False

    def update_custom_field(self, contact_id: str, field_key: str, value: Any) -> bool:
        """
        Update single custom field for contact

        Args:
            contact_id: GHL contact ID
            field_key: Custom field key
            value: New value

        Returns:
            True if successful
        """
        try:
            self.update_contact(contact_id, {
                "customFields": {field_key: value}
            })
            return True
        except GHLAPIError:
            return False

    def get_contact_by_email(self, email: str) -> Optional[Dict]:
        """
        Search for contact by email address

        Args:
            email: Email address

        Returns:
            Contact dictionary or None if not found
        """
        contacts = self.get_contacts(filters={"email": email}, limit=1)
        return contacts[0] if contacts else None

    # OPPORTUNITY MANAGEMENT

    def create_opportunity(self, opportunity_data: Dict) -> Dict:
        """
        Create new opportunity (v2 API)

        Args:
            opportunity_data: Must include pipelineId, name, pipelineStageId, contactId
                Optional: monetaryValue, status, assignedTo, customFields

        Returns:
            Created opportunity with ID
        """
        opportunity_data["locationId"] = self.location_id
        response = self._request("POST", "/opportunities/", json=opportunity_data)
        return response.get("opportunity", response)

    def update_opportunity(self, opportunity_id: str, updates: Dict) -> Dict:
        """
        Update existing opportunity

        Args:
            opportunity_id: GHL opportunity ID
            updates: Fields to update

        Returns:
            Updated opportunity data
        """
        response = self._request("PUT", f"/opportunities/{opportunity_id}", json=updates)
        return response.get("opportunity", response)

    def move_opportunity_stage(self, opportunity_id: str, stage_id: str) -> bool:
        """
        Move opportunity to different pipeline stage

        Args:
            opportunity_id: GHL opportunity ID
            stage_id: Target pipeline stage ID

        Returns:
            True if successful
        """
        try:
            self.update_opportunity(opportunity_id, {"pipelineStageId": stage_id})
            return True
        except GHLAPIError:
            return False

    def get_opportunity(self, opportunity_id: str) -> Dict:
        """
        Get opportunity by ID

        Args:
            opportunity_id: GHL opportunity ID

        Returns:
            Opportunity data
        """
        response = self._request("GET", f"/opportunities/{opportunity_id}")
        return response.get("opportunity", response)

    def get_pipeline_stages(self, pipeline_id: str) -> List[Dict]:
        """
        Get all stages for a pipeline

        Args:
            pipeline_id: GHL pipeline ID

        Returns:
            List of stage dictionaries
        """
        response = self._request("GET", f"/opportunities/pipelines/{pipeline_id}")
        pipeline = response.get("pipeline", response)
        return pipeline.get("stages", [])

    def assign_opportunity(self, opportunity_id: str, user_id: str) -> bool:
        """
        Assign opportunity to team member

        Args:
            opportunity_id: GHL opportunity ID
            user_id: GHL user ID

        Returns:
            True if successful
        """
        try:
            self.update_opportunity(opportunity_id, {"assignedTo": user_id})
            return True
        except GHLAPIError:
            return False

    # TASK MANAGEMENT

    def create_task(self, task_data: Dict) -> Dict:
        """
        Create new task

        Args:
            task_data: Task fields (title, description, assignedTo, dueDate, priority, relatedTo)

        Returns:
            Created task with ID
        """
        response = self._request("POST", "/tasks/", json=task_data)
        return response.get("task", response)

    def update_task(self, task_id: str, updates: Dict) -> Dict:
        """
        Update existing task

        Args:
            task_id: GHL task ID
            updates: Fields to update

        Returns:
            Updated task data
        """
        response = self._request("PUT", f"/tasks/{task_id}", json=updates)
        return response.get("task", response)

    def complete_task(self, task_id: str) -> bool:
        """
        Mark task as complete

        Args:
            task_id: GHL task ID

        Returns:
            True if successful
        """
        try:
            self.update_task(task_id, {"completed": True, "status": "completed"})
            return True
        except GHLAPIError:
            return False

    # WORKFLOW TRIGGERS

    def trigger_workflow(self, workflow_id: str, contact_id: str, custom_data: Dict = None) -> bool:
        """
        Trigger workflow for contact with custom data

        Args:
            workflow_id: GHL workflow ID
            contact_id: GHL contact ID
            custom_data: Custom data to pass to workflow

        Returns:
            True if successful
        """
        try:
            payload = {
                "contactId": contact_id
            }
            if custom_data:
                payload["customData"] = custom_data

            self._request("POST", f"/workflows/{workflow_id}/subscribe", json=payload)
            return True
        except GHLAPIError as e:
            self.logger.error(f"Failed to trigger workflow: {e.message}")
            return False

    def add_to_workflow(self, contact_id: str, workflow_id: str) -> bool:
        """
        Enroll contact in workflow

        Args:
            contact_id: GHL contact ID
            workflow_id: GHL workflow ID

        Returns:
            True if successful
        """
        return self.trigger_workflow(workflow_id, contact_id)

    # COMMUNICATION

    def send_sms(self, contact_id: str, message: str) -> Dict:
        """
        Send SMS message to contact

        Args:
            contact_id: GHL contact ID
            message: SMS message text

        Returns:
            Message data
        """
        payload = {
            "type": "SMS",
            "contactId": contact_id,
            "message": message
        }
        response = self._request("POST", "/conversations/messages", json=payload)
        return response

    def send_email(self, contact_id: str, subject: str, html_body: str) -> Dict:
        """
        Send email to contact

        Args:
            contact_id: GHL contact ID
            subject: Email subject
            html_body: HTML email body

        Returns:
            Message data
        """
        payload = {
            "type": "Email",
            "contactId": contact_id,
            "subject": subject,
            "html": html_body
        }
        response = self._request("POST", "/conversations/messages", json=payload)
        return response

    def add_note(self, contact_id: str, note_text: str) -> Dict:
        """
        Add note to contact

        Args:
            contact_id: GHL contact ID
            note_text: Note content

        Returns:
            Note data
        """
        payload = {
            "body": note_text
        }
        response = self._request("POST", f"/contacts/{contact_id}/notes", json=payload)
        return response

    # CUSTOM FIELDS

    def get_custom_fields(self) -> List[Dict]:
        """
        Get all custom field definitions for location

        Returns:
            List of custom field definitions
        """
        params = {"locationId": self.location_id}
        response = self._request("GET", "/custom-fields/", params=params)
        return response.get("customFields", [])

    def validate_custom_field_exists(self, field_key: str, field_type: str = 'contact') -> bool:
        """
        Check if custom field exists in GHL

        Args:
            field_key: Custom field key to validate
            field_type: 'contact' or 'opportunity'

        Returns:
            True if field exists
        """
        try:
            custom_fields = self.get_custom_fields()
            for field in custom_fields:
                if field.get("key") == field_key and field.get("model") == field_type:
                    return True
            return False
        except GHLAPIError:
            return False
