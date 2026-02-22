# CI/CD Setup Guide - DIA v2.0

## 📋 Overview

Automated deployment pipeline for Snowflake semantic models using GitHub Actions and Python scripts.

**What's Automated:**
- ✅ Semantic model validation on every PR
- ✅ Automatic deployment to Snowflake on merge to main
- ✅ Python test suite execution
- ✅ Code linting and formatting checks

---

## 🚀 Quick Start

### 1. Configure GitHub Secrets

Go to your repository: `Settings` → `Secrets and variables` → `Actions` → `New repository secret`

Add these secrets:

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

### 2. Test Locally

```powershell
# Validate semantic model
python scripts/manage_semantic_model.py validate

# Show model statistics
python scripts/manage_semantic_model.py stats

# Deploy to Snowflake
python scripts/manage_semantic_model.py deploy

# CI/CD workflow (validate + deploy + verify)
python scripts/manage_semantic_model.py ci-deploy
```

### 3. Push Changes

```bash
# Make changes to semantic.yaml
git add data-layer/semantic-models/semantic.yaml
git commit -m "Update semantic model: added new table"
git push origin main
```

**GitHub Actions will automatically:**
1. Validate the YAML syntax
2. Run model statistics
3. Deploy to Snowflake
4. Verify deployment

---

## 📝 Python Script Usage

### `manage_semantic_model.py` Commands

#### Validation

```powershell
# Validate YAML syntax and structure
python scripts/manage_semantic_model.py validate
```

#### Deployment

```powershell
# Deploy to Snowflake
python scripts/manage_semantic_model.py deploy

# Verify deployed model
python scripts/manage_semantic_model.py verify

# Full CI/CD workflow (validate → deploy → verify)
python scripts/manage_semantic_model.py ci-deploy
```

#### Model Information

```powershell
# Show model statistics
python scripts/manage_semantic_model.py stats

# List all tables
python scripts/manage_semantic_model.py list-tables

# List deployed versions
python scripts/manage_semantic_model.py list-versions
```

#### Model Updates

```powershell
# Update model description
python scripts/manage_semantic_model.py update-description "New description text"

# Add a new table
python scripts/manage_semantic_model.py add-table MY_NEW_TABLE \
    --database DEV_MARCOM_DB \
    --schema APP_DIRECTMARKETING \
    --table MY_TABLE \
    --description "Description of the table"

# Update table description
python scripts/manage_semantic_model.py update-table-description MY_TABLE "New description"
```

---

## 🔄 CI/CD Workflows

### 1. Deploy Semantic Model Workflow

**File:** `.github/workflows/deploy-semantic-model.yml`

**Triggers:**
- Push to `main` branch (changes to `semantic.yaml` or scripts)
- Pull requests (validation only, no deployment)
- Manual trigger via GitHub Actions UI

**Jobs:**

1. **validate-semantic-model**
   - Validates YAML syntax
   - Shows model statistics
   - Lists all tables
   - Runs on every PR

2. **deploy-to-snowflake**
   - Only runs on push to main (not PRs)
   - Deploys validated model to Snowflake
   - Verifies deployment success
   - Uses GitHub secrets for credentials

### 2. Test Workflow

**File:** `.github/workflows/test.yml`

**Triggers:**
- Push to `main` or `develop`
- Pull requests
- Manual trigger

**Jobs:**

1. **test-orchestrator**
   - Runs pytest suite (33 tests)
   - Tests FastAPI endpoints
   - Checks API functionality

2. **lint-code**
   - Runs flake8 for syntax errors
   - Checks PEP 8 compliance
   - Runs black formatter check

---

## 📊 Example Workflow

### Scenario: Update Semantic Model

1. **Local Development**
   ```powershell
   # Edit semantic.yaml
   code data-layer/semantic-models/semantic.yaml
   
   # Validate changes
   python scripts/manage_semantic_model.py validate
   
   # Test deployment locally (optional)
   python scripts/manage_semantic_model.py deploy
   ```

2. **Create Pull Request**
   ```bash
   git checkout -b update-semantic-model
   git add data-layer/semantic-models/semantic.yaml
   git commit -m "feat: add new table to semantic model"
   git push origin update-semantic-model
   # Create PR on GitHub
   ```

3. **Automated Validation**
   - GitHub Actions validates YAML
   - Shows model stats in PR
   - No deployment happens yet

4. **Merge to Main**
   ```bash
   # After PR approval, merge to main
   ```

5. **Automated Deployment**
   - GitHub Actions deploys to Snowflake
   - Verifies deployment
   - Model available in Snowsight

---

## 🛠️ Advanced Usage

### Programmatic Model Updates

```python
from scripts.manage_semantic_model import SemanticModelManager

# Load model
manager = SemanticModelManager()
manager.load()

# Update description
manager.update_description("New description for the model")

# Add a table
manager.add_table(
    name="VW_NEW_TABLE",
    database="DEV_MARCOM_DB",
    schema="APP_DIRECTMARKETING",
    table="NEW_TABLE",
    description="New table for analysis"
)

# Validate
if manager.validate():
    manager.save()  # Auto-creates backup
```

