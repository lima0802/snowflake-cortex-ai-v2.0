# DIA v2 Implementation Plan

## Proposed Architecture: DIA v2

### Design Principles

DIA v2 follows an **"API-First" philosophy**, decoupling the intelligence layer from the presentation layer. This enables flexible deployment across multiple channels while maintaining centralized governance and business logic.

| Principle | Implementation |
|---|---|
| API-First | All Cortex capabilities accessed via REST APIs, not UI-bound |
| Separation of Concerns | Orchestration layer manages routing; Cortex services handle execution |
| Progressive Intelligence | Descriptive > Diagnostic > Predictive > Prescriptive analytics |
| Cost-Conscious Evaluation | Tiered evaluation framework minimizing LLM-as-judge costs |
| Replicability | Template architecture adaptable for VML MAP client portfolio |

---

## System Architecture Overview

The architecture consists of four primary layers, each with distinct responsibilities.

### Layer 1: Presentation Layer

Multiple frontend options connect to a unified backend orchestrator:

- **Web Application (Streamlit/React)** - Primary interface for internal users
- **Slack/Teams Integration** - Conversational interface for quick queries
- **REST API** - Programmatic access for automation and integration

### Layer 2: Orchestration Layer

A Python-based orchestration service (FastAPI) handles query routing and response enhancement:

- **Intent Classification** - Determines query type (descriptive, diagnostic, predictive)
- **Tool Selection** - Routes to appropriate Cortex service(s)
- **Response Enhancement** - Adds context, recommendations, and formatting
- **Conversation Management** - Maintains context across multi-turn interactions

### Layer 3: Intelligence Layer (Snowflake Cortex)

Four Cortex services provide distinct analytical capabilities:

| Service | Capability | Use Case |
|---|---|---|
| Cortex Analyst | Natural language to SQL conversion | "What was click rate in Spain?" |
| Cortex Search | RAG / Vector search for fuzzy matching | LTA entity resolution, campaign lookup |
| Cortex ML | Anomaly detection, forecasting, contribution explorer | "Why did click rate drop?" "Predict next month" |
| Cortex Complete | LLM completion for response enhancement | Natural language summaries, recommendations |

### Layer 4: Data Layer

Governed data assets within Snowflake:

- **Semantic Views** - Cleansed, standardized SFMC data with business logic
- **Semantic Model (YAML)** - Field descriptions, synonyms, relationships
- **ML Model Objects** - Trained anomaly detection and forecasting models
- **Benchmark Thresholds** - Industry standards for KPI classification

---

## Directory Structure

