# Modular Semantic Model Structure

**Model:** SFMC_EMAIL_PERFORMANCE_DEV  
**Created:** 2026-02-24  
**Description:** Salesforce Marketing Cloud email campaign performance analytics for Volvo.
Tracks sends, opens, clicks, bounces, and unsubscribes across business units and markets.
Primary use cases: campaign performance monitoring, engagement rate analysis, 
market comparisons, and trend reporting.

Business Units: VCUK (UK), VCDE (Germany), VCFR (France), VCES (Spain), 
VCIT (Italy), VCNL (Netherlands), VCBE (Belgium), and others.


---

## 📁 File Structure

This semantic model is split into three modular components:

### 1. `schema.yaml` - Table Schemas
- **Purpose:** Define all tables, dimensions, measures, and time dimensions
- **Update when:** Adding/modifying tables or columns
- **Size:** ~91533 characters

### 2. `instructions.yaml` - Business Rules
- **Purpose:** Define how Cortex Analyst should interpret queries
- **Update when:** Adding business logic or query guidelines
- **Contains:** Business rules, data interpretation, best practices

### 3. `verified_queries.yaml` - Training Examples
- **Purpose:** Provide example questions with verified SQL
- **Update when:** Adding new query patterns or training examples
- **Contains:** Question/SQL pairs for training

---

## 🔄 Deployment Workflow

1. **Edit** the appropriate file (schema, instructions, or verified_queries)
2. **Merge** files into single model: `python scripts/merge_semantic_models.py`
3. **Deploy** to Snowflake: `python scripts/deploy_semantic_model.py`

---

## 📝 Editing Guidelines

### Adding a New Table
```bash
# Edit schema.yaml
# Add your table under 'tables:' section
# Then merge and deploy
```

### Updating Business Rules
```bash
# Edit instructions.yaml
# Add/modify rules
# Then merge and deploy
```

### Adding Training Examples
```bash
# Edit verified_queries.yaml
# Add question/SQL pairs
# Then merge and deploy
```

---

## 🧪 Testing

```bash
# Merge files
python scripts/merge_semantic_models.py

# Validate YAML syntax
python -c "import yaml; yaml.safe_load(open('semantic_merged.yaml'))"

# Deploy to test stage
python scripts/deploy_semantic_model.py --stage TEST_SEMANTIC_MODELS
```

---

## 📚 Documentation

- [Cortex Analyst Documentation](https://docs.snowflake.com/en/user-guide/snowflake-cortex/cortex-analyst)
- [Semantic Model Guide](../../guides/02_STEP_2.2_SEMANTIC_MODEL_AUTOMATION.md)
- [DIA Implementation Plan](../../DIA_V2_IMPLEMENTATION_PLAN.md)

---

**Last Split:** 2026-02-24 21:22:12  
**Original File:** data-layer\semantic-models\semantic.yaml
