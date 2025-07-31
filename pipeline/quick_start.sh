#!/bin/bash

# Quick start script for Shopify Airflow pipeline

echo "🚀 Quick Start: Shopify Airflow Pipeline"
echo "=========================================="

check_error() {
    if [ $? -ne 0 ]; then
        echo "❌ Error in previous step. Exiting."
        exit 1
    fi
}

# Check if we're in the right directory
if [ ! -f "setup_airflow.sh" ]; then
    echo "❌ Please run this script from the pipieline directory"
    exit 1
fi

# Step 1: Setup Airflow
echo "📦 Step 1: Setting up Airflow..."
./setup_airflow.sh
check_error

# Step 2: Check if .env exists
if [ ! -f ".env" ]; then
    echo "⚠️  .env file not found. Please create it with your Shopify credentials:"
    echo "   cp env.example .env"
    echo "   # Then edit .env with your Shopify domain and access token"
    exit 1
fi

# Step 3: Test connections
echo "🧪 Step 2: Testing connections..."
source ../env/bin/activate
pip install -r requirements.txt
python test_shopify_connection.py
check_error

# Step 4: Start Airflow
echo "🌐 Step 3: Starting Airflow..."
echo ""
echo "Starting Airflow webserver on port 8080..."
echo "You can now access the Airflow UI at: http://localhost:8080"
echo "Username: admin"
echo "Password: admin"
echo ""
echo "To start the scheduler in another terminal:"
echo "  cd ppieline"
echo "  source venv/bin/activate"
echo "  airflow scheduler"
echo "Or run ./start_server.sh"
echo "Press Ctrl+C to stop the webserver"
