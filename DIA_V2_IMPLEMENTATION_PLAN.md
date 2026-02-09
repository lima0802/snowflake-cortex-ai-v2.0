# DIA v2 Implementation Plan

**Version:** 2.0  
**Date:** February 9, 2026  
**Status:** Planning Phase

---

## Executive Summary

DIA (Direct Marketing Intelligence Agent) v2 represents a strategic evolution from UI-bound analytics to an API-first, multi-channel intelligence platform. This implementation plan outlines the architecture, development phases, and technical specifications for building a scalable, cost-effective analytics solution powered by Snowflake Cortex.

---

## Proposed Architecture: DIA v2

### Design Principles

DIA v2 follows an **"API-First"** philosophy, decoupling the intelligence layer from the presentation layer. This enables flexible deployment across multiple channels while maintaining centralized governance and business logic.

| Principle | Implementation |
|-----------|----------------|
| **API-First** | All Cortex capabilities accessed via REST APIs, not UI-bound |
| **Separation of Concerns** | Orchestration layer manages routing; Cortex services handle execution |
| **Progressive Intelligence** | Descriptive → Diagnostic → Predictive → Prescriptive analytics |
| **Cost-Conscious Evaluation** | Tiered evaluation framework minimizing LLM-as-judge costs |
| **Replicability** | Template architecture adaptable for VML MAP client portfolio |

---

## System Architecture Overview

The architecture consists of four primary layers, each with distinct responsibilities:

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
|---------|-----------|----------|
| **Cortex Analyst** | Natural language to SQL conversion | "What was click rate in Spain?" |
| **Cortex Search** | RAG / Vector search for fuzzy matching | LTA entity resolution, campaign lookup |
| **Cortex ML** | Anomaly detection, forecasting, contribution explorer | "Why did click rate drop?" "Predict next month" |
| **Cortex Complete** | LLM completion for response enhancement | Natural language summaries, recommendations |

### Layer 4: Data Layer

Governed data assets within Snowflake:

- **Semantic Views** - Cleansed, standardized SFMC data with business logic
- **Semantic Model (YAML)** - Field descriptions, synonyms, relationships
- **ML Model Objects** - Trained anomaly detection and forecasting models
- **Benchmark Thresholds** - Industry standards for KPI classification

---

## Implementation Phases

### Phase 1: Foundation (Weeks 1-2)

**Objective:** Establish core infrastructure and data layer

#### Tasks:

1. **Data Layer Setup**
   - [ ] Create semantic views for SFMC data
   - [ ] Update semantic model YAML with complete field descriptions
   - [ ] Implement fuzzy matching logic for LTA resolution
   - [ ] Set up benchmark threshold tables

2. **Cortex Services Configuration**
   - [ ] Deploy Cortex Analyst with updated semantic model
   - [ ] Configure Cortex Search service for campaign/LTA lookup
   - [ ] Test basic queries against each service

3. **Development Environment**
   - [ ] Set up Python development environment (Python 3.10+)
   - [ ] Install dependencies: FastAPI, Snowflake connector, Pydantic
   - [ ] Configure environment variables and secrets management

**Deliverables:**
- Semantic model v2.0 deployed to Snowflake
- Cortex Analyst and Search services operational
- Development environment ready

---

### Phase 2: Orchestration Layer (Weeks 3-4)

**Objective:** Build the API-first orchestration service

#### Tasks:

1. **FastAPI Application Setup**
   - [ ] Create FastAPI project structure
   - [ ] Implement health check and status endpoints
   - [ ] Set up logging and error handling
   - [ ] Configure CORS for web application access

2. **Intent Classification**
   - [ ] Design intent classification logic (rule-based or LLM-based)
   - [ ] Implement query routing to appropriate Cortex services
   - [ ] Create intent categories:
     - Descriptive (metrics, KPIs)
     - Diagnostic (root cause, anomalies)
     - Predictive (forecasting)
     - Prescriptive (recommendations)

3. **Cortex Service Integrations**
   - [ ] Build Cortex Analyst API wrapper
   - [ ] Build Cortex Search API wrapper
   - [ ] Build Cortex Complete API wrapper
   - [ ] Implement error handling and retry logic

