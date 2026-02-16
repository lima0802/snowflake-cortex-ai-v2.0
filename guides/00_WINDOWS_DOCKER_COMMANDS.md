# Windows Docker Commands - Quick Reference

## 🐛 Common Error: "the input device is not a TTY"

This happens when using `-it` flags in certain Windows terminals (Git Bash, MinTTY, VSCode terminal).

---

## ✅ Working Commands for Windows

### Run Python Scripts (No TTY Required)
```bash
# Test logging
docker exec dia-orchestrator python test_logging.py

# Test Snowflake connection
docker exec dia-orchestrator python ../tests/test_connection.py

# Run pytest
docker exec dia-orchestrator pytest -v

# Execute Python code directly
docker exec dia-orchestrator python -c "print('Hello from container')"
```

### Check Container Status
```bash
# View running containers
docker-compose ps

# View logs (real-time)
docker-compose logs -f orchestrator

# View last 50 lines
docker-compose logs --tail=50 orchestrator

# Check container info
docker exec dia-orchestrator python --version
docker exec dia-orchestrator pip list
docker exec dia-orchestrator ls -la
```

### Test API Endpoints
```bash
# Health check
curl http://localhost:8000/api/v1/health

# Root endpoint
curl http://localhost:8000/

# API documentation (open in browser)
start http://localhost:8000/docs
```

---

## 🔧 Interactive Shell Options

### Option 1: PowerShell (Best for Windows)
```powershell
# Open PowerShell (not Git Bash)
# Then run:
docker exec -it dia-orchestrator /bin/bash
```

### Option 2: Git Bash with winpty
```bash
# In Git Bash, add winpty prefix:
winpty docker exec -it dia-orchestrator /bin/bash
winpty docker exec -it dia-orchestrator python
```

### Option 3: Docker Desktop GUI (Easiest)
1. Open **Docker Desktop**
2. Click **Containers** in left sidebar
3. Find `dia-orchestrator`
4. Click the **CLI** button (terminal icon on the right)
5. Interactive shell opens automatically ✅

### Option 4: VSCode Docker Extension
1. Install **Docker** extension in VSCode
2. Click Docker icon in left sidebar
3. Expand **Containers**
4. Right-click `dia-orchestrator`
5. Select **Attach Shell**

---

## 📝 Testing Checklist

Copy-paste these commands to test your setup:

```bash
# 1. Check containers are running
docker-compose ps

# 2. Test orchestrator health
curl http://localhost:8000/api/v1/health

# 3. Check container access
docker exec dia-orchestrator python --version

# 4. List files in container
docker exec dia-orchestrator ls -la

# 5. Test Python imports
docker exec dia-orchestrator python -c "import fastapi; print(fastapi.__version__)"

# 6. Run test script
docker exec dia-orchestrator python test_logging.py

# 7. Check logs
docker-compose logs --tail=20 orchestrator
```

---

## 🚀 Development Workflow

### After Code Changes
```bash
# Changes are auto-reloaded (volumes mounted)
# Just save your file and check logs:
docker-compose logs -f orchestrator

# If changes not reflected, restart:
docker-compose restart orchestrator

# If requirements.txt changed, rebuild:
docker-compose up --build orchestrator
```

### Debugging
```bash
# View real-time logs
docker-compose logs -f

# View specific service logs
docker-compose logs -f orchestrator
docker-compose logs -f web-app

# Check container resource usage
docker stats dia-orchestrator

# Inspect container
docker inspect dia-orchestrator
```

### Stop/Start Services
```bash
# Stop all services
docker-compose down

# Start all services
docker-compose up -d

# Restart specific service
docker-compose restart orchestrator

# Stop specific service
docker-compose stop orchestrator
```

---

## 🎯 Quick Tests You Can Run Now

### Test 1: Orchestrator Health
```bash
curl http://localhost:8000/api/v1/health
```
**Expected:** JSON response with Snowflake config

### Test 2: API Documentation
```bash
start http://localhost:8000/docs
```
**Expected:** FastAPI Swagger UI opens in browser

### Test 3: Web App
```bash
start http://localhost:8501
```
**Expected:** Streamlit app opens in browser

### Test 4: Container Access
```bash
docker exec dia-orchestrator python -c "import sys; print(sys.version)"
```
**Expected:** Python version output

### Test 5: Check Packages
```bash
docker exec dia-orchestrator pip list | findstr snowflake
```
**Expected:** List of Snowflake packages

### Test 6: View Container Files
```bash
docker exec dia-orchestrator ls -la /app
```
**Expected:** List of orchestrator files

---

## 💡 Pro Tips

1. **Use PowerShell for interactive sessions** - Best Windows compatibility
2. **Use regular Command Prompt** - Also works well for non-interactive commands
3. **Avoid Git Bash for interactive Docker** - Requires `winpty` prefix
4. **Use Docker Desktop GUI** - Easiest for quick shell access
5. **Check logs frequently** - `docker-compose logs -f` is your friend
6. **Hot reload works** - Python files auto-reload on save (volume mounted)

---

## 🆘 Troubleshooting

### Error: "Cannot connect to Docker daemon"
```bash
# Solution: Start Docker Desktop
# Check if running:
docker info
```

### Error: "TTY input" issues
```bash
# Solution: Remove -it flags or use PowerShell
docker exec dia-orchestrator python test_logging.py
```

### Error: "Container not found"
```bash
# Solution: Check container name
docker-compose ps

# Or use container ID
docker ps
docker exec <container-id> python test_logging.py
```

### Changes not reflected
```bash
# Solution 1: Check logs for auto-reload
docker-compose logs -f orchestrator

# Solution 2: Restart service
docker-compose restart orchestrator

# Solution 3: Rebuild (if requirements changed)
docker-compose up --build orchestrator
```

---

## 📚 Additional Resources

- [TESTING_GUIDE.md](TESTING_GUIDE.md) - Complete testing documentation
- [DOCKER_QUICKSTART.md](DOCKER_QUICKSTART.md) - Docker basics
- [DIA_V2_IMPLEMENTATION_PLAN.md](DIA_V2_IMPLEMENTATION_PLAN.md) - Implementation phases

---

**Remember:** For most testing, you don't need interactive shells. Use `docker exec dia-orchestrator python <script>.py` instead! ✅
