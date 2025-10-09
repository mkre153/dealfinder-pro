"""
Configuration Page - Enhanced with Sliders
Manage search criteria, counties, and deal filters
"""

import streamlit as st
import sys
from pathlib import Path

# Add paths
dashboard_dir = Path(__file__).parent.parent
project_root = dashboard_dir.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(dashboard_dir))

from components.config_manager import ConfigManager

st.set_page_config(page_title="Configuration", page_icon="⚙️", layout="wide")

st.title("⚙️ Investment Criteria Configuration")
st.markdown("Configure your search areas, deal criteria, and filters")
st.markdown("---")

# Initialize
config_mgr = ConfigManager()
config = config_mgr.load_config()
search_criteria = config.get('search_criteria', {})
undervalued_criteria = config.get('undervalued_criteria', {})

# Tabs
tab1, tab2, tab3 = st.tabs(["🗺️ Target Markets", "💰 Deal Criteria", "🔍 Advanced Filters"])

# TAB 1: Target Markets
with tab1:
    st.markdown("### Target Markets")
    st.markdown("Enable or disable entire counties with one click")

    county_groups = search_criteria.get('county_groups', {})

    col1, col2 = st.columns(2)

    # San Diego County
    with col1:
        st.markdown("#### San Diego County, CA")

        sd_data = county_groups.get('san_diego', {})
        sd_enabled = st.checkbox(
            "Enable San Diego County",
            value=sd_data.get('enabled', True),
            key="sd_enabled",
            help="Search all San Diego County ZIP codes"
        )

        if sd_enabled:
            sd_zips = sd_data.get('zips', [])
            st.success(f"✅ {len(sd_zips)} ZIP codes active")
            with st.expander("View ZIP Codes"):
                # Display in grid
                cols = st.columns(4)
                for idx, zip_code in enumerate(sd_zips):
                    with cols[idx % 4]:
                        st.caption(zip_code)
        else:
            st.info("County disabled")

    # Clark County
    with col2:
        st.markdown("#### Clark County, NV (Las Vegas)")

        clark_data = county_groups.get('clark', {})
        clark_enabled = st.checkbox(
            "Enable Clark County",
            value=clark_data.get('enabled', True),
            key="clark_enabled",
            help="Search all Clark County/Las Vegas ZIP codes"
        )

        if clark_enabled:
            clark_zips = clark_data.get('zips', [])
            st.success(f"✅ {len(clark_zips)} ZIP codes active")
            with st.expander("View ZIP Codes"):
                cols = st.columns(4)
                for idx, zip_code in enumerate(clark_zips):
                    with cols[idx % 4]:
                        st.caption(zip_code)
        else:
            st.info("County disabled")

    st.markdown("---")

    # Save county settings
    if st.button("💾 Save Market Selection", type="primary"):
        if 'county_groups' not in config['search_criteria']:
            config['search_criteria']['county_groups'] = {}

        config['search_criteria']['county_groups']['san_diego']['enabled'] = sd_enabled
        config['search_criteria']['county_groups']['clark']['enabled'] = clark_enabled

        # Update target_locations list
        active_zips = []
        if sd_enabled:
            active_zips.extend(sd_data.get('zips', []))
        if clark_enabled:
            active_zips.extend(clark_data.get('zips', []))

        config['search_criteria']['target_locations'] = active_zips

        if config_mgr.save_config(config):
            st.success(f"✅ Saved! Now scanning {len(active_zips)} ZIP codes")
            st.balloons()
        else:
            st.error("Failed to save configuration")

