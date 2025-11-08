#!/bin/bash

# Test script for Document Processing Service

echo "🧪 Testing Document Processing Service"
echo "======================================"
echo ""

# Check if service is running
echo "1. Checking service health..."
curl -s http://localhost:8001/health | python3 -m json.tool
echo ""

# Test root endpoint
echo "2. Checking service info..."
curl -s http://localhost:8001/ | python3 -m json.tool
echo ""

# Test document listing (API v1)
echo "3. Listing documents (API v1)..."
curl -s http://localhost:8001/api/v1/documents | python3 -m json.tool
echo ""

echo "✅ Basic tests completed!"
echo ""
echo "📚 API Documentation:"
echo "  Swagger UI: http://localhost:8001/docs"
echo "  ReDoc: http://localhost:8001/redoc"
echo ""
echo "To upload a document:"
echo "curl -X POST http://localhost:8001/api/v1/upload -F 'file=@your_paper.pdf'"
echo ""
