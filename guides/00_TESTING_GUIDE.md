# Testing Guide - DIA v2.0

## 🚀 Quick Start - Most Common Commands

**First, navigate to your project directory in PowerShell:**
```powershell
cd "c:\Users\LiMa\OneDrive - WPP Cloud\Documentos\Li\05_Project\01_Volvo\DIA\snowflake-cortex-ai-v2.0"
```

**Then run these tests:**
```powershell
# Test Snowflake connection (✅ Working!)
docker exec dia-orchestrator python test_connection.py

# Test logging (⏳ Needs implementation)
docker exec dia-orchestrator python test_logging.py

# Test API health
curl http://localhost:8000/api/v1/health

# View logs
docker-compose logs --tail=50 orchestrator
```

---

## Where to Test Code

You have **3 main testing locations** depending on what you're testing:

### 1. 🐳 Run Commands in Docker Container (Recommended)

**Best for:** Testing code in the actual runtime environment

**⚠️ IMPORTANT: Always run from your project directory first!**
```powershell
cd "c:\Users\LiMa\OneDrive - WPP Cloud\Documentos\Li\05_Project\01_Volvo\DIA\snowflake-cortex-ai-v2.0"
```

**Non-Interactive Commands (Works in all terminals):**
```powershell
# Execute Python commands directly
docker exec dia-orchestrator python -c "print('Hello from container')"

# Run a test script
docker exec dia-orchestrator python test_logging.py

# Run Snowflake connection test
docker exec dia-orchestrator python test_connection.py

# Check Python packages
docker exec dia-orchestrator pip list

# List files in container
docker exec dia-orchestrator ls -la
```

**Interactive Shell (PowerShell only):**
```powershell
# Access container bash shell
docker exec -it dia-orchestrator /bin/bash

# When inside container (root@...:/app#):
ls -la
python test_logging.py
python test_connection.py
exit  # to leave container
```

**Why use Docker exec:**
- ✅ Same environment as production
- ✅ All dependencies installed
- ✅ Environment variables loaded
- ✅ Tests containerized code
- ✅ No need to install packages on Windows

---

### 2. 📝 Create Test Scripts in Project

**Best for:** Repeatable, documented tests

**Location:** Create test files in your project directories:
- `orchestrator/test_logging.py` - Test logging configuration
- `orchestrator/test_services.py` - Test Cortex services
- `tests/test_connection.py` - Test Snowflake connection (already exists)

**Example:**
```python
# orchestrator/test_logging.py
if __name__ == "__main__":
    from utils.logging import configure_logging, get_logger
    configure_logging()
    logger = get_logger(__name__)
    logger.info("test", component="setup")
```

**Run inside container:**
```bash
docker exec dia-orchestrator python test_logging.py
```

---

### 3. 🧪 Use pytest Framework

**Best for:** Automated testing, CI/CD integration

**Location:** `tests/` directory (already exists)

**Create test files:**
```python
# tests/test_orchestrator.py
import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_health_check():
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_query_endpoint():
    response = client.post("/api/v1/query", json={"query": "test"})
    assert response.status_code == 200
```

**Run pytest:**
```bash
# Run all tests
docker exec dia-orchestrator pytest

# Run specific test file
docker exec dia-orchestrator pytest tests/test_orchestrator.py

# Run with verbose output
docker exec dia-orchestrator pytest -v

# Run with coverage
docker exec dia-orchestrator pytest --cov=orchestrator
```

---

## Current Testing Status

### ✅ What You Can Test Now

**Navigate to project first:**
```powershell
cd "c:\Users\LiMa\OneDrive - WPP Cloud\Documentos\Li\05_Project\01_Volvo\DIA\snowflake-cortex-ai-v2.0"
```

**Then test:**

1. **Orchestrator Health Check:**
   ```powershell
   curl http://localhost:8000/api/v1/health
   ```
   Expected: JSON response with Snowflake configuration ✅

2. **Snowflake Connection:**
   ```powershell
   docker exec dia-orchestrator python test_connection.py
   ```
   Expected: "CONNECTION SUCCESSFUL!" ✅

3. **API Documentation:**
   ```powershell
   start http://localhost:8000/docs
   ```
   Expected: FastAPI Swagger UI opens in browser ✅

