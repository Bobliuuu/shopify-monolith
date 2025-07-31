#!/bin/bash

echo "📅 Starting Airflow Scheduler..."
echo "================================"

# Change to the script directory
cd "$(dirname "$0")"

# Activate virtual environment
source ../env/bin/activate

echo "✅ Virtual environment activated"
echo "🚀 Starting Airflow Scheduler..."
echo ""
echo "Press Ctrl+C to stop the scheduler"
echo ""

# Start the scheduler
airflow scheduler 