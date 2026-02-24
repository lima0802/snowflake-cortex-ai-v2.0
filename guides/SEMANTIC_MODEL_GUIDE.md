# 🎯 Semantic Model - Complete Guide

**Comprehensive guide for managing SFMC Email Performance semantic model using modular structure**

---

## 📋 Table of Contents

1. [Quick Start](#-quick-start)
2. [Understanding the Modular Structure](#-understanding-the-modular-structure)
3. [Split vs Merge - When to Use](#-split-vs-merge---when-to-use)
4. [Daily Development Workflow](#-daily-development-workflow)
5. [Best Practices](#-best-practices)
6. [Common Tasks](#-common-tasks)
7. [CI/CD Automation](#-cicd-automation)
8. [Troubleshooting](#-troubleshooting)

---

## 🚀 Quick Start

### One-Line Commands

```powershell
# Merge modular files for deployment
python scripts/merge_semantic_models.py

# Deploy merged model to Snowflake
python scripts/deploy_semantic_model.py

# Split existing semantic.yaml into modular components (one-time)
python scripts/split_semantic_model.py

# Validate YAML syntax
python -c "import yaml; yaml.safe_load(open('semantic_merged.yaml'))"
```

### 30-Second Workflow

```powershell
# 1. Edit modular files
code orchestrator/semantic_models/schema.yaml       # Add tables/columns
code orchestrator/semantic_models/instructions.yaml # Add business rules
code orchestrator/semantic_models/verified_queries.yaml # Add examples

# 2. Merge and deploy
python scripts/merge_semantic_models.py
python scripts/deploy_semantic_model.py
```

---

## 📁 Understanding the Modular Structure

### Why Modular?

**Before (Monolithic):**
- ❌ 5,034 lines in one file (`semantic.yaml`)
- ❌ Hard to find specific sections
- ❌ Merge conflicts with multiple editors
- ❌ Large Git diffs

**After (Modular):**
- ✅ 3 focused files (schema, instructions, verified queries)
- ✅ Easy to navigate and edit
- ✅ Team can edit different components simultaneously
- ✅ Clear Git diffs showing what changed
- ✅ Automated merge for deployment

### File Structure

```
orchestrator/semantic_models/
├── README.md                    # This documentation
├── __init__.py                  # Module initialization (v2.0.0)
├── schema.yaml                  # 📊 Tables, dimensions, measures
├── instructions.yaml            # 📋 Business rules & guidelines
└── verified_queries.yaml        # 💡 Training examples (Q&A pairs)

scripts/
├── split_semantic_model.py      # Split monolithic → modular
└── merge_semantic_models.py     # Merge modular → deployment

data-layer/semantic-models/
└── semantic.yaml                # Original monolithic file (backup)
```

---

## ⚖️ Split vs Merge - When to Use

### Split: Development & Editing

**Use split when:**
- ✅ Starting from existing monolithic `semantic.yaml`
- ✅ Breaking down large file into components (ONE-TIME operation)
- ✅ Making the model easier to maintain

**Command:**
```powershell
python scripts/split_semantic_model.py
```

**What it does:**
- Reads `data-layer/semantic-models/semantic.yaml` (5,034 lines)
- Extracts schema → `orchestrator/semantic_models/schema.yaml`
- Extracts instructions → `orchestrator/semantic_models/instructions.yaml`
- Extracts verified queries → `orchestrator/semantic_models/verified_queries.yaml`
- Creates automatic backup
- Generates README documentation

**Output:**
```
✅ Split complete!
   Tables: 6
   Instructions: 14
   Verified Queries: 63
```

### Merge: Deployment

**Use merge when:**
- ✅ Ready to deploy to Snowflake
- ✅ After editing any modular file
- ✅ Before running `deploy_semantic_model.py`
- ✅ In CI/CD pipeline

**Command:**
```powershell
python scripts/merge_semantic_models.py
```

**What it does:**
- Reads 3 modular files (schema, instructions, verified_queries)
- Validates structure
- Combines into single YAML
- Adds metadata (merge timestamp, version)
- Outputs → `semantic_merged.yaml` (169.3 KB)

**Output:**
```
✅ MERGE COMPLETE!
   Name: SFMC_EMAIL_PERFORMANCE_DEV
   Tables: 6
   Instructions: 14
   Verified Queries: 63
   File Size: 173,334 bytes (169.3 KB)
```

### The Complete Workflow

```
┌─────────────────────────────────────────────────────────────┐
│                    DEVELOPMENT (Split)                       │
│                                                               │
│  semantic.yaml (monolithic)                                   │
│         │                                                     │
│         │ python scripts/split_semantic_model.py             │
│         ▼                                                     │
│  ┌──────────────┬────────────────┬─────────────────┐        │
│  │ schema.yaml  │  instructions  │ verified_queries │        │
│  │              │     .yaml      │     .yaml        │        │
│  └──────────────┴────────────────┴─────────────────┘        │
│         │              │                  │                  │
│         └──────────────┼──────────────────┘                  │
│                        │ EDIT SEPARATELY                      │
└────────────────────────┼──────────────────────────────────────┘
                         │
                         │ python scripts/merge_semantic_models.py
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                   DEPLOYMENT (Merge)                         │
│                                                               │
│  semantic_merged.yaml (169.3 KB)                             │
│         │                                                     │
│         │ python scripts/deploy_semantic_model.py            │
│         ▼                                                     │
│  Snowflake @SEMANTIC_MODELS stage                            │
│         │                                                     │
│         │ Cortex Analyst reads model                         │
│         ▼                                                     │
│  🤖 AI Agent answers business questions                      │
└─────────────────────────────────────────────────────────────┘
```

---

## 🔄 Daily Development Workflow

### Scenario 1: Add New Table

```powershell
# 1. Edit schema.yaml
code orchestrator/semantic_models/schema.yaml

# Add your table:
# - name: MY_NEW_TABLE
#   base_table: PLAYGROUND_LM.CORTEX_ANALYTICS_ORCHESTRATOR.MY_TABLE
#   description: "My new table for XYZ analysis"
#   dimensions: ...
#   measures: ...

# 2. Merge and deploy
python scripts/merge_semantic_models.py
python scripts/deploy_semantic_model.py

# 3. Verify
# Ask Cortex Analyst: "What tables are available?"
```

### Scenario 2: Add Business Rules

```powershell
# 1. Edit instructions.yaml
code orchestrator/semantic_models/instructions.yaml

# Add new instruction rule:
# - name: "New Rule Category"
#   rules:
#     - "When user asks X, always do Y"
#     - "Filter out invalid data by Z condition"

# 2. Merge and deploy
python scripts/merge_semantic_models.py
python scripts/deploy_semantic_model.py

# 3. Test with query that uses new rule
```

### Scenario 3: Add Training Examples

```powershell
# 1. Edit verified_queries.yaml
code orchestrator/semantic_models/verified_queries.yaml

# Add Q&A pair:
# - question: "What is the average open rate in Germany?"
#   sql: "SELECT AVG(OPEN_RATE) * 100 AS open_rate_pct 
#         FROM VW_SFMC_EMAIL_PERFORMANCE 
#         WHERE MARKET = 'Germany'"

# 2. Merge and deploy
python scripts/merge_semantic_models.py
python scripts/deploy_semantic_model.py

# 3. Ask Cortex Analyst your new question
```

### Scenario 4: Git Workflow (Team Collaboration)

```bash
# 1. Create feature branch
git checkout -b feature/add-bounce-analysis

# 2. Edit modular files
code orchestrator/semantic_models/schema.yaml
# ... make changes ...

# 3. Test locally
python scripts/merge_semantic_models.py
python scripts/deploy_semantic_model.py

# 4. Commit only the modular files
git add orchestrator/semantic_models/schema.yaml
git add orchestrator/semantic_models/instructions.yaml
git commit -m "feat: add bounce rate analysis dimensions"

# 5. Push and create PR
git push origin feature/add-bounce-analysis

# 6. GitHub Actions will:
#    ✅ Validate structure
#    ✅ Merge files
#    ✅ Deploy to staging
#    ✅ Run tests

# 7. After PR approved and merged:
#    ✅ Auto-deploy to production
```

---

## ✨ Best Practices

### 1. **Edit Modular Files, Not Merged**

```powershell
# ✅ CORRECT: Edit modular files
code orchestrator/semantic_models/schema.yaml
code orchestrator/semantic_models/instructions.yaml
code orchestrator/semantic_models/verified_queries.yaml

# ❌ WRONG: Don't edit merged output
code semantic_merged.yaml  # This gets overwritten!
```

### 2. **Always Merge Before Deploy**

```powershell
# ✅ CORRECT: Merge → Deploy
python scripts/merge_semantic_models.py
python scripts/deploy_semantic_model.py

# ❌ WRONG: Deploy without merge
python scripts/deploy_semantic_model.py  # Deploys old version!
```

### 3. **Validate YAML Syntax**

```powershell
# After editing any YAML file:
python -c "import yaml; yaml.safe_load(open('orchestrator/semantic_models/schema.yaml'))"
python -c "import yaml; yaml.safe_load(open('orchestrator/semantic_models/instructions.yaml'))"
python -c "import yaml; yaml.safe_load(open('orchestrator/semantic_models/verified_queries.yaml'))"
```

### 4. **Use Descriptive Commit Messages**

```bash
# ✅ GOOD
git commit -m "feat: add BOUNCE_RATE dimension to email performance table"
git commit -m "fix: correct open rate calculation in instructions"
git commit -m "docs: add examples for market comparison queries"

# ❌ BAD
git commit -m "update"
git commit -m "changes"
git commit -m "fix bug"
```

### 5. **Test After Each Change**

```powershell
# After adding new table/dimension:
# 1. Merge
python scripts/merge_semantic_models.py

# 2. Deploy
python scripts/deploy_semantic_model.py

# 3. Test with Cortex Analyst
# Ask: "What tables do we have?"
# Ask: "Show me data from MY_NEW_TABLE"
```

### 6. **Keep Instructions Clear & Specific**

```yaml
# ✅ GOOD - Clear and actionable
- name: "Date Range Handling"
  rules:
    - "'Last month' = Previous complete calendar month (e.g., if today is Feb 15, last month = Jan 1 to Jan 31)"
    - "Always use SEND_DATE for time-based filtering"

# ❌ BAD - Vague
- name: "Dates"
  rules:
    - "Handle dates properly"
```

### 7. **Add Context to Verified Queries**

```yaml
# ✅ GOOD - Realistic business question
- question: "Which campaigns in Germany had open rates above 30% last month?"
  sql: |
    SELECT 
      CAMPAIGN_NAME,
      OPEN_RATE * 100 AS open_rate_pct,
      SENT_COUNT
    FROM VW_SFMC_EMAIL_PERFORMANCE
    WHERE MARKET = 'Germany'
      AND SEND_DATE >= DATE_TRUNC('month', ADD_MONTHS(CURRENT_DATE(), -1))
      AND SEND_DATE < DATE_TRUNC('month', CURRENT_DATE())
      AND OPEN_RATE > 0.30
    ORDER BY OPEN_RATE DESC
    LIMIT 20

# ❌ BAD - Too simple
- question: "Show me data"
  sql: "SELECT * FROM VW_SFMC_EMAIL_PERFORMANCE"
```

---

## 🛠️ Common Tasks

### Add New Dimension to Existing Table

```powershell
# 1. Edit schema.yaml
code orchestrator/semantic_models/schema.yaml
```

```yaml
# Find your table and add dimension:
tables:
  - name: VW_SFMC_EMAIL_PERFORMANCE
    dimensions:
      # ... existing dimensions ...
      - name: CAMPAIGN_OBJECTIVE
        expr: CAMPAIGN_OBJECTIVE
        data_type: VARCHAR
        unique_name: EMAIL_CAMPAIGN_OBJECTIVE
        description: "Campaign objective: awareness, consideration, conversion, retention"
        sample_values:
          - "awareness"
          - "consideration"
          - "conversion"
```

```powershell
# 2. Merge and deploy
python scripts/merge_semantic_models.py
python scripts/deploy_semantic_model.py
```

### Add New Measure (Metric)

```yaml
# In schema.yaml, add to measures section:
measures:
  - name: CONVERSION_RATE
    expr: CONVERSION_COUNT / NULLIF(CLICK_COUNT, 0)
    data_type: FLOAT
    default_aggregation: avg
    description: "Conversion rate = Conversions / Clicks"
```

### Add Time Dimension

```yaml
# In schema.yaml:
time_dimensions:
  - name: PURCHASE_DATE
    expr: PURCHASE_DATE
    data_type: DATE
    unique_name: EMAIL_PURCHASE_DATE
    description: "Date when customer made purchase after clicking email"
```

### Update Business Rule

```yaml
# In instructions.yaml:
- name: "Rate Calculations and Formatting"
  rules:
    - "All rate metrics are stored as decimals (0.0 to 1.0)"
    - "When displaying rates, multiply by 100 and show as percentages"
    - "NEW: Round percentages to 1 decimal place for clarity"
    - "NEW: Highlight rates above benchmark in green, below in red"
```

### Add Multiple Related Queries

```yaml
# In verified_queries.yaml:
# Group related queries together:

# --- Campaign Performance Analysis ---
- question: "What are the top 10 campaigns by open rate this month?"
  sql: |
    SELECT ...

- question: "Which campaigns had the worst bounce rates this month?"
  sql: |
    SELECT ...

- question: "Compare campaign performance across all markets this month"
  sql: |
    SELECT ...
```

---

## 🤖 CI/CD Automation

### Quick Reference Commands

```powershell
# Modular workflow (recommended)
python scripts/merge_semantic_models.py     # Merge components
python scripts/deploy_semantic_model.py      # Deploy to Snowflake

# Legacy monolithic workflow
python scripts/manage_semantic_model.py validate   # Validate YAML
python scripts/manage_semantic_model.py stats      # Show statistics
python scripts/manage_semantic_model.py deploy     # Deploy
python scripts/manage_semantic_model.py ci-deploy  # Full CI/CD
```

### GitHub Actions Setup

#### 1. Configure Secrets

Go to: `Repository Settings` → `Secrets and variables` → `Actions` → `New repository secret`

Required secrets:
```
SNOWFLAKE_ACCOUNT=fvqlqib-tj68700
SNOWFLAKE_USER=LIMA
SNOWFLAKE_PASSWORD=your_password_here
SNOWFLAKE_ROLE=SYSADMIN
SNOWFLAKE_WAREHOUSE=TEST
SNOWFLAKE_DATABASE=PLAYGROUND_LM
SNOWFLAKE_SCHEMA=CORTEX_ANALYTICS_ORCHESTRATOR
SNOWFLAKE_SEMANTIC_STAGE=SEMANTIC_MODELS
```

#### 2. Workflow File

Create `.github/workflows/deploy-semantic-model.yml`:

```yaml
name: Deploy Semantic Model

on:
  push:
    branches: [main]
    paths:
      - 'orchestrator/semantic_models/**'
  workflow_dispatch:

jobs:
  merge-and-deploy:
    runs-on: ubuntu-latest
    
    steps:
      - name: Checkout code
        uses: actions/checkout@v4
      
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          pip install pyyaml snowflake-connector-python python-dotenv
      
      - name: Merge semantic model
        run: |
          python scripts/merge_semantic_models.py
      
      - name: Deploy to Snowflake
        env:
          SNOWFLAKE_ACCOUNT: ${{ secrets.SNOWFLAKE_ACCOUNT }}
          SNOWFLAKE_USER: ${{ secrets.SNOWFLAKE_USER }}
          SNOWFLAKE_PASSWORD: ${{ secrets.SNOWFLAKE_PASSWORD }}
          SNOWFLAKE_ROLE: ${{ secrets.SNOWFLAKE_ROLE }}
          SNOWFLAKE_WAREHOUSE: ${{ secrets.SNOWFLAKE_WAREHOUSE }}
          SNOWFLAKE_DATABASE: ${{ secrets.SNOWFLAKE_DATABASE }}
          SNOWFLAKE_SCHEMA: ${{ secrets.SNOWFLAKE_SCHEMA }}
        run: |
          python scripts/deploy_semantic_model.py
      
      - name: Upload merged model artifact
        uses: actions/upload-artifact@v3
        with:
          name: semantic-merged-model
          path: semantic_merged.yaml
```

#### 3. Trigger Deployment

**Automatic:**
- Any push to `main` that modifies `orchestrator/semantic_models/**`

**Manual:**
1. Go to `Actions` tab
2. Select `Deploy Semantic Model`
3. Click `Run workflow`
4. Select branch
5. Click `Run workflow` button

### Trigger Workflows

**Automatic:**
- Push to `main` with changes to `orchestrator/semantic_models/**`
- Workflow automatically merges and deploys

**Manual:**
1. Go to `Actions` tab in GitHub
2. Select `Deploy Semantic Model`
3. Click `Run workflow`
4. Select branch (usually `main`)
5. Click `Run workflow` button

### Exit Codes

Understanding script exit codes for CI/CD pipeline:

- `0` - Success ✅
- `1` - Validation/deployment failed ❌
- `130` - User cancelled (Ctrl+C) ⚠️

### Local Pre-Commit Validation

Create `.git/hooks/pre-commit`:

```bash
#!/bin/bash

# Check if semantic model files changed
if git diff --cached --name-only | grep -q "orchestrator/semantic_models/"
then
    echo "🔍 Validating semantic model changes..."
    
    # Validate YAML syntax
    python -c "import yaml; yaml.safe_load(open('orchestrator/semantic_models/schema.yaml'))" || exit 1
    python -c "import yaml; yaml.safe_load(open('orchestrator/semantic_models/instructions.yaml'))" || exit 1
    python -c "import yaml; yaml.safe_load(open('orchestrator/semantic_models/verified_queries.yaml'))" || exit 1
    
    # Try merge
    python scripts/merge_semantic_models.py || exit 1
    
    echo "✅ Semantic model validation passed!"
fi
```

Make executable:
```bash
chmod +x .git/hooks/pre-commit
```

---

## 🔧 Troubleshooting

### Issue: "File not found" when merging

```powershell
# Check if modular files exist:
ls orchestrator/semantic_models/

# If missing, split from original:
python scripts/split_semantic_model.py
```

### Issue: "YAML syntax error"

```powershell
# Validate each file individually:
python -c "import yaml; yaml.safe_load(open('orchestrator/semantic_models/schema.yaml'))"
python -c "import yaml; yaml.safe_load(open('orchestrator/semantic_models/instructions.yaml'))"
python -c "import yaml; yaml.safe_load(open('orchestrator/semantic_models/verified_queries.yaml'))"

# Common issues:
# - Incorrect indentation (use 2 spaces, not tabs)
# - Unquoted special characters (: - [ ] { } # ! & * ?)
# - Missing colons after keys
# - Inconsistent list formatting
```

### Issue: "Deploy fails but merge succeeds"

```powershell
# Test Snowflake connection:
python tests/test_connection.py

# Check credentials in .env:
cat .env | grep SNOWFLAKE

# Check if stage exists:
# In Snowflake, run:
# SHOW STAGES IN PLAYGROUND_LM.CORTEX_ANALYTICS_ORCHESTRATOR;
```

### Issue: "Cortex Analyst gives wrong answers"

```powershell
# 1. Check if latest model deployed:
# In Snowflake:
# LIST @SEMANTIC_MODELS;

# 2. Verify instructions are clear:
code orchestrator/semantic_models/instructions.yaml

# 3. Add more verified queries for training:
code orchestrator/semantic_models/verified_queries.yaml

# 4. Re-deploy:
python scripts/merge_semantic_models.py
python scripts/deploy_semantic_model.py
```

### Issue: "Merge creates huge file"

```powershell
# Check modular file sizes:
ls -lh orchestrator/semantic_models/*.yaml

# If schema.yaml is too large, consider:
# 1. Remove unused dimensions
# 2. Split into multiple semantic models (by business unit)
# 3. Use views to pre-aggregate data
```

### Issue: "Git merge conflicts"

```powershell
# Because files are modular, conflicts are easier:

# 1. Accept both changes if in different sections
# 2. Edit conflicted file directly
code orchestrator/semantic_models/schema.yaml  # Fix conflicts

# 3. Test the merge
python scripts/merge_semantic_models.py

# 4. Complete merge
git add orchestrator/semantic_models/schema.yaml
git commit -m "fix: resolve merge conflict in schema"
```

---

## 📊 Statistics & Monitoring

### Current Model Stats

```
Model: SFMC_EMAIL_PERFORMANCE_DEV
Created: 2026-02-24
Last Updated: 2026-02-24

Components:
- schema.yaml: 6 tables, ~90KB
- instructions.yaml: 14 rules, ~6KB
- verified_queries.yaml: 63 queries, ~67KB

Merged Output:
- semantic_merged.yaml: 169.3 KB (173,334 bytes)

Business Units: 7 (VCUK, VCDE, VCFR, VCES, VCIT, VCNL, VCBE)
Markets: 15+ (UK, Germany, France, Spain, Italy, Netherlands, Belgium, etc.)
Date Range: 2023-01-01 to present
```

### View Merge Statistics

```powershell
python scripts/merge_semantic_models.py

# Output shows:
# ✅ Tables: 6
# ✅ Instructions: 14
# ✅ Verified Queries: 63
# ✅ File Size: 173,334 bytes
```

---

## 📚 Additional Resources

### Documentation

- [Cortex Analyst Official Docs](https://docs.snowflake.com/en/user-guide/snowflake-cortex/cortex-analyst)
- [Semantic Model Best Practices](https://docs.snowflake.com/en/user-guide/snowflake-cortex/cortex-analyst-semantic-model)
- [Cortex Services Guide](./02_STEP_2.1_CORTEX_SERVICES.md)
- [Semantic Model Automation](./02_STEP_2.2_SEMANTIC_MODEL_AUTOMATION.md)
- [DIA Implementation Plan](../DIA_V2_IMPLEMENTATION_PLAN.md)

### Related Files

```
orchestrator/semantic_models/     # Modular model components
scripts/split_semantic_model.py   # Split utility
scripts/merge_semantic_models.py  # Merge utility
scripts/deploy_semantic_model.py  # Deployment script
data-layer/semantic-models/       # Original monolithic backup
.github/workflows/                # CI/CD automation
```

### Support

- **Issues**: Create issue on GitHub
- **Questions**: Check [orchestrator/semantic_models/README.md](../orchestrator/semantic_models/README.md)
- **Updates**: Follow commits to `orchestrator/semantic_models/`

---

## 🎓 Summary

### Key Concepts

1. **Modular = Easy Editing**
   - Edit `schema.yaml`, `instructions.yaml`, `verified_queries.yaml` separately
   - Clear separation of concerns
   - Team-friendly collaboration

2. **Split Once = One-Time Operation**
   - Use `split_semantic_model.py` to break down existing monolithic file
   - Creates 3 modular files from 1 large file

3. **Merge Every Time = Deployment**
   - Use `merge_semantic_models.py` before every deployment
   - Combines 3 modular files into 1 deployment-ready file
   - Automated in CI/CD pipeline

4. **Git = Version Control**
   - Commit modular files, not merged output
   - Small focused commits
   - Easy code reviews

### Quick Command Reference

```powershell
# Daily workflow
code orchestrator/semantic_models/schema.yaml       # Edit
python scripts/merge_semantic_models.py             # Merge
python scripts/deploy_semantic_model.py             # Deploy

# One-time setup
python scripts/split_semantic_model.py              # Split monolithic → modular

# Validation
python -c "import yaml; yaml.safe_load(open('orchestrator/semantic_models/schema.yaml'))"

# Git workflow
git add orchestrator/semantic_models/*.yaml
git commit -m "feat: add new dimensions"
git push origin main
```

---

## 📎 Appendix: Legacy Monolithic Workflow

> **⚠️ Note**: The commands below work with the **original single-file approach** (`data-layer/semantic-models/semantic.yaml`).
> 
> **We recommend using the modular workflow** described in this guide instead.

### Legacy Commands

```powershell
# Validate semantic.yaml
python scripts/manage_semantic_model.py validate

# Show model info
python scripts/manage_semantic_model.py stats

# Deploy to Snowflake
python scripts/manage_semantic_model.py deploy

# Full CI/CD workflow (validate → deploy → verify)
python scripts/manage_semantic_model.py ci-deploy

# List deployed versions
python scripts/manage_semantic_model.py list-versions

# Verify current deployment
python scripts/manage_semantic_model.py verify
```

### Legacy Daily Development

```powershell
# Edit semantic.yaml in VSCode
code data-layer/semantic-models/semantic.yaml

# Validate changes
python scripts/manage_semantic_model.py validate

# Deploy when ready
python scripts/manage_semantic_model.py deploy
```

### Legacy Add Table Programmatically

```powershell
python scripts/manage_semantic_model.py add-table MY_NEW_TABLE \
    --database DEV_MARCOM_DB \
    --schema APP_DIRECTMARKETING \
    --table MY_TABLE \
    --description "My new table"
```

### Legacy File Structure

```
data-layer/semantic-models/
├── semantic.yaml              # Main semantic model (monolithic)
└── backups/                   # Auto-created backups
    └── semantic_YYYYMMDD_HHMMSS.yaml
```

### Migration from Legacy to Modular

If you have an existing monolithic `semantic.yaml`:

```powershell
# Split into modular components (one-time operation)
python scripts/split_semantic_model.py

# This creates:
# - orchestrator/semantic_models/schema.yaml
# - orchestrator/semantic_models/instructions.yaml
# - orchestrator/semantic_models/verified_queries.yaml

# Then use modular workflow going forward:
code orchestrator/semantic_models/schema.yaml        # Edit
python scripts/merge_semantic_models.py              # Merge
python scripts/deploy_semantic_model.py              # Deploy
```

---

**Last Updated:** 2026-02-24  
**Version:** 2.0.0  
**Maintainer:** Lima (lima0802)

🎯 Happy modeling!