```
snowflake-cortex-ai-v2.0/
│
├── .env
├── .gitignore
├── LICENSE
├── README.md
├── DIA_V2_IMPLEMENTATION_PLAN.md
│
│── ──────────────────────────────────────────────────────
│   LAYER 1: PRESENTATION LAYER
│── ──────────────────────────────────────────────────────
│
├── web-app/                              # Streamlit/React web application
│   ├── app.py                            # Main Streamlit entry point
│   ├── requirements.txt                  # Web app dependencies
│   ├── components/
│   │   ├── __init__.py
│   │   ├── chat.py                       # Chat interface component
│   │   └── visualizations.py             # Charts, tables, export components
│   └── utils/
│       ├── __init__.py
│       └── api_client.py                 # HTTP client for orchestrator API
│
├── integrations/                         # Conversational channel integrations
│   ├── slack/
│   │   ├── bot.py                        # Slack bot entry point
│   │   └── handlers.py                   # Slash command & event handlers
│   └── teams/
│       ├── bot.py                        # Teams bot entry point
│       └── handlers.py                   # Adaptive card & message handlers
│
│── ──────────────────────────────────────────────────────
│   LAYER 2: ORCHESTRATION LAYER
│── ──────────────────────────────────────────────────────
│
├── orchestrator/                         # FastAPI orchestration service
│   ├── __init__.py
│   ├── main.py                           # FastAPI app entry point
│   ├── requirements.txt                  # Orchestrator dependencies
│   ├── Dockerfile                        # Container deployment
│   ├── api/
│   │   ├── __init__.py
│   │   ├── models.py                     # Pydantic request/response models
│   │   └── routes/
│   │       ├── __init__.py
│   │       ├── query.py                  # POST /api/v1/query
│   │       ├── health.py                 # GET /api/v1/health
│   │       └── admin.py                  # GET /api/v1/metrics, evaluate, models
│   ├── services/
│   │   ├── __init__.py
│   │   ├── intent_classifier.py          # Query intent classification logic
│   │   ├── cortex_analyst.py             # Cortex Analyst API wrapper
│   │   ├── cortex_search.py              # Cortex Search API wrapper
│   │   ├── cortex_ml.py                  # Cortex ML API wrapper (anomaly, forecast)
│   │   ├── cortex_complete.py            # Cortex Complete API wrapper
│   │   └── response_enhancer.py          # Context injection, formatting, summaries
│   └── utils/
│       ├── __init__.py
│       ├── logging.py                    # Structured logging configuration
│       └── config.py                     # Environment and settings management
│
│── ──────────────────────────────────────────────────────
│   LAYER 3: INTELLIGENCE LAYER (configured via Snowflake Cortex)
│── ──────────────────────────────────────────────────────
│
├── config/                               # Cortex service configurations
│   ├── semantic.yaml                     # Active semantic model for Cortex Analyst
│   ├── semantic_prod.yaml                # Production semantic model
│   ├── sementic_backup.yaml              # Backup semantic model
│   ├── agent_spec.yaml                   # Cortex Agent specification
│   ├── README_WIP.md
│   └── agents/
│       └── backup/
│           ├── semantic_template.yaml    # Reusable semantic model template
│           ├── about/
│           │   └── default.md            # Agent about/description
│           ├── access/
│           │   └── access.md             # Access control definitions
│           ├── orchestration/
│           │   ├── instructions_default.md  # Agent instructions
│           │   └── response_default.md      # Response formatting rules
│           └── tools/
│               ├── cortex_analyst.md      # Cortex Analyst tool config
│               └── cortex_search.md       # Cortex Search tool config
│
│── ──────────────────────────────────────────────────────
│   LAYER 4: DATA LAYER
│── ──────────────────────────────────────────────────────
│
├── data-layer/                           # Governed data assets in Snowflake
│   ├── semantic-models/
│   │   └── semantic.yaml                 # Field descriptions, synonyms, relationships
│   ├── views/
│   │   └── setup_semantic_views.sql      # Cleansed, standardized SFMC semantic views
│   ├── benchmarks/
│   │   └── setup_benchmarks.sql          # Industry KPI benchmark thresholds
│   └── ml-models/
│       └── setup_ml_models.sql           # Anomaly detection & forecasting model objects
│
│── ──────────────────────────────────────────────────────
│   EVALUATION & TESTING
│── ──────────────────────────────────────────────────────
│
├── evaluation/                           # Cost-conscious evaluation framework
│   ├── tier1_deterministic.py            # SQL validity, response format checks (free)
│   ├── tier2_heuristic.py                # Metric ranges, logic consistency (free)
│   ├── tier3_llm_judge.py                # Semantic correctness - edge cases only (paid)
│   └── test_suite.py                     # Verified query test suite
│
├── tests/                                # Unit & integration tests
│   └── test_connection.py                # Snowflake connection test
│
│── ──────────────────────────────────────────────────────
│   DEPLOYMENT & OPERATIONS
│── ──────────────────────────────────────────────────────
│
├── scripts/                              # Deployment & setup scripts
│   ├── setup_data_layer.py               # Data layer setup (views, benchmarks, ML, semantic model)
│   ├── deploy_semantic_model.py          # Re-deploy semantic model YAML to stage
│   ├── deploy_agent.py                   # Cortex Agent deployment automation
│   ├── create_agent.sql                  # Cortex Agent creation SQL (used by deploy_agent.py)
│   └── inspect_agent.py                  # Agent inspection utility
│
└── docs/                                 # Documentation
    ├── user_guide.md                     # End-user query guide
    ├── api_reference.md                  # OpenAPI/Swagger reference
    └── deployment_guide.md               # Production deployment steps
```

---

## Step-by-Step Implementation Guide

This guide provides a detailed, sequential approach to implementing DIA v2 from scratch.

