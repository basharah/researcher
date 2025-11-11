#!/bin/bash
# Start services with production configuration (low CPU usage)

echo "Starting services with production configuration..."
echo "Features:"
echo "  ✓ No file watching (--reload disabled)"
echo "  ✓ Resource limits (CPU and memory)"
echo "  ✓ Read-only volumes where possible"
echo "  ✓ Multiple workers for better performance"
echo ""

docker-compose -f docker-compose.prod.yml up -d

echo ""
echo "Services starting..."
echo "Use 'docker-compose -f docker-compose.prod.yml logs -f' to view logs"
echo "Use 'docker-compose -f docker-compose.prod.yml down' to stop"
