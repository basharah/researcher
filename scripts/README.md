# Scripts

Utility and integration scripts consolidated here. Run from repository root.

- `start.sh` — Migration-first startup for the full stack
- `test-phase2-integration.sh` — Document Processing ↔ Vector DB integration
- `test-phase4-integration.sh` — API Gateway end-to-end checks
- `test-extraction-endpoints.sh` — Tables, figures, references validation
- `test-auth-postgresql.sh` — Auth flow against PostgreSQL user storage
- `verify-gpu.sh` — Environment and container GPU verification
- `test-gpu.sh` — Sample workload to see GPU utilization during embeddings

Notes:

- Scripts expect Docker/Compose available on PATH.
- Some tests assume services are already running (`./scripts/start.sh`).
- GPU-related scripts require the NVIDIA Container Toolkit; see `docs/GPU_SETUP.md`.
