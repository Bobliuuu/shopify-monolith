#!/bin/bash

echo "🧪 Testing Shopify Products API..."

# Set environment variables
export SHOPIFY_DOMAIN=shop-monolith.myshopify.com
export SHOPIFY_ACCESS_TOKEN=***REMOVED***

echo "📋 Environment variables:"
echo "  SHOPIFY_DOMAIN: $SHOPIFY_DOMAIN"
echo "  SHOPIFY_ACCESS_TOKEN: $SHOPIFY_ACCESS_TOKEN"
echo ""

# Test 1: Check if Rails server is running
echo "🔍 Test 1: Checking if Rails server is running..."
if curl -s http://localhost:3000/up > /dev/null; then
    echo "✅ Rails server is running"
else
    echo "❌ Rails server is not running. Please start it first:"
    echo "   cd shopify-api && ./setup_and_run.sh"
    exit 1
fi

# Test 2: Test the products endpoint
echo ""
echo "🔍 Test 2: Testing products endpoint..."
response=$(curl -s http://localhost:3000/products)

if [ $? -eq 0 ]; then
    echo "✅ Products endpoint is working"
    echo "📄 Response preview:"
    echo "$response" | head -20
    echo "..."
else
    echo "❌ Products endpoint failed"
    echo "Response: $response"
fi

# Test 3: Download SQL file
echo ""
echo "🔍 Test 3: Downloading SQL file..."
curl -s http://localhost:3000/products > test_output.sql

if [ -s test_output.sql ]; then
    echo "✅ SQL file downloaded successfully"
    echo "📄 SQL file preview:"
    head -10 test_output.sql
    echo "..."
    echo "📁 File size: $(wc -l < test_output.sql) lines"
else
    echo "❌ Failed to download SQL file"
fi

echo ""
echo "🎉 Testing completed!" 