"""
Opportunities Page - Enhanced Property Browser
3 view modes: Card, Table, Map with investment metrics
"""

import streamlit as st
import sys
from pathlib import Path
import pandas as pd
from datetime import datetime

# Add paths
dashboard_dir = Path(__file__).parent.parent
project_root = dashboard_dir.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(dashboard_dir))

from components.config_manager import ConfigManager

st.set_page_config(page_title="Opportunities", page_icon="📊", layout="wide")

# Custom CSS
st.markdown("""
<style>
    .deal-badge {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 12px;
        font-size: 12px;
        font-weight: bold;
        margin-right: 8px;
    }
    .badge-hot { background: #ff4444; color: white; }
    .badge-good { background: #ff9800; color: white; }
    .badge-fair { background: #4caf50; color: white; }
    .badge-pass { background: #9e9e9e; color: white; }

    .property-card {
        background: white;
        border: 1px solid #e0e0e0;
        border-radius: 8px;
        padding: 20px;
        margin: 10px 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .property-card:hover {
        box-shadow: 0 4px 8px rgba(0,0,0,0.15);
    }
    .metric-highlight {
        background: #f8f9fa;
        padding: 10px;
        border-radius: 4px;
        margin: 5px 0;
    }
</style>
""", unsafe_allow_html=True)

st.title("📊 Investment Opportunities")
st.markdown("Browse, filter, and analyze qualified properties")
st.markdown("---")

# Check for properties
if 'scraped_properties' not in st.session_state or not st.session_state['scraped_properties']:
    st.info("📭 No properties loaded yet")
    st.markdown("""
    ### Get Started:
    1. Go to **🏠 Command Center**
    2. Click **"Run Scan Now"** or wait for scheduled scan
    3. Properties will appear here automatically

    **Tip:** The system is configured to scan San Diego County and Clark County (Las Vegas)
    3 times daily at 6 AM, 10 AM, and 2 PM.
    """)

    col1, col2 = st.columns(2)
    with col1:
        if st.button("➡️ Go to Command Center", use_container_width=True):
            st.switch_page("pages/1_🏠_Command_Center.py")
    with col2:
        if st.button("⚙️ Configure Criteria", use_container_width=True):
            st.switch_page("pages/3_⚙️_Configuration.py")
    st.stop()

# Load properties
properties = st.session_state['scraped_properties']
df = pd.DataFrame(properties)

# Calculate deal quality if not present
for prop in properties:
    if 'opportunity_score' not in prop:
        prop['opportunity_score'] = 0

    score = prop['opportunity_score']
    if score >= 90:
        prop['deal_quality'] = 'HOT'
    elif score >= 75:
        prop['deal_quality'] = 'GOOD'
    elif score >= 60:
        prop['deal_quality'] = 'FAIR'
    else:
        prop['deal_quality'] = 'PASS'

# Reload df with updated properties
df = pd.DataFrame(properties)

# Summary metrics
col1, col2, col3, col4 = st.columns(4)

hot_count = len([p for p in properties if p.get('opportunity_score', 0) >= 90])
good_count = len([p for p in properties if 75 <= p.get('opportunity_score', 0) < 90])
fair_count = len([p for p in properties if 60 <= p.get('opportunity_score', 0) < 75])

with col1:
    st.metric("🔥 Hot Deals", hot_count, help="Score 90+")
with col2:
    st.metric("⭐ Good", good_count, help="Score 75-89")
with col3:
    st.metric("✅ Fair", fair_count, help="Score 60-74")
with col4:
    st.metric("Total", len(properties))

st.markdown("---")

# Filters
with st.expander("🔍 Smart Filters", expanded=True):
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        # Deal quality filter
        quality_options = st.multiselect(
            "Deal Quality",
            options=["HOT", "GOOD", "FAIR", "PASS"],
            default=["HOT", "GOOD", "FAIR", "PASS"],
            help="Filter by deal classification"
        )

    with col2:
        # Price range
        if 'list_price' in df.columns:
            prices = df['list_price'].dropna()
            if len(prices) > 0:
                min_price = int(prices.min())
                max_price = int(prices.max())

                # Default to $100K - $2M range (filters out rentals and ultra-luxury)
                default_min = max(min_price, 100000)
                default_max = min(max_price, 2000000)

                price_range = st.slider(
                    "Price Range",
                    min_value=min_price,
                    max_value=max_price,
                    value=(default_min, default_max),
                    format="$%d",
                    help="Filter by listing price (default: $100K-$2M)"
                )
            else:
                price_range = None
        else:
            price_range = None

    with col3:
        # Below market filter
        if 'below_market_percentage' in df.columns:
            below_market = df['below_market_percentage'].dropna()
            if len(below_market) > 0:
                min_below = st.slider(
                    "Min Below Market %",
                    min_value=0,
                    max_value=50,
                    value=15,
                    help="Minimum % below market value"
                )
            else:
                min_below = 0
        else:
            min_below = 0

    with col4:
        # Min opportunity score
        min_score = st.slider(
            "Min Opportunity Score",
            min_value=0,
            max_value=100,
            value=10,
            help="Minimum investment score (default: 10)"
        )

