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

## 🎯 Understanding All Cortex Functions

### Quick Comparison Table

| Service | Primary Function | Input | Output | Use Case |
|---------|-----------------|-------|--------|----------|
| **Cortex Analyst** | Natural Language → SQL → Data | Question | SQL + Real Data | "What were sales last month?" |
| **Cortex Complete** | Text Generation (LLM) | Prompt | Generated Text | "Write 3 email subject lines" |
| **Cortex Search** | Semantic Vector Search | Query | Similar Documents | "Find campaigns about summer" |
| **Cortex ML** | Time Series Prediction | Historical Data | Forecasts/Anomalies | "Predict next week's metrics" |

---

## 📚 CORTEX ANALYST - Comprehensive Guide

### What It Does
Converts natural language questions into SQL queries and executes them against your data.

### Snowflake Function
```sql
SELECT SNOWFLAKE.CORTEX.ANALYST(
    'What was the average click rate in January?',  -- Your question
    '@SEMANTIC_MODELS/semantic.yaml'                 -- Path to semantic model
) AS response;
```

### Python Wrapper Methods

#### 1. `send_message()` - Ask Questions
```python
analyst = CortexAnalyst()
response = analyst.send_message("What were total emails sent last week?")

print(response.sql)       # Generated SQL query
print(response.results)   # Actual data from database
```

#### 2. `verify_semantic_model()` - Check Model Exists
```python
exists = analyst.verify_semantic_model()
print(f"Semantic model available: {exists}")
```

### Practical Use Cases

**Business Intelligence:**
```python
# Sales Analysis
analyst.send_message("Show me top 10 campaigns by revenue")
analyst.send_message("Compare open rates Q1 vs Q4 2025")

# Performance Metrics
analyst.send_message("What's the average bounce rate by market?")
analyst.send_message("Which segments have click rate above 5%?")

# Trend Analysis
analyst.send_message("Show me weekly email volume for last 3 months")
analyst.send_message("What's the conversion trend by day of week?")
```

**Requirements:**
- ✅ Semantic model (YAML) uploaded to Snowflake stage
- ✅ Data tables defined in semantic model
- ✅ Cortex Analyst API enabled in account

**Limitations:**
- ❌ Cannot generate creative text
- ❌ Cannot summarize in natural language (only returns SQL + data)
- ❌ Requires semantic model configuration

---

## 📚 CORTEX COMPLETE - Comprehensive Guide

### What It Does
Uses Large Language Models (LLMs) to generate text, summarize content, answer questions, and more.

### Snowflake Function
```sql
SELECT SNOWFLAKE.CORTEX.COMPLETE(
    'llama3-70b',                              -- Model name
    'Write a catchy email subject line',       -- Your prompt
    OBJECT_CONSTRUCT('temperature', 0.9)       -- Options
) AS completion;
```

### Available Models

| Model | Size | Best For | Speed | Quality |
|-------|------|----------|-------|---------|
| `llama3-70b` | 70B params | High quality, reasoning | Slower | ⭐⭐⭐⭐⭐ |
| `llama3-8b` | 8B params | Fast general use | Fast | ⭐⭐⭐⭐ |
| `mistral-large` | Large | Reasoning, analysis | Medium | ⭐⭐⭐⭐⭐ |
| `mistral-7b` | 7B params | Fast responses | Very Fast | ⭐⭐⭐ |
| `mixtral-8x7b` | 8x7B (MoE) | Balanced performance | Medium | ⭐⭐⭐⭐ |

### Python Wrapper Methods

#### 1. `complete()` - General Text Generation
```python
llm = CortexComplete(model="llama3-70b", temperature=0.8)
response = llm.complete("Write a tagline for a data analytics platform")

print(response.completion)  # Generated text
print(response.model)       # Model used
```

#### 2. `summarize()` - Text Summarization
```python
long_text = """
    The Q1 campaign ran for 3 months with 500,000 emails sent.
    We achieved 24.5% open rate and 3.2% click rate.
    Revenue was $125,000, a 15% increase from Q4.
"""

response = llm.summarize(long_text, max_length=30)
# Output: "Q1 campaign sent 500K emails achieving 24.5% opens, 3.2% clicks, and $125K revenue, up 15%."
```

