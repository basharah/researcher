#!/bin/bash

# Quick test of async upload with a simple text-based PDF

set -e

echo "🧪 Testing Async Upload with Sample PDF"
echo "========================================"

API_URL="http://localhost:8000/api/v1"

# Create a simple valid PDF using Python reportlab
echo "Creating test PDF..."
python3 - <<'PYTHON'
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

pdf_file = "sample_paper.pdf"
c = canvas.Canvas(pdf_file, pagesize=letter)

# Add title
c.setFont("Helvetica-Bold", 24)
c.drawString(100, 750, "Test Research Paper")

# Add author
c.setFont("Helvetica", 14)
c.drawString(100, 720, "Author: Test Author")

# Add abstract
c.setFont("Helvetica-Bold", 16)
c.drawString(100, 680, "Abstract")
c.setFont("Helvetica", 12)
c.drawString(100, 660, "This is a test paper for validating the async upload workflow.")
c.drawString(100, 645, "It tests Celery-based background processing of PDFs.")

# Add sections
c.setFont("Helvetica-Bold", 16)
c.drawString(100, 600, "1. Introduction")
c.setFont("Helvetica", 12)
c.drawString(100, 580, "Machine learning has revolutionized natural language processing.")
c.drawString(100, 565, "This paper explores transformer architectures for document analysis.")

c.setFont("Helvetica-Bold", 16)
c.drawString(100, 530, "2. Methodology")
c.setFont("Helvetica", 12)
c.drawString(100, 510, "We use sentence transformers for embedding generation.")
c.drawString(100, 495, "Vector databases enable semantic search capabilities.")

c.setFont("Helvetica-Bold", 16)
c.drawString(100, 460, "3. Results")
c.setFont("Helvetica", 12)
c.drawString(100, 440, "The system successfully processes PDFs and creates embeddings.")
c.drawString(100, 425, "Search queries return relevant chunks with high accuracy.")

c.setFont("Helvetica-Bold", 16)
c.drawString(100, 390, "4. Conclusion")
c.setFont("Helvetica", 12)
c.drawString(100, 370, "Async processing with Celery enables scalable document handling.")

c.save()
print(f"✓ Created {pdf_file}")
PYTHON

echo ""

# Upload
echo "Uploading via /upload-async..."
RESPONSE=$(curl -s -X POST "$API_URL/upload-async" -F "file=@sample_paper.pdf")
echo "$RESPONSE" | jq '.'

JOB_ID=$(echo "$RESPONSE" | jq -r '.job_id')

if [ "$JOB_ID" = "null" ]; then
    echo "✗ Upload failed"
    exit 1
fi

echo "✓ Job ID: $JOB_ID"
echo ""

# Wait and check status
echo "Waiting for processing (30s max)..."
for i in {1..15}; do
    sleep 2
    STATUS=$(curl -s "$API_URL/jobs/$JOB_ID" | jq -r '.status')
    PROGRESS=$(curl -s "$API_URL/jobs/$JOB_ID" | jq -r '.progress // 0')
    echo "  [$i] Status: $STATUS | Progress: ${PROGRESS}%"
    
    if [ "$STATUS" = "completed" ]; then
        echo "✓ Processing completed!"
        break
    fi
    
    if [ "$STATUS" = "failed" ]; then
        echo "✗ Processing failed"
        curl -s "$API_URL/jobs/$JOB_ID" | jq '.'
        exit 1
    fi
done

echo ""

# Get document ID
DOC_ID=$(curl -s "$API_URL/jobs/$JOB_ID" | jq -r '.document_id')
echo "Document ID: $DOC_ID"

echo ""
echo "Checking Vector DB chunks (wait 5s)..."
sleep 5

CHUNKS=$(curl -s -X POST "$API_URL/search" \
    -H "Content-Type: application/json" \
    -d "{\"query\": \"methodology\", \"document_id\": $DOC_ID, \"max_results\": 3}")

COUNT=$(echo "$CHUNKS" | jq '.results | length')
echo "Found $COUNT chunks"

if [ "$COUNT" -gt 0 ]; then
    echo "$CHUNKS" | jq '.results[] | {section, similarity_score, text: (.text[:80])}'
    echo ""
    echo "✓ SUCCESS! Async upload workflow working!"
else
    echo "✗ No chunks found"
    echo "$CHUNKS" | jq '.'
fi

rm -f sample_paper.pdf
