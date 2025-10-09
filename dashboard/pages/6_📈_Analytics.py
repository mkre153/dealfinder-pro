"""
Analytics & Market Insights Page
Interactive charts and market trends analysis
"""

import streamlit as st
import sys
from pathlib import Path
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

# Add paths
dashboard_dir = Path(__file__).parent.parent
project_root = dashboard_dir.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(dashboard_dir))

from components.config_manager import ConfigManager

st.set_page_config(page_title="Analytics", page_icon="📈", layout="wide")

st.title("📈 Market Analytics & Insights")
st.markdown("Data-driven insights from your property scans")
st.markdown("---")

# Check for properties
if 'scraped_properties' not in st.session_state or not st.session_state['scraped_properties']:
    st.info("📊 No data available for analysis yet")
    st.markdown("""
    ### Get Started:
    1. Run property scans from **🏠 Command Center**
    2. Analytics will appear here automatically
    3. All charts update in real-time as new properties are found
    """)

    if st.button("➡️ Go to Command Center", use_container_width=True):
        st.switch_page("pages/1_🏠_Command_Center.py")
    st.stop()

# Load properties
properties = st.session_state['scraped_properties']
df = pd.DataFrame(properties)

# Ensure deal quality is set
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

# Reload df
df = pd.DataFrame(properties)

# Date range filter
st.markdown("### 📅 Date Range")
col1, col2 = st.columns([3, 1])

with col1:
    date_options = ["Last 7 Days", "Last 30 Days", "Last 90 Days", "All Time"]
    date_range = st.selectbox(
        "Show data from:",
        options=date_options,
        index=1,
        help="Filter analytics by date range"
    )

# Top-level metrics
st.markdown("---")
st.markdown("### 📊 Key Metrics")

col1, col2, col3, col4 = st.columns(4)

total_properties = len(df)
hot_deals = len([p for p in properties if p.get('opportunity_score', 0) >= 90])
good_deals = len([p for p in properties if 75 <= p.get('opportunity_score', 0) < 90])

with col1:
    st.metric("Total Properties", f"{total_properties:,}")

with col2:
    if 'list_price' in df.columns:
        avg_price = df['list_price'].mean()
        st.metric("Avg List Price", f"${avg_price:,.0f}")
    else:
        st.metric("Avg List Price", "N/A")

with col3:
    if 'below_market_percentage' in df.columns:
        below_market_props = df[df['below_market_percentage'] > 0]
        if len(below_market_props) > 0:
            avg_below = below_market_props['below_market_percentage'].mean()
            st.metric("Avg Below Market", f"{avg_below:.1f}%", delta=f"{len(below_market_props)} deals")
        else:
            st.metric("Avg Below Market", "N/A")
    else:
        st.metric("Avg Below Market", "N/A")

with col4:
    if 'estimated_profit' in df.columns:
        total_profit = df['estimated_profit'].sum()
        st.metric("Total Profit Potential", f"${total_profit:,.0f}")
    else:
        st.metric("Total Profit Potential", "N/A")

st.markdown("---")

# Charts section
col1, col2 = st.columns(2)

# CHART 1: Deal Quality Distribution (Pie)
with col1:
    st.markdown("### 🎯 Deal Quality Distribution")

    if 'deal_quality' in df.columns:
        quality_counts = df['deal_quality'].value_counts()

        # Define colors
        color_map = {
            'HOT': '#ff4444',
            'GOOD': '#ff9800',
            'FAIR': '#4caf50',
            'PASS': '#9e9e9e'
        }

        colors = [color_map.get(q, '#cccccc') for q in quality_counts.index]

        fig_quality = go.Figure(data=[go.Pie(
            labels=quality_counts.index,
            values=quality_counts.values,
            marker=dict(colors=colors),
            hole=0.4,
            textinfo='label+percent+value',
            textposition='outside'
        )])

        fig_quality.update_layout(
            height=350,
            margin=dict(l=20, r=20, t=20, b=20),
            showlegend=True
        )

        st.plotly_chart(fig_quality, use_container_width=True)
    else:
        st.info("No deal quality data available")

# CHART 2: Price Distribution (Histogram)
with col2:
    st.markdown("### 💰 Price Distribution")

    if 'list_price' in df.columns:
        price_data = df[df['list_price'] > 0]['list_price']

        fig_price = px.histogram(
            price_data,
            nbins=20,
            labels={'value': 'List Price', 'count': 'Properties'},
            color_discrete_sequence=['#1f77b4']
        )

        fig_price.update_layout(
            height=350,
            margin=dict(l=20, r=20, t=20, b=20),
            showlegend=False,
            xaxis_title="Price Range",
            yaxis_title="Number of Properties"
        )

        fig_price.update_traces(marker_line_color='white', marker_line_width=1)

        st.plotly_chart(fig_price, use_container_width=True)
    else:
        st.info("No price data available")

