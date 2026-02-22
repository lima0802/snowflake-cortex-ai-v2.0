"""
Pytest tests for DIA v2.0 Orchestrator API
Tests FastAPI endpoints and functionality
"""

import sys
import os
import pytest
from fastapi.testclient import TestClient

# Add /app to Python path for imports
sys.path.insert(0, '/app')

from main import app

# Create test client
client = TestClient(app)


class TestRootEndpoint:
    """Tests for root endpoint"""
    
    def test_root_endpoint_exists(self):
        """Test root endpoint is accessible"""
        response = client.get("/")
        assert response.status_code == 200
    
    def test_root_endpoint_returns_json(self):
        """Test root endpoint returns JSON"""
        response = client.get("/")
        assert response.headers["content-type"] == "application/json"
    
    def test_root_endpoint_content(self):
        """Test root endpoint returns expected content"""
        response = client.get("/")
        data = response.json()
        
        assert "service" in data
        assert "status" in data
        assert "version" in data
        assert "docs" in data
        
        assert data["service"] == "DIA v2.0 Orchestrator"
        assert data["status"] == "running"
        assert data["version"] == "2.0.0"
        assert data["docs"] == "/docs"


class TestHealthEndpoint:
    """Tests for health check endpoint"""
    
    def test_health_endpoint_exists(self):
        """Test health endpoint is accessible"""
        response = client.get("/api/v1/health")
        assert response.status_code == 200
    
    def test_health_endpoint_returns_healthy(self):
        """Test health endpoint returns healthy status"""
        response = client.get("/api/v1/health")
        data = response.json()
        
        assert data["status"] == "healthy"
        assert data["service"] == "orchestrator"
    
    def test_health_endpoint_includes_snowflake_config(self):
        """Test health endpoint includes Snowflake configuration"""
        response = client.get("/api/v1/health")
        data = response.json()
        
        assert "snowflake" in data
        assert "account" in data["snowflake"]
        assert "database" in data["snowflake"]
        assert "schema" in data["snowflake"]
    
    def test_health_endpoint_snowflake_values(self):
        """Test health endpoint returns actual Snowflake values"""
        response = client.get("/api/v1/health")
        data = response.json()
        
        # Should have values from environment variables
        snowflake = data["snowflake"]
        assert snowflake["account"] is not None
        assert snowflake["database"] is not None
        assert snowflake["schema"] is not None


class TestQueryEndpoint:
    """Tests for query endpoint"""
    
    def test_query_endpoint_exists(self):
        """Test query endpoint is accessible"""
        response = client.post("/api/v1/query", json={"query": "test"})
        assert response.status_code == 200
    
    def test_query_endpoint_accepts_json(self):
        """Test query endpoint accepts JSON payload"""
        test_payload = {
            "query": "What was the click rate last month?",
            "session_id": "test-session-123"
        }
        response = client.post("/api/v1/query", json=test_payload)
        assert response.status_code == 200
    
    def test_query_endpoint_placeholder_response(self):
        """Test query endpoint returns placeholder response"""
        response = client.post("/api/v1/query", json={"query": "test"})
        data = response.json()
        
        # Currently returns placeholder until Phase 2
        assert "status" in data
        assert "message" in data
        assert data["status"] == "not_implemented"
    
    def test_query_endpoint_echoes_request(self):
        """Test query endpoint echoes received request"""
        test_payload = {"query": "test query", "user_id": 123}
        response = client.post("/api/v1/query", json=test_payload)
        data = response.json()
        
        assert "received" in data
        assert data["received"] == test_payload


class TestAPIDocumentation:
    """Tests for API documentation endpoints"""
    
    def test_swagger_docs_accessible(self):
        """Test Swagger UI documentation is accessible"""
        response = client.get("/docs")
        assert response.status_code == 200
    
    def test_redoc_accessible(self):
        """Test ReDoc documentation is accessible"""
        response = client.get("/redoc")
        assert response.status_code == 200
    
    def test_openapi_json_accessible(self):
        """Test OpenAPI JSON schema is accessible"""
        response = client.get("/openapi.json")
        assert response.status_code == 200
        
        # Verify it's valid JSON
        schema = response.json()
        assert "openapi" in schema
        assert "info" in schema
        assert "paths" in schema


