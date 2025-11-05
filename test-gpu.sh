#!/bin/bash

# Quick GPU Test - Upload a paper and verify GPU acceleration

echo "🚀 Quick GPU Acceleration Test"
echo "==============================="
echo ""

# Check if vector-db is running
if ! docker ps | grep -q vector-db-service; then
    echo "📦 Vector DB not running. Starting services..."
    docker-compose build vector-db
    docker-compose up -d vector-db
    echo "⏳ Waiting 30 seconds for service to initialize..."
    sleep 30
fi

# Check GPU status in logs
echo "1. Checking GPU Status..."
docker logs vector-db-service 2>&1 | grep -E "Device:|GPU:|CUDA" | tail -5
echo ""

# Find a test PDF
TEST_PDF=$(find uploads_data -name "*.pdf" -type f | head -1)

if [ -z "$TEST_PDF" ]; then
    echo "❌ No PDF found in uploads_data/"
    echo "   Please add a test PDF to uploads_data/ and try again"
    exit 1
fi

echo "2. Testing with PDF: $(basename "$TEST_PDF")"
echo ""

# Monitor GPU during upload
echo "3. Starting GPU monitoring (Ctrl+C to stop)..."
echo "   Watch for GPU utilization to spike during embedding generation"
echo ""

# Upload in background and monitor GPU
echo "Uploading PDF..."
start_time=$(date +%s)

curl -X POST -F "file=@$TEST_PDF" http://localhost:8001/api/v1/upload -o /tmp/upload_result.json 2>/dev/null &
upload_pid=$!

# Monitor GPU for 10 seconds
for i in {1..10}; do
    nvidia-smi --query-gpu=utilization.gpu,utilization.memory,memory.used --format=csv,noheader
    sleep 1
done

wait $upload_pid
end_time=$(date +%s)
duration=$((end_time - start_time))

echo ""
echo "4. Results:"
echo "   Upload completed in ${duration} seconds"
echo ""

# Check Vector DB logs
echo "5. Vector DB Processing:"
docker logs vector-db-service 2>&1 | tail -10

echo ""
echo "✅ Test Complete!"
echo ""
echo "Expected GPU behavior:"
echo "- GPU utilization should spike during embedding generation"
echo "- Memory usage should increase temporarily"
echo "- Check logs for 'Device: cuda' confirmation"