#### 3. `generate_subject_lines()` - Marketing Content
```python
response = llm.generate_subject_lines(
    "Summer sale, 30% off, free shipping",
    count=5
)
# Output:
# 1. "🌞 Summer Sale: 30% Off + FREE Shipping!"
# 2. "Hot Deal Alert: Save 30% This Summer"
# 3. "Your Summer Savings Start Now - 30% Off"
```

#### 4. `analyze_sentiment()` - Sentiment Analysis
```python
response = llm.analyze_sentiment(
    "Your product is amazing! Best purchase ever!"
)
# Output: "Positive - Strong enthusiasm with superlatives indicating high satisfaction"
```

### Practical Use Cases

**Marketing Content Generation:**
```python
llm = CortexComplete(model="llama3-70b", temperature=0.9)

# Email subject lines
llm.complete("Generate 3 email subject lines for Black Friday sale")

# Ad copy
llm.complete("Write compelling ad copy for new product launch")

# Social media posts
llm.complete("Create 5 LinkedIn posts about email marketing best practices")
```

**Data Analysis & Summarization:**
```python
llm = CortexComplete(model="mistral-large", temperature=0.3)

# Summarize reports
llm.summarize(campaign_report, max_length=100)

# Explain metrics
llm.complete("Explain what a 25% open rate means in email marketing")

# Generate insights
llm.complete(f"Analyze this data and provide 3 key insights: {data}")
```

**Customer Feedback Analysis:**
```python
llm = CortexComplete(model="mistral-7b", temperature=0.2)

# Sentiment analysis
for feedback in customer_reviews:
    sentiment = llm.analyze_sentiment(feedback)
    print(f"Review: {feedback}\nSentiment: {sentiment}")
```

**Temperature Guide:**
- `0.0-0.3`: Focused, deterministic (facts, analysis, sentiment)
- `0.4-0.7`: Balanced creativity (general use)
- `0.8-1.0`: Very creative (marketing, storytelling)

**Requirements:**
- ✅ Just a prompt (no special setup needed)
- ✅ Cortex Complete enabled in account

**Limitations:**
- ❌ Cannot access your database tables
- ❌ Cannot generate SQL queries
- ❌ May "hallucinate" (make up facts) - verify important information

---

## 📚 CORTEX SEARCH - Comprehensive Guide

### What It Does
Performs semantic (meaning-based) search using vector embeddings to find similar content.

### Snowflake Function
```sql
-- First, create a Cortex Search Service
CREATE CORTEX SEARCH SERVICE campaign_knowledge
    ON content
    WAREHOUSE = COMPUTE_WH
    TARGET_LAG = '1 hour'
    AS (
        SELECT content, campaign_name, metadata
        FROM campaign_documents
    );

-- Then search
SELECT * FROM TABLE(
    campaign_knowledge!SEARCH(
        'summer promotion campaigns',
        10  -- Return top 10 results
    )
);
```

### Python Wrapper Methods

#### 1. `search()` - Semantic Search
```python
search_service = CortexSearch(service_name="campaign_knowledge")

results = search_service.search(
    query="email campaigns about seasonal promotions",
    limit=10
)

for result in results.results:
    print(f"Match: {result.content}")
    print(f"Score: {result.score}")  # Similarity: 0.0 to 1.0
    print(f"Rank: {result.rank}")
```

#### 2. `search_with_llm()` - RAG (Retrieval Augmented Generation)
```python
# Combines search + LLM for intelligent answers
answer = search_service.search_with_llm(
    query="What are best practices for summer email campaigns?",
    limit=5,
    llm_model="llama3-70b"
)

print(answer)
# Output: "Based on our campaign documents, summer campaigns perform best
# when sent Tuesday-Thursday mornings, with subject lines emphasizing
# limited-time offers and seasonal imagery..."
```

### Practical Use Cases

**Knowledge Base Search:**
```python
# Find relevant documentation
kb_search = CortexSearch(service_name="company_kb")
results = kb_search.search("how to set up email automation")

# Find similar campaigns
campaign_search = CortexSearch(service_name="campaign_history")
results = campaign_search.search("Black Friday 2025")
```