### Custom Deployment Script

```python
from scripts.manage_semantic_model import SnowflakeDeployer

deployer = SnowflakeDeployer()

# Deploy
success = deployer.deploy("data-layer/semantic-models/semantic.yaml")

# Verify
if success:
    deployer.verify()

# List versions
versions = deployer.list_versions()
for v in versions:
    print(f"{v['name']} - {v['modified']}")
```

---

## 🔒 Security Best Practices

### GitHub Secrets

✅ **DO:**
- Store Snowflake credentials in GitHub Secrets
- Use service accounts (not personal accounts)
- Rotate credentials regularly
- Use least-privilege roles

❌ **DON'T:**
- Commit credentials to git
- Share secrets across repos unnecessarily
- Use admin accounts for automation

### Access Control

```sql
-- Create dedicated CI/CD service account
CREATE USER cicd_user PASSWORD='secure_password';

-- Grant minimal permissions
GRANT ROLE SYSADMIN TO USER cicd_user;
GRANT USAGE ON WAREHOUSE TEST TO ROLE SYSADMIN;
GRANT USAGE, CREATE STAGE ON SCHEMA CORTEX_ANALYTICS_ORCHESTRATOR TO ROLE SYSADMIN;
```

---

## 📈 Monitoring & Debugging

### View GitHub Actions Logs

1. Go to repository → `Actions` tab
2. Click on workflow run
3. Expand job steps to see detailed logs

### Local Debugging

```powershell
# Enable verbose output
$env:PYTHONUNBUFFERED="1"
python scripts/manage_semantic_model.py ci-deploy

# Check Snowflake stage
python -c "
from scripts.manage_semantic_model import SnowflakeDeployer
deployer = SnowflakeDeployer()
versions = deployer.list_versions()
for v in versions: print(v)
"
```

### Common Issues

#### Issue 1: Validation Fails

**Error:** `YAML Syntax Error`

**Solution:**
```powershell
# Check YAML syntax
python -c "import yaml; yaml.safe_load(open('data-layer/semantic-models/semantic.yaml'))"

# Fix formatting
python scripts/manage_semantic_model.py validate
```

#### Issue 2: Deployment Fails

**Error:** `Snowflake Connection Error`

**Solution:**
```powershell
# Test connection
python tests/test_connection.py

# Check .env file
cat .env

# Verify secrets in GitHub
# Go to Settings → Secrets → Check all secrets exist
```

#### Issue 3: Stage Not Found

**Error:** `Object 'SEMANTIC_MODELS' does not exist`

**Solution:**
```sql
-- Create stage manually
USE DATABASE PLAYGROUND_LM;
USE SCHEMA CORTEX_ANALYTICS_ORCHESTRATOR;
CREATE STAGE IF NOT EXISTS SEMANTIC_MODELS;
ALTER STAGE SEMANTIC_MODELS SET DIRECTORY = (ENABLE = TRUE);
```

---

## 📚 Additional Resources

### GitHub Actions Documentation
- [GitHub Actions Quickstart](https://docs.github.com/en/actions/quickstart)
- [Using secrets in GitHub Actions](https://docs.github.com/en/actions/security-guides/encrypted-secrets)
- [Workflow syntax](https://docs.github.com/en/actions/using-workflows/workflow-syntax-for-github-actions)

### Snowflake Documentation
- [Snowpark Python API](https://docs.snowflake.com/en/developer-guide/snowpark/python/index)
- [File staging](https://docs.snowflake.com/en/user-guide/data-load-local-file-system-stage)
- [Cortex Analyst semantic models](https://docs.snowflake.com/en/user-guide/snowflake-cortex/cortex-analyst/semantic-model-spec)

### Project Documentation
- [DIA_V2_IMPLEMENTATION_PLAN.md](../DIA_V2_IMPLEMENTATION_PLAN.md) - Full implementation guide
- [guides/00_TESTING_GUIDE.md](00_TESTING_GUIDE.md) - Testing documentation
- [guides/10_STEP_6.1_DEPLOYMENT.md](10_STEP_6.1_DEPLOYMENT.md) - Deployment guide

---

## 🎯 Next Steps

After setting up CI/CD:

1. **Enable Branch Protection**
   - Require PR reviews before merge
   - Require status checks to pass
   - Enable "deploy-semantic-model" workflow as required check

2. **Add More Workflows**
   - Docker image builds
   - Integration tests
   - Performance benchmarks

3. **Monitor Deployments**
   - Set up Slack/Teams notifications
   - Track deployment frequency
   - Monitor semantic model usage in Snowflake

---

## 📝 Change Log

- **2026-02-22**: Initial CI/CD setup with GitHub Actions
- Created `manage_semantic_model.py` automation script
- Added validation, deployment, and verification workflows
- Configured automated testing pipeline

---

**Questions?** Check [DIA_V2_IMPLEMENTATION_PLAN.md](../DIA_V2_IMPLEMENTATION_PLAN.md) or open an issue.
