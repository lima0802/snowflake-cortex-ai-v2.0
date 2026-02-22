# 📚 Learning Guide: Cortex Analyst Service

## 🎯 What You Just Built

You created a **professional Python wrapper** for Snowflake Cortex Analyst with:
- ✅ Proper class structure
- ✅ Error handling and logging
- ✅ Context manager support (`with` statement)
- ✅ Comprehensive documentation
- ✅ Test-driven approach

---

## 📊 Test Results Summary

```
✅ Test 1: Initialization - PASSED
✅ Test 2: Semantic Model Verification - PASSED (217 KB file found!)  
✅ Test 3: Data Structure (AnalystResponse) - PASSED
✅ Test 4: Context Manager - PASSED
✅ Test 5: SQL Execution - PASSED (100,000 rows in your table!)
⚠️  Test 6: Cortex Analyst Query - Function not available yet
```

---

## 🔍 Understanding Your Code

### 1. **Class Structure** (lines 100-150)

```python
class CortexAnalyst:
    def __init__(self, ...):
        # Sets up configuration
        # Loads environment variables
        # Doesn't connect yet (lazy loading!)
```

**Why lazy loading?**  
We don't connect to Snowflake until you actually need it. This saves resources!

### 2. **Connection Management** (lines 152-200)

```python
def _get_session(self) -> Session:
    if self._session is not None:
        return self._session  # Reuse existing connection
    
    # Create new connection only when needed
    self._session = Session.builder.configs(...).create()
```

**Pattern:** Singleton pattern - one connection per instance.

### 3. **Main Functionality** (lines 202-320)

```python
def send_message(self, query: str) -> AnalystResponse:
    # 1. Get connection
    # 2. Build SQL to call Cortex Analyst
    # 3. Parse response
    # 4. Return structured data
```

**Key Learning:** Always return structured data (not raw dictionaries).

### 4. **Error Handling**

```python
try:
    # Do something risky
    result = analyst.send_message(query)
except Exception as e:
    # Handle the error gracefully
    logger.error(f"Error: {e}")
```

**Best Practice:** Never let exceptions crash your app silently.

---

## 🛠️ Practice Exercises

### Exercise 1: Add a New Method

Add a method to get query history:

```python
def get_query_history(self) -> List[Dict]:
    """Get list of past queries"""
    # TODO: Implement this!
    # Hint: Store queries in a list attribute
    pass
```

<details>
<summary>Click to see solution</summary>

```python
def __init__(self, ...):
    # Add this to __init__
    self.query_history = []

def send_message(self, query: str) -> AnalystResponse:
    # Add this at the end of send_message
    self.query_history.append({
        "query": query,
        "timestamp": datetime.now(),
        "success": response.error is None
    })
    
def get_query_history(self) -> List[Dict]:
    """Get list of past queries"""
    return self.query_history
```
</details>

### Exercise 2: Add Retry Logic

What if the connection fails? Add retry logic:

```python
def _get_session_with_retry(self, max_retries=3) -> Session:
    """Try to connect, retry if it fails"""
    for attempt in range(max_retries):
        try:
            return self._get_session()
        except Exception as e:
            if attempt == max_retries - 1:
                raise  # Last attempt failed
            logger.warning(f"Connection attempt {attempt + 1} failed, retrying...")
            time.sleep(2 ** attempt)  # Exponential backoff
```

### Exercise 3: Add Caching

Cache responses to avoid re-running expensive queries:

```python
def __init__(self, ...):
    self.response_cache = {}  # Add to __init__

def send_message(self, query: str, use_cache=True) -> AnalystResponse:
    # Check cache first
    if use_cache and query in self.response_cache:
        logger.info("Returning cached response")
        return self.response_cache[query]
    
    # Get response normally
    response = ... # existing code
    
    # Store in cache
    if use_cache and not response.error:
        self.response_cache[query] = response
    
    return response
```

---

## ⚠️ About Cortex Analyst Availability

Your test shows:
```
Unknown user-defined function SNOWFLAKE.CORTEX.ANALYST
```

This means **Cortex Analyst isn't enabled** in your Snowflake account yet.

### How to Enable

