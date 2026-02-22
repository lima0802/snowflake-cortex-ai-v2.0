# Step 3.1: Implement API Routes

**Phase:** 3 - Orchestration Layer  
**Goal:** Build FastAPI endpoints for query, health, and admin functions  
**Status:** ⏳ Not Started

---

## Overview

Create RESTful API endpoints that tie together all Cortex services, intent classification, and response enhancement.

---

## Prerequisites

- [ ] Step 2.1-2.3: All core services implemented
- [ ] FastAPI app running (Step 1.1)

---

## API Routes to Implement

### 1. Health Route

**File:** `orchestrator/api/routes/health.py`

```python
from fastapi import APIRouter
from pydantic import BaseModel
from datetime import datetime

router = APIRouter(prefix="/api/v1", tags=["health"])

class HealthResponse(BaseModel):
    status: str
    timestamp: datetime
    services: dict

@router.get("/health")
async def health_check() -> HealthResponse:
    """
    Check health of all services
    """
    services_health = {
        "snowflake": _check_snowflake(),
        "cortex_analyst": _check_analyst(),
        "cortex_complete": _check_complete()
    }
    
    overall_status = "healthy" if all(services_health.values()) else "degraded"
    
    return HealthResponse(
        status=overall_status,
        timestamp=datetime.utcnow(),
        services=services_health
    )
```

### 2. Query Route

**File:** `orchestrator/api/routes/query.py`

```python
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter(prefix="/api/v1", tags=["query"])

class QueryRequest(BaseModel):
    query: str
    session_id: str | None = None

class QueryResponse(BaseModel):
    query: str
    intent: dict
    results: dict
    enhanced_response: dict
    execution_time_ms: float

@router.post("/query")
async def query(request: QueryRequest) -> QueryResponse:
    """
    Main query endpoint - orchestrates full pipeline
    """
    start_time = time.time()
    
    # 1. Classify intent
    intent = intent_classifier.classify(request.query)
    
    # 2. Route to appropriate service(s)
    if intent.intent == "descriptive":
        results = cortex_analyst.send_message(request.query)
    elif intent.intent == "diagnostic":
        results = cortex_ml.detect_anomalies(...)
    # etc...
    
    # 3. Enhance response
    enhanced = response_enhancer.enhance(results, intent.intent, metric="click_rate")
    
    # 4. Return formatted response
    execution_time = (time.time() - start_time) * 1000
    
    return QueryResponse(
        query=request.query,
        intent=intent.dict(),
        results=results,
        enhanced_response=enhanced.dict(),
        execution_time_ms=execution_time
    )
```

### 3. Admin Route

**File:** `orchestrator/api/routes/admin.py`

```python
from fastapi import APIRouter

router = APIRouter(prefix="/api/v1/admin", tags=["admin"])

@router.get("/metrics")
async def get_metrics():
    """System metrics"""
    return {
        "total_queries": metrics.total_queries,
        "avg_response_time": metrics.avg_response_time,
        "error_rate": metrics.error_rate
    }

@router.post("/evaluate")
async def run_evaluation():
    """Run evaluation suite"""
    results = evaluation_framework.run()
    return results

@router.get("/models")
async def list_models():
    """List available ML models"""
    return ml_registry.list_models()
```

---

## Register Routes in Main App

Update `orchestrator/main.py`:

```python
from api.routes import health, query, admin

app.include_router(health.router)
app.include_router(query.router)
app.include_router(admin.router)
```

---

## Testing

```bash
# Test health endpoint
curl http://localhost:8000/api/v1/health

# Test query endpoint
curl -X POST http://localhost:8000/api/v1/query \
  -H "Content-Type: application/json" \
  -d '{"query": "What was click rate last month?"}'

# Test admin metrics
curl http://localhost:8000/api/v1/admin/metrics
```

---

## Deliverables

- [ ] Health route implemented
- [ ] Query route with full orchestration
- [ ] Admin routes functional
- [ ] API documentation updated
- [ ] Error handling added
- [ ] Logging configured

---

## Success Criteria

✅ FastAPI app with all routes functional  
✅ Full orchestration pipeline working  
✅ API documentation at /docs  
✅ Error handling and logging  

---

**Next:** [Step 3.2: Conversation Management](06_STEP_3.2_CONVERSATION_MANAGEMENT.md)  
**Estimated Time:** 1 day
