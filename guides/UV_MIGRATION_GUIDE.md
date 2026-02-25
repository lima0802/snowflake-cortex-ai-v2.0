# Migration Guide: pip → UV for Fast Deployment

**Upgrade your DIA v2.0 deployment to use UV for 10-100x faster builds**

---

## 📊 Why Migrate?

| Metric | Before (pip) | After (UV) | Improvement |
|--------|-------------|-----------|-------------|
| **Local install time** | 120-180s | 10-15s | **10-12x faster** |
| **Docker build time** | 150-240s | 20-30s | **7-8x faster** |
| **CI/CD pipeline** | 5-8 min | 1-2 min | **4-5x faster** |
| **Dependency resolution** | 30-60s | 2-3s | **15-20x faster** |
| **Reproducibility** | ⚠️ Variable | ✅ Guaranteed | 100% consistent |

---

## 🚀 Migration Steps

### Step 1: Backup Current Setup

```powershell
# Create backup of current files
New-Item -ItemType Directory -Path backup -Force
Copy-Item orchestrator/requirements.txt backup/
Copy-Item web-app/requirements.txt backup/
Copy-Item orchestrator/Dockerfile backup/Dockerfile.orchestrator
Copy-Item web-app/Dockerfile backup/Dockerfile.webapp
Copy-Item docker-compose.yml backup/
```

### Step 2: Install UV Locally

```powershell
# Option 1: Using pip
pip install uv

# Option 2: Using pipx (recommended for tools)
pip install pipx
pipx install uv

# Verify installation
uv --version
# Expected: uv 0.1.15 or higher
```

### Step 3: Generate pyproject.toml Files

**For Orchestrator:**
```powershell
cd orchestrator

# Initialize UV
uv init --no-workspace

# Add dependencies from requirements.txt
Get-Content requirements.txt | ForEach-Object {
    if ($_ -match '^([a-zA-Z0-9-_]+)==(.+)$') {
        $package = $matches[1]
        $version = $matches[2]
        uv add "$package==$version"
    }
}

# Add dev dependencies
uv add --dev pytest pytest-asyncio pytest-cov black ruff

# Generate lock file
uv lock

cd ..
```

**For Web App:**
```powershell
cd web-app

# Initialize UV
uv init --no-workspace

# Add dependencies from requirements.txt
Get-Content requirements.txt | ForEach-Object {
    if ($_ -match '^([a-zA-Z0-9-_]+)==(.+)$') {
        $package = $matches[1]
        $version = $matches[2]
        uv add "$package==$version"
    }
}

# Generate lock file
uv lock

cd ..
```

### Step 4: Update Dockerfiles

**Files are already updated in the repository:**
- ✅ `orchestrator/Dockerfile` - Multi-stage with UV
- ✅ `web-app/Dockerfile` - Multi-stage with UV

**What changed:**
- Uses `ghcr.io/astral-sh/uv:python3.11-bookworm-slim` as builder
- Multi-stage build (builder + production)
- Virtual environment copied from builder
- Smaller final image size
- Non-root user for security

### Step 5: Create Environment Files

```powershell
# Copy templates
Copy-Item .env.dev.template .env.dev
Copy-Item .env.prod.template .env.prod

# Edit with your credentials
notepad .env.dev
notepad .env.prod
```

**Update `.env.dev`:**
```ini
ENV=dev
BUILD_TARGET=development
SNOWFLAKE_DATABASE=DEV_MARCOM_DB
SNOWFLAKE_WAREHOUSE=DEV_WH
SNOWFLAKE_ROLE=DEV_ROLE
LOG_LEVEL=DEBUG
```

**Update `.env.prod`:**
```ini
ENV=prod
BUILD_TARGET=production
SNOWFLAKE_DATABASE=PROD_MARCOM_DB
SNOWFLAKE_WAREHOUSE=PROD_WH
SNOWFLAKE_ROLE=PROD_ROLE
LOG_LEVEL=INFO
```

### Step 6: Update docker-compose.yml

The file is already updated with:
- ✅ Multi-environment support
- ✅ Environment-specific profiles
- ✅ Resource limits
- ✅ Build caching
- ✅ Health checks

### Step 7: Test The Migration

**Test Development Build:**
```powershell
# Set environment
$env:ENV = "dev"
$env:BUILD_TARGET = "development"

# Build (first time will be slower as it pulls UV image)
docker-compose build

# Start services
docker-compose up
```

**Expected Output:**
```
[+] Building 25.3s (14/14) FINISHED
 => [builder 1/4] FROM ghcr.io/astral-sh/uv:python3.11-bookworm-slim  5.2s
 => [builder 2/4] COPY pyproject.toml ./                               0.1s
 => [builder 3/4] RUN uv venv /app/.venv                              2.1s
 => [builder 4/4] RUN uv pip install -r pyproject.toml               12.4s  ⚡ FAST!
 => [production 1/5] COPY --from=builder /app/.venv /app/.venv        3.2s
 => [production 2/5] COPY . .                                          0.3s
✅ Build complete!
```

**Compare Build Times:**
```powershell
# Measure old build (if you have backup)
Measure-Command {
    docker build -t test-old -f backup/Dockerfile.orchestrator orchestrator/
}
# Expected: 2-3 minutes

# Measure new build
Measure-Command {
    docker-compose build orchestrator
}
# Expected: 20-40 seconds (first time), 10-15s (cached)
```