st.markdown("---")

# CHART 3: Top ZIP Codes (Bar)
col1, col2 = st.columns(2)

with col1:
    st.markdown("### 🏘️ Top Performing ZIP Codes")

    if 'zip_code' in df.columns and 'opportunity_score' in df.columns:
        # Average score by ZIP
        zip_scores = df.groupby('zip_code')['opportunity_score'].agg(['mean', 'count']).reset_index()
        zip_scores = zip_scores[zip_scores['count'] >= 2]  # At least 2 properties
        zip_scores = zip_scores.sort_values('mean', ascending=False).head(10)

        fig_zips = px.bar(
            zip_scores,
            x='zip_code',
            y='mean',
            text='count',
            labels={'mean': 'Avg Score', 'zip_code': 'ZIP Code', 'count': 'Properties'},
            color='mean',
            color_continuous_scale='RdYlGn'
        )

        fig_zips.update_traces(texttemplate='%{text} props', textposition='outside')

        fig_zips.update_layout(
            height=350,
            margin=dict(l=20, r=20, t=20, b=20),
            xaxis_title="ZIP Code",
            yaxis_title="Average Opportunity Score"
        )

        st.plotly_chart(fig_zips, use_container_width=True)
    else:
        st.info("No ZIP code data available")

# CHART 4: Below Market vs Days on Market (Scatter)
with col2:
    st.markdown("### 📉 Below Market % vs Days Listed")

    if 'below_market_percentage' in df.columns and 'days_on_market' in df.columns:
        scatter_data = df[
            (df['below_market_percentage'] > 0) &
            (df['days_on_market'] > 0)
        ]

        if len(scatter_data) > 0:
            fig_scatter = px.scatter(
                scatter_data,
                x='days_on_market',
                y='below_market_percentage',
                color='opportunity_score',
                size='list_price' if 'list_price' in scatter_data.columns else None,
                hover_data=['street_address', 'city'] if 'street_address' in scatter_data.columns else None,
                color_continuous_scale='RdYlGn',
                labels={
                    'days_on_market': 'Days on Market',
                    'below_market_percentage': 'Below Market %',
                    'opportunity_score': 'Score'
                }
            )

            fig_scatter.update_layout(
                height=350,
                margin=dict(l=20, r=20, t=20, b=20)
            )

            st.plotly_chart(fig_scatter, use_container_width=True)
        else:
            st.info("No data points available for comparison")
    else:
        st.info("Insufficient data for comparison")

st.markdown("---")

# County Comparison
st.markdown("### 🗺️ County Comparison")

if 'city' in df.columns:
    # Try to identify counties
    df['county'] = df['city'].apply(
        lambda x: 'San Diego County' if pd.notna(x) and any(sd in str(x).lower() for sd in ['san diego', 'la jolla', 'del mar', 'encinitas', 'carlsbad', 'oceanside'])
        else ('Clark County' if pd.notna(x) and any(lv in str(x).lower() for lv in ['las vegas', 'henderson', 'north las vegas', 'summerlin'])
        else 'Other')
    )

    county_df = df[df['county'].isin(['San Diego County', 'Clark County'])]

    if len(county_df) > 0:
        col1, col2, col3 = st.columns(3)

        with col1:
            st.markdown("#### Properties by County")
            county_counts = county_df['county'].value_counts()

            for county, count in county_counts.items():
                st.metric(county, f"{count} properties")

        with col2:
            st.markdown("#### Avg Price by County")
            if 'list_price' in county_df.columns:
                county_prices = county_df.groupby('county')['list_price'].mean()

                for county, price in county_prices.items():
                    st.metric(county, f"${price:,.0f}")
            else:
                st.info("No price data")

        with col3:
            st.markdown("#### Avg Below Market")
            if 'below_market_percentage' in county_df.columns:
                county_below = county_df[county_df['below_market_percentage'] > 0].groupby('county')['below_market_percentage'].mean()

                for county, below in county_below.items():
                    st.metric(county, f"{below:.1f}%")
            else:
                st.info("No below market data")

        # County comparison chart
        if 'opportunity_score' in county_df.columns:
            st.markdown("#### Opportunity Score Distribution by County")

            fig_county = px.box(
                county_df,
                x='county',
                y='opportunity_score',
                color='county',
                labels={'county': 'County', 'opportunity_score': 'Opportunity Score'},
                color_discrete_map={
                    'San Diego County': '#1f77b4',
                    'Clark County': '#ff7f0e'
                }
            )

            fig_county.update_layout(
                height=300,
                margin=dict(l=20, r=20, t=20, b=20),
                showlegend=False
            )

            st.plotly_chart(fig_county, use_container_width=True)
    else:
        st.info("No county data available for comparison")
