# User Storage Architecture Guide

## Current Implementation: Redis (Temporary)

### How It Works

```
┌─────────────┐
│   Request   │
└──────┬──────┘
       │
       ▼
┌─────────────────┐
│  AuthService    │
│  .store_user()  │
└──────┬──────────┘
       │
       ▼
┌─────────────────┐
│     Redis       │
│                 │
│ Key:   user:abc │
│ Value: {JSON}   │
│ TTL:   30 days  │
└─────────────────┘
```

**Storage Format:**
```python
# Redis Key-Value
Key:   "user:user_abc123"
Value: '{"user_id":"user_abc123","email":"...","password_hash":"...","role":"user",...}'
TTL:   2592000 seconds (30 days)
```

**Limitations:**
- ❌ Data lost on Redis restart (not persistent by default)
- ❌ Cannot query by email (must know user_id)
- ❌ Users expire after 30 days
- ❌ No relationships with documents
- ❌ Memory constraints for large user bases

---

## Recommended: PostgreSQL (Production-Ready)

### Architecture

```
┌─────────────┐
│   Request   │
└──────┬──────┘
       │
       ▼
┌─────────────────┐
│   UserCRUD      │
│  .create_user() │
└──────┬──────────┘
       │
       ▼
┌─────────────────────────────┐
│        PostgreSQL           │
│                             │
│  Table: users               │
│  ├─ id (PK)                 │
│  ├─ user_id (unique)        │
│  ├─ email (unique, indexed) │
│  ├─ password_hash           │
│  ├─ full_name               │
│  ├─ organization            │
│  ├─ role (enum)             │
│  ├─ disabled                │
│  ├─ created_at              │
│  └─ last_login              │
│                             │
│  Table: api_keys            │
│  └─ FK to users.user_id     │
│                             │
│  Table: refresh_tokens      │
│  └─ FK to users.user_id     │
└─────────────────────────────┘
```

### Database Schema

**Created files for PostgreSQL:**
1. `models.py` - SQLAlchemy models (User, APIKey, RefreshToken)
2. `database.py` - Database connection and session management
3. `crud.py` - CRUD operations for users

**Tables:**

```sql
-- Users table
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(100) NOT NULL,
    organization VARCHAR(100),
    role VARCHAR(20) DEFAULT 'user',
    disabled BOOLEAN DEFAULT false,
    email_verified BOOLEAN DEFAULT false,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    last_login TIMESTAMP
);

CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_user_id ON users(user_id);

-- API Keys table
CREATE TABLE api_keys (
    id SERIAL PRIMARY KEY,
    api_key VARCHAR(100) UNIQUE NOT NULL,
    user_id VARCHAR(50) NOT NULL,
    name VARCHAR(100) NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    expires_at TIMESTAMP,
    last_used TIMESTAMP,
    disabled BOOLEAN DEFAULT false,
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);

CREATE INDEX idx_api_keys_key ON api_keys(api_key);
CREATE INDEX idx_api_keys_user ON api_keys(user_id);

-- Refresh Tokens table
CREATE TABLE refresh_tokens (
    id SERIAL PRIMARY KEY,
    token_hash VARCHAR(64) UNIQUE NOT NULL,
    user_id VARCHAR(50) NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    expires_at TIMESTAMP NOT NULL,
    revoked BOOLEAN DEFAULT false,
    user_agent VARCHAR(255),
    ip_address VARCHAR(45),
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);

CREATE INDEX idx_refresh_tokens_hash ON refresh_tokens(token_hash);
CREATE INDEX idx_refresh_tokens_user ON refresh_tokens(user_id);
```

### Benefits of PostgreSQL

✅ **Persistent** - Data survives restarts  
✅ **Queryable** - Fast email lookups with indexes  
✅ **Relationships** - Can join users with their documents  
✅ **ACID transactions** - Data consistency  
✅ **Scalable** - Handles millions of users  
✅ **No expiration** - Users don't auto-delete  
✅ **Foreign keys** - Data integrity  
✅ **Backups** - Point-in-time recovery  

---

## Migration Path: Redis → PostgreSQL

### Step 1: Add SQLAlchemy Dependency

```bash
# Update requirements_auth.txt
echo "sqlalchemy==2.0.23" >> requirements_auth.txt
echo "psycopg2-binary==2.9.9" >> requirements_auth.txt
```

### Step 2: Initialize Database

```python
# In main.py startup event
from database import init_db

@app.on_event("startup")
async def startup_event():
    # Create tables
    init_db()
    logger.info("Database initialized")
```

### Step 3: Update Auth Service

Replace Redis operations with PostgreSQL:

