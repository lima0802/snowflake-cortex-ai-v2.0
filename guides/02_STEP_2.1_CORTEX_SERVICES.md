# Step 2.1: Implement Cortex Service Wrappers

**Phase:** 2 - Core Services Implementation  
**Goal:** Build Python wrappers for each Cortex service  
**Status:** ⏳ Not Started

---

## Overview

This step involves creating Python wrapper classes for all four Snowflake Cortex services:
1. Cortex Analyst (NL-to-SQL)
2. Cortex Complete (LLM generation)
3. Cortex Search (Vector search)
4. Cortex ML (Anomaly detection, forecasting)

---

## Prerequisites

- [ ] Step 1.1: Docker environment running
- [ ] Step 1.2: Data layer setup complete
- [ ] Snowflake credentials configured in `.env`
- [ ] `orchestrator/requirements.txt` includes Snowflake packages

---

## Implementation Priority Order

### 1. Cortex Analyst Wrapper

**File:** `orchestrator/services/cortex_analyst.py`

**Tasks:**
- [ ] Create `CortexAnalyst` class
- [ ] Implement `send_message()` method for NL-to-SQL conversion
- [ ] Handle semantic model loading from stage
- [ ] Parse SQL results and metadata
- [ ] Add error handling for invalid queries
- [ ] Add logging for debugging

**Example Usage:**
```python
from services.cortex_analyst import CortexAnalyst

analyst = CortexAnalyst()
response = analyst.send_message("What was total emails sent last month?")
print(response.sql)
print(response.results)
```

**Test Query:**
```python
# Test with simple query
result = analyst.send_message("Show me click rate by market")
assert result.sql is not None
assert len(result.results) > 0
```

---

### 2. Cortex Complete Wrapper

**File:** `orchestrator/services/cortex_complete.py`

**Tasks:**
- [ ] Create `CortexComplete` class
- [ ] Implement `complete()` method for LLM generation
- [ ] Support prompt templates
- [ ] Handle streaming responses (optional)
- [ ] Add model selection (mixtral, llama, etc.)
- [ ] Add temperature and max_tokens parameters

**Example Usage:**
```python
from services.cortex_complete import CortexComplete

complete = CortexComplete()
summary = complete.complete(
    prompt="Summarize these metrics: {data}",
    model="mistral-large",
    temperature=0.7
)
```

**Test:**
```python
# Test with sample prompt
response = complete.complete("Explain what click rate means in email marketing")
assert len(response) > 0
```

---

### 3. Cortex Search Wrapper

**File:** `orchestrator/services/cortex_search.py`

**Tasks:**
- [ ] Create `CortexSearch` class
- [ ] Implement `search()` method for vector search
- [ ] Handle filter parameters
- [ ] Parse relevance scores
- [ ] Support fuzzy matching for campaign names

**Example Usage:**
```python
from services.cortex_search import CortexSearch

search = CortexSearch()
results = search.search(
    query="summer campaign",
    service_name="campaign_search",
    top_k=10
)
```

**Test:**
```python
# Test campaign search
results = search.search("newsletter")
assert len(results) > 0
assert results[0].relevance_score > 0.5
```

---

### 4. Cortex ML Wrapper

**File:** `orchestrator/services/cortex_ml.py`

**Tasks:**
- [ ] Create `CortexML` class
- [ ] Implement `detect_anomalies()` method
- [ ] Implement `forecast()` method
- [ ] Implement `contribution_analysis()` method
- [ ] Handle time series data format

**Example Usage:**
```python
from services.cortex_ml import CortexML

ml = CortexML()

# Anomaly detection
anomalies = ml.detect_anomalies(
    table="VW_SFMC_EMAIL_PERFORMANCE",
    timestamp_col="SEND_DATE",
    metric_col="CLICK_RATE"
)

# Forecasting
forecast = ml.forecast(
    table="VW_SFMC_EMAIL_PERFORMANCE",
    timestamp_col="SEND_DATE",
    target_col="EMAILS_SENT",
    periods=30
)
```

**Test:**
```python
# Test anomaly detection
anomalies = ml.detect_anomalies(sample_data)
assert "anomalies" in anomalies
```

---

## Testing Approach

### Unit Tests

Create test file: `tests/test_cortex_services.py`

```python
import pytest
from orchestrator.services import (
    CortexAnalyst,
    CortexComplete,
    CortexSearch,
    CortexML
)

def test_cortex_analyst():
    analyst = CortexAnalyst()
    result = analyst.send_message("What was click rate last month?")
    assert result is not None

def test_cortex_complete():
    complete = CortexComplete()
    result = complete.complete("What is email marketing?")
    assert len(result) > 0

def test_cortex_search():
    search = CortexSearch()
    results = search.search("campaign")
    assert len(results) >= 0

def test_cortex_ml():
    ml = CortexML()
    # Test with sample data
    pass
```

### Run Tests

```powershell
# Inside Docker container
docker exec dia-orchestrator pytest tests/test_cortex_services.py -v

# Or locally
cd orchestrator
pytest tests/test_cortex_services.py -v
```

---

## Integration with Main App

Update `orchestrator/main.py` to use services:

```python
from services.cortex_analyst import CortexAnalyst
from services.cortex_complete import CortexComplete

analyst = CortexAnalyst()
complete = CortexComplete()

@app.post("/api/v1/query")
async def query(request: QueryRequest):
    # Use Cortex Analyst for SQL generation
    analyst_response = analyst.send_message(request.query)
    
    # Use Cortex Complete for natural language summary
    summary = complete.complete(
        f"Summarize these results: {analyst_response.results}"
    )
    
    return {
        "query": request.query,
        "sql": analyst_response.sql,
        "results": analyst_response.results,
        "summary": summary
    }
```

---

## Deliverables

- [ ] `orchestrator/services/cortex_analyst.py` - Functional with tests
- [ ] `orchestrator/services/cortex_complete.py` - Functional with tests
- [ ] `orchestrator/services/cortex_search.py` - Functional with tests
- [ ] `orchestrator/services/cortex_ml.py` - Functional with tests
- [ ] `tests/test_cortex_services.py` - All tests passing
- [ ] Integration with main FastAPI app
- [ ] Documentation strings added to all methods

---

## Success Criteria

✅ All 4 Cortex services functional with unit tests  
✅ Response format matches Pydantic models  
✅ Error handling implemented  
✅ Logging configured  
✅ Integration tested with sample queries  

---

## Troubleshooting

### Issue: Connection to Snowflake fails
**Solution:** Verify `.env` credentials, check network access

### Issue: Semantic model not found
**Solution:** Ensure Step 1.2 completed, check stage: `LIST @SEMANTIC_MODELS;`

### Issue: Cortex services not available
**Solution:** Verify Cortex services enabled in Snowflake account

---

## Next Steps

After completing this step:
- [ ] Proceed to Step 2.2: Intent Classification
- [ ] Test each service individually
- [ ] Document any API limitations discovered

---

**Related Documentation:**
- [Step 1.2: Data Layer Setup](01_STEP_1.2_DATA_LAYER_SETUP.md)
- [Step 2.2: Intent Classifier](03_STEP_2.2_INTENT_CLASSIFIER.md)
- [DIA v2 Implementation Plan](../DIA_V2_IMPLEMENTATION_PLAN.md)

---

**Status:** Ready to implement ✅  
**Estimated Time:** 2-3 days  
**Last Updated:** February 22, 2026
