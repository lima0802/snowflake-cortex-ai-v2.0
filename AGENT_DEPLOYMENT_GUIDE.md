# Agent Deployment Guide

**Date:** January 30, 2026  
**Agent:** Direct Marketing Analytics Agent

---

## ✅ Recommended Method: Deploy via Snowsight UI

The `create_agent.sql` script contains complex multi-line JSON structures that work best when executed directly in Snowsight.

### Steps to Deploy:

#### 1. Open Snowsight
- Go to your Snowflake account: https://app.snowflake.com/

#### 2. Create a New SQL Worksheet
- Click **Projects** → **Worksheets**
- Click **+ Worksheet** (top right)

#### 3. Set Context
Run these commands first:
```sql
USE ROLE SYSADMIN;
USE WAREHOUSE TEST;
USE DATABASE PLAYGROUND_LM;
USE SCHEMA CORTEX_ANALYTICS_ORCHESTRATOR;
```

#### 4. Copy & Paste the Agent Creation Script
- Open: `scripts/create_agent.sql`
- Copy the ENTIRE file contents
- Paste into the Snowsight worksheet

#### 5. Execute the Script
- Click **Run** (or press Ctrl+Enter)
- Wait for execution to complete (~5-10 seconds)

#### 6. Verify Agent Creation
Run this query:
```sql
SHOW AGENTS LIKE 'DIRECT_MARKETING_ANALYTICS_AGENT' 
IN SCHEMA PLAYGROUND_LM.CORTEX_ANALYTICS_ORCHESTRATOR;
```

You should see:
- **Name:** DIRECT_MARKETING_ANALYTICS_AGENT
- **Created_on:** [timestamp]
- **Database:** PLAYGROUND_LM
- **Schema:** CORTEX_ANALYTICS_ORCHESTRATOR

---

## 🧪 Test the Agent

### Option 1: Test in Snowsight UI

1. Go to **AI & ML** → **Agents**
2. Find **Direct Marketing Analytics Agent**
3. Click on it to open the chat interface
4. Try these test questions:

**Simple Queries:**
```
What is the YTD click rate?
```

**Campaign Search (with LTA):**
```
Show me all campaigns with EX30
```

**Fuzzy Matching:**
```
Find campaigns mentioning sustainability
```

**Global Campaign vs E-newsletter:**
```
Show me Global Campaign performance
What's the click rate for Global E-newsletters?
```

**Market Comparison:**
```
How does Germany compare to the EMEA average?
```

**Benchmark:**
```
How do we compare against industry benchmarks?
```

---

### Option 2: Test via SQL

You can also test the agent using SQL:
```sql
SELECT SNOWFLAKE.CORTEX.COMPLETE(
  'PLAYGROUND_LM.CORTEX_ANALYTICS_ORCHESTRATOR.DIRECT_MARKETING_ANALYTICS_AGENT',
  [
    {'role': 'user', 'content': 'What is the YTD click rate?'}
  ]
) AS response;
```

---

## 📋 What the Script Does

The `create_agent.sql` script will:

1. ✅ **Create the Agent** with name: `DIRECT_MARKETING_ANALYTICS_AGENT`
2. ✅ **Configure Profile**:
   - Display Name: "Direct Marketing Analytics Agent"
   - Avatar: Robot icon
   - Color: Chart color theme

3. ✅ **Set Up Orchestration**:
   - Model: Claude Sonnet 4.5
   - Time Limit: 300 seconds
   - Token Limit: 4000 tokens

4. ✅ **Load Instructions**:
   - Orchestration instructions (with LTA support, fuzzy matching)
   - Response instructions (with campaign clarification)
   - Sample questions

5. ✅ **Configure Tools**:
   - **Email_Performance_Analytics** (Cortex Analyst)
     - Semantic Model: `@PLAYGROUND_LM.CORTEX_ANALYTICS_ORCHESTRATOR.SEMANTIC_FILES/semantic.yaml`
     - Warehouse: TEST
   - **Benchmark_Intelligence_Base** (Cortex Search)
     - Search Service: `DEV_MARCOM_DB.APP_DIRECTMARKETING.CORTEX_SFMC_BENCHMARK_SEARCH`

---

## 🔍 Troubleshooting

### Error: "Agent already exists"
- The script uses `CREATE OR REPLACE`, so it should overwrite
- If you get this error, manually drop the agent first:
```sql
DROP AGENT IF EXISTS PLAYGROUND_LM.CORTEX_ANALYTICS_ORCHESTRATOR.DIRECT_MARKETING_ANALYTICS_AGENT;
```

### Error: "Semantic model file not found"
- Ensure you've run the migration: `python scripts/migrate_semantic_objects.py`
- Verify the file exists:
```sql
LIST @PLAYGROUND_LM.CORTEX_ANALYTICS_ORCHESTRATOR.SEMANTIC_FILES;
```

### Error: "Cortex Search service not found"
- Verify the search service exists:
```sql
SHOW CORTEX SEARCH SERVICES IN SCHEMA DEV_MARCOM_DB.APP_DIRECTMARKETING;
```

### Agent doesn't respond correctly
1. Check the semantic model is valid
2. Verify warehouse TEST is running
3. Check permissions on the semantic model and search service

---

## 📊 Expected Results

After deployment, you should be able to:

✅ Ask questions about email campaign performance  
✅ Search for campaigns using fuzzy matching (handles `-`, `_`, spaces)  
✅ Search for Link Tracking Aliases (LTA)  
✅ Filter by Global Campaign vs E-newsletter  
✅ Compare markets against benchmarks  
✅ Get YTD metrics with YoY comparisons  

---

## 🎯 Next Steps After Deployment

1. **Test Core Functionality**
   - Try the sample questions above
   - Verify LTA search works
   - Test fuzzy matching with different separators

2. **Share with Stakeholders**
   - Provide access to the agent in Snowsight
   - Share sample questions
   - Gather feedback

3. **Monitor Performance**
   - Check query execution times
   - Review agent responses for accuracy
   - Identify any edge cases

4. **Iterate**
   - Update instructions based on feedback
   - Add new verified questions
   - Refine response templates

---

**Ready to deploy?** Open Snowsight and follow the steps above! 🚀
