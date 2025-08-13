#!/bin/bash

echo "🚀 Starting Airflow services in separate windows..."

airflow db migrate

# Get the current directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Function to start scheduler in new terminal window
start_scheduler() {
    open -a Terminal "$SCRIPT_DIR/start_scheduler.sh"
}

# Function to start API server in new terminal window
start_api_server() {
    open -a Terminal "$SCRIPT_DIR/start_api_server.sh"
}

# Start scheduler in new window
echo "📅 Opening scheduler window..."
start_scheduler

# Wait a moment for the window to open
sleep 2

# Start API server in new window
echo "🌐 Opening API server window..."
start_api_server

echo ""
echo "✅ Airflow services started in separate windows!"
echo "You can now access the Airflow UI at: http://localhost:8080"
echo "Each service is running in its own terminal window."
echo "To stop the services, close the respective terminal windows or use Ctrl+C in each window."