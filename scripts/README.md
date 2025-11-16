# Scripts Directory

Utility and integration scripts for the Research Paper Analysis Chatbot. Run all scripts from the repository root.

## 🚀 Startup Scripts

### `start.sh`

Migration-first startup for the full development stack.

```bash
./scripts/start.sh
```

Starts all services with automatic database migrations.

## 🧪 Integration Test Scripts

### Core Integration Tests

- **`test-phase2-integration.sh`** - Document Processing ↔ Vector DB integration test
  - Tests document upload, vector embedding, and semantic search
  - Validates GPU acceleration (if available)

- **`test-phase4-integration.sh`** - API Gateway end-to-end checks
  - Tests unified API endpoints through the gateway
  - Validates service orchestration and health aggregation

### Feature-Specific Tests

- **`test-extraction-endpoints.sh`** - PDF extraction validation
  - Tests table, figure, and reference extraction
  - Validates metadata and section detection

- **`test-auth-postgresql.sh`** - Authentication flow test
  - Tests user registration, login, and token management
  - Validates PostgreSQL user storage

### Service Tests

- **`test-service.sh`** - Basic document-processing service test
  - Simple health check and document upload
  - Useful for quick service validation

## 🎯 Functional Test Scripts

### Upload & Processing

- **`test-async-upload.sh`** - Async document upload workflow
  - Tests background job processing with Celery
  - Validates job status tracking

- **`test-quick-async.sh`** - Quick async workflow test
  - Lightweight async processing test
  - Faster alternative to full async test

- **`test-batch-endpoints.sh`** - Batch upload endpoints
  - Tests multiple document upload
  - Validates batch job management

- **`simple-upload.sh`** - Simple document upload
  - Quick single-file upload test
  - Usage: `./scripts/simple-upload.sh <file.pdf> [password]`

- **`upload-test-papers.sh`** - Upload multiple test papers
  - Bulk upload for testing and development
  - Populates database with sample papers

### Analysis & Search

- **`test-pipeline.sh`** - Full analysis pipeline test
  - End-to-end: upload → extract → embed → search → analyze
  - Comprehensive system validation

- **`test-section-detection.sh`** - Section detection test
  - Tests advanced section parsing
  - Validates abstract, introduction, methodology, etc.

- **`test-cookie-auth.sh`** - Cookie-based authentication
  - Tests session management
  - Validates auth cookies

## 🔧 GPU & Performance Scripts

- **`verify-gpu.sh`** - GPU environment verification
  - Checks NVIDIA drivers and Docker GPU support
  - Validates container GPU access

- **`test-gpu.sh`** - GPU embedding workload test
  - Tests sentence-transformers with GPU
  - Measures performance improvement

## 🛠️ Utility Scripts

- **`clean-deploy.sh`** - Clean deployment
  - Removes containers, volumes, and images
  - Fresh start for troubleshooting

## 📝 Usage Notes

### Prerequisites

- Docker and Docker Compose installed
- Services running (`./scripts/start.sh` or `./start-prod.sh`)
- API keys in `.env` file (for LLM tests)
- NVIDIA Container Toolkit (for GPU tests)

### Running Tests

Most test scripts expect services to be running:

```bash
# Start services first
./scripts/start.sh

# Then run tests
./scripts/test-phase2-integration.sh
./scripts/test-extraction-endpoints.sh
```

### GPU Tests

GPU-related tests require proper setup:

```bash
# Verify GPU setup first
./scripts/verify-gpu.sh

# Then test GPU functionality
./scripts/test-gpu.sh
```

See `docs/GPU_SETUP.md` for complete GPU configuration.

### Authentication Tests

Auth tests may require user creation:

```bash
# Test auth flow (creates test user)
./scripts/test-auth-postgresql.sh
```

## 🔗 Related Documentation

- **Testing Overview**: `../tests/README.md` - Python unit and integration tests
- **GPU Setup**: `../docs/GPU_SETUP.md` - Complete GPU configuration guide
- **Authentication**: `../docs/AUTHENTICATION_GUIDE.md` - Auth system documentation
- **Deployment**: `../docs/DEPLOYMENT_COMPLETE.md` - Production deployment guide

---

**Last Updated**: November 2025
**Maintainers**: Keep script descriptions updated when adding new scripts.
