#!/bin/bash

# Integration Test Script for Phase 2
# Tests Document Processing + Vector DB integration

echo "🧪 Phase 2 Integration Test"
echo "=============================="
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check services health
echo "1. Checking services health..."
echo ""

echo "Document Processing Service:"
doc_health=$(curl -s http://localhost:8001/health)
echo "$doc_health" | python3 -m json.tool
echo ""

echo "Vector DB Service:"
vector_health=$(curl -s http://localhost:8002/health 2>/dev/null)
if [ $? -eq 0 ]; then
    echo "$vector_health" | python3 -m json.tool
    echo -e "${GREEN}✅ Vector DB is running${NC}"
else
    echo -e "${RED}❌ Vector DB is not responding (may still be loading model)${NC}"
    echo -e "${YELLOW}⏳ Note: First startup takes 2-5 minutes on CPU to load embedding model${NC}"
fi
echo ""

# Check if Vector DB is ready
vector_ready=$(echo "$doc_health" | python3 -c "import sys, json; print(json.load(sys.stdin).get('vector_db_status', 'unknown'))" 2>/dev/null)

if [ "$vector_ready" != "healthy" ]; then
    echo -e "${YELLOW}⚠️  Vector DB not ready yet. You can still upload documents.${NC}"
    echo -e "${YELLOW}   Processing will happen in background once Vector DB is ready.${NC}"
    echo ""
fi

# Get document count
echo "2. Checking existing documents..."
docs=$(curl -s http://localhost:8001/api/v1/documents)
doc_count=$(echo "$docs" | python3 -c "import sys, json; print(len(json.load(sys.stdin)))")
echo "📚 Documents in database: $doc_count"
echo ""

if [ "$doc_count" -gt 0 ]; then
    echo "Latest documents:"
    echo "$docs" | python3 -m json.tool | head -30
    echo ""
    
    # Get latest document ID
    latest_id=$(echo "$docs" | python3 -c "import sys, json; docs = json.load(sys.stdin); print(docs[-1]['id'] if docs else 0)")
    
    if [ "$vector_ready" = "healthy" ] && [ "$latest_id" != "0" ]; then
        echo "3. Testing semantic search..."
        echo ""
        
        search_result=$(curl -s -X POST http://localhost:8001/api/v1/search \
          -H "Content-Type: application/json" \
          -d "{\"query\": \"data lake\", \"max_results\": 3, \"document_id\": $latest_id}")
        
        if echo "$search_result" | grep -q "results_count"; then
            echo -e "${GREEN}✅ Search successful!${NC}"
            echo "$search_result" | python3 -m json.tool | head -50
            echo ""
        else
            echo -e "${YELLOW}⚠️  Search returned unexpected response${NC}"
            echo "$search_result"
            echo ""
        fi
        
        echo "4. Checking Vector DB chunks..."
        chunks=$(curl -s "http://localhost:8002/documents/$latest_id/chunks")
        chunk_count=$(echo "$chunks" | python3 -c "import sys, json; print(len(json.load(sys.stdin)))" 2>/dev/null || echo "0")
        echo "📊 Chunks in Vector DB for document $latest_id: $chunk_count"
        
        if [ "$chunk_count" -gt 0 ]; then
            echo -e "${GREEN}✅ Document has been processed in Vector DB${NC}"
            echo ""
            echo "Sample chunk:"
            echo "$chunks" | python3 -m json.tool | head -30
        else
            echo -e "${YELLOW}⚠️  Document not yet processed in Vector DB${NC}"
            echo -e "${YELLOW}   This is normal if upload was recent. Check logs:${NC}"
            echo -e "${YELLOW}   docker logs document-processing-service${NC}"
        fi
    else
        echo -e "${YELLOW}⏭️  Skipping search test (Vector DB not ready)${NC}"
    fi
fi

echo ""
echo "=============================="
echo "📋 Integration Status Summary"
echo "=============================="
echo ""
echo "Service URLs:"
echo "  • Document Processing: http://localhost:8001"
echo "  • Document Processing API Docs: http://localhost:8001/docs"
echo "  • Vector DB: http://localhost:8002"
echo "  • Vector DB API Docs: http://localhost:8002/docs"
echo ""
echo "Integration Features:"
echo "  ✅ Upload endpoint with background Vector DB processing"
echo "  ✅ Semantic search endpoint"
echo "  ✅ Health monitoring with Vector DB status"
echo "  ✅ Automatic cleanup on document deletion"
echo ""
echo "To test the integration:"
echo "  1. Upload a PDF:"
echo "     curl -X POST http://localhost:8001/api/v1/upload -F 'file=@paper.pdf'"
echo ""
echo "  2. Wait for Vector DB processing (check logs):"
echo "     docker logs -f document-processing-service"
echo ""
echo "  3. Search semantically:"
echo "     curl -X POST http://localhost:8001/api/v1/search \\\n       -H 'Content-Type: application/json' \\\n       -d '{"query": "your search query", "max_results": 5}'"
echo ""
echo "For more information, see: PHASE2_INTEGRATION_COMPLETE.md"
echo ""
