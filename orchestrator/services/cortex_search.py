"""
Cortex Search Service Wrapper - DIA v2.0
========================================

This module provides a Python wrapper for Snowflake Cortex Search,
which enables semantic search using vector embeddings.

Key Features:
- Vector similarity search (find similar content)
- Semantic understanding (meaning-based, not just keywords)
- RAG (Retrieval Augmented Generation) support
- Fast and scalable search

Use Cases:
- Search campaign documents by meaning
- Find similar email content
- Recommend related campaigns
- Question answering over your data
- Content discovery

Learning Resources:
- https://docs.snowflake.com/en/user-guide/snowflake-cortex/cortex-search
- https://docs.snowflake.com/en/user-guide/snowflake-cortex/vector-embeddings

Author: Li Ma
Date: February 24, 2026
docker exec dia-orchestrator python services/cortex_search.py
"""

import os
import sys
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import json

from snowflake.snowpark import Session
from dotenv import load_dotenv

# Add parent directory to Python path for proper imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.logging import get_logger

# Load environment variables
load_dotenv()

# Initialize logger
logger = get_logger(__name__)


# ==============================================================================
# DATA MODELS
# ==============================================================================

@dataclass
class SearchResult:
    """
    Container for a single search result.
    
    Represents one matching document/record from your search.
    
    Attributes:
        content (str): The actual text content that matched
        score (float): Similarity score (0-1, higher = more similar)
        metadata (Dict): Additional fields (id, title, category, etc.)
        rank (int): Position in results (1 = best match)
    
    Example:
        result = SearchResult(
            content="Summer Sale Email - 30% off all items",
            score=0.92,
            metadata={"campaign_id": "C123", "category": "promotional"},
            rank=1
        )
    """
    content: str
    score: float
    metadata: Optional[Dict[str, Any]] = None
    rank: Optional[int] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "content": self.content,
            "score": self.score,
            "metadata": self.metadata,
            "rank": self.rank
        }


@dataclass
class SearchResponse:
    """
    Container for search API responses.
    
    Holds all results from a search query plus metadata.
    
    Attributes:
        query (str): The search query you submitted
        results (List[SearchResult]): List of matching results
        total_results (int): Total number of matches found
        metadata (Dict): Search metadata (time taken, filters used, etc.)
        error (str): Error message if something went wrong
    
    Example:
        response = SearchResponse(
            query="promotional emails for summer",
            results=[result1, result2, result3],
            total_results=15,
            metadata={"search_time_ms": 125}
        )
    """
    query: str
    results: Optional[List[SearchResult]] = None
    total_results: Optional[int] = None
    metadata: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "query": self.query,
            "results": [r.to_dict() for r in (self.results or [])],
            "total_results": self.total_results,
            "metadata": self.metadata,
            "error": self.error
        }


# ==============================================================================
# CORTEX SEARCH SERVICE
# ==============================================================================

