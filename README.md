# Research Paper Analysis Chatbot

A production-ready microservices platform for AI-powered research paper analysis with semantic search, RAG-enhanced insights, and interactive chat.

## 🎯 Project Overview

### Quick Links

📚 **[Complete Documentation Index](docs/INDEX.md)** - Browse all documentation organized by topic

🚀 **[Getting Started Guide](docs/GETTING_STARTED.md)** - Environment setup and first steps

🧪 **[Testing Guide](tests/README.md)** - Python tests and integration validation

🔧 **[Scripts Reference](scripts/README.md)** - All utility and test scripts

### System Capabilities

- **PDF Upload & Processing**: Extract text, metadata, tables, figures, and references from research papers
- **Semantic Search**: Find relevant content using vector embeddings with GPU acceleration
- **AI-Powered Analysis**: Generate summaries, extract methodologies, compare papers using LLMs (OpenAI/Anthropic)
- **Interactive Chat**: Q&A interface with RAG (Retrieval-Augmented Generation)
- **Async Processing**: Background jobs with Celery for scalable document ingestion
- **Production-Ready**: Docker Compose orchestration, health monitoring, authentication

### Documentation Structure

All documentation is organized in the `docs/` directory:

- **Getting Started**: [GETTING_STARTED.md](docs/GETTING_STARTED.md), [LEARNING_GUIDE.md](docs/LEARNING_GUIDE.md)
- **Architecture**: Phase completion docs ([Phase 2](docs/PHASE2_INTEGRATION_COMPLETE.md), [Phase 3](docs/PHASE3_LLM_SERVICE.md), [Phase 4](docs/PHASE4_API_GATEWAY.md), [Phase 5](docs/PHASE5_FRONTEND.md))
- **Authentication**: [AUTHENTICATION_GUIDE.md](docs/AUTHENTICATION_GUIDE.md), [AUTH_QUICK_REF.md](docs/AUTH_QUICK_REF.md)
- **GPU Setup**: [GPU_SETUP.md](docs/GPU_SETUP.md), [GPU_CONFIGURATION.md](docs/GPU_CONFIGURATION.md)
- **Deployment**: [DEPLOYMENT_COMPLETE.md](docs/DEPLOYMENT_COMPLETE.md)

**Browse the full index**: [docs/INDEX.md](docs/INDEX.md)

## 🏗️ Architecture

```text
┌─────────────────┐
│    Frontend     │ (React Chat Interface)
│   (Phase 5)     │
└────────┬────────┘
         │
┌────────▼────────┐
│  API Gateway    │ (Service Orchestration)
│   (Phase 4)     │
└────────┬────────┘
         │
    ┌────┴────┬────────────┬────────────┐
    │         │            │            │
┌───▼───┐ ┌──▼──┐ ┌───────▼──────┐ ┌───▼────┐
│ Doc   │ │Vec  │ │ LLM Service  │ │ Redis  │
│Process│ │ DB  │ │  (Phase 3)   │ │ Cache  │
│(Phase1│ │(Ph2)│ └──────────────┘ └────────┘
└───┬───┘ └──┬──┘
    │        │
┌───▼────────▼───┐
│   PostgreSQL   │
│   + pgvector   │
└────────────────┘
```

## 📚 Technology Stack

### Backend Services

- **Framework**: Python FastAPI
- **Database**: PostgreSQL with pgvector extension
- **Cache**: Redis
- **Containerization**: Docker & Docker Compose

### AI/ML Libraries

- **PDF Processing**: PyPDF2, pdfplumber
- **Embeddings**: Sentence Transformers
- **LLM Integration**: LangChain, OpenAI API, Anthropic Claude

### Frontend

- **Framework**: React
- **State Management**: Context API / Redux
- **HTTP Client**: Axios

## 🚀 Quick Start

### Development Mode

Prerequisites:

- Docker and Docker Compose
- (Optional) NVIDIA GPU with container toolkit - see [GPU Setup Guide](docs/GPU_SETUP.md)
- (Optional) OpenAI/Anthropic API keys - see [.env.example](.env.example)

**Start all services:**

```bash
./scripts/start.sh
```

This script:

- Starts PostgreSQL, Redis, and all microservices
- Runs database migrations automatically
- Enables GPU acceleration if available

**Verify services:**

```bash
# Check all services via API Gateway
curl http://localhost:8000/api/v1/health

# Or check individual services
curl http://localhost:8001/health  # Document Processing
curl http://localhost:8002/health  # Vector DB
curl http://localhost:8003/health  # LLM Service
```

**Access points:**

- API Gateway: <http://localhost:8000/api/v1/>
- Frontend: <http://localhost:3000> (if running frontend service)
- Flower (Celery monitoring): <http://localhost:5555>

### Production Mode

Build and deploy with production configuration:

```bash
# Build all images
./build-images.sh

# Start production stack
./start-prod.sh --build

# Or with custom API base URL
./build-images.sh --api-base https://your-domain/api/v1
./start-prod.sh
```

**Production endpoints:**

- Frontend: <http://localhost:3000>
- API Health: <http://localhost:8000/api/v1/health>

**Default admin credentials:**

- Email: `admin@bashars.eu`
- Password: `admin123`
- ⚠️ **Change password immediately after first login!**

See [Deployment Guide](docs/DEPLOYMENT_COMPLETE.md) for production deployment details and [Default Admin User Guide](docs/DEFAULT_ADMIN_USER.md) for admin user configuration.

