"""
DIA v2.0 Orchestrator - FastAPI Application
Main entry point for the orchestration service
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Create FastAPI application
app = FastAPI(
    title="DIA v2.0 Orchestrator",
    description="Direct Marketing Analytics Intelligence Orchestrator",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "DIA v2.0 Orchestrator",
        "status": "running",
        "version": "2.0.0",
        "docs": "/docs"
    }

# Health check endpoint
@app.get("/api/v1/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "orchestrator",
        "snowflake": {
            "account": os.getenv("SNOWFLAKE_ACCOUNT"),
            "database": os.getenv("SNOWFLAKE_DATABASE"),
            "schema": os.getenv("SNOWFLAKE_SCHEMA")
        }
    }

# Query endpoint (placeholder)
@app.post("/api/v1/query")
async def query(request: dict):
    """
    Main query endpoint
    TODO: Implement intent classification and routing
    """
    return {
        "status": "not_implemented",
        "message": "Query endpoint will be implemented in Phase 2",
        "received": request
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
