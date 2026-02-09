
import os
import sys
from dotenv import load_dotenv
from snowflake.snowpark import Session

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

def inspect():
    print("Inspecting Agent Objects...")
    session = get_session()
    
    try:
        # Check current schema objects
        print(f"\nObjects in {session.get_current_database()}.{session.get_current_schema()}:")
        # specific command to show Cortex Agents if they exist as standard objects?
        # Trying SHOW CORTEX AGENTS or SHOW AGENTS
        try:
            res = session.sql("SHOW AGENTS").collect()
            for r in res:
                print(r)
        except Exception as e:
            print(f"SHOW AGENTS failed: {e}")

        # Also check SNOWFLAKE_INTELLIGENCE if accessible
        try:
            print("\nAttempting to show agents in SNOWFLAKE_INTELLIGENCE.AGENTS...")
            session.use_schema("SNOWFLAKE_INTELLIGENCE.AGENTS")
            res = session.sql("SHOW AGENTS").collect()
            for r in res:
                print(r)
        except Exception as e:
            print(f"Could not access SNOWFLAKE_INTELLIGENCE: {e}")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        session.close()

if __name__ == "__main__":
    inspect()
