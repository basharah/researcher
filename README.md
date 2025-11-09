# Research Paper Analysis Chatbot

All core phases (1–5 backend + initial frontend scaffold) are complete. This README reflects the consolidated structure (docs/, scripts/, tests/) and migration-first startup pattern.

## 🎯 Project Overview

### Documentation Hub

Primary entry point: `docs/INDEX.md`

Selected quick links:

- Phase 2 (Vector DB Integration): `docs/PHASE2_INTEGRATION_COMPLETE.md`
- Phase 3 (LLM Service): `docs/PHASE3_LLM_SERVICE.md`
- Phase 4 (API Gateway): `docs/PHASE4_API_GATEWAY.md`, `docs/PHASE4_COMPLETE.md`
- Phase 5 (Frontend Overview): `docs/PHASE5_FRONTEND.md`
- Authentication Guides: `docs/AUTHENTICATION_GUIDE.md`, `docs/AUTH_QUICK_REF.md`
- GPU Setup & Configuration: `docs/GPU_SETUP.md`, `docs/GPU_CONFIGURATION.md`
- User Storage & Migration: `docs/USER_STORAGE_GUIDE.md`, `docs/POSTGRESQL_USER_STORAGE_COMPLETE.md`
- Extraction Testing Summary: `docs/EXTRACTION_TESTING_SUMMARY.md`

### Deep Dives

- Architecture & Data Flows: `docs/INDEX.md` (big-picture and entry points)
- Vector DB integration details: `docs/PHASE2_INTEGRATION_COMPLETE.md`
- LLM orchestration and prompts: `docs/PHASE3_LLM_SERVICE.md`
- API Gateway design & health aggregation: `docs/PHASE4_API_GATEWAY.md`
- GPU setup, config, and verification: `docs/GPU_SETUP.md`, `docs/GPU_CONFIGURATION.md`
- Authentication & security model: `docs/AUTHENTICATION_GUIDE.md`, `docs/AUTHENTICATION_IMPLEMENTATION.md`, `docs/AUTH_QUICK_REF.md`
- User storage migration (Redis → PostgreSQL): `docs/USER_STORAGE_GUIDE.md`, `docs/POSTGRESQL_USER_STORAGE_COMPLETE.md`

The system is a production-style microservices platform for research paper analysis with PDF ingestion, rich extraction (tables, figures, references, metadata), semantic vector search, RAG-enhanced LLM analysis, an API gateway, and GPU acceleration.

### Key Features

- **PDF Upload & Processing**: Extract text, metadata, and sections from research papers
- **Semantic Search**: Find relevant papers using vector embeddings
- **AI-Powered Analysis**: Extract literature reviews and conduct research using LLMs
- **Interactive Chat**: User-friendly interface for research assistance

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

## 🚀 Quick Start (Migration-First Stack)

Prerequisites:

- Docker / Docker Compose
- NVIDIA GPU (optional) with container toolkit (see `docs/GPU_SETUP.md`)
- OpenAI / Anthropic API keys for LLM features (optional until Phase 3 use)

Startup (all core services, applies migrations before bring-up):

```bash
./scripts/start.sh  # or ./start.sh (legacy root script maintained)
```

Health check:

```bash
curl http://localhost:8000/api/v1/health
```

If running only document-processing service:

```bash
docker-compose up -d postgres redis document-processing
```

Access points:

