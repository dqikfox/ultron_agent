#!/bin/bash

echo "🤖 Setting up Ultron Assistant Frontend..."

# Navigate to frontend directory
cd "$(dirname "$0")"

# Install dependencies
echo "📦 Installing dependencies..."
npm install

# Start development server
echo "🚀 Starting Ultron Assistant frontend..."
echo "Make sure the backend server is running on http://127.0.0.1:8000"
echo "Frontend will be available at http://localhost:3000"

npm run dev