# Apply filters
filtered_df = df.copy()

# Filter by deal quality
if 'deal_quality' in filtered_df.columns:
    filtered_df = filtered_df[filtered_df['deal_quality'].isin(quality_options)]

# Filter by price
if price_range and 'list_price' in filtered_df.columns:
    filtered_df = filtered_df[
        (filtered_df['list_price'] >= price_range[0]) &
        (filtered_df['list_price'] <= price_range[1])
    ]

# Filter by below market
if min_below > 0 and 'below_market_percentage' in filtered_df.columns:
    filtered_df = filtered_df[filtered_df['below_market_percentage'] >= min_below]

# Filter by score
if 'opportunity_score' in filtered_df.columns:
    filtered_df = filtered_df[filtered_df['opportunity_score'] >= min_score]

# Sort by score (highest first)
if 'opportunity_score' in filtered_df.columns:
    filtered_df = filtered_df.sort_values('opportunity_score', ascending=False)

st.markdown(f"### Showing {len(filtered_df)} qualified properties")

# View mode selector
view_mode = st.radio(
    "View Mode",
    options=["🎴 Cards", "📋 Table", "🗺️ Map"],
    horizontal=True,
    help="Choose how to display properties"
)

st.markdown("---")

# CARD VIEW
if view_mode == "🎴 Cards":
    if len(filtered_df) == 0:
        st.info("No properties match your filters. Try adjusting the criteria.")
    else:
        for idx, row in filtered_df.iterrows():
            deal_quality = row.get('deal_quality', 'PASS')
            score = row.get('opportunity_score', 0)

            # Deal badge
            badge_class = f"badge-{deal_quality.lower()}"
            if deal_quality == 'HOT':
                badge_emoji = "🔥"
            elif deal_quality == 'GOOD':
                badge_emoji = "⭐"
            elif deal_quality == 'FAIR':
                badge_emoji = "✅"
            else:
                badge_emoji = "❌"

            with st.container():
                st.markdown(f'<span class="deal-badge {badge_class}">{badge_emoji} {deal_quality} ({score}/100)</span>', unsafe_allow_html=True)

                col1, col2, col3 = st.columns([2, 3, 1])

                with col1:
                    # Photo
                    if 'primary_photo' in row and pd.notna(row['primary_photo']):
                        st.image(row['primary_photo'], use_container_width=True)
                    else:
                        st.info("📷 No photo available")

                with col2:
                    # Property details
                    address = row.get('street_address', 'Unknown Address')
                    city = row.get('city', '')
                    state = row.get('state', '')
                    price = row.get('list_price', 0)

                    st.markdown(f"### {address}")
                    st.markdown(f"**{city}, {state}**")

                    if price:
                        st.markdown(f"**Price:** ${price:,.0f}")

                    # Specs
                    specs = []
                    if 'bedrooms' in row and pd.notna(row['bedrooms']):
                        specs.append(f"🛏️ {int(row['bedrooms'])} beds")
                    if 'bathrooms' in row and pd.notna(row['bathrooms']):
                        specs.append(f"🚿 {row['bathrooms']} baths")
                    if 'square_feet' in row and pd.notna(row['square_feet']):
                        specs.append(f"📐 {int(row['square_feet']):,} sqft")

                    if specs:
                        st.markdown(" | ".join(specs))

                    # Investment metrics
                    st.markdown("**💡 Why This Deal:**")

                    highlights = []
                    if 'below_market_percentage' in row and row['below_market_percentage'] > 0:
                        highlights.append(f"• {row['below_market_percentage']:.1f}% below market")
                    if 'days_on_market' in row and pd.notna(row['days_on_market']):
                        highlights.append(f"• Listed {int(row['days_on_market'])} days (motivated)")
                    if 'estimated_profit' in row and row['estimated_profit'] > 0:
                        highlights.append(f"• Est. profit: ${row['estimated_profit']:,.0f}")

                    for highlight in highlights:
                        st.caption(highlight)

                with col3:
                    # Actions
                    st.markdown("**Actions:**")

                    if st.button("📊 Analyze", key=f"analyze_{idx}", use_container_width=True):
                        st.session_state['selected_property'] = row.to_dict()
                        st.switch_page("pages/4_🤖_Agent_Control.py")

                    # Watchlist
                    if 'watched_properties' not in st.session_state:
                        st.session_state['watched_properties'] = []

                    is_watched = any(p.get('address') == address for p in st.session_state['watched_properties'])

                    if is_watched:
                        if st.button("⭐ Watching", key=f"unwatch_{idx}", use_container_width=True):
                            st.session_state['watched_properties'] = [
                                p for p in st.session_state['watched_properties']
                                if p.get('address') != address
                            ]
                            st.rerun()
                    else:
                        if st.button("☆ Watch", key=f"watch_{idx}", use_container_width=True):
                            st.session_state['watched_properties'].append(row.to_dict())
                            st.success("Added to watchlist!")
                            st.rerun()

                    if 'listing_url' in row and pd.notna(row['listing_url']):
                        st.link_button("🔗 View Listing", row['listing_url'], use_container_width=True)

                st.markdown("---")

