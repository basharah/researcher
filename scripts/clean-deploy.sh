#!/bin/bash
# Complete cleanup and redeployment script
# This will reset everything and start fresh

set -e  # Exit on error

echo "=========================================="
echo "Research Paper Analysis - Clean Deploy"
echo "=========================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Step 1: Stop all services
echo -e "${YELLOW}Step 1: Stopping all services...${NC}"
docker-compose down -v
echo -e "${GREEN}✓ Services stopped${NC}"
echo ""

# Step 2: Clean up volumes and networks
echo -e "${YELLOW}Step 2: Cleaning up Docker volumes...${NC}"
docker volume prune -f
echo -e "${GREEN}✓ Volumes cleaned${NC}"
echo ""

# Step 3: Remove old uploads (optional - uncomment if needed)
# echo -e "${YELLOW}Step 3: Cleaning upload directory...${NC}"
# rm -rf services/document-processing/uploads_data/*
# echo -e "${GREEN}✓ Uploads cleaned${NC}"
# echo ""

# Step 4: Build all services
echo -e "${YELLOW}Step 3: Building all services...${NC}"
docker-compose build
echo -e "${GREEN}✓ Services built${NC}"
echo ""

# Step 5: Start database services first
echo -e "${YELLOW}Step 4: Starting database services...${NC}"
docker-compose up -d postgres redis
echo -e "${GREEN}✓ Databases starting...${NC}"
echo "Waiting for databases to be ready (15 seconds)..."
sleep 15
echo ""

# Step 6: Run migrations
echo -e "${YELLOW}Step 5: Running database migrations...${NC}"
echo "Creating API Gateway tables..."
docker-compose run --rm api-gateway python create_tables.py
echo ""
echo "Running document processing migrations..."
docker-compose run --rm migrate
echo -e "${GREEN}✓ Migrations complete${NC}"
echo ""

# Step 7: Initialize default admin user
echo -e "${YELLOW}Step 6: Creating default admin user...${NC}"
docker-compose run --rm -e DEFAULT_ADMIN_EMAIL=admin@researcher.local -e DEFAULT_ADMIN_PASSWORD=admin123 api-gateway python init_admin.py
echo -e "${GREEN}✓ Admin user created${NC}"
echo ""

# Step 8: Start all services
echo -e "${YELLOW}Step 7: Starting all services...${NC}"
docker-compose --profile phase4 up -d
echo -e "${GREEN}✓ All services started${NC}"
echo ""

# Step 9: Wait for services to be ready
echo -e "${YELLOW}Step 8: Waiting for services to be ready...${NC}"
echo "This may take 30-60 seconds for Vector DB to download embeddings model..."
sleep 5

# Check health
for i in {1..12}; do
    echo -n "Checking health (attempt $i/12)... "
    HEALTH=$(curl -s http://localhost:8000/api/v1/health 2>/dev/null | grep -o '"status":"[^"]*"' | cut -d'"' -f4 || echo "waiting")
    if [ "$HEALTH" == "healthy" ]; then
        echo -e "${GREEN}✓ Healthy!${NC}"
        break
    else
        echo "waiting..."
        sleep 5
    fi
done
echo ""

# Step 10: Display service status
echo -e "${YELLOW}Step 9: Service Status${NC}"
docker-compose ps
echo ""

# Step 11: Show admin credentials
echo "=========================================="
echo -e "${GREEN}Deployment Complete!${NC}"
echo "=========================================="
echo ""
echo -e "${YELLOW}Default Admin Credentials:${NC}"
echo "  Email: admin@researcher.local"
echo "  Password: admin123"
echo ""
echo -e "${RED}⚠️  IMPORTANT: Change password after first login!${NC}"
echo ""
echo -e "${YELLOW}Service URLs:${NC}"
echo "  Frontend: http://localhost:3000"
echo "  API Gateway: http://localhost:8000"
echo "  Flower (Celery): http://localhost:5555"
echo ""
echo -e "${YELLOW}Quick Test:${NC}"
echo "  curl http://localhost:8000/api/v1/health"
echo ""
echo -e "${YELLOW}View Logs:${NC}"
echo "  docker-compose logs -f [service-name]"
echo ""
echo "=========================================="
