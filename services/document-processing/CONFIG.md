# Configuration Management

## Overview

The service uses **Pydantic Settings** for type-safe configuration management. All settings are centralized in `config.py` and loaded from environment variables or `.env` file.

## Benefits

### 1. **Type Safety**

```python
from config import settings

# Type-checked and validated
port: int = settings.port  # ✅ Always an integer
debug: bool = settings.debug  # ✅ Always a boolean
```

### 2. **Environment Variables**

All settings can be overridden with environment variables:
```bash
export DATABASE_URL="postgresql://user:pass@db:5432/mydb"
export DEBUG=true
export MAX_FILE_SIZE=20971520  # 20MB
```

### 3. **.env File Support**

Create a `.env` file in the project root:
```bash
cp .env.example .env
# Edit .env with your values
```

### 4. **Validation**

Invalid values are caught immediately on startup:
```python
# ❌ This will fail validation
PORT=invalid  # Error: value is not a valid integer
```

### 5. **Default Values**

Sensible defaults are provided for all settings:
```python
max_file_size: int = 10 * 1024 * 1024  # 10MB default
debug: bool = False  # Safe default
```

## Configuration Sections

### Application Settings

```python
settings.app_name         # "Document Processing Service"
settings.app_version      # "1.0.0"
settings.debug            # false (true in development)
```

### API Settings

```python
settings.api_prefix       # "/api"
settings.api_v1_prefix    # "/v1"
settings.full_api_v1_prefix  # "/api/v1" (computed)
settings.docs_url         # "/docs"
settings.redoc_url        # "/redoc"
```

### Server Settings

```python
settings.host             # "0.0.0.0"
settings.port             # 8000
```

### CORS Settings

```python
settings.cors_origins           # ["*"]
settings.cors_allow_credentials # true
settings.cors_allow_methods     # ["*"]
settings.cors_allow_headers     # ["*"]
```

### Database Settings

```python
settings.database_url     # PostgreSQL connection string
settings.database_echo    # false (true to see SQL queries)
```

### Redis Settings

```python
settings.redis_url        # "redis://localhost:6379"
settings.redis_db         # 0
settings.redis_decode_responses  # true
```

### File Upload Settings

```python
settings.upload_dir       # Path("./uploads")
settings.max_file_size    # 10485760 (10MB)
settings.allowed_extensions  # ["pdf"]
```

### PDF Processing Settings

```python
settings.pdf_extraction_timeout  # 60 seconds
settings.max_page_count          # 500 pages
```

### Service URLs (Phase 4)

```python
settings.vector_service_url  # Optional[str]
settings.llm_service_url     # Optional[str]
```

### Security Settings

```python
settings.secret_key       # Optional[str]
settings.api_key          # Optional[str]
```

### LLM API Keys (Phase 3)

```python
settings.openai_api_key     # Optional[str]
settings.anthropic_api_key  # Optional[str]
```

### Logging Settings

```python
settings.log_level        # "INFO"
settings.log_format       # "json" or "text"
```

## Usage Examples

### In FastAPI Application

```python
from fastapi import FastAPI
from config import settings

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    debug=settings.debug,
    docs_url=settings.docs_url
)
```

### In Endpoints

```python
from config import settings

@router.post("/upload")
async def upload(file: UploadFile):
    if file.size > settings.max_file_size:
        raise HTTPException(
            status_code=413,
            detail=f"Max size: {settings.max_file_size} bytes"
        )
    
    file_path = settings.upload_dir / file.filename
    # ... process file
```

### In Database Configuration

```python
from sqlalchemy import create_engine
from config import settings

engine = create_engine(
    settings.database_url,
    echo=settings.database_echo
)
```

### Computed Properties

```python
from config import settings

# Automatic path creation
settings.create_upload_dir()

# Computed full API path
full_path = settings.full_api_v1_prefix  # "/api/v1"
```

## Environment Variables

All settings support environment variable overrides using uppercase names:

| Setting | Environment Variable | Example |
|---------|---------------------|---------|
| `app_name` | `APP_NAME` | `"My Service"` |
| `port` | `PORT` | `8080` |
| `debug` | `DEBUG` | `true` |
| `database_url` | `DATABASE_URL` | `postgresql://...` |
| `max_file_size` | `MAX_FILE_SIZE` | `20971520` |
| `openai_api_key` | `OPENAI_API_KEY` | `sk-...` |

### Loading Priority

