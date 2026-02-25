# Docker Setup Guide - DIA v2.0 (Complete From Zero)

**Complete Docker setup guide for Windows users - from installation to running DIA v2.0**

---

## Table of Contents

1. [Prerequisites & Installation](#prerequisites--installation)
2. [Initial Project Setup](#initial-project-setup)
3. [Docker Configuration](#docker-configuration)
4. [Building & Running Services](#building--running-services)
5. [Testing & Verification](#testing--verification)
6. [Development Workflow](#development-workflow)
7. [Windows-Specific Commands](#windows-specific-commands)
8. [Troubleshooting](#troubleshooting)

---

## Prerequisites & Installation

### Step 1: Install Docker Desktop for Windows

1. **System Requirements:**
   - Windows 10 64-bit: Pro, Enterprise, or Education (Build 19041 or higher)
   - Windows 11 64-bit
   - WSL 2 feature enabled
   - At least 4GB RAM (8GB recommended)
   - Virtualization enabled in BIOS

2. **Download Docker Desktop:**
   - Visit: https://www.docker.com/products/docker-desktop/
   - Click "Download for Windows"
   - Run the installer: `Docker Desktop Installer.exe`

3. **Installation Steps:**
   ```
   ✅ Use WSL 2 instead of Hyper-V (recommended)
   ✅ Add shortcut to desktop
   ✅ Install required Windows components
   ```

4. **Enable WSL 2 (if not already enabled):**
   ```powershell
   # Open PowerShell as Administrator
   wsl --install
   
   # Restart computer if prompted
   
   # Verify WSL 2 is installed
   wsl --list --verbose
   ```

5. **Start Docker Desktop:**
   - Launch Docker Desktop from Start menu
   - Wait for "Docker Desktop is running" message
   - Verify Docker icon in system tray shows green

6. **Verify Installation:**
   ```powershell
   # Check Docker version
   docker --version
   # Expected: Docker version 24.0.x or higher
   
   # Check Docker Compose version
   docker-compose --version
   # Expected: Docker Compose version v2.x.x or higher
   
   # Test Docker is working
   docker run hello-world
   # Expected: "Hello from Docker!" message
   ```

### Step 2: Install Git (if not already installed)

```powershell
# Check if Git is installed
git --version

# If not installed, download from:
# https://git-scm.com/download/win
```

### Step 3: Install Python (Optional - for local development)

```powershell
# Download Python 3.11+ from:
# https://www.python.org/downloads/

# Verify installation
python --version
# Expected: Python 3.11.x or higher
```

---

## Initial Project Setup

### Step 1: Clone or Navigate to Project

```powershell
# If cloning from GitHub
git clone https://github.com/lima0802/snowflake-cortex-ai-v2.0.git
cd snowflake-cortex-ai-v2.0

# If already have project
cd path\to\snowflake-cortex-ai-v2.0
```

### Step 2: Configure Environment Variables

1. **Create `.env` file in project root:**
   ```powershell
   # Copy template
   Copy-Item .env.example .env
   
   # Or create manually
   New-Item -Path .env -ItemType File
   ```

2. **Edit `.env` file with your Snowflake credentials:**
   ```ini
   # Snowflake Connection
   SNOWFLAKE_ACCOUNT=your_account.region
   SNOWFLAKE_USER=your_username
   SNOWFLAKE_PASSWORD=your_password
   SNOWFLAKE_WAREHOUSE=your_warehouse
   SNOWFLAKE_DATABASE=PLAYGROUND_LM
   SNOWFLAKE_SCHEMA=CORTEX_ANALYTICS_ORCHESTRATOR
   SNOWFLAKE_ROLE=your_role
   
   # Application Settings
   ENVIRONMENT=development
   LOG_LEVEL=INFO
   
   # Optional: API Keys
   OPENAI_API_KEY=your_openai_key_if_needed
   ```

3. **Secure `.env` file:**
   ```powershell
   # Verify .env is in .gitignore
   Select-String -Path .gitignore -Pattern "\.env"
   # Expected: Should show .env in list
   ```

### Step 3: Review Project Structure

```
snowflake-cortex-ai-v2.0/
├── .env                     # ← Your credentials (just created)
├── docker-compose.yml       # ← Multi-container orchestration
├── orchestrator/
│   ├── Dockerfile          # ← Orchestrator container config
│   ├── requirements.txt    # ← Python dependencies
│   └── main.py            # ← FastAPI application
├── web-app/
│   ├── Dockerfile          # ← Web app container config
│   ├── requirements.txt    # ← Streamlit dependencies
│   └── app.py             # ← Streamlit application
└── guides/                 # ← Documentation (you are here)
```

---

## Docker Configuration

### Understanding docker-compose.yml

The `docker-compose.yml` file defines two services:

```yaml
services:
  orchestrator:
    # FastAPI backend on port 8000
    # Handles AI orchestration and Cortex integration
    
  web-app:
    # Streamlit frontend on port 8501
    # User interface for DIA v2.0
```

### Check Docker Compose File

```powershell
# View docker-compose.yml content
Get-Content docker-compose.yml

# Validate syntax
docker-compose config
# Expected: Parsed YAML configuration displayed
```

### Verify Dockerfiles Exist

```powershell
# Check orchestrator Dockerfile
Test-Path orchestrator/Dockerfile

# Check web-app Dockerfile
Test-Path web-app/Dockerfile

# Both should return: True
```

---

## Modern Dependency Management with UV + Docker

### Why UV for CI/CD and Production?

**⚡ Performance Breakthrough:** DIA v2.0 now uses **UV (by Astral)** for dependency management inside Docker containers, providing **10-100x faster builds** compared to traditional pip.

#### Key Benefits for Dev/Prod Consistency:

| Feature | Traditional pip | UV (New Standard) |
|---------|----------------|-------------------|
| **Build Speed** | 100s for Snowflake deps | 10-15s |
| **Lock File** | requirements.txt (loose) | uv.lock (precise) |
| **Reproducibility** | ⚠️ Can drift | ✅ Guaranteed |
| **CI/CD Performance** | Slow | ⚡ Blazing fast |
| **Docker Layer Caching** | Basic | Optimized |
| **Multi-Environment** | Manual | Built-in |

### Architecture: Multi-Stage Docker Build

```dockerfile
# Stage 1: Builder (Install with UV)
FROM ghcr.io/astral-sh/uv:python3.11-bookworm-slim AS builder
RUN uv venv /app/.venv && uv pip install -r pyproject.toml

# Stage 2: Production (Slim runtime)
FROM python:3.11-slim AS production
COPY --from=builder /app/.venv /app/.venv
# Result: Minimal image size with deterministic dependencies
```

### Environment Strategy: Dev vs Prod

**Development Environment (`ENV=dev`):**
```powershell
# Features:
# ✅ Hot-reload enabled
# ✅ Source code mounted as volumes
# ✅ Debug tools included
# ✅ Lower resource limits

# Start development
$env:ENV = "dev"
$env:BUILD_TARGET = "development"
docker-compose up
```

**Production Environment (`ENV=prod`):**
```powershell
# Features:
# ✅ Code baked into image (no volumes)
# ✅ Optimized dependencies (no dev tools)
# ✅ Production resource limits
# ✅ Health checks enabled

# Build production
$env:ENV = "prod"
$env:BUILD_TARGET = "production"
docker-compose build --no-cache
docker-compose up -d
```

### Setup UV Locally (Optional - For Development)

**Install UV on Windows:**
```powershell
# Option 1: Using pip
pip install uv

# Option 2: Using pipx (recommended)
pipx install uv

# Verify installation
uv --version
# Expected: uv 0.1.x or higher
```

**Initialize UV in Project (if modifying dependencies):**
```powershell
# Navigate to orchestrator
cd orchestrator

# Initialize UV (creates pyproject.toml if needed)
uv init

# Install dependencies
uv sync

# Add new dependency
uv add fastapi

# Add dev dependency
uv add --dev pytest

# Generate lock file
uv lock
# Creates uv.lock - commit this to git!
```

### Environment Files Structure

**Create environment-specific configs:**

```powershell
# Development (.env.dev)
Copy-Item .env.dev.template .env.dev
# Edit with dev credentials: DEV_MARCOM_DB, DEV_WH, etc.

# Production (.env.prod)
Copy-Item .env.prod.template .env.prod
# Edit with prod credentials: PROD_MARCOM_DB, PROD_WH, etc.

# Staging (.env.staging) - optional
Copy-Item .env.staging.template .env.staging
```

**Example `.env.dev`:**
```ini
ENV=dev
BUILD_TARGET=development
SNOWFLAKE_DATABASE=DEV_MARCOM_DB
SNOWFLAKE_WAREHOUSE=DEV_WH
LOG_LEVEL=DEBUG
ENABLE_DEBUG_MODE=true
```

**Example `.env.prod`:**
```ini
ENV=prod
BUILD_TARGET=production
SNOWFLAKE_DATABASE=PROD_MARCOM_DB
SNOWFLAKE_WAREHOUSE=PROD_WH
LOG_LEVEL=INFO
ENABLE_DEBUG_MODE=false
```

### CI/CD Pipeline with UV

**GitHub Actions workflow** (`.github/workflows/ci-cd-uv.yml`):

```yaml
- name: Install UV
  uses: astral-sh/setup-uv@v1

- name: Install dependencies (10-100x faster!)
  run: uv sync

- name: Run tests
  run: uv run pytest
```

**Benefits in CI/CD:**
- ⚡ **Faster builds:** 3-5 min → 30-60 sec
- 🔒 **Guaranteed consistency:** Dev = Staging = Prod
- 💰 **Cost savings:** Reduced CI minutes
- 🚀 **Rapid deployments:** Quick rollbacks

### Docker Build Comparison

**Before (pip):**
```powershell
# Time: ~2-3 minutes
docker build -t dia-orchestrator .
# Installing snowflake-connector-python...
# [████████████████████░░░░░░] Long wait...
```

**After (UV):**
```powershell
# Time: ~15-30 seconds
docker build -t dia-orchestrator .
# Using UV: Dependencies cached and installed ⚡
# [████████████████████████████] Done!
```

### Best Practices for Multi-Environment

**1. Use Environment Variables:**
```yaml
# docker-compose.yml
services:
  orchestrator:
    build:
      target: ${BUILD_TARGET:-production}
    container_name: dia-orchestrator-${ENV:-dev}
    env_file:
      - .env.${ENV:-dev}
```

**2. Resource Management:**
```powershell
# Dev: Light resources
$env:ORCHESTRATOR_CPU_LIMIT = "1.0"
$env:ORCHESTRATOR_MEM_LIMIT = "1G"

# Prod: Production-grade
$env:ORCHESTRATOR_CPU_LIMIT = "4.0"
$env:ORCHESTRATOR_MEM_LIMIT = "4G"
```

**3. Volume Strategy:**
```powershell
# Dev: Mount source code for hot-reload
$env:ORCHESTRATOR_VOLUMES = "./orchestrator:/app"

# Prod: No volumes (code baked in)
$env:ORCHESTRATOR_VOLUMES = ""
```

### Quick Start Commands

```powershell
# 🔵 Development Mode
$env:ENV = "dev"; docker-compose up --build

# 🟢 Production Mode
$env:ENV = "prod"; docker-compose -f docker-compose.yml --profile prod up -d

# 🔄 Rebuild with no cache
docker-compose build --no-cache --parallel

# 📊 Check build performance
Measure-Command { docker-compose build }
```

### Troubleshooting UV + Docker

**Issue: UV not found in container**
```powershell
# Solution: Update Docker image tag
# Use: ghcr.io/astral-sh/uv:python3.11-bookworm-slim (latest)
```

**Issue: Dependencies not updating**
```powershell
# Solution: Regenerate lock file
cd orchestrator
uv lock --upgrade
docker-compose build --no-cache
```

**Issue: Different results in dev vs prod**
```powershell
# Solution: Ensure using same lock file
# Verify uv.lock is committed to git
git add orchestrator/uv.lock
git commit -m "Lock dependencies for reproducibility"
```

---

## Building & Running Services

### Option A: First-Time Setup (Recommended)

**Complete setup with build and start:**

```powershell
# Build images and start services (foreground with logs)
docker-compose up --build

# Expected output:
# ✅ Building orchestrator...
# ✅ Building web-app...
# ✅ Creating network...
# ✅ Creating dia-orchestrator...
# ✅ Creating dia-webapp...
# ✅ Services running...
```

**What happens:**
1. Docker builds the `orchestrator` image (installs Python packages)
2. Docker builds the `web-app` image (installs Streamlit)
3. Creates network for inter-service communication
4. Starts both containers
5. Mounts code directories as volumes (hot reload)
6. Exposes ports 8000 and 8501

**Wait for these messages:**
```
orchestrator_1  | INFO:     Uvicorn running on http://0.0.0.0:8000
web-app_1      | You can now view your Streamlit app in your browser.
web-app_1      | URL: http://0.0.0.0:8501
```

### Option B: Start in Background (Detached)

```powershell
# Start services in background
docker-compose up -d --build

# Check status
docker-compose ps

# View logs
docker-compose logs -f
```

### Option C: Start Without Rebuild (After First Build)

```powershell
# Start services (uses existing images)
docker-compose up

# Or in background
docker-compose up -d
```

---

## Testing & Verification

### Step 1: Check Services Are Running

```powershell
# Check container status
docker-compose ps

# Expected output:
#       Name                Command           State           Ports
# ---------------------------------------------------------------------
# dia-orchestrator   uvicorn main:app...   Up      0.0.0.0:8000->8000/tcp
# dia-webapp        streamlit run app.py   Up      0.0.0.0:8501->8501/tcp
```

### Step 2: Test Orchestrator (FastAPI Backend)

#### A. Health Check Endpoint
```powershell
# Test health endpoint
curl http://localhost:8000/api/v1/health

# Expected JSON response:
# {
#   "status": "healthy",
#   "services": {
#     "snowflake": "connected",
#     "orchestrator": "running"
#   },
#   "timestamp": "2026-02-22T..."
# }
```

#### B. Root Endpoint
```powershell
# Test root path
curl http://localhost:8000/

# Expected:
# {"message": "DIA v2.0 Orchestrator API", "version": "2.0.0"}
```

#### C. API Documentation (Interactive)
```powershell
# Open API docs in browser
start http://localhost:8000/docs

# Expected: FastAPI Swagger UI with all endpoints
```

#### D. Test Query Endpoint
```powershell
# Send test query
curl -X POST http://localhost:8000/api/v1/query `
  -H "Content-Type: application/json" `
  -d '{\"query\": \"What was the click rate last month?\"}'

# Or using Invoke-WebRequest
$body = @{
    query = "What was the click rate last month?"
} | ConvertTo-Json

Invoke-WebRequest -Uri http://localhost:8000/api/v1/query `
  -Method POST `
  -ContentType "application/json" `
  -Body $body
```

### Step 3: Test Web App (Streamlit Frontend)

```powershell
# Open web app in browser
start http://localhost:8501

# Expected: Streamlit DIA v2.0 interface loads
```

### Step 4: Execute Commands Inside Containers

#### Test Python Environment
```powershell
# Check Python version
docker exec dia-orchestrator python --version

# Check installed packages
docker exec dia-orchestrator pip list

# Check Snowflake connector
docker exec dia-orchestrator pip list | Select-String snowflake
```

#### Run Test Scripts
```powershell
# Test Snowflake connection
docker exec dia-orchestrator python ../tests/test_connection.py

# Test logging configuration
docker exec dia-orchestrator python test_logging.py

# Run pytest suite
docker exec dia-orchestrator pytest -v
```

#### List Files in Container
```powershell
# List orchestrator files
docker exec dia-orchestrator ls -la /app

# List web-app files
docker exec dia-webapp ls -la /app
```

### Step 5: View Logs

```powershell
# View all logs (real-time)
docker-compose logs -f

# View specific service logs
docker-compose logs -f orchestrator
docker-compose logs -f web-app

# View last 50 lines
docker-compose logs --tail=50 orchestrator

# View logs without following
docker-compose logs orchestrator
```

---

## Development Workflow

### Making Code Changes

**Your code is mounted as volumes - changes are automatically detected!**

1. **Edit Python files locally:**
   ```
   Edit: orchestrator/main.py
   Edit: web-app/app.py
   ```

2. **Save files - auto-reload triggers:**
   ```
   Orchestrator: Uvicorn auto-reloads (watch logs)
   Web App: Streamlit detects changes (click "Rerun" in browser)
   ```

3. **Watch logs for reload confirmation:**
   ```powershell
   docker-compose logs -f orchestrator
   # Expected: "Detected changes, reloading..."
   ```

### When Auto-Reload Doesn't Work

**Restart specific service:**
```powershell
docker-compose restart orchestrator
# Or
docker-compose restart web-app
```

### When Requirements Change

**If you modify `requirements.txt`, rebuild:**

```powershell
# Rebuild specific service
docker-compose up --build orchestrator

# Rebuild all services
docker-compose up --build

# Or stop, rebuild, start
docker-compose down
docker-compose up --build
```

### Managing Services

```powershell
# Start services
docker-compose up -d

# Stop services (keeps containers)
docker-compose stop

# Start stopped services
docker-compose start

# Restart services
docker-compose restart

# Stop and remove containers (keeps images)
docker-compose down

# Stop and remove everything including volumes
docker-compose down -v
```

### Debugging

```powershell
# View real-time logs
docker-compose logs -f

# Check resource usage
docker stats dia-orchestrator

# Inspect container details
docker inspect dia-orchestrator

# Check container processes
docker exec dia-orchestrator ps aux

# Check disk space in container
docker exec dia-orchestrator df -h
```

---

## Windows-Specific Commands

### 🐛 Common Error: "the input device is not a TTY"

This happens when using `-it` flags in certain Windows terminals (Git Bash, MinTTY, VSCode terminal).

**✅ Solution: Use commands without `-it` for non-interactive tasks**

### Running Scripts (No TTY Required)

```powershell
# Test logging
docker exec dia-orchestrator python test_logging.py

# Test Snowflake connection
docker exec dia-orchestrator python ../tests/test_connection.py

# Run pytest
docker exec dia-orchestrator pytest -v

# Execute Python code directly
docker exec dia-orchestrator python -c "print('Hello from container')"
```

### Interactive Shell Options

#### Option 1: PowerShell (Best for Windows) ✅ RECOMMENDED
```powershell
# Open PowerShell (not Git Bash)
docker exec -it dia-orchestrator /bin/bash

# Now you're inside the container
root@container:/app# ls
root@container:/app# python
root@container:/app# exit
```

#### Option 2: Git Bash with winpty
```bash
# In Git Bash, add winpty prefix:
winpty docker exec -it dia-orchestrator /bin/bash
winpty docker exec -it dia-orchestrator python
```

#### Option 3: Docker Desktop GUI (Easiest) ⭐
1. Open **Docker Desktop**
2. Click **Containers** in left sidebar
3. Find `dia-orchestrator`
4. Click the **CLI** button (terminal icon on the right)
5. Interactive shell opens automatically ✅

#### Option 4: VSCode Docker Extension
1. Install **Docker** extension in VSCode
2. Click Docker icon in left sidebar
3. Expand **Containers**
4. Right-click `dia-orchestrator`
5. Select **Attach Shell**

### Testing Checklist (Copy-Paste Ready)

```powershell
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

# 6. Run test script (if available)
docker exec dia-orchestrator python test_logging.py

# 7. Check logs
docker-compose logs --tail=20 orchestrator

# 8. Open API docs
start http://localhost:8000/docs

# 9. Open Web App
start http://localhost:8501
```

### Port Management

```powershell
# Check what's using port 8000
netstat -ano | findstr :8000

# Check what's using port 8501
netstat -ano | findstr :8501

# Kill process using port (if needed)
# First, get PID from netstat output above, then:
Stop-Process -Id <PID> -Force
```

---

## Troubleshooting

### Issue 1: Docker Desktop Not Running

**Error:** "Cannot connect to the Docker daemon"

**Solution:**
```powershell
# 1. Check if Docker is running
docker info

# 2. If not, start Docker Desktop
# - Open Docker Desktop from Start menu
# - Wait for "Docker Desktop is running"

# 3. Verify
docker ps
```

### Issue 2: Port Already in Use

**Error:** "port is already allocated"

**Solution:**
```powershell
# Option A: Stop the conflicting process
netstat -ano | findstr :8000
Stop-Process -Id <PID> -Force

# Option B: Change ports in docker-compose.yml
# Edit docker-compose.yml:
# ports:
#   - "8001:8000"  # Change left side only

# Then restart
docker-compose down
docker-compose up
```

### Issue 3: Code Changes Not Reflected

**Solution 1: Check auto-reload logs**
```powershell
docker-compose logs -f orchestrator
# Look for "Detected changes, reloading..."
```

**Solution 2: Restart service**
```powershell
docker-compose restart orchestrator
```

**Solution 3: Rebuild (if requirements changed)**
```powershell
docker-compose up --build orchestrator
```

### Issue 4: Container Exits Immediately

**Solution:**
```powershell
# Check exit status
docker-compose ps

# View error logs
docker-compose logs orchestrator

# Common causes:
# - Syntax error in Python code
# - Missing .env file
# - Invalid Snowflake credentials
# - Port conflict
```

### Issue 5: Cannot Access http://localhost:8000

**Solution:**
```powershell
# 1. Check container is running
docker-compose ps

# 2. Check container logs
docker-compose logs orchestrator

# 3. Check port mapping
docker port dia-orchestrator

# 4. Test from inside container
docker exec dia-orchestrator curl localhost:8000

# 5. Check Windows Firewall
# Add rule to allow ports 8000 and 8501
```

### Issue 6: Build Fails - Requirements Installation Error

**Solution:**
```powershell
# Clear build cache and rebuild
docker-compose build --no-cache orchestrator

# Or full reset
docker-compose down
docker system prune -a
docker-compose up --build
```

### Issue 7: Volume Mount Issues (Files Not Syncing)

**Solution:**
```powershell
# Check volume mounts
docker inspect dia-orchestrator | Select-String -Pattern "Mounts" -Context 0,20

# Verify file exists in container
docker exec dia-orchestrator ls -la /app/main.py

# If still issues, restart Docker Desktop
# Settings > Troubleshoot > Restart Docker Desktop
```

### Issue 8: WSL 2 Integration Issues

**Solution:**
```powershell
# Update WSL 2
wsl --update

# Restart WSL
wsl --shutdown

# Restart Docker Desktop

# Enable WSL integration
# Docker Desktop > Settings > Resources > WSL Integration
# Enable integration with required distros
```

### Issue 9: Out of Disk Space

**Solution:**
```powershell
# Check Docker disk usage
docker system df

# Clean up unused images
docker image prune -a

# Clean up unused volumes
docker volume prune

# Clean up everything (WARNING: removes all unused data)
docker system prune -a --volumes
```

### Issue 10: TTY Input Errors

**Error:** "the input device is not a TTY"

**Solution:**
```powershell
# Use PowerShell instead of Git Bash for interactive commands
# Or remove -it flags for non-interactive commands

# Instead of:
docker exec -it dia-orchestrator python test.py

# Use:
docker exec dia-orchestrator python test.py
```

---

## 🚀 Services Running

Your DIA v2.0 application runs with two services:

### 1. Orchestrator (FastAPI Backend)
- **URL:** http://localhost:8000
- **API Docs:** http://localhost:8000/docs
- **Health Check:** http://localhost:8000/api/v1/health
- **Purpose:** AI orchestration, Cortex integration, query routing

### 2. Web App (Streamlit Frontend)
- **URL:** http://localhost:8501
- **Purpose:** User interface for querying DIA v2.0

---

## 📝 Next Steps After Setup

Once your Docker environment is running successfully:

1. **✅ Verify Snowflake Connectivity**
   ```powershell
   docker exec dia-orchestrator python ../tests/test_connection.py
   ```

2. **✅ Run Data Layer Setup**
   ```powershell
   docker exec dia-orchestrator python ../scripts/setup_data_layer.py
   ```

3. **✅ Deploy Semantic Model**
   ```powershell
   docker exec dia-orchestrator python ../scripts/deploy_semantic_model.py
   ```

4. **✅ Test Query Flow**
   - Open http://localhost:8501
   - Enter query: "What was the click rate last month?"
   - Verify response

5. **✅ Implement Core Services**
   - See [DIA_V2_IMPLEMENTATION_PLAN.md](../DIA_V2_IMPLEMENTATION_PLAN.md)
   - Phase 2: Core Services Implementation

---

## 💡 Pro Tips

1. **Use PowerShell for Docker commands** - Best Windows compatibility
2. **Keep Docker Desktop running** - Required for all Docker operations
3. **Use Docker Desktop GUI** - Easiest for quick shell access and logs
4. **Check logs frequently** - `docker-compose logs -f` is your friend
5. **Hot reload works** - Python files auto-reload on save (volume mounted)
6. **Use `--build` when dependencies change** - Rebuilds containers with new packages
7. **Enable WSL 2** - Better performance than Hyper-V
8. **Allocate enough resources** - Docker Desktop > Settings > Resources
9. **Use .dockerignore** - Speeds up builds by excluding unnecessary files
10. **Monitor resource usage** - `docker stats` shows CPU/memory usage

---

## 📚 Related Documentation

- **[01_STEP_1.2_DATA_LAYER_SETUP.md](01_STEP_1.2_DATA_LAYER_SETUP.md)** - Data layer configuration
- **[00_TESTING_GUIDE.md](00_TESTING_GUIDE.md)** - Complete testing guide
- **[DIA_V2_IMPLEMENTATION_PLAN.md](../DIA_V2_IMPLEMENTATION_PLAN.md)** - Full implementation guide
- **[README.md](../README.md)** - Project overview

---

## 🎯 Current Implementation Status

✅ Docker Desktop installed and configured  
✅ Project setup with .env configuration  
✅ Docker containers built and running  
✅ Orchestrator API accessible (port 8000)  
✅ Web App accessible (port 8501)  
✅ Volume mounts working (hot reload)  
✅ Environment variables loaded  
✅ Health check endpoints responding  
⏳ Intent classification (Next: Phase 2)  
⏳ Cortex service integration (Next: Phase 2)  
⏳ Response enhancement (Next: Phase 2)  
⏳ Advanced visualizations (Next: Phase 4)  

---

**DIA v2.0** - Digital Intelligence Assistant  
Powered by Snowflake Cortex AI  
**Docker Deployment Ready** ✅

---

**Last Updated:** February 22, 2026  
**Version:** 2.0  
**Maintained By:** VML MAP Data Intelligence Team
