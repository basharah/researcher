from fastapi import FastAPI

app = FastAPI(
    title="API Gateway",
    description="Gateway to orchestrate all microservices (Phase 4 - To be implemented)",
    version="1.0.0"
)

@app.get("/")
async def root():
    return {
        "service": "API Gateway",
        "status": "Phase 4 - To be implemented",
        "version": "1.0.0"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