- API Gateway unified endpoint: [http://localhost:8000/api/v1/](http://localhost:8000/api/v1/)
- Document Processing (direct): [http://localhost:8001](http://localhost:8001)
- Vector DB: [http://localhost:8002](http://localhost:8002)
- LLM Service: [http://localhost:8003](http://localhost:8003)

GPU verification:

```bash
./scripts/verify-gpu.sh
```

## 📖 Learning Path - Build Gradually

### **Phase 1: Document Processing Service** ✅ (Complete)

**What You'll Learn:**

- FastAPI basics and REST API design
- PDF text extraction techniques
- Database modeling with SQLAlchemy
- File upload handling
- Docker containerization

**Tasks:**

1. ✅ Upload PDF research papers
2. ✅ Extract text and metadata
3. ✅ Parse sections (abstract, introduction, etc.)
4. ✅ Store in PostgreSQL database

**Get Started:**

```bash
cd services/document-processing
pip install -r requirements.txt
uvicorn main:app --reload --port 8001
```

**Test it:**

```bash
# Upload a PDF
curl -X POST "http://localhost:8001/upload" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@your_paper.pdf"

# List documents
curl "http://localhost:8001/documents"
```

**Next Steps:**

- [ ] Add support for DOI extraction
- [ ] Implement batch upload
- [ ] Add OCR for scanned PDFs
- [ ] Improve section detection accuracy

---

### **Phase 2: Vector Database Service** ✅ (Complete)

**What You'll Learn:**

- Vector embeddings and semantic search
- Working with pgvector extension
- Sentence transformers
- Similarity search algorithms

**Features to Implement:**

1. Generate embeddings for documents
2. Store vectors in PostgreSQL with pgvector
3. Implement semantic search
4. Create similar documents endpoint

**Learning Resources:**

- [pgvector documentation](https://github.com/pgvector/pgvector)
- [Sentence Transformers](https://www.sbert.net/)

---

### **Phase 3: LLM Service** ✅ (Complete)

**What You'll Learn:**

- LangChain framework
- Prompt engineering
- OpenAI/Claude API integration
- Token management and cost optimization

**Features to Implement:**

1. Literature review extraction
2. Research gap identification
3. Methodology comparison
4. Citation analysis
5. Question answering over documents

**Learning Resources:**

- [LangChain Documentation](https://python.langchain.com/)
- [OpenAI API](https://platform.openai.com/docs)

---

### **Phase 4: API Gateway** ✅ (Complete)

**What You'll Learn:**

- Service orchestration
- API composition patterns
- Load balancing
- Error handling across services

**Features to Implement:**

1. Unified API endpoint
2. Request routing
3. Service health monitoring
4. Rate limiting
5. Authentication & authorization

---

### **Phase 5: Frontend** ✅ (Initial scaffold & integration complete)

**What You'll Learn:**

- React application structure
- State management
- WebSocket for real-time chat
- File upload UI
- Results visualization

**Features to Implement:**

1. Chat interface
2. Document upload widget
3. Search and filter documents
4. Visualization of analysis results
5. Export functionality

## 🧪 Testing Your Services

Each phase includes testing:

```bash
# Run tests for document processing
cd services/document-processing
pytest

# Run all tests
docker-compose -f docker-compose.test.yml up
```

## 📊 Current Project Structure

```text
researcher/
├── .github/
│   └── copilot-instructions.md    # Project context for AI
├── services/
│   ├── document-processing/       # Phase 1
│   │   ├── main.py
│   │   ├── models.py
│   │   ├── database.py
│   │   ├── utils/
│   │   ├── requirements.txt
│   │   ├── Dockerfile
│   │   └── README.md
│   ├── vector-db/                 # Phase 2
│   │   ├── main.py
│   │   ├── requirements.txt
│   │   └── Dockerfile
│   ├── llm-service/               # Phase 3
│   │   ├── main.py
│   │   ├── requirements.txt
│   │   └── Dockerfile
│   └── api-gateway/               # Phase 4
├── docs/                          # Consolidated documentation (see INDEX.md)
├── scripts/                       # Test / utility scripts (start, gpu, integration)
├── tests/                         # Python test scripts (extraction, vector db)
│       ├── main.py
│       ├── requirements.txt
│       └── Dockerfile
├── frontend/                      # Phase 5 🔲
├── shared/                        # Shared utilities
├── docker-compose.yml
├── .env.example
├── .gitignore
└── README.md                      # This file
```

## 🔧 Development Tips

### Running Individual Services (Profiles)

Each service can run independently:

```bash
# Document Processing only
docker-compose up postgres redis document-processing

# Add Vector DB (Phase 2)
docker-compose --profile phase2 up

# Add LLM Service (Phase 3)
docker-compose --profile phase3 up

# Full stack (Phase 4+)
docker-compose --profile phase4 up
```

### Local Development (Single Service)

```bash
# Set up Python virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies for a service
cd services/document-processing
pip install -r requirements.txt

# Run locally
uvicorn main:app --reload --port 8001
```

### Database Migrations (Manual Invocation)

```bash
# Create migration
cd services/document-processing
alembic revision --autogenerate -m "description"

# Apply migration
alembic upgrade head
```

## 📝 API Documentation

Each service provides interactive API documentation via Swagger UI:

- Document Processing: [http://localhost:8001/docs](http://localhost:8001/docs)
- Vector DB: [http://localhost:8002/docs](http://localhost:8002/docs)
- LLM Service: [http://localhost:8003/docs](http://localhost:8003/docs)
- API Gateway: [http://localhost:8000/docs](http://localhost:8000/docs)

## 🤝 Contributing

This is a learning project! Feel free to:

- Improve existing services
- Add new features
- Optimize performance
- Enhance documentation

## 📚 Learning Resources

### Microservices

- [Microservices Patterns](https://microservices.io/patterns/index.html)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)

### AI/ML for Research

- [LangChain for Research](https://python.langchain.com/docs/use_cases/question_answering/)
- [Semantic Scholar API](https://www.semanticscholar.org/product/api)

### Vector Databases

- [Vector Database Guide](https://www.pinecone.io/learn/vector-database/)

## 🎓 Next Steps After Completion

Once you've completed all phases:

1. **Deploy to Cloud**: AWS, GCP, or Azure
2. **Add Monitoring**: Prometheus, Grafana
3. **Implement CI/CD**: GitHub Actions
4. **Scale Services**: Kubernetes
5. **Add More Features**:
   - Citation network visualization
   - Automated systematic reviews
   - Research trend analysis
   - Collaborative features

## 📄 License

MIT License - Feel free to use for learning and personal projects

## 🆘 Troubleshooting

### Common Issues

**Port already in use:**

```bash
# Find and kill process
lsof -ti:8001 | xargs kill -9
```

**Database connection failed:**

```bash
# Check PostgreSQL is running
docker-compose ps postgres
# View logs
docker-compose logs postgres
```

**Import errors:**

```bash
# Rebuild containers
docker-compose build --no-cache
```

---

## 🔒 Authentication & User Storage

Phase 4 includes full JWT auth (access + refresh), API keys, role-based access, and PostgreSQL user/token storage. See `docs/AUTHENTICATION_IMPLEMENTATION.md` and `docs/USER_STORAGE_GUIDE.md`.

## 🧠 Retrieval-Augmented Generation (RAG)

The LLM service performs document-aware analysis using semantic search results from the Vector DB (MiniLM 384-d embeddings). GPU acceleration is enabled for embeddings when available.

## ⚙️ Performance & GPU

Vector DB embeddings run on GPU 0; LLM can target GPU 1 for local models (future expansion). See `docs/GPU_CONFIGURATION.md`.

## 🧪 Testing & Scripts

Integration and feature test scripts now under `scripts/`:

- Phase 2 integration: `scripts/test-phase2-integration.sh`
- API Gateway integration: `scripts/test-phase4-integration.sh`
- Extraction endpoints: `scripts/test-extraction-endpoints.sh`
- Auth flow (PostgreSQL): `scripts/test-auth-postgresql.sh`
- GPU verification & workload: `scripts/verify-gpu.sh`, `scripts/test-gpu.sh`

Python tests in `tests/` (transitioning toward pytest harness):

- `tests/test_comprehensive.py`
- `tests/test_vector_db.py`
- `tests/test.py`

Pytest configuration added in `pytest.ini` – run all tests:

```bash
pytest
```

## 🧼 Ongoing Cleanup

Remaining cleanup tasks tracked internally: markdown lint adjustments, root doc stubs, expanding automated test coverage, and de-duplicating legacy root markdown files.

---
**System ready.** Explore `docs/INDEX.md`, run `./scripts/start.sh`, and begin leveraging the full research workflow.
