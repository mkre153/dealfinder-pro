"""
Notification Module for DealFinder Pro
Handles email, SMS, and webhook notifications
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from typing import Dict, List, Optional
import logging
import os
from datetime import datetime
import requests
import json

class Notifier:
    """Handles all notifications (email, SMS, webhooks)"""

    def __init__(self, config: Dict):
        self.config = config
        self.logger = logging.getLogger(__name__)

        # Email config
        self.email_config = config.get('notifications', {}).get('email', {})
        self.sms_config = config.get('notifications', {}).get('sms', {})
        self.webhook_config = config.get('notifications', {}).get('webhook', {})

    def send_daily_report(self, html_content: str, stats: Dict, excel_path: Optional[str] = None):
        """
        Send daily HTML email report

        Args:
            html_content: HTML email body
            stats: Workflow statistics dictionary
            excel_path: Optional path to Excel attachment
        """
        if not self.email_config.get('enabled', True):
            self.logger.info("Email notifications disabled")
            return

        subject = f"DealFinder Pro - Daily Report - {datetime.now().strftime('%B %d, %Y')}"

        # Add stats footer to HTML
        stats_html = self._generate_stats_footer(stats)
        full_html = html_content + stats_html

        self._send_email(
            to=self.email_config.get('recipient'),
            subject=subject,
            html_body=full_html,
            attachment_path=excel_path
        )

    def send_hot_deal_sms(self, property_data: Dict):
        """
        Send SMS alert for hot deal

        Args:
            property_data: Property dictionary with analysis results
        """
        if not self.sms_config.get('enabled', False):
            self.logger.info("SMS notifications disabled")
            return

        # Format SMS message
        message = f"""
🔥 HOT DEAL! Score: {property_data.get('opportunity_score', 0)}/100

{property_data.get('street_address', 'N/A')}
{property_data.get('city', '')}, {property_data.get('state', '')}

💰 ${property_data.get('list_price', 0):,}
📊 {property_data.get('below_market_percentage', 0):.1f}% below market
💵 Est. Profit: ${property_data.get('estimated_profit', 0):,}
🏠 {property_data.get('bedrooms', 0)} bed / {property_data.get('bathrooms', 0)} bath