class CortexSearch:
    """
    Python wrapper for Snowflake Cortex Search service.
    
    This service enables semantic search using vector embeddings.
    Unlike traditional keyword search, it understands the *meaning*
    of your query and finds semantically similar content.
    
    How it works:
    1. Your documents are converted to vector embeddings (numbers)
    2. When you search, your query is also converted to a vector
    3. Snowflake finds documents with similar vectors (similar meanings)
    
    Example: Searching "affordable housing" might also find
    documents about "low-cost apartments" or "budget homes"
    even if they don't contain the exact words.
    
    Prerequisites:
        You must first create a Cortex Search Service in Snowflake:
        
        CREATE CORTEX SEARCH SERVICE my_search_service
        ON content_column
        WAREHOUSE = my_warehouse
        TARGET_LAG = '1 hour'
        AS SELECT id, content, metadata FROM my_table;
    
    Usage Example:
        # Initialize
        search = CortexSearch(service_name="campaign_search")
        
        # Search
        response = search.search("email campaigns about summer sale")
        for result in response.results:
            print(f"Score: {result.score:.2f} | {result.content}")
        
        # With context manager
        with CortexSearch("campaign_search") as search:
            response = search.search("promotional content", limit=10)
    """
    
    def __init__(
        self,
        service_name: str,
        database: str = None,
        schema: str = None,
        warehouse: str = None
    ):
        """
        Initialize Cortex Search service.
        
        Args:
            service_name: Name of your Cortex Search Service in Snowflake
            database: Snowflake database (from env if not provided)
            schema: Snowflake schema (from env if not provided)
            warehouse: Snowflake warehouse (from env if not provided)
        
        Example:
            # Use default database/schema from .env
            search = CortexSearch("my_search_service")
            
            # Override database/schema
            search = CortexSearch(
                "my_search_service",
                database="ANALYTICS_DB",
                schema="PUBLIC"
            )
        """
        self.service_name = service_name
        
        # Snowflake connection details (from environment variables)
        self.database = database or os.getenv("SNOWFLAKE_DATABASE")
        self.schema = schema or os.getenv("SNOWFLAKE_SCHEMA")
        self.warehouse = warehouse or os.getenv("SNOWFLAKE_WAREHOUSE")
        
        # Session will be created lazily (only when needed)
        self._session: Optional[Session] = None
        
        logger.info(
            "CortexSearch initialized",
            service_name=self.service_name,
            database=self.database,
            schema=self.schema
        )
    
    # --------------------------------------------------------------------------
    # SNOWFLAKE SESSION MANAGEMENT
    # --------------------------------------------------------------------------
    
    def _get_session(self) -> Session:
        """
        Get or create Snowflake session (lazy loading pattern).
        
        Returns:
            Active Snowflake session
        """
        if self._session is None:
            logger.info("Creating Snowflake session...")
            
            self._session = Session.builder.configs({
                "account": os.getenv("SNOWFLAKE_ACCOUNT"),
                "user": os.getenv("SNOWFLAKE_USER"),
                "password": os.getenv("SNOWFLAKE_PASSWORD"),
                "role": os.getenv("SNOWFLAKE_ROLE"),
                "warehouse": self.warehouse,
                "database": self.database,
                "schema": self.schema,
            }).create()
            
            logger.info(
                "Snowflake session created successfully",
                account=os.getenv("SNOWFLAKE_ACCOUNT"),
                database=self.database
            )
        
        return self._session
    
    # --------------------------------------------------------------------------
    # SEARCH FUNCTIONS
    # --------------------------------------------------------------------------
    
    def search(
        self,
        query: str,
        limit: int = 10,
        filters: Optional[Dict[str, Any]] = None
    ) -> SearchResponse:
        """
        Perform semantic search.
        
        Find documents similar to your query based on meaning,
        not just keyword matching.
        
        Args:
            query: Your search query (natural language)
            limit: Maximum number of results to return
            filters: Optional filters (e.g., {"category": "promotional"})
        
        Returns:
            SearchResponse with matching results
        
        Examples:
            # Basic search
            response = search.search("summer sale campaigns")
            
            # Filtered search
            response = search.search(
                "email marketing",
                limit=20,
                filters={"year": 2026, "status": "active"}
            )
            
            # Process results
            for result in response.results:
                print(f"{result.rank}. [{result.score:.2f}] {result.content}")
        """
        logger.info(
            "Executing semantic search",
            query=query,
            limit=limit,
            has_filters=filters is not None
        )
        
        try:
            session = self._get_session()
            
            # Build filter clause if filters provided
            filter_clause = ""
            if filters:
                filter_parts = [f"{k} = '{v}'" for k, v in filters.items()]
                filter_clause = f"FILTER => {{'where': \"{' AND '.join(filter_parts)}\"}}"
            
            # Build the SQL query to call Cortex Search
            # Format: SELECT PARSE_JSON(SNOWFLAKE.CORTEX.SEARCH(...))
            sql = f"""
                SELECT
                    SNOWFLAKE.CORTEX.SEARCH(
                        '{self.service_name}',
                        {{
                            'query': '{self._escape_quotes(query)}',
                            'top_k': {limit}
                            {', ' + filter_clause if filter_clause else ''}
                        }}
                    ) AS search_results
            """
            
            logger.debug("Executing Cortex Search query", sql=sql.strip())
            
            # Execute the query
            result = session.sql(sql).collect()
            
            if result and len(result) > 0:
                # Parse the JSON response
                search_data = json.loads(result[0]["SEARCH_RESULTS"])
                
                # Extract results
                results = []
                if "results" in search_data:
                    for idx, item in enumerate(search_data["results"], 1):
                        results.append(SearchResult(
                            content=item.get("content", ""),
                            score=item.get("score", 0.0),
                            metadata=item.get("metadata", {}),
                            rank=idx
                        ))
                
                logger.info(
                    "Search completed successfully",
                    results_count=len(results),
                    top_score=results[0].score if results else 0
                )
                
                return SearchResponse(
                    query=query,
                    results=results,
                    total_results=len(results),
                    metadata={
                        "limit": limit,
                        "filters": filters,
                        "service": self.service_name
                    }
                )
            else:
                error_msg = "No search results returned"
                logger.warning(error_msg)
                return SearchResponse(query=query, results=[], total_results=0)
        
        except Exception as e:
            error_msg = f"Search error: {str(e)}"
            logger.error(error_msg, query=query)
            return SearchResponse(query=query, error=error_msg)
    
    def search_with_llm(
        self,
        query: str,
        limit: int = 5,
        llm_model: str = "llama3-70b"
    ) -> str:
        """
        RAG (Retrieval Augmented Generation) pattern.
        
        1. Search for relevant documents
        2. Use LLM to generate answer based on those documents
        
        This combines search with text generation for more accurate answers.
        
        Args:
            query: Your question
            limit: How many documents to retrieve
            llm_model: Which LLM to use for answer generation
        
        Returns:
            Generated answer based on retrieved documents
        
        Example:
            answer = search.search_with_llm(
                "What are our best performing campaigns?"
            )
            print(answer)  # "Based on the data, your top campaigns are..."
        """
        # Step 1: Search for relevant documents
        search_response = self.search(query, limit=limit)
        
        if search_response.error or not search_response.results:
            return "Sorry, I couldn't find relevant information."
        
        # Step 2: Build context from search results
        context = "\n\n".join([
            f"Document {r.rank}: {r.content}"
            for r in search_response.results
        ])
        
        # Step 3: Generate answer using LLM with context
        try:
            session = self._get_session()
            
            prompt = f"""Based on the following documents, answer this question: {query}

Documents:
{context}

Answer:"""
            
            sql = f"""
                SELECT SNOWFLAKE.CORTEX.COMPLETE(
                    '{llm_model}',
                    '{self._escape_quotes(prompt)}',
                    OBJECT_CONSTRUCT('temperature', 0.3)
                ) AS answer
            """
            
            result = session.sql(sql).collect()
            
            if result and len(result) > 0:
                return result[0]["ANSWER"]
            else:
                return "Sorry, I couldn't generate an answer."
        
        except Exception as e:
            logger.error(f"RAG generation error: {e}")
            return f"Error generating answer: {str(e)}"
    
    # --------------------------------------------------------------------------
    # HELPER METHODS
    # --------------------------------------------------------------------------
    
    def _escape_quotes(self, text: str) -> str:
        """Escape quotes in text for SQL safety"""
        return text.replace("'", "''").replace('"', '\\"')
    
    def close(self) -> None:
        """Close Snowflake session and cleanup resources"""
        if self._session is not None:
            self._session.close()
            self._session = None
            logger.info("Snowflake session closed")
    
    # --------------------------------------------------------------------------
    # CONTEXT MANAGER SUPPORT
    # --------------------------------------------------------------------------
    
    def __enter__(self):
        """Enable use with 'with' statement"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Automatically close connection when exiting 'with' block"""
        self.close()
    
    def __del__(self):
        """Cleanup when object is destroyed"""
        self.close()


