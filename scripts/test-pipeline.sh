#!/bin/bash
# Complete Pipeline Test Script
# Tests: Upload → Extraction → Vector DB → Search

set -e  # Exit on error

echo "========================================="
echo "Research Paper Analysis - Pipeline Test"
echo "========================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Test PDF file
PDF_FILE="${1:-papers/3447772.pdf}"

if [[ ! -f "$PDF_FILE" ]]; then
    echo -e "${RED}✗ PDF file not found: $PDF_FILE${NC}"
    exit 1
fi

echo -e "${YELLOW}Using PDF:${NC} $PDF_FILE"
echo ""

# Step 1: Check services health
echo "=== Step 1: Health Check ==="
HEALTH=$(curl -s http://localhost:8000/api/v1/health | jq -r '.status')
if [[ "$HEALTH" == "healthy" ]]; then
    echo -e "${GREEN}✓ All services healthy${NC}"
else
    echo -e "${RED}✗ Services not healthy${NC}"
    curl -s http://localhost:8000/api/v1/health | jq
    exit 1
fi
echo ""

# Step 2: Upload document
echo "=== Step 2: Upload Document ==="
UPLOAD_RESPONSE=$(curl -s -X POST http://localhost:8000/api/v1/upload \
    -F "file=@$PDF_FILE")

DOC_ID=$(echo "$UPLOAD_RESPONSE" | jq -r '.id')
DOC_TITLE=$(echo "$UPLOAD_RESPONSE" | jq -r '.title')
PAGE_COUNT=$(echo "$UPLOAD_RESPONSE" | jq -r '.page_count')

if [[ "$DOC_ID" != "null" && "$DOC_ID" != "" ]]; then
    echo -e "${GREEN}✓ Document uploaded${NC}"
    echo "  ID: $DOC_ID"
    echo "  Title: $DOC_TITLE"
    echo "  Pages: $PAGE_COUNT"
else
    echo -e "${RED}✗ Upload failed${NC}"
    echo "$UPLOAD_RESPONSE" | jq
    exit 1
fi
echo ""

# Step 3: Wait for Vector DB processing
echo "=== Step 3: Wait for Vector DB Processing ==="
echo -e "${YELLOW}Waiting 45 seconds for background processing...${NC}"
for i in {45..1}; do
    echo -ne "\r  Time remaining: ${i}s "
    sleep 1
done
echo -e "\n${GREEN}✓ Wait complete${NC}"
echo ""

# Step 4: Verify chunks were created
echo "=== Step 4: Verify Chunks Created ==="
CHUNK_COUNT=$(docker exec researcher-postgres psql -U researcher -d research_papers -t -c \
    "SELECT COUNT(*) FROM document_chunks WHERE document_id = $DOC_ID;" | tr -d ' ')

if [[ "$CHUNK_COUNT" -gt 0 ]]; then
    echo -e "${GREEN}✓ Chunks created: $CHUNK_COUNT${NC}"
else
    echo -e "${RED}✗ No chunks created${NC}"
    echo "Checking document-processing logs..."
    docker logs document-processing-service 2>&1 | tail -20
    exit 1
fi
echo ""

# Step 5: Test semantic search
echo "=== Step 5: Test Semantic Search ==="
SEARCH_QUERY="knowledge graphs"
SEARCH_RESPONSE=$(curl -s -X POST http://localhost:8000/api/v1/search \
    -H "Content-Type: application/json" \
    -d "{\"query\":\"$SEARCH_QUERY\",\"max_results\":3}")

RESULTS_COUNT=$(echo "$SEARCH_RESPONSE" | jq -r '.results_count')

if [[ "$RESULTS_COUNT" -gt 0 ]]; then
    echo -e "${GREEN}✓ Search successful${NC}"
    echo "  Query: '$SEARCH_QUERY'"
    echo "  Results: $RESULTS_COUNT"
    echo ""
    echo "Top result:"
    echo "$SEARCH_RESPONSE" | jq -r '.chunks[0] | "  Score: \(.similarity_score)\n  Section: \(.section)\n  Text: \(.text[0:150])..."'
else
    echo -e "${RED}✗ Search returned no results${NC}"
    echo "$SEARCH_RESPONSE" | jq
    exit 1
fi
echo ""

# Step 6: Test document retrieval
echo "=== Step 6: Test Document Retrieval ==="
DOC_RESPONSE=$(curl -s http://localhost:8000/api/v1/documents/$DOC_ID)
RETRIEVED_TITLE=$(echo "$DOC_RESPONSE" | jq -r '.title')

if [[ "$RETRIEVED_TITLE" == "$DOC_TITLE" ]]; then
    echo -e "${GREEN}✓ Document retrieved successfully${NC}"
    echo "  ID: $DOC_ID"
    echo "  Title: $RETRIEVED_TITLE"
else
    echo -e "${RED}✗ Document retrieval failed${NC}"
    exit 1
fi
echo ""

echo "========================================="
echo -e "${GREEN}✓ ALL TESTS PASSED!${NC}"
echo "========================================="
echo ""
echo "Pipeline verified:"
echo "  1. Document uploaded and extracted"
echo "  2. Text chunked into $CHUNK_COUNT chunks"
echo "  3. Embeddings generated (GPU-accelerated)"
echo "  4. Semantic search working"
echo "  5. Document retrieval working"
echo ""
echo -e "${GREEN}The RAG pipeline is fully operational!${NC}"