### Prerequisites

- [ ] Snowflake account with Cortex services enabled
- [ ] Python 3.11+ installed locally
- [ ] Git repository initialized
- [ ] .env file configured with Snowflake credentials

---

### Phase 1: Foundation Setup (Week 1)

#### Step 1.1: Environment Setup
**Goal:** Configure development environment and dependencies

1. **Install Python dependencies:**
   ```bash
   # For orchestrator
   cd orchestrator/
   pip install -r requirements.txt

   # For web app
   cd ../web-app/
   pip install -r requirements.txt
   ```

2. **Verify Snowflake connection:**
   ```bash
   cd ../tests/
   python test_connection.py
   ```
   - Expected: Successful connection and query execution
   - Troubleshoot: Check .env credentials if fails

3. **Test logging configuration:**
   ```python
   from orchestrator.utils.logging import configure_logging, get_logger
   configure_logging()
   logger = get_logger(__name__)
   logger.info("test", component="setup")
   ```

**Deliverable:** ✅ Working Python environment with Snowflake connectivity

---

#### Step 1.2: Data Layer Setup
**Goal:** Create semantic views, benchmarks, and ML model placeholders in Snowflake

All steps are automated via `scripts/setup_data_layer.py` (no SnowSQL required).
It uses `snowflake.connector` to execute SQL files and `snowflake.snowpark` for file uploads.

1. **Run all steps at once (recommended):**
   ```bash
   python scripts/setup_data_layer.py
   ```

   Or run each step individually:

   ```bash
   # Create semantic views (data-layer/views/setup_semantic_views.sql)
   python scripts/setup_data_layer.py --step views

   # Load benchmark thresholds (data-layer/benchmarks/setup_benchmarks.sql)
   python scripts/setup_data_layer.py --step benchmarks

   # Create ML model placeholders (data-layer/ml-models/setup_ml_models.sql)
   python scripts/setup_data_layer.py --step ml-models

   # Upload semantic model to @SEMANTIC_MODELS stage
   python scripts/setup_data_layer.py --step semantic-model
   ```

2. **Verify in Snowsight:**
   ```sql
   SELECT * FROM PLAYGROUND_LM.CORTEX_ANALYTICS_ORCHESTRATOR.VW_SFMC_EMAIL_PERFORMANCE LIMIT 10;
   SELECT * FROM PLAYGROUND_LM.CORTEX_ANALYTICS_ORCHESTRATOR.BENCHMARK_THRESHOLDS;
   SELECT * FROM PLAYGROUND_LM.CORTEX_ANALYTICS_ORCHESTRATOR.ML_MODEL_REGISTRY;
   LIST @PLAYGROUND_LM.CORTEX_ANALYTICS_ORCHESTRATOR.SEMANTIC_MODELS;
   ```

3. **Upload semantic model only** (if re-deploying after edits to `data-layer/semantic-models/semantic.yaml`):
   ```bash
   python scripts/deploy_semantic_model.py
   ```
   - Source file: `data-layer/semantic-models/semantic.yaml`
   - Target stage: `@PLAYGROUND_LM.CORTEX_ANALYTICS_ORCHESTRATOR.SEMANTIC_MODELS`

**Deliverable:** ✅ Data layer configured with views, benchmarks, and semantic model

---

### Phase 2: Core Services Implementation (Week 2)

#### Step 2.1: Implement Cortex Service Wrappers
**Goal:** Build Python wrappers for each Cortex service

**Priority Order:**
1. **Cortex Analyst** (`orchestrator/services/cortex_analyst.py`)
   - Implement `send_message()` method for NL-to-SQL
   - Handle semantic model loading
   - Parse SQL results and metadata
   - **Test:** Query "What was total emails sent last month?"

2. **Cortex Complete** (`orchestrator/services/cortex_complete.py`)
   - Implement `complete()` method for LLM generation
   - Support prompt templates
   - Handle streaming responses (optional)
   - **Test:** Generate summary from sample data

3. **Cortex Search** (`orchestrator/services/cortex_search.py`)
   - Implement `search()` method for vector search
   - Handle filter parameters
   - Parse relevance scores
   - **Test:** Search for campaign names

