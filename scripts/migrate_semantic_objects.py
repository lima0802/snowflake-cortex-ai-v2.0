
import os
from dotenv import load_dotenv
from snowflake.snowpark import Session

# Load environment variables
load_dotenv()

def get_session():
    connection_parameters = {
        "account": os.getenv("SNOWFLAKE_ACCOUNT"),
        "user": os.getenv("SNOWFLAKE_USER"),
        "password": os.getenv("SNOWFLAKE_PASSWORD"),
        "role": os.getenv("SNOWFLAKE_ROLE"),
        "warehouse": os.getenv("SNOWFLAKE_WAREHOUSE"),
        "database": os.getenv("SNOWFLAKE_DATABASE"),
        "schema": os.getenv("SNOWFLAKE_SCHEMA")
    }
    return Session.builder.configs(connection_parameters).create()

def migrate_semantic_objects():
    """
    Migrates SEMANTIC_MODELS and SEMANTIC_FILES stages to CORTEX_ANALYTICS_ORCHESTRATOR schema
    """
    print("Starting Semantic Objects Migration...")
    session = get_session()
    
    try:
        database = os.getenv("SNOWFLAKE_DATABASE")
        target_schema = "CORTEX_ANALYTICS_ORCHESTRATOR"
        
        # Get current schema to check where objects currently exist
        current_schema = session.get_current_schema()
        print(f"\nCurrent context: {database}.{current_schema}")
        print(f"Target schema: {database}.{target_schema}")
        
        # 1. Ensure target schema exists
        print(f"\n[Step 1] Ensuring schema {target_schema} exists...")
        session.sql(f"CREATE SCHEMA IF NOT EXISTS {database}.{target_schema}").collect()
        print(f"   [OK] Schema {target_schema} is ready")
        
        # 2. Switch to target schema
        print(f"\n[Step 2] Switching to {target_schema} schema...")
        session.sql(f"USE SCHEMA {database}.{target_schema}").collect()
        print(f"   [OK] Now using {target_schema}")
        
        # 3. Create/verify SEMANTIC_FILES stage in target schema
        print(f"\n[Step 3] Creating SEMANTIC_FILES stage in {target_schema}...")
        session.sql(f"CREATE STAGE IF NOT EXISTS {database}.{target_schema}.SEMANTIC_FILES").collect()
        session.sql(f"ALTER STAGE {database}.{target_schema}.SEMANTIC_FILES SET DIRECTORY = (ENABLE = TRUE)").collect()
        print(f"   [OK] Stage SEMANTIC_FILES created/verified")
        
        # 4. Check if semantic.yaml exists in old location and copy if needed
        print(f"\n[Step 4] Checking for existing semantic.yaml files...")
        
        # List files in current schema's SEMANTIC_FILES (if it exists)
        try:
            old_files = session.sql(f"LIST @{database}.{current_schema}.SEMANTIC_FILES").collect()
            if old_files:
                print(f"   Found {len(old_files)} file(s) in {current_schema}.SEMANTIC_FILES")
                print(f"   Note: These files will remain in the old location.")
                print(f"   The deployment script will upload fresh files to the new location.")
        except Exception as e:
            print(f"   No existing files found in old location (this is normal)")
        
        # 5. Upload semantic.yaml to new location
        print(f"\n[Step 5] Uploading semantic.yaml to new location...")
        local_file = "config/semantic.yaml"
        put_result = session.file.put(
            local_file, 
            f"@{database}.{target_schema}.SEMANTIC_FILES", 
            auto_compress=False, 
            overwrite=True
        )
        print(f"   [OK] Upload status: {put_result[0].status}")
        
        # 6. Refresh stage
        session.sql(f"ALTER STAGE {database}.{target_schema}.SEMANTIC_FILES REFRESH").collect()
        print(f"   [OK] Stage refreshed")
        
        # 7. Verify upload
        print(f"\n[Step 6] Verifying files in new location...")
        new_files = session.sql(f"LIST @{database}.{target_schema}.SEMANTIC_FILES").collect()
        print(f"   [OK] Found {len(new_files)} file(s) in {target_schema}.SEMANTIC_FILES:")
        for file in new_files:
            print(f"      - {file['name']}")
        
        # 8. Summary
        print(f"\n{'='*60}")
        print(f"MIGRATION COMPLETE!")
        print(f"{'='*60}")
        print(f"\nSemantic objects are now in:")
        print(f"   Database: {database}")
        print(f"   Schema: {target_schema}")
        print(f"   Stage: SEMANTIC_FILES")
        print(f"   File: semantic.yaml")
        
        print(f"\n[NEXT STEPS]:")
        print(f"1. Go to Snowsight: AI & ML -> Agents")
        print(f"2. Edit your Agent's Cortex Analyst tool")
        print(f"3. Update the semantic model reference to:")
        print(f"   - Database: {database}")
        print(f"   - Schema: {target_schema}")
        print(f"   - Stage: SEMANTIC_FILES")
        print(f"   - File: semantic.yaml")
        
        print(f"\n[TIP]: The deployment script will now automatically")
        print(f"   upload to this new location going forward.")
        
    except Exception as e:
        print(f"\n[ERROR] Error during migration: {e}")
        import traceback
        traceback.print_exc()
    finally:
        session.close()

if __name__ == "__main__":
    migrate_semantic_objects()
