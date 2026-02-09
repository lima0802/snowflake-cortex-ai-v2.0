# Instructor Setup Guide - Multi-User Cortex AI Lab

## Overview

This guide provides step-by-step instructions for instructors to set up the multi-user Snowflake Cortex AI lab environment. The setup creates a shared sandbox environment where multiple participants can work simultaneously in isolated schemas.

## Prerequisites

- **ORGADMIN** or **ACCOUNTADMIN** role access
- Snowflake account with Cortex AI enabled
- List of participant email addresses/usernames
- Estimated number of participants (for resource sizing)

## Pre-Lab Setup (Required)

### Step 1: Account-Level Configuration

Execute the following SQL as **ACCOUNTADMIN**:

```sql
-- Account-level setup (done once by ORGADMIN/ACCOUNTADMIN)
USE ROLE ACCOUNTADMIN;

-- Enable Cortex cross-region (done centrally)
ALTER ACCOUNT SET CORTEX_ENABLED_CROSS_REGION = 'AWS_EU';

-- Create shared database for all users
CREATE DATABASE IF NOT EXISTS SNOWCAMP_DB;

-- Create Snowflake Intelligence database and schema for agents
CREATE DATABASE IF NOT EXISTS SNOWFLAKE_INTELLIGENCE;
CREATE SCHEMA IF NOT EXISTS SNOWFLAKE_INTELLIGENCE.AGENTS;

-- Create multi-cluster warehouse for 80+ concurrent users
CREATE WAREHOUSE IF NOT EXISTS SNOWCAMP_WHS
WITH 
  WAREHOUSE_SIZE = 'MEDIUM'           -- 4 credits per cluster
  MIN_CLUSTER_COUNT = 2               -- Always have 2 clusters ready
  MAX_CLUSTER_COUNT = 12              -- Scale up to 12 clusters for 80+ users
  SCALING_POLICY = 'STANDARD'         -- Auto-scale based on query queue
  AUTO_SUSPEND = 60                   -- Suspend after 1 minute of inactivity
  AUTO_RESUME = TRUE
  COMMENT = 'Multi-cluster warehouse for Cortex AI lab with 80+ concurrent users';

-- Create account-level email integration (shared by all users)
CREATE OR REPLACE NOTIFICATION INTEGRATION email_integration_shared
  TYPE = email
  ENABLED = true
  DEFAULT_SUBJECT = 'Snowflake Intelligence Lab';

-- Create lab user role template
CREATE ROLE IF NOT EXISTS SNOWCAMP;

-- Grant necessary privileges to the role
GRANT USAGE ON DATABASE SNOWCAMP_DB TO ROLE SNOWCAMP;
GRANT CREATE SCHEMA ON DATABASE SNOWCAMP_DB TO ROLE SNOWCAMP;
GRANT USAGE ON DATABASE SNOWFLAKE_INTELLIGENCE TO ROLE SNOWCAMP;
GRANT USAGE ON SCHEMA SNOWFLAKE_INTELLIGENCE.AGENTS TO ROLE SNOWCAMP;
GRANT USAGE ON WAREHOUSE SNOWCAMP_WHS TO ROLE SNOWCAMP;
GRANT USAGE ON INTEGRATION email_integration_shared TO ROLE SNOWCAMP;

-- Create dedicated database and schema for SI and agents. 

-- Grant Cortex database roles (this is the correct approach)
GRANT DATABASE ROLE SNOWFLAKE.CORTEX_USER TO ROLE SNOWCAMP;

-- Grant privileges for future schemas
GRANT CREATE TABLE ON FUTURE SCHEMAS IN DATABASE SNOWCAMP_DB TO ROLE SNOWCAMP;
GRANT CREATE VIEW ON FUTURE SCHEMAS IN DATABASE SNOWCAMP_DB TO ROLE SNOWCAMP;
GRANT CREATE CORTEX SEARCH SERVICE ON FUTURE SCHEMAS IN DATABASE SNOWCAMP_DB TO ROLE SNOWCAMP;
GRANT USAGE ON FUTURE SCHEMAS IN DATABASE SNOWCAMP_DB TO ROLE SNOWCAMP;
GRANT CREATE AGENT ON FUTURE SCHEMAS IN DATABASE SNOWCAMP_DB TO ROLE SNOWCAMP;
GRANT CREATE AGENT ON SCHEMA SNOWFLAKE_INTELLIGENCE.AGENTS TO ROLE SNOWCAMP;

```

### Step 2: User Account Setup

For each participant, execute the following (replace email addresses):