4. **Cortex ML** (`orchestrator/services/cortex_ml.py`)
   - Implement `detect_anomalies()` method
   - Implement `forecast()` method
   - Implement `contribution_analysis()` method
   - **Test:** Detect anomalies in sample time series

**Testing Approach:**
- Create standalone test script for each service
- Use sample queries from test_suite.py
- Verify response format matches Pydantic models

**Deliverable:** ✅ All 4 Cortex services functional with unit tests

---

#### Step 2.2: Implement Intent Classifier
**Goal:** Build logic to classify queries into descriptive/diagnostic/predictive/prescriptive

**Implementation:** `orchestrator/services/intent_classifier.py`

1. **Create classification logic:**
   - Use Cortex Complete with prompt engineering
   - Define intent patterns (keywords, question types)
   - Return IntentClassification model

2. **Test with sample queries:**
   ```python
   classify_intent("What was click rate last month?")  # → descriptive
   classify_intent("Why did click rate drop?")         # → diagnostic
   classify_intent("What will click rate be next month?")  # → predictive
   classify_intent("How can I improve click rate?")    # → prescriptive
   ```

3. **Refine classification accuracy:**
   - Add edge cases to test suite
   - Tune prompt template
   - Measure accuracy (>90% target)

**Deliverable:** ✅ Intent classifier with >90% accuracy on test suite

---

#### Step 2.3: Implement Response Enhancer
**Goal:** Add context, recommendations, and formatting to Cortex responses

**Implementation:** `orchestrator/services/response_enhancer.py`

1. **Build enhancement pipeline:**
   - Add benchmark comparisons ("above/below industry average")
   - Inject market context
   - Generate recommendations based on intent
   - Format data for visualizations

2. **Create enhancement methods:**
   ```python
   def add_benchmarks(data: dict, metric: str) -> dict
   def generate_recommendations(intent: str, data: dict) -> List[str]
   def format_for_visualization(data: dict) -> dict
   ```

3. **Test enhancement quality:**
   - Compare raw vs enhanced responses
   - Verify recommendations are actionable
   - Ensure benchmark data is accurate

**Deliverable:** ✅ Response enhancer adding value to all query types

---

### Phase 3: Orchestration Layer (Week 3)

#### Step 3.1: Implement API Routes
**Goal:** Build FastAPI endpoints for query, health, and admin functions

**Priority Order:**

1. **Health Route** (`orchestrator/api/routes/health.py`)
   ```python
   GET /api/v1/health
   # Returns: status, services health, timestamp
   ```
   - Test all Cortex service connections
   - Return degraded if any service fails
   - **Test:** `curl http://localhost:8000/api/v1/health`

2. **Query Route** (`orchestrator/api/routes/query.py`)
   ```python
   POST /api/v1/query
   # Body: QueryRequest
   # Returns: QueryResponse
   ```
   - Implement full orchestration flow:
     1. Classify intent
     2. Route to appropriate Cortex service(s)
     3. Enhance response
     4. Return formatted result
   - **Test:** Send sample queries via Postman/curl

3. **Admin Route** (`orchestrator/api/routes/admin.py`)
   ```python
   GET /api/v1/metrics      # System metrics
   POST /api/v1/evaluate    # Run evaluation
   GET /api/v1/models       # List available models
   ```
   - Implement metrics tracking
   - Connect to evaluation framework
   - **Test:** Verify metrics endpoint

**Deliverable:** ✅ FastAPI app with all routes functional

---

#### Step 3.2: Implement Main Orchestrator App
**Goal:** Configure FastAPI app with middleware, CORS, and startup logic

**Implementation:** `orchestrator/main.py`

1. **Configure FastAPI app:**
   ```python
   app = FastAPI(
       title="DIA v2 Orchestrator",
       version="2.0.0",
       docs_url="/docs"
   )
   ```

2. **Add middleware:**
   - CORS (allow Streamlit origin)
   - Request logging
   - Error handling
   - Response timing

3. **Add startup/shutdown events:**
   - Initialize Snowflake connection pool
   - Load semantic model into memory
   - Configure logging