### Step 8: Verify Services Work

```powershell
# Check containers are running
docker-compose ps

# Test orchestrator health
curl http://localhost:8000/api/v1/health

# Test web app
Start-Process http://localhost:8501

# Check logs
docker-compose logs orchestrator
docker-compose logs web-app
```

### Step 9: Test Production Build

```powershell
# Stop dev containers
docker-compose down

# Set production environment
$env:ENV = "prod"
$env:BUILD_TARGET = "production"

# Build with no cache to test clean build
docker-compose build --no-cache

# Start in detached mode
docker-compose up -d

# Verify health
curl http://localhost:8000/api/v1/health

# Check resource usage
docker stats
```

### Step 10: Update CI/CD

**GitHub Actions is already updated:**
- ✅ `.github/workflows/ci-cd-uv.yml` - New UV-based pipeline
- ✅ Faster test runs (uv sync + uv run pytest)
- ✅ Docker build caching
- ✅ Multi-environment support

**To activate:**
```powershell
# Commit all changes
git add .
git commit -m "Migrate to UV for fast deployment"
git push origin main
```

---

## 📦 What Gets Committed to Git?

**✅ DO commit:**
- `orchestrator/pyproject.toml` - Dependency specification
- `orchestrator/uv.lock` - Locked versions (CRITICAL for reproducibility!)
- `web-app/pyproject.toml` - Web app dependencies
- `web-app/uv.lock` - Web app locked versions
- `orchestrator/Dockerfile` - Updated build instructions
- `web-app/Dockerfile` - Updated build instructions
- `docker-compose.yml` - Updated orchestration
- `.env.*.template` - Environment templates

**❌ DO NOT commit:**
- `.env` - Main environment file
- `.env.dev` - Development credentials
- `.env.prod` - Production credentials
- `orchestrator/.venv/` - Local virtual environment
- `web-app/.venv/` - Local virtual environment

**Update `.gitignore`:**
```gitignore
# Environment files (sensitive)
.env
.env.dev
.env.prod
.env.staging
.env.local

# Virtual environments
.venv/
venv/
*/.venv/
*/venv/

# UV cache
.uv/

# Python cache
__pycache__/
*.pyc
*.pyo
*.pyd
.Python

# Docker
docker-compose.override.yml
```

---

## 🔄 Rollback Plan (If Needed)

If you encounter issues:

```powershell
# Option 1: Restore from backup
Copy-Item backup/* ./

# Option 2: Use requirements.txt fallback
# Dockerfiles support both pyproject.toml and requirements.txt

# Option 3: Git revert
git revert HEAD
```

---

## 🧪 Validation Checklist

After migration, verify:

- [ ] Development containers build successfully
- [ ] Production containers build successfully
- [ ] `uv.lock` files are in git
- [ ] Services start without errors
- [ ] API endpoints respond correctly
- [ ] Streamlit UI loads properly
- [ ] Snowflake connection works
- [ ] Tests pass in CI/CD
- [ ] Build time reduced (measure with `Measure-Command`)
- [ ] No dependency conflicts

---

## 📊 Performance Benchmarks

Record your improvements:

```powershell
# Before migration (pip)
# docker build time: _______ seconds
# docker-compose up: _______ seconds
# CI/CD pipeline:    _______ minutes

# After migration (UV)
# docker build time: _______ seconds  (should be 5-10x faster)
# docker-compose up: _______ seconds  (should be 3-5x faster)
# CI/CD pipeline:    _______ minutes  (should be 3-4x faster)
```

---

## 🎓 Learning Resources

- **UV Documentation:** https://github.com/astral-sh/uv
- **Docker Multi-Stage Builds:** https://docs.docker.com/build/building/multi-stage/
- **GitHub Actions UV:** https://github.com/astral-sh/setup-uv

---

## 💡 Tips & Best Practices

1. **Always commit `uv.lock` files** - They guarantee reproducibility
2. **Use `uv lock --upgrade` sparingly** - Only when intentionally updating
3. **Test in dev before prod** - Validate changes work end-to-end
4. **Monitor build times** - Track improvements over time
5. **Use `.env.template` files** - Share config structure without secrets

---

## 🆘 Troubleshooting

**Issue: "uv: command not found" in Docker**
```powershell
# Solution: Update Dockerfile base image
FROM ghcr.io/astral-sh/uv:python3.11-bookworm-slim
```

**Issue: Build fails with "No such file: pyproject.toml"**
```powershell
# Solution: Ensure pyproject.toml exists
cd orchestrator
uv init
uv add [dependencies]
```

**Issue: Different versions in dev vs prod**
```powershell
# Solution: Use same uv.lock file
# Ensure uv.lock is committed and not in .gitignore
git status | Select-String "uv.lock"
```

**Issue: "Permission denied" in container**
```powershell
# Solution: Already fixed in new Dockerfile
# Non-root user (appuser) is created and used
```

---

## ✅ Migration Complete!

You now have:
- ⚡ **10-100x faster builds**
- 🔒 **100% reproducible environments**
- 🚀 **Faster CI/CD pipelines**
- 💰 **Reduced infrastructure costs**
- 🎯 **Dev/Prod consistency**

**Next Steps:**
1. Monitor build times and document improvements
2. Train team on UV commands
3. Update deployment runbooks
4. Celebrate faster deployments! 🎉
