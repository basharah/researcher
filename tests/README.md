# Tests Directory

Python unit and integration tests for the Research Paper Analysis Chatbot.

## 🧪 Test Files

### Integration Tests

#### `test_vector_db.py`

Vector DB integration test - validates document processing and semantic search.

**What it tests:**

- Document retrieval from document-processing service
- Vector embedding generation
- Document chunk storage
- Semantic search with similarity scoring
- GPU acceleration (if available)

**Usage:**

```bash
# Ensure services are running
./scripts/start.sh

# Run the test
python tests/test_vector_db.py
```

**Expected output:**

- ✅ Document fetched successfully
- ✅ Document processed and chunked
- ✅ Semantic search returns relevant results

#### `test_vector_client_errors.py`

Vector client error handling test - validates graceful degradation.

**What it tests:**

- Network error handling
- Timeout handling
- Service unavailable scenarios
- Fallback behavior

**Usage:**

```bash
python tests/test_vector_client_errors.py
```

#### `test_service_client_errors.py`

Service client error handling test - validates API Gateway client.

**What it tests:**

- API Gateway client error handling
- Retry logic
- Connection failures
- Response parsing errors

**Usage:**

```bash
python tests/test_service_client_errors.py
```

### Feature Tests

#### `test_comprehensive.py`

Comprehensive PDF extraction test - validates all extraction features.

**What it tests:**

- Metadata extraction (title, authors, page count)
- Table extraction and parsing
- Figure extraction with captions
- Reference parsing
- Column-aware text extraction

**Usage:**

```bash
python tests/test_comprehensive.py
```

**Sample PDF required:** Place a research paper PDF in the repository root or specify path in the script.

**Expected output:**

- Metadata: title, authors, page count
- Tables: count, dimensions, captions
- Figures: count, captions, file paths
- References: count, parsed citations
- Text: column-aware extraction preview

#### `test_section_detection.py`

Section detection test - validates advanced section parsing.

**What it tests:**

- Abstract detection
- Introduction detection
- Methodology/Methods section
- Results section
- Discussion section
- Conclusion section
- References section

**Usage:**

```bash
python tests/test_section_detection.py
```

**Related documentation:** `docs/SECTION_DETECTION_IMPROVEMENTS.md`

### Ad-hoc Tests

#### `test.py`

Simple ad-hoc integration helper for quick testing.

**What it does:**

- Basic PDF parsing test
- Quick metadata extraction
- Text preview

**Usage:**

```bash
python tests/test.py
```

Modify this file for quick one-off tests during development.

## 🔧 Running Tests

### Prerequisites

```bash
# Install test dependencies
pip install -r requirements-dev.txt

# Or use the virtual environment
source .venv/bin/activate
```

### Running Individual Tests

```bash
# Run specific test
python tests/test_comprehensive.py

# Run with verbose output
python -v tests/test_vector_db.py
```

### Running All Tests

```bash
# Using pytest (if configured)
pytest tests/

# Or run individually
for test in tests/test_*.py; do python $test; done
```

## 📊 Test Coverage

### Current Coverage

- ✅ PDF extraction (metadata, tables, figures, references)
- ✅ Vector DB integration (embeddings, search)
- ✅ Section detection (abstract, intro, methods, etc.)
- ✅ Error handling (network, timeouts, service failures)

### Planned Coverage

- [ ] LLM service integration tests
- [ ] API Gateway workflow tests
- [ ] Frontend component tests
- [ ] Performance/load tests
- [ ] End-to-end user journey tests

## 🐛 Debugging Tests

### Common Issues

#### Services Not Running

```bash
# Check service health
curl http://localhost:8001/health  # Document Processing
curl http://localhost:8002/health  # Vector DB
curl http://localhost:8003/health  # LLM Service
curl http://localhost:8000/api/v1/health  # API Gateway

# Start services if needed
./scripts/start.sh
```

#### Missing Dependencies

```bash
# Install all dependencies
pip install -r requirements-dev.txt

# Or install specific packages
pip install pytest httpx pdfplumber
```

#### GPU Tests Failing

```bash
# Verify GPU setup
./scripts/verify-gpu.sh

# Check GPU availability in container
docker exec vector-db-service nvidia-smi
```

See `docs/GPU_SETUP.md` for GPU troubleshooting.

#### Database Connection Issues

```bash
# Reset database
docker-compose down -v
./scripts/start.sh
```

### Verbose Output

Add print statements or use Python's logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 📝 Test Data

### Sample PDFs

Place test PDFs in:

- `papers/` - Research papers for testing
- Root directory - Individual test files (e.g., `test_paper.pdf`)

### Test Database

Tests use the development database. For isolated testing:

```bash
# Use test-specific compose file (if available)
docker-compose -f docker-compose.test.yml up -d
```

## 🔗 Related Documentation

- **Shell Test Scripts**: `../scripts/README.md` - Bash integration tests
- **Extraction Testing**: `../docs/EXTRACTION_TESTING_SUMMARY.md` - Extraction validation results
- **Vector DB**: `../docs/PHASE2_INTEGRATION_COMPLETE.md` - Vector DB integration details
- **GPU Setup**: `../docs/GPU_SETUP.md` - GPU configuration for tests

## 🚀 Adding New Tests

### Test File Template

```python
#!/usr/bin/env python3
"""
Test description: What this test validates
"""
import requests
from pathlib import Path

def test_feature():
    """Test specific feature"""
    # Arrange
    test_data = {...}
    
    # Act
    response = requests.post("http://localhost:8001/endpoint", json=test_data)
    
    # Assert
    assert response.status_code == 200
    result = response.json()
    assert "expected_key" in result
    
    print("✅ Test passed!")

if __name__ == "__main__":
    try:
        test_feature()
    except Exception as e:
        print(f"❌ Test failed: {e}")
        raise
```

### Best Practices

1. **Descriptive names**: Use `test_<feature>_<scenario>.py`
2. **Docstrings**: Explain what the test validates
3. **Cleanup**: Reset state after tests if needed
4. **Independence**: Tests should not depend on each other
5. **Output**: Use ✅/❌ emojis for clear pass/fail

---

**Last Updated**: November 2025
**Maintainers**: Keep test documentation updated when adding new tests.
