#!/bin/bash

# SaveMoney Development Startup Script
# One-click script to start both backend and frontend development servers

echo "🚀 Starting SaveMoney Development Environment..."
echo "================================================"

# Check if .env file exists
if [ ! -f "backend/.env" ]; then
    echo "⚠️  Warning: backend/.env file not found"
    echo "   Please copy .env.example to .env and configure your API keys"
    echo "   Required: OPENAI_API_KEY, FEISHU_APP_ID, FEISHU_APP_SECRET, FEISHU_TABLE_ID"
fi

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check for required tools
echo "🔍 Checking required tools..."

if ! command_exists uv; then
    echo "❌ uv (Python package manager) not found"
    echo "   Install with: curl -LsSf https://astral.sh/uv/install.sh | sh"
    exit 1
fi

if ! command_exists node; then
    echo "❌ Node.js not found"
    echo "   Install from: https://nodejs.org/"
    exit 1
fi

if ! command_exists npm; then
    echo "❌ npm not found"
    echo "   Install with Node.js"
    exit 1
fi

echo "✅ All required tools are available"

# Install backend dependencies if needed
echo "📦 Setting up backend dependencies..."
cd backend
if [ ! -d ".venv" ] || [ ! -f "uv.lock" ]; then
    echo "   Installing Python dependencies with uv..."
    uv sync
fi
cd ..

# Install frontend dependencies if needed
echo "📦 Setting up frontend dependencies..."
cd frontend
if [ ! -d "node_modules" ]; then
    echo "   Installing Node.js dependencies..."
    npm install
fi
cd ..

echo ""
echo "🎯 Starting development servers..."
echo "   Backend: http://localhost:8000"
echo "   Frontend: http://localhost:5173"
echo "   API Docs: http://localhost:8000/docs"
echo ""

# Function to handle cleanup on script exit
cleanup() {
    echo ""
    echo "🛑 Stopping development servers..."
    kill $BACKEND_PID $FRONTEND_PID 2>/dev/null
    echo "✅ Development environment stopped"
    exit 0
}

# Set up signal handlers
trap cleanup SIGINT SIGTERM

# Start backend server in background
echo "🔧 Starting backend server..."
cd backend
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!
cd ..

# Wait a moment for backend to start
sleep 3

# Start frontend server in background
echo "🎨 Starting frontend server..."
cd frontend
npm run dev &
FRONTEND_PID=$!
cd ..

echo ""
echo "✅ Development servers started successfully!"
echo ""
echo "📋 Quick Start Guide:"
echo "   1. Open frontend: http://localhost:5173"
echo "   2. Click '开始录音' to record your voice"
echo "   3. Say something like: '今天中午花了25.3毛钱吃午饭'"
echo "   4. Review the extracted expense data"
echo "   5. Click '确认保存' to save to Feishu"
echo ""
echo "🔍 Debug Information:"
echo "   - Backend logs: Check terminal for API calls"
echo "   - Frontend logs: Check browser developer console"
echo "   - API testing: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop all servers"

# Wait for user to stop the servers
wait