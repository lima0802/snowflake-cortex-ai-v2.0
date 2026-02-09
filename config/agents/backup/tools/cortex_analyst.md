#  Cortex Analyst Tool Configuration

> **Purpose**: Configuration and description templates for the Direct Marketing Analytics tool.

---

## Tool Setup in Snowsight

**Location**: AI&ML  Agents > [SFMC_EMAIL_ANALYTICS_AGENT]  Edit  Tools  Add Cortex Analyst

| Setting | Value |
|---------|-------|
| Semantic View | `DEV_MARCOM_DB.APP_DIRECTMARKETING.SFMC_EMAIL_PERFORMANCE` |
| Name | `Direct_Marketing_Analytics` |
| Warehouse | `DEV_MARCOM_APP_DIRECTMARKETING_ETL_WHS` |
| Query Timeout | 90 seconds |

---

## Tool Description

Copy this into the **Description** field:

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
- Viewing raw subscriber lists or PII data
```

---

## Alternative Descriptions

### Short Version (for simple agents)
```text
Query SFMC email marketing metrics including sends, opens, clicks, and bounces. Use for calculating KPIs like open rate/CTOR and comparing performance across markets and programs.
```

### Detailed Version (Analytical Focus)
```text
Primary analytics tool for SFMC Email Performance. 
- Metrics: Gross/Net Sends, Unique Opens, Unique Clicks, Hard/Soft Bounces, Unsubscribes.
- Calculated Fields: Open Rate, Click Rate, Click-to-Open Rate (CTOR).
- Features: Handles YTD/YoY temporal analysis, cross-market variance, and program-level deep dives.
- Reliability: Connected to dev_marcom_db production-ready semantic view.
```
