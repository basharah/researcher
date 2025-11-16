# Docker Optimization Summary

## Changes Made

### 1. **Optimized Dockerfiles with Multi-Stage Builds**
All service Dockerfiles now use multi-stage builds:
- **Builder stage**: Installs build dependencies and Python packages
- **Final stage**: Only includes runtime dependencies and installed packages
- **Result**: Smaller final images, faster builds with layer caching

### 2. **Non-Root User Security**
All services now run as non-root user `appuser` (UID 1000):
- User created in Dockerfile
- All files owned by `appuser:appuser`
- Volume mounts won't create root-owned files
- **Security benefit**: Reduced attack surface

### 3. **Build Optimization**
- Virtual environment (`/opt/venv`) for isolated Python packages
- Proper layer caching (dependencies installed before code copy)
- Build dependencies removed from final image
- `--no-install-recommends` for apt packages

### 4. **File Ownership**
Docker Compose now specifies `user: "1000:1000"` for all services:
- Matches the `appuser` UID/GID in Dockerfiles
- Mounted volumes will be owned by host user (UID 1000)
- No more root-owned files in your workspace

## Dockerfile Structure

```dockerfile
# Stage 1: Builder
FROM python:3.11-slim as builder
- Install build dependencies
- Create virtual environment
- Install Python packages

# Stage 2: Final
FROM python:3.11-slim as final
- Install only runtime dependencies
- Copy virtual environment from builder
- Create non-root user
- Set ownership and permissions
- Switch to non-root user
```

## Performance Improvements

1. **Layer Caching**: Requirements installed separately from code
2. **Smaller Images**: Build tools not included in final image
3. **Faster Rebuilds**: Only changed layers rebuild
4. **Parallel Builds**: Multiple stages can build in parallel

## Security Improvements

1. **Non-Root Execution**: All services run as UID 1000
2. **Minimal Attack Surface**: Only runtime dependencies included
3. **Read-Only Filesystem Compatible**: Services don't need write access to /app (except uploads)

## File Locations

- `services/document-processing/Dockerfile` - Optimized with PDF/OCR tools
- `services/vector-db/Dockerfile` - Optimized with CUDA support
- `services/api-gateway/Dockerfile` - Optimized minimal image
- `services/llm-service/Dockerfile` - Optimized minimal image
- `services/base.Dockerfile` - Base template (reference)

Old Dockerfiles backed up as `Dockerfile.old` in each service directory.

## Testing

Run the new pipeline test:
```bash
./test-pipeline.sh papers/3447772.pdf
```

This will verify:
- Document upload and extraction
- Background Vector DB processing
- Chunk creation with embeddings
- Semantic search functionality
- Document retrieval

## Rebuild Instructions

```bash
# Clean rebuild with new Dockerfiles
docker-compose down -v
docker system prune -af
docker-compose build --no-cache
docker-compose --profile phase4 up -d

# Wait for services to be ready (Vector DB downloads model)
sleep 30

# Initialize database
docker exec api-gateway-service python /app/create_tables.py
docker exec api-gateway-service python /app/init_admin.py

# Test the pipeline
./test-pipeline.sh
```

## Code Inconsistencies Fixed

1. **BackgroundTasks**: Fixed parameter order in upload endpoint (non-default before default params)
2. **Vector DB URLs**: All services consistently use `http://vector-db:8000`
3. **API Routes**: All endpoints properly prefixed with `/api/v1/`
4. **User Permissions**: Consistent UID/GID across all services (1000:1000)

## Known Issues Resolved

- ❌ **Background tasks not executing** → Fixed parameter ordering
- ❌ **Root-owned files in mounted volumes** → Non-root user
- ❌ **Slow builds** → Multi-stage with caching
- ❌ **Large images** → Build deps removed from final stage