4. **Run locally:**
   ```bash
   cd orchestrator/
   uvicorn main:app --reload --port 8000
   ```
   - Verify: http://localhost:8000/docs

**Deliverable:** ✅ Orchestrator API running locally with Swagger docs

---

### Phase 4: Presentation Layer (Week 4)

#### Step 4.1: Implement Streamlit Web App
**Goal:** Build chat interface for querying DIA v2

**Implementation:** `web-app/app.py`

1. **Create main page layout:**
   ```python
   st.set_page_config(page_title="DIA v2", layout="wide")
   st.title("🧠 DIA v2 - Digital Intelligence Assistant")
   ```

2. **Implement chat interface:**
   - Use `st.chat_input()` for user queries
   - Display conversation history with `st.chat_message()`
   - Show typing indicator during API calls

3. **Implement API client:** (`web-app/utils/api_client.py`)
   ```python
   def query_orchestrator(query: str) -> QueryResponse:
       response = requests.post(
           "http://localhost:8000/api/v1/query",
           json={"query": query}
       )
       return response.json()
   ```

4. **Add visualizations:** (`web-app/components/visualizations.py`)
   - Line charts for time series
   - Bar charts for comparisons
   - Tables for raw data
   - Export to CSV/Excel

5. **Run web app:**
   ```bash
   cd web-app/
   streamlit run app.py
   ```
   - Verify: http://localhost:8501

**Deliverable:** ✅ Streamlit app with chat interface and visualizations

---

#### Step 4.2: Add Conversational Integrations (Optional)
**Goal:** Enable Slack/Teams bot access to DIA v2

**Slack Integration:** `integrations/slack/bot.py`
1. Create Slack app in workspace
2. Configure bot token and permissions
3. Implement slash command handler (`/dia <query>`)
4. Test: `/dia What was click rate last week?`

**Teams Integration:** `integrations/teams/bot.py`
1. Register bot in Azure Bot Service
2. Configure Teams channel
3. Implement message handler
4. Test: Send query in Teams chat

**Deliverable:** ✅ Slack/Teams integration functional (optional)

---

### Phase 5: Evaluation Framework (Week 5)

#### Step 5.1: Implement Tier 1 - Deterministic Evaluation
**Goal:** Build free, fast validation checks

**Implementation:** `evaluation/tier1_deterministic.py`

**Checks to implement:**
1. **SQL Validity:**
   ```python
   def validate_sql(query_response: QueryResponse) -> bool:
       # Check if SQL is parseable
       # Verify no syntax errors
   ```

2. **Response Format:**
   ```python
   def validate_response_format(response: QueryResponse) -> bool:
       # Verify all required fields present
       # Check data types match schema
   ```

3. **Data Integrity:**
   ```python
   def validate_data_integrity(response: QueryResponse) -> bool:
       # Check for null values in critical fields
       # Verify numeric ranges are reasonable
   ```

**Test suite integration:**
```python
for test_case in load_test_suite():
    response = orchestrator.query(test_case.query)
    assert validate_sql(response)
    assert validate_response_format(response)
    assert validate_data_integrity(response)
```

**Deliverable:** ✅ Tier 1 evaluation catching format/syntax errors

---

#### Step 5.2: Implement Tier 2 - Heuristic Evaluation
**Goal:** Build business logic validation

**Implementation:** `evaluation/tier2_heuristic.py`

**Checks to implement:**
1. **Metric Range Validation:**
   ```python
   def validate_metric_ranges(data: dict, metric: str) -> bool:
       # Click rate: 0-100%
       # Bounce rate: 0-100%
       # Emails sent: > 0
   ```

2. **Benchmark Comparison:**
   ```python
   def validate_benchmark_alignment(data: dict) -> bool:
       # Compare against industry benchmarks
       # Flag if severely out of range (>3 std dev)
   ```

3. **Temporal Consistency:**
   ```python
   def validate_temporal_logic(query: str, data: dict) -> bool:
       # "Last month" should return previous month's data
       # Date ranges should be consistent
   ```

4. **Logic Consistency:**
   ```python
   def validate_logic(query: str, response: str) -> bool:
       # Intent matches response type
       # Diagnostic queries include "because/due to"
       # Predictive queries include future dates
   ```

