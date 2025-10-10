#!/bin/bash
# Start DealFinder Pro Next.js Frontend (Development Mode)

cd "$(dirname "$0")"

echo "🚀 Starting DealFinder Pro Frontend..."
echo "📡 Frontend will be available at: http://localhost:3000"
echo "🔧 Make sure FastAPI backend is running at http://localhost:8000"
echo ""

# Create .env.local if it doesn't exist
if [ ! -f .env.local ]; then
  echo "Creating .env.local..."
  echo "NEXT_PUBLIC_API_URL=http://localhost:8000" > .env.local
fi

# Start Next.js dev server
npm run dev