4. **Web App Interface:**
   ```powershell
   start http://localhost:8501
   ```
   Expected: Streamlit app opens in browser ✅
   - Click "Check Orchestrator Health" button to test connection

### ⏳ What Needs Implementation First

Before you can test these, implement the modules:

1. **Logging Configuration** (`orchestrator/utils/logging.py`)
   - Test with: `docker exec dia-orchestrator python test_logging.py`
   - Status: ❌ Not implemented

2. **Cortex Services** (`orchestrator/services/`)
   - cortex_analyst.py
   - cortex_search.py
   - cortex_ml.py
   - cortex_complete.py
   - Status: ❌ Not implemented

3. **Intent Classifier** (`orchestrator/services/intent_classifier.py`)
   - Status: ❌ Not implemented

---

## Implementation Order (From DIA_V2_IMPLEMENTATION_PLAN.md)

### Phase 1: Foundation (Week 1)
**Step 1.1: Implement Utility Modules**
- [ ] `orchestrator/utils/config.py`
- [ ] `orchestrator/utils/logging.py`

**Step 1.2: Implement Pydantic Models**
- [ ] `orchestrator/api/models.py`

### Phase 2: Core Services (Week 2)
**Step 2.1: Implement Cortex Service Wrappers**
- [ ] `orchestrator/services/cortex_analyst.py`
- [ ] `orchestrator/services/cortex_search.py`
- [ ] `orchestrator/services/cortex_ml.py`
- [ ] `orchestrator/services/cortex_complete.py`

---

## Quick Testing Commands (Copy-Paste Ready)

**Step 1: Navigate to project directory**
```powershell
cd "c:\Users\LiMa\OneDrive - WPP Cloud\Documentos\Li\05_Project\01_Volvo\DIA\snowflake-cortex-ai-v2.0"
```

### Test Current Setup
```powershell
# Check Docker containers are running
docker-compose ps

# Check orchestrator health
curl http://localhost:8000/api/v1/health

# Test Snowflake connection (✅ Working!)
docker exec dia-orchestrator python test_connection.py

# Open API docs in browser
start http://localhost:8000/docs

# Open web app in browser
start http://localhost:8501

# View orchestrator logs (last 50 lines)
docker-compose logs --tail=50 orchestrator

# View real-time logs
docker-compose logs -f orchestrator
```

### Test After Implementation
```powershell
# Test logging (once implemented)
docker exec dia-orchestrator python test_logging.py

# Run all pytest tests
docker exec dia-orchestrator pytest -v

# Test specific API endpoint
curl -X POST http://localhost:8000/api/v1/query -H "Content-Type: application/json" -d "{\"query\": \"What was the click rate?\"}"
```

---

## Common Issues & Solutions

### Issue 1: "can't open file 'C:\\tests\\test_connection.py'"

**Problem:** You're running Python command from Windows PowerShell, not inside container.

**Solution:**
```powershell
# ❌ Wrong (tries to find file on Windows)
python tests/test_connection.py

# ✅ Correct (runs inside container)
docker exec dia-orchestrator python test_connection.py
```

### Issue 2: "the input device is not a TTY"

**Problem:** Using `-it` flags in Git Bash or certain terminals.

**Solutions:**
```powershell
# Option 1: Use PowerShell (not Git Bash)
docker exec -it dia-orchestrator /bin/bash

# Option 2: Remove -it flags
docker exec dia-orchestrator python test_logging.py

# Option 3: Use Docker Desktop GUI
# Containers → dia-orchestrator → CLI button
```

### Issue 3: File not found in container

**Problem:** Test file is in `tests/` directory, which isn't mounted in container.

**Solution:** Copy file to container first
```powershell
# Copy file to container
docker cp tests/test_connection.py dia-orchestrator:/app/

# Then run it
docker exec dia-orchestrator python test_connection.py
```
Note: I already copied `test_connection.py` for you ✅

### Issue 4: Lost in container shell

**Problem:** You're inside container (`root@...:/app#`) but want to exit.

**Solution:**
```bash
# Just type:
exit
# Or press: Ctrl+D
```

## Debugging Tips

### View Container Logs
```powershell
# Real-time logs (press Ctrl+C to stop)
docker-compose logs -f

# Last 100 lines
docker-compose logs --tail=100

# Specific service
docker-compose logs -f orchestrator
docker-compose logs -f web-app
```

