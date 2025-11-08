# Phase 1 Learning Guide: Document Processing Service

Welcome to Phase 1 of building the Research Paper Analysis Chatbot! This guide will help you understand what you've built and how to extend it.

## 🎯 What You've Built

A complete document processing microservice that can:
- Accept PDF uploads via REST API
- Extract text from PDFs using two methods (PyPDF2 and pdfplumber)
- Parse research paper sections (abstract, introduction, methodology, etc.)
- Store documents in a PostgreSQL database
- Provide CRUD operations via RESTful endpoints

## 📚 Key Concepts Covered

### 1. FastAPI Framework
FastAPI is a modern Python web framework that provides:
- Automatic API documentation (Swagger UI)
- Data validation with Pydantic
- Async support for better performance
- Type hints for better code quality

**Files to study:**
- `services/document-processing/main.py` - Main application and endpoints

**Key patterns:**
```python
@app.post("/upload", response_model=DocumentResponse)
async def upload_document(file: UploadFile = File(...)):
    # Automatic validation, file handling, and response serialization
```

### 2. Database Modeling with SQLAlchemy
Learn how to define database models and relationships.

**Files to study:**
- `services/document-processing/models.py` - Database models
- `services/document-processing/database.py` - Database connection

**Key concepts:**
- ORM (Object-Relational Mapping)
- Migrations (coming in future iterations)
- Database sessions and connections

### 3. PDF Processing
Two libraries are used for robustness:
- **PyPDF2**: Metadata extraction
- **pdfplumber**: Better text extraction

**Files to study:**
- `services/document-processing/utils/pdf_parser.py`

**Challenge:** Try adding support for:
- Table extraction
- Image extraction
- OCR for scanned PDFs

### 4. Text Processing & NLP Basics
Basic natural language processing to identify paper sections.

**Files to study:**
- `services/document-processing/utils/text_processor.py`

**How it works:**
1. Regex patterns match section headers
2. Extract text between headers
3. Fallback heuristics for missing sections

**Improvements to try:**
- Use ML models for better section detection
- Extract author names and affiliations
- Identify key findings automatically

### 5. Docker & Containerization
Each service runs in its own container.

**Files to study:**
- `services/document-processing/Dockerfile`
- `docker-compose.yml`

**Key concepts:**
- Multi-stage builds (can be added for optimization)
- Volume mounting for development
- Health checks
- Service dependencies

## 🛠️ Hands-On Exercises

### Exercise 1: Add DOI Extraction
**Goal:** Extract the DOI (Digital Object Identifier) from papers

**Steps:**
1. Add a `doi` field to the Document model
2. Create a regex pattern to find DOI in text
3. Update the text processor to extract DOI
4. Add DOI to the API response

**Hint:** DOI pattern: `10\.\d{4,9}/[-._;()/:A-Za-z0-9]+`

### Exercise 2: Add Batch Upload
**Goal:** Allow uploading multiple PDFs at once

**Steps:**
1. Create a new endpoint `/upload/batch`
2. Accept multiple files in the request
3. Process files concurrently using `asyncio`
4. Return list of uploaded documents

### Exercise 3: Add Full-Text Search
**Goal:** Search documents by content

**Steps:**
1. Create a new endpoint `/search?q=query`
2. Use PostgreSQL's full-text search capabilities
3. Return ranked results
4. Add pagination support

**PostgreSQL FTS Example:**
```sql
SELECT * FROM documents 
WHERE to_tsvector('english', full_text) @@ to_tsquery('english', 'query');
```

### Exercise 4: Add File Validation
**Goal:** Better validate uploaded PDFs

**Steps:**
1. Check if file is actually a PDF (not just extension)
2. Validate PDF is not corrupted
3. Check for minimum page count
4. Add file type detection using `python-magic`

### Exercise 5: Add Caching with Redis
**Goal:** Cache document metadata to reduce database queries

**Steps:**
1. Import Redis client
2. Cache document list for 5 minutes
3. Invalidate cache on new upload
4. Add cache hit/miss metrics

## 🧪 Testing Your Service

### Manual Testing with curl

```bash
# Health check
curl http://localhost:8001/health

# Upload a document
curl -X POST http://localhost:8001/upload \
  -F "file=@research_paper.pdf"

# List all documents
curl http://localhost:8001/documents

# Get specific document
curl http://localhost:8001/documents/1

# Get document sections
curl http://localhost:8001/documents/1/sections

# Delete document
curl -X DELETE http://localhost:8001/documents/1
```

### Using the Interactive API Docs

Visit http://localhost:8001/docs for a complete interactive interface!

### Writing Unit Tests

Create `services/document-processing/tests/test_api.py`:

```python
import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_upload_pdf():
    # Test with a sample PDF
    with open("sample.pdf", "rb") as f:
        response = client.post(
            "/upload",
            files={"file": ("test.pdf", f, "application/pdf")}
        )
    assert response.status_code == 201
    assert "id" in response.json()
```

## 🔍 Understanding the Code Flow

### Upload Flow:
1. Client uploads PDF via `/upload` endpoint
2. FastAPI validates file type and size
3. File is saved to disk with unique filename
4. PDFParser extracts text and metadata
5. TextProcessor identifies sections
6. Document model created and saved to database
7. Response sent back with document ID

### Retrieval Flow:
1. Client requests document via `/documents/{id}`
2. SQLAlchemy queries database
3. Document model serialized to DocumentResponse
4. JSON response sent to client

## 🚀 Next Steps

Once you're comfortable with Phase 1:

### Prepare for Phase 2: Vector Database
You'll learn:
- Vector embeddings and semantic search
- Working with pgvector extension
- Sentence transformers for generating embeddings
- Similarity search implementation

### Before Phase 2:
- [ ] Understand how Phase 1 works completely
- [ ] Complete at least 2 exercises above
- [ ] Read about vector embeddings
- [ ] Familiarize yourself with sentence-transformers library

## 📖 Additional Resources

### FastAPI
- [FastAPI Tutorial](https://fastapi.tiangolo.com/tutorial/)
- [Pydantic Documentation](https://docs.pydantic.dev/)

### SQLAlchemy
- [SQLAlchemy ORM Tutorial](https://docs.sqlalchemy.org/en/20/orm/tutorial.html)

### PDF Processing
- [PyPDF2 Documentation](https://pypdf2.readthedocs.io/)
- [pdfplumber Docs](https://github.com/jsvine/pdfplumber)

### Research Papers & PDFs
- [Understanding PDF Structure](https://resources.infosecinstitute.com/topic/pdf-file-format-basic-structure/)
- [Academic Paper Structure](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC3178846/)

## 💡 Tips for Success

1. **Read the code thoroughly** - Understand every line before modifying
2. **Use the API docs** - FastAPI's auto-generated docs are your friend
3. **Experiment** - Break things and fix them to learn
4. **Add logging** - Use Python's logging module to debug
5. **Version control** - Commit your changes frequently

## 🐛 Common Issues & Solutions

### Issue: "Import could not be resolved"
**Solution:** Install dependencies:
```bash
cd services/document-processing
pip install -r requirements.txt
```

### Issue: Database connection failed
**Solution:** Ensure PostgreSQL is running:
```bash
docker-compose ps postgres
docker-compose logs postgres
```

### Issue: PDF extraction returns empty text
**Solution:** Try the other extraction method or check if PDF has text layer (not scanned image)

### Issue: Port 8001 already in use
**Solution:** 
```bash
lsof -ti:8001 | xargs kill -9
```

---

**Ready for Phase 2?** Move on to implementing the Vector Database Service to add semantic search capabilities!