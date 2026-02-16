# Step 1.2: Data Layer Setup Guide - DIA v2.0

## 📋 Overview

**Goal:** Create semantic views, benchmarks, and ML model placeholders in Snowflake to support Cortex Analytics.

**Time Estimate:** 30-60 minutes

**Prerequisites:**
- ✅ Snowflake connection working (tested in Step 1.1)
- ✅ Docker containers running
- ✅ Environment variables configured in `.env`

---

## 🎯 What You'll Create

1. **Semantic Views** - Clean, standardized views of SFMC email data
2. **Benchmark Data** - Industry standards for KPI comparison
3. **ML Model Placeholders** - Forecasting and anomaly detection models
4. **Semantic Model File** - YAML configuration for Cortex Analyst

---

## 📊 Step-by-Step Implementation

### Step 1: Create Semantic Views

**What are Semantic Views?**
- Clean, business-friendly views of your data
- Standardized column names and calculations
- Used by Cortex Analyst for natural language queries

**Implementation:**

#### Option 1: Run SQL Script (Recommended)

1. **Navigate to project directory:**
   ```powershell
   cd "c:\Users\LiMa\OneDrive - WPP Cloud\Documentos\Li\05_Project\01_Volvo\DIA\snowflake-cortex-ai-v2.0"
   ```

2. **Run the setup script via Snowflake:**
   ```sql
   -- Open SnowSQL or Snowsight and run:
   USE DATABASE PLAYGROUND_LM;
   USE SCHEMA CORTEX_ANALYTICS_ORCHESTRATOR;
   USE WAREHOUSE TEST;

   -- Execute the views script
   !source data-layer/views/setup_semantic_views.sql
   ```

#### Option 2: Use Snowsight UI

1. Open Snowsight: https://app.snowflake.com/
2. Navigate to **Worksheets**
3. Copy contents from `data-layer/views/setup_semantic_views.sql`
4. Execute the SQL

#### Option 3: Use Python Script

```powershell
# Run from project root
python scripts/setup_data_layer.py --step views
```

**Verify Views Created:**
```sql
-- Check views exist
SHOW VIEWS LIKE 'VW_%' IN SCHEMA CORTEX_ANALYTICS_ORCHESTRATOR;

-- Test data
SELECT * FROM VW_SFMC_EMAIL_PERFORMANCE LIMIT 10;
SELECT * FROM VW_CAMPAIGN_SUMMARY LIMIT 10;
SELECT * FROM VW_MARKET_PERFORMANCE LIMIT 10;
```

**Expected Output:**
- 3 views created: `VW_SFMC_EMAIL_PERFORMANCE`, `VW_CAMPAIGN_SUMMARY`, `VW_MARKET_PERFORMANCE`
- Sample data visible in each view

---

### Step 2: Load Benchmark Data

**What is Benchmark Data?**
- Industry standards for email KPIs (open rate, click rate, etc.)
- Used for comparative analysis: "Is this above/below average?"
- Enables prescriptive recommendations

**Implementation:**

1. **Execute benchmark setup:**
   ```sql
   -- In Snowsight or SnowSQL
   USE DATABASE PLAYGROUND_LM;
   USE SCHEMA CORTEX_ANALYTICS_ORCHESTRATOR;

   !source data-layer/benchmarks/setup_benchmarks.sql
   ```

2. **Verify benchmark table:**
   ```sql
   SELECT * FROM BENCHMARK_THRESHOLDS;
   ```

**Expected Output:**
```
METRIC_NAME     | INDUSTRY_AVG | GOOD_THRESHOLD | EXCELLENT_THRESHOLD
----------------|--------------|----------------|--------------------
OPEN_RATE       | 21.5         | 25.0           | 30.0
CLICK_RATE      | 2.6          | 3.5            | 5.0
BOUNCE_RATE     | 0.7          | 1.0            | 0.5
```

---

### Step 3: Create ML Model Placeholders

**What are ML Models?**
- Forecasting models: Predict future performance
- Anomaly detection: Flag unusual patterns
- Contribution analysis: Explain changes

**Implementation:**

1. **Create model objects:**
   ```sql
   USE DATABASE PLAYGROUND_LM;
   USE SCHEMA CORTEX_ANALYTICS_ORCHESTRATOR;

   !source data-layer/ml-models/setup_ml_models.sql
   ```