**Deliverable:** ✅ Tier 2 evaluation catching business logic errors

---

#### Step 5.3: Implement Tier 3 - LLM Judge (Edge Cases Only)
**Goal:** Semantic correctness validation for ambiguous cases

**Implementation:** `evaluation/tier3_llm_judge.py`

**When to use Tier 3:**
- Tier 1 & 2 pass but human review flagged issue
- Query is ambiguous or complex
- Response accuracy is critical (executive reporting)

**Implementation:**
```python
def llm_judge_evaluate(query: str, expected: str, actual: str) -> float:
    prompt = f"""
    Evaluate if the actual response correctly answers the query.

    Query: {query}
    Expected: {expected}
    Actual: {actual}

    Score 0-1 for semantic correctness.
    """
    score = cortex_complete(prompt, model="mistral-large")
    return float(score)
```

**Cost optimization:**
- Only run on <5% of queries (edge cases)
- Cache results for similar queries
- Use cheaper model when possible

**Deliverable:** ✅ Tier 3 LLM judge for edge case validation

---

#### Step 5.4: Create Test Suite
**Goal:** Build golden dataset for regression testing

**Implementation:** `evaluation/test_suite.py`

**Test categories:**
1. **Descriptive Queries (30 tests)**
   - "What was click rate in Spain last month?"
   - "How many emails were sent last week?"
   - "What is the average open rate by market?"

2. **Diagnostic Queries (20 tests)**
   - "Why did click rate drop in Germany?"
   - "What caused the spike in unsubscribes?"
   - "Why is bounce rate higher in France?"

3. **Predictive Queries (15 tests)**
   - "What will click rate be next month?"
   - "Forecast email volume for Q2"
   - "Predict unsubscribe rate trend"

4. **Prescriptive Queries (10 tests)**
   - "How can I improve open rates?"
   - "What should I do about high bounce rate?"
   - "Recommend optimizations for Spain market"

**Test format:**
```python
test_cases = [
    {
        "query": "What was click rate in Spain last month?",
        "intent": "descriptive",
        "expected_services": ["analyst", "complete"],
        "expected_data_fields": ["click_rate", "market", "period"],
        "validation_rules": {
            "click_rate": {"min": 0, "max": 100},
            "market": "ES"
        }
    },
    # ... more test cases
]
```

**Run test suite:**
```bash
python evaluation/test_suite.py --tier all --report html
```

**Deliverable:** ✅ Comprehensive test suite with 75+ verified test cases

---

### Phase 6: Deployment & Operations (Week 6)

#### Step 6.1: Containerize Orchestrator
**Goal:** Package orchestrator as Docker container

1. **Build Docker image:**
   ```bash
   cd orchestrator/
   docker build -t dia-orchestrator:v2.0 .
   ```

2. **Run container locally:**
   ```bash
   docker run -p 8000:8000 \
     --env-file ../.env \
     dia-orchestrator:v2.0
   ```

3. **Test containerized app:**
   ```bash
   curl http://localhost:8000/api/v1/health
   ```

**Deliverable:** ✅ Containerized orchestrator running locally

---

#### Step 6.2: Deploy to Production
**Goal:** Deploy to cloud environment (Snowpark Container Services / AWS / Azure)

**Option A: Snowpark Container Services**
```sql
CREATE SERVICE DIA_ORCHESTRATOR
  IN COMPUTE POOL dia_compute_pool
  FROM SPECIFICATION $$
    spec:
      containers:
        - name: orchestrator
          image: /dia/dia-orchestrator:v2.0
          env:
            SNOWFLAKE_ACCOUNT: <account>
            ...
      endpoints:
        - name: api
          port: 8000
          public: true
  $$;
```

**Option B: AWS ECS / Azure Container Apps**
- Use Terraform/CloudFormation for IaC
- Configure load balancer
- Set up auto-scaling
- Configure logging/monitoring

**Deliverable:** ✅ Production deployment with monitoring

---

#### Step 6.3: Documentation & Handoff
**Goal:** Complete documentation for users and maintainers

1. **User Guide** (`docs/user_guide.md`)
   - How to ask questions
   - Query examples by category
   - Interpreting results
   - Troubleshooting

