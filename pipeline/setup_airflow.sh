#!/bin/bash

# Setup script for Airflow with Shopify integration

echo "Setting up Airflow for Shopify data pipeline..."

# Create virtual environment if it doesn't exist
if [ ! -d "../env" ]; then
    echo "Creating virtual environment..."
    python3 -m venv ../env
fi

# Activate virtual environment
echo "Activating virtual environment..."
source ../env/bin/activate

# Install requirements
echo "Installing requirements..."
pip install -r ../requirements.txt

# Initialize Airflow database
echo "Initializing Airflow database..."
airflow db migrate

echo "Airflow setup complete!"
echo "To start Airflow webserver: airflow webserver --port 8080"
echo "To start Airflow scheduler: airflow scheduler"
echo "Access Airflow UI at: http://localhost:8080" 