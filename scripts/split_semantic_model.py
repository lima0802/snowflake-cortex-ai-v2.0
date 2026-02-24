"""
Split Semantic Model into Modular Components
=============================================

This script splits a large semantic.yaml file into three separate components:
1. schema.yaml - Table schemas, dimensions, measures
2. instructions.yaml - Business rules and guidelines
3. verified_queries.yaml - Example questions and SQL

Usage:
    python scripts/split_semantic_model.py [--input semantic.yaml] [--output-dir semantic_models/]

Author: Li Ma
Date: February 24, 2026
"""

import os
import sys
import yaml
import argparse
from pathlib import Path
from typing import Dict, Any
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Try to import ruamel.yaml for better formatting
try:
    from ruamel.yaml import YAML
    from ruamel.yaml.scalarstring import LiteralScalarString
    HAS_RUAMEL = True
except ImportError:
    HAS_RUAMEL = False


# PyYAML fallback: Custom literal string class
class LiteralStr(str):
    """String subclass that will be represented as YAML literal block (|)"""
    pass


def literal_representer(dumper, data):
    """YAML representer for literal block style"""
    return dumper.represent_scalar('tag:yaml.org,2002:str', data, style='|')


# Register the literal representer with PyYAML
yaml.add_representer(LiteralStr, literal_representer)


