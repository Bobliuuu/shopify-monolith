#!/bin/bash

echo "🌐 Starting Airflow API Server..."
echo "================================="

# Change to the script directory
cd "$(dirname "$0")"

# Activate virtual environment
source ../env/bin/activate

echo "✅ Virtual environment activated"
echo "🚀 Starting Airflow API Server..."
echo ""
echo "You can access the Airflow UI at: http://localhost:8080"
echo "Username: admin"
echo "Password: admin"
echo ""
echo "Press Ctrl+C to stop the API server"
echo ""

# Start the API server
airflow api-server 