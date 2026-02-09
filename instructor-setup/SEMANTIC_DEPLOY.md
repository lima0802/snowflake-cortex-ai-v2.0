---
description: Deploy and Update Semantic Model Object to Snowflake
---

# 🚀 Deploy Semantic Model Workflow

This workflow automates the deployment of your Semantic Model using a robust Python script.

## Prerequisites
- `pip install snowflake-snowpark-python python-dotenv`
- `.env` file configured with credentials (already done).

## Steps

// turbo
1. **Run Deployment Script**
   This script handles creating the stage `semantic_models`, uploading `config/semantic.yaml`, and updating the `SFMC_EMAIL_PERFORMANCE` object.
   ```powershell
   python scripts/deploy_semantic_model.py
   ```

## 🏁 Post-Deployment Verification

After deployment, test the PROD agent as follows:
1. Open [Snowflake AI Enterprise](https://ai.snowflake.com/volvocars/enterprise/#/homepage)
2. Switch Role to: `CLD-SNOWFLAKE-DEV-MARCOM-APP-DIRECTMARKETING-ANALYST-SG`
3. Select Warehouse: `DEV_MARCOM_APP_DIRECTMARKETING_ANALYST_WHS`
4. Use **"SFMC_EMAIL_PERFORMANCE_DEV"**.

