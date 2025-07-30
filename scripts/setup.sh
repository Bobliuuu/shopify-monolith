#!/bin/bash

# Shopify Monolith dbt Setup Script
echo "Setting up Shopify Monolith dbt project..."

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is required but not installed."
    exit 1
fi

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Test connection
echo "Testing dbt connection..."
dbt debug

# Run models
echo "Running dbt models..."
dbt run

# Run tests
echo "Running dbt tests..."
dbt test

# Show sample data
echo "Displaying sample data..."
python show_data.py

echo "Setup complete! Your shopify_transactions_base table is ready."
echo "Database file: shopify_monolith.duckdb"
echo "Target: dev" 