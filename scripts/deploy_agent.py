
import os
from dotenv import load_dotenv
import snowflake.connector

# Load environment variables
load_dotenv()

def create_agent():
    """
    Creates or replaces the Direct Marketing Analytics Agent in Snowflake
    by executing the create_agent.sql script
    """
    print("="*60)
    print("SNOWFLAKE AGENT DEPLOYMENT")
    print("="*60)
    
    # Create connection using snowflake.connector (supports multi-statement)
    conn = snowflake.connector.connect(
        account=os.getenv("SNOWFLAKE_ACCOUNT"),
        user=os.getenv("SNOWFLAKE_USER"),
        password=os.getenv("SNOWFLAKE_PASSWORD"),
        role=os.getenv("SNOWFLAKE_ROLE"),
        warehouse=os.getenv("SNOWFLAKE_WAREHOUSE"),
        database=os.getenv("SNOWFLAKE_DATABASE"),
        schema=os.getenv("SNOWFLAKE_SCHEMA")
    )
    
    try:
        # Read the SQL file
        sql_file = "scripts/create_agent.sql"
        print(f"\n[Step 1] Reading SQL script: {sql_file}")
        
        with open(sql_file, 'r', encoding='utf-8') as f:
            sql_content = f.read()
        
        print(f"   [OK] SQL script loaded ({len(sql_content)} characters)")
        
        # Execute the SQL using execute_string (handles multi-statement)
        print(f"\n[Step 2] Setting up Snowflake context...")
        
        cursor = conn.cursor()
        
        # Execute USE statements first
        cursor.execute("USE ROLE SYSADMIN")
        cursor.execute("USE WAREHOUSE TEST")
        cursor.execute("USE DATABASE PLAYGROUND_LM")
        cursor.execute("USE SCHEMA CORTEX_ANALYTICS_ORCHESTRATOR")
        
        print(f"   [OK] Context set: PLAYGROUND_LM.CORTEX_ANALYTICS_ORCHESTRATOR")
        
        # Find the CREATE AGENT statement (starts at line 10)
        lines = sql_content.split('\n')
        create_agent_start = None
        for i, line in enumerate(lines):
            if line.strip().startswith('CREATE OR REPLACE AGENT'):
                create_agent_start = i
                break
        
        if create_agent_start is None:
            raise Exception("Could not find CREATE OR REPLACE AGENT statement in SQL file")
        
        # Get everything from CREATE AGENT onwards
        create_agent_sql = '\n'.join(lines[create_agent_start:])
        
        print(f"\n[Step 3] Executing CREATE OR REPLACE AGENT command...")
        print(f"   Target: PLAYGROUND_LM.CORTEX_ANALYTICS_ORCHESTRATOR.DIRECT_MARKETING_ANALYTICS_AGENT")
        
        # Execute the CREATE AGENT statement
        # Note: We need to execute this as a single statement
        cursor.execute(create_agent_sql)
        
        print(f"   [OK] Agent created successfully!")
        
        # Verify the agent exists
        print(f"\n[Step 4] Verifying agent creation...")
        verify_sql = """
        SHOW AGENTS LIKE 'DIRECT_MARKETING_ANALYTICS_AGENT' 
        IN SCHEMA PLAYGROUND_LM.CORTEX_ANALYTICS_ORCHESTRATOR
        """
        cursor.execute(verify_sql)
        result = cursor.fetchall()
        
        if result:
            print(f"   [OK] Agent verified!")
            print(f"   Name: {result[0][1]}")  # name column
            print(f"   Created on: {result[0][0]}")  # created_on column
        else:
            print(f"   [WARNING] Could not verify agent (but creation command succeeded)")
        
        # Summary
        print(f"\n{'='*60}")
        print(f"DEPLOYMENT COMPLETE!")
        print(f"{'='*60}")
        print(f"\nAgent Details:")
        print(f"   Name: DIRECT_MARKETING_ANALYTICS_AGENT")
        print(f"   Database: PLAYGROUND_LM")
        print(f"   Schema: CORTEX_ANALYTICS_ORCHESTRATOR")
        print(f"   Model: Claude Sonnet 4.5")
        
        print(f"\nTools Configured:")
        print(f"   1. Email_Performance_Analytics (Cortex Analyst)")
        print(f"      - Semantic Model: @PLAYGROUND_LM.CORTEX_ANALYTICS_ORCHESTRATOR.SEMANTIC_FILES/semantic.yaml")
        print(f"      - Warehouse: TEST")
        print(f"   2. Benchmark_Intelligence_Base (Cortex Search)")
        print(f"      - Search Service: DEV_MARCOM_DB.APP_DIRECTMARKETING.CORTEX_SFMC_BENCHMARK_SEARCH")
        
        print(f"\n[NEXT STEPS]:")
        print(f"1. Go to Snowsight: AI & ML -> Agents")
        print(f"2. Find 'Direct Marketing Analytics Agent'")
        print(f"3. Test with sample questions:")
        print(f"   - 'What is the YTD click rate?'")
        print(f"   - 'Show me campaign performance for EX30'")
        print(f"   - 'How does Germany compare to EMEA average?'")
        
        cursor.close()
        
    except Exception as e:
        print(f"\n[ERROR] Failed to create agent: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        conn.close()
    
    return True

if __name__ == "__main__":
    success = create_agent()
    exit(0 if success else 1)
