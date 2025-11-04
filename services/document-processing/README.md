# Document Processing Service

This service handles PDF upload, text extraction, and section parsing for research papers.

## Features

- Upload PDF research papers
- Extract text and metadata
- Parse paper sections (abstract, introduction, methodology, results, conclusion, references)
- Store documents in PostgreSQL database
- **API Versioning support** for future-proof development

## API Endpoints

### Root Endpoints

```
GET /
GET /health
```

### API v1 Endpoints

All v1 endpoints are prefixed with `/api/v1`:

#### Upload Document

```
POST /api/v1/upload
```

Upload a research paper PDF (max 10MB)

#### List Documents

```
GET /api/v1/documents?skip=0&limit=10
```

Get all uploaded documents with pagination

#### Get Document Details

```
GET /api/v1/documents/{document_id}
```

Get details of a specific document

#### Get Document Sections

```
GET /api/v1/documents/{document_id}/sections
```

Get all extracted sections from a document

#### Delete Document

```
DELETE /api/v1/documents/{document_id}
```

Delete a document and its file

## Project Structure

```
services/document-processing/
├── main.py                    # Application entry point
├── api/
│   ├── __init__.py           # Main API router
│   ├── README.md             # API versioning guide
│   └── v1/
│       ├── __init__.py       # v1 router
│       └── endpoints.py      # v1 endpoints
├── crud.py                    # Database operations (CRUD)
├── models.py                  # SQLAlchemy models
├── schemas.py                 # Pydantic schemas
├── database.py                # Database configuration
├── utils/
│   ├── pdf_parser.py         # PDF extraction
│   └── text_processor.py     # Text processing
├── requirements.txt
├── Dockerfile
└── README.md
```

## Running Locally

1. Install dependencies:

```bash
pip install -r requirements.txt
```

2. Set environment variables:

```bash
export DATABASE_URL=postgresql://researcher:researcher_pass@localhost:5432/research_papers
export REDIS_URL=redis://localhost:6379
```

3. Run the service:

```bash
uvicorn main:app --reload --port 8001
```
### Migrations (Alembic)
	- Initialize already configured Alembic in this service under `alembic/`.
	- Common commands (run from `services/document-processing/`):
		- Upgrade to latest: `./migrate.sh upgrade head`
		- Create new revision (autogenerate): `./migrate.sh revision -m "message" --autogenerate`
		- Downgrade one step: `./migrate.sh downgrade -1`
	- Alembic reads the database URL from `config.settings.database_url` (or `DATABASE_URL` env var).
	- New columns added:
		- `tables_data` JSONB
		- `figures_metadata` JSONB
		- `references_json` JSONB
		- `tables_extracted`, `figures_extracted`, `references_extracted` booleans

## Running with Docker

```bash
docker-compose up document-processing
```

## Testing

Visit `http://localhost:8001/docs` for interactive API documentation (Swagger UI).