# TABLE VIEW
elif view_mode == "📋 Table":
    if len(filtered_df) == 0:
        st.info("No properties match your filters.")
    else:
        # Select columns to display
        display_cols = []

        # Always show these if available
        priority_cols = ['deal_quality', 'opportunity_score', 'street_address', 'city', 'state',
                        'list_price', 'below_market_percentage', 'days_on_market',
                        'estimated_profit', 'bedrooms', 'bathrooms', 'square_feet']

        for col in priority_cols:
            if col in filtered_df.columns:
                display_cols.append(col)

        if display_cols:
            display_df = filtered_df[display_cols].copy()

            # Format columns
            if 'list_price' in display_df.columns:
                display_df['list_price'] = display_df['list_price'].apply(
                    lambda x: f"${x:,.0f}" if pd.notna(x) else "N/A"
                )

            if 'below_market_percentage' in display_df.columns:
                display_df['below_market_percentage'] = display_df['below_market_percentage'].apply(
                    lambda x: f"{x:.1f}%" if pd.notna(x) else "N/A"
                )

            if 'estimated_profit' in display_df.columns:
                display_df['estimated_profit'] = display_df['estimated_profit'].apply(
                    lambda x: f"${x:,.0f}" if pd.notna(x) and x > 0 else "N/A"
                )

            # Rename columns for display
            display_df = display_df.rename(columns={
                'deal_quality': 'Quality',
                'opportunity_score': 'Score',
                'street_address': 'Address',
                'city': 'City',
                'state': 'State',
                'list_price': 'Price',
                'below_market_percentage': 'Below Market',
                'days_on_market': 'Days',
                'estimated_profit': 'Est. Profit',
                'bedrooms': 'Beds',
                'bathrooms': 'Baths',
                'square_feet': 'Sqft'
            })

            st.dataframe(
                display_df,
                use_container_width=True,
                hide_index=True,
                height=600
            )

            # Export button
            csv = filtered_df.to_csv(index=False)
            st.download_button(
                label="📥 Download as CSV",
                data=csv,
                file_name=f"opportunities_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv",
                use_container_width=True
            )

# MAP VIEW
else:  # Map view
    st.info("🗺️ Map view requires property coordinates. This feature will display properties geographically once location data is available.")
    st.markdown("""
    **Coming soon:**
    - Interactive map with property pins
    - Color-coded by deal quality
    - Click for details
    - Cluster view when zoomed out

    For now, use Card or Table view to browse properties.
    """)

st.markdown("---")

# Quick stats
if len(filtered_df) > 0:
    with st.expander("📊 Quick Statistics", expanded=False):
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            if 'list_price' in filtered_df.columns:
                avg_price = filtered_df['list_price'].mean()
                st.metric("Avg Price", f"${avg_price:,.0f}")

        with col2:
            if 'below_market_percentage' in filtered_df.columns:
                avg_below = filtered_df['below_market_percentage'].mean()
                st.metric("Avg Below Market", f"{avg_below:.1f}%")

        with col3:
            if 'days_on_market' in filtered_df.columns:
                avg_dom = filtered_df['days_on_market'].mean()
                st.metric("Avg Days Listed", f"{avg_dom:.0f}")

        with col4:
            if 'estimated_profit' in filtered_df.columns:
                total_profit = filtered_df['estimated_profit'].sum()
                st.metric("Total Profit Potential", f"${total_profit:,.0f}")
