# Clean Deployment and Testing Complete ✅

## What Was Done

### 1. Clean Deployment Script (`clean-deploy.sh`)
Created comprehensive deployment script that:
- ✅ Stops all services and removes volumes
- ✅ Rebuilds all Docker images
- ✅ Starts databases (PostgreSQL + Redis)
- ✅ Creates API Gateway tables (users, api_keys, refresh_tokens)
- ✅ Runs document processing migrations
- ✅ Creates default admin user
- ✅ Starts all services (phase4 profile)
- ✅ Health checks

### 2. Default Admin User
Created system with default credentials:
- **Email**: `admin@example.com`
- **Password**: `admin123`
- **Role**: admin
- **Status**: Email verified, active

⚠️ **Remember to change the password after first login!**

### 3. Database Initialization Scripts
Created two helper scripts:

#### `create_tables.py` (API Gateway)
- Creates users table
- Creates api_keys table  
- Creates refresh_tokens table
- Auto-runs during deployment

#### `init_admin.py` (API Gateway)
- Creates default admin user
- Checks for existing admin
- Configurable via environment variables:
  - `DEFAULT_ADMIN_EMAIL`
  - `DEFAULT_ADMIN_PASSWORD`
  - `DEFAULT_ADMIN_NAME`

### 4. Test Paper Upload
Successfully uploaded 7 research papers:

1. AnAlgebraicFoundation (ID: 3)
2. Research Knowledge Graphs (ID: 4)
3. Zou 2020 Physics Conference (ID: 5)
4. Knowledge Graphs (ID: 6)
5. Open Access proceedings Journal (ID: 7)
6. Survey of RDF stores & SPARQL engines (ID: 8)
7. Universal Data Model for Multi-Paradigm Data Lakes (ID: 9)

All documents processed and indexed in Vector DB!

---

## System Status

### Running Services
```
✓ PostgreSQL (port 5432)
✓ Redis (port 6379)
✓ API Gateway (port 8000)
✓ Document Processing (port 8001)
✓ Vector DB (port 8002) - GPU accelerated
✓ LLM Service (port 8003)
✓ Celery Worker (4 queues)
✓ Flower Monitor (port 5555)
✓ Frontend (port 3000)
```

### Health Check
```bash
$ curl http://localhost:8000/api/v1/health
{"status": "healthy"}
```

---

## How to Use

### 1. Login to System
Navigate to: **http://localhost:3000/login**

Credentials:
- Email: `admin@example.com`
- Password: `admin123`

### 2. Test Search
Navigate to: **http://localhost:3000/search**

Try queries like:
- "knowledge graphs"
- "data lakes"
- "RDF stores"
- "machine learning"

Features:
- Filter by document
- Filter by section (abstract, methodology, etc.)
- Adjust max results
- View similarity scores
- Click to view full document

### 3. Test AI Analysis
Navigate to: **http://localhost:3000/analysis**

Features:
- Select any uploaded document
- Choose analysis type:
  - Summary
  - Key Findings
  - Methodology
  - Literature Review
  - Results Analysis
  - Limitations
  - Future Work
  - Custom (enter your own prompt)
- Select LLM provider (OpenAI/Anthropic)
- Toggle RAG on/off
- Download or copy results

### 4. Other Features
- **Batch Upload**: http://localhost:3000/batch-upload
- **Processing Jobs**: http://localhost:3000/jobs
- **Profile**: http://localhost:3000/profile
- **Dashboard**: http://localhost:3000/dashboard

---

## Quick Commands

### View Logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f api-gateway-service
docker-compose logs -f document-processing-service
docker-compose logs -f vector-db-service
docker-compose logs -f llm-service
docker-compose logs -f celery-worker
```

### Check Service Status
```bash
docker-compose ps
```

### Restart a Service
```bash
docker-compose restart api-gateway-service
```

### Upload More Papers
```bash
# Place PDFs in the root directory, then:
./simple-upload.sh admin@example.com admin123
```

### Clean Redeploy (if needed)
```bash
./clean-deploy.sh
```

---

## Files Created/Modified

### New Scripts
1. **`clean-deploy.sh`** - Complete deployment automation
2. **`simple-upload.sh`** - Easy paper upload script
3. **`upload-test-papers.sh`** - Comprehensive upload with stats
4. **`services/api-gateway/create_tables.py`** - DB table creation
5. **`services/api-gateway/init_admin.py`** - Admin user initialization

### Updated Files
1. **`.env`** - Added default admin credentials
2. **Frontend pages** - Search and Analysis UI complete

---

## Testing Checklist

### ✅ Completed
- [x] Clean deployment successful
- [x] All services running
- [x] Health check passing
- [x] Admin user created
- [x] 7 papers uploaded
- [x] Vector DB processing complete
- [x] Login works
- [x] Frontend accessible

### 🧪 Ready for Testing
- [ ] Search functionality (try different queries)
- [ ] Analysis with different types
- [ ] Batch upload
- [ ] Job monitoring
- [ ] Profile management

---

## System Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Frontend (Next.js)                   │
│              http://localhost:3000                       │
└────────────────────────┬────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────┐
│                  API Gateway (8000)                      │
│  • Authentication (JWT + HttpOnly Cookies)               │
│  • Request routing                                       │
│  • Health monitoring                                     │
└─┬──────────┬───────────┬──────────┬──────────────────────┘
  │          │           │          │
  ▼          ▼           ▼          ▼
┌──────┐ ┌────────┐ ┌────────┐ ┌────────┐
│ Doc  │ │Vector  │ │  LLM   │ │Celery  │
│Process│ │  DB    │ │Service │ │Worker  │
│(8001)│ │ (8002) │ │ (8003) │ │        │
└──┬───┘ └───┬────┘ └───┬────┘ └───┬────┘
   │         │          │          │
   └─────────┴──────────┴──────────┘
                   │
      ┌────────────┴────────────┐
      ▼                         ▼
┌──────────┐            ┌──────────┐
│PostgreSQL│            │  Redis   │
│  (5432)  │            │  (6379)  │
└──────────┘            └──────────┘
```

---

## Next Steps

1. **Test Search**:
   - Try semantic queries
   - Filter by document/section
   - Check similarity scores

2. **Test Analysis**:
   - Analyze uploaded papers
   - Try different analysis types
   - Compare RAG vs non-RAG results

3. **Change Admin Password**:
   - Login → Profile → Change password

4. **Upload More Papers**:
   - Use batch upload feature
   - Monitor jobs page

5. **Explore API**:
   - API docs: http://localhost:8000/docs
   - Health: http://localhost:8000/api/v1/health

---

## Troubleshooting

### If services won't start:
```bash
./clean-deploy.sh
```

### If login doesn't work:
```bash
# Recreate admin user
docker-compose run --rm api-gateway python init_admin.py
```

### If uploads fail:
```bash
# Check logs
docker-compose logs -f document-processing-service
docker-compose logs -f celery-worker
```

### If search returns no results:
```bash
# Check Vector DB logs
docker-compose logs -f vector-db-service

# Verify documents are processed
curl -s http://localhost:8000/api/v1/documents | jq .
```

---

## Success! 🎉

Your Research Paper Analysis system is fully deployed and ready to use!

**Admin Credentials:**
- Email: admin@example.com
- Password: admin123

**Access Points:**
- Frontend: http://localhost:3000
- API Gateway: http://localhost:8000
- API Docs: http://localhost:8000/docs
- Flower (Celery): http://localhost:5555

Happy researching! 📚🔬
