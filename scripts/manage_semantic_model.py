#!/usr/bin/env python3
"""
Semantic Model Manager - DIA v2.0
==================================
Comprehensive automation tool for managing Snowflake semantic models.

Features:
- Validate YAML syntax and schema
- Update model sections programmatically
- Deploy to Snowflake stages
- Version control and diffing
- CI/CD friendly (exit codes, logging, parameters)

Usage:
    # Validate semantic model
    python scripts/manage_semantic_model.py validate

    # Deploy to Snowflake
    python scripts/manage_semantic_model.py deploy

    # Update model description
    python scripts/manage_semantic_model.py update --description "New description"

    # Add a new table
    python scripts/manage_semantic_model.py add-table --name MY_TABLE --database DEV --schema APP

    # Verify deployment
    python scripts/manage_semantic_model.py verify

    # Show diff between local and deployed
    python scripts/manage_semantic_model.py diff
"""

import os
import sys
import yaml
import argparse
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, List
from dotenv import load_dotenv
from snowflake.snowpark import Session

# Load environment variables
load_dotenv()

# Constants
SEMANTIC_FILE = "data-layer/semantic-models/semantic.yaml"
STAGE_NAME = os.getenv("SNOWFLAKE_SEMANTIC_STAGE", "SEMANTIC_MODELS")
BACKUP_DIR = "data-layer/semantic-models/backups"


