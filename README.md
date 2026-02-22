# DIA v2.0 - Direct Marketing Analytics Intelligence

Snowflake Cortex AI-powered analytics orchestrator for SFMC email performance analysis.

## 🚀 Quick Start

### Prerequisites
- Docker Desktop installed and running
- Snowflake account with Cortex services enabled
- Python 3.11+ (for local development)

### Setup

1. **Clone and navigate to project:**
   ```powershell
   cd "c:\Users\LiMa\OneDrive - WPP Cloud\Documentos\Li\05_Project\01_Volvo\DIA\snowflake-cortex-ai-v2.0"
   ```

2. **Configure environment:**
   ```bash
   # Copy .env.example to .env (if exists) or create .env with:
   SNOWFLAKE_ACCOUNT=your-account
   SNOWFLAKE_USER=your-user
   SNOWFLAKE_PASSWORD=your-password
   SNOWFLAKE_WAREHOUSE=your-warehouse
   SNOWFLAKE_DATABASE=your-database
   SNOWFLAKE_SCHEMA=your-schema
   SNOWFLAKE_ROLE=your-role
   ```

3. **Start Docker containers:**
   ```bash
   docker-compose up --build
   ```

4. **Access services:**
   - **Orchestrator API**: http://localhost:8000
   - **API Documentation**: http://localhost:8000/docs
   - **Web Application**: http://localhost:8501

## 📚 Documentation

### Implementation Guides
All step-by-step guides are in the **[guides/](guides/)** directory:

- **[guides/README.md](guides/README.md)** - Master guide index and progress tracker
- **[guides/00_DOCKER_SETUP_COMPLETE.md](guides/00_DOCKER_SETUP_COMPLETE.md)** - Complete Docker setup guide (from zero)
- **[guides/00_WINDOWS_DOCKER_COMMANDS.md](guides/00_WINDOWS_DOCKER_COMMANDS.md)** - Windows-specific commands
- **[guides/00_TESTING_GUIDE.md](guides/00_TESTING_GUIDE.md)** - Testing procedures
- **[guides/01_STEP_1.2_DATA_LAYER_SETUP.md](guides/01_STEP_1.2_DATA_LAYER_SETUP.md)** - Data layer implementation

### Architecture Documentation
- **[DIA_V2_IMPLEMENTATION_PLAN.md](DIA_V2_IMPLEMENTATION_PLAN.md)** - Complete implementation plan with architecture details

## 🏗️ Project Structure

```
snowflake-cortex-ai-v2.0/
├── guides/                    # Implementation guides (START HERE)
│   ├── README.md             # Guide index and progress tracker
│   ├── 00_*.md              # Setup and testing guides
│   └── 01-10_*.md           # Implementation step guides
│
├── orchestrator/             # FastAPI backend service
│   ├── main.py              # Application entry point
│   ├── requirements.txt     # Python dependencies
│   ├── Dockerfile           # Container configuration
│   ├── api/                 # API routes and models
│   ├── services/            # Cortex service wrappers
│   └── utils/               # Utilities (config, logging)
│
├── web-app/                  # Streamlit frontend
│   ├── app.py               # Streamlit application
│   ├── requirements.txt     # Python dependencies
│   ├── Dockerfile           # Container configuration
│   └── components/          # UI components
│
├── data-layer/               # Snowflake SQL scripts
│   ├── views/               # Semantic views
│   ├── benchmarks/          # Benchmark data
│   └── ml-models/           # ML model setup
│
├── config/                   # Configuration files
│   ├── semantic.yaml        # Cortex Analyst semantic model
│   └── agent_spec.yaml      # Cortex Agent specification
│
├── scripts/                  # Deployment scripts
│   ├── deploy_semantic_model.py
│   ├── deploy_agent.py
│   └── test_connection.py
│
├── tests/                    # Test files
│   └── test_connection.py
│
├── docker-compose.yml        # Multi-container orchestration
├── .env                      # Environment variables (not in git)
└── README.md                 # This file
```

## 🧪 Testing

```powershell
# Test Snowflake connection
docker exec dia-orchestrator python test_connection.py

# Test API health
curl http://localhost:8000/api/v1/health

# View logs
docker-compose logs --tail=50 orchestrator

# Run pytest (once implemented)
docker exec dia-orchestrator pytest -v
```

See [guides/00_TESTING_GUIDE.md](guides/00_TESTING_GUIDE.md) for complete testing documentation.

## 📊 Current Status

**Phase 1: Foundation Setup** ✅
- Docker containerization ✅
- Python dependencies ✅
- Snowflake connection ✅
- Basic API endpoints ✅
- Data layer SQL scripts ✅

**Phase 2: Core Services** ⏳
- Cortex service wrappers (planned)
- Intent classifier (planned)
- Response enhancer (planned)

**Phase 3: Orchestration** ⏳
- API routes (health endpoint complete)
- Conversation management (planned)

**Phase 4: Presentation** ⏳
- Web application (basic UI complete)
- Integration channels (planned)

**Phase 5: Evaluation & Deployment** ⏳
- Evaluation framework (planned)
- Production deployment (planned)

See [guides/README.md](guides/README.md) for detailed progress tracker.

## 🎯 Architecture

### Layer 1: Presentation
- **Web App** (Streamlit) - Primary UI
- **Slack/Teams** - Conversational interfaces
- **REST API** - Programmatic access

### Layer 2: Orchestration (FastAPI)
- **Intent Classification** - Route queries
- **Tool Selection** - Choose Cortex service
- **Response Enhancement** - Add context
- **Conversation Management** - Multi-turn support

### Layer 3: Intelligence (Snowflake Cortex)
- **Cortex Analyst** - NL-to-SQL queries
- **Cortex Search** - Vector search / RAG
- **Cortex ML** - Forecasting, anomaly detection
- **Cortex Complete** - LLM text generation

### Layer 4: Data (Snowflake)
- **Semantic Views** - Standardized SFMC data
- **Benchmark Data** - Industry standards
- **ML Models** - Trained models for predictions

## 🔧 Development

### Docker Commands
```bash
# Start services
docker-compose up

# Rebuild after code changes
docker-compose up --build

# Stop services
docker-compose down

# View logs
docker-compose logs -f orchestrator
docker-compose logs -f web-app

# Access container shell (PowerShell)
docker exec -it dia-orchestrator /bin/bash
```

### Local Development (without Docker)
```bash
# Install orchestrator dependencies
cd orchestrator
pip install -r requirements.txt

# Install web app dependencies
cd ../web-app
pip install -r requirements.txt

# Run tests
cd ../tests
python test_connection.py
```

## 📖 Additional Resources

- **Snowflake Cortex Analyst**: https://docs.snowflake.com/en/user-guide/snowflake-cortex/cortex-analyst
- **Snowflake Cortex ML**: https://docs.snowflake.com/en/user-guide/snowflake-cortex/ml-functions
- **FastAPI Documentation**: https://fastapi.tiangolo.com/
- **Streamlit Documentation**: https://docs.streamlit.io/

## 🤝 Contributing

When implementing new features:
1. Follow the implementation plan in [DIA_V2_IMPLEMENTATION_PLAN.md](DIA_V2_IMPLEMENTATION_PLAN.md)
2. Refer to guides in [guides/](guides/) directory
3. Write tests for new functionality
4. Update documentation

## 📝 License

See [LICENSE](LICENSE) file for details.

---

**Project:** DIA v2.0 - Direct Marketing Analytics Intelligence
**Stack:** Snowflake Cortex AI, FastAPI, Streamlit, Docker
**Status:** Phase 1 Complete, Phase 2 In Progress
**Last Updated:** February 16, 2026