2. **Verify models:**
   ```sql
   SHOW MODELS IN SCHEMA CORTEX_ANALYTICS_ORCHESTRATOR;
   ```

**Note:** These are placeholders. Actual model training happens in Phase 2.

---

### Step 4: Deploy Semantic Model YAML

**What is the Semantic Model?**
- YAML file that describes your data to Cortex Analyst
- Defines tables, columns, relationships, and business logic
- Enables natural language queries

**Implementation:**

#### Option 1: Use Python Script (Recommended)

```powershell
# Navigate to project
cd "c:\Users\LiMa\OneDrive - WPP Cloud\Documentos\Li\05_Project\01_Volvo\DIA\snowflake-cortex-ai-v2.0"

# Deploy semantic model
python scripts/deploy_semantic_model.py
```

**Expected Output:**
```
Starting Semantic Model Deployment...
Ensuring stage 'SEMANTIC_MODELS' exists and has directory enabled...
Uploading 'config/semantic.yaml' to @SEMANTIC_MODELS...
   Upload status: UPLOADED

Deployment Complete!
Your semantic model has been uploaded to @SEMANTIC_MODELS.
```

#### Option 2: Manual Upload via Snowsight

1. Open Snowsight
2. Go to **Data** → **Databases** → **PLAYGROUND_LM** → **CORTEX_ANALYTICS_ORCHESTRATOR**
3. Click **Stages** tab
4. Create or open `SEMANTIC_MODELS` stage
5. Upload `config/semantic.yaml`

**Verify Upload:**
```sql
LIST @SEMANTIC_MODELS;

-- Should show semantic.yaml file
```

---

## ✅ Verification Checklist

Run these commands to verify everything is set up correctly:

```sql
-- 1. Check database and schema
USE DATABASE PLAYGROUND_LM;
USE SCHEMA CORTEX_ANALYTICS_ORCHESTRATOR;

-- 2. Verify views exist and have data
SHOW VIEWS LIKE 'VW_%';

SELECT COUNT(*) AS VW_EMAIL_PERFORMANCE_ROWS
FROM VW_SFMC_EMAIL_PERFORMANCE;

-- 3. Verify benchmark table
SELECT COUNT(*) AS BENCHMARK_ROWS
FROM BENCHMARK_THRESHOLDS;

-- 4. Verify semantic model uploaded
LIST @SEMANTIC_MODELS;

-- 5. Check stage directory enabled
DESCRIBE STAGE SEMANTIC_MODELS;
```

**Expected Results:**
- ✅ 3 semantic views created
- ✅ Benchmark table has 5+ rows
- ✅ Semantic model file visible in stage
- ✅ Stage has DIRECTORY = ENABLED

---

## 🧪 Testing the Data Layer

### Test 1: Query Semantic Views

```sql
-- Test email performance view
SELECT
    CAMPAIGN_NAME,
    MARKET,
    EMAILS_SENT,
    OPEN_RATE,
    CLICK_RATE
FROM VW_SFMC_EMAIL_PERFORMANCE
WHERE SEND_DATE >= DATEADD(month, -3, CURRENT_DATE())
ORDER BY SEND_DATE DESC
LIMIT 10;
```

### Test 2: Compare Against Benchmarks

```sql
-- Compare performance to benchmarks
SELECT
    v.CAMPAIGN_NAME,
    v.OPEN_RATE AS ACTUAL_OPEN_RATE,
    b.INDUSTRY_AVG AS BENCHMARK_OPEN_RATE,
    CASE
        WHEN v.OPEN_RATE >= b.EXCELLENT_THRESHOLD THEN 'Excellent'
        WHEN v.OPEN_RATE >= b.GOOD_THRESHOLD THEN 'Good'
        WHEN v.OPEN_RATE >= b.INDUSTRY_AVG THEN 'Average'
        ELSE 'Below Average'
    END AS PERFORMANCE_RATING
FROM VW_SFMC_EMAIL_PERFORMANCE v
CROSS JOIN BENCHMARK_THRESHOLDS b
WHERE b.METRIC_NAME = 'OPEN_RATE'
LIMIT 10;
```

### Test 3: Verify Semantic Model Format