# TAB 2: Deal Criteria
with tab2:
    st.markdown("### Investment Deal Criteria")
    st.markdown("Set your filters - only properties meeting ALL criteria will be shown")

    # Price Range
    st.markdown("#### 💰 Price Range")

    price_range = search_criteria.get('price_range', {'min': 500000, 'max': 1500000})

    col1, col2 = st.columns(2)

    with col1:
        min_price = st.number_input(
            "Minimum Price ($)",
            min_value=100000,
            max_value=10000000,
            value=price_range.get('min', 500000),
            step=50000,
            format="%d",
            help="Lowest price you're willing to consider"
        )

    with col2:
        max_price = st.number_input(
            "Maximum Price ($)",
            min_value=100000,
            max_value=10000000,
            value=price_range.get('max', 1500000),
            step=50000,
            format="%d",
            help="Highest price you're willing to pay"
        )

    st.caption(f"**Active Range:** ${min_price:,} - ${max_price:,}")

    st.markdown("---")

    # Below Market Threshold
    st.markdown("#### 📉 Below Market Value Threshold")

    below_market_pct = st.slider(
        "Minimum % Below Market",
        min_value=0,
        max_value=50,
        value=undervalued_criteria.get('price_per_sqft_below_market_pct', 15),
        step=1,
        format="%d%%",
        help="Only show properties priced this much below comparable properties"
    )

    st.caption(f"🎯 Show properties priced **{below_market_pct}%+ below market average**")

    st.markdown("---")

    # Days on Market
    st.markdown("#### ⏱️ Days on Market (Seller Motivation)")

    days_on_market = st.slider(
        "Minimum Days Listed",
        min_value=0,
        max_value=180,
        value=undervalued_criteria.get('days_on_market_minimum', 30),
        step=5,
        format="%d days",
        help="Properties listed longer = more motivated sellers"
    )

    st.caption(f"🎯 Show properties listed for **{days_on_market}+ days**")

    st.markdown("---")

    # Property Requirements
    st.markdown("#### 🏠 Property Requirements")

    col1, col2, col3 = st.columns(3)

    with col1:
        min_beds = st.number_input(
            "Min Bedrooms",
            min_value=0,
            max_value=10,
            value=search_criteria.get('min_bedrooms', 2),
            step=1
        )

    with col2:
        min_baths = st.number_input(
            "Min Bathrooms",
            min_value=0,
            max_value=10,
            value=search_criteria.get('min_bathrooms', 2),
            step=1
        )

    with col3:
        days_back = st.selectbox(
            "Search Last X Days",
            options=[7, 14, 30, 60, 90],
            index=2,
            format_func=lambda x: f"{x} days",
            help="How far back to search for listings"
        )

    st.markdown("---")

    # Property Types
    st.markdown("#### 🏘️ Property Types")

    current_types = search_criteria.get('property_types', [])

    property_types = st.multiselect(
        "Include these property types:",
        options=["single_family", "multi_family", "condo", "townhouse", "land"],
        default=current_types if current_types else ["single_family", "multi_family", "condo", "townhouse"],
        format_func=lambda x: x.replace('_', ' ').title(),
        help="Select all property types you want to consider"
    )

    st.markdown("---")

    # Opportunity Score Threshold
    st.markdown("#### 📊 Minimum Opportunity Score")

    min_score = st.slider(
        "Only show properties with score >=",
        min_value=0,
        max_value=100,
        value=undervalued_criteria.get('min_opportunity_score', 75),
        step=5,
        format="%d",
        help="Our AI calculates a score (0-100) based on all factors. Higher = better deal."
    )

    # Score legend
    col1, col2, col3 = st.columns(3)
    with col1:
        st.caption("🔥 **90-100:** Hot Deal")
    with col2:
        st.caption("⭐ **75-89:** Good Opportunity")
    with col3:
        st.caption("✅ **60-74:** Fair Deal")

    st.markdown("---")

    # Save button
    if st.button("💾 Save Deal Criteria", type="primary", use_container_width=True):
        try:
            # Update config
            config['search_criteria']['price_range'] = {'min': min_price, 'max': max_price}
            config['search_criteria']['min_bedrooms'] = min_beds
            config['search_criteria']['min_bathrooms'] = min_baths
            config['search_criteria']['days_back'] = days_back
            config['search_criteria']['property_types'] = property_types

            config['undervalued_criteria']['price_per_sqft_below_market_pct'] = below_market_pct
            config['undervalued_criteria']['days_on_market_minimum'] = days_on_market
            config['undervalued_criteria']['min_opportunity_score'] = min_score

            if config_mgr.save_config(config):
                st.success("✅ Configuration saved successfully!")
                st.balloons()
            else:
                st.error("❌ Failed to save configuration")

        except Exception as e:
            st.error(f"Error: {e}")

