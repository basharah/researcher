from fastapi import FastAPI

app = FastAPI(
    title="Vector Database Service",
    description="Service for generating embeddings and semantic search (Phase 2 - To be implemented)",
    version="1.0.0"
)

@app.get("/")
async def root():
    return {
        "service": "Vector Database Service",
        "status": "Phase 2 - To be implemented",
        "version": "1.0.0"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
