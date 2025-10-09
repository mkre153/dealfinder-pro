"""
Schedule & Alerts Page
Manage automated scans and notifications (Email + SMS)
"""

import streamlit as st
import sys
from pathlib import Path
import os

# Add paths
dashboard_dir = Path(__file__).parent.parent
project_root = dashboard_dir.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(dashboard_dir))

from components.config_manager import ConfigManager
from components.scheduler import get_scheduler
from components.notifier import NotificationManager

st.set_page_config(page_title="Schedule & Alerts", page_icon="⏰", layout="wide")

st.title("⏰ Schedule & Notifications")
st.markdown("Manage automated scans and alert preferences")
st.markdown("---")

# Initialize
config_mgr = ConfigManager()
config = config_mgr.load_config()
scheduler = get_scheduler()
notifier = NotificationManager()

# Tabs
tab1, tab2, tab3, tab4 = st.tabs([
    "🔄 Automated Scans",
    "📧 Email Notifications",
    "💬 SMS/Text Alerts",
    "🎚️ Alert Thresholds"
])

# TAB 1: Automated Scans
with tab1:
    st.markdown("### Automated Property Scanning")

    schedule_config = config.get('scheduling', {})
    scan_times = schedule_config.get('scan_times', [])

    # Scheduler status
    col1, col2 = st.columns(2)

    with col1:
        if scheduler.is_running:
            st.success("✅ **Scheduler Status:** Active")
        else:
            st.warning("⚠️ **Scheduler Status:** Stopped")

    with col2:
        if scheduler.is_running:
            try:
                next_scan = scheduler.get_next_run_time()
                st.info(f"⏰ **Next Scan:** {next_scan}")
            except:
                st.info("⏰ **Next Scan:** Calculating...")

    st.markdown("---")

    # Control buttons
    col1, col2, col3 = st.columns(3)

    with col1:
        if not scheduler.is_running:
            if st.button("▶️ Start Scheduler", type="primary", use_container_width=True):
                scheduler.start()
                st.success("Scheduler started!")
                st.rerun()

    with col2:
        if scheduler.is_running:
            if st.button("⏸️ Pause Scheduler", use_container_width=True):
                scheduler.pause()
                st.info("Scheduler paused")
                st.rerun()

    with col3:
        if st.button("⚡ Run Scan Now", use_container_width=True):
            with st.spinner("Running manual scan..."):
                try:
                    result = scheduler.run_manual_scan()
                    if result['status'] == 'completed':
                        st.success(f"✅ Scan complete! Found {result['properties_found']} properties")
                    else:
                        st.warning(f"⚠️ Scan completed with issues")
                except Exception as e:
                    st.error(f"Error: {e}")

    st.markdown("---")

    # Scan schedule
    st.markdown("### 📅 Scan Schedule")
    st.markdown("**Current scan times:**")

    for idx, scan_time in enumerate(scan_times):
        col1, col2, col3 = st.columns([2, 2, 1])

        with col1:
            st.markdown(f"**{scan_time.get('label', 'Scan')}**")

        with col2:
            st.markdown(f"⏰ {scan_time['time']}")

        with col3:
            enabled = scan_time.get('enabled', True)
            if enabled:
                st.success("✅ Active")
            else:
                st.warning("⚠️ Disabled")

    st.markdown("---")

    # Settings
    st.markdown("### ⚙️ Schedule Settings")

    col1, col2 = st.columns(2)

    with col1:
        skip_weekends = st.checkbox(
            "Skip weekends",
            value=schedule_config.get('skip_weekends', False),
            help="Don't run scans on Saturday/Sunday"
        )

    with col2:
        skip_holidays = st.checkbox(
            "Skip holidays",
            value=schedule_config.get('skip_holidays', False),
            help="Don't run scans on major holidays"
        )

    if st.button("💾 Save Schedule Settings", type="primary"):
        config['scheduling']['skip_weekends'] = skip_weekends
        config['scheduling']['skip_holidays'] = skip_holidays

        if config_mgr.save_config(config):
            st.success("✅ Settings saved!")
        else:
            st.error("❌ Failed to save")

