"""
Merge Modular Semantic Model Components
========================================

This script merges modular semantic model files into a single
complete model ready for deployment to Snowflake.

Merges:
1. schema/_metadata.yaml - Model name and description
2. schema/*.yaml - All table definitions (6 tables)
3. instructions.yaml - Business rules
4. verified_queries.yaml - Example queries

Output:
- orchestrator/semantic_models/semantic_merged.yaml (ready for deployment)

Usage:
    python scripts/merge_semantic_models.py [--input-dir semantic_models/] [--output orchestrator/semantic_models/semantic_merged.yaml]

Author: Li Ma
Date: February 24, 2026
"""

import os
import sys
import yaml
import argparse
from pathlib import Path
from typing import Dict, Any, List
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class SemanticModelMerger:
    """Merge modular semantic model components into single file"""
    
    def __init__(self, input_dir: str, output_file: str):
        self.input_dir = Path(input_dir)
        self.output_file = Path(output_file)
        self.schema_dir = self.input_dir / 'schema'
        self.metadata_file = self.schema_dir / '_metadata.yaml'
        self.instructions_file = self.input_dir / 'instructions.yaml'
        self.verified_queries_file = self.input_dir / 'verified_queries.yaml'
    
    def load_yaml(self, filepath: Path) -> Dict[str, Any]:
        """Load YAML file with error handling"""
        if not filepath.exists():
            print(f"⚠️  File not found: {filepath}")
            return {}
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
            print(f"✅ Loaded: {filepath.name}")
            return data if data is not None else {}
        except yaml.YAMLError as e:
            print(f"❌ YAML error in {filepath.name}: {e}")
            raise
        except Exception as e:
            print(f"❌ Error loading {filepath.name}: {e}")
            raise
    
    def load_table_files(self) -> List[Dict[str, Any]]:
        """Load all table YAML files from schema directory"""
        tables = []
        
        if not self.schema_dir.exists():
            print(f"❌ Schema directory not found: {self.schema_dir}")
            return tables
        
        # Get all YAML files except _metadata.yaml
        table_files = sorted([
            f for f in self.schema_dir.glob('*.yaml')
            if f.name != '_metadata.yaml'
        ])
        
        print(f"📚 Loading {len(table_files)} table files from schema/...")
        for table_file in table_files:
            table_data = self.load_yaml(table_file)
            if table_data:
                tables.append(table_data)
        
        return tables
    
    def validate_schema(self, tables: List[Dict[str, Any]]) -> bool:
        """Validate schema structure"""
        if not tables:
            print("❌ No tables loaded")
            return False
        
        if not isinstance(tables, list):
            print("❌ Tables must be a list")
            return False
        
        print(f"✅ Schema valid: {len(tables)} tables")
        return True
    
    def merge(self) -> Dict[str, Any]:
        """Merge all components into single semantic model"""
        print("\n" + "="*70)
        print("🔄 MERGING SEMANTIC MODEL COMPONENTS")
        print("="*70 + "\n")
        
        # Load metadata
        print("📖 Loading model metadata...")
        metadata = self.load_yaml(self.metadata_file)
        
        # Load all table files
        print()
        tables = self.load_table_files()
        
        # Load instructions and verified queries
        print()
        print("📖 Loading additional components...")
        instructions = self.load_yaml(self.instructions_file)
        verified_queries = self.load_yaml(self.verified_queries_file)
        
        print()
        
        # Validate tables
        if not self.validate_schema(tables):
            raise ValueError("Schema validation failed")
        
        print()
        
        # Build merged model
        print("🔀 Merging components...")
        merged = {
            'name': metadata.get('name', 'Unknown Model'),
            'description': metadata.get('description', ''),
            'tables': tables
        }
        
        # Add instructions if present
        if instructions and 'instructions' in instructions:
            merged['instructions'] = instructions['instructions']
            count = len(instructions['instructions']) if isinstance(instructions['instructions'], list) else len(instructions['instructions'])
            print(f"   ✅ Added {count} instruction rules")
        
        # Add verified queries if present
        if verified_queries and 'verified_queries' in verified_queries:
            merged['verified_queries'] = verified_queries['verified_queries']
            count = len(verified_queries['verified_queries']) if isinstance(verified_queries['verified_queries'], list) else 0
            print(f"   ✅ Added {count} verified queries")
        
        # Add metadata
        merged['metadata'] = {
            'merged_at': datetime.now().isoformat(),
            'merged_from': {
                'schema_metadata': '_metadata.yaml',
                'schema_tables': [f.name for f in sorted(self.schema_dir.glob('*.yaml')) if f.name != '_metadata.yaml'],
                'instructions': 'instructions.yaml',
                'verified_queries': 'verified_queries.yaml'
            },
            'version': '2.0'
        }
        
        print()
        
        # Save merged model
        print(f"💾 Saving merged model: {self.output_file}")
        with open(self.output_file, 'w', encoding='utf-8') as f:
            yaml.dump(
                merged,
                f,
                default_flow_style=False,
                sort_keys=False,
                allow_unicode=True,
                width=120
            )
        
        # Calculate statistics
        file_size = self.output_file.stat().st_size
        
        print()
        print("="*70)
        print("✅ MERGE COMPLETE!")
        print("="*70)
        print(f"\n📊 Merged Model Statistics:")
        print(f"   Name: {merged['name']}")
        print(f"   Tables: {len(merged.get('tables', []))}")
        print(f"   Instructions: {len(merged.get('instructions', []))}")
        print(f"   Verified Queries: {len(merged.get('verified_queries', []))}")
        print(f"   File Size: {file_size:,} bytes ({file_size/1024:.1f} KB)")
        print(f"\n📁 Output: {self.output_file}")
        print(f"\n🚀 Next step:")
        print(f"   Deploy: python scripts/deploy_semantic_model.py")
        print()
        
        return merged


def main():
    parser = argparse.ArgumentParser(
        description='Merge modular semantic model components',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        '--input-dir',
        '-i',
        default='orchestrator/semantic_models',
        help='Directory containing modular files (default: orchestrator/semantic_models)'
    )
    
    parser.add_argument(
        '--output',
        '-o',
        default='orchestrator/semantic_models/semantic_merged.yaml',
        help='Output file for merged model (default: orchestrator/semantic_models/semantic_merged.yaml)'
    )
    
    parser.add_argument(
        '--validate-only',
        '-v',
        action='store_true',
        help='Only validate files without merging'
    )
    
    args = parser.parse_args()
    
    # Create merger and run
    merger = SemanticModelMerger(args.input_dir, args.output)
    
    try:
        if args.validate_only:
            print("\n🔍 Validation mode - checking files only...\n")
            merger.load_yaml(merger.metadata_file)
            tables = merger.load_table_files()
            merger.validate_schema(tables)
            print("\n✅ Validation passed!")
        else:
            merger.merge()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