class TestCORS:
    """Tests for CORS configuration"""
    
    def test_cors_allows_all_origins(self):
        """Test CORS allows all origins (development mode)"""
        response = client.get(
            "/api/v1/health",
            headers={"Origin": "http://localhost:3000"}
        )
        
        # Should allow the origin
        assert response.status_code == 200
        assert response.headers.get("access-control-allow-origin") == "*"
    
    def test_cors_headers_on_query(self):
        """Test CORS headers are present on query endpoint"""
        response = client.post(
            "/api/v1/query",
            json={"query": "test"},
            headers={"Origin": "http://localhost:8501"}
        )
        
        assert response.status_code == 200
        # CORS middleware should add this header
        assert "access-control-allow-origin" in response.headers


class TestErrorHandling:
    """Tests for error handling"""
    
    def test_404_on_invalid_endpoint(self):
        """Test 404 response for non-existent endpoints"""
        response = client.get("/api/v1/nonexistent")
        assert response.status_code == 404
    
    def test_405_on_wrong_method(self):
        """Test 405 response for wrong HTTP method"""
        # Query endpoint is POST only
        response = client.get("/api/v1/query")
        assert response.status_code == 405
    
    def test_query_endpoint_requires_json(self):
        """Test query endpoint handles invalid content type"""
        response = client.post(
            "/api/v1/query",
            data="not json",
            headers={"Content-Type": "text/plain"}
        )
        # Should return 422 (Unprocessable Entity) for invalid data
        assert response.status_code == 422


class TestResponseFormat:
    """Tests for response format consistency"""
    
    def test_all_endpoints_return_json(self):
        """Test all endpoints return JSON responses"""
        endpoints = [
            ("GET", "/"),
            ("GET", "/api/v1/health"),
            ("POST", "/api/v1/query", {"query": "test"})
        ]
        
        for method, path, *args in endpoints:
            if method == "GET":
                response = client.get(path)
            else:
                response = client.post(path, json=args[0] if args else None)
            
            assert "application/json" in response.headers["content-type"]
            
            # Verify it's valid JSON
            data = response.json()
            assert isinstance(data, dict)


class TestApplicationMetadata:
    """Tests for application metadata"""
    
    def test_app_title(self):
        """Test FastAPI app has correct title"""
        assert app.title == "DIA v2.0 Orchestrator"
    
    def test_app_version(self):
        """Test FastAPI app has correct version"""
        assert app.version == "2.0.0"
    
    def test_app_description(self):
        """Test FastAPI app has description"""
        assert app.description is not None
        assert len(app.description) > 0


# Integration test
class TestIntegration:
    """Integration tests"""
    
    def test_full_workflow_placeholder(self):
        """Test placeholder for full query workflow"""
        # 1. Check service is healthy
        health_response = client.get("/api/v1/health")
        assert health_response.status_code == 200
        assert health_response.json()["status"] == "healthy"
        
        # 2. Send a query
        query_response = client.post(
            "/api/v1/query",
            json={"query": "What was the click rate last month?"}
        )
        assert query_response.status_code == 200
        
        # 3. Verify response structure (currently placeholder)
        data = query_response.json()
        assert "status" in data
        assert "received" in data


# Pytest fixtures
@pytest.fixture
def sample_query():
    """Fixture providing sample query data"""
    return {
        "query": "What was the click rate last month?",
        "session_id": "test-session-123"
    }


@pytest.fixture
def sample_queries():
    """Fixture providing multiple sample queries"""
    return [
        "What was the click rate last month?",
        "Compare ES and SE markets",
        "Why did open rate drop?",
        "Predict clicks for next month",
        "How to improve engagement?"
    ]


# Parameterized tests
@pytest.mark.parametrize("endpoint", [
    "/",
    "/api/v1/health",
    "/docs",
    "/redoc",
])
def test_endpoint_accessibility(endpoint):
    """Test multiple endpoints are accessible"""
    response = client.get(endpoint)
    assert response.status_code == 200


@pytest.mark.parametrize("query_text", [
    "What was the click rate?",
    "Show me email performance",
    "Analyze market trends",
    "Predict future outcomes",
])
def test_query_endpoint_with_various_queries(query_text):
    """Test query endpoint with various query strings"""
    response = client.post("/api/v1/query", json={"query": query_text})
    assert response.status_code == 200
    data = response.json()
    assert data["received"]["query"] == query_text


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v", "--tb=short"])
