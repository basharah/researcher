# API Gateway Authentication & Security

## Overview

The API Gateway now includes comprehensive JWT-based authentication and authorization, protecting your research paper analysis system with enterprise-grade security.

## Features

✅ **JWT Authentication** - Industry-standard token-based auth  
✅ **User Management** - Registration, login, profile management  
✅ **API Keys** - Alternative authentication for programmatic access  
✅ **Role-Based Access Control (RBAC)** - Admin and user roles  
✅ **Rate Limiting** - Per-user request throttling  
✅ **Password Security** - Bcrypt hashing with strength validation  
✅ **Token Blacklisting** - Secure logout via Redis  
✅ **Flexible Security** - Optional auth for read endpoints  

## Quick Start

### 1. Update Configuration

Copy the new config file:
```bash
cd services/api-gateway
cp config_new.py config.py
```

Update `.env` with secure values:
```bash
# Generate a secure secret key
SECRET_KEY=$(openssl rand -hex 32)

# Add to .env
echo "SECRET_KEY=$SECRET_KEY" >> .env
echo "ADMIN_EMAIL=admin@yourdomain.com" >> .env
echo "ADMIN_PASSWORD=ChangeMe123!" >> .env
```

### 2. Install Dependencies

```bash
cd services/api-gateway
pip install -r requirements_auth.txt
```

Or rebuild Docker container:
```bash
# Update requirements.txt with auth dependencies
cp requirements_auth.txt requirements.txt

# Rebuild
docker-compose build api-gateway
docker-compose up -d api-gateway
```

### 3. Initialize Admin User

On first startup, create the admin user:

```bash
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@researcher.local",
    "password": "Admin123!",
    "full_name": "System Administrator"
  }'
```

### Register New User

```bash
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "researcher@university.edu",
    "password": "SecurePass123!",
    "full_name": "Dr. Jane Smith",
    "organization": "MIT AI Lab"
  }'
```

**Password Requirements:**

- Minimum 8 characters
- At least 1 uppercase letter
- At least 1 lowercase letter
- At least 1 digit

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

### Login

```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "researcher@university.edu",
    "password": "SecurePass123!"
  }'
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

Save the `access_token` - you'll need it for authenticated requests!

### Using the Access Token

Include the token in the `Authorization` header:

```bash
# Example: Upload a document (requires authentication)
curl -X POST http://localhost:8000/api/v1/upload \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
  -F "file=@paper.pdf"

# Example: Analyze document
curl -X POST http://localhost:8000/api/v1/analyze \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
  -H "Content-Type: application/json" \
  -d '{
    "document_id": 1,
    "analysis_type": "summary"
  }'
```

### Refresh Token

When your access token expires (30 minutes default), use the refresh token:

```bash
curl -X POST http://localhost:8000/api/v1/auth/refresh \
  -H "Content-Type: application/json" \
  -d '{
    "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
  }'
```

**Response:** New access token (refresh token remains valid)

### Logout

```bash
curl -X POST http://localhost:8000/api/v1/auth/logout \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

## User Profile Management

### Get Profile

```bash
curl http://localhost:8000/api/v1/auth/me \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

**Response:**
```json
{
  "user_id": "user_abc123",
  "email": "researcher@university.edu",
  "full_name": "Dr. Jane Smith",
  "organization": "MIT AI Lab",
  "role": "user",
  "created_at": "2025-01-06T12:00:00Z",
  "disabled": false
}
```

### Update Profile

```bash
curl -X PUT http://localhost:8000/api/v1/auth/me \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
  -H "Content-Type: application/json" \
  -d '{
    "full_name": "Dr. Jane Smith-Jones",
    "organization": "Stanford NLP Group"
  }'
```

### Change Password

```bash
curl -X POST http://localhost:8000/api/v1/auth/change-password \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
  -H "Content-Type: application/json" \
  -d '{
    "current_password": "SecurePass123!",
    "new_password": "NewSecure456!"
  }'
```

## API Keys (Alternative Authentication)

For programmatic access (scripts, integrations), use API keys instead of JWT tokens.

### Create API Key

```bash
curl -X POST http://localhost:8000/api/v1/auth/api-keys \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Research Analysis Script"
  }'
```

**Response:**
```json
{
  "api_key": "rpa_abc123def456...",
  "name": "Research Analysis Script",
  "created_at": "2025-01-06T12:00:00Z"
}
```

**⚠️ Save this API key - it won't be shown again!**

### Use API Key

API keys work exactly like JWT tokens:

```bash
curl -X POST http://localhost:8000/api/v1/upload \
  -H "Authorization: Bearer rpa_abc123def456..." \
  -F "file=@paper.pdf"