```sql
-- Create user accounts (if they don't exist)
-- Replace with actual participant email addresses
CREATE USER IF NOT EXISTS "participant1@company.com" 
  PASSWORD = 'TempPassword123!' 
  MUST_CHANGE_PASSWORD = TRUE
  DEFAULT_ROLE = SNOWCAMP;

CREATE USER IF NOT EXISTS "participant2@company.com" 
  PASSWORD = 'TempPassword123!' 
  MUST_CHANGE_PASSWORD = TRUE
  DEFAULT_ROLE = SNOWCAMP;

-- Grant the lab role to all participants
GRANT ROLE SNOWCAMP TO USER "participant1@company.com";
GRANT ROLE SNOWCAMP TO USER "participant2@company.com";

-- Repeat for all participants...
```

### Step 3: Verification Script

Run this verification to ensure setup is correct:

```sql
-- Verify database and warehouse
SHOW DATABASES LIKE 'SNOWCAMP_DB';
SHOW WAREHOUSES LIKE 'SNOWCAMP_WHS';

-- Verify role and permissions
SHOW GRANTS TO ROLE SNOWCAMP;

-- Verify integration
SHOW INTEGRATIONS LIKE 'email_integration_shared';

-- Check user assignments
SHOW GRANTS OF ROLE SNOWCAMP;
```

## Lab Day Setup

### Pre-Session Checklist

- [ ] All participant accounts created and tested
- [ ] Warehouse `SNOWCAMP_WHS` is running
- [ ] Database `SNOWCAMP_DB` is accessible
- [ ] Email integration is functional
- [ ] Lab materials distributed to participants
- [ ] Backup instructor account with ACCOUNTADMIN access available

### Session Preparation

1. **Test Environment**: Log in with a test participant account to verify full workflow
2. **Resource Monitoring**: Set up monitoring for warehouse usage and costs
3. **Backup Plan**: Prepare troubleshooting scripts for common issues

### During the Lab

#### Monitoring Commands

```sql
-- Monitor multi-cluster warehouse usage and scaling
SELECT * FROM SNOWFLAKE.ACCOUNT_USAGE.WAREHOUSE_METERING_HISTORY 
WHERE WAREHOUSE_NAME = 'SNOWCAMP_WHS' 
AND START_TIME >= CURRENT_DATE();

-- Monitor active clusters and auto-scaling
SELECT 
    WAREHOUSE_NAME,
    WAREHOUSE_SIZE,
    MIN_CLUSTER_COUNT,
    MAX_CLUSTER_COUNT,
    RUNNING_CLUSTERS,
    QUEUED_PROVISIONING_CLUSTERS,
    QUEUED_REPAIR_CLUSTERS
FROM SNOWFLAKE.INFORMATION_SCHEMA.WAREHOUSES 
WHERE WAREHOUSE_NAME = 'SNOWCAMP_WHS';

-- Monitor query queue and concurrency
SELECT 
    WAREHOUSE_NAME,
    AVG(AVG_RUNNING) as AVG_RUNNING_QUERIES,
    AVG(AVG_QUEUED_LOAD) as AVG_QUEUED_QUERIES,
    MAX(AVG_QUEUED_LOAD) as MAX_QUEUED_QUERIES
FROM SNOWFLAKE.ACCOUNT_USAGE.WAREHOUSE_LOAD_HISTORY 
WHERE WAREHOUSE_NAME = 'SNOWCAMP_WHS'
AND START_TIME >= CURRENT_DATE()
GROUP BY WAREHOUSE_NAME;

-- Monitor schema creation
SHOW SCHEMAS IN DATABASE SNOWCAMP_DB;

-- Check active sessions
SHOW SESSIONS;

-- Monitor Cortex usage
SELECT * FROM SNOWFLAKE.ACCOUNT_USAGE.QUERY_HISTORY 
WHERE QUERY_TEXT ILIKE '%CORTEX%' 
AND START_TIME >= CURRENT_DATE();
```

#### Common Troubleshooting

**User Can't Create Schema**
```sql
-- Grant additional privileges if needed
GRANT CREATE SCHEMA ON DATABASE SNOWCAMP_DB TO ROLE SNOWCAMP;
```

**Warehouse Access Issues**
```sql
-- Verify warehouse grants
SHOW GRANTS ON WAREHOUSE SNOWCAMP_WHS;
-- Re-grant if necessary
GRANT USAGE ON WAREHOUSE SNOWCAMP_WHS TO ROLE SNOWCAMP;
```

**Multi-Cluster Scaling Issues**
```sql
-- Check current cluster status
SELECT 
    WAREHOUSE_NAME,
    RUNNING_CLUSTERS,
    QUEUED_PROVISIONING_CLUSTERS
FROM SNOWFLAKE.INFORMATION_SCHEMA.WAREHOUSES 
WHERE WAREHOUSE_NAME = 'SNOWCAMP_WHS';

-- Emergency scaling adjustments
-- Increase capacity immediately for high load:
ALTER WAREHOUSE SNOWCAMP_WHS SET MAX_CLUSTER_COUNT = 15;

-- Reduce capacity to control costs:
ALTER WAREHOUSE SNOWCAMP_WHS SET MAX_CLUSTER_COUNT = 6;

-- Force immediate scaling up (if needed):
ALTER WAREHOUSE SNOWCAMP_WHS SET MIN_CLUSTER_COUNT = 4;
```

