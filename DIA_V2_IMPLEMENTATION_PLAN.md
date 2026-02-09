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
│   ├── create_agent.sql                  # Cortex Agent creation SQL
│   ├── deploy_agent.py                   # Agent deployment automation
│   ├── deploy_semantic_model.py          # Semantic model deployment
│   ├── inspect_agent.py                  # Agent inspection utility
│   ├── migrate_semantic_objects.py       # Semantic object migration
│   └── setup_benchmarks.sql              # Benchmark data loading
│
├── docs/                                 # Documentation
│   ├── user_guide.md                     # End-user query guide
│   ├── api_reference.md                  # OpenAPI/Swagger reference
│   └── deployment_guide.md               # Production deployment steps
│
│── ──────────────────────────────────────────────────────
│   REFERENCE & TRAINING (existing)
│── ──────────────────────────────────────────────────────
│
├── instructor-setup/                     # Instructor training materials
│   ├── AGENT_SETUP.md
│   ├── INSTRUCTOR_SETUP_WIP.md
│   └── SEMANTIC_DEPLOY.md
│
├── participant-setup/                    # Participant onboarding
│   ├── FILE_UPLOAD_GUIDE.md
│   ├── PARTICIPANT_GUIDE.md
│   ├── README.md
│   └── setup.sql
│
├── sample-data/                          # Sample documents for Cortex Search
│   ├── README.md
│   └── docs/
│       ├── *.pdf                         # Product specification guides
│       └── *.jpeg                        # Product images
│
├── AGENT_DEPLOYMENT_GUIDE.md
├── MIGRATION_SUMMARY.md
└── WHY_USE_SNOWSIGHT.md
```
