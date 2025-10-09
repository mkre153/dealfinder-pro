#!/usr/bin/env python3
"""
DealFinder Pro - Web Dashboard
Main entry point for the Streamlit dashboard
"""

import streamlit as st
import sys
import os
from pathlib import Path

# Add parent directory to path
parent_dir = str(Path(__file__).parent.parent)
sys.path.insert(0, parent_dir)

# Page configuration
st.set_page_config(
    page_title="DealFinder Pro Dashboard",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        color: #1f77b4;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #666;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1.5rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
    .success-box {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        border-radius: 0.25rem;
        padding: 1rem;
        color: #155724;
    }
    .warning-box {
        background-color: #fff3cd;
        border: 1px solid #ffeaa7;
        border-radius: 0.25rem;
        padding: 1rem;
        color: #856404;
    }
</style>
""", unsafe_allow_html=True)

# Main page
def main():
    # Header
    st.markdown('<div class="main-header">🏠 DealFinder Pro</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">AI-Powered Real Estate Investment Platform</div>', unsafe_allow_html=True)

    st.markdown("---")

    # Welcome message
    col1, col2 = st.columns([2, 1])

    with col1:
        st.markdown("### 👋 Welcome to Your Dashboard")
        st.markdown("""
        This dashboard allows you to:
        - **Configure** search areas and deal criteria
        - **Schedule** automated scans 3x daily
        - **Browse** qualified investment opportunities
        - **Import** external property data
        - **Analyze** market trends and insights
        """)

        st.markdown("### 🚀 Quick Start")
        st.markdown("""
        1. Go to **🏠 Command Center** to run scans
        2. Visit **⚙️ Configuration** to set your criteria
        3. Check **📊 Opportunities** to browse deals
        4. Use **⏰ Schedule & Alerts** for automation
        5. Review **📈 Analytics** for market insights
        """)

    with col2:
        st.markdown("### 📊 System Status")

        # Check if config file exists
        config_path = os.path.join(parent_dir, 'config.json')
        if os.path.exists(config_path):
            st.success("✅ Configuration loaded")
        else:
            st.error("❌ Config file missing")

        # Check if .env exists
        env_path = os.path.join(parent_dir, '.env')
        if os.path.exists(env_path):
            st.success("✅ Environment configured")
        else:
            st.warning("⚠️ .env file missing")

        # Check GHL connection
        try:
            from dotenv import load_dotenv
            load_dotenv(env_path)

            ghl_api_key = os.getenv('GHL_API_KEY')
            ghl_location_id = os.getenv('GHL_LOCATION_ID')

            if ghl_api_key and ghl_location_id:
                st.success("✅ GHL connected")
            else:
                st.warning("⚠️ GHL not configured")
        except:
            st.warning("⚠️ GHL not configured")

        # Check AI
        try:
            anthropic_key = os.getenv('ANTHROPIC_API_KEY')
            if anthropic_key:
                st.success("✅ AI agent ready")
            else:
                st.warning("⚠️ AI not configured")
        except:
            st.warning("⚠️ AI not configured")

    st.markdown("---")

    # Feature cards
    st.markdown("### 🎯 Dashboard Features")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("#### 🏠 Command Center")
        st.markdown("""
        - Run scans now
        - View scan status
        - System metrics
        - Quick actions
        """)

        st.markdown("#### 📊 Opportunities")
        st.markdown("""
        - 3 view modes
        - Smart filters
        - Deal quality badges
        - Watchlist feature
        """)

    with col2:
        st.markdown("#### ⚙️ Configuration")
        st.markdown("""
        - County toggles
        - Price ranges
        - Deal thresholds
        - Property types
        """)

        st.markdown("#### ⏰ Schedule & Alerts")
        st.markdown("""
        - Automated scans
        - Email notifications
        - SMS text alerts
        - Alert thresholds
        """)

    with col3:
        st.markdown("#### 📥 Data Import")
        st.markdown("""
        - CSV/Excel upload
        - MLS bulk import
        - Template downloads
        - Import history
        """)

        st.markdown("#### 📈 Analytics")
        st.markdown("""
        - Market insights
        - Interactive charts
        - County comparison
        - Export reports
        """)

    st.markdown("---")

    # Quick actions
    st.markdown("### ⚡ Quick Actions")

    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        if st.button("🏠 Command Center", use_container_width=True):
            st.switch_page("pages/1_🏠_Command_Center.py")

    with col2:
        if st.button("📊 Opportunities", use_container_width=True):
            st.switch_page("pages/2_📊_Opportunities.py")

    with col3:
        if st.button("⚙️ Configuration", use_container_width=True):
            st.switch_page("pages/3_⚙️_Configuration.py")

    with col4:
        if st.button("⏰ Schedule & Alerts", use_container_width=True):
            st.switch_page("pages/4_⏰_Schedule_Alerts.py")

    with col5:
        if st.button("📈 Analytics", use_container_width=True):
            st.switch_page("pages/6_📈_Analytics.py")

    st.markdown("---")

    # Footer
    st.markdown("""
    <div style='text-align: center; color: #666; padding: 2rem 0;'>
        <p>DealFinder Pro Dashboard v1.0 | Built with Streamlit</p>
        <p>AI-Powered Real Estate Investment Platform</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