**Cortex AI Function Errors**
```sql
-- Check account-level Cortex settings
SHOW PARAMETERS LIKE 'CORTEX_ENABLED_CROSS_REGION' IN ACCOUNT;
```

## Resource Management

### Sizing Guidelines

| Participants | Warehouse Size | Estimated Cost/Hour |
|-------------|----------------|-------------------|
| 1-10        | SMALL          | $2-4              |
| 11-25       | MEDIUM         | $4-8              |
| 26-50       | LARGE          | $8-16             |
| 50+         | X-LARGE        | $16-32            |

### Cost Control

```sql
-- Set warehouse auto-suspend (recommended: 1-2 minutes for labs)
ALTER WAREHOUSE SNOWCAMP_WHS SET AUTO_SUSPEND = 60;

-- Monitor costs during lab
SELECT 
    WAREHOUSE_NAME,
    SUM(CREDITS_USED) AS TOTAL_CREDITS,
    SUM(CREDITS_USED) * 3 AS ESTIMATED_COST_USD  -- Adjust multiplier based on your pricing
FROM SNOWFLAKE.ACCOUNT_USAGE.WAREHOUSE_METERING_HISTORY 
WHERE WAREHOUSE_NAME = 'SNOWCAMP_WHS' 
AND START_TIME >= CURRENT_DATE()
GROUP BY WAREHOUSE_NAME;
```

## Post-Lab Cleanup

### Immediate Cleanup (Optional)

```sql
-- Suspend warehouse to stop costs
ALTER WAREHOUSE SNOWCAMP_WHS SUSPEND;

-- List all user schemas for review
SHOW SCHEMAS IN DATABASE SNOWCAMP_DB;
```

### Full Cleanup (After Lab Series)

```sql
-- WARNING: This will delete all lab data
-- Drop all user schemas (run carefully)
-- DROP SCHEMA SNOWCAMP_DB.USER01;  -- Repeat for each user schema

-- Drop shared resources
-- DROP WAREHOUSE SNOWCAMP_WHS;
-- DROP DATABASE SNOWCAMP_DB;
-- DROP INTEGRATION email_integration_shared;
-- DROP ROLE SNOWCAMP;
```

## Participant Instructions Template

### Email Template for Participants

```
Subject: Snowflake Cortex AI Lab - Access Information

Dear [Participant Name],

You're registered for the Snowflake Cortex AI hands-on lab. Here are your access details:

**Account Information:**
- Account URL: [Your Snowflake Account URL]
- Username: [participant@company.com]
- Temporary Password: TempPassword123!
- Role: SNOWCAMP

**Pre-Lab Preparation:**
1. Download the lab repository: [Repository URL]
2. Review the README.md file
3. Ensure you can log into Snowflake with the provided credentials

**Lab Day:**
- Date: [Date]
- Time: [Time]
- Duration: [Duration]
- Location/Link: [Details]

**What to Bring:**
- Laptop with internet connection
- Downloaded lab materials
- Notebook for taking notes

Questions? Reply to this email or contact [Instructor Contact].

Looking forward to seeing you at the lab!

Best regards,
[Instructor Name]
```

## Troubleshooting Guide

### Common Issues and Solutions

| Issue | Symptom | Solution |
|-------|---------|----------|
| Permission Denied | "Insufficient privileges" error | Check role grants, re-run privilege grants |
| Warehouse Not Found | "Warehouse does not exist" error | Verify warehouse name, check if suspended |
| Schema Creation Failed | "Cannot create schema" error | Verify CREATE SCHEMA privilege on database |
| File Upload Issues | "Stage not found" error | Ensure user created their schema and stages |
| Cortex Functions Fail | "Function not available" error | Check account-level Cortex enablement |

### Emergency Contacts

- **Snowflake Support**: [Support contact information]
- **Account Admin**: [Admin contact information]
- **Technical Backup**: [Backup instructor contact]

## Success Metrics

Track these metrics to measure lab success:

- [ ] All participants successfully logged in
- [ ] All participants created their schemas
- [ ] All participants completed file uploads
- [ ] All participants ran the notebook successfully
- [ ] All participants deployed the Streamlit app
- [ ] Warehouse costs stayed within budget
- [ ] No major technical issues occurred

## Feedback Collection

Post-lab survey questions:

1. How would you rate the overall lab experience? (1-5)
2. Were the instructions clear and easy to follow?
3. Did you encounter any technical issues?
4. What was the most valuable part of the lab?
5. What could be improved for future sessions?
6. Would you recommend this lab to colleagues?

---

**Need Help?** Contact the lab development team or refer to the main repository for additional resources.