else:
    st.info("City data not available for county comparison")

st.markdown("---")

# Investment Summary Table
st.markdown("### 💎 Top Investment Opportunities")

if 'opportunity_score' in df.columns:
    top_deals = df.nlargest(10, 'opportunity_score')

    display_cols = []
    col_mapping = {
        'street_address': 'Address',
        'city': 'City',
        'opportunity_score': 'Score',
        'list_price': 'Price',
        'below_market_percentage': 'Below Market',
        'days_on_market': 'Days',
        'estimated_profit': 'Est. Profit'
    }

    for col in col_mapping.keys():
        if col in top_deals.columns:
            display_cols.append(col)

    if display_cols:
        summary_df = top_deals[display_cols].copy()

        # Format
        if 'list_price' in summary_df.columns:
            summary_df['list_price'] = summary_df['list_price'].apply(
                lambda x: f"${x:,.0f}" if pd.notna(x) else "N/A"
            )

        if 'below_market_percentage' in summary_df.columns:
            summary_df['below_market_percentage'] = summary_df['below_market_percentage'].apply(
                lambda x: f"{x:.1f}%" if pd.notna(x) else "N/A"
            )

        if 'estimated_profit' in summary_df.columns:
            summary_df['estimated_profit'] = summary_df['estimated_profit'].apply(
                lambda x: f"${x:,.0f}" if pd.notna(x) and x > 0 else "N/A"
            )

        # Rename
        summary_df = summary_df.rename(columns=col_mapping)

        st.dataframe(
            summary_df,
            use_container_width=True,
            hide_index=True,
            height=400
        )

        # Export
        csv = df.to_csv(index=False)
        st.download_button(
            label="📥 Download Full Dataset (CSV)",
            data=csv,
            file_name=f"dealfinder_analytics_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv",
            use_container_width=True
        )
    else:
        st.info("No properties to display")
else:
    st.info("No scored properties available")

st.markdown("---")

# Market Insights
with st.expander("💡 AI Market Insights", expanded=False):
    st.markdown("### Automated Market Analysis")

    # Calculate insights
    insights = []

    # Hot market insight
    if hot_deals > 0:
        insights.append(f"🔥 **{hot_deals} hot deals** (90+ score) available - act fast on these opportunities!")

    # Price trends
    if 'list_price' in df.columns:
        avg_price = df['list_price'].mean()
        if avg_price < 700000:
            insights.append(f"💰 **Buyer's market detected** - Average price ${avg_price:,.0f} is below typical range")
        elif avg_price > 1200000:
            insights.append(f"📈 **Premium market** - Average price ${avg_price:,.0f} suggests high-end properties")

    # Days on market insight
    if 'days_on_market' in df.columns:
        avg_dom = df['days_on_market'].mean()
        if avg_dom > 60:
            insights.append(f"⏰ **Motivated sellers** - Properties averaging {avg_dom:.0f} days on market = negotiation opportunity")
        elif avg_dom < 20:
            insights.append(f"⚡ **Fast-moving market** - Properties selling quickly ({avg_dom:.0f} days average)")

    # Below market insight
    if 'below_market_percentage' in df.columns:
        below_market_props = df[df['below_market_percentage'] > 20]
        if len(below_market_props) > 0:
            insights.append(f"💎 **{len(below_market_props)} deep discounts** - Properties 20%+ below market value found")

    # County comparison
    if 'county' in df.columns:
        sd_count = len(df[df['county'] == 'San Diego County'])
        clark_count = len(df[df['county'] == 'Clark County'])

        if sd_count > clark_count * 1.5:
            insights.append(f"🏖️ **San Diego dominated** - {sd_count} vs {clark_count} properties (SD has more opportunities)")
        elif clark_count > sd_count * 1.5:
            insights.append(f"🎰 **Las Vegas dominated** - {clark_count} vs {sd_count} properties (Vegas has more deals)")

    if insights:
        for insight in insights:
            st.markdown(insight)
    else:
        st.info("Analyzing market trends... Run more scans to generate insights.")

st.markdown("---")

# Quick Actions
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