```python
# OLD (Redis)
from auth import AuthService
AuthService.store_user(user_data)
user = AuthService.get_user(user_id)

# NEW (PostgreSQL)
from crud import UserCRUD
from database import get_db

db = next(get_db())
UserCRUD.create_user(db, user_data, password_hash)
user = UserCRUD.get_user_by_id(db, user_id)
```

### Step 4: Update Endpoints

Use FastAPI dependency injection:

```python
from database import get_db
from crud import UserCRUD

@router.post("/register")
async def register(
    user_data: UserRegister,
    db: Session = Depends(get_db)
):
    # Create user in PostgreSQL
    password_hash = AuthService.hash_password(user_data.password)
    user = UserCRUD.create_user(db, user_data, password_hash)
    
    # Generate tokens
    access_token = AuthService.create_access_token(
        data={"sub": user.user_id, "email": user.email}
    )
    
    return Token(access_token=access_token, ...)
```

### Step 5: Update get_current_user Dependency

```python
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    token = credentials.credentials
    
    # Decode token
    payload = AuthService.decode_token(token)
    user_id = payload.get("sub")
    
    # Get user from PostgreSQL
    user = UserCRUD.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    
    if user.disabled:
        raise HTTPException(status_code=403, detail="User disabled")
    
    return user
```

---

## Hybrid Approach (Optional)

Keep Redis for **session management** and PostgreSQL for **user storage**:

```
User Data        → PostgreSQL (persistent)
  ↓
Login Creates    → Session in Redis (fast, temporary)
  ↓
Requests Check   → Redis session first (cache)
  ↓
If expired       → Query PostgreSQL (fallback)
```

### Implementation

```python
class SessionManager:
    """Hybrid: PostgreSQL for users, Redis for sessions"""
    
    @staticmethod
    def create_session(user: User, access_token: str):
        """Cache user session in Redis"""
        redis_client.setex(
            f"session:{user.user_id}",
            1800,  # 30 minutes (match token expiry)
            json.dumps(user.to_dict())
        )
    
    @staticmethod
    def get_session(user_id: str, db: Session) -> Optional[User]:
        """Get user from cache or database"""
        # Try Redis first
        cached = redis_client.get(f"session:{user.user_id}")
        if cached:
            return json.loads(cached)
        
        # Fallback to PostgreSQL
        user = UserCRUD.get_user_by_id(db, user_id)
        if user:
            # Refresh cache
            SessionManager.create_session(user, None)
        return user
```

---

## Comparison Table

| Feature | Redis (Current) | PostgreSQL (Recommended) | Hybrid |
|---------|----------------|-------------------------|--------|
| Persistence | ❌ Volatile | ✅ Persistent | ✅ Persistent |
| Query by email | ❌ Slow | ✅ Fast (indexed) | ✅ Fast |
| Relationships | ❌ None | ✅ Foreign keys | ✅ Foreign keys |
| Scalability | ⚠️ Memory limited | ✅ Disk-based | ✅ Best of both |
| Speed | ✅ Microseconds | ⚠️ Milliseconds | ✅ Cached reads fast |
| Setup complexity | ✅ Simple | ⚠️ Migrations needed | ⚠️ More complex |
| Production ready | ❌ No | ✅ Yes | ✅ Yes |

---

## Recommendation

**For Development/Testing:** 
- ✅ Redis is fine (quick setup, no migrations)

**For Production:**
- ✅ PostgreSQL (reliable, scalable, standard practice)
- Optional: Hybrid with Redis session cache for performance

**Migration Timeline:**
1. **Now:** Use Redis (as implemented) for quick testing
2. **Before production:** Migrate to PostgreSQL
3. **Optional:** Add Redis session caching later for scale

---

## Quick Setup: PostgreSQL User Storage

```bash
# 1. Add dependencies
cd services/api-gateway
cat >> requirements_auth.txt << EOF
sqlalchemy==2.0.23
psycopg2-binary==2.9.9
EOF

# 2. Update config_new.py (add database URL)
echo "database_url: str = \"postgresql://researcher:researcher_pass@postgres:5432/research_papers\"" >> config_new.py

# 3. Initialize on startup (in main.py)
# from database import init_db
# @app.on_event("startup")
# async def startup(): init_db()

# 4. Rebuild container
docker-compose build api-gateway
docker-compose up -d api-gateway

# 5. Tables auto-created on first startup
```

---

## Summary

**Current:** Redis (temporary, in-memory, volatile)  
**Recommended:** PostgreSQL (persistent, queryable, production-ready)  
**Files created:** `models.py`, `database.py`, `crud.py`  

You can switch to PostgreSQL anytime by:
1. Adding SQLAlchemy to requirements
2. Calling `init_db()` on startup
3. Replacing `AuthService` calls with `UserCRUD` calls
4. Using `Depends(get_db)` in endpoints

Both implementations are ready - you choose when to migrate!
