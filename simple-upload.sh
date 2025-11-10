#!/bin/bash
# Simple upload script for test papers

EMAIL="${1:-admin@example.com}"
PASSWORD="${2:-admin123}"

echo "==========================================" 
echo "Uploading Papers to Research System"
echo "=========================================="
echo ""

# Login
echo "Logging in as: $EMAIL"
curl -s -c cookies.txt -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d "{\"email\":\"$EMAIL\",\"password\":\"$PASSWORD\"}" > /dev/null

if [ $? -eq 0 ]; then
    echo "✓ Login successful"
else
    echo "✗ Login failed"
    exit 1
fi
echo ""

# Upload each PDF
count=0
for pdf in *.pdf; do
    if [ -f "$pdf" ]; then
        echo "Uploading: $pdf"
        response=$(curl -s -b cookies.txt -X POST "http://localhost:8000/api/v1/upload" -F "file=@$pdf")
        
        if echo "$response" | grep -q '"id"'; then
            id=$(echo "$response" | grep -o '"id":[0-9]*' | head -1 | cut -d':' -f2)
            echo "  ✓ Uploaded successfully (ID: $id)"
            ((count++))
        else
            echo "  ✗ Upload failed"
            echo "  Response: $response"
        fi
        
        # Small delay between uploads
        sleep 1
    fi
done

echo ""
echo "=========================================="
echo "Uploaded $count documents"
echo "=========================================="

# Wait for vector processing
echo ""
echo "Waiting 30 seconds for vector processing..."
sleep 30

# Check documents
echo ""
echo "Fetching document list..."
curl -s -b cookies.txt "http://localhost:8000/api/v1/documents?limit=20" | jq -r '.documents[] | "\(.id): \(.title // .filename)"'

# Cleanup
rm -f cookies.txt

echo ""
echo "Done! You can now:"
echo "- Login at: http://localhost:3000/login"
echo "- Search at: http://localhost:3000/search"
echo "- Analysis at: http://localhost:3000/analysis"
