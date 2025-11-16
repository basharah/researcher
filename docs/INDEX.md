# Documentation Index

Centralized documentation for the Research Paper Analysis Chatbot.

This index organizes all project documentation by topic. All documentation files are in the `docs/` directory.

## 📖 Table of Contents

- [Getting Started](#getting-started)
- [Architecture & Phases](#architecture--phases)
- [Authentication & Security](#authentication--security)
- [GPU & Performance](#gpu--performance)
- [Features & Capabilities](#features--capabilities)
- [Development & Testing](#development--testing)
- [Deployment](#deployment)
- [Service-Specific Docs](#service-specific-docs)

---

## Getting Started

Start here if you're new to the project:

- **[GETTING_STARTED.md](GETTING_STARTED.md)** - Quick start guide, environment setup, and basic usage
- **[LEARNING_GUIDE.md](LEARNING_GUIDE.md)** - Phase 1 deep dive with exercises and learning paths

## Architecture & Phases

Understand the system architecture and how it evolved:

### Phase Completion Documentation

- **[PHASE2_INTEGRATION_COMPLETE.md](PHASE2_INTEGRATION_COMPLETE.md)** - Vector DB integration (semantic search)
- **[PHASE3_LLM_SERVICE.md](PHASE3_LLM_SERVICE.md)** - LLM service capabilities, prompts, and endpoints
- **[PHASE4_API_GATEWAY.md](PHASE4_API_GATEWAY.md)** - API Gateway architecture and orchestration
- **[PHASE4_COMPLETE.md](PHASE4_COMPLETE.md)** - Phase 4 completion summary
- **[PHASE5_FRONTEND.md](PHASE5_FRONTEND.md)** - Frontend implementation (Next.js)
- **[PHASE6_SECTION_DETECTION_COMPLETE.md](PHASE6_SECTION_DETECTION_COMPLETE.md)** - Advanced section detection

### Implementation Details

- **[ASYNC_WORKFLOW_COMPLETE.md](ASYNC_WORKFLOW_COMPLETE.md)** - Async processing with Celery
- **[CELERY_SETUP_COMPLETE.md](CELERY_SETUP_COMPLETE.md)** - Celery configuration and usage
- **[DOCUMENT_PROCESSING_ENHANCEMENT.md](DOCUMENT_PROCESSING_ENHANCEMENT.md)** - PDF extraction improvements
- **[SECTION_DETECTION_IMPROVEMENTS.md](SECTION_DETECTION_IMPROVEMENTS.md)** - Section parsing techniques
- **[SEARCH_AND_ANALYSIS_COMPLETE.md](SEARCH_AND_ANALYSIS_COMPLETE.md)** - Search and analysis features

## Authentication & Security

User authentication and storage:

- **[AUTHENTICATION_GUIDE.md](AUTHENTICATION_GUIDE.md)** - Complete authentication system guide
- **[AUTHENTICATION_IMPLEMENTATION.md](AUTHENTICATION_IMPLEMENTATION.md)** - Implementation details and decisions
- **[AUTH_QUICK_REF.md](AUTH_QUICK_REF.md)** - Quick reference for auth endpoints and flows
- **[USER_STORAGE_GUIDE.md](USER_STORAGE_GUIDE.md)** - User data storage architecture
- **[POSTGRESQL_USER_STORAGE_COMPLETE.md](POSTGRESQL_USER_STORAGE_COMPLETE.md)** - PostgreSQL migration from Redis
- **[COOKIE_AUTH_FIX.md](COOKIE_AUTH_FIX.md)** - Cookie-based authentication fixes

## GPU & Performance

GPU acceleration and performance optimization:

- **[GPU_SETUP.md](GPU_SETUP.md)** - Complete GPU setup instructions (NVIDIA drivers, Docker toolkit)
- **[GPU_CONFIGURATION.md](GPU_CONFIGURATION.md)** - GPU configuration for vector embeddings
- **[CPU_OPTIMIZATION.md](CPU_OPTIMIZATION.md)** - CPU resource optimization
- **[DOCKER_OPTIMIZATION.md](DOCKER_OPTIMIZATION.md)** - Docker performance tuning

Related scripts: `../scripts/verify-gpu.sh`, `../scripts/test-gpu.sh`

## Features & Capabilities

Detailed feature documentation:

- **[EXTRACTION_TESTING_SUMMARY.md](EXTRACTION_TESTING_SUMMARY.md)** - PDF extraction validation (tables, figures, references)
- **[PHASE3_LLM_SERVICE.md](PHASE3_LLM_SERVICE.md)** - LLM analysis types (summary, methodology, comparison, Q&A)
- **[PHASE5_FRONTEND.md](PHASE5_FRONTEND.md)** - Frontend features (search, analysis, compare, chat)

## Development & Testing

Development guides and testing:

- **[CONTRIBUTING.md](CONTRIBUTING.md)** - Contribution guidelines
- **[DEV_CONTAINER.md](DEV_CONTAINER.md)** - VS Code dev container setup
- **Testing Documentation**: See `../tests/README.md` and `../scripts/README.md`

## Deployment

Production deployment:

- **[DEPLOYMENT_COMPLETE.md](DEPLOYMENT_COMPLETE.md)** - Production deployment guide
- **Production Scripts**: `build-images.sh`, `start-prod.sh` in repository root
- **Docker Compose**: `docker-compose.prod.yml` for production orchestration

## Service-Specific Docs

Each microservice has detailed documentation in its directory:

- **Document Processing**: `../services/document-processing/README.md`
  - Also: `../services/document-processing/API_VERSIONING.md`
  - Also: `../services/document-processing/CONFIG.md`
  - Also: `../services/document-processing/COMPREHENSIVE_EXTRACTION.md`
  - Also: `../services/document-processing/REFACTORING_NOTES.md`

- **Vector DB**: `../services/vector-db/README.md`

- **LLM Service**: `../services/llm-service/README.md`

- **API Gateway**: `../services/api-gateway/README.md`

- **Frontend**: `../frontend/README.md`

---

## Quick Navigation

| I want to... | Go to... |
|--------------|----------|
| Get started quickly | [GETTING_STARTED.md](GETTING_STARTED.md) |
| Understand the architecture | [PHASE4_API_GATEWAY.md](PHASE4_API_GATEWAY.md) |
| Set up GPU acceleration | [GPU_SETUP.md](GPU_SETUP.md) |
| Learn about authentication | [AUTHENTICATION_GUIDE.md](AUTHENTICATION_GUIDE.md) |
| Deploy to production | [DEPLOYMENT_COMPLETE.md](DEPLOYMENT_COMPLETE.md) |
| Run tests | `../tests/README.md` and `../scripts/README.md` |
| Understand LLM features | [PHASE3_LLM_SERVICE.md](PHASE3_LLM_SERVICE.md) |
| Use the frontend | [PHASE5_FRONTEND.md](PHASE5_FRONTEND.md) |

---

**Last Updated**: November 2025  
**Maintainers**: Keep this index updated when adding new documentation.
