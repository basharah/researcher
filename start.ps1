# Quick Start Script for Research Paper Chatbot (Windows)
# This script helps you get started with Phase 1

Write-Host "🚀 Research Paper Chatbot - Quick Start" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if .env exists
if (-not (Test-Path .env)) {
    Write-Host "📝 Creating .env file from .env.example..." -ForegroundColor Yellow
    Copy-Item .env.example .env
    Write-Host "⚠️  Please edit .env and add your API keys before proceeding to Phase 3" -ForegroundColor Yellow
    Write-Host ""
}

# Check if Docker is running
try {
    docker info | Out-Null
} catch {
    Write-Host "❌ Docker is not running. Please start Docker and try again." -ForegroundColor Red
    exit 1
}

Write-Host "🐳 Starting Docker containers for Phase 1..." -ForegroundColor Green
Write-Host ""
Write-Host "Services starting:"
Write-Host "  - PostgreSQL (with pgvector)"
Write-Host "  - Redis"
Write-Host "  - Document Processing Service"
Write-Host ""

# Start Phase 1 services
docker-compose up -d postgres redis

Write-Host "⏳ Waiting for database to be ready..." -ForegroundColor Yellow
Start-Sleep -Seconds 5

docker-compose up -d document-processing

Write-Host ""
Write-Host "✅ Phase 1 is now running!" -ForegroundColor Green
Write-Host ""
Write-Host "📍 Service URLs:"
Write-Host "  - Document Processing API: http://localhost:8001"
Write-Host "  - API Documentation: http://localhost:8001/docs"
Write-Host "  - PostgreSQL: localhost:5432"
Write-Host "  - Redis: localhost:6379"
Write-Host ""
Write-Host "🧪 Test the service:"
Write-Host "  curl http://localhost:8001/health"
Write-Host ""
Write-Host "📚 Next steps:"
Write-Host "  1. Visit http://localhost:8001/docs for interactive API documentation"
Write-Host "  2. Upload a research paper PDF using the /upload endpoint"
Write-Host "  3. Check the README.md for more information"
Write-Host ""
Write-Host "🛑 To stop all services:"
Write-Host "  docker-compose down"
Write-Host ""