1. Environment variables (highest priority)
2. `.env` file
3. Default values in `config.py` (lowest priority)

## Docker Environment Variables

### In docker-compose.yml

```yaml
services:
  document-processing:
    environment:
      - DATABASE_URL=postgresql://researcher:pass@postgres:5432/db
      - REDIS_URL=redis://redis:6379
      - MAX_FILE_SIZE=20971520
      - DEBUG=false
```

### In Dockerfile

```dockerfile
ENV APP_NAME="Document Processing Service"
ENV PORT=8000
ENV LOG_LEVEL=INFO
```

## Development vs Production

### Development (.env)

```bash
DEBUG=true
DATABASE_ECHO=true
LOG_LEVEL=DEBUG
LOG_FORMAT=text
CORS_ORIGINS=*
```

### Production (Environment Variables)

```bash
export DEBUG=false
export DATABASE_ECHO=false
export LOG_LEVEL=INFO
export LOG_FORMAT=json
export CORS_ORIGINS=https://yourdomain.com,https://app.yourdomain.com
export SECRET_KEY=$(openssl rand -hex 32)
export OPENAI_API_KEY=sk-prod-key-here
```

## Testing Configuration

### Override in Tests

```python
from config import Settings

def test_with_custom_config():
    test_settings = Settings(
        database_url="sqlite:///test.db",
        max_file_size=1024,
        debug=True
    )
    # Use test_settings instead of global settings
```

### Mock Settings

```python
from unittest.mock import patch
from config import settings

def test_upload():
    with patch.object(settings, 'max_file_size', 1024):
        # Test with 1KB limit
        pass
```

## Adding New Settings

### 1. Add to config.py

```python
class Settings(BaseSettings):
    # ... existing settings
    
    # New setting
    new_feature_enabled: bool = False
    new_timeout: int = 30
```

### 2. Add to .env.example

```bash
# New Feature Settings
NEW_FEATURE_ENABLED=false
NEW_TIMEOUT=30
```

### 3. Update Documentation

Add to this README with description and usage examples.

### 4. Use in Code

```python
from config import settings

if settings.new_feature_enabled:
    # Use new feature
    pass
```

## Validation Examples

### Custom Validators

```python
from pydantic import field_validator

class Settings(BaseSettings):
    port: int
    
    @field_validator('port')
    def validate_port(cls, v):
        if not (1024 <= v <= 65535):
            raise ValueError('Port must be between 1024 and 65535')
        return v
```

### Dependent Fields

```python
from pydantic import model_validator

class Settings(BaseSettings):
    database_url: str
    database_echo: bool
    
    @model_validator(mode='after')
    def check_production_settings(self):
        if not self.debug and self.database_echo:
            raise ValueError('database_echo should be False in production')
        return self
```

## Best Practices

### DO ✅

- Use `settings` singleton throughout the app
- Set sensitive values via environment variables
- Use type hints for all settings
- Provide sensible defaults
- Document all settings in .env.example
- Validate settings on startup

### DON'T ❌

- Hardcode configuration values
- Store secrets in code or .env files in git
- Create multiple Settings instances
- Use string types for everything
- Skip validation

## Security Notes

### Sensitive Values

Never commit these to git:
- API keys
- Secret keys
- Database passwords
- Production URLs

### .gitignore

Ensure `.env` is in `.gitignore`:
```
.env
.env.local
.env.production
```

### Production Checklist

- [ ] Set `DEBUG=false`
- [ ] Use strong `SECRET_KEY`
- [ ] Restrict `CORS_ORIGINS`
- [ ] Set `DATABASE_ECHO=false`
- [ ] Use environment variables (not .env file)
- [ ] Rotate API keys regularly
- [ ] Enable HTTPS
- [ ] Set appropriate log levels

## Troubleshooting

### Settings Not Loading

```python
# Check if .env file exists
from pathlib import Path
print(Path('.env').exists())

# Print current settings
from config import settings
print(settings.model_dump())
```

### Type Conversion Errors

```bash
# Wrong: PORT=8000 (string)
# Right: PORT=8000 (will be converted to int)

# Wrong: DEBUG=False (string "False" is truthy!)
# Right: DEBUG=false or DEBUG=0
```

### Environment Variable Not Working

```bash
# Check if variable is set
echo $DATABASE_URL

# Verify loading
python3 -c "from config import settings; print(settings.database_url)"
```

---

**Configuration is now centralized, type-safe, and easy to manage!** 🎉
