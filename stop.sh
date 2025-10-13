#!/bin/bash

# SaveMoney Service Stop Script
# Gracefully stops all running development servers

echo "🛑 Stopping SaveMoney Development Services..."
echo "============================================="

# Function to kill processes by port
kill_by_port() {
    local port=$1
    local service_name=$2

    echo "🔍 Looking for $service_name on port $port..."

    # Find PIDs using the port
    local pids=$(lsof -ti:$port 2>/dev/null)

    if [ -n "$pids" ]; then
        echo "   Found PIDs: $pids"
        kill $pids 2>/dev/null

        # Wait a moment for graceful shutdown
        sleep 2

        # Force kill if still running
        if lsof -ti:$port >/dev/null 2>&1; then
            echo "   Force killing remaining processes..."
            kill -9 $pids 2>/dev/null
        fi

        echo "✅ $service_name stopped"
    else
        echo "   No $service_name found running on port $port"
    fi
}

# Function to kill processes by name pattern
kill_by_pattern() {
    local pattern=$1
    local service_name=$2

    echo "🔍 Looking for $service_name with pattern '$pattern'..."

    local pids=$(pgrep -f "$pattern" 2>/dev/null)

    if [ -n "$pids" ]; then
        echo "   Found PIDs: $pids"
        kill $pids 2>/dev/null

        # Wait a moment for graceful shutdown
        sleep 2

        # Force kill if still running
        if pgrep -f "$pattern" >/dev/null 2>&1; then
            echo "   Force killing remaining processes..."
            kill -9 $pids 2>/dev/null
        fi

        echo "✅ $service_name stopped"
    else
        echo "   No $service_name found"
    fi
}

# Stop backend server (FastAPI)
kill_by_port 8000 "Backend Server (FastAPI)"

# Stop frontend server (Vite)
kill_by_port 5173 "Frontend Server (Vite)"

# Also kill any remaining uvicorn processes
kill_by_pattern "uvicorn" "Uvicorn Processes"

# Kill any remaining npm dev processes
kill_by_pattern "npm run dev" "npm dev processes"

# Kill any remaining node processes for this project
kill_by_pattern "vite" "Vite processes"

echo ""
echo "✅ All SaveMoney services have been stopped"
echo ""
echo "📋 Services stopped:"
echo "   - Backend API (port 8000)"
echo "   - Frontend development server (port 5173)"
echo "   - All related development processes"
echo ""
echo "💡 To restart services, run: ./dev.sh"