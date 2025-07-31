#!/bin/bash

# Setup script for Airflow with Shopify integration

echo "Setting up Airflow for Shopify data pipeline..."

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install requirements
echo "Installing requirements..."
pip install -r requirements.txt

# Initialize Airflow database
echo "Initializing Airflow database..."
airflow db init

# Create admin user
echo "Creating Airflow admin user..."
airflow users create \
    --username admin \
    --firstname Admin \
    --lastname User \
    --role Admin \
    --email admin@example.com \
    --password admin

# Set environment variables
echo "Setting up environment variables..."
if [ ! -f ".env" ]; then
    cp env.example .env
    echo "Please edit .env file with your Shopify credentials"
fi

echo "Airflow setup complete!"
echo "To start Airflow webserver: airflow webserver --port 8080"
echo "To start Airflow scheduler: airflow scheduler"
echo "Access Airflow UI at: http://localhost:8080" 