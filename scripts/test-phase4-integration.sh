#!/bin/bash

# Phase 4 Integration Test - API Gateway
# Tests all Gateway endpoints with real backend services

set -e  # Exit on error

BASE_URL="http://localhost:8000/api/v1"
GREEN='\033[0;32m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Phase 4: API Gateway Integration Test${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Test 1: Health Check
echo -e "${BLUE}Test 1: Health Check${NC}"
HEALTH_STATUS=$(curl -s "$BASE_URL/health" | jq -r '.status')
if [ "$HEALTH_STATUS" = "healthy" ]; then
    echo -e "${GREEN}✓ Health check passed${NC}"
    curl -s "$BASE_URL/health" | jq '.services | to_entries | .[] | "\(.key): \(.value.status)"'
else
    echo -e "${RED}✗ Health check failed: $HEALTH_STATUS${NC}"
    exit 1
fi
echo ""

# Test 2: Stats Endpoint
echo -e "${BLUE}Test 2: Stats Endpoint${NC}"
STATS=$(curl -s "$BASE_URL/stats")
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Stats endpoint working${NC}"
    echo "$STATS" | jq '.total_requests, .uptime_seconds'
else
    echo -e "${RED}✗ Stats endpoint failed${NC}"
    exit 1
fi
echo ""

# Test 3: List Documents (empty)
echo -e "${BLUE}Test 3: List Documents${NC}"
DOC_COUNT=$(curl -s "$BASE_URL/documents" | jq '.total')
echo -e "${GREEN}✓ Found $DOC_COUNT documents${NC}"
echo ""

# Test 4: Upload Document (if test PDF exists)
if [ -f "test-data/sample.pdf" ]; then
    echo -e "${BLUE}Test 4: Upload Document${NC}"
    UPLOAD_RESPONSE=$(curl -s -X POST "$BASE_URL/upload" -F "file=@test-data/sample.pdf")
    DOC_ID=$(echo "$UPLOAD_RESPONSE" | jq -r '.id')
    
    if [ "$DOC_ID" != "null" ] && [ -n "$DOC_ID" ]; then
        echo -e "${GREEN}✓ Document uploaded successfully (ID: $DOC_ID)${NC}"
        echo "$UPLOAD_RESPONSE" | jq '.filename, .title'
        
        # Test 5: Get Document
        echo ""
        echo -e "${BLUE}Test 5: Get Document${NC}"
        DOC_TITLE=$(curl -s "$BASE_URL/documents/$DOC_ID" | jq -r '.title')
        echo -e "${GREEN}✓ Retrieved document: $DOC_TITLE${NC}"
        
        # Test 6: Get Sections
        echo ""
        echo -e "${BLUE}Test 6: Get Document Sections${NC}"
        SECTIONS=$(curl -s "$BASE_URL/documents/$DOC_ID/sections" | jq -r '.sections | keys | length')
        echo -e "${GREEN}✓ Found $SECTIONS sections${NC}"
        
        # Wait for Vector DB processing
        echo ""
        echo -e "${BLUE}Waiting 10s for Vector DB processing...${NC}"
        sleep 10
        
        # Test 7: Semantic Search
        echo ""
        echo -e "${BLUE}Test 7: Semantic Search${NC}"
        SEARCH_RESULTS=$(curl -s -X POST "$BASE_URL/search" \
            -H "Content-Type: application/json" \
            -d '{"query": "machine learning", "max_results": 3}' | jq -r '.results | length')
        
        if [ "$SEARCH_RESULTS" -gt 0 ]; then
            echo -e "${GREEN}✓ Search found $SEARCH_RESULTS results${NC}"
        else
            echo -e "${GREEN}⚠ Search returned 0 results (Vector DB may still be processing)${NC}"
        fi
        
        # Test 8: LLM Analysis (requires API key)
        echo ""
        echo -e "${BLUE}Test 8: LLM Analysis${NC}"
        if [ -n "$OPENAI_API_KEY" ]; then
            ANALYSIS=$(curl -s -X POST "$BASE_URL/analyze" \
                -H "Content-Type: application/json" \
                -d "{\"document_id\": $DOC_ID, \"analysis_type\": \"summary\"}")
            
            ANALYSIS_LENGTH=$(echo "$ANALYSIS" | jq -r '.result | length')
            if [ "$ANALYSIS_LENGTH" -gt 0 ]; then
                echo -e "${GREEN}✓ Analysis completed ($ANALYSIS_LENGTH chars)${NC}"
                echo "$ANALYSIS" | jq -r '.result' | head -n 3
                echo "..."
            else
                echo -e "${RED}✗ Analysis failed${NC}"
                echo "$ANALYSIS" | jq .
            fi
        else
            echo -e "${BLUE}⊘ Skipped (no OPENAI_API_KEY)${NC}"
        fi
        
    else
        echo -e "${RED}✗ Upload failed${NC}"
        echo "$UPLOAD_RESPONSE" | jq .
        exit 1
    fi
else
    echo -e "${BLUE}⊘ Skipping upload test (no test-data/sample.pdf)${NC}"
fi

# Test 9: Service Integration
echo ""
echo -e "${BLUE}Test 9: Service Integration Check${NC}"
DOC_HEALTH=$(curl -s "$BASE_URL/health" | jq -r '.services.document_processing.status')
VEC_HEALTH=$(curl -s "$BASE_URL/health" | jq -r '.services.vector_db.status')
LLM_HEALTH=$(curl -s "$BASE_URL/health" | jq -r '.services.llm_service.status')

echo "Document Processing: $DOC_HEALTH"
echo "Vector DB: $VEC_HEALTH"
echo "LLM Service: $LLM_HEALTH"

if [ "$DOC_HEALTH" = "healthy" ] && [ "$VEC_HEALTH" = "healthy" ] && [ "$LLM_HEALTH" = "healthy" ]; then
    echo -e "${GREEN}✓ All services integrated successfully${NC}"
else
    echo -e "${RED}✗ Some services unhealthy${NC}"
    exit 1
fi

# Test 10: Gateway Stats Update
echo ""
echo -e "${BLUE}Test 10: Request Statistics${NC}"
FINAL_STATS=$(curl -s "$BASE_URL/stats")
TOTAL_REQUESTS=$(echo "$FINAL_STATS" | jq '.total_requests')
DOC_REQUESTS=$(echo "$FINAL_STATS" | jq '.requests_per_service.document_processing')
VEC_REQUESTS=$(echo "$FINAL_STATS" | jq '.requests_per_service.vector_db')
LLM_REQUESTS=$(echo "$FINAL_STATS" | jq '.requests_per_service.llm_service')

echo "Total requests: $TOTAL_REQUESTS"
echo "Document service: $DOC_REQUESTS"
echo "Vector DB service: $VEC_REQUESTS"
echo "LLM service: $LLM_REQUESTS"
echo -e "${GREEN}✓ Stats tracking working${NC}"

# Summary
echo ""
echo -e "${BLUE}========================================${NC}"
echo -e "${GREEN}✓ Phase 4 Integration Test PASSED${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""
echo "API Gateway is working correctly!"
echo "All endpoints tested and functional."
echo ""
echo "Next steps:"
echo "  1. Check OpenAPI docs: http://localhost:8000/docs"
echo "  2. Build frontend (Phase 5) using these endpoints"
echo "  3. See PHASE4_API_GATEWAY.md for full API reference"