Review immediately!
        """.strip()

        # Send via configured method
        if self.sms_config.get('via_ghl', False):
            # GHL SMS (would need GHL connector)
            self.logger.info(f"SMS notification (via GHL): {message[:50]}...")
        elif self.sms_config.get('via_twilio', False):
            self._send_twilio_sms(
                to=self.sms_config.get('broker_phone'),
                message=message
            )
        else:
            self.logger.info(f"SMS notification (simulated): {message[:50]}...")

    def send_error_alert(self, error_message: str):
        """
        Send alert when workflow fails

        Args:
            error_message: Error description
        """
        subject = "🚨 DealFinder Pro - Workflow Error"

        body = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; padding: 20px; }}
                .error-box {{ background: #ffebee; border-left: 4px solid #f44336; padding: 20px; }}
                .error-header {{ color: #c62828; font-size: 18px; font-weight: bold; }}
                .error-details {{ background: #fff; padding: 15px; margin-top: 10px; border: 1px solid #ddd; }}
                .timestamp {{ color: #666; font-size: 14px; }}
            </style>
        </head>
        <body>
            <div class="error-box">
                <div class="error-header">⚠️ Workflow Error Detected</div>
                <p class="timestamp"><strong>Time:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>

                <div class="error-details">
                    <strong>Error Message:</strong><br>
                    <pre>{error_message}</pre>
                </div>

                <p style="margin-top: 20px;">
                    Please check the application logs for detailed information:<br>
                    <code>/logs/app_{datetime.now().strftime('%Y%m%d')}.log</code>
                </p>
            </div>
        </body>
        </html>
        """

        self._send_email(
            to=self.email_config.get('recipient'),
            subject=subject,
            html_body=body
        )

    def send_property_match_notification(self, property_data: Dict, buyer_data: Dict):
        """
        Send notification for property-buyer match

        Args:
            property_data: Property dictionary
            buyer_data: Buyer dictionary with match details
        """
        subject = f"New Property Match for {buyer_data.get('first_name')} {buyer_data.get('last_name')}"

        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; }}
                .match-card {{ background: #e8f5e9; padding: 20px; border-radius: 8px; }}
                .property-details {{ background: white; padding: 15px; margin-top: 10px; }}
            </style>
        </head>
        <body>
            <div class="match-card">
                <h2>🎯 Property Match Found!</h2>
                <p><strong>Buyer:</strong> {buyer_data.get('first_name')} {buyer_data.get('last_name')}</p>
                <p><strong>Match Score:</strong> {buyer_data.get('match_score', 0)}/100</p>

                <div class="property-details">
                    <h3>{property_data.get('street_address')}</h3>
                    <p>{property_data.get('city')}, {property_data.get('state')} {property_data.get('zip_code')}</p>

                    <p><strong>Price:</strong> ${property_data.get('list_price', 0):,}</p>
                    <p><strong>Beds/Baths:</strong> {property_data.get('bedrooms')}/{property_data.get('bathrooms')}</p>
                    <p><strong>Opportunity Score:</strong> {property_data.get('opportunity_score', 0)}/100</p>

                    <p><strong>Why this matches:</strong></p>
                    <ul>
                        {''.join([f"<li>{reason}</li>" for reason in buyer_data.get('match_reasons', [])])}
                    </ul>
                </div>
            </div>
        </body>
        </html>
        """

        self._send_email(
            to=self.email_config.get('recipient'),
            subject=subject,
            html_body=html
        )

    def send_webhook_notification(self, event_type: str, data: Dict):
        """
        Send webhook notification for integrations

        Args:
            event_type: Type of event (hot_deal, property_matched, etc.)
            data: Event data payload
        """
        if not self.webhook_config.get('enabled', False):
            return

        webhook_url = self.webhook_config.get('url')
        if not webhook_url:
            self.logger.warning("Webhook enabled but no URL configured")
            return

        payload = {
            'event': event_type,
            'timestamp': datetime.now().isoformat(),
            'data': data
        }

        try:
            response = requests.post(
                webhook_url,
                json=payload,
                headers={'Content-Type': 'application/json'},
                timeout=10
            )

            if response.status_code == 200:
                self.logger.info(f"Webhook notification sent: {event_type}")
            else:
                self.logger.warning(f"Webhook failed with status {response.status_code}")

        except Exception as e:
            self.logger.error(f"Webhook notification failed: {e}")

    def _send_email(self, to: str, subject: str, html_body: str,
                   attachment_path: Optional[str] = None):
        """
        Send HTML email via SMTP

        Args:
            to: Recipient email address
            subject: Email subject
            html_body: HTML email body
            attachment_path: Optional file to attach
        """
        try:
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = self.email_config.get('sender')
            msg['To'] = to

            # Attach HTML body
            html_part = MIMEText(html_body, 'html')
            msg.attach(html_part)

            # Attach file if provided
            if attachment_path and os.path.exists(attachment_path):
                with open(attachment_path, 'rb') as f:
                    part = MIMEBase('application', 'octet-stream')
                    part.set_payload(f.read())

                encoders.encode_base64(part)
                part.add_header(
                    'Content-Disposition',
                    f'attachment; filename={os.path.basename(attachment_path)}'
                )
                msg.attach(part)

            # Connect to SMTP server
            smtp_server = self.email_config.get('smtp_server')
            smtp_port = self.email_config.get('smtp_port', 587)
            username = self.email_config.get('username')
            password = self.email_config.get('password')

            with smtplib.SMTP(smtp_server, smtp_port) as server:
                server.starttls()
                server.login(username, password)
                server.send_message(msg)

            self.logger.info(f"Email sent to {to}: {subject}")

        except Exception as e:
            self.logger.error(f"Failed to send email: {e}", exc_info=True)

    def _send_twilio_sms(self, to: str, message: str):
        """
        Send SMS via Twilio

        Args:
            to: Phone number
            message: SMS message text
        """
        try:
            # Import Twilio client if available
            from twilio.rest import Client

            account_sid = os.getenv('TWILIO_ACCOUNT_SID')
            auth_token = os.getenv('TWILIO_AUTH_TOKEN')
            from_number = os.getenv('TWILIO_PHONE_NUMBER')

            if not all([account_sid, auth_token, from_number]):
                self.logger.warning("Twilio credentials not configured")
                return

            client = Client(account_sid, auth_token)

            message = client.messages.create(
                body=message,
                from_=from_number,
                to=to
            )

            self.logger.info(f"SMS sent to {to}: {message.sid}")

        except ImportError:
            self.logger.warning("Twilio library not installed. Install with: pip install twilio")
        except Exception as e:
            self.logger.error(f"Failed to send SMS: {e}")

    def _generate_stats_footer(self, stats: Dict) -> str:
        """Generate HTML stats footer for email"""
        return f"""
        <div style="background: #f5f5f5; padding: 20px; margin-top: 30px; border-radius: 8px;">
            <h3 style="margin-top: 0; color: #333;">📊 Workflow Statistics</h3>
            <table style="width: 100%; border-collapse: collapse;">
                <tr>
                    <td style="padding: 8px; border-bottom: 1px solid #ddd;">Properties Scraped</td>
                    <td style="padding: 8px; border-bottom: 1px solid #ddd; text-align: right;">
                        <strong>{stats.get('scraped', 0)}</strong>
                    </td>
                </tr>
                <tr>
                    <td style="padding: 8px; border-bottom: 1px solid #ddd;">Properties Analyzed</td>
                    <td style="padding: 8px; border-bottom: 1px solid #ddd; text-align: right;">
                        <strong>{stats.get('analyzed', 0)}</strong>
                    </td>
                </tr>
                <tr>
                    <td style="padding: 8px; border-bottom: 1px solid #ddd;">Unique Properties</td>
                    <td style="padding: 8px; border-bottom: 1px solid #ddd; text-align: right;">
                        <strong>{stats.get('unique', 0)}</strong>
                    </td>
                </tr>
                <tr>
                    <td style="padding: 8px; border-bottom: 1px solid #ddd;">GHL Opportunities Created</td>
                    <td style="padding: 8px; border-bottom: 1px solid #ddd; text-align: right;">
                        <strong>{stats.get('ghl', {}).get('opportunities_created', 0)}</strong>
                    </td>
                </tr>
                <tr>
                    <td style="padding: 8px; border-bottom: 1px solid #ddd;">Buyers Matched</td>
                    <td style="padding: 8px; border-bottom: 1px solid #ddd; text-align: right;">
                        <strong>{stats.get('matches', {}).get('total_matches', 0)}</strong>
                    </td>
                </tr>
                <tr>
                    <td style="padding: 8px;">Execution Time</td>
                    <td style="padding: 8px; text-align: right;">
                        <strong>{stats.get('duration_seconds', 0):.1f} seconds</strong>
                    </td>
                </tr>
            </table>

            <p style="margin-top: 20px; color: #666; font-size: 12px;">
                Generated by DealFinder Pro at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
            </p>
        </div>
        """