2. **API Reference** (`docs/api_reference.md`)
   - OpenAPI/Swagger specification
   - Request/response schemas
   - Authentication
   - Rate limits

3. **Deployment Guide** (`docs/deployment_guide.md`)
   - Infrastructure requirements
   - Configuration options
   - Scaling guidelines
   - Monitoring setup

4. **Update README.md:**
   - Architecture diagram
   - Quick start guide
   - Links to detailed docs

**Deliverable:** ✅ Complete documentation suite

---

## Success Criteria

### Functional Requirements
- [ ] All Cortex services integrated and functional
- [ ] Intent classification >90% accurate
- [ ] Orchestrator handles 100+ QPS (queries per second)
- [ ] Streamlit UI responsive (<2s query response)
- [ ] Evaluation framework catching >95% of errors

### Non-Functional Requirements
- [ ] API uptime >99.9%
- [ ] Average query latency <3 seconds
- [ ] Cost per query <$0.05
- [ ] Tier 3 evaluation used on <5% of queries
- [ ] Zero exposed credentials or secrets

### Business Requirements
- [ ] Supports all 4 query intents (descriptive/diagnostic/predictive/prescriptive)
- [ ] Provides actionable recommendations
- [ ] Benchmark comparisons included
- [ ] Exportable results (CSV/Excel)
- [ ] Multi-turn conversations supported

---

## Troubleshooting Guide

### Common Issues

**Issue:** Snowflake connection fails
- **Solution:** Verify .env credentials, check network/firewall, test with snowsql

**Issue:** Cortex Analyst returns empty results
- **Solution:** Verify semantic model is uploaded, check YAML syntax, test query directly in Snowsight

**Issue:** Intent classification is inaccurate
- **Solution:** Review classification prompt, add examples to few-shot learning, tune temperature

**Issue:** Response time too slow (>5s)
- **Solution:** Enable Snowflake query result caching, optimize semantic views, add indexes

**Issue:** Evaluation framework is too expensive
- **Solution:** Reduce Tier 3 usage, increase Tier 1/2 coverage, batch LLM judge calls

**Issue:** Streamlit app crashes on large responses
- **Solution:** Implement pagination, limit data returned, use lazy loading for visualizations

---

## Next Steps After Implementation

### Phase 7: Enhancements (Post-Launch)
1. **Multi-language support** (Spanish, German, French)
2. **Advanced visualizations** (Plotly Dash, custom D3.js)
3. **Query suggestion engine** (autocomplete, recommended questions)
4. **Scheduled reports** (daily/weekly email digests)
5. **Fine-tuned LLM** (domain-specific model training)
6. **A/B testing framework** (experiment with different prompts/models)

### Phase 8: Scale to VML MAP Portfolio
1. **Templatize architecture** (reusable for other clients)
2. **Multi-tenant support** (isolate data by client)
3. **White-label UI** (customizable branding)
4. **Central admin dashboard** (manage multiple deployments)

---

## Appendix

### Useful Commands

**Test Snowflake connection:**
```bash
python tests/test_connection.py
```

**Run orchestrator locally:**
```bash
cd orchestrator && uvicorn main:app --reload --port 8000
```

**Run Streamlit app:**
```bash
cd web-app && streamlit run app.py
```

**Run evaluation suite:**
```bash
python evaluation/test_suite.py --tier all
```

**Deploy semantic model:**
```bash
python scripts/deploy_semantic_model.py
```

**Inspect deployed agent:**
```bash
python scripts/inspect_agent.py --agent DIA_AGENT
```

### Resource Links
- [Snowflake Cortex Analyst Documentation](https://docs.snowflake.com/en/user-guide/snowflake-cortex/cortex-analyst)
- [Snowflake Cortex Search Documentation](https://docs.snowflake.com/en/user-guide/snowflake-cortex/cortex-search)
- [Snowflake Cortex ML Functions](https://docs.snowflake.com/en/user-guide/snowflake-cortex/ml-functions)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Streamlit Documentation](https://docs.streamlit.io/)

---

**Last Updated:** 2026-02-09
**Version:** 2.0
**Maintained By:** VML MAP Data Intelligence Team
