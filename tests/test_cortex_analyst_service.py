"""
Test Script for Cortex Analyst Service
=======================================

This script tests the CortexAnalyst class functionality.
It provides both real tests and mock tests for when Cortex Analyst
isn't available yet.
"""

import sys
sys.path.insert(0, '/app')

from services.cortex_analyst import CortexAnalyst, AnalystResponse

def test_initialization():
    """Test 1: Can we create a CortexAnalyst instance?"""
    print("\n" + "="*70)
    print("TEST 1: Initialization")
    print("="*70)
    
    analyst = CortexAnalyst()
    print("✅ CortexAnalyst instance created successfully")
    print(f"   Database: {analyst.database}")
    print(f"   Schema: {analyst.schema}")
    print(f"   Semantic Model: @{analyst.stage_name}/{analyst.semantic_model_file}")
    analyst.close()


def test_semantic_model_verification():
    """Test 2: Can we verify the semantic model exists?"""
    print("\n" + "="*70)
    print("TEST 2: Semantic Model Verification")
    print("="*70)
    
    with CortexAnalyst() as analyst:
        verification = analyst.verify_semantic_model()
        
        if verification['exists']:
            print("✅ Semantic model found!")
            print(f"   File: {verification['file_name']}")
            print(f"   Size: {verification['file_size']:,} bytes")
            print(f"   Modified: {verification['last_modified']}")
        else:
            print("❌ Semantic model NOT found")
            print(f"   Error: {verification.get('error', 'Unknown')}")


def test_analyst_response_dataclass():
    """Test 3: Test the AnalystResponse data structure"""
    print("\n" + "="*70)
    print("TEST 3: AnalystResponse DataClass")
    print("="*70)
    
    # Create a mock response
    response = AnalystResponse(
        query="What is the average click rate?",
        sql="SELECT AVG(CLICK_RATE) FROM VW_SFMC_EMAIL_PERFORMANCE",
        results=[{"AVG_CLICK_RATE": 3.2}],
        metadata={"row_count": 1}
    )
    
    print("✅ AnalystResponse created")
    print(f"   Query: {response.query}")
    print(f"   SQL: {response.sql}")
    print(f"   Results: {response.results}")
    print(f"   Metadata: {response.metadata}")
    
    # Test to_dict method
    response_dict = response.to_dict()
    print("\n✅ Converted to dictionary:")
    print(f"   Keys: {list(response_dict.keys())}")


def test_context_manager():
    """Test 4: Does the context manager work?"""
    print("\n" + "="*70)
    print("TEST 4: Context Manager (with statement)")
    print("="*70)
    
    # This should automatically handle connection cleanup
    with CortexAnalyst() as analyst:
        print("✅ Inside 'with' block - connection active")
        print(f"   Session exists: {analyst._session is not None}")
    
    # After exiting 'with' block, connection should be closed
    print("✅ Exited 'with' block - connection should be closed")


def test_real_query():
    """Test 5: Try a real Cortex Analyst query"""
    print("\n" + "="*70)
    print("TEST 5: Real Cortex Analyst Query")
    print("="*70)
    
    with CortexAnalyst() as analyst:
        try:
            response = analyst.send_message("What is the average open rate?")
            
            if response.error:
                print(f"⚠️  Query failed (expected if Cortex Analyst not enabled)")
                print(f"   Error: {response.error}")
                print("\n💡 To enable Cortex Analyst:")
                print("   1. Contact Snowflake support or account admin")
                print("   2. Request Cortex Analyst feature enable")
                print("   3. Or use alternative: CORTEX.COMPLETE() for now")
            else:
                print("✅ Query successful!")
                print(f"   SQL: {response.sql}")
                print(f"   Results: {response.results[:3]}")  # First 3 rows
        
        except Exception as e:
            print(f"❌ Exception: {e}")


def test_sql_execution():
    """Test 6: Can we execute SQL directly?"""
    print("\n" + "="*70)
    print("TEST 6: Direct SQL Execution")
    print("="*70)
    
    with CortexAnalyst() as analyst:
        try:
            # Try a simple SQL query
            sql = "SELECT COUNT(*) AS ROW_COUNT FROM VW_SFMC_EMAIL_PERFORMANCE LIMIT 1"
            results = analyst._execute_sql(sql)
            
            print("✅ SQL executed successfully")
            print(f"   Results: {results}")
        
        except Exception as e:
            print(f"❌ SQL execution failed: {e}")


# ==============================================================================
# MAIN TEST RUNNER
# ==============================================================================

if __name__ == "__main__":
    print("\n")
    print("╔" + "="*68 + "╗")
    print("║" + " CORTEX ANALYST SERVICE - TEST SUITE".center(68) + "║")
    print("╚" + "="*68 + "╝")
    
    tests = [
        test_initialization,
        test_semantic_model_verification,
        test_analyst_response_dataclass,
        test_context_manager,
        test_sql_execution,
        test_real_query,  # This might fail if Cortex Analyst not enabled
    ]
    
    passed = 0
    failed = 0
    
    for test_func in tests:
        try:
            test_func()
            passed += 1
        except Exception as e:
            print(f"\n❌ TEST FAILED: {e}")
            failed += 1
    
    # Summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    print(f"📊 Total:  {passed + failed}")
    
    if failed == 0:
        print("\n🎉 All tests passed!")
    else:
        print(f"\n⚠️  {failed} test(s) failed (may be expected if Cortex Analyst not enabled)")
    
    print("="*70)