class SemanticModelManager:
    """Manages semantic model operations"""
    
    def __init__(self, file_path: str = SEMANTIC_FILE):
        self.file_path = file_path
        self.model_data: Optional[Dict[str, Any]] = None
        
    def load(self) -> Dict[str, Any]:
        """Load semantic model from YAML file"""
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                self.model_data = yaml.safe_load(f)
            return self.model_data
        except FileNotFoundError:
            print(f"❌ Error: File not found: {self.file_path}")
            sys.exit(1)
        except yaml.YAMLError as e:
            print(f"❌ YAML Syntax Error: {e}")
            sys.exit(1)
    
    def save(self, backup: bool = True) -> None:
        """Save semantic model to YAML file"""
        if backup:
            self._create_backup()
        
        try:
            with open(self.file_path, 'w', encoding='utf-8') as f:
                yaml.safe_dump(
                    self.model_data,
                    f,
                    default_flow_style=False,
                    allow_unicode=True,
                    sort_keys=False,
                    width=100
                )
            print(f"✅ Saved: {self.file_path}")
        except Exception as e:
            print(f"❌ Error saving file: {e}")
            sys.exit(1)
    
    def _create_backup(self) -> None:
        """Create timestamped backup of current file"""
        os.makedirs(BACKUP_DIR, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = f"{BACKUP_DIR}/semantic_{timestamp}.yaml"
        
        try:
            import shutil
            shutil.copy2(self.file_path, backup_file)
            print(f"📦 Backup created: {backup_file}")
        except Exception as e:
            print(f"⚠️  Warning: Could not create backup: {e}")
    
    def validate(self) -> bool:
        """Validate semantic model structure"""
        print("\n🔍 Validating Semantic Model...")
        
        if not self.model_data:
            self.load()
        
        errors = []
        
        # Required top-level fields
        required_fields = ['name', 'description', 'tables']
        for field in required_fields:
            if field not in self.model_data:
                errors.append(f"Missing required field: {field}")
        
        # Validate tables
        if 'tables' in self.model_data:
            tables = self.model_data.get('tables', [])
            if not isinstance(tables, list):
                errors.append("'tables' must be a list")
            else:
                for i, table in enumerate(tables):
                    if not isinstance(table, dict):
                        errors.append(f"Table {i} must be a dictionary")
                        continue
                    
                    # Check required table fields
                    if 'name' not in table:
                        errors.append(f"Table {i} missing 'name' field")
                    if 'base_table' not in table:
                        errors.append(f"Table {i} ({table.get('name', 'unknown')}) missing 'base_table' field")
        
        if errors:
            print("❌ Validation Failed:")
            for error in errors:
                print(f"   - {error}")
            return False
        
        print("✅ Validation Passed")
        print(f"   Model: {self.model_data.get('name')}")
        print(f"   Tables: {len(self.model_data.get('tables', []))}")
        return True
    
    def update_description(self, new_description: str) -> None:
        """Update model description"""
        if not self.model_data:
            self.load()
        
        old_description = self.model_data.get('description', '')
        self.model_data['description'] = new_description
        
        print(f"\n📝 Updated Description:")
        print(f"   Old: {old_description[:50]}...")
        print(f"   New: {new_description[:50]}...")
        
        self.save()
    
    def add_table(self, name: str, database: str, schema: str, table: str, 
                  description: str = "") -> None:
        """Add a new table to the semantic model"""
        if not self.model_data:
            self.load()
        
        # Check if table already exists
        tables = self.model_data.get('tables', [])
        for t in tables:
            if t.get('name') == name:
                print(f"⚠️  Table '{name}' already exists. Use update instead.")
                sys.exit(1)
        
        # Create new table entry
        new_table = {
            'name': name,
            'description': description or f"Table {name}",
            'base_table': {
                'database': database,
                'schema': schema,
                'table': table
            },
            'dimensions': [],
            'time_dimensions': [],
            'measures': []
        }
        
        tables.append(new_table)
        self.model_data['tables'] = tables
        
        print(f"✅ Added table: {name}")
        print(f"   Base: {database}.{schema}.{table}")
        
        self.save()
    
    def get_table(self, table_name: str) -> Optional[Dict[str, Any]]:
        """Get table definition by name"""
        if not self.model_data:
            self.load()
        
        for table in self.model_data.get('tables', []):
            if table.get('name') == table_name:
                return table
        return None
    
    def update_table_description(self, table_name: str, description: str) -> None:
        """Update description for a specific table"""
        if not self.model_data:
            self.load()
        
        table = self.get_table(table_name)
        if not table:
            print(f"❌ Table '{table_name}' not found")
            sys.exit(1)
        
        table['description'] = description
        print(f"✅ Updated description for table: {table_name}")
        self.save()
    
    def list_tables(self) -> List[str]:
        """List all table names in the model"""
        if not self.model_data:
            self.load()
        
        return [t.get('name') for t in self.model_data.get('tables', [])]
    
    def get_stats(self) -> Dict[str, Any]:
        """Get model statistics"""
        if not self.model_data:
            self.load()
        
        stats = {
            'name': self.model_data.get('name'),
            'tables': len(self.model_data.get('tables', [])),
            'total_dimensions': 0,
            'total_measures': 0,
            'total_time_dimensions': 0
        }
        
        for table in self.model_data.get('tables', []):
            stats['total_dimensions'] += len(table.get('dimensions', []))
            stats['total_measures'] += len(table.get('measures', []))
            stats['total_time_dimensions'] += len(table.get('time_dimensions', []))
        
        return stats


class SnowflakeDeployer:
    """Handles Snowflake deployment operations"""
    
    def __init__(self):
        self.session: Optional[Session] = None
    
    def connect(self) -> Session:
        """Create Snowflake session"""
        if self.session:
            return self.session
        
        connection_parameters = {
            "account": os.getenv("SNOWFLAKE_ACCOUNT"),
            "user": os.getenv("SNOWFLAKE_USER"),
            "password": os.getenv("SNOWFLAKE_PASSWORD"),
            "role": os.getenv("SNOWFLAKE_ROLE"),
            "warehouse": os.getenv("SNOWFLAKE_WAREHOUSE"),
            "database": os.getenv("SNOWFLAKE_DATABASE"),
            "schema": os.getenv("SNOWFLAKE_SCHEMA")
        }
        
        try:
            self.session = Session.builder.configs(connection_parameters).create()
            return self.session
        except Exception as e:
            print(f"❌ Snowflake Connection Error: {e}")
            sys.exit(1)
    
    def deploy(self, file_path: str) -> bool:
        """Deploy semantic model to Snowflake stage"""
        print("\n🚀 Deploying Semantic Model to Snowflake...")
        
        session = self.connect()
        
        try:
            # 1. Ensure stage exists
            print(f"📦 Ensuring stage exists: @{STAGE_NAME}")
            session.sql(f"CREATE STAGE IF NOT EXISTS {STAGE_NAME}").collect()
            session.sql(f"ALTER STAGE {STAGE_NAME} SET DIRECTORY = (ENABLE = TRUE)").collect()
            
            # 2. Upload file
            print(f"📤 Uploading: {file_path}")
            put_result = session.file.put(
                file_path,
                f"@{STAGE_NAME}",
                auto_compress=False,
                overwrite=True
            )
            
            status = put_result[0].status
            print(f"   Status: {status}")
            
            # 3. Refresh stage
            session.sql(f"ALTER STAGE {STAGE_NAME} REFRESH").collect()
            
            # 4. Verify upload
            files = session.sql(f"LIST @{STAGE_NAME}").collect()
            deployed_file = None
            for file in files:
                if 'semantic.yaml' in file['name']:
                    deployed_file = file
                    break
            
            if deployed_file:
                size_mb = deployed_file['size'] / (1024 * 1024)
                print(f"✅ Deployment Successful!")
                print(f"   File: {deployed_file['name']}")
                print(f"   Size: {size_mb:.2f} MB")
                print(f"   Modified: {deployed_file['last_modified']}")
                return True
            else:
                print("❌ Deployment verification failed")
                return False
                
        except Exception as e:
            print(f"❌ Deployment Error: {e}")
            return False
        finally:
            if self.session:
                self.session.close()
    
    def verify(self) -> bool:
        """Verify deployed semantic model exists"""
        print("\n🔍 Verifying Deployment...")
        
        session = self.connect()
        
        try:
            files = session.sql(f"LIST @{STAGE_NAME}").collect()
            found = False
            
            for file in files:
                if 'semantic.yaml' in file['name']:
                    found = True
                    size_mb = file['size'] / (1024 * 1024)
                    print(f"✅ Found: {file['name']}")
                    print(f"   Size: {size_mb:.2f} MB")
                    print(f"   Modified: {file['last_modified']}")
            
            if not found:
                print(f"❌ semantic.yaml not found in @{STAGE_NAME}")
                return False
            
            return True
            
        except Exception as e:
            print(f"❌ Verification Error: {e}")
            return False
        finally:
            if self.session:
                self.session.close()
    
    def list_versions(self) -> List[Dict[str, Any]]:
        """List all versions in the stage"""
        session = self.connect()
        
        try:
            files = session.sql(f"LIST @{STAGE_NAME}").collect()
            versions = []
            
            for file in files:
                if file['name'].endswith('.yaml'):
                    versions.append({
                        'name': file['name'],
                        'size_mb': file['size'] / (1024 * 1024),
                        'modified': file['last_modified']
                    })
            
            return versions
            
        finally:
            if self.session:
                self.session.close()


def main():
    parser = argparse.ArgumentParser(
        description="Semantic Model Manager - Automate semantic.yaml updates and deployments",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Validate model
  python scripts/manage_semantic_model.py validate

  # Deploy to Snowflake
  python scripts/manage_semantic_model.py deploy

  # Update description
  python scripts/manage_semantic_model.py update-description "New description text"

  # Add new table
  python scripts/manage_semantic_model.py add-table MY_TABLE \\
      --database DEV_DB --schema MY_SCHEMA --table MY_TABLE

  # Show model stats
  python scripts/manage_semantic_model.py stats

  # Verify deployment
  python scripts/manage_semantic_model.py verify
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Command to execute')
    
    # Validate command
    subparsers.add_parser('validate', help='Validate semantic model YAML')
    
    # Deploy command
    subparsers.add_parser('deploy', help='Deploy model to Snowflake')
    
    # Verify command
    subparsers.add_parser('verify', help='Verify deployed model exists')
    
    # Stats command
    subparsers.add_parser('stats', help='Show model statistics')
    
    # List tables command
    subparsers.add_parser('list-tables', help='List all tables in model')
    
    # Update description command
    update_desc = subparsers.add_parser('update-description', help='Update model description')
    update_desc.add_argument('description', help='New description text')
    
    # Add table command
    add_table = subparsers.add_parser('add-table', help='Add new table to model')
    add_table.add_argument('name', help='Table name (semantic model name)')
    add_table.add_argument('--database', required=True, help='Database name')
    add_table.add_argument('--schema', required=True, help='Schema name')
    add_table.add_argument('--table', required=True, help='Physical table name')
    add_table.add_argument('--description', default='', help='Table description')
    
    # Update table description
    update_table = subparsers.add_parser('update-table-description', help='Update table description')
    update_table.add_argument('table_name', help='Table name')
    update_table.add_argument('description', help='New description')
    
    # List versions
    subparsers.add_parser('list-versions', help='List deployed versions')
    
    # Validate and deploy (CI/CD workflow)
    subparsers.add_parser('ci-deploy', help='Validate then deploy (CI/CD use)')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    # Execute commands
    manager = SemanticModelManager()
    deployer = SnowflakeDeployer()
    
    try:
        if args.command == 'validate':
            success = manager.validate()
            sys.exit(0 if success else 1)
        
        elif args.command == 'deploy':
            success = deployer.deploy(SEMANTIC_FILE)
            sys.exit(0 if success else 1)
        
        elif args.command == 'verify':
            success = deployer.verify()
            sys.exit(0 if success else 1)
        
        elif args.command == 'stats':
            stats = manager.get_stats()
            print("\n📊 Semantic Model Statistics:")
            print(f"   Name: {stats['name']}")
            print(f"   Tables: {stats['tables']}")
            print(f"   Total Dimensions: {stats['total_dimensions']}")
            print(f"   Total Measures: {stats['total_measures']}")
            print(f"   Total Time Dimensions: {stats['total_time_dimensions']}")
        
        elif args.command == 'list-tables':
            tables = manager.list_tables()
            print(f"\n📋 Tables ({len(tables)}):")
            for table in tables:
                print(f"   - {table}")
        
        elif args.command == 'update-description':
            manager.update_description(args.description)
        
        elif args.command == 'add-table':
            manager.add_table(
                name=args.name,
                database=args.database,
                schema=args.schema,
                table=args.table,
                description=args.description
            )
        
        elif args.command == 'update-table-description':
            manager.update_table_description(args.table_name, args.description)
        
        elif args.command == 'list-versions':
            versions = deployer.list_versions()
            print(f"\n📦 Deployed Versions ({len(versions)}):")
            for v in versions:
                print(f"   - {v['name']} ({v['size_mb']:.2f} MB) - {v['modified']}")
        
        elif args.command == 'ci-deploy':
            # CI/CD workflow: validate then deploy
            print("🔄 CI/CD Deployment Workflow")
            
            # Step 1: Validate
            if not manager.validate():
                print("❌ Validation failed - aborting deployment")
                sys.exit(1)
            
            # Step 2: Deploy
            if not deployer.deploy(SEMANTIC_FILE):
                print("❌ Deployment failed")
                sys.exit(1)
            
            # Step 3: Verify
            if not deployer.verify():
                print("❌ Verification failed")
                sys.exit(1)
            
            print("\n✅ CI/CD Deployment Complete!")
            sys.exit(0)
    
    except KeyboardInterrupt:
        print("\n\n⚠️  Operation cancelled by user")
        sys.exit(130)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
