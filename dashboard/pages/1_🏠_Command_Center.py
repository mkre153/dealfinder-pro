"""
Command Center - Home Dashboard
Main hub with system status, quick actions, and activity timeline
"""

import streamlit as st
import sys
from pathlib import Path
from datetime import datetime, timedelta
import json

# Add paths
dashboard_dir = Path(__file__).parent.parent
project_root = dashboard_dir.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(dashboard_dir))

from components.config_manager import ConfigManager
from components.scheduler import get_scheduler

st.set_page_config(page_title="Command Center", page_icon="🏠", layout="wide")

# Custom CSS
st.markdown("""
<style>
    .big-metric {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 20px;
        border-radius: 10px;
        text-align: center;
        color: white;
    }
    .big-metric h1 {
        margin: 0;
        font-size: 48px;
    }
    .big-metric p {
        margin: 5px 0 0 0;
        font-size: 14px;
        opacity: 0.9;
    }
    .status-indicator {
        display: inline-block;
        width: 12px;
        height: 12px;
        border-radius: 50%;
        margin-right: 8px;
    }
    .status-active { background-color: #00ff00; }
    .status-warning { background-color: #ffa500; }
    .status-error { background-color: #ff4444; }
    .quick-action-btn {
        padding: 15px;
        text-align: center;
        border-radius: 8px;
        background: #f8f9fa;
        cursor: pointer;
        transition: all 0.3s;
    }
    .quick-action-btn:hover {
        background: #e9ecef;
        transform: translateY(-2px);
    }
</style>
""", unsafe_allow_html=True)

# Header
st.title("🏠 DealFinder Pro - Command Center")
st.markdown("**Investment Property Scanner** | San Diego County & Clark County, Nevada")
st.markdown("---")

# Initialize components
config_mgr = ConfigManager()
config = config_mgr.load_config()
scheduler = get_scheduler()

# System Status Banner
st.markdown("### 📊 System Status")

col1, col2, col3, col4 = st.columns(4)

with col1:
    # Scheduler status
    if scheduler.is_running:
        st.markdown('<span class="status-indicator status-active"></span>**Scheduler:** Active', unsafe_allow_html=True)
    else:
        st.markdown('<span class="status-indicator status-warning"></span>**Scheduler:** Stopped', unsafe_allow_html=True)

with col2:
    # Email status
    email_enabled = config.get('notifications', {}).get('email', {}).get('enabled', False)
    if email_enabled:
        st.markdown('<span class="status-indicator status-active"></span>**Email:** Enabled', unsafe_allow_html=True)
    else:
        st.markdown('<span class="status-indicator status-warning"></span>**Email:** Disabled', unsafe_allow_html=True)

with col3:
    # SMS status
    sms_enabled = config.get('notifications', {}).get('sms', {}).get('enabled', False)
    if sms_enabled:
        st.markdown('<span class="status-indicator status-active"></span>**SMS:** Enabled', unsafe_allow_html=True)
    else:
        st.markdown('<span class="status-indicator status-warning"></span>**SMS:** Disabled', unsafe_allow_html=True)

with col4:
    # Next scan
    if scheduler.is_running:
        try:
            next_run = scheduler.get_next_run_time()
            st.markdown(f"**Next Scan:** {next_run}")
        except:
            st.markdown("**Next Scan:** N/A")
    else:
        st.markdown("**Next Scan:** Scheduler stopped")

st.markdown("---")

# Key Metrics
st.markdown("### 📈 Key Metrics")

col1, col2, col3 = st.columns(3)

# Get counts from session state
hot_deals_count = 0
new_today_count = 0
watching_count = 0

if 'scraped_properties' in st.session_state and st.session_state['scraped_properties']:
    properties = st.session_state['scraped_properties']

    # Count hot deals (score >= 90)
    hot_deals_count = len([p for p in properties if p.get('opportunity_score', 0) >= 90])

    # Count new today
    today = datetime.now().date()
    new_today_count = len([p for p in properties
                           if 'scraped_date' in p and
                           datetime.fromisoformat(p['scraped_date']).date() == today])

    # Count watched
    if 'watched_properties' in st.session_state:
        watching_count = len(st.session_state['watched_properties'])

