
import os
from dotenv import load_dotenv
from snowflake.snowpark import Session

# Load environment variables from .env
load_dotenv()

def test_connection():
    # 1. Prepare Connection Parameters
    connection_parameters = {
        "account": os.getenv("SNOWFLAKE_ACCOUNT"),
        "user": os.getenv("SNOWFLAKE_USER"),
        "password": os.getenv("SNOWFLAKE_PASSWORD"),
        "role": os.getenv("SNOWFLAKE_ROLE"),
        "warehouse": os.getenv("SNOWFLAKE_WAREHOUSE"),
        "database": os.getenv("SNOWFLAKE_DATABASE"),
        "schema": os.getenv("SNOWFLAKE_SCHEMA")
    }

    print("\nTesting Connection with parameters:")
    print(f"   Account: {connection_parameters['account']}")
    print(f"   User:    {connection_parameters['user']}")
    print(f"   Role:    {connection_parameters['role']}")
    print(f"   DB/Sch:  {connection_parameters['database']}.{connection_parameters['schema']}")

    # 2. Create Session
    try:
        session = Session.builder.configs(connection_parameters).create()
        print("\nCONNECTION SUCCESSFUL!")
        
        # 3. Verify Context
        current_db = session.get_current_database()
        current_schema = session.get_current_schema()
        print(f"   Connected to: {current_db}.{current_schema}")
        
    except Exception as e:
        print("\nCONNECTION FAILED")
        print(e)
    finally:
        if 'session' in locals():
            session.close()

if __name__ == "__main__":
    test_connection()
