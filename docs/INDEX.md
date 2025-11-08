# Documentation Index

Centralized documentation for the Research Paper Analysis Chatbot.

## High-Level Guides
- GETTING_STARTED.md – Quick start and environment setup
- LEARNING_GUIDE.md – Phase 1 deep dive & exercises
- PHASE2_INTEGRATION_COMPLETE.md – Vector DB integration details
- PHASE3_LLM_SERVICE.md – LLM service capabilities & endpoints
- PHASE4_API_GATEWAY.md – API Gateway architecture & endpoints
- PHASE5_FRONTEND.md – Frontend implementation summary

## Authentication & User Storage
- AUTHENTICATION_GUIDE.md – Full auth system guide
- AUTHENTICATION_IMPLEMENTATION.md – Implementation summary
- AUTH_QUICK_REF.md – Quick reference for auth endpoints
- USER_STORAGE_GUIDE.md – User storage architecture (Redis → PostgreSQL)
- POSTGRESQL_USER_STORAGE_COMPLETE.md – PostgreSQL migration status

## GPU & Performance
- GPU_SETUP.md – Full GPU setup instructions
- GPU_CONFIGURATION.md – GPU configuration summary
- verify-gpu.sh – Script to validate GPU readiness

## Extraction & Processing
- EXTRACTION_TESTING_SUMMARY.md – Extraction feature validation results
- COMPREHENSIVE_EXTRACTION.md – (In service folder) extraction approach

## Phase Completion Summaries
- PHASE4_COMPLETE.md – API Gateway completion summary
- PHASE5_FRONTEND.md – Frontend completion summary

## Scripts (now moved to scripts/)
See the `scripts/` directory for:
- start.sh / start.ps1 – Environment startup
- test-phase2-integration.sh – Vector DB integration test
- test-phase4-integration.sh – API Gateway integration test
- test-extraction-endpoints.sh – Extraction endpoints test
- test-auth-postgresql.sh – Auth with PostgreSQL test
- test-service.sh – Basic document-processing service test
- test-gpu.sh / verify-gpu.sh – GPU validation

## Tests (now moved to tests/)
Python test files:
- test_comprehensive.py – Comprehensive parser tests
- test_vector_db.py – Vector DB operations
- test.py – Ad-hoc integration helper

## Internal Service Docs
Located within each service directory:
- services/document-processing/README.md
- services/vector-db/README.md
- services/llm-service/README.md

---
Use this index to find the right doc quickly. Update when new docs are added.