4. **Response Enhancement**
   - [ ] Design response formatting templates
   - [ ] Implement context injection (benchmarks, trends)
   - [ ] Add visualization recommendations
   - [ ] Create natural language summaries

**Deliverables:**
- FastAPI orchestration service with core endpoints
- Intent classification working for basic queries
- Integration with Cortex Analyst and Search

---

### Phase 3: Advanced Analytics (Weeks 5-6)

**Objective:** Implement diagnostic and predictive capabilities

#### Tasks:

1. **Cortex ML Integration**
   - [ ] Set up anomaly detection models
   - [ ] Implement forecasting models for key metrics
   - [ ] Create contribution explorer for root cause analysis
   - [ ] Build ML model management utilities

2. **Diagnostic Analytics**
   - [ ] Implement "Why did X happen?" query handling
   - [ ] Integrate anomaly detection into responses
   - [ ] Add YoY/MoM comparison logic
   - [ ] Create benchmark comparison framework

3. **Predictive Analytics**
   - [ ] Implement forecasting endpoints
   - [ ] Add confidence intervals to predictions
   - [ ] Create "what-if" scenario analysis
   - [ ] Build trend detection algorithms

**Deliverables:**
- Anomaly detection operational
- Forecasting models deployed
- Diagnostic query handling complete

---

### Phase 4: Presentation Layer (Weeks 7-8)

**Objective:** Build user-facing interfaces

#### Tasks:

1. **Web Application (Streamlit)**
   - [ ] Create Streamlit app structure
   - [ ] Build chat interface connected to orchestrator API
   - [ ] Add visualization components (charts, tables)
   - [ ] Implement conversation history
   - [ ] Add export functionality (PDF, CSV)

2. **Slack Integration**
   - [ ] Set up Slack app and bot
   - [ ] Implement slash commands for queries
   - [ ] Add interactive message components
   - [ ] Configure authentication and permissions

3. **Teams Integration**
   - [ ] Set up Teams app registration
   - [ ] Implement bot framework
   - [ ] Add adaptive cards for rich responses
   - [ ] Configure SSO integration

**Deliverables:**
- Streamlit web application deployed
- Slack bot operational
- Teams bot operational (optional)

---

### Phase 5: Evaluation & Optimization (Weeks 9-10)

**Objective:** Implement cost-effective evaluation framework

#### Tasks:

1. **Tiered Evaluation Framework**
   - [ ] **Tier 1:** Deterministic checks (SQL validity, response format)
   - [ ] **Tier 2:** Heuristic validation (metric ranges, logic checks)
   - [ ] **Tier 3:** LLM-as-judge (semantic correctness, only for edge cases)

2. **Performance Monitoring**
   - [ ] Implement query logging and analytics
   - [ ] Track response times by service
   - [ ] Monitor Cortex API costs
   - [ ] Create performance dashboards

3. **Quality Assurance**
   - [ ] Build test suite with verified queries
   - [ ] Implement regression testing
   - [ ] Create user acceptance testing plan
   - [ ] Document known limitations

**Deliverables:**
- Evaluation framework operational
- Performance monitoring dashboards
- Test suite with 50+ verified queries

---

### Phase 6: Production Deployment (Weeks 11-12)

**Objective:** Deploy to production and enable stakeholder access

#### Tasks:

1. **Production Infrastructure**
   - [ ] Set up production Snowflake environment
   - [ ] Deploy orchestrator API to cloud (AWS/GCP/Azure)
   - [ ] Configure load balancing and auto-scaling
   - [ ] Implement security hardening (API keys, rate limiting)

2. **Documentation**
   - [ ] Create user guide with example queries
   - [ ] Write API documentation (OpenAPI/Swagger)
   - [ ] Document deployment procedures
   - [ ] Create troubleshooting guide

3. **Training & Rollout**
   - [ ] Conduct stakeholder training sessions
   - [ ] Create demo videos and tutorials
   - [ ] Establish feedback collection process
   - [ ] Plan phased rollout strategy

**Deliverables:**
- Production deployment complete
- Documentation published
- Stakeholder training completed

---

## Technical Specifications

### Technology Stack

