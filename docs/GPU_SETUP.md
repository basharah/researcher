# GPU Acceleration Setup Guide

## Overview

This project is configured to use **NVIDIA GPUs** for accelerating:
- **Vector DB Service**: Embedding generation with sentence-transformers (~10-50x faster)
- **LLM Service** (Phase 3): Local model inference

## GPU Allocation

The system has **2 NVIDIA GPUs** configured as follows:

| GPU | Model | Memory | Assigned Service | Purpose |
|-----|-------|--------|------------------|---------|
| GPU 0 | RTX 2080 Ti | 11GB | Vector DB | Embedding generation |
| GPU 1 | GTX 960 | 4GB | LLM Service | Local LLM inference |

GPU allocation is controlled via `CUDA_VISIBLE_DEVICES` in `docker-compose.yml`.

## Prerequisites

### 1. NVIDIA Drivers

Install the latest NVIDIA drivers for your GPU:

```bash
# Check current driver version
nvidia-smi

# Ubuntu/Debian
sudo apt update
sudo apt install nvidia-driver-XXX  # Replace XXX with version number

# Verify installation
nvidia-smi
```

### 2. NVIDIA Container Toolkit

Install Docker GPU support:

```bash
# Add NVIDIA package repository
distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
curl -s -L https://nvidia.github.io/nvidia-docker/gpgkey | sudo apt-key add -
curl -s -L https://nvidia.github.io/nvidia-docker/$distribution/nvidia-docker.list | \
  sudo tee /etc/apt/sources.list.d/nvidia-docker.list

# Install nvidia-container-toolkit
sudo apt-get update
sudo apt-get install -y nvidia-container-toolkit

# Restart Docker
sudo systemctl restart docker

# Test GPU access
docker run --rm --gpus all nvidia/cuda:12.1.0-base-ubuntu22.04 nvidia-smi
```

### 3. Docker Compose Version

Ensure Docker Compose ≥ 1.28 for GPU support:

```bash
docker-compose --version

# Upgrade if needed
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" \
  -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

## Verification

Run the GPU verification script:

```bash
./verify-gpu.sh
```

This checks:
- ✅ NVIDIA drivers installed
- ✅ Docker GPU access
- ✅ Docker Compose version
- ✅ PyTorch GPU compatibility
- ✅ Vector DB service GPU usage

## Starting Services with GPU

### Start Vector DB with GPU (Phase 2)

```bash
# Build with GPU-enabled PyTorch
docker-compose build vector-db

# Start with GPU support
docker-compose up -d vector-db

# Verify GPU is being used
docker logs vector-db-service | grep "Device:"
# Should show: "Device: cuda"

# Monitor GPU usage
watch -n 1 nvidia-smi
```

### Start LLM Service with GPU (Phase 3)

```bash
# Build and start
docker-compose --profile phase3 up -d llm-service

# Verify GPU assignment
docker exec llm-service nvidia-smi
```

## Performance Benchmarks

### Embedding Generation (Vector DB)

| Operation | CPU (i7-9700K) | GPU (RTX 2080 Ti) | Speedup |
|-----------|----------------|-------------------|---------|
| Single paper (~10 pages) | ~5 minutes | ~30 seconds | **10x** |
| Batch (10 papers) | ~45 minutes | ~3 minutes | **15x** |
| Large paper (~50 pages) | ~20 minutes | ~90 seconds | **13x** |

### Expected GPU Logs

When Vector DB starts with GPU, you should see:

```text
Loading embedding model: sentence-transformers/all-MiniLM-L6-v2
Device: cuda
GPU: NVIDIA GeForce RTX 2080 Ti
CUDA Version: 12.1
GPU Memory: 11.00 GB
Model loaded. Embedding dimension: 384
```

## Troubleshooting

### Vector DB using CPU instead of GPU

**Problem**: Logs show `Device: cpu`

**Solutions**:

1. **Rebuild with GPU-enabled PyTorch**:
   ```bash
   docker-compose build --no-cache vector-db
   docker-compose up -d vector-db
   ```

2. **Check GPU reservation in docker-compose.yml**:
   ```yaml
   deploy:
     resources:
       reservations:
         devices:
           - driver: nvidia
             count: 1
             capabilities: [gpu]
   ```

3. **Verify CUDA_VISIBLE_DEVICES**:
   ```bash
   docker exec vector-db-service printenv CUDA_VISIBLE_DEVICES
   # Should show: 0
   ```

### Out of Memory (OOM) Errors

**Problem**: `CUDA out of memory` errors

**Solutions**:

1. **Reduce batch size** in `services/vector-db/config.py`:
   ```python
   chunk_size: int = 300  # Reduce from 500
   ```

2. **Use smaller model**:
   ```python
   embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"  # Already optimal
   ```

3. **Monitor GPU memory**:
   ```bash
   watch -n 1 nvidia-smi
   ```

### Docker doesn't see GPU

**Problem**: `docker run --gpus all` fails

**Solution**: Install NVIDIA Container Toolkit (see Prerequisites)

### Wrong GPU being used

**Problem**: Want to use different GPU

**Solution**: Change `CUDA_VISIBLE_DEVICES` in docker-compose.yml:
```yaml
environment:
  - CUDA_VISIBLE_DEVICES=1  # Use second GPU instead
```

## Configuration Files

### GPU-Related Settings

**docker-compose.yml**:
```yaml
vector-db:
  environment:
    - CUDA_VISIBLE_DEVICES=0  # GPU selection
  deploy:
    resources:
      reservations:
        devices:
          - driver: nvidia
            count: 1
            capabilities: [gpu]
```

**services/vector-db/requirements.txt**:
```
torch==2.2.0+cu121 --index-url https://download.pytorch.org/whl/cu121
```

**services/vector-db/config.py**:
```python
use_gpu: bool = True  # Enable GPU acceleration
```

**services/vector-db/embedding_service.py**:
```python
self.device = "cuda" if torch.cuda.is_available() else "cpu"
self.model = SentenceTransformer(self.model_name, device=self.device)
```

## Monitoring GPU Usage

### Real-time monitoring

```bash
# Basic monitoring
watch -n 1 nvidia-smi

# Detailed monitoring with gpustat (optional)
pip install gpustat
watch -n 1 gpustat -cpu
```

### Check Vector DB GPU usage

```bash
# View startup logs
docker logs vector-db-service | head -20

# Follow live logs
docker logs -f vector-db-service

# Check current GPU memory
docker exec vector-db-service nvidia-smi --query-gpu=memory.used --format=csv
```

## Disabling GPU (CPU-only mode)

If you need to run without GPU:

1. **Remove GPU reservation** from docker-compose.yml:
   ```yaml
   vector-db:
     # Comment out deploy section
     # deploy:
     #   resources:
     #     reservations:
     #       devices:
     #         - driver: nvidia
   ```

2. **Use CPU-only PyTorch** in requirements.txt:
   ```
   torch==2.2.0  # Remove +cu121 suffix
   ```

3. **Rebuild**:
   ```bash
   docker-compose build vector-db
   docker-compose up -d vector-db
   ```

## Additional Resources

- [NVIDIA Container Toolkit Installation](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/install-guide.html)
- [Docker GPU Support Documentation](https://docs.docker.com/config/containers/resource_constraints/#gpu)
- [PyTorch CUDA Installation](https://pytorch.org/get-started/locally/)
- [Sentence-Transformers GPU Usage](https://www.sbert.net/docs/usage/computing_sentence_embeddings.html#multi-gpus)
