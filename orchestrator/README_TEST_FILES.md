# Test Files in Orchestrator Directory

## Why test_connection.py exists here

You may notice `test_connection.py` appears in both locations:
- `tests/test_connection.py` (original)
- `orchestrator/test_connection.py` (copy for container)

### Reason

The `orchestrator/` directory is **mounted in the Docker container** as `/app/`, making files here directly accessible:

```yaml
# docker-compose.yml
volumes:
  - ./orchestrator:/app  # Mounted ✅
  - ./tests:/tests        # Also mounted ✅
```

### Usage

Both work, use whichever is more convenient:

```powershell
# Using copy in orchestrator (shorter path)
docker exec dia-orchestrator python test_connection.py

# Using original in tests
docker exec dia-orchestrator python /tests/test_connection.py
```

### Maintenance

If you update `tests/test_connection.py`, remember to update the copy:

```powershell
docker cp tests/test_connection.py dia-orchestrator:/app/test_connection.py
```

Or just use the `/tests/` version directly since it's now mounted!
