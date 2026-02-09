# ⚙️ Configuration Files

This folder contains configuration files for Snowflake Cortex AI lab setup and agent configuration.

## 📁 Contents

```
config/
├── README.md                    # This file
├── semantic.yaml                # Basic semantic model for Cortex Analyst
├── semantic_search.yaml         # 🆕 Enhanced model with Cortex Search integration
├── environment.yml              # Python dependencies (optional)
└── agents/                      # 🤖 Agent configuration templates
    ├── README.md                # Agent config overview
    ├── orchestration/           # How the agent thinks & uses tools
    │   ├── default.md           # Default orchestration instructions
    │   └── examples.md          # Variations for different use cases
    ├── response/                # How the agent formats responses
    │   ├── default.md           # Default response formatting
    │   └── examples.md          # Style variations (Executive, Technical, etc.)
    └── tools/                   # Tool descriptions
        ├── cortex_analyst.md    # Sales_Data tool config
        └── cortex_search.md     # Docs tool config
```

---

## 📊 Semantic Models

Two versions of the semantic model are provided:

### `semantic.yaml` (Basic)

The standard semantic model with static sample values.

**Use this if:**
- You're just getting started with the lab
- You want a simpler setup
- You haven't created the `ARTICLE_NAME_SEARCH` Cortex Search service yet

### `semantic_search.yaml` (Enhanced) ⭐ Recommended

Enhanced version with **Cortex Search integration** for dynamic literal retrieval.

**Use this if:**
- You've completed the notebook and created `ARTICLE_NAME_SEARCH`
- You want better fuzzy matching for product names
- You want "carvers" to automatically match "Carver Skis"

**Key difference:**
```yaml
# semantic.yaml (static)
- name: ARTICLE_NAME
  sample_values:
    - Mondracer Infant Bike
    - Premium Bicycle
    
# semantic_search.yaml (dynamic)
- name: ARTICLE_NAME
  cortex_search_service:
    service: ARTICLE_NAME_SEARCH
    literal_column: ARTICLE_NAME
```

### Setup Instructions

1. **Update Schema Reference**:
   - Open the YAML file you want to use
   - Replace `USER01` (or `WAKRAM`) with your actual schema name
   
2. **Upload to Snowflake**:
   - Upload to your `@semantic_files` stage
   - See `../participant-setup/FILE_UPLOAD_GUIDE.md` for detailed steps

### What They Contain
- Table definitions: `DIM_ARTICLE`, `DIM_CUSTOMER`, `FACT_SALES`
- Column mappings and business terminology
- Relationships between tables
- Synonyms for natural language queries
- Verified queries for common questions

---

## 🤖 Agent Configuration (`agents/`)

Templates for configuring your Cortex Agent in Snowsight.

### Quick Reference

| What You Need | File to Use | Where to Paste in Snowsight |
|---------------|-------------|----------------------------|
| Tool selection rules | `agents/orchestration/default.md` | Orchestration → Instructions |
| Response formatting | `agents/response/default.md` | Orchestration → Response Instructions |
| Sales_Data tool description | `agents/tools/cortex_analyst.md` | Tools → Cortex Analyst → Description |
| Docs tool description | `agents/tools/cortex_search.md` | Tools → Cortex Search → Description |

### Available Variations

**Orchestration Styles** (in `agents/orchestration/examples.md`):
- 🎯 Sales-Focused Agent
- 🔍 Product Specialist Agent
- 🔄 Multi-Modal Agent
- 🌐 Multilingual Agent

**Response Styles** (in `agents/response/examples.md`):
- 🎩 Executive Summary
- 📊 Data Analyst (Technical)
- 🎨 Visual-First
- 🎓 Educational
- 🌍 Localized (European)
- 🤝 Conversational

---

## 🐍 Environment (`environment.yml`)

Python dependencies for optional local development.

```bash
conda env create -f environment.yml
conda activate snowflake-cortex-lab
```

> **Note**: This is only needed if you want to run code locally. The lab is designed to run entirely in Snowflake.

---

## ⚠️ Important Notes

1. **Schema Customization Required**: `semantic.yaml` contains `schema: USER01` - you MUST change this
2. **Upload Location**: Semantic files go to `@semantic_files` stage, not `@docs`
3. **Agent Config**: Copy-paste from `agents/` folder into Snowsight UI (no upload needed)

---

## 🔍 Troubleshooting

| Error | Solution |
|-------|----------|
| "Schema not found" | Update schema name in `semantic.yaml` |
| "File not found" | Verify upload to `@semantic_files` stage |
| YAML validation errors | Check for extra spaces or invalid characters |
| Agent not using tools correctly | Review tool descriptions in `agents/tools/` |
