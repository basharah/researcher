#!/bin/bash

# Quick Start Script for Research Paper Chatbot
# This script helps you get started with Phase 1

set -e

echo "🚀 Research Paper Chatbot - Quick Start"
echo "========================================"
echo ""

# Check if .env exists
if [ ! -f .env ]; then
    echo "📝 Creating .env file from .env.example..."
    cp .env.example .env
    echo "⚠️  Please edit .env and add your API keys before proceeding to Phase 3"
    echo ""
fi

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker and try again."
    exit 1
fi

echo "🐳 Starting Docker containers for Phase 1..."
echo ""
echo "Services starting:"
echo "  - PostgreSQL (with pgvector)"
echo "  - Redis"
echo "  - Document Processing Service"
echo ""

# Start Phase 1 services
docker-compose up -d postgres redis

echo "⏳ Waiting for database to be ready..."
sleep 5

docker-compose up -d document-processing

echo ""
echo "✅ Phase 1 is now running!"
echo ""
echo "📍 Service URLs:"
echo "  - Document Processing API: http://localhost:8001"
echo "  - API Documentation: http://localhost:8001/docs"
echo "  - PostgreSQL: localhost:5432"
echo "  - Redis: localhost:6379"
echo ""
echo "🧪 Test the service:"
echo "  curl http://localhost:8001/health"
echo ""
echo "📚 Next steps:"
echo "  1. Visit http://localhost:8001/docs for interactive API documentation"
echo "  2. Upload a research paper PDF using the /upload endpoint"
echo "  3. Check the README.md for more information"
echo ""
echo "🛑 To stop all services:"
echo "  docker-compose down"
echo ""
