#  Snowflake Agent Creation Script (Refined)

> **Agent Name**: `Direct Marketing Analytics Agent`
> **Environment**: `DEV_MARCOM_DB.APP_DIRECTMARKETING`

---

##  1. Set context

```sql
-- Set context
USE ROLE CLD-SNOWFLAKE-DEV-MARCOM-APP-DIRECTMARKETING-ETL-SG;
USE DATABASE DEV_MARCOM_DB;
USE SCHEMA APP_DIRECTMARKETING;

-- Ensure stages exist (for tools and assets)
-- CREATE STAGE IF NOT EXISTS SEMANTIC_MODELS DIRECTORY = (ENABLE = TRUE);
-- (Optional) Verify Search Service creation
```

---

##  2. Agent Setup Instructions (Manual Steps)

Follow these steps in **AI & ML** > **Agents** > **+ Agent**:

###  Tab 1: About
*   **Display Name**: `Direct Marketing Analytics Agent`
*   **Description**: `AI-powered analytics agent for Salesforce Marketing Cloud email campaign performance. Query YTD metrics, YoY benchmarks, program performance, and market comparisons using natural language.`
*   **Example Questions**:
    1. `What was the open rate for last month's global eDM campaign?`
    2. `Show me the click-through rate trend for the past six months in Europe`
    3. `How does Germany's email performance compare to the European average?`
    4. `Which campaign achieved the highest engagement in Q3?`
    5. `Compare open rates for France Spain and Italy for the most recent campaign`
    6. `What is Spain's opt-out rate compared to the EU average in Q3?`
    7. `Compare open and click rates for EX30 campaigns in NL versus BE`
    8. `Summarize all markets where the opt-out rate exceeds 0.5%`
    9. `Show me Link Tracking Alias performance for Global eNewsletter in France`

###  Tab 2: Tools

#### Tool A: Cortex Analyst (Email_Performance_Analytics)
*   **Add Tool**: Cortex Analyst
*   **Semantic Model / View**: `DEV_MARCOM_DB.APP_DIRECTMARKETING.SFMC_EMAIL_PERFORMANCE`
*   **Name**: `Email_Performance_Analytics`
*   **Warehouse**: `DEV_MARCOM_APP_DIRECTMARKETING_ANALYST_WHS`
*   **Description**:
    ```text
    Analyzes SFMC (Salesforce Marketing Cloud) email marketing performance data. Use this tool to query core campaign metrics and calculate marketing KPIs across different dimensions.

    **Use this tool when the user asks about:**
    - Campaign metrics (Sends, Opens, Clicks, Bounces, Unsubscribes)
    - Performance KPIs (Open Rate, Click Rate, CTOR, Bounce Rate)
    - Market and Program comparisons
    - Year-to-Date (YTD) performance and Year-over-Year (YoY) trends
    - Performance benchmarks and target attainment

    **Available Data Dimensions:**
    - Markets: Regional or country-level segmentation
    - Programs: Specific marketing initiatives or journeys
    - Time: Daily, Monthly, Quarterly, and Yearly granularity
    - Campaigns: Individual email sends and subject lines
    
    **Do NOT use this tool for:**
    - Searching for specific document content or marketing PDFs (use Cortex Search)
    - Managing user permissions or warehouse settings
    ```

#### Tool B: Cortex Search (Benchmark_Intelligence_Base)
*   **Add Tool**: Cortex Search Services
*   **Cortex Search Service**: `DEV_MARCOM_DB.APP_DIRECTMARKETING.CORTEX_SFMC_BENCHMARK_SEARCH`
*   **ID Column**: `BENCHMARK_ID`
*   **Title Column**: `METRIC_NAME`
*   **Name**: `Benchmark_Intelligence_Base`
*   **Description**:
    ```text
    Searches through industry benchmarks, performance standards, and campaign threshold guidelines for SFMC email marketing.

    **Use this tool when the user asks about:**
    - Industry benchmark standards (vitals for retail/automotive)
    - Expected performance for specific email types (Newsletter, eDM, Triggered)
    - Metric definitions and benchmark thresholds (Excellent, Strong, Good, Warning, Critical)
    - Success criteria and action requirements for email campaigns
    - Market-specific or industry-specific performance standards

    **Available Attributes:**
    METRIC_NAME, EMAIL_TYPE, STATUS, INDUSTRY, YEAR_PERIOD
    ```

###  Tab 3: Orchestration
*   **Model**: `Claude 4.5 Sonnet` 
*   **Time Limit**: `300 seconds`
*   **Token Limit**: `4000 tokens`

#### Orchestration Instructions
**Copy the `instructions.orchestration` block from [`config/agent_spec.yaml`](../../agent_spec.yaml).**

#### Response Instructions
**Copy the `instructions.response` block from [`config/agent_spec.yaml`](../../agent_spec.yaml).**

###  Tab 4: Access
*   **Owner**: `LIMA`

#### Roles & Permissions Reference

**PROD Environment**
| Role | Access Level | Description |
|------|--------------|-------------|
| `CLD-SNOWFLAKE-PROD-MARCOM-APP-DIRECTMARKETING-ETL-SG` | **Ownership / Full Access** | Developers/Engineers. Manage semantic views. |
| `CLD-SNOWFLAKE-PROD-MARCOM-APP-DIRECTMARKETING-ANALYST-SG` | **Usage Only** | Stakeholders. Use agent to ask questions. |

**DEV Environment**
| Role | Access Level | Description |
|------|--------------|-------------|
| `CLD-SNOWFLAKE-DEV-MARCOM-APP-DIRECTMARKETING-ETL-SG` | **Ownership / Full Access** | Developers/Engineers. Manage semantic views. |
| `CLD-SNOWFLAKE-DEV-MARCOM-APP-DIRECTMARKETING-ANALYST-SG` | **Usage Only** | Stakeholders. Use agent to ask questions. |

####  How to Configure
1. Click **+ Add role** in the Access tab.
2. Search for the relevant Account Roles listed above.
3. Assign the appropriate permission levels.

---

##  3. Test in Snowflake Intelligence (UI)

Once the agent is created, follow these steps to validate it in the Snowsight UI:

1.  Navigate to **AI & ML** > **Agents** > **SFMC_EMAIL_ANALYTICS_AGENT**.
2.  Click **Preview in Snowflake Intelligence** (top right corner).
3.  **Role Selection**:
    *   Click the user/role icon (usually top-right or bottom-left of the chat window).
    *   Select Role: `CLD-SNOWFLAKE-DEV-MARCOM-APP-DIRECTMARKETING-ANALYST-SG`.
4.  **Warehouse Selection**:
    *   Select Warehouse: `DEV_MARCOM_APP_DIRECTMARKETING_ANALYST_WHS`.
5.  **Run Test**:
    *   Type the following question into the chat:
        > "What was the average open rate last month?"
    *   Verify that the agent uses the tool and returns a valid response.

