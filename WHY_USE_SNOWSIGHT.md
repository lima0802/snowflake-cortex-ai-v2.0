# Why Agent Deployment Must Use Snowsight

**TL;DR:** The `CREATE AGENT` SQL statement contains complex JSON structures that the Snowflake Python connector cannot parse correctly. You **must** use Snowsight UI to deploy the agent.

---

## The Problem

The `create_agent.sql` file contains a `CREATE AGENT` statement with nested JSON like this:

```sql
CREATE OR REPLACE AGENT PLAYGROUND_LM.CORTEX_ANALYTICS_ORCHESTRATOR.DIRECT_MARKETING_ANALYTICS_AGENT
COMMENT = '...'
PROFILE = {
  "display_name": "Direct Marketing Analytics Agent",
  "avatar": "RobotAgentIcon",
  "color": "var(--chartDim_8-x1mzf9u0)"
}
AGENT_SPEC = {
  "models": {
    "orchestration": "claude-sonnet-4-5"
  },
  "instructions": {
    "orchestration": $$
    ... multi-line text ...
    $$
  }
}
```

### Why Python Fails

The Snowflake Python connector (`snowflake-connector-python`) has a SQL parser that:
1. **Treats `{` as SQL syntax** - It doesn't recognize JSON in CREATE AGENT context
2. **Fails on `:` in JSON** - Interprets it as a SQL operator
3. **Cannot handle `$$` delimiters** - The multi-line string delimiters confuse the parser

**Error:**
```
SQL compilation error:
syntax error line 3 at position 10 unexpected '{'.
syntax error line 4 at position 16 unexpected ':'.
```

---

## Why Snowsight Works

Snowsight's SQL editor:
- ✅ **Understands CREATE AGENT syntax** - Native support for agent DDL
- ✅ **Parses JSON correctly** - Recognizes JSON in PROFILE and AGENT_SPEC
- ✅ **Handles `$$` delimiters** - Properly processes multi-line strings
- ✅ **Validates agent structure** - Provides helpful error messages

---

## Solutions

### ✅ **Option 1: Use Snowsight (Recommended)**

**Steps:**
1. Open Snowsight: https://app.snowflake.com/
2. Go to **Projects** → **Worksheets**
3. Create new worksheet
4. Copy entire `scripts/create_agent.sql` content
5. Click **Run**

**Pros:**
- Works reliably
- Provides validation feedback
- Can test agent immediately in UI

**Cons:**
- Manual process (not automated)

---

### ⚠️ **Option 2: Use Snowflake CLI (SnowSQL)**

If you have SnowSQL installed:

```bash
snowsql -a fvqlqib-tj68700 -u LIMA -d PLAYGROUND_LM -s CORTEX_ANALYTICS_ORCHESTRATOR -f scripts/create_agent.sql
```

**Pros:**
- Can be automated
- Command-line friendly

**Cons:**
- Requires SnowSQL installation
- May still have parsing issues with complex JSON

---

### ❌ **Option 3: Python API (Not Supported)**

Unfortunately, the Snowflake Python connector **cannot** execute CREATE AGENT statements with complex JSON.

**Attempted methods that failed:**
- ✗ `session.sql(sql_content).collect()` - Snowpark
- ✗ `conn.execute_string(sql_content)` - snowflake-connector-python
- ✗ `cursor.execute(sql_content)` - Direct execution

All fail with JSON parsing errors.

---

## Alternative: Programmatic Agent Creation

If you **must** create agents programmatically, you would need to:

1. **Use Snowflake REST API** (not officially supported for agents yet)
2. **Use Terraform Snowflake Provider** (if agent resources are supported)
3. **Wait for Python SDK updates** to properly handle CREATE AGENT syntax

---

## Recommendation

**For now, use Snowsight.** It's the most reliable method and takes less than 1 minute:

1. Open Snowsight
2. Paste `create_agent.sql`
3. Click Run
4. Done! ✅

---

## Future Improvements

Snowflake may add:
- Python SDK support for agent creation
- Simplified agent creation API
- Better JSON handling in Python connector

Until then, **Snowsight is the way to go**. 🚀

---

## Quick Reference

| Method | Works? | Effort | Automation |
|--------|--------|--------|------------|
| Snowsight UI | ✅ Yes | Low | Manual |
| SnowSQL CLI | ⚠️ Maybe | Medium | Scriptable |
| Python API | ❌ No | High | Not possible |
| REST API | ❓ Unknown | Very High | Possible |

**Bottom line:** Use Snowsight for agent deployment. It's fast, reliable, and officially supported.
