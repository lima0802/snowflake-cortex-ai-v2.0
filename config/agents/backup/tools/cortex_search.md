#  Cortex Search Tool Configuration

> **Purpose**: Template for searching unstructured marketing assets (Guidelines, Briefs, Strategy).

---

## Tool Setup in Snowsight

**Location**: AI&ML  Agents  [SFMC_EMAIL_ANALYTICS_AGENT]  Edit  Tools  Add Cortex Search Services

| Setting | Value |
|---------|-------|
| Cortex Search Service | `DEV_MARCOM_DB.APP_DIRECTMARKETING.CORTEX_SFMC_BENCHMARK_SEARCH` |
| ID Column | `BENCHMARK_ID` |
| Title Column | `METRIC_NAME` |
| Name | `Benchmark_Intelligence_Base` |

---

## Tool Description

Copy this into the **Description** field:

```text
Searches through industry benchmarks, performance standards, and campaign threshold guidelines for SFMC email marketing.

**Use this tool when the user asks about:**
- Industry benchmark standards (vitals for retail/automotive)
- Expected performance for specific email types (Newsletter, eDM, Triggered)
- Metric definitions and benchmark thresholds (Excellent, Strong, Good, Warning, Critical)
- Success criteria and action requirements for email campaigns
- Market-specific or industry-specific performance standards

**Searchable Content:**
- SEARCH_CONTENT: Contains the textual description of the benchmark and thresholds.

**Available Attributes & Columns:**
- METRIC_NAME: Open Rate, Click Rate, CTOR, etc.
- EMAIL_TYPE: Newsletter, Promotional, Automated, etc.
- STATUS: Performance level (Excellent to Critical)
- INDUSTRY: Automotive, Retail, etc.
- YEAR_PERIOD: 2024, 2025.
- MIN_VALUE / MAX_VALUE: Numeric thresholds for the status.
- STATUS_LABEL: Human-readable status name.
- ACTION_REQUIRED: Recommended action for that performance level.

**Do NOT use this tool for:**
- Querying YOUR live performance numbers or KPIs (use Email_Performance_Analytics)
- Calculating YTD/YoY trends for your internal data
```

---

## Alternative Descriptions

### Short Version
```text
Search marketing playbooks, brand guidelines, and campaign strategy documents for qualitative context.
```

### Detailed Version
```text
Semantic search over marketing unstructured data:
- Content: Strategy briefs, playbooks, guidelines.
- Searchable Metadata: Document type, Market, Program Name.
- Use Case: Identifying "How" or "Why" behind campaign performance, vs "What" (which is in Analyst).
```
