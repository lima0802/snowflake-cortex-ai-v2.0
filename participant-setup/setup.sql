-- Multi-User Lab Setup Script
-- This script is designed for hands-on lab environments where multiple users
-- share a sandbox account with individual schemas

-- Step 1: Use the lab role (assigned by instructor)
USE ROLE SNOWCAMP;
USE DATABASE SNOWCAMP_DB;
USE WAREHOUSE SNOWCAMP_WHS;

-- Note: You also have access to SNOWFLAKE_INTELLIGENCE database for creating agents
-- USE DATABASE SNOWFLAKE_INTELLIGENCE;
-- USE SCHEMA AGENTS;

-- Step 2: Create your own schema (replace 'USER01' with your unique identifier)
-- Suggested naming: USER01, USER02, or use your initials like JD_SCHEMA
CREATE SCHEMA IF NOT EXISTS USER01;
USE SCHEMA USER01;

-- Step 3: Create your document stage
CREATE OR REPLACE STAGE docs 
  ENCRYPTION = (TYPE = 'SNOWFLAKE_SSE') 
  DIRECTORY = (ENABLE = true);

-- Step 4: Create your semantic files stage
CREATE OR REPLACE STAGE semantic_files 
  ENCRYPTION = (TYPE = 'SNOWFLAKE_SSE') 
  DIRECTORY = (ENABLE = true);

-- (Optional) Step 5: Create your email procedure (uses shared integration)
CREATE OR REPLACE PROCEDURE send_email(
    recipient_email VARCHAR,
    subject VARCHAR,
    body VARCHAR
)
RETURNS VARCHAR
LANGUAGE PYTHON
RUNTIME_VERSION = '3.12'
PACKAGES = ('snowflake-snowpark-python')
HANDLER = 'send_email'
AS
$$
def send_email(session, recipient_email, subject, body):
    try:
        # Escape single quotes in the body
        escaped_body = body.replace("'", "''")
        
        # Execute the system procedure call using shared integration
        session.sql(f"""
            CALL SYSTEM$SEND_EMAIL(
                'email_integration_shared',
                '{recipient_email}',
                '{subject}',
                '{escaped_body}',
                'text/html'
            )
        """).collect()
        
        return "Email sent successfully"
    except Exception as e:
        return f"Error sending email: {str(e)}"
$$;

/* Next Step: Upload Files 

-- Method 1: Using Snowsight (Recommended)**

-- **Upload Document Files**
   - Navigate to: Data → Databases → SNOWCAMP_DB → [Your Schema] → Stages
   - Click on the `docs` stage
   - Click "Upload Files"
   - Select ALL files from the `docs/` folder in your downloaded repository
   - Wait for upload to complete

2. **Upload Semantic Files**
   - Click on the `semantic_files` stage
   - Upload `semantic.yaml` from the repository root */

-- Quick verification commands (run these after file upload)
SELECT * FROM DIRECTORY('@docs');
SELECT * FROM DIRECTORY('@semantic_files');

-- All good? All good!
