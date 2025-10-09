"""
Data Import Page
Upload CSV/Excel files to enhance property data
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

from components.data_importer import DataImporter

st.set_page_config(page_title="Data Import", page_icon="📥", layout="wide")

st.title("📥 Data Import Center")
st.markdown("Upload external property data to enhance analysis")
st.markdown("---")

# Initialize
importer = DataImporter()

# Import type selector
st.markdown("### 📂 Select Import Type")

import_type = st.selectbox(
    "What type of data are you importing?",
    options=["MLS Bulk Export", "Comparable Sales", "Tax Assessment Data", "General Property Data"],
    help="Choose the type that best matches your data"
)

# Map display name to internal type
type_mapping = {
    "MLS Bulk Export": "mls",
    "Comparable Sales": "comps",
    "Tax Assessment Data": "tax_data",
    "General Property Data": "general"
}

selected_type = type_mapping[import_type]

st.markdown("---")

# File upload
st.markdown("### 📎 Upload File")

uploaded_file = st.file_uploader(
    "Choose a CSV or Excel file",
    type=['csv', 'xlsx', 'xls'],
    help="Maximum file size: 50 MB"
)

if uploaded_file:
    st.success(f"✅ File loaded: **{uploaded_file.name}** ({uploaded_file.size:,} bytes)")

    # Show file preview
    try:
        if uploaded_file.name.endswith('.csv'):
            df_preview = pd.read_csv(uploaded_file, nrows=10)
        else:
            df_preview = pd.read_excel(uploaded_file, nrows=10)

        st.markdown("### 👀 Data Preview (First 10 rows)")
        st.dataframe(df_preview, use_container_width=True)

        # Reset file pointer
        uploaded_file.seek(0)

        # Column info
        st.markdown("### 📊 Detected Columns")
        col1, col2 = st.columns([1, 3])

        with col1:
            st.metric("Total Columns", len(df_preview.columns))

        with col2:
            st.caption(", ".join(df_preview.columns.tolist()))

        st.markdown("---")

        # Process button
        col1, col2 = st.columns([2, 1])

        with col1:
            st.markdown("**Ready to import?**")
            st.caption(f"This will process all rows in {uploaded_file.name}")

        with col2:
            if st.button("🚀 Process & Import", type="primary", use_container_width=True):
                with st.spinner("Processing file..."):
                    try:
                        # Reset file pointer again
                        uploaded_file.seek(0)

                        # Process file
                        result = importer.process_file(uploaded_file, selected_type)

                        if result['success']:
                            st.success(f"✅ Successfully imported {result['imported_count']} properties!")

                            # Store in session state
                            if 'scraped_properties' not in st.session_state:
                                st.session_state['scraped_properties'] = []

                            # Merge with existing
                            merged = importer.merge_with_existing(
                                result['data'],
                                st.session_state['scraped_properties']
                            )

                            st.session_state['scraped_properties'] = merged

                            st.balloons()

                            # Show summary
                            st.markdown("### 📊 Import Summary")

                            col1, col2, col3 = st.columns(3)

                            with col1:
                                st.metric("Imported", result['imported_count'])

                            with col2:
                                st.metric("Total Properties", len(merged))

                            with col3:
                                if result.get('errors'):
                                    st.metric("Errors", len(result['errors']))

                            # Show sample
                            if result['data']:
                                with st.expander("📋 View Imported Data Sample"):
                                    sample_df = pd.DataFrame(result['data'][:5])
                                    st.dataframe(sample_df, use_container_width=True)

                        else:
                            st.error(f"❌ Import failed: {result['message']}")

                            if result.get('errors'):
                                with st.expander("❌ View Errors"):
                                    for error in result['errors']:
                                        st.error(error)

                    except Exception as e:
                        st.error(f"❌ Error processing file: {e}")

    except Exception as e:
        st.error(f"❌ Error loading file preview: {e}")

else:
    st.info("👆 Upload a CSV or Excel file to get started")

st.markdown("---")

# Download templates
st.markdown("### 📋 Download Template Files")
st.markdown("Not sure what format to use? Download a template:")

col1, col2, col3, col4 = st.columns(4)

with col1:
    template_mls = importer.generate_template('mls')
    csv_mls = template_mls.to_csv(index=False)

    st.download_button(
        label="📄 MLS Template",
        data=csv_mls,
        file_name="template_mls.csv",
        mime="text/csv",
        use_container_width=True,
        help="For bulk MLS exports"
    )

with col2:
    template_comps = importer.generate_template('comps')
    csv_comps = template_comps.to_csv(index=False)

    st.download_button(
        label="📄 Comps Template",
        data=csv_comps,
        file_name="template_comps.csv",
        mime="text/csv",
        use_container_width=True,
        help="For comparable sales data"
    )

with col3:
    template_tax = importer.generate_template('tax_data')
    csv_tax = template_tax.to_csv(index=False)

    st.download_button(
        label="📄 Tax Data Template",
        data=csv_tax,
        file_name="template_tax.csv",
        mime="text/csv",
        use_container_width=True,
        help="For tax assessment values"
    )

with col4:
    template_general = importer.generate_template('general')
    csv_general = template_general.to_csv(index=False)

    st.download_button(
        label="📄 General Template",
        data=csv_general,
        file_name="template_general.csv",
        mime="text/csv",
        use_container_width=True,
        help="For any property data"
    )

st.markdown("---")

# Import history
st.markdown("### 📜 Import History")

history = importer.get_import_history()

if history:
    history_df = pd.DataFrame(history)

    # Format timestamp
    if 'timestamp' in history_df.columns:
        history_df['timestamp'] = pd.to_datetime(history_df['timestamp']).dt.strftime('%Y-%m-%d %H:%M:%S')

    # Rename columns
    history_df = history_df.rename(columns={
        'timestamp': 'Date/Time',
        'filename': 'File Name',
        'type': 'Import Type',
        'count': 'Properties'
    })

    st.dataframe(
        history_df,
        use_container_width=True,
        hide_index=True
    )
else:
    st.info("No imports yet. Upload a file to get started!")

st.markdown("---")

# Column mapping guide
with st.expander("📖 Column Mapping Guide"):
    st.markdown("""
    ### How Data Import Works

    The system automatically maps your columns to standard fields. Here's what it looks for:

    #### For MLS Data:
    - **Address:** `address`, `street_address`, `property_address`, `FullStreetAddress`
    - **City:** `city`, `City`, `CITY`
    - **Price:** `price`, `list_price`, `asking_price`, `ListPrice`
    - **Bedrooms:** `beds`, `bedrooms`, `BedsTotal`
    - **Bathrooms:** `baths`, `bathrooms`, `BathsTotal`
    - **Square Feet:** `sqft`, `square_feet`, `LivingArea`

    #### For Comparable Sales:
    - **Sold Price:** `sold_price`, `sale_price`, `price`
    - **Sold Date:** `sold_date`, `sale_date`, `date`
    - Plus all address/property fields above

    #### For Tax Data:
    - **Tax Value:** `assessed_value`, `tax_value`, `assessment`
    - **Annual Taxes:** `annual_tax`, `taxes`, `property_tax`

    **Tip:** Your column names don't have to match exactly - the system tries multiple variations!
    """)

# Usage tips
with st.expander("💡 Usage Tips"):
    st.markdown("""
    ### Best Practices for Data Import

    1. **Start with a template** - Download the appropriate template and fill it with your data

    2. **Clean your data** - Remove:
       - Extra header rows
       - Summary rows at the bottom
       - Special characters in addresses

    3. **Check formats:**
       - Prices: Just numbers (no $ or commas) - e.g., `500000` not `$500,000`
       - Dates: YYYY-MM-DD format - e.g., `2025-01-15`
       - Phone numbers: Include country code - e.g., `+1 234 567 8900`

    4. **Preview first** - Always check the preview before importing

    5. **Merge strategy:**
       - System matches by address
       - Imported data updates/enhances existing properties
       - New properties are added automatically

    6. **Use cases:**
       - **MLS data:** Bulk import from your MLS system
       - **Comps:** Add recent sales for better ARV calculations
       - **Tax data:** Identify properties below tax assessments
       - **General:** Your own research, notes, custom values
    """)

st.markdown("---")

# Quick actions
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