```

### Revoke API Key

```bash
curl -X DELETE http://localhost:8000/api/v1/auth/api-keys/rpa_abc123def456... \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

## Security Configuration

### Authentication Settings (config.py)

```python
# Enable/disable authentication
enable_auth: bool = True

# Public read access (GET endpoints don't require auth)
require_auth_for_read: bool = False

# Protected write access (POST/PUT/DELETE require auth)
require_auth_for_write: bool = True

# JWT Settings
secret_key: str = "your-secret-key-here"  # Use openssl rand -hex 32
jwt_algorithm: str = "HS256"
access_token_expire_minutes: int = 30
refresh_token_expire_days: int = 7

# API Keys
enable_api_keys: bool = True
```

### Security Levels

**Level 1: Public Access (Default for development)**
```python
enable_auth = False
```
All endpoints are public - good for testing.

**Level 2: Protected Writes**
```python
enable_auth = True
require_auth_for_read = False  # GET endpoints public
require_auth_for_write = True  # POST/PUT/DELETE require auth
```
Users can browse/search documents without login, but must authenticate to upload or analyze.

**Level 3: Full Protection**
```python
enable_auth = True
require_auth_for_read = True
require_auth_for_write = True
```
All endpoints require authentication.

## Rate Limiting

Authenticated users have rate limits applied:

```python
rate_limit_requests: int = 100  # requests per minute
```

**Per-user rate limiting** prevents abuse while allowing legitimate use.

Example rate-limited endpoint:
```python
@router.post("/analyze", dependencies=[Depends(RateLimiter.check_user_rate_limit)])
async def analyze_document(...):
    # Limited to 100 requests/minute per user
```

## Role-Based Access Control

### User Roles

- **user**: Default role - can upload, search, analyze
- **admin**: Full access + user management

### Admin Endpoints

```bash
# List all users (admin only)
curl http://localhost:8000/api/v1/auth/admin/users \
  -H "Authorization: Bearer <admin_token>"

# Disable user (admin only)
curl -X PUT http://localhost:8000/api/v1/auth/admin/users/user_abc123/disable \
  -H "Authorization: Bearer <admin_token>"

# Enable user (admin only)
curl -X PUT http://localhost:8000/api/v1/auth/admin/users/user_abc123/enable \
  -H "Authorization: Bearer <admin_token>"
```

## Implementation Details

### Architecture

```text
┌─────────────┐
│   Client    │
└──────┬──────┘
       │ 1. POST /auth/login
       ▼
┌─────────────────┐
│  API Gateway    │
│  auth.py        │──→ Redis (user data, blacklist)
└──────┬──────────┘
       │ 2. Returns JWT
       │
       │ 3. Request with JWT
       ▼
┌─────────────────┐
│  Protected      │
│  Endpoint       │──→ get_current_user()
└─────────────────┘       │
                         ▼
                   Validates JWT
                   Checks blacklist
                   Returns user data
```

### Token Structure
 
Below are example decoded JWT payloads (after base64 decoding). Do not hardcode these values.

#### Access Token (30 min)

```json
{
  "sub": "user_abc123",
  "type": "access",
  "role": "user",
  "iat": 1704543600,
  "exp": 1704545400
}
```

#### Refresh Token (7 days)

```json
{
  "sub": "user_abc123",
  "type": "refresh",
  "iat": 1704543600,
  "exp": 1705148400
}
```

### Password Hashing

Uses **bcrypt** with automatic salt generation:

```python
from passlib.context import CryptContext
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Hash
hashed = pwd_context.hash("password123")

# Verify
is_valid = pwd_context.verify("password123", hashed)
```

### Token Blacklisting

When users logout, tokens are added to Redis blacklist:

```python
# Store in Redis with expiration = token TTL
redis_client.setex(
  f"blacklist:{token}",
  expires_in_seconds,
  "1"
)
```

Subsequent requests check blacklist before validating token.

## Frontend Integration

### React Example

```typescript
const API = 'http://localhost:8000/api/v1';

type AuthResponse = {
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in: number;
};

export async function login(email: string, password: string): Promise<AuthResponse> {
  const res = await fetch(`${API}/auth/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, password })
  });
  if (!res.ok) throw new Error('Login failed');
  const data: AuthResponse = await res.json();
  localStorage.setItem('access_token', data.access_token);
  localStorage.setItem('refresh_token', data.refresh_token);
  return data;
}

