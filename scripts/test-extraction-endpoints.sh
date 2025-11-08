#!/bin/bash

# Test script for Document Extraction Endpoints
# Tests tables, figures, references, and figure file serving

echo "🧪 Testing Document Extraction Endpoints"
echo "=========================================="
echo ""

# Check if service is running
echo "1. Checking service health..."
response=$(curl -s http://localhost:8001/health)
if [ $? -eq 0 ]; then
    echo "✅ Service is running"
else
    echo "❌ Service is not running. Please start it first."
    exit 1
fi
echo ""

# Get the latest document ID
echo "2. Getting latest document..."
latest_doc=$(curl -s http://localhost:8001/api/v1/documents | python3 -c "import sys, json; docs = json.load(sys.stdin); print(docs[-1]['id'] if docs else 0)")
echo "📄 Latest document ID: $latest_doc"
echo ""

if [ "$latest_doc" = "0" ]; then
    echo "❌ No documents found. Please upload a PDF first."
    echo "Example: curl -X POST http://localhost:8001/api/v1/upload -F 'file=@paper.pdf'"
    exit 1
fi

# Test tables endpoint
echo "3. Testing tables extraction endpoint..."
tables=$(curl -s "http://localhost:8001/api/v1/documents/$latest_doc/tables")
table_count=$(echo "$tables" | python3 -c "import sys, json; print(len(json.load(sys.stdin)))")
echo "📊 Found $table_count tables"
if [ "$table_count" -gt 0 ]; then
    echo "Sample table:"
    echo "$tables" | python3 -m json.tool | head -30
fi
echo ""

# Test figures endpoint
echo "4. Testing figures extraction endpoint..."
figures=$(curl -s "http://localhost:8001/api/v1/documents/$latest_doc/figures")
figure_count=$(echo "$figures" | python3 -c "import sys, json; print(len(json.load(sys.stdin)))")
echo "🖼️  Found $figure_count figures"
if [ "$figure_count" -gt 0 ]; then
    echo "Sample figure metadata:"
    echo "$figures" | python3 -m json.tool | head -30
fi
echo ""

# Test references endpoint
echo "5. Testing structured references endpoint..."
references=$(curl -s "http://localhost:8001/api/v1/documents/$latest_doc/references/structured")
ref_count=$(echo "$references" | python3 -c "import sys, json; print(len(json.load(sys.stdin)))")
echo "📚 Found $ref_count references"
if [ "$ref_count" -gt 0 ]; then
    echo "Sample references:"
    echo "$references" | python3 -m json.tool | head -40
fi
echo ""

# Test figure file serving
echo "6. Testing figure file serving endpoint..."
if [ "$figure_count" -gt 0 ]; then
    first_fig_num=$(echo "$figures" | python3 -c "import sys, json; print(json.load(sys.stdin)[0]['figure_num'])")
    echo "Downloading figure $first_fig_num..."
    curl -s "http://localhost:8001/api/v1/documents/$latest_doc/figure-file/$first_fig_num" --output /tmp/test_figure.png
    file_info=$(file /tmp/test_figure.png)
    echo "✅ Downloaded: $file_info"
    rm -f /tmp/test_figure.png
else
    echo "⏭️  Skipping (no figures found)"
fi
echo ""

echo "✅ All extraction endpoint tests completed!"
echo ""
echo "📚 Extraction Summary for Document $latest_doc:"
echo "  - Tables: $table_count"
echo "  - Figures: $figure_count"
echo "  - References: $ref_count"
echo ""
echo "🌐 View in browser:"
echo "  Full document: http://localhost:8001/api/v1/documents/$latest_doc"
echo "  Tables: http://localhost:8001/api/v1/documents/$latest_doc/tables"
echo "  Figures: http://localhost:8001/api/v1/documents/$latest_doc/figures"
echo "  References: http://localhost:8001/api/v1/documents/$latest_doc/references/structured"
echo "  API Docs: http://localhost:8001/docs"
echo ""