with col1:
    st.markdown(f"""
    <div class="big-metric" style="background: linear-gradient(135deg, #ff6b6b 0%, #ee5a6f 100%);">
        <h1>🔥 {hot_deals_count}</h1>
        <p>Hot Deals</p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="big-metric" style="background: linear-gradient(135deg, #4ecdc4 0%, #44a08d 100%);">
        <h1>⭐ {new_today_count}</h1>
        <p>New Today</p>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class="big-metric" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);">
        <h1>📊 {watching_count}</h1>
        <p>Watching</p>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# Quick Actions
st.markdown("### ⚡ Quick Actions")

col1, col2, col3, col4 = st.columns(4)

with col1:
    if st.button("🔍 View Opportunities", use_container_width=True, type="primary"):
        st.switch_page("pages/2_📊_Opportunities.py")

with col2:
    if st.button("⚡ Run Scan Now", use_container_width=True):
        with st.spinner("Running scan..."):
            try:
                result = scheduler.run_manual_scan()
                if result['status'] in ['completed', 'completed_with_errors']:
                    st.success(f"✅ Scan complete! Found {result['properties_found']} properties")
                else:
                    st.error(f"❌ Scan failed: {result.get('errors', ['Unknown error'])}")
            except Exception as e:
                st.error(f"Error running scan: {e}")

with col3:
    if st.button("⚙️ Configure Criteria", use_container_width=True):
        st.switch_page("pages/3_⚙️_Configuration.py")

with col4:
    if st.button("⏰ Manage Schedule", use_container_width=True):
        st.switch_page("pages/4_⏰_Schedule_Alerts.py")

st.markdown("---")

# Recent Activity
st.markdown("### 📋 Recent Activity")

# Get scan history
scan_history = scheduler.get_scan_history(limit=10)

if scan_history:
    for scan in reversed(scan_history):  # Most recent first
        timestamp = datetime.fromisoformat(scan['timestamp'])
        time_str = timestamp.strftime("%I:%M %p")
        date_str = timestamp.strftime("%b %d")

        status_emoji = "✅" if scan['status'] == 'completed' else "⚠️" if scan['status'] == 'completed_with_errors' else "❌"

        with st.container():
            col1, col2 = st.columns([1, 4])
            with col1:
                st.markdown(f"**{time_str}**")
                st.caption(date_str)
            with col2:
                if scan['status'] == 'completed':
                    st.success(f"{status_emoji} Scan completed: {scan['properties_found']} properties found")
                elif scan['status'] == 'completed_with_errors':
                    st.warning(f"{status_emoji} Scan completed with errors: {scan['properties_found']} properties found")
                else:
                    st.error(f"{status_emoji} Scan failed: {', '.join(scan.get('errors', ['Unknown error']))}")
else:
    st.info("No recent activity. Run a scan to get started!")

st.markdown("---")

# Configuration Summary
with st.expander("📋 Current Configuration Summary", expanded=False):
    st.markdown("#### Search Criteria")

    search_criteria = config.get('search_criteria', {})
    undervalued_criteria = config.get('undervalued_criteria', {})

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**Target Areas:**")
        county_groups = search_criteria.get('county_groups', {})
        for county_key, county_data in county_groups.items():
            if county_data.get('enabled', False):
                st.markdown(f"✅ {county_data['name']}")
                st.caption(f"   {len(county_data['zips'])} ZIP codes")

        st.markdown("**Property Types:**")
        prop_types = search_criteria.get('property_types', [])
        for ptype in prop_types:
            st.markdown(f"• {ptype.replace('_', ' ').title()}")

    with col2:
        price_range = search_criteria.get('price_range', {})
        st.markdown(f"**Price Range:** ${price_range.get('min', 0):,} - ${price_range.get('max', 0):,}")

        st.markdown(f"**Below Market:** {undervalued_criteria.get('price_per_sqft_below_market_pct', 0)}%+")

        st.markdown(f"**Days on Market:** {undervalued_criteria.get('days_on_market_minimum', 0)}+ days")

        st.markdown(f"**Min Opportunity Score:** {undervalued_criteria.get('min_opportunity_score', 75)}")

st.markdown("---")

# System Info
st.markdown("### ℹ️ System Information")

col1, col2, col3 = st.columns(3)

with col1:
    total_zips = len(search_criteria.get('target_locations', []))
    st.metric("Total ZIP Codes", total_zips)

with col2:
    if 'scraped_properties' in st.session_state:
        total_props = len(st.session_state['scraped_properties'])
    else:
        total_props = 0
    st.metric("Properties in Database", total_props)

with col3:
    schedule_config = config.get('scheduling', {})
    scan_times = schedule_config.get('scan_times', [])
    active_scans = len([s for s in scan_times if s.get('enabled', True)])
    st.metric("Daily Scans", active_scans)

# Footer
st.markdown("---")
st.markdown("**DealFinder Pro** | Powered by AI | Last updated: " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
