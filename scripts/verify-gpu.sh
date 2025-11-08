#!/bin/bash

# GPU Verification Script
# Checks if GPU is properly configured for Docker services

echo "🔍 GPU Configuration Verification"
echo "=================================="
echo ""

# Check NVIDIA driver
echo "1. Checking NVIDIA Driver..."
if command -v nvidia-smi &> /dev/null; then
    nvidia-smi --query-gpu=name,driver_version,memory.total --format=csv,noheader
    echo "✅ NVIDIA Driver installed"
else
    echo "❌ nvidia-smi not found. Install NVIDIA drivers first."
    exit 1
fi
echo ""

# Check Docker GPU support
echo "2. Checking Docker GPU Support..."
if docker run --rm --gpus all nvidia/cuda:12.1.0-base-ubuntu22.04 nvidia-smi &> /dev/null; then
    echo "✅ Docker can access GPU"
else
    echo "❌ Docker cannot access GPU"
    echo "   Install NVIDIA Container Toolkit:"
    echo "   https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/install-guide.html"
    exit 1
fi
echo ""

# Check Docker Compose version
echo "3. Checking Docker Compose Version..."
compose_version=$(docker-compose --version | grep -oP '\\d+\\.\\d+\\.\\d+' | head -1)
echo "Docker Compose version: $compose_version"
if [ "$(printf '%s\n' "1.28.0" "$compose_version" | sort -V | head -n1)" = "1.28.0" ]; then
    echo "✅ Docker Compose version supports GPU (≥1.28)"
else
    echo "⚠️  Docker Compose version <1.28 may not support deploy.resources"
fi
echo ""

# Test PyTorch in container
echo "4. Testing PyTorch GPU Access..."
cat > /tmp/test_gpu.py << 'EOF'
import torch
print(f"PyTorch version: {torch.__version__}")
print(f"CUDA available: {torch.cuda.is_available()}")
if torch.cuda.is_available():
    print(f"CUDA version: {torch.version.cuda}")
    print(f"GPU count: {torch.cuda.device_count()}")
    print(f"GPU 0: {torch.cuda.get_device_name(0)}")
    print(f"GPU memory: {torch.cuda.get_device_properties(0).total_memory / 1024**3:.2f} GB")
else:
    print("❌ CUDA not available in PyTorch")
    exit(1)
EOF

if docker run --rm --gpus all -v /tmp/test_gpu.py:/test_gpu.py python:3.11-slim \
    bash -c "pip install -q torch==2.2.0 && python /test_gpu.py" 2>&1; then
    echo "✅ PyTorch can access GPU in Docker"
else
    echo "❌ PyTorch cannot access GPU in Docker"
    exit 1
fi
echo ""

# Check if vector-db service is running with GPU
echo "5. Checking Vector DB Service GPU Status..."
if docker ps | grep -q vector-db-service; then
    echo "Vector DB service is running. Checking logs..."
    docker logs vector-db-service 2>&1 | grep -E "Device:|GPU:|CUDA" | tail -5
    echo ""
    if docker logs vector-db-service 2>&1 | grep -q "Device: cuda"; then
        echo "✅ Vector DB is using GPU"
    else
        echo "⚠️  Vector DB is using CPU (check logs above)"
    fi
else
    echo "ℹ️  Vector DB service not running. Start with:"
    echo "   docker-compose up -d vector-db"
fi
echo ""

echo "=================================="
echo "✅ GPU Configuration Complete!"
echo ""
echo "Tips:"
echo "- Monitor GPU usage: watch -n 1 nvidia-smi"
echo "- Vector DB logs: docker logs -f vector-db-service"
echo "- Embedding speedup: ~10-50x faster with GPU"
