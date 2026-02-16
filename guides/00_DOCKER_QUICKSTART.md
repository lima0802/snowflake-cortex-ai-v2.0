# Docker Quick Start Guide - DIA v2.0

## 🚀 Services Running

Your DIA v2.0 application is now running with two services:

### 1. Orchestrator (FastAPI Backend)
- **URL**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/api/v1/health

### 2. Web App (Streamlit Frontend)
- **URL**: http://localhost:8501

## 📋 Common Commands

### Start Services
```bash
# Start in foreground (see logs)
docker-compose up

# Start in background
docker-compose up -d
```

### Stop Services
```bash
# Stop services
docker-compose down

# Stop and remove volumes
docker-compose down -v
```

### View Logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f orchestrator
docker-compose logs -f web-app
```

### Rebuild After Code Changes
```bash
# Rebuild specific service
docker-compose up --build orchestrator

# Rebuild all services
docker-compose up --build
```

### Restart Services
```bash
# Restart all
docker-compose restart

# Restart specific service
docker-compose restart orchestrator
```

## 🔍 Testing

### Test Orchestrator API
```bash
# Health check
curl http://localhost:8000/api/v1/health

# Root endpoint
curl http://localhost:8000/

# Test query endpoint
curl -X POST http://localhost:8000/api/v1/query \
  -H "Content-Type: application/json" \
  -d '{"query": "What was the click rate last month?"}'
```

### Access Web App
Open browser: http://localhost:8501

## 🐛 Troubleshooting

### Services Won't Start
```bash
# Check Docker is running
docker info

# Check container status
docker-compose ps

# View error logs
docker-compose logs
```

### Port Already in Use
```bash
# Check what's using port 8000
netstat -ano | findstr :8000

# Check what's using port 8501
netstat -ano | findstr :8501

# Change ports in docker-compose.yml if needed
```

### Code Changes Not Reflected
```bash
# Rebuild the container
docker-compose up --build orchestrator

# Or restart with volume refresh
docker-compose down
docker-compose up
```

## 📊 Service Status

Check service health:
- Orchestrator: http://localhost:8000/api/v1/health
- Web App: http://localhost:8501/_stcore/health

## 🔐 Environment Variables

Configured in `.env` file:
- SNOWFLAKE_ACCOUNT
- SNOWFLAKE_USER
- SNOWFLAKE_PASSWORD
- SNOWFLAKE_WAREHOUSE
- SNOWFLAKE_DATABASE
- SNOWFLAKE_SCHEMA
- SNOWFLAKE_ROLE

## 📝 Next Steps

1. **Implement Orchestrator Logic** ([orchestrator/main.py](orchestrator/main.py))
   - Intent classification
   - Cortex service wrappers
   - Response enhancement

2. **Enhance Web App** ([web-app/app.py](web-app/app.py))
   - Add visualizations
   - Improve UI components
   - Add export functionality

3. **Add API Routes** ([orchestrator/api/routes/](orchestrator/api/routes/))
   - Query route
   - Admin route
   - Metrics route

4. **Implement Services** ([orchestrator/services/](orchestrator/services/))
   - cortex_analyst.py
   - cortex_search.py
   - cortex_ml.py
   - intent_classifier.py

## 🎯 Current Implementation Status

✅ Docker containerization
✅ Requirements.txt with dependencies
✅ Basic FastAPI orchestrator
✅ Basic Streamlit web app
✅ Environment configuration
✅ Health check endpoints
⏳ Intent classification (TODO)
⏳ Cortex service integration (TODO)
⏳ Response enhancement (TODO)
⏳ Advanced visualizations (TODO)

---

**DIA v2.0** - Direct Marketing Analytics Intelligence
Powered by Snowflake Cortex AI
