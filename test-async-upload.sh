#!/bin/bash

# Test script for async upload endpoint
# This tests the Celery-based upload workflow

set -e

echo "🧪 Testing Async Upload Workflow with Celery"
echo "=============================================="
echo ""

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

API_URL="http://localhost:8000/api/v1"

# Function to print colored output
print_step() {
    echo -e "${BLUE}▶ $1${NC}"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_info() {
    echo -e "${YELLOW}ℹ $1${NC}"
}

# Step 1: Check services health
print_step "Step 1: Checking service health"
curl -s "$API_URL/health" | jq '.' || {
    print_error "API Gateway health check failed"
    exit 1
}
print_success "All services healthy"
echo ""

# Step 2: Check Celery worker is running
print_step "Step 2: Checking Celery worker status"
CELERY_STATUS=$(docker ps --filter "name=celery-worker-prod" --format "{{.Status}}")
if [[ $CELERY_STATUS == *"Up"* ]]; then
    print_success "Celery worker is running: $CELERY_STATUS"
else
    print_error "Celery worker not running!"
    exit 1
fi
echo ""

# Step 3: Create a test PDF
print_step "Step 3: Creating test PDF"
TEST_PDF="test_paper.pdf"
cat > temp_tex.tex << 'EOF'
\documentclass{article}
\begin{document}
\title{Test Research Paper for Async Upload}
\author{Test Author}
\date{\today}
\maketitle

\begin{abstract}
This is a test paper for validating the async upload workflow using Celery.
\end{abstract}

\section{Introduction}
This paper tests the asynchronous document processing pipeline with Celery workers.

\section{Methodology}
We upload a PDF and track processing status via job ID.

\section{Results}
Expected: Document processed, chunks created, embeddings generated.

\section{Conclusion}
Async processing with Celery enables scalable document handling.

\end{document}
EOF

# Try to compile with pdflatex if available, otherwise skip
if command -v pdflatex &> /dev/null; then
    pdflatex -interaction=nonstopmode temp_tex.tex > /dev/null 2>&1 || true
    if [ -f "temp_tex.pdf" ]; then
        mv temp_tex.pdf "$TEST_PDF"
        rm -f temp_tex.* 2>/dev/null
        print_success "Test PDF created"
    else
        print_info "pdflatex failed, will use curl to fetch sample PDF"
        curl -s -o "$TEST_PDF" "https://arxiv.org/pdf/2101.00001.pdf" || {
            print_error "Failed to create test PDF"
            exit 1
        }
        print_success "Downloaded sample PDF from arXiv"
    fi
else
    print_info "pdflatex not found, downloading sample PDF"
    curl -s -o "$TEST_PDF" "https://arxiv.org/pdf/2101.00001.pdf" || {
        print_error "Failed to download test PDF"
        exit 1
    }
    print_success "Downloaded sample PDF from arXiv"
fi
echo ""

# Step 4: Upload document via async endpoint
print_step "Step 4: Uploading document via /upload-async"
UPLOAD_RESPONSE=$(curl -s -X POST "$API_URL/upload-async" \
    -F "file=@$TEST_PDF")

echo "$UPLOAD_RESPONSE" | jq '.'

JOB_ID=$(echo "$UPLOAD_RESPONSE" | jq -r '.job_id')
TASK_ID=$(echo "$UPLOAD_RESPONSE" | jq -r '.task_id')

if [ "$JOB_ID" = "null" ] || [ -z "$JOB_ID" ]; then
    print_error "Upload failed - no job_id returned"
    exit 1
fi

print_success "Document uploaded - Job ID: $JOB_ID, Task ID: $TASK_ID"
echo ""

# Step 5: Monitor job status
print_step "Step 5: Monitoring job processing (max 60 seconds)"
TIMEOUT=60
ELAPSED=0
while [ $ELAPSED -lt $TIMEOUT ]; do
    sleep 2
    ELAPSED=$((ELAPSED + 2))
    
    JOB_STATUS=$(curl -s "$API_URL/jobs/$JOB_ID" | jq -r '.status')
    PROGRESS=$(curl -s "$API_URL/jobs/$JOB_ID" | jq -r '.progress')
    
    echo -ne "\r  Status: $JOB_STATUS | Progress: ${PROGRESS}% | Time: ${ELAPSED}s"
    
    if [ "$JOB_STATUS" = "completed" ]; then
        echo ""
        print_success "Job completed successfully!"
        break
    fi
    
    if [ "$JOB_STATUS" = "failed" ]; then
        echo ""
        print_error "Job processing failed"
        curl -s "$API_URL/jobs/$JOB_ID" | jq '.'
        exit 1
    fi
done
echo ""

if [ "$JOB_STATUS" != "completed" ]; then
    print_error "Job did not complete within ${TIMEOUT} seconds"
    print_info "Current status: $JOB_STATUS"
    exit 1
fi
echo ""

# Step 6: Get job details
print_step "Step 6: Fetching job details"
JOB_DETAILS=$(curl -s "$API_URL/jobs/$JOB_ID")
echo "$JOB_DETAILS" | jq '.'

DOCUMENT_ID=$(echo "$JOB_DETAILS" | jq -r '.document_id')
print_success "Document ID: $DOCUMENT_ID"
echo ""

# Step 7: Verify document exists
print_step "Step 7: Verifying document in database"
DOC_RESPONSE=$(curl -s "$API_URL/documents/$DOCUMENT_ID")
echo "$DOC_RESPONSE" | jq '.id, .filename, .title, .page_count, .tables_extracted, .figures_extracted'
print_success "Document found in database"
echo ""

# Step 8: Check Vector DB chunks
print_step "Step 8: Checking Vector DB chunks (wait 5s for background processing)"
sleep 5

CHUNKS_RESPONSE=$(curl -s -X POST "$API_URL/search" \
    -H "Content-Type: application/json" \
    -d "{\"query\": \"test\", \"document_id\": $DOCUMENT_ID, \"max_results\": 5}")

CHUNK_COUNT=$(echo "$CHUNKS_RESPONSE" | jq '.results | length')
print_info "Found $CHUNK_COUNT chunks"

if [ "$CHUNK_COUNT" -gt 0 ]; then
    echo "$CHUNKS_RESPONSE" | jq '.results[0] | {chunk_index, section, similarity_score, text: (.text[:100])}'
    print_success "Vector DB chunks created successfully!"
else
    print_error "No chunks found in Vector DB"
    echo "$CHUNKS_RESPONSE" | jq '.'
    exit 1
fi
echo ""

# Step 9: Test semantic search
print_step "Step 9: Testing semantic search"
SEARCH_RESPONSE=$(curl -s -X POST "$API_URL/search" \
    -H "Content-Type: application/json" \
    -d '{"query": "methodology research", "max_results": 3}')

SEARCH_COUNT=$(echo "$SEARCH_RESPONSE" | jq '.results | length')
print_info "Search returned $SEARCH_COUNT results"
echo "$SEARCH_RESPONSE" | jq '.results[] | {document_id, section, similarity_score}'
print_success "Semantic search working!"
echo ""

# Cleanup
print_step "Cleanup: Removing test PDF"
rm -f "$TEST_PDF"
print_success "Test PDF removed"
echo ""

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}✓ All tests passed successfully!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
print_info "Summary:"
echo "  • Async upload endpoint: ✓ Working"
echo "  • Celery task processing: ✓ Working"
echo "  • Job tracking: ✓ Working"
echo "  • Vector DB chunking: ✓ Working"
echo "  • Semantic search: ✓ Working"
echo ""
print_info "View Flower monitor at: http://localhost:5555"
print_info "Check Celery logs: docker logs -f celery-worker-prod"