1. **Contact your Snowflake account admin**
2. **Or** use Snowflake support: https://community.snowflake.com/
3. **Request:** Cortex Analyst feature activation

### Alternative: Use CORTEX.COMPLETE() Now

While waiting, you can use `CORTEX.COMPLETE()` (working LLM function):

```python
def ask_llm(self, prompt: str) -> str:
    """Use Cortex Complete instead"""
    session = self._get_session()
    
    sql = f"""
        SELECT SNOWFLAKE.CORTEX.COMPLETE(
            'mistral-large',
            '{self._escape_quotes(prompt)}'
        ) AS response
    """
    
    result = session.sql(sql).collect()
    return result[0]['RESPONSE']
```

Test it:
```python
analyst = CortexAnalyst()
response = analyst.ask_llm("Explain what email open rate means")
print(response)
```

---

## 🔧 Your Code Files

| File | Purpose | Status |
|------|---------|--------|
| `orchestrator/services/cortex_analyst.py` | Main service class | ✅ Complete |
| `tests/test_cortex_analyst_service.py` | Test suite | ✅ Complete |
| `orchestrator/utils/logging.py` | Logging utility | ✅ Existing |

---

## 📖 Next Steps for Learning

### 1. **Read the Code Comments**
Every function has detailed explanations. Read through them!

### 2. **Modify and Experiment**
- Change the logging messages
- Add new methods
- Try different error handling approaches

### 3. **Run Tests**
```powershell
docker exec dia-orchestrator python /tests/test_cortex_analyst_service.py
```

### 4. **Debug with Print Statements**
Add `print()` statements to see what's happening:
```python
def send_message(self, query: str):
    print(f"DEBUG: Received query: {query}")
    # ... rest of code
```

### 5. **Check the Logs**
Your code uses structured logging - watch the logs:
```powershell
docker-compose logs -f orchestrator
```

---

## 🎓 Key Python Concepts You Learned

1. **Classes and Objects**
   - `__init__` constructor
   - Instance variables (`self.database`)
   - Instance methods (`self.send_message()`)

2. **Type Hints**
   ```python
   def send_message(self, query: str) -> AnalystResponse:
   ```
   Helps catch bugs early!

3. **Dataclasses**
   ```python
   @dataclass
   class AnalystResponse:
   ```
   Clean way to structure data

4. **Context Managers**
   ```python
   def __enter__(self): ...
   def __exit__(self, ...): ...
   ```
   Enables `with CortexAnalyst() as analyst:`

5. **Logging**
   ```python
   logger.info("Message", key=value)
   ```
   Better than print()!

6. **Error Handling**
   ```python
   try: ... except Exception as e: ...
   ```
   Always handle errors gracefully

---

## 🚀 Production Checklist

Before using in production:

- [ ] Enable Cortex Analyst in Snowflake
- [ ] Add unit tests with pytest
- [ ] Add input validation (max query length, etc.)
- [ ] Add rate limiting
- [ ] Add response caching
- [ ] Monitor performance metrics
- [ ] Add circuit breaker for failures
- [ ] Document API usage examples

---

## 📚 Additional Resources

- [Snowflake Cortex Documentation](https://docs.snowflake.com/en/user-guide/snowflake-cortex)
- [Python Dataclasses](https://docs.python.org/3/library/dataclasses.html)
- [Context Managers](https://docs.python.org/3/reference/datamodel.html#context-managers)
- [Structlog Documentation](https://www.structlog.org/)

---

## 💡 Tips for Continued Learning

1. **Read error messages carefully** - they tell you exactly what's wrong
2. **Use print() and logger.debug()** liberally while learning
3. **Test small changes** - don't write 100 lines before testing
4. **Read other people's code** - learn from examples
5. **Ask "why?"** - understand the reasoning, not just the syntax

---

**Great job building your first Cortex service wrapper! 🎉**

You now have a solid foundation to build the other 3 services:
- ✅ `cortex_analyst.py` - COMPLETE
- ⏳ `cortex_complete.py` - Next
- ⏳ `cortex_search.py` - Next
- ⏳ `cortex_ml.py` - Next

---

**Questions?** Check the code comments or run the tests again!
