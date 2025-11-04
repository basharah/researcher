# API Versioning Structure

## Overview

The API has been restructured to support versioning, allowing for future API changes without breaking existing clients.

## Structure

```
services/document-processing/
├── main.py                    # Main application entry point
├── api/
│   ├── __init__.py           # Main API router (aggregates all versions)
│   └── v1/
│       ├── __init__.py       # v1 router
│       └── endpoints.py      # v1 endpoints (documents)
├── crud.py                    # Database operations
├── models.py                  # Database models
├── schemas.py                 # Pydantic schemas
├── database.py                # Database configuration
└── utils/                     # Utility functions
```

## API Endpoints

### Current API URLs (v1)

All API endpoints are now prefixed with `/api/v1`:

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/upload` | Upload a PDF document |
| GET | `/api/v1/documents` | List all documents |
| GET | `/api/v1/documents/{id}` | Get document by ID |
| GET | `/api/v1/documents/{id}/sections` | Get document sections |
| DELETE | `/api/v1/documents/{id}` | Delete a document |

### Root Endpoints (Unversioned)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Service information |
| GET | `/health` | Health check |
| GET | `/docs` | Swagger UI documentation |
| GET | `/redoc` | ReDoc documentation |

## Examples

### Upload Document (v1)
```bash
curl -X POST "http://localhost:8001/api/v1/upload" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@research_paper.pdf"
```

### List Documents (v1)
```bash
curl "http://localhost:8001/api/v1/documents?skip=0&limit=10"
```

### Get Document (v1)
```bash
curl "http://localhost:8001/api/v1/documents/1"
```

## Adding a New API Version (v2)

When you need to make breaking changes, create a new version:

### 1. Create v2 directory structure
```bash
mkdir -p api/v2
touch api/v2/__init__.py
touch api/v2/endpoints.py
```

### 2. Implement v2 endpoints
```python
# api/v2/endpoints.py
from fastapi import APIRouter

router = APIRouter()

@router.post("/upload")
async def upload_document_v2(...):
    # New implementation with breaking changes
    pass
```

### 3. Register v2 router
```python
# api/v2/__init__.py
from fastapi import APIRouter
from api.v2 import endpoints

router = APIRouter()
router.include_router(endpoints.router, tags=["documents-v2"])
```

### 4. Include in main API router
```python
# api/__init__.py
from fastapi import APIRouter
from .v1 import router as v1_router
from .v2 import router as v2_router  # Add this

api_router = APIRouter()
api_router.include_router(v1_router, prefix="/v1")
api_router.include_router(v2_router, prefix="/v2")  # Add this
```

## Migration Strategy

### Option 1: Parallel Versions (Recommended)

- Keep both v1 and v2 running
- Gradually migrate clients to v2
- Deprecate v1 after migration period
- Remove v1 after all clients migrated

### Option 2: Sunset Period

- Announce v1 deprecation
- Add deprecation warnings to v1 responses
- Set sunset date
- Redirect v1 to v2 after sunset

### Example Deprecation Header
```python
from fastapi import Response

@router.get("/documents")
async def list_documents_v1(response: Response, ...):
    response.headers["Sunset"] = "Wed, 01 Jan 2026 00:00:00 GMT"
    response.headers["Deprecation"] = "true"
    response.headers["Link"] = '</api/v2/documents>; rel="successor-version"'
    # ... rest of implementation
```

## Benefits of This Structure

### 1. **Non-Breaking Changes**

- Add new features in v2 without affecting v1 clients
- Maintain backward compatibility

### 2. **Clear Organization**

- Each version in its own directory
- Easy to find and maintain version-specific code

### 3. **Gradual Migration**

- Clients can upgrade at their own pace
- Test new version before full migration

### 4. **Documentation**

- Each version has its own API docs
- Clear version history

### 5. **Team Collaboration**

- Different teams can work on different versions
- Reduces merge conflicts

## Best Practices

### DO ✅

- Version major breaking changes
- Keep versions simple (v1, v2, v3)
- Document changes between versions
- Maintain older versions during migration
- Use semantic versioning for service versions

### DON'T ❌

- Don't version every small change
- Don't have too many active versions (max 2-3)
- Don't remove versions without notice
- Don't mix version logic in same files

## Version Lifecycle

```
v1: Current (Stable)
    ↓
v2: Beta → Current (Stable)
    ↓
v1: Deprecated → Sunset → Removed
    ↓
v3: Beta → Current (Stable)
    ↓
v2: Deprecated → Sunset → Removed
```

## Testing Different Versions

```python
# tests/test_api_v1.py
def test_upload_v1(client):
    response = client.post("/api/v1/upload", ...)
    assert response.status_code == 201

# tests/test_api_v2.py
def test_upload_v2(client):
    response = client.post("/api/v2/upload", ...)
    assert response.status_code == 201
```

## Monitoring

Track version usage to plan deprecations:

```python
from fastapi import Request
import logging

@router.post("/upload")
async def upload_document(request: Request, ...):
    logging.info(f"API v1 called from {request.client.host}")
    # ... implementation
```

---

**Current Status**: ✅ v1 implemented and ready
**Next Step**: When needed, create v2 following the guide above