### Interactive Container Access

**⚠️ Windows Terminal Issues:**
If you get `the input device is not a TTY` error, you have these options:

**Option 1: Use PowerShell (Recommended)**
```powershell
# Open PowerShell and run:
docker exec -it dia-orchestrator /bin/bash
docker exec -it dia-orchestrator python
```

**Option 2: Use winpty prefix (Git Bash/MinTTY)**
```bash
# If using Git Bash:
winpty docker exec -it dia-orchestrator /bin/bash
winpty docker exec -it dia-orchestrator python
```

**Option 3: Run Non-Interactive Commands (Works Everywhere)**
```bash
# Execute single commands without shell
docker exec dia-orchestrator python test_logging.py
docker exec dia-orchestrator pip list
docker exec dia-orchestrator python -c "print('Hello')"

# List files
docker exec dia-orchestrator ls -la

# Check Python version
docker exec dia-orchestrator python --version
```

**Option 4: Docker Desktop CLI**
1. Open Docker Desktop
2. Go to "Containers" tab
3. Click on `dia-orchestrator` container
4. Click "CLI" button (terminal icon)
5. This opens an interactive shell directly

### Restart After Code Changes
```bash
# Hot reload (if volume mounted - already configured)
# Just save your Python files, Docker will auto-reload

# Manual restart
docker-compose restart orchestrator

# Rebuild if dependencies changed
docker-compose up --build orchestrator
```

---

## Testing Best Practices

1. **Start Simple:** Test basic functionality first (health checks, connections)
2. **Test in Containers:** Always test in Docker environment, not local Python
3. **Use Test Scripts:** Create reusable test scripts for complex scenarios
4. **Add pytest Tests:** Write automated tests for CI/CD
5. **Check Logs:** Always check logs when something fails
6. **Incremental Development:** Implement → Test → Debug → Repeat

---

## 📊 Testing Status Summary

| Test | Command | Status |
|------|---------|--------|
| Snowflake Connection | `docker exec dia-orchestrator python test_connection.py` | ✅ Working |
| API Health | `curl http://localhost:8000/api/v1/health` | ✅ Working |
| API Docs | `start http://localhost:8000/docs` | ✅ Working |
| Web App | `start http://localhost:8501` | ✅ Working |
| Logging Module | `docker exec dia-orchestrator python test_logging.py` | ⏳ Not implemented |
| Cortex Services | N/A | ⏳ Not implemented |
| Intent Classifier | N/A | ⏳ Not implemented |
| pytest Suite | `docker exec dia-orchestrator pytest -v` | ⏳ Not implemented |

## Next Steps

1. ✅ **You are here:** Basic Docker setup working, Snowflake connection tested
2. ⏳ **Next:** Implement `orchestrator/utils/logging.py` (Phase 1, Step 1.1)
3. ⏳ **Then:** Test logging with `docker exec dia-orchestrator python test_logging.py`
4. ⏳ **Continue:** Follow implementation plan phases

## 🎯 Key Takeaways

**Remember these rules:**

1. **Always navigate to project directory first**
   ```powershell
   cd "c:\Users\LiMa\OneDrive - WPP Cloud\Documentos\Li\05_Project\01_Volvo\DIA\snowflake-cortex-ai-v2.0"
   ```

2. **Run tests inside container**
   ```powershell
   docker exec dia-orchestrator python <script>.py
   ```

3. **Check if you're in Windows or Container**
   - `PS C:\>` = Windows PowerShell → use `docker exec`
   - `root@...:/app#` = Inside container → use `python` directly

4. **Use PowerShell for interactive shells**
   ```powershell
   docker exec -it dia-orchestrator /bin/bash
   ```

5. **View logs when debugging**
   ```powershell
   docker-compose logs --tail=50 orchestrator
   ```

## 📚 Additional Resources

- [WINDOWS_DOCKER_COMMANDS.md](WINDOWS_DOCKER_COMMANDS.md) - Windows-specific Docker commands
- [DOCKER_QUICKSTART.md](DOCKER_QUICKSTART.md) - Docker basics and common operations
- [DIA_V2_IMPLEMENTATION_PLAN.md](DIA_V2_IMPLEMENTATION_PLAN.md) - Complete implementation roadmap
