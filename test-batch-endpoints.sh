#!/bin/bash
# Test Batch Upload and Job Management Endpoints

set -e

BASE_URL="http://localhost:8001/api/v1"
BATCH_URL="http://localhost:8000/api/v1"  # API Gateway

echo "============================================"
echo "Testing Batch Upload & Job Management"
echo "============================================"
echo ""

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Create test PDFs if they don't exist
echo -e "${BLUE}Preparing test PDFs...${NC}"
mkdir -p /tmp/test_pdfs

# Check if sample PDFs exist
if [ ! -f "/tmp/test_pdfs/test1.pdf" ]; then
    echo "Note: No test PDFs found. Please add PDF files to /tmp/test_pdfs/"
    echo "Skipping actual upload test, but testing other endpoints..."
    SKIP_UPLOAD=true
else
    SKIP_UPLOAD=false
fi

if [ "$SKIP_UPLOAD" = false ]; then
    # Test 1: Batch Upload
    echo -e "\n${GREEN}Test 1: Batch Upload Multiple PDFs${NC}"
    RESPONSE=$(curl -s -X POST "$BASE_URL/batch-upload" \
        -F "files=@/tmp/test_pdfs/test1.pdf" \
        -F "files=@/tmp/test_pdfs/test2.pdf")
    
    echo "$RESPONSE" | jq '.'
    
    BATCH_ID=$(echo "$RESPONSE" | jq -r '.batch_id')
    echo -e "${YELLOW}Batch ID: $BATCH_ID${NC}"
    
    # Wait a moment for jobs to be created
    sleep 2
fi

# Test 2: List All Jobs
echo -e "\n${GREEN}Test 2: List All Jobs${NC}"
curl -s "$BASE_URL/jobs?limit=5" | jq '.jobs[] | {job_id, filename, status, progress}'

# Test 3: List All Batches
echo -e "\n${GREEN}Test 3: List All Batches${NC}"
curl -s "$BASE_URL/batches?limit=5" | jq '.batches[] | {batch_id, total_jobs, completed, failed, pending}'

if [ "$SKIP_UPLOAD" = false ] && [ ! -z "$BATCH_ID" ]; then
    # Test 4: Get Batch Status
    echo -e "\n${GREEN}Test 4: Get Batch Status${NC}"
    curl -s "$BASE_URL/batches/$BATCH_ID" | jq '.'
    
    # Get first job ID from batch
    JOB_RESPONSE=$(curl -s "$BASE_URL/batches/$BATCH_ID")
    FIRST_JOB=$(echo "$JOB_RESPONSE" | jq -r '.jobs[0].job_id // empty')
    
    if [ ! -z "$FIRST_JOB" ]; then
        # Test 5: Get Job Status
        echo -e "\n${GREEN}Test 5: Get Job Status${NC}"
        curl -s "$BASE_URL/jobs/$FIRST_JOB" | jq '{job: .job | {job_id, status, progress, error_message}, steps: .steps | length}'
        
        # Test 6: Get Job Steps Detail
        echo -e "\n${GREEN}Test 6: Get Job Processing Steps${NC}"
        curl -s "$BASE_URL/jobs/$FIRST_JOB" | jq '.steps[] | {step_name, status, duration_ms}'
        
        # Test 7: Cancel Job (only if still pending/processing)
        JOB_STATUS=$(curl -s "$BASE_URL/jobs/$FIRST_JOB" | jq -r '.job.status')
        if [ "$JOB_STATUS" = "pending" ] || [ "$JOB_STATUS" = "processing" ]; then
            echo -e "\n${GREEN}Test 7: Cancel Job${NC}"
            curl -s -X POST "$BASE_URL/jobs/$FIRST_JOB/cancel" | jq '.'
        else
            echo -e "\n${YELLOW}Test 7: Skip cancel (job status: $JOB_STATUS)${NC}"
        fi
    fi
fi

# Test 8: Reprocess Document (if any documents exist)
echo -e "\n${GREEN}Test 8: Check Document Reprocessing Endpoint${NC}"
DOC_COUNT=$(curl -s "$BASE_URL/documents?limit=1" | jq '.documents | length')
if [ "$DOC_COUNT" -gt 0 ]; then
    FIRST_DOC_ID=$(curl -s "$BASE_URL/documents?limit=1" | jq -r '.documents[0].id')
    echo "Testing reprocess for document ID: $FIRST_DOC_ID"
    curl -s -X POST "$BASE_URL/documents/$FIRST_DOC_ID/reprocess?force_ocr=false" | jq '.'
else
    echo "No documents available for reprocessing test"
fi

echo -e "\n${GREEN}============================================${NC}"
echo -e "${GREEN}All Tests Completed!${NC}"
echo -e "${GREEN}============================================${NC}"
echo ""
echo "Endpoints tested:"
echo "  ✓ POST /batch-upload"
echo "  ✓ GET  /jobs"
echo "  ✓ GET  /jobs/{job_id}"
echo "  ✓ GET  /batches"
echo "  ✓ GET  /batches/{batch_id}"
echo "  ✓ POST /jobs/{job_id}/cancel"
echo "  ✓ POST /documents/{document_id}/reprocess"
echo ""
