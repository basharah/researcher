# Quick Start and Production Guide

Looking to run everything in production mode via Docker? Use:

```bash
./start-prod.sh --build
```

Then open:

- Frontend: <http://localhost:3000>
- API Health: <http://localhost:8000/api/v1/health>

For domain deployments, bake your public API into the frontend:

```bash
./build-images.sh --api-base https://your-domain/api/v1
./start-prod.sh
```

Below is the original getting started content for local/dev.

## What's Been Created

Your microservices-based research paper chatbot project is now set up with **Phase 1** fully implemented!

### ✅ Completed Structure

```text
researcher/
├── .github/
│   └── copilot-instructions.md     # AI context for the project
├── services/
│   ├── document-processing/        # ✅ PHASE 1 - COMPLETE
│   │   ├── main.py                 # FastAPI application
│   │   ├── models.py               # Database models
│   │   ├── database.py             # DB connection
│   │   ├── utils/
│   │   │   ├── pdf_parser.py       # PDF extraction
│   │   │   └── text_processor.py   # Section parsing
│   │   ├── requirements.txt
│   │   ├── Dockerfile
│   │   └── README.md
│   ├── vector-db/                  # Phase 2 - Placeholder
│   ├── llm-service/                # Phase 3 - Placeholder
│   └── api-gateway/                # Phase 4 - Placeholder
├── frontend/                       # Phase 5 - Integrated (Next.js)
├── shared/                         # Shared utilities
├── docker-compose.yml              # Dev orchestration
├── docker-compose.prod.yml         # Production orchestration
├── .env.example                    # Environment template
├── .gitignore
├── README.md                       # Main documentation
├── LEARNING_GUIDE.md              # Phase 1 learning guide
├── start.sh                        # Quick start (macOS/Linux)
├── start-prod.sh                   # Production start (Docker Compose)
├── start.ps1                       # Quick start (Windows)
└── test-service.sh                 # Test script
```

## 🚀 Quick Start - Get Running Now

### Option 1: Using the Quick Start Script (Recommended)

**macOS/Linux:**

```bash
./start.sh
```

**Windows (PowerShell):**

```powershell
.\start.ps1
```

### Option 2: Manual Docker Commands

```bash
# Start the services
docker-compose up -d postgres redis document-processing

# Check status
docker-compose ps

# View logs
docker-compose logs -f document-processing
```

### Option 3: Local Development (without Docker)

```bash
# Install PostgreSQL and Redis locally first, then:
cd services/document-processing
pip install -r requirements.txt
export DATABASE_URL="postgresql://researcher:researcher_pass@localhost:5432/research_papers"
uvicorn main:app --reload --port 8001
```

## 🧪 Test Your Setup

### 1. Check Service Health

```bash
curl http://localhost:8001/health
```

Expected output:

```json
{
  "status": "healthy",
  "database": "connected",
  "upload_dir": "./uploads",
  "upload_dir_exists": true
}
```

### 2. Visit API Documentation

Open in your browser:

- **Swagger UI**: <http://localhost:8001/docs>
- **ReDoc**: <http://localhost:8001/redoc>

### 3. Upload a Test Document

```bash
curl -X POST http://localhost:8001/upload \
  -F "file=@your_research_paper.pdf"
```

### 4. List Documents

```bash
curl http://localhost:8001/documents
```

## 📚 What You Can Do Now

### Immediate Actions

1. **Explore the API** → <http://localhost:8001/docs>
2. **Upload PDFs** → Test with research papers
3. **Read the code** → Start with `services/document-processing/main.py`
4. **Read LEARNING_GUIDE.md** → Understand Phase 1 in depth

### Learning Exercises

The `LEARNING_GUIDE.md` includes 5 hands-on exercises:

1. ✏️ Add DOI extraction
2. 📦 Implement batch upload
3. 🔍 Add full-text search
4. ✅ Improve file validation
5. ⚡ Add Redis caching

## 🗺️ Your Learning Roadmap

### Phase 1: Document Processing ✅ (You are here!)

- FastAPI REST API
- PDF processing
- Database modeling
- Docker basics

**Time to complete**: 1-2 weeks
**Status**: ✅ Infrastructure ready, now learn & extend!

### Phase 2: Vector Database 🔲 (Next)

- Vector embeddings
- Semantic search
- pgvector extension
- Sentence transformers

**Time to complete**: 1-2 weeks
**Start when**: You're comfortable with Phase 1

### Phase 3: LLM Service 🔲

- LangChain integration
- Prompt engineering
- OpenAI/Claude APIs
- Literature review extraction

**Time to complete**: 1-2 weeks
**Prerequisites**: Phase 1 & 2 complete

### Phase 4: API Gateway 🔲

- Service orchestration
- Request routing
- Load balancing
- Authentication

**Time to complete**: 1 week
**Prerequisites**: Phases 1-3 complete

### Phase 5: Frontend 🔲

- React application
- Chat interface
- Real-time updates
- Result visualization

**Time to complete**: 2-3 weeks
**Prerequisites**: All backend phases complete

## 🎯 Next Steps

### Right Now (Today)

1. ✅ Run the quick start script
2. ✅ Test the API endpoints
3. ✅ Upload your first PDF
4. ✅ Explore the Swagger docs

### This Week

1. 📖 Read through `LEARNING_GUIDE.md`
2. 🔍 Study the code in `services/document-processing/`
3. ✏️ Complete Exercise 1 (Add DOI extraction)
4. 🧪 Write your first unit test

### Next Week

1. ✅ Complete 2-3 more exercises
2. 🚀 Start planning Phase 2 (Vector DB)
3. 📚 Read about vector embeddings
4. 🎨 Customize the service to your needs

## 📖 Documentation Quick Links

- **Main README**: `README.md` - Project overview
- **Learning Guide**: `LEARNING_GUIDE.md` - Phase 1 deep dive
- **Service README**: `services/document-processing/README.md` - API docs
- **Copilot Instructions**: `.github/copilot-instructions.md` - AI context

## 🆘 Getting Help

### Common Issues

**Service won't start:**

```bash
docker-compose logs document-processing
```

**Port already in use:**

```bash
lsof -ti:8001 | xargs kill -9
docker-compose down
docker-compose up
```

**Database errors:**

```bash
docker-compose restart postgres
docker-compose logs postgres
```

**Need to rebuild:**

```bash
docker-compose down
docker-compose build --no-cache
docker-compose up
```

### Resources

- FastAPI Docs: <https://fastapi.tiangolo.com/>
- Docker Docs: <https://docs.docker.com/>
- PostgreSQL Docs: <https://www.postgresql.org/docs/>

## 💡 Pro Tips

1. **Keep Docker running** - Services auto-restart on code changes
2. **Use the API docs** - Swagger UI is interactive and helpful
3. **Commit often** - Use git to track your progress
4. **Learn gradually** - Master each phase before moving on
5. **Experiment freely** - This is a learning project!

## 🎓 Learning Objectives by Phase

By completing all phases, you'll learn:

- ✅ Microservices architecture
- ✅ RESTful API design with FastAPI
- ✅ Docker & containerization
- ✅ Database design & ORM
- ✅ Vector databases & embeddings
- ✅ LLM integration & prompt engineering
- ✅ Service orchestration
- ✅ Full-stack development
- ✅ DevOps basics

## 🌟 You're All Set

Your development environment is ready. Start exploring, learning, and building!

**First command to try:**

```bash
./start.sh && curl http://localhost:8001/health
```

Happy coding! 🚀

---

**Questions?** Check the documentation or modify the code to learn by doing!