**Customer Support (RAG Pattern):**
```python
# Search knowledge base + generate answer
support = CortexSearch(service_name="support_docs")
answer = support.search_with_llm(
    "How do I improve my email deliverability?",
    limit=3
)
print(answer)  # Gets context from docs, generates natural answer
```

**Content Recommendation:**
```python
# Find similar products/content
content = CortexSearch(service_name="product_catalog")
similar = content.search(
    "women's summer dresses",
    limit=20,
    filters={"category": "apparel", "season": "summer"}
)
```

**Requirements:**
- ✅ Cortex Search Service must be created first in Snowflake
- ✅ Source table with content to search
- ✅ Embeddings automatically generated by Snowflake

**Setup Required:**
```sql
-- Create search service (one-time setup)
CREATE CORTEX SEARCH SERVICE my_search_service
    ON content_column
    WAREHOUSE = COMPUTE_WH
    TARGET_LAG = '1 hour'
    AS (
        SELECT content_column, metadata_column
        FROM your_table
    );
```

**Limitations:**
- ❌ Requires upfront setup (create search service)
- ❌ Cannot search arbitrary tables (must create service first)
- ❌ Target lag means data isn't instantly searchable

---

## 📚 CORTEX ML - Comprehensive Guide

### What It Does
Provides time series forecasting and anomaly detection for predicting trends and identifying unusual patterns.

### Snowflake Functions

#### FORECAST() - Predict Future Values
```sql
SELECT * FROM TABLE(
    FORECAST(
        INPUT_DATA => system$reference('table', 'historical_data'),
        TIMESTAMP_COLNAME => 'date',
        TARGET_COLNAME => 'sales'
    )
);
```

#### ANOMALY_DETECTION() - Find Outliers
```sql
SELECT * FROM TABLE(
    SNOWFLAKE.CORTEX.ANOMALY_DETECTION(
        INPUT => system$reference('table', 'metrics_table'),
        TIMESTAMP_COLNAME => 'date',
        TARGET_COLNAME => 'click_rate',
        THRESHOLD => 0.95
    )
);
```

### Python Wrapper Methods

#### 1. `forecast()` - Time Series Forecasting
```python
ml = CortexML()

forecast_results = ml.forecast(
    table="VW_SFMC_EMAIL_PERFORMANCE",
    timestamp_col="SEND_DATE",
    target_col="OPEN_RATE",
    periods=30  # Forecast next 30 days
)

for prediction in forecast_results.forecasts:
    print(f"Date: {prediction.timestamp}")
    print(f"Predicted: {prediction.forecast}")
    print(f"Lower Bound: {prediction.lower_bound}")
    print(f"Upper Bound: {prediction.upper_bound}")
```

#### 2. `detect_anomalies()` - Anomaly Detection
```python
anomaly_results = ml.detect_anomalies(
    table="VW_SFMC_EMAIL_PERFORMANCE",
    timestamp_col="SEND_DATE",
    target_col="BOUNCE_RATE",
    sensitivity=0.95  # 0.9 to 0.99 (higher = more sensitive)
)

for anomaly in anomaly_results.anomalies:
    if anomaly.is_anomaly:
        print(f"⚠️ Anomaly detected on {anomaly.timestamp}")
        print(f"   Value: {anomaly.value}")
        print(f"   Expected: {anomaly.expected}")
        print(f"   Score: {anomaly.score}")
```

### Practical Use Cases

**Performance Forecasting:**
```python
ml = CortexML()

# Predict future email volume
email_forecast = ml.forecast(
    table="EMAIL_METRICS",
    timestamp_col="DATE",
    target_col="EMAILS_SENT",
    periods=14
)

# Forecast click rates
click_forecast = ml.forecast(
    table="CAMPAIGN_PERFORMANCE",
    timestamp_col="WEEK",
    target_col="CLICK_RATE",
    periods=8
)
```

**Anomaly Monitoring:**
```python
# Detect unusual bounce rates
bounce_anomalies = ml.detect_anomalies(
    table="DAILY_METRICS",
    timestamp_col="DATE",
    target_col="BOUNCE_RATE",
    sensitivity=0.95
)

# Alert if anomalies found
if bounce_anomalies.has_anomalies:
    send_alert(f"Found {bounce_anomalies.anomaly_count} anomalies!")
```

