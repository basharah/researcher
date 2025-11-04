# Research Paper Analysis Chatbot - Microservices Project

A microservices-based chatbot system for analyzing research papers, extracting literature reviews, and conducting research assistance. Built with a gradual learning approach where each service is developed incrementally.

## 🎯 Project Overview

This project implements a complete chatbot system for research paper analysis using microservices architecture. Each service is independent and can be developed, tested, and deployed separately.

### Key Features

- **PDF Upload & Processing**: Extract text, metadata, and sections from research papers
- **Semantic Search**: Find relevant papers using vector embeddings
- **AI-Powered Analysis**: Extract literature reviews and conduct research using LLMs
- **Interactive Chat**: User-friendly interface for research assistance

## 🏗️ Architecture

```
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

## 🚀 Getting Started

### Prerequisites

- Docker and Docker Compose
- Python 3.11+ (for local development)
- Node.js 18+ (for frontend development)
- OpenAI or Anthropic API key (for Phase 3)

### Quick Start

1. **Clone and setup**
   ```bash
   cd researcher
   cp .env.example .env
   # Edit .env and add your API keys
   ```

2. **Start Phase 1 (Document Processing)**
   ```bash
   docker-compose up postgres redis document-processing
   ```

3. **Access the service**
   - Document Processing API: http://localhost:8001
   - API Documentation: http://localhost:8001/docs
   - PostgreSQL: localhost:5432
   - Redis: localhost:6379

## 📖 Learning Path - Build Gradually

### **Phase 1: Document Processing Service** ✅ (Current Phase)

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

### **Phase 2: Vector Database Service** 🔲 (To be implemented)

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

### **Phase 3: LLM Service** 🔲 (To be implemented)

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

### **Phase 4: API Gateway** 🔲 (To be implemented)

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

### **Phase 5: Frontend** 🔲 (To be implemented)

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

## 📊 Project Structure

```
researcher/
├── .github/
│   └── copilot-instructions.md    # Project context for AI
├── services/
│   ├── document-processing/       # Phase 1 ✅
│   │   ├── main.py
│   │   ├── models.py
│   │   ├── database.py
│   │   ├── utils/
│   │   ├── requirements.txt
│   │   ├── Dockerfile
│   │   └── README.md
│   ├── vector-db/                 # Phase 2 🔲
│   │   ├── main.py
│   │   ├── requirements.txt
│   │   └── Dockerfile
│   ├── llm-service/               # Phase 3 🔲
│   │   ├── main.py
│   │   ├── requirements.txt
│   │   └── Dockerfile
│   └── api-gateway/               # Phase 4 🔲
│       ├── main.py
│       ├── requirements.txt
│       └── Dockerfile
├── frontend/                      # Phase 5 🔲
├── shared/                        # Shared utilities
├── docker-compose.yml
├── .env.example
├── .gitignore
└── README.md
```

## 🔧 Development Tips

### Running Individual Services

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

### Local Development

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

### Database Migrations

```bash
# Create migration
cd services/document-processing
alembic revision --autogenerate -m "description"

# Apply migration
alembic upgrade head
```

## 📝 API Documentation

Each service provides interactive API documentation via Swagger UI:

- Document Processing: http://localhost:8001/docs
- Vector DB: http://localhost:8002/docs
- LLM Service: http://localhost:8003/docs
- API Gateway: http://localhost:8000/docs

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

**Happy Learning! 🚀**

Start with Phase 1 and gradually build your knowledge of microservices, AI, and full-stack development!
