#  Agent Access Control

> **Purpose**: Defines who can access and interact with the Direct Marketing Analytics Agent across Dev and Prod environments.

---

## Roles and Permissions

### PROD Environment
| Role | Access Level | Description |
|------|--------------|-------------|
| `CLD-SNOWFLAKE-PROD-MARCOM-APP-DIRECTMARKETING-ETL-SG` | **Ownership / Full Access** | AI Developers and Data Engineers. Can develop, edit, and manage the PROD semantic view in Cortex Analyst. |
| `CLD-SNOWFLAKE-PROD-MARCOM-APP-DIRECTMARKETING-ANALYST-SG` | **Usage Only** | AI Developers + Business Stakeholders. Can edit agent system prompt, use the agent to ask questions. |

### DEV Environment
| Role | Access Level | Description |
|------|--------------|-------------|
| `CLD-SNOWFLAKE-DEV-MARCOM-APP-DIRECTMARKETING-ETL-SG` | **Ownership / Full Access** | AI Developers and Data Engineers. Can develop, edit, and manage the DEV semantic view in Cortex Analyst. |
| `CLD-SNOWFLAKE-DEV-MARCOM-APP-DIRECTMARKETING-ANALYST-SG` | **Usage Only** | Business Stakeholders. Can edit agent system prompt and use the agent to ask questions. |

---

## Specific User Access

*Primary developer/owner:*
- User: `[LIMA]`
- Access: Owner/Editor

---

##  How to Configure
In the **Access** tab in Snowsight:
1. Click **+ Add role**
2. Add the relevant Account Roles from the tables above.
3. Assign the appropriate permission levels (Ownership, Usage & Monitor, or Usage Only).

---

##  Grant Privileges
```sql
-- DEV Permissions
GRANT USAGE ON AGENT DEV_MARCOM_DB.APP_DIRECTMARKETING.SFMC_EMAIL_ANALYTICS_AGENT TO ROLE "CLD-SNOWFLAKE-DEV-MARCOM-APP-DIRECTMARKETING-ETL-SG";
GRANT OWNERSHIP ON AGENT DEV_MARCOM_DB.APP_DIRECTMARKETING.SFMC_EMAIL_ANALYTICS_AGENT TO ROLE "CLD-SNOWFLAKE-DEV-MARCOM-APP-DIRECTMARKETING-ETL-SG";
GRANT USAGE ON AGENT DEV_MARCOM_DB.APP_DIRECTMARKETING.SFMC_EMAIL_ANALYTICS_AGENT TO ROLE "CLD-SNOWFLAKE-DEV-MARCOM-APP-DIRECTMARKETING-ANALYST-SG";
GRANT MONITOR ON AGENT DEV_MARCOM_DB.APP_DIRECTMARKETING.SFMC_EMAIL_ANALYTICS_AGENT TO ROLE "CLD-SNOWFLAKE-DEV-MARCOM-APP-DIRECTMARKETING-ANALYST-SG";

-- PROD Permissions (Example for PROD Agent)
-- GRANT USAGE ON AGENT PROD_MARCOM_DB.APP_DIRECTMARKETING.SFMC_EMAIL_ANALYTICS_AGENT TO ROLE "CLD-SNOWFLAKE-PROD-MARCOM-APP-DIRECTMARKETING-ETL-SG";
-- GRANT OWNERSHIP ON AGENT PROD_MARCOM_DB.APP_DIRECTMARKETING.SFMC_EMAIL_ANALYTICS_AGENT TO ROLE "CLD-SNOWFLAKE-PROD-MARCOM-APP-DIRECTMARKETING-ETL-SG";
-- GRANT USAGE ON AGENT PROD_MARCOM_DB.APP_DIRECTMARKETING.SFMC_EMAIL_ANALYTICS_AGENT TO ROLE "CLD-SNOWFLAKE-PROD-MARCOM-APP-DIRECTMARKETING-ANALYST-SG";
```

---

## 🧪 PROD Agent Testing Procedure

Once you have been assigned the appropriate role, please follow these steps to test the new PROD agent:

| Step | Action |
| :--- | :--- |
| **1** | Open: [Snowflake AI Enterprise](https://ai.snowflake.com/volvocars/enterprise/#/homepage) |
| **2** | Click the **User Icon** (bottom left) |
| **3** | Set role to: `CLD-SNOWFLAKE-PROD-MARCOM-APP-DIRECTMARKETING-ANALYST-SG` |
| **4** | Set warehouse to: `PROD_MARCOM_APP_DIRECTMARKETING_ANALYST_WHS` |
| **5** | Look for **"Direct Marketing Analytics PROD Agent"** in the chat, and select **'Direct_Marketing_Analytics_PROD'** as the source |

