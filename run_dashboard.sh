#!/bin/bash
# Launch DealFinder Pro Dashboard
# Usage: ./run_dashboard.sh

echo "🏠 Starting DealFinder Pro Dashboard..."
echo ""

cd "/Users/mikekwak/Real Estate Valuation"
python3 -m streamlit run dashboard/app.py

# Dashboard will open automatically in your browser
# Visit: http://localhost:8501