## 🧪 Testing

### Run Tests

All test scripts are in the `scripts/` directory:

```bash
# Integration tests
./scripts/test-phase2-integration.sh    # Vector DB integration
./scripts/test-phase4-integration.sh    # API Gateway workflows
./scripts/test-extraction-endpoints.sh   # PDF extraction features

# Feature tests
./scripts/test-pipeline.sh               # Full pipeline
./scripts/test-auth-postgresql.sh        # Authentication

# GPU tests
./scripts/verify-gpu.sh                  # Verify GPU setup
./scripts/test-gpu.sh                    # GPU performance
```

### Python Tests

Unit and integration tests are in the `tests/` directory:

```bash
# Run specific test
python tests/test_comprehensive.py      # PDF extraction
python tests/test_vector_db.py          # Vector DB integration

# Run all tests
pytest tests/
```

**Documentation:**

- [Scripts Reference](scripts/README.md) - All shell test scripts
- [Tests Documentation](tests/README.md) - Python test suite

## 📖 Learning Path

All phases are complete. Use these guides to understand each component:

- **[Phase 1: Document Processing](docs/GETTING_STARTED.md)** - PDF upload, extraction, metadata
- **[Phase 2: Vector DB](docs/PHASE2_INTEGRATION_COMPLETE.md)** - Semantic search with embeddings
- **[Phase 3: LLM Service](docs/PHASE3_LLM_SERVICE.md)** - AI analysis and RAG
- **[Phase 4: API Gateway](docs/PHASE4_API_GATEWAY.md)** - Service orchestration
- **[Phase 5: Frontend](docs/PHASE5_FRONTEND.md)** - Next.js chat interface
- **[Learning Guide](docs/LEARNING_GUIDE.md)** - Detailed Phase 1 walkthrough

## 📊 Project Structure

```text
researcher/
├── docs/                          # 📚 All documentation (see INDEX.md)
├── scripts/                       # 🔧 Utility and test scripts
├── tests/                         # 🧪 Python unit and integration tests
├── services/                      # 🚀 Microservices
│   ├── document-processing/       # Phase 1: PDF extraction
│   ├── vector-db/                 # Phase 2: Semantic search
│   ├── llm-service/               # Phase 3: AI analysis
│   └── api-gateway/               # Phase 4: Orchestration
├── frontend/                      # Phase 5: Next.js UI
├── docker-compose.yml             # Development orchestration
├── docker-compose.prod.yml        # Production orchestration
├── build-images.sh                # Build all Docker images
├── start-prod.sh                  # Production startup
└── README.md                      # This file
```

## 🔧 Development Tips

### Running Individual Services

Use Docker Compose profiles:

```bash
# Document Processing only
docker-compose up -d postgres redis document-processing

# With Vector DB (Phase 2)
docker-compose --profile phase2 up -d

# With LLM Service (Phase 3)
docker-compose --profile phase3 up -d

# Full stack (all phases)
docker-compose --profile phase4 up -d
```

### Local Development (Without Docker)

```bash
# Create Python virtual environment
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Install dependencies for a service
cd services/document-processing
pip install -r requirements.txt

# Run locally
uvicorn main:app --reload --port 8001
```

### Database Migrations

```bash
# From document-processing service directory
cd services/document-processing

# Create migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head
```

Or use the provided script:

```bash
./services/document-processing/migrate.sh
```

## 📝 API Documentation

Each service provides interactive Swagger UI documentation:

- **API Gateway**: <http://localhost:8000/docs> - Unified API
- **Document Processing**: <http://localhost:8001/docs> - Upload and extraction
- **Vector DB**: <http://localhost:8002/docs> - Search and embeddings
- **LLM Service**: <http://localhost:8003/docs> - AI analysis

## 🤝 Contributing

Contributions welcome! See [CONTRIBUTING.md](docs/CONTRIBUTING.md) for guidelines.

## 📚 Additional Resources

- **[Complete Documentation Index](docs/INDEX.md)** - Browse all docs
- **[GPU Setup Guide](docs/GPU_SETUP.md)** - Configure GPU acceleration
- **[Authentication Guide](docs/AUTHENTICATION_GUIDE.md)** - User auth and security
- **[Deployment Guide](docs/DEPLOYMENT_COMPLETE.md)** - Production deployment

## 🆘 Troubleshooting

### Common Issues

**Services won't start:**

```bash
# Check Docker is running
docker ps

# Rebuild and start clean
docker-compose down -v
./scripts/start.sh
```

**Port conflicts:**

```bash
# Find process using port
lsof -i :8000  # macOS/Linux
netstat -ano | findstr :8000  # Windows

# Change ports in docker-compose.yml if needed
```

**GPU not detected:**

```bash
# Verify GPU setup
./scripts/verify-gpu.sh

# See full GPU guide
cat docs/GPU_SETUP.md
```

**Tests failing:**

```bash
# Ensure services are running
curl http://localhost:8000/api/v1/health

# Check service logs
docker-compose logs document-processing
```

**Database migrations failing:**

```bash
# Reset database
docker-compose down -v
./scripts/start.sh  # Migrations run automatically
```

For more help, see:

- [Getting Started Guide](docs/GETTING_STARTED.md)
- [Scripts Reference](scripts/README.md)
- [Tests Documentation](tests/README.md)

## 📄 License

MIT License - Feel free to use for learning and projects.

---

**Last Updated**: November 2025