**Capacity Planning:**
```python
# Predict resource needs
resource_forecast = ml.forecast(
    table="SYSTEM_METRICS",
    timestamp_col="HOUR",
    target_col="API_REQUESTS",
    periods=168  # Next week (hourly)
)
```

**Data Quality Monitoring:**
```python
# Detect data quality issues
quality_check = ml.detect_anomalies(
    table="DATA_QUALITY_METRICS",
    timestamp_col="DATE",
    target_col="NULL_RATE",
    sensitivity=0.99
)
```

**Requirements:**
- ✅ Time series data (date/timestamp + numeric metric)
- ✅ Minimum 14 days of historical data
- ✅ One row per time period (no gaps)
- ✅ Consistent time intervals

**Limitations:**
- ❌ Requires clean time series data (no missing timestamps)
- ❌ May struggle with highly irregular patterns
- ❌ Needs sufficient historical data for accuracy

---

## 🔄 Combining Cortex Services - Real-World Examples

### Example 1: Intelligent Data Analysis
```python
# Step 1: Get data using Cortex Analyst
analyst = CortexAnalyst()
data = analyst.send_message("What was the click rate by market last month?")

# Step 2: Use ML to detect anomalies
ml = CortexML()
anomalies = ml.detect_anomalies(
    table="PERFORMANCE_BY_MARKET",
    timestamp_col="DATE",
    target_col="CLICK_RATE"
)

# Step 3: Generate natural language summary using Complete
llm = CortexComplete(temperature=0.5)
summary = llm.complete(f"""
Analyze this data and anomalies, provide 3 key insights:

Data: {data.results}
Anomalies: {anomalies.anomalies}

Insights:
""")

print(summary.completion)
```

### Example 2: Smart Campaign Assistant
```python
# Step 1: Search for similar past campaigns
search = CortexSearch(service_name="campaign_history")
similar_campaigns = search.search("summer promotional email")

# Step 2: Generate subject lines based on best practices
llm = CortexComplete(temperature=0.9)
subject_lines = llm.generate_subject_lines(
    f"Summer promotion based on successful campaigns: {similar_campaigns}",
    count=5
)

# Step 3: Forecast expected performance
ml = CortexML()
expected_performance = ml.forecast(
    table="SUMMER_CAMPAIGNS_HISTORY",
    timestamp_col="YEAR",
    target_col="OPEN_RATE",
    periods=1
)

print(f"Generated Subject Lines: {subject_lines}")
print(f"Expected Open Rate: {expected_performance.forecasts[0].forecast}")
```

### Example 3: Knowledge Base Q&A System
```python
def answer_question(user_question: str):
    # Step 1: Search knowledge base
    search = CortexSearch(service_name="company_kb")
    
    # Step 2: Use RAG (Retrieval + Generation)
    answer = search.search_with_llm(
        query=user_question,
        limit=5,
        llm_model="mistral-large"
    )
    
    return answer

# Usage
answer = answer_question("How do I improve email deliverability?")
print(answer)
```

---

## 🎯 Decision Matrix: Which Service to Use?

### User Ask: "What was revenue last month?"
- ✅ **Use: Cortex Analyst** - Needs real data from database
- ❌ Cortex Complete - Would just make up an answer

### User Ask: "Write me 3 email subject lines"
- ❌ Cortex Analyst - Cannot generate creative content
- ✅ **Use: Cortex Complete** - LLM text generation

### User Ask: "Find campaigns similar to Black Friday 2025"
- ❌ Cortex Analyst - Not designed for similarity search
- ✅ **Use: Cortex Search** - Semantic similarity search

### User Ask: "Predict next week's email volume"
- ❌ Cortex Analyst - Can query historical data but not predict
- ✅ **Use: Cortex ML** - Time series forecasting

### User Ask: "Analyze this data and explain what it means"
- ✅ **Use: Cortex Analyst + Cortex Complete** - Get data, then summarize
- 📝 Pattern: Analyst for data → Complete for explanation

### User Ask: "How do I set up automation?" (from docs)
- ✅ **Use: Cortex Search + Complete (RAG)** - Search docs + generate answer
- 📝 Pattern: Search for context → Complete for natural answer

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
