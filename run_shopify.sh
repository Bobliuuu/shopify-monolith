#!/bin/bash

# Script to run the Shopify pipeline from the root directory
# This replicates the command: cd dlt && python3 -m pipelines.run_shopify_pipeline

# Get the directory where this script is located (root of the project)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DLT_DIR="$SCRIPT_DIR/dlt"

echo "🚀 Running Shopify pipeline..."
echo "📁 Working directory: $DLT_DIR"
echo "🐍 Command: python3 -m pipelines.run_shopify_pipeline"
echo "----------------------------------------"

# Check if dlt directory exists
if [ ! -d "$DLT_DIR" ]; then
    echo "❌ Error: dlt directory not found!"
    echo "Expected path: $DLT_DIR"
    exit 1
fi

# Check if the pipeline file exists
PIPELINE_FILE="$DLT_DIR/pipelines/run_shopify_pipeline.py"
if [ ! -f "$PIPELINE_FILE" ]; then
    echo "❌ Error: run_shopify_pipeline.py not found!"
    echo "Expected path: $PIPELINE_FILE"
    exit 1
fi

# Change to dlt directory and run the pipeline
cd "$DLT_DIR" || {
    echo "❌ Error: Could not change to dlt directory"
    exit 1
}

# Run the pipeline
if python3 -m pipelines.run_shopify_pipeline; then
    echo "----------------------------------------"
    echo "✅ Shopify pipeline completed successfully!"
else
    echo "----------------------------------------"
    echo "❌ Shopify pipeline failed!"
    exit 1
fi 