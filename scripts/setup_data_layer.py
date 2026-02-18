
import os
import sys
import argparse
from dotenv import load_dotenv
import snowflake.connector
from snowflake.snowpark import Session

# Load environment variables
load_dotenv()

# =====================================================
# Connection helpers
# =====================================================

def get_connector():
    """snowflake.connector – best for executing SQL files with multiple statements."""
    return snowflake.connector.connect(
        account=os.getenv("SNOWFLAKE_ACCOUNT"),
        user=os.getenv("SNOWFLAKE_USER"),
        password=os.getenv("SNOWFLAKE_PASSWORD"),
        role=os.getenv("SNOWFLAKE_ROLE"),
        warehouse=os.getenv("SNOWFLAKE_WAREHOUSE"),
        database=os.getenv("SNOWFLAKE_DATABASE"),
        schema=os.getenv("SNOWFLAKE_SCHEMA"),
    )

def get_session():
    """snowflake.snowpark.Session – best for session.file.put() uploads."""
    params = {
        "account":   os.getenv("SNOWFLAKE_ACCOUNT"),
        "user":      os.getenv("SNOWFLAKE_USER"),
        "password":  os.getenv("SNOWFLAKE_PASSWORD"),
        "role":      os.getenv("SNOWFLAKE_ROLE"),
        "warehouse": os.getenv("SNOWFLAKE_WAREHOUSE"),
        "database":  os.getenv("SNOWFLAKE_DATABASE"),
        "schema":    os.getenv("SNOWFLAKE_SCHEMA"),
    }
    return Session.builder.configs(params).create()

# =====================================================
# SQL file execution helper
# =====================================================

def run_sql_file(cursor, sql_file_path, label):
    """
    Reads a SQL file, strips comment-only lines and blank lines,
    then splits on semicolons and executes each statement individually.
    Uses the same approach as deploy_agent.py (cursor.execute per statement).
    """
    print(f"\n[Running] {label}")
    print(f"   File: {sql_file_path}")

    if not os.path.exists(sql_file_path):
        raise FileNotFoundError(f"SQL file not found: {sql_file_path}")

    with open(sql_file_path, "r", encoding="utf-8") as f:
        raw_sql = f.read()

    # Split on semicolons; skip empty or comment-only fragments
    statements = [s.strip() for s in raw_sql.split(";")]
    executed = 0
    for stmt in statements:
        # Drop blank lines/comment-only blocks
        non_comment_lines = [
            line for line in stmt.splitlines()
            if line.strip() and not line.strip().startswith("--")
        ]
        if not non_comment_lines:
            continue

        try:
            cursor.execute(stmt)
            executed += 1
        except Exception as e:
            # Warn but continue – e.g. SHOW commands that return result sets
            # are harmless; actual DDL errors will surface clearly
            print(f"   [WARN] Statement skipped ({e.__class__.__name__}: {e})")

    print(f"   [OK] {executed} statement(s) executed")

# =====================================================
# Step functions
# =====================================================

def step_views(cursor):
    print("\n" + "="*60)
    print("STEP 1/4 – SEMANTIC VIEWS")
    print("="*60)
    run_sql_file(cursor, "data-layer/views/setup_semantic_views.sql", "Create semantic views")

    # Quick row-count verification
    cursor.execute(
        "SELECT 'VW_SFMC_EMAIL_PERFORMANCE' AS V, COUNT(*) AS N FROM VW_SFMC_EMAIL_PERFORMANCE "
        "UNION ALL SELECT 'VW_CAMPAIGN_SUMMARY', COUNT(*) FROM VW_CAMPAIGN_SUMMARY "
        "UNION ALL SELECT 'VW_MARKET_PERFORMANCE', COUNT(*) FROM VW_MARKET_PERFORMANCE"
    )
    rows = cursor.fetchall()
    for view_name, count in rows:
        status = "[OK]" if count > 0 else "[WARN] 0 rows – check data source mapping"
        print(f"   {status}  {view_name}: {count} row(s)")


def step_benchmarks(cursor):
    print("\n" + "="*60)
    print("STEP 2/4 – BENCHMARK THRESHOLDS")
    print("="*60)
    run_sql_file(cursor, "data-layer/benchmarks/setup_benchmarks.sql", "Load benchmark data")

    cursor.execute("SELECT COUNT(*) FROM BENCHMARK_THRESHOLDS")
    count = cursor.fetchone()[0]
    status = "[OK]" if count >= 6 else f"[WARN] Expected 6 rows, got {count}"
    print(f"   {status}  BENCHMARK_THRESHOLDS: {count} row(s)")


def step_ml_models(cursor):
    print("\n" + "="*60)
    print("STEP 3/4 – ML MODEL PLACEHOLDERS")
    print("="*60)
    run_sql_file(cursor, "data-layer/ml-models/setup_ml_models.sql", "Create ML model registry")

    cursor.execute("SELECT COUNT(*) FROM ML_MODEL_REGISTRY")
    count = cursor.fetchone()[0]
    status = "[OK]" if count >= 3 else f"[WARN] Expected 3 rows, got {count}"
    print(f"   {status}  ML_MODEL_REGISTRY: {count} row(s)")

    cursor.execute("SELECT COUNT(*) FROM VW_FORECAST_TRAINING_DATA")
    forecast_rows = cursor.fetchone()[0]
    print(f"   {'[OK]' if forecast_rows > 0 else '[WARN] 0 rows'}  VW_FORECAST_TRAINING_DATA: {forecast_rows} row(s)")


def step_semantic_model():
    """
    Uploads config/semantic.yaml to the existing semantic stage.
    Uses Snowpark session.file.put() – same as migrate_semantic_objects.py.
    The stage name is read from SNOWFLAKE_SEMANTIC_STAGE env var (default: SEMANTIC_MODELS).
    """
    print("\n" + "="*60)
    print("STEP 4/4 – SEMANTIC MODEL UPLOAD")
    print("="*60)

    stage_name = os.getenv("SNOWFLAKE_SEMANTIC_STAGE", "SEMANTIC_FILES")
    local_file  = "data-layer/semantic-models/semantic.yaml"
    database    = os.getenv("SNOWFLAKE_DATABASE")
    schema      = os.getenv("SNOWFLAKE_SCHEMA")
    stage_path  = f"@{database}.{schema}.{stage_name}"

    if not os.path.exists(local_file):
        raise FileNotFoundError(f"Semantic model file not found: {local_file}")

    print(f"   Stage  : {stage_path}")
    print(f"   File   : {local_file}")

    session = get_session()
    try:
        # Ensure stage exists and has directory enabled
        # (safe to run even if already configured)
        session.sql(f"CREATE STAGE IF NOT EXISTS {stage_path[1:]}").collect()
        session.sql(f"ALTER STAGE {stage_path[1:]} SET DIRECTORY = (ENABLE = TRUE)").collect()

        # Upload the file
        put_result = session.file.put(
            local_file,
            stage_path,
            auto_compress=False,
            overwrite=True,
        )
        upload_status = put_result[0].status
        print(f"   [OK]  Upload status: {upload_status}")

        # Refresh directory metadata and verify
        session.sql(f"ALTER STAGE {stage_path[1:]} REFRESH").collect()
        files = session.sql(f"LIST {stage_path}").collect()
        yaml_files = [f for f in files if "semantic.yaml" in str(f["name"])]
        if yaml_files:
            print(f"   [OK]  File confirmed in stage: {yaml_files[0]['name']}")
        else:
            print(f"   [WARN] File not found in stage listing – check stage manually")

        print(f"\n   Next step in Snowsight:")
        print(f"   AI & ML → Agents → Edit Cortex Analyst tool → point to:")
        print(f"     Database : {database}")
        print(f"     Schema   : {schema}")
        print(f"     Stage    : {stage_name}")
        print(f"     File     : semantic.yaml")

    finally:
        session.close()

# =====================================================
# Main
# =====================================================

STEPS = {
    "views":          step_views,
    "benchmarks":     step_benchmarks,
    "ml-models":      step_ml_models,
    "semantic-model": None,   # handled separately (uses Snowpark)
}

def main():
    parser = argparse.ArgumentParser(
        description="DIA v2.0 – Data Layer Setup (no SnowSQL required)"
    )
    parser.add_argument(
        "--step",
        choices=list(STEPS.keys()) + ["all"],
        default="all",
        help="Which step to run (default: all)",
    )
    args = parser.parse_args()

    run_all = (args.step == "all")
    steps_to_run = list(STEPS.keys()) if run_all else [args.step]

    print("="*60)
    print("DIA v2.0 – DATA LAYER SETUP")
    print("="*60)
    print(f"Account  : {os.getenv('SNOWFLAKE_ACCOUNT')}")
    print(f"Database : {os.getenv('SNOWFLAKE_DATABASE')}")
    print(f"Schema   : {os.getenv('SNOWFLAKE_SCHEMA')}")
    print(f"Steps    : {', '.join(steps_to_run)}")

    # Steps 1-3 use snowflake.connector (multi-statement SQL files)
    sql_steps = [s for s in steps_to_run if s != "semantic-model"]
    if sql_steps:
        conn = get_connector()
        try:
            cursor = conn.cursor()
            # Set context once
            cursor.execute("USE ROLE " + os.getenv("SNOWFLAKE_ROLE", "SYSADMIN"))
            cursor.execute("USE WAREHOUSE " + os.getenv("SNOWFLAKE_WAREHOUSE", "TEST"))
            cursor.execute("USE DATABASE " + os.getenv("SNOWFLAKE_DATABASE"))
            cursor.execute("USE SCHEMA " + os.getenv("SNOWFLAKE_SCHEMA"))

            for step_name in sql_steps:
                STEPS[step_name](cursor)

            cursor.close()
        except Exception as e:
            print(f"\n[ERROR] {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)
        finally:
            conn.close()

    # Step 4 uses Snowpark (file upload)
    if "semantic-model" in steps_to_run:
        try:
            step_semantic_model()
        except Exception as e:
            print(f"\n[ERROR] {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)

    print("\n" + "="*60)
    print("DATA LAYER SETUP COMPLETE")
    print("="*60)
    print("\nVerification queries (run in Snowsight):")
    print("  SELECT * FROM VW_SFMC_EMAIL_PERFORMANCE LIMIT 5;")
    print("  SELECT * FROM BENCHMARK_THRESHOLDS;")
    print("  SELECT * FROM ML_MODEL_REGISTRY;")
    print(f"  LIST @{os.getenv('SNOWFLAKE_DATABASE')}.{os.getenv('SNOWFLAKE_SCHEMA')}.{os.getenv('SNOWFLAKE_SEMANTIC_STAGE','SEMANTIC_FILES')};")


if __name__ == "__main__":
    main()
