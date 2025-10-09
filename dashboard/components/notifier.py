"""
Notification Manager
Handles email and SMS notifications
"""

import smtplib
import os
import json
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from typing import List, Dict
from pathlib import Path

logger = logging.getLogger(__name__)


class NotificationManager:
    """Manages email and SMS notifications"""

    def __init__(self, config_path: str = None):
        """Initialize notification manager"""
        if config_path is None:
            config_path = Path(__file__).parent.parent.parent / 'config.json'

        with open(config_path) as f:
            self.config = json.load(f)

        self.email_config = self.config.get('notifications', {}).get('email', {})
        self.sms_config = self.config.get('notifications', {}).get('sms', {})
        self.thresholds = self.config.get('notifications', {}).get('thresholds', {})

        # Get credentials from environment
        self.email_user = os.getenv('EMAIL_USERNAME', '')
        self.email_password = os.getenv('EMAIL_PASSWORD', '')
        self.twilio_account_sid = os.getenv('TWILIO_ACCOUNT_SID', '')
        self.twilio_auth_token = os.getenv('TWILIO_AUTH_TOKEN', '')
        self.twilio_phone = os.getenv('TWILIO_PHONE_NUMBER', '')

    def send_email(self, subject: str, body_html: str, to_email: str = None) -> bool:
        """Send email notification"""
        if not self.email_config.get('enabled', False):
            logger.info("Email notifications disabled")
            return False

        if not self.email_user or not self.email_password:
            logger.error("Email credentials not configured in .env")
            return False

        try:
            recipient = to_email or self.email_config.get('recipient')

            # Create message
            msg = MIMEMultipart('alternative')
            msg['From'] = self.email_user
            msg['To'] = recipient
            msg['Subject'] = subject

            # Attach HTML body
            html_part = MIMEText(body_html, 'html')
            msg.attach(html_part)

            # Send via SMTP
            with smtplib.SMTP(self.email_config['smtp_server'], self.email_config['smtp_port']) as server:
                server.starttls()
                server.login(self.email_user, self.email_password)
                server.send_message(msg)

            logger.info(f"Email sent successfully to {recipient}")
            return True

        except Exception as e:
            logger.error(f"Failed to send email: {e}")
            return False

    def send_sms(self, message: str, to_phone: str = None) -> bool:
        """Send SMS notification via Twilio"""
        if not self.sms_config.get('enabled', False):
            logger.info("SMS notifications disabled")
            return False

        if not all([self.twilio_account_sid, self.twilio_auth_token, self.twilio_phone]):
            logger.error("Twilio credentials not configured in .env")
            return False

        try:
            from twilio.rest import Client

            recipient = to_phone or self.sms_config.get('broker_phone')

            if not recipient:
                logger.error("No recipient phone number configured")
                return False

            # Check quiet hours
            if self._is_quiet_hours():
                logger.info("Skipping SMS - quiet hours active")
                return False

            client = Client(self.twilio_account_sid, self.twilio_auth_token)

            message_obj = client.messages.create(
                body=message,
                from_=self.twilio_phone,
                to=recipient
            )

            logger.info(f"SMS sent successfully: {message_obj.sid}")
            return True

        except Exception as e:
            logger.error(f"Failed to send SMS: {e}")
            return False

    def send_scan_summary(self, properties: List[Dict]) -> Dict:
        """Send summary of scan results"""
        results = {'email_sent': False, 'sms_sent': False}

        if not properties:
            logger.info("No properties to notify about")
            return results

        # Classify deals
        hot_deals = [p for p in properties if p.get('opportunity_score', 0) >= 90]
        good_deals = [p for p in properties if 75 <= p.get('opportunity_score', 0) < 90]

        # Email notification
        if self.email_config.get('send_daily_summary', True):
            email_body = self._generate_email_html(properties, hot_deals, good_deals)
            subject = f"DealFinder: {len(properties)} Properties Found"

            if hot_deals:
                subject = f"🔥 DealFinder: {len(hot_deals)} HOT DEALS + {len(properties) - len(hot_deals)} More"

            results['email_sent'] = self.send_email(subject, email_body)

        # SMS notification for hot deals
        if hot_deals and self.sms_config.get('hot_deal_only', True):
            sms_message = self._generate_sms_text(hot_deals, good_deals)
            results['sms_sent'] = self.send_sms(sms_message)

        return results

    def _generate_email_html(self, all_properties: List[Dict], hot_deals: List[Dict], good_deals: List[Dict]) -> str:
        """Generate HTML email body"""
        html = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 8px; }}
                .summary {{ background: #f4f4f4; padding: 15px; border-radius: 8px; margin: 20px 0; }}
                .deal {{ background: white; border-left: 4px solid #667eea; padding: 15px; margin: 10px 0; border-radius: 4px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
                .hot {{ border-left-color: #ff4444; }}
                .good {{ border-left-color: #ff9800; }}
                .badge {{ display: inline-block; padding: 4px 8px; border-radius: 4px; font-size: 12px; font-weight: bold; }}
                .badge-hot {{ background: #ff4444; color: white; }}
                .badge-good {{ background: #ff9800; color: white; }}
                .metric {{ display: inline-block; margin-right: 15px; }}
                .footer {{ margin-top: 30px; padding-top: 20px; border-top: 1px solid #ddd; font-size: 12px; color: #666; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>🏠 DealFinder Pro - Scan Results</h1>
                <p>{datetime.now().strftime('%B %d, %Y at %I:%M %p')}</p>
            </div>

            <div class="summary">
                <h2>📊 Summary</h2>
                <div class="metric"><strong>Total Properties:</strong> {len(all_properties)}</div>
                <div class="metric"><strong>🔥 Hot Deals:</strong> {len(hot_deals)}</div>
                <div class="metric"><strong>⭐ Good Opportunities:</strong> {len(good_deals)}</div>
            </div>

            <h2>🔥 Hot Deals (Score 90+)</h2>
        """

        # Add hot deals
        for prop in hot_deals[:5]:  # Top 5
            html += self._format_property_html(prop, 'hot')

        if len(hot_deals) > 5:
            html += f"<p><em>...and {len(hot_deals) - 5} more hot deals</em></p>"

        # Add good deals
        if good_deals:
            html += "<h2>⭐ Good Opportunities (Score 75-89)</h2>"
            for prop in good_deals[:5]:  # Top 5
                html += self._format_property_html(prop, 'good')

            if len(good_deals) > 5:
                html += f"<p><em>...and {len(good_deals) - 5} more opportunities</em></p>"

        # Footer
        html += """
            <div class="footer">
                <p>🤖 Generated by DealFinder Pro</p>
                <p>View full details in your dashboard</p>
            </div>
        </body>
        </html>
        """

        return html

    def _format_property_html(self, prop: Dict, deal_type: str = 'good') -> str:
        """Format single property for email"""
        address = prop.get('street_address', 'Unknown Address')
        city = prop.get('city', '')
        state = prop.get('state', '')
        price = prop.get('list_price', 0)
        score = prop.get('opportunity_score', 0)
        below_market = prop.get('below_market_percentage', 0)
        days = prop.get('days_on_market', 0)
        profit = prop.get('estimated_profit', 0)

        badge_class = f'badge-{deal_type}'
        deal_class = deal_type

        return f"""
        <div class="deal {deal_class}">
            <div>
                <span class="badge {badge_class}">Score: {score}/100</span>
                <h3>{address}</h3>
                <p><strong>{city}, {state}</strong></p>
            </div>
            <div>
                <div class="metric"><strong>Price:</strong> ${price:,.0f}</div>
                <div class="metric"><strong>Below Market:</strong> {below_market:.1f}%</div>
                <div class="metric"><strong>Days Listed:</strong> {days}</div>
                {f'<div class="metric"><strong>Est. Profit:</strong> ${profit:,.0f}</div>' if profit > 0 else ''}
            </div>
        </div>
        """

    def _generate_sms_text(self, hot_deals: List[Dict], good_deals: List[Dict]) -> str:
        """Generate concise SMS message"""
        total_deals = len(hot_deals) + len(good_deals)

        if not hot_deals:
            return f"DealFinder: {total_deals} new opportunities found. Check dashboard for details."

        top_deal = hot_deals[0]
        address = top_deal.get('street_address', 'Property')
        city = top_deal.get('city', '')
        price = top_deal.get('list_price', 0)
        below_market = top_deal.get('below_market_percentage', 0)
        days = top_deal.get('days_on_market', 0)

        message = f"🔥 DealFinder: {len(hot_deals)} HOT DEALS!\n\n"
        message += f"Top: ${price/1000:.0f}K {city} ({below_market:.0f}% below, {days}d)\n\n"
        message += f"View all {total_deals} deals in dashboard"

        return message

    def _is_quiet_hours(self) -> bool:
        """Check if current time is in quiet hours"""
        now = datetime.now().time()

        quiet_start = self.sms_config.get('quiet_hours_start', '22:00')
        quiet_end = self.sms_config.get('quiet_hours_end', '06:00')

        start_hour, start_min = map(int, quiet_start.split(':'))
        end_hour, end_min = map(int, quiet_end.split(':'))

        start_time = datetime.now().replace(hour=start_hour, minute=start_min).time()
        end_time = datetime.now().replace(hour=end_hour, minute=end_min).time()

        if start_time < end_time:
            # Quiet hours don't cross midnight
            return start_time <= now <= end_time
        else:
            # Quiet hours cross midnight
            return now >= start_time or now <= end_time

    def send_test_email(self) -> bool:
        """Send test email"""
        subject = "DealFinder Pro - Test Email"
        body = """
        <html>
        <body style="font-family: Arial, sans-serif;">
            <h2>🎉 Email Configured Successfully!</h2>
            <p>This is a test email from your DealFinder Pro system.</p>
            <p>If you're reading this, your email notifications are working correctly.</p>
            <hr>
            <p style="font-size: 12px; color: #666;">
                <strong>System Info:</strong><br>
                Time: {}<br>
                Recipient: {}<br>
            </p>
        </body>
        </html>
        """.format(datetime.now().strftime('%Y-%m-%d %H:%M:%S'), self.email_config.get('recipient'))

        return self.send_email(subject, body)

    def send_test_sms(self) -> bool:
        """Send test SMS"""
        message = "🏠 DealFinder Pro: This is a test message. Your SMS notifications are working!"
        return self.send_sms(message)