# TAB 3: Advanced Filters
with tab3:
    st.markdown("### Advanced Investment Filters")

    # Financial thresholds
    st.markdown("#### 💵 Financial Return Thresholds")

    col1, col2 = st.columns(2)

    with col1:
        min_cap_rate = st.number_input(
            "Minimum Cap Rate (%)",
            min_value=0.0,
            max_value=20.0,
            value=undervalued_criteria.get('min_cap_rate', 6.0),
            step=0.5,
            format="%.1f",
            help="For rental investments"
        )

    with col2:
        min_coc = st.number_input(
            "Minimum Cash-on-Cash Return (%)",
            min_value=0.0,
            max_value=30.0,
            value=undervalued_criteria.get('min_cash_on_cash_return', 8.0),
            step=0.5,
            format="%.1f",
            help="Annual cash return on investment"
        )

    st.markdown("---")

    # Distressed signals
    st.markdown("#### 🚨 Distressed/Motivated Seller Keywords")
    st.markdown("Properties with these keywords in the description are flagged as motivated sellers")

    default_keywords = undervalued_criteria.get('distressed_keywords', [
        "motivated seller", "as-is", "fixer", "estate sale", "must sell"
    ])

    distressed_keywords = st.multiselect(
        "Flag properties containing:",
        options=[
            "motivated seller", "motivated", "as-is", "fixer", "fixer upper",
            "needs work", "estate sale", "must sell", "bring offers",
            "bring all offers", "tlc", "handyman special", "cash only",
            "investor opportunity", "investor special", "price reduced"
        ],
        default=default_keywords,
        help="System will highlight properties with these terms"
    )

    # Add custom keyword
    custom_keyword = st.text_input(
        "Add custom keyword",
        placeholder="e.g., 'short sale', 'foreclosure'",
        help="Enter your own distressed signal keywords"
    )

    if custom_keyword and st.button("➕ Add Custom Keyword"):
        if custom_keyword not in distressed_keywords:
            distressed_keywords.append(custom_keyword)
            st.success(f"Added: {custom_keyword}")

    st.markdown("---")

    # Save advanced settings
    if st.button("💾 Save Advanced Filters", type="primary", use_container_width=True):
        config['undervalued_criteria']['min_cap_rate'] = min_cap_rate
        config['undervalued_criteria']['min_cash_on_cash_return'] = min_coc
        config['undervalued_criteria']['distressed_keywords'] = distressed_keywords

        if config_mgr.save_config(config):
            st.success("✅ Advanced filters saved!")
        else:
            st.error("❌ Failed to save")

st.markdown("---")

# Current Configuration Preview
with st.expander("📋 Current Configuration Preview", expanded=False):
    st.json(config)

# Quick Actions
st.markdown("### ⚡ Quick Actions")

col1, col2, col3 = st.columns(3)

with col1:
    if st.button("🔄 Reset to Defaults", use_container_width=True):
        if st.session_state.get('confirm_reset'):
            # Reset logic here
            st.warning("Reset functionality - implement if needed")
            st.session_state['confirm_reset'] = False
        else:
            st.session_state['confirm_reset'] = True
            st.warning("Click again to confirm reset")

with col2:
    if st.button("📊 View Opportunities", use_container_width=True):
        st.switch_page("pages/2_📊_Opportunities.py")

with col3:
    if st.button("🏠 Command Center", use_container_width=True):
        st.switch_page("pages/1_🏠_Command_Center.py")