| Component | Technology | Version |
|-----------|-----------|---------|
| **Orchestration** | FastAPI | 0.109+ |
| **Data Platform** | Snowflake | Latest |
| **AI/ML** | Snowflake Cortex | Latest |
| **Web App** | Streamlit | 1.30+ |
| **Chat Integration** | Slack SDK / Teams SDK | Latest |
| **Language** | Python | 3.10+ |
| **Deployment** | Docker + Cloud Run/ECS | Latest |

### API Endpoints (Orchestration Layer)

#### Core Endpoints

```
POST /api/v1/query
- Submit natural language query
- Returns: Enhanced response with data, visualizations, insights

GET /api/v1/health
- Health check endpoint
- Returns: Service status

POST /api/v1/feedback
- Submit user feedback on response quality
- Returns: Acknowledgment

GET /api/v1/conversation/{session_id}
- Retrieve conversation history
- Returns: List of messages
```

#### Admin Endpoints

```
GET /api/v1/metrics
- Service performance metrics
- Returns: Response times, costs, usage stats

POST /api/v1/evaluate
- Run evaluation suite
- Returns: Evaluation results

GET /api/v1/models
- List available ML models
- Returns: Model metadata
```

### Data Models

#### Query Request

```python
class QueryRequest(BaseModel):
    query: str
    session_id: Optional[str] = None
    user_id: str
    context: Optional[Dict] = None
    preferences: Optional[Dict] = None
```

#### Query Response

```python
class QueryResponse(BaseModel):
    query: str
    intent: str  # descriptive, diagnostic, predictive, prescriptive
    data: Optional[Dict] = None
    visualizations: Optional[List[Dict]] = None
    insights: List[str]
    recommendations: Optional[List[str]] = None
    confidence: float
    sources: List[str]
    execution_time_ms: int
```

---

## Cost Optimization Strategy

### Tiered Evaluation Framework

To minimize LLM-as-judge costs while maintaining quality:

#### Tier 1: Deterministic Checks (Free)
- SQL syntax validation
- Response format validation
- Required field presence
- Data type correctness

#### Tier 2: Heuristic Validation (Free)
- Metric range checks (e.g., click rate 0-100%)
- Logical consistency (e.g., sends ≥ clicks)
- Benchmark comparison
- Historical trend alignment

#### Tier 3: LLM-as-Judge (Paid - Use Sparingly)
- Semantic correctness
- Response relevance
- Natural language quality
- Only for: new query patterns, edge cases, periodic audits

**Expected Cost Reduction:** 80-90% compared to LLM-as-judge for all queries

---

## Success Metrics

### Technical Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| **Response Time** | < 3 seconds (p95) | API latency monitoring |
| **Accuracy** | > 90% correct responses | Evaluation framework |
| **Uptime** | 99.5% | Service monitoring |
| **Cost per Query** | < $0.05 | Snowflake credits tracking |

### Business Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| **User Adoption** | 80% of stakeholders | Active user tracking |
| **Query Volume** | 500+ queries/month | Usage analytics |
| **Time Savings** | 10 hours/week | User surveys |
| **Stakeholder Satisfaction** | > 4.0/5.0 | Feedback scores |

---

## Risk Mitigation

### Technical Risks

| Risk | Mitigation |
|------|-----------|
| **Cortex API Rate Limits** | Implement caching, request queuing, graceful degradation |
| **Query Ambiguity** | Clarification prompts, intent confirmation, example suggestions |
| **Data Quality Issues** | Data validation layer, anomaly detection, user feedback loop |
| **Cost Overruns** | Budget alerts, query throttling, tiered evaluation |

### Business Risks

| Risk | Mitigation |
|------|-----------|
| **Low Adoption** | Comprehensive training, champion program, continuous improvement |
| **Inaccurate Responses** | Evaluation framework, user feedback, verified query library |
| **Scope Creep** | Phased rollout, clear requirements, change management process |

---

## Replicability Framework

DIA v2 is designed as a **template architecture** for VML MAP's client portfolio:

### Reusable Components

1. **Orchestration Service** - FastAPI template with intent classification
2. **Semantic Model Template** - YAML structure for any marketing dataset
3. **Evaluation Framework** - Tiered validation applicable to any domain
4. **Deployment Scripts** - Infrastructure-as-code for cloud deployment