# ==============================================================================
# EXAMPLE USAGE
# ==============================================================================

if __name__ == "__main__":
    """
    Example usage of CortexSearch class.
    
    Note: These examples will only work if you've created a Cortex Search
    Service in your Snowflake account first.
    
    Run this file directly to test:
        python orchestrator/services/cortex_search.py
    
    Or from Docker:
        docker exec dia-orchestrator python services/cortex_search.py
    """
    
    print("=" * 70)
    print("CORTEX SEARCH SERVICE - EXAMPLE USAGE")
    print("=" * 70)
    
    # Note: Replace 'MY_SEARCH_SERVICE' with your actual service name
    SERVICE_NAME = "campaign_search_service"  # Update this!
    
    print(f"\n⚠️  Using service: {SERVICE_NAME}")
    print("   If this doesn't exist, examples will fail.")
    print("   Create one first with: CREATE CORTEX SEARCH SERVICE...")
    
    # Example 1: Basic semantic search
    print("\n📝 Example 1: Semantic Search")
    print("-" * 70)
    
    try:
        with CortexSearch(SERVICE_NAME) as search:
            response = search.search(
                "email campaigns about summer promotions",
                limit=5
            )
            
            if response.error:
                print(f"❌ Error: {response.error}")
            elif response.results:
                print(f"✅ Found {response.total_results} results:\n")
                for result in response.results:
                    print(f"   {result.rank}. Score: {result.score:.3f}")
                    print(f"      Content: {result.content[:80]}...")
                    print()
            else:
                print("ℹ️  No results found")
    
    except Exception as e:
        print(f"❌ Error: {e}")
        print("   Make sure your Cortex Search Service exists!")
    
    # Example 2: Filtered search
    print("\n📝 Example 2: Filtered Search")
    print("-" * 70)
    
    try:
        with CortexSearch(SERVICE_NAME) as search:
            response = search.search(
                "promotional content",
                limit=10,
                filters={"category": "email", "status": "active"}
            )
            
            if response.results:
                print(f"✅ Found {len(response.results)} filtered results")
            else:
                print("ℹ️  No results found")
    
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Example 3: RAG (Search + LLM)
    print("\n📝 Example 3: RAG - Search with LLM Answer")
    print("-" * 70)
    
    try:
        with CortexSearch(SERVICE_NAME) as search:
            answer = search.search_with_llm(
                "What are the main themes in our marketing campaigns?",
                limit=5
            )
            
            print(f"✅ Answer:\n{answer}")
    
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print("\n" + "=" * 70)
    print("✅ Examples complete!")
    print("=" * 70)