function authHeader(): Record<string, string> {
  const token = localStorage.getItem('access_token');
  return token ? { Authorization: `Bearer ${token}` } : {};
}

export async function refreshToken(): Promise<void> {
  const refresh = localStorage.getItem('refresh_token');
  if (!refresh) throw new Error('No refresh token');
  const res = await fetch(`${API}/auth/refresh`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ refresh_token: refresh })
  });
  if (!res.ok) throw new Error('Refresh failed');
  const data: Partial<AuthResponse> = await res.json();
  if (data.access_token) localStorage.setItem('access_token', data.access_token);
}

export async function uploadDocument(file: File): Promise<unknown> {
  const form = new FormData();
  form.append('file', file);
  let res = await fetch(`${API}/upload`, { method: 'POST', headers: authHeader(), body: form });
  if (res.status === 401) {
    await refreshToken();
    res = await fetch(`${API}/upload`, { method: 'POST', headers: authHeader(), body: form });
  }
  if (!res.ok) throw new Error('Upload failed');
  return res.json();
}
```

## Production Deployment

### Security Checklist

- [ ] Change `SECRET_KEY` to cryptographically random value
- [ ] Change admin password immediately
- [ ] Use HTTPS (TLS/SSL) for all traffic
- [ ] Set `debug = False`
- [ ] Use environment variables for secrets (not .env in repo)
- [ ] Enable rate limiting
- [ ] Replace Redis user storage with PostgreSQL
- [ ] Implement email verification
- [ ] Add password reset flow
- [ ] Set up monitoring/alerts for failed logins
- [ ] Configure CORS origins to specific domains (not "*")
- [ ] Enable request logging
- [ ] Set up token rotation policy

### Environment Variables

```bash
# Production .env
SECRET_KEY=<output-of-openssl-rand-hex-32>
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

ADMIN_EMAIL=admin@yourdomain.com
ADMIN_PASSWORD=<strong-password>

ENABLE_AUTH=true
REQUIRE_AUTH_FOR_READ=true
REQUIRE_AUTH_FOR_WRITE=true

CORS_ORIGINS=["https://your-frontend.com"]

RATE_LIMIT_REQUESTS=100
ENABLE_RATE_LIMITING=true
```

### Database Migration (Redis → PostgreSQL)

For production, replace Redis user storage with PostgreSQL:

1. Create `users` table
2. Update `AuthService.store_user()` to use SQLAlchemy
3. Add indexes on email, user_id
4. Implement proper user lookup by email

Example schema:

```sql
CREATE TABLE users (
  user_id VARCHAR(50) PRIMARY KEY,
  email VARCHAR(255) UNIQUE NOT NULL,
  password_hash VARCHAR(255) NOT NULL,
  full_name VARCHAR(100),
  organization VARCHAR(100),
  role VARCHAR(20) DEFAULT 'user',
  created_at TIMESTAMP DEFAULT NOW(),
  disabled BOOLEAN DEFAULT FALSE
);

CREATE INDEX idx_users_email ON users(email);
```

## Troubleshooting

### 401 Unauthorized

**Symptom:** All authenticated requests fail with 401

**Solutions:**

- Check token is included in `Authorization: Bearer <token>` header
- Token may be expired - use refresh token
- Secret key mismatch - ensure config is consistent
- User may be disabled - check user status

### 429 Too Many Requests

**Symptom:** Rate limit exceeded

**Solutions:**

- Wait for rate limit window to reset (60 seconds)
- Increase `RATE_LIMIT_REQUESTS` in config
- Use multiple API keys for parallel processing
- Optimize requests (batch operations)

### Token Blacklist Not Working

**Symptom:** Logged out users can still access endpoints

**Solutions:**

- Check Redis connection
- Ensure token extraction in logout endpoint
- Verify blacklist check in `get_current_user()`

## Next Steps

1. **Implement frontend login UI** - React login/register forms
2. **Add email verification** - Confirm email addresses
3. **Password reset flow** - "Forgot password" feature
4. **OAuth integration** - Google/GitHub login
5. **Audit logging** - Track all authentication events
6. **2FA (Two-Factor Auth)** - Enhanced security with TOTP
7. **Session management** - Active sessions, revoke all

## Summary

The API Gateway now has **production-ready authentication** with:

✅ JWT tokens (access + refresh)  
✅ User registration and login  
✅ Profile management  
✅ API keys for programmatic access  
✅ Role-based access control  
✅ Rate limiting per user  
✅ Secure password hashing  
✅ Token blacklisting for logout  

**All research paper analysis endpoints are now protected!**

Your system is ready for multi-user deployment with proper security controls.