```python
# Test semantic model can be loaded
import yaml

with open('config/semantic.yaml', 'r') as f:
    semantic_model = yaml.safe_load(f)
    print(f"Tables defined: {len(semantic_model.get('tables', []))}")
    print(f"Relationships: {len(semantic_model.get('relationships', []))}")
```

---

## 🔧 Troubleshooting

### Issue 1: "Object does not exist" Error

**Problem:** Views or tables not found

**Solution:**
```sql
-- Check you're in the right database/schema
SELECT CURRENT_DATABASE(), CURRENT_SCHEMA();

-- Should show: PLAYGROUND_LM, CORTEX_ANALYTICS_ORCHESTRATOR

-- If not, run:
USE DATABASE PLAYGROUND_LM;
USE SCHEMA CORTEX_ANALYTICS_ORCHESTRATOR;
```

### Issue 2: "Insufficient Privileges"

**Problem:** User doesn't have permission to create objects

**Solution:**
```sql
-- Run as ACCOUNTADMIN or user with CREATE privileges
USE ROLE SYSADMIN;

-- Or grant privileges:
GRANT CREATE VIEW ON SCHEMA CORTEX_ANALYTICS_ORCHESTRATOR TO ROLE SYSADMIN;
GRANT CREATE TABLE ON SCHEMA CORTEX_ANALYTICS_ORCHESTRATOR TO ROLE SYSADMIN;
GRANT CREATE STAGE ON SCHEMA CORTEX_ANALYTICS_ORCHESTRATOR TO ROLE SYSADMIN;
```

### Issue 3: Semantic Model Upload Fails

**Problem:** `deploy_semantic_model.py` script fails

**Solution:**
```powershell
# Test Snowflake connection first
docker exec dia-orchestrator python test_connection.py

# Check file exists
ls config/semantic.yaml

# Run with verbose output
python scripts/deploy_semantic_model.py --verbose
```

### Issue 4: No Sample Data in Views

**Problem:** Views created but return empty results

**Solution:**
The placeholder data in `setup_semantic_views.sql` is sample data. You need to:
1. Replace the sample data source with your actual SFMC tables
2. Update column mappings to match your schema
3. Adjust the view logic as needed

---

## 📊 Data Layer Architecture

```
PLAYGROUND_LM
└── CORTEX_ANALYTICS_ORCHESTRATOR
    ├── Views (Semantic Layer)
    │   ├── VW_SFMC_EMAIL_PERFORMANCE
    │   ├── VW_CAMPAIGN_SUMMARY
    │   └── VW_MARKET_PERFORMANCE
    │
    ├── Tables (Reference Data)
    │   └── BENCHMARK_THRESHOLDS
    │
    ├── Models (ML)
    │   ├── EMAIL_FORECAST_MODEL (placeholder)
    │   └── ANOMALY_DETECTION_MODEL (placeholder)
    │
    └── Stages (File Storage)
        └── SEMANTIC_MODELS
            └── semantic.yaml
```

---

## 🚀 Next Steps

After completing Step 1.2, you should have:
- ✅ Semantic views with clean, standardized data
- ✅ Benchmark thresholds for KPI comparison
- ✅ ML model placeholders
- ✅ Semantic model YAML deployed to Snowflake

**Ready to proceed to Phase 2: Core Services Implementation**

Refer to [DIA_V2_IMPLEMENTATION_PLAN.md](DIA_V2_IMPLEMENTATION_PLAN.md) for Step 2.1: Implement Cortex Service Wrappers.

---

## 📚 Additional Resources

- [Snowflake Cortex Analyst Documentation](https://docs.snowflake.com/en/user-guide/snowflake-cortex/cortex-analyst)
- [Semantic Model YAML Reference](https://docs.snowflake.com/en/user-guide/snowflake-cortex/cortex-analyst/semantic-model-spec)
- [DIA_V2_IMPLEMENTATION_PLAN.md](DIA_V2_IMPLEMENTATION_PLAN.md) - Full implementation guide

---

## 📝 Notes

- The sample data in the SQL scripts is for demonstration only
- Replace placeholder data sources with your actual SFMC tables
- Adjust views and calculations to match your business requirements
- Consider using materialized views for better performance with large datasets