### Customization Points

- **Data Layer:** Replace SFMC views with client-specific data sources
- **Semantic Model:** Update field descriptions, synonyms, relationships
- **Benchmarks:** Load client-specific or industry benchmarks
- **Branding:** Customize UI/UX for client brand guidelines

### Estimated Replication Time

- **New Client Setup:** 2-3 weeks (with existing template)
- **Data Integration:** 1-2 weeks (depending on data complexity)
- **Customization:** 1 week
- **Testing & Deployment:** 1 week

**Total:** 5-7 weeks per new client (vs. 12 weeks from scratch)

---

## Next Steps

### Immediate Actions (This Week)

1. **Review & Approve** this implementation plan with stakeholders
2. **Provision Resources:**
   - Snowflake environment (DEV, PROD)
   - Cloud infrastructure (GCP/AWS/Azure)
   - Development team assignments
3. **Kick-off Phase 1:**
   - Data layer setup
   - Semantic model updates
   - Development environment configuration

### Decision Points

- [ ] **Presentation Layer:** Streamlit vs. React for web app?
- [ ] **Chat Platform:** Slack, Teams, or both?
- [ ] **Cloud Provider:** AWS, GCP, or Azure for orchestrator deployment?
- [ ] **Intent Classification:** Rule-based vs. LLM-based routing?
- [ ] **Evaluation Strategy:** Confirm tiered approach and LLM-as-judge budget

---

## Appendix

### A. Directory Structure

```
dia-v2/
├── orchestrator/              # FastAPI orchestration service
│   ├── api/
│   │   ├── routes/
│   │   │   ├── query.py
│   │   │   ├── health.py
│   │   │   └── admin.py
│   │   └── models.py
│   ├── services/
│   │   ├── intent_classifier.py
│   │   ├── cortex_analyst.py
│   │   ├── cortex_search.py
│   │   ├── cortex_ml.py
│   │   └── response_enhancer.py
│   ├── utils/
│   │   ├── logging.py
│   │   └── config.py
│   └── main.py
├── web-app/                   # Streamlit application
│   ├── app.py
│   ├── components/
│   └── utils/
├── integrations/              # Slack/Teams bots
│   ├── slack/
│   └── teams/
├── evaluation/                # Evaluation framework
│   ├── tier1_deterministic.py
│   ├── tier2_heuristic.py
│   ├── tier3_llm_judge.py
│   └── test_suite.py
├── config/                    # Configuration files
│   ├── semantic.yaml
│   ├── benchmarks.yaml
│   └── prompts.yaml
├── scripts/                   # Deployment scripts
│   ├── deploy_semantic_model.py
│   ├── deploy_orchestrator.sh
│   └── setup_cortex_services.sql
├── tests/                     # Test suite
│   ├── unit/
│   ├── integration/
│   └── e2e/
├── docs/                      # Documentation
│   ├── user_guide.md
│   ├── api_reference.md
│   └── deployment_guide.md
├── .env.example
├── requirements.txt
├── Dockerfile
└── README.md
```

### B. Sample Queries by Intent

#### Descriptive Queries
- "What was the click rate in Spain last month?"
- "Show me all campaigns with EX30 in the name"
- "What are the top 5 countries by open rate?"

#### Diagnostic Queries
- "Why did click rate drop in Germany?"
- "What caused the spike in unsubscribes?"
- "How does our performance compare to benchmarks?"

#### Predictive Queries
- "What will next month's click rate be?"
- "Predict open rate for the next quarter"
- "What's the expected trend for engagement?"

#### Prescriptive Queries
- "How can we improve click rate in EMEA?"
- "What should we do about low engagement?"
- "Recommend campaigns to optimize"

### C. References

- [Snowflake Cortex Documentation](https://docs.snowflake.com/en/user-guide/snowflake-cortex)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Streamlit Documentation](https://docs.streamlit.io/)
- [Slack API Documentation](https://api.slack.com/)
- [Microsoft Teams Bot Framework](https://dev.teams.microsoft.com/)

---

**Document Version:** 1.0  
**Last Updated:** February 9, 2026  
**Owner:** LiMaData  
**Status:** Draft - Pending Stakeholder Review