class SemanticModelSplitter:
    """Split a monolithic semantic model into modular components"""
    
    def __init__(self, input_file: str, output_dir: str):
        self.input_file = Path(input_file)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
    def load_model(self) -> Dict[str, Any]:
        """Load the semantic model from YAML file"""
        print(f"📖 Loading semantic model from: {self.input_file}")
        
        with open(self.input_file, 'r', encoding='utf-8') as f:
            model = yaml.safe_load(f)
        
        print(f"✅ Loaded model: {model.get('name', 'Unknown')}")
        return model
    
    def extract_schema(self, model: Dict[str, Any]) -> Dict[str, Any]:
        """Extract table schemas (tables section)"""
        schema = {
            'name': model.get('name'),
            'description': model.get('description', ''),
            'tables': model.get('tables', [])
        }
        
        print(f"📊 Extracted {len(schema['tables'])} tables")
        return schema
    
    def extract_instructions(self, model: Dict[str, Any]) -> Dict[str, Any]:
        """Extract business instructions"""
        instructions = {
            'instructions': model.get('instructions', [])
        }
        
        count = len(instructions['instructions']) if isinstance(instructions['instructions'], list) else 0
        print(f"📋 Extracted {count} instruction rules")
        return instructions
    
    def extract_verified_queries(self, model: Dict[str, Any]) -> Dict[str, Any]:
        """Extract verified queries"""
        verified_queries = {
            'verified_queries': model.get('verified_queries', [])
        }
        
        count = len(verified_queries['verified_queries']) if isinstance(verified_queries['verified_queries'], list) else 0
        print(f"✅ Extracted {count} verified queries")
        return verified_queries
    
    def format_sql_as_literal(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Format SQL fields as literal block scalars for better readability"""
        if 'verified_queries' not in data:
            return data
        
        queries = data.get('verified_queries', [])
        if not isinstance(queries, list):
            return data
        
        for query in queries:
            if 'sql' in query and isinstance(query['sql'], str):
                # Normalize escaped newlines and strip trailing whitespace
                sql = query['sql'].replace('\\n', '\n')
                lines = [line.rstrip() for line in sql.splitlines()]
                sql_clean = '\n'.join(lines).strip() + '\n'
                
                if HAS_RUAMEL:
                    query['sql'] = LiteralScalarString(sql_clean)
                else:
                    # For PyYAML, use a custom LiteralStr class
                    query['sql'] = LiteralStr(sql_clean)
        
        return data
    
    def save_yaml(self, data: Dict[str, Any], filename: str):
        """Save data to YAML file with proper SQL formatting"""
        output_path = self.output_dir / filename
        
        # Format SQL as literal blocks for verified_queries
        if filename == 'verified_queries.yaml':
            data = self.format_sql_as_literal(data)
        
        if HAS_RUAMEL:
            # Use ruamel.yaml for best formatting
            ryaml = YAML()
            ryaml.preserve_quotes = True
            ryaml.width = 120
            ryaml.indent(mapping=2, sequence=2, offset=0)
            ryaml.default_flow_style = False
            
            with open(output_path, 'w', encoding='utf-8') as f:
                ryaml.dump(data, f)
        else:
            # Fall back to PyYAML
            with open(output_path, 'w', encoding='utf-8') as f:
                yaml.dump(
                    data,
                    f,
                    default_flow_style=False,
                    sort_keys=False,
                    allow_unicode=True,
                    width=120
                )
        
        print(f"💾 Saved: {output_path}")
    
    def create_readme(self, model: Dict[str, Any]):
        """Create README documentation"""
        readme_content = f"""# Modular Semantic Model Structure

**Model:** {model.get('name', 'Unknown')}  
**Created:** {datetime.now().strftime('%Y-%m-%d')}  
**Description:** {model.get('description', 'No description')}

---

## 📁 File Structure

This semantic model is split into three modular components:

### 1. `schema.yaml` - Table Schemas
- **Purpose:** Define all tables, dimensions, measures, and time dimensions
- **Update when:** Adding/modifying tables or columns
- **Size:** ~{len(str(model.get('tables', [])))} characters

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
python -c "import yaml; yaml.safe_load(open('orchestrator/semantic_models/semantic_merged.yaml'))"

# Deploy to test stage
python scripts/deploy_semantic_model.py --stage TEST_SEMANTIC_MODELS
```

---

## 📚 Documentation

- [Cortex Analyst Documentation](https://docs.snowflake.com/en/user-guide/snowflake-cortex/cortex-analyst)
- [Semantic Model Guide](../../guides/02_STEP_2.2_SEMANTIC_MODEL_AUTOMATION.md)
- [DIA Implementation Plan](../../DIA_V2_IMPLEMENTATION_PLAN.md)

---

**Last Split:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**Original File:** {self.input_file}
"""
        
        readme_path = self.output_dir / 'README.md'
        with open(readme_path, 'w', encoding='utf-8') as f:
            f.write(readme_content)
        
        print(f"📖 Created: {readme_path}")
    
    def split(self):
        """Main splitting logic"""
        print("\n" + "="*70)
        print("🔧 SEMANTIC MODEL SPLITTER")
        print("="*70 + "\n")
        
        # Show formatting method
        if HAS_RUAMEL:
            print("✅ Using ruamel.yaml for optimal SQL formatting")
        else:
            print("ℹ️  Using PyYAML (install ruamel.yaml for better formatting)")
        print()
        
        # Backup original file
        backup_path = self.input_file.parent / f"{self.input_file.stem}_backup{self.input_file.suffix}"
        if not backup_path.exists():
            import shutil
            shutil.copy2(self.input_file, backup_path)
            print(f"💾 Backup created: {backup_path}\n")
        
        # Load model
        model = self.load_model()
        
        print()
        
        # Extract components
        schema = self.extract_schema(model)
        instructions = self.extract_instructions(model)
        verified_queries = self.extract_verified_queries(model)
        
        print()
        
        # Save files
        self.save_yaml(schema, 'schema.yaml')
        self.save_yaml(instructions, 'instructions.yaml')
        self.save_yaml(verified_queries, 'verified_queries.yaml')
        
        # Count formatted SQL queries
        sql_count = len([q for q in verified_queries.get('verified_queries', []) if 'sql' in q])
        if sql_count > 0:
            print(f"✨ Formatted {sql_count} SQL queries as literal blocks for readability")
        
        print()
        
        # Create README
        self.create_readme(model)
        
        print("\n" + "="*70)
        print("✅ SPLITTING COMPLETE!")
        print("="*70)
        print(f"\n📁 Output directory: {self.output_dir}")
        print(f"📊 Files created:")
        print(f"   - schema.yaml")
        print(f"   - instructions.yaml")
        print(f"   - verified_queries.yaml (SQL in literal block format)")
        print(f"   - README.md")
        print(f"\n🚀 Next steps:")
        print(f"   1. Review the generated files")
        print(f"   2. Run: python scripts/merge_semantic_models.py")
        print(f"   3. Deploy: python scripts/deploy_semantic_model.py")
        print()


def main():
    parser = argparse.ArgumentParser(
        description='Split semantic model into modular components',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        '--input',
        '-i',
        default='data-layer/semantic-models/semantic.yaml',
        help='Input semantic model file (default: data-layer/semantic-models/semantic.yaml)'
    )
    
    parser.add_argument(
        '--output-dir',
        '-o',
        default='orchestrator/semantic_models',
        help='Output directory for split files (default: orchestrator/semantic_models)'
    )
    
    args = parser.parse_args()
    
    # Create splitter and run
    splitter = SemanticModelSplitter(args.input, args.output_dir)
    
    try:
        splitter.split()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
