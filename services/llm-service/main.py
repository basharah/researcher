from fastapi import FastAPI

app = FastAPI(
    title="LLM Service",
    description="Service for AI-powered analysis using OpenAI/Claude (Phase 3 - To be implemented)",
    version="1.0.0"
)

@app.get("/")
async def root():
    return {
        "service": "LLM Service",
        "status": "Phase 3 - To be implemented",
        "version": "1.0.0"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