# TAB 2: Email Notifications
with tab2:
    st.markdown("### 📧 Email Notifications")

    email_config = config.get('notifications', {}).get('email', {})

    # Email status
    email_enabled = email_config.get('enabled', False)

    if email_enabled:
        st.success("✅ Email notifications are **ENABLED**")
    else:
        st.warning("⚠️ Email notifications are **DISABLED**")

    st.markdown("---")

    # Email settings
    st.markdown("### ⚙️ Email Settings")

    recipient_email = st.text_input(
        "Recipient Email Address",
        value=email_config.get('recipient', 'mkre153@gmail.com'),
        help="Where to send property alerts"
    )

    st.markdown("**Send emails when:**")

    send_daily = st.checkbox(
        "📅 Daily scan summary (after each scan)",
        value=email_config.get('send_daily_summary', True),
        help="Get summary after each scheduled scan"
    )

    send_hot_deals = st.checkbox(
        "🔥 Hot deal alerts (Score 90+)",
        value=email_config.get('send_hot_deal_alerts', True),
        help="Immediate alert for exceptional properties"
    )

    send_weekly = st.checkbox(
        "📊 Weekly digest (Sundays)",
        value=email_config.get('send_weekly_digest', True),
        help="Weekly summary of all activity"
    )

    st.markdown("---")

    # Email format
    st.markdown("### 📄 Email Format")

    email_format = st.radio(
        "Choose email style:",
        options=["Summary", "Detailed", "Full Report"],
        index=1,
        help="Summary = counts only, Detailed = top 5 deals, Full = all deals attached"
    )

    st.markdown("---")

    # Test email
    col1, col2 = st.columns([2, 1])

    with col1:
        st.markdown("**Test your email setup:**")

    with col2:
        if st.button("📧 Send Test Email", use_container_width=True):
            with st.spinner("Sending test email..."):
                success = notifier.send_test_email()
                if success:
                    st.success(f"✅ Test email sent to {recipient_email}")
                else:
                    st.error("❌ Failed to send. Check your .env file for EMAIL_USERNAME and EMAIL_PASSWORD")

    st.markdown("---")

    # Save email settings
    if st.button("💾 Save Email Settings", type="primary", use_container_width=True):
        config['notifications']['email']['enabled'] = email_enabled
        config['notifications']['email']['recipient'] = recipient_email
        config['notifications']['email']['send_daily_summary'] = send_daily
        config['notifications']['email']['send_hot_deal_alerts'] = send_hot_deals
        config['notifications']['email']['send_weekly_digest'] = send_weekly

        if config_mgr.save_config(config):
            st.success("✅ Email settings saved!")
            st.balloons()
        else:
            st.error("❌ Failed to save")

    # Setup instructions
    with st.expander("📖 Email Setup Instructions"):
        st.markdown("""
        ### Gmail Setup (Required)

        1. **Enable 2-Step Verification** on your Google Account
        2. Go to: https://myaccount.google.com/security
        3. Click "2-Step Verification" → Turn it on
        4. **Generate App Password:**
           - Go to: https://myaccount.google.com/apppasswords
           - Select "Mail" and your device
           - Copy the 16-character password
        5. **Add to .env file:**
           ```
           EMAIL_USERNAME=your.email@gmail.com
           EMAIL_PASSWORD=your_16_char_app_password
           ```

        **Note:** Use the app password, NOT your regular Gmail password!
        """)

# TAB 3: SMS Notifications
with tab3:
    st.markdown("### 💬 SMS/Text Notifications")

    sms_config = config.get('notifications', {}).get('sms', {})

    # SMS status
    sms_enabled = sms_config.get('enabled', False)

    if sms_enabled:
        st.success("✅ SMS notifications are **ENABLED**")
    else:
        st.warning("⚠️ SMS notifications are **DISABLED**")

    st.markdown("---")

    # Enable/disable toggle
    sms_enabled = st.checkbox(
        "Enable SMS Notifications",
        value=sms_enabled,
        help="Turn on text message alerts"
    )

    if sms_enabled:
        st.markdown("### 📱 SMS Settings")

        phone_number = st.text_input(
            "Phone Number",
            value=sms_config.get('broker_phone', ''),
            placeholder="+1 234 567 8900",
            help="Include country code (e.g., +1 for US)"
        )

        st.markdown("**Send text messages when:**")

        hot_deal_only = st.checkbox(
            "🔥 Hot deals only (Score 90+)",
            value=sms_config.get('hot_deal_only', True),
            help="Only text for exceptional deals"
        )

        send_daily_sms = st.checkbox(
            "📅 Daily summary",
            value=sms_config.get('send_daily_summary', False),
            help="Daily text with deal count"
        )

        st.markdown("---")

        # SMS format
        st.markdown("### 📝 Text Message Format")

        sms_format = st.radio(
            "Choose format:",
            options=["Concise", "Detailed"],
            index=0 if sms_config.get('format') == 'concise' else 1,
            help="Concise = count + top deal, Detailed = top 3 deals"
        )

        # Example message
        with st.expander("📱 Preview Message Format"):
            if sms_format == "Concise":
                st.code("""🔥 DealFinder: 3 HOT DEALS!

Top: $625K San Diego (22% below, 67d)

View all in dashboard""")
            else:
                st.code("""🔥 DealFinder: 3 HOT DEALS

1. $625K SD (22% below)
2. $485K Vegas (18% below)
3. $725K SD (16% below)

Dashboard: [link]""")

        st.markdown("---")

        # Quiet hours
        st.markdown("### 🌙 Quiet Hours")
        st.markdown("Don't send text messages during these hours:")

        col1, col2 = st.columns(2)

        with col1:
            quiet_start = st.time_input(
                "Start (Don't disturb after)",
                value=None,
                help="No texts after this time"
            )

        with col2:
            quiet_end = st.time_input(
                "End (Resume texts at)",
                value=None,
                help="Resume texts at this time"
            )

        st.caption("💡 Default: 10:00 PM - 6:00 AM")

        st.markdown("---")

        # Test SMS
        col1, col2 = st.columns([2, 1])

        with col1:
            st.markdown("**Test your SMS setup:**")

        with col2:
            if st.button("💬 Send Test SMS", use_container_width=True):
                if not phone_number:
                    st.error("Please enter a phone number first")
                else:
                    with st.spinner("Sending test SMS..."):
                        success = notifier.send_test_sms()
                        if success:
                            st.success(f"✅ Test SMS sent to {phone_number}")
                        else:
                            st.error("❌ Failed to send. Check Twilio credentials in .env")

        st.markdown("---")

        # Save SMS settings
        if st.button("💾 Save SMS Settings", type="primary", use_container_width=True):
            config['notifications']['sms']['enabled'] = sms_enabled
            config['notifications']['sms']['broker_phone'] = phone_number
            config['notifications']['sms']['hot_deal_only'] = hot_deal_only
            config['notifications']['sms']['send_daily_summary'] = send_daily_sms
            config['notifications']['sms']['format'] = sms_format.lower()

            if quiet_start and quiet_end:
                config['notifications']['sms']['quiet_hours_start'] = quiet_start.strftime("%H:%M")
                config['notifications']['sms']['quiet_hours_end'] = quiet_end.strftime("%H:%M")

            if config_mgr.save_config(config):
                st.success("✅ SMS settings saved!")
                st.balloons()
            else:
                st.error("❌ Failed to save")

    # Twilio setup instructions
    with st.expander("📖 Twilio Setup Instructions (Optional)"):
        st.markdown("""
        ### SMS Setup with Twilio

        1. **Sign up for Twilio:** https://www.twilio.com/try-twilio
           - Get $15 free credit (enough for ~2000 texts!)

        2. **Get your credentials:**
           - Account SID
           - Auth Token
           - Phone Number (from Twilio)

        3. **Add to .env file:**
           ```
           TWILIO_ACCOUNT_SID=your_account_sid
           TWILIO_AUTH_TOKEN=your_auth_token
           TWILIO_PHONE_NUMBER=+1234567890
           ```

        4. **Cost:** ~$0.0075 per text message

        **Note:** If you don't configure Twilio, email notifications will still work!
        """)

