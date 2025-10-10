#!/bin/bash
# Start DealFinder Pro FastAPI Backend
# Usage: ./start_api.sh

cd "$(dirname "$0")"

echo "🚀 Starting DealFinder Pro API..."
echo "📡 API will be available at: http://localhost:8000"
echo "📚 API Docs will be available at: http://localhost:8000/docs"
echo ""

# Start uvicorn with auto-reload
python3 -m uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
