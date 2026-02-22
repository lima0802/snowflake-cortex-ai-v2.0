# 🚀 Semantic Model CI/CD - Quick Reference

## One-Line Commands

```powershell
# Validate semantic.yaml
python scripts/manage_semantic_model.py validate

# Show model info
python scripts/manage_semantic_model.py stats

# Deploy to Snowflake
python scripts/manage_semantic_model.py deploy

# Full CI/CD workflow (validate → deploy → verify)
python scripts/manage_semantic_model.py ci-deploy
```

## Common Workflows

### 1. Daily Development

```powershell
# Edit semantic.yaml in VSCode
code data-layer/semantic-models/semantic.yaml

# Validate changes
python scripts/manage_semantic_model.py validate

# Deploy when ready
python scripts/manage_semantic_model.py deploy
```

### 2. Add New Table

```powershell
# Option A: Programmatic
python scripts/manage_semantic_model.py add-table MY_NEW_TABLE \
    --database DEV_MARCOM_DB \
    --schema APP_DIRECTMARKETING \
    --table MY_TABLE \
    --description "My new table"

# Option B: Manual edit then validate
code data-layer/semantic-models/semantic.yaml
python scripts/manage_semantic_model.py validate
```

### 3. Git Workflow

```bash
# Make changes
code data-layer/semantic-models/semantic.yaml

# Validate locally
python scripts/manage_semantic_model.py validate

# Commit and push
git add data-layer/semantic-models/semantic.yaml
git commit -m "feat: update semantic model"
git push origin main

# GitHub Actions automatically:
# ✅ Validates
# ✅ Deploys to Snowflake
# ✅ Verifies deployment
```

## GitHub Actions Setup

### Required Secrets

Go to: `Settings` → `Secrets and variables` → `Actions`

```
SNOWFLAKE_ACCOUNT=fvqlqib-tj68700
SNOWFLAKE_USER=LIMA
SNOWFLAKE_PASSWORD=your_password
SNOWFLAKE_ROLE=SYSADMIN
SNOWFLAKE_WAREHOUSE=TEST
SNOWFLAKE_DATABASE=PLAYGROUND_LM
SNOWFLAKE_SCHEMA=CORTEX_ANALYTICS_ORCHESTRATOR
SNOWFLAKE_SEMANTIC_STAGE=SEMANTIC_MODELS
```

### Trigger Workflows

- **Automatic**: Push to `main` with semantic.yaml changes
- **Manual**: `Actions` → `Deploy Semantic Model` → `Run workflow`

## Troubleshooting

```powershell
# Connection test
python tests/test_connection.py

# List deployed versions
python scripts/manage_semantic_model.py list-versions

# Verify current deployment
python scripts/manage_semantic_model.py verify

# Check backups
ls data-layer/semantic-models/backups/
```

## File Structure

```
.github/workflows/
├── deploy-semantic-model.yml  # Semantic model deployment
└── test.yml                   # Test suite runner

scripts/
├── manage_semantic_model.py   # Main automation script
└── deploy_semantic_model.py   # Legacy simple deployer

data-layer/semantic-models/
├── semantic.yaml              # Main semantic model
└── backups/                   # Auto-created backups
    └── semantic_YYYYMMDD_HHMMSS.yaml
```

## Exit Codes

- `0` - Success
- `1` - Validation/deployment failed
- `130` - User cancelled (Ctrl+C)

Perfect for scripting and CI/CD! 🎯

---

**Full documentation:** [guides/11_CI_CD_SETUP.md](11_CI_CD_SETUP.md)