# TAB 4: Alert Thresholds
with tab4:
    st.markdown("### 🎚️ Notification Thresholds")
    st.markdown("Fine-tune when you get notified")

    thresholds = config.get('notifications', {}).get('thresholds', {})

    st.markdown("---")

    # Score thresholds
    st.markdown("#### 📊 Score Thresholds")

    col1, col2 = st.columns(2)

    with col1:
        min_score_email = st.slider(
            "Minimum score for email",
            min_value=0,
            max_value=100,
            value=thresholds.get('min_score_for_email', 75),
            step=5,
            format="%d",
            help="Only email about properties with this score or higher"
        )

    with col2:
        min_score_sms = st.slider(
            "Minimum score for SMS",
            min_value=0,
            max_value=100,
            value=thresholds.get('min_score_for_sms', 90),
            step=5,
            format="%d",
            help="Only text about properties with this score or higher"
        )

    st.markdown("---")

    # Deal criteria for alerts
    st.markdown("#### 💎 Deal Quality Thresholds")

    min_below_market = st.slider(
        "Alert when below market by >=",
        min_value=0,
        max_value=50,
        value=thresholds.get('min_below_market_for_alert', 20),
        step=1,
        format="%d%%",
        help="Extra alert for extreme discounts"
    )

    min_deals = st.number_input(
        "Minimum deals for notification",
        min_value=1,
        max_value=20,
        value=thresholds.get('min_deals_for_notification', 1),
        step=1,
        help="Don't notify unless at least this many deals found"
    )

    st.markdown("---")

    # Save thresholds
    if st.button("💾 Save Alert Thresholds", type="primary", use_container_width=True):
        if 'thresholds' not in config['notifications']:
            config['notifications']['thresholds'] = {}

        config['notifications']['thresholds']['min_score_for_email'] = min_score_email
        config['notifications']['thresholds']['min_score_for_sms'] = min_score_sms
        config['notifications']['thresholds']['min_below_market_for_alert'] = min_below_market
        config['notifications']['thresholds']['min_deals_for_notification'] = min_deals

        if config_mgr.save_config(config):
            st.success("✅ Thresholds saved!")
        else:
            st.error("❌ Failed to save")

st.markdown("---")

# Quick navigation
st.markdown("### ⚡ Quick Actions")

col1, col2, col3 = st.columns(3)

with col1:
    if st.button("🏠 Command Center", use_container_width=True):
        st.switch_page("pages/1_🏠_Command_Center.py")

with col2:
    if st.button("📊 View Opportunities", use_container_width=True):
        st.switch_page("pages/2_📊_Opportunities.py")

with col3:
    if st.button("⚙️ Configuration", use_container_width=True):
        st.switch_page("pages/3_⚙️_Configuration.py")
