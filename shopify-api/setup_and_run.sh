#!/bin/bash

echo "🚀 Setting up Shopify API Rails app..."

# Install gems
echo "📦 Installing gems..."
bundle install

# Set environment variables
export SHOPIFY_DOMAIN=shop-monolith.myshopify.com
export SHOPIFY_ACCESS_TOKEN=test
export SHOPIFY_API_KEY=dummy_key
export SHOPIFY_API_SECRET=dummy_secret
export SHOPIFY_HOST=https://localhost:3000

echo "✅ Environment variables set:"
echo "  SHOPIFY_DOMAIN: $SHOPIFY_DOMAIN"
echo "  SHOPIFY_ACCESS_TOKEN: $SHOPIFY_ACCESS_TOKEN"
echo "  SHOPIFY_API_KEY: $SHOPIFY_API_KEY"
echo "  SHOPIFY_API_SECRET: $SHOPIFY_API_SECRET"
echo "  SHOPIFY_HOST: $SHOPIFY_HOST"

# Start Rails server
echo "🌐 Starting Rails server on http://localhost:3000"
echo ""
echo "You can now:"
echo "  - Visit: http://localhost:3000/products"
echo "  - Download SQL: curl http://localhost:3000/products > output.sql"
echo ""
echo "Press Ctrl+C to stop the server"

# Start the Rails server
rails server -p 3000 