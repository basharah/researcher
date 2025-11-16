#!/bin/bash
# Upload test papers to the system

set -e

echo "=========================================="
echo "Upload Test Papers"
echo "=========================================="
echo ""

# Check if papers exist
if [ ! -f "157180001.pdf" ]; then
    echo "Error: No PDF files found in current directory"
    echo "Expected files like: 157180001.pdf, 157180634.pdf, etc."
    exit 1
fi

# Default credentials
EMAIL="${1:-admin@researcher.local}"
PASSWORD="${2:-admin123}"
API_URL="http://localhost:8000/api/v1"

echo "Using credentials:"
echo "  Email: $EMAIL"
echo "  Password: $PASSWORD"
echo ""

# Step 1: Login to get cookie
echo "Step 1: Logging in..."
LOGIN_RESPONSE=$(curl -s -c cookies.txt -X POST "$API_URL/auth/login" \
  -H "Content-Type: application/json" \
  -d "{\"email\":\"$EMAIL\",\"password\":\"$PASSWORD\"}")

if echo "$LOGIN_RESPONSE" | grep -q "access_token"; then
    echo "✓ Login successful"
else
    echo "✗ Login failed"
    echo "Response: $LOGIN_RESPONSE"
    exit 1
fi
echo ""

# Step 2: Upload each PDF
echo "Step 2: Uploading papers..."
UPLOADED=0
FAILED=0

for pdf in *.pdf; do
    if [ -f "$pdf" ]; then
        echo -n "Uploading: $pdf ... "
        
        UPLOAD_RESPONSE=$(curl -s -b cookies.txt -X POST "$API_URL/upload" \
          -F "file=@$pdf" 2>&1)
        
        if echo "$UPLOAD_RESPONSE" | grep -q '"id"'; then
            DOC_ID=$(echo "$UPLOAD_RESPONSE" | grep -o '"id":[0-9]*' | cut -d':' -f2)
            echo "✓ Success (ID: $DOC_ID)"
            ((UPLOADED++))
        else
            echo "✗ Failed"
            echo "  Response: $UPLOAD_RESPONSE"
            ((FAILED++))
        fi
    fi
done
echo ""

# Step 3: Summary
echo "=========================================="
echo "Upload Summary"
echo "=========================================="
echo "Uploaded: $UPLOADED"
echo "Failed: $FAILED"
echo ""

# Step 4: List documents
echo "Checking uploaded documents..."
DOCS=$(curl -s -b cookies.txt "$API_URL/documents?limit=20")
DOC_COUNT=$(echo "$DOCS" | grep -o '"total":[0-9]*' | cut -d':' -f2)
echo "Total documents in system: $DOC_COUNT"
echo ""

# Cleanup
rm -f cookies.txt

echo "=========================================="
echo "Done!"
echo ""
echo "Next steps:"
echo "1. Wait ~30 seconds for Vector DB processing"
echo "2. Test search: http://localhost:3000/search"
echo "3. Test analysis: http://localhost:3000/analysis"
echo "=========================================="
