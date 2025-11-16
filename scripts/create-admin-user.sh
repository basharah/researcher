#!/bin/bash
# Create default admin user in running API Gateway container
# This is useful if the system is already running and you need to create the admin user

set -e

echo "=========================================="
echo "Creating Default Admin User"
echo "=========================================="
echo ""

# Check if API Gateway container is running
if ! docker ps | grep -q api-gateway-service; then
    echo "❌ Error: API Gateway container is not running"
    echo "   Please start the services first with ./start-prod.sh or ./start.sh"
    exit 1
fi

echo "📝 Creating admin user in API Gateway..."
docker exec api-gateway-service python init_admin.py

echo ""
echo "=========================================="
echo "✅ Admin user creation complete!"
echo "=========================================="
echo ""
echo "Default credentials:"
echo "  Email: admin@bashars.eu"
echo "  Password: admin123"
echo ""
echo "⚠️  IMPORTANT: Change the password after first login!"
echo "   You can do this from the Profile page after logging in."
echo ""
