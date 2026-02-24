"""
Cortex Complete Service Wrapper - DIA v2.0
==========================================

This module provides a Python wrapper for Snowflake Cortex Complete,
which is Snowflake's LLM (Large Language Model) service for text generation.

Key Features:
- Text generation and completion
- Multiple LLM models (llama3, mistral, etc.)
- Customizable parameters (temperature, max tokens)
- Streaming support for real-time responses

Use Cases:
- Generate marketing content
- Summarize campaign data
- Create email subject lines
- Answer questions about data
- Translate text

Learning Resources:
- https://docs.snowflake.com/en/user-guide/snowflake-cortex/llm-functions
- https://docs.snowflake.com/en/sql-reference/functions/complete-snowflake-cortex

Author: Li Ma
Date: February 24, 2026
docker exec dia-orchestrator python services/cortex_complete.py
"""

import os
import sys
from typing import Dict, List, Any, Optional, Generator
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
class CompleteResponse:
    """
    Container for Cortex Complete API responses.
    
    This dataclass holds the results from text generation requests.
    Makes it easier to work with API responses in a structured way.
    
    Attributes:
        prompt (str): The input text/question you provided
        completion (str): The generated text response from the LLM
        model (str): Which LLM model was used (e.g., 'llama3-70b')
        metadata (Dict): Additional info (tokens used, finish reason, etc.)
        error (str): Error message if something went wrong
    
    Example:
        response = CompleteResponse(
            prompt="Write a subject line for...",
            completion="Unlock 30% Off: Exclusive Deal Inside!",
            model="llama3-70b",
            metadata={"tokens": 15}
        )
    """
    prompt: str
    completion: Optional[str] = None
    model: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary (useful for JSON APIs)"""
        return {
            "prompt": self.prompt,
            "completion": self.completion,
            "model": self.model,
            "metadata": self.metadata,
            "error": self.error
        }


# ==============================================================================
# CORTEX COMPLETE SERVICE
# ==============================================================================

class CortexComplete:
    """
    Python wrapper for Snowflake Cortex Complete (LLM) service.
    
    This service lets you use Large Language Models to generate text,
    answer questions, summarize content, and more - all running securely
    inside Snowflake.
    
    Available Models:
    - llama3-70b: Meta's Llama 3 (70 billion parameters) - Best quality
    - llama3-8b: Meta's Llama 3 (8 billion parameters) - Faster, cheaper
    - mistral-large: Mistral AI's large model - Great for reasoning
    - mistral-7b: Mistral AI's compact model - Fast and efficient
    - mixtral-8x7b: Mixture of Experts model - Good balance
    
    Usage Example:
        # Basic usage
        llm = CortexComplete(model="llama3-70b")
        response = llm.complete("Write a catchy email subject line about summer sale")
        print(response.completion)
        
        # With context manager (auto cleanup)
        with CortexComplete() as llm:
            response = llm.complete("Summarize: ...")
            print(response.completion)
    """
    
    # Available LLM models in Snowflake Cortex
    AVAILABLE_MODELS = [
        "llama3-70b",      # Best quality, slower
        "llama3-8b",       # Fast, good quality
        "mistral-large",   # Great reasoning
        "mistral-7b",      # Fast and efficient
        "mixtral-8x7b",    # Balanced performance
    ]
    
    def __init__(
        self,
        model: str = "llama3-70b",
        temperature: float = 0.7,
        max_tokens: int = 500,
        database: str = None,
        schema: str = None,
        warehouse: str = None
    ):
        """
        Initialize Cortex Complete service.
        
        Args:
            model: Which LLM to use (default: llama3-70b)
            temperature: Creativity level (0.0=focused, 1.0=creative)
            max_tokens: Maximum length of generated text
            database: Snowflake database (from env if not provided)
            schema: Snowflake schema (from env if not provided)
            warehouse: Snowflake warehouse (from env if not provided)
        
        Temperature Guide:
            0.0-0.3: Focused, deterministic (facts, data analysis)
            0.4-0.7: Balanced creativity (general use)
            0.8-1.0: Very creative (marketing, storytelling)
        
        Example:
            # Creative content generation
            llm = CortexComplete(model="llama3-70b", temperature=0.9)
            
            # Factual data analysis
            llm = CortexComplete(model="mistral-large", temperature=0.2)
        """
        # Validate model selection
        if model not in self.AVAILABLE_MODELS:
            logger.warning(f"Model '{model}' not in known models list. Using anyway...")
        
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        
        # Snowflake connection details (from environment variables)
        self.database = database or os.getenv("SNOWFLAKE_DATABASE")
        self.schema = schema or os.getenv("SNOWFLAKE_SCHEMA")
        self.warehouse = warehouse or os.getenv("SNOWFLAKE_WAREHOUSE")
        
        # Session will be created lazily (only when needed)
        self._session: Optional[Session] = None
        
        logger.info(
            "CortexComplete initialized",
            model=self.model,
            temperature=self.temperature,
            max_tokens=self.max_tokens,
            database=self.database,
            schema=self.schema
        )
    
    # --------------------------------------------------------------------------
    # SNOWFLAKE SESSION MANAGEMENT
    # --------------------------------------------------------------------------
    
    def _get_session(self) -> Session:
        """
        Get or create Snowflake session (lazy loading pattern).
        
        Lazy Loading: We only connect to Snowflake when actually needed,
        not when the object is created. This saves resources!
        
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
    # CORE LLM FUNCTIONS
    # --------------------------------------------------------------------------
    
    def complete(
        self,
        prompt: str,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None
    ) -> CompleteResponse:
        """
        Generate text completion using Cortex LLM.
        
        This is the main function for text generation. You give it a prompt,
        and the LLM generates a response.
        
        Args:
            prompt: Your input text/question
            temperature: Override default creativity level (optional)
            max_tokens: Override default max length (optional)
        
        Returns:
            CompleteResponse with generated text
        
        Examples:
            # Generate marketing content
            response = llm.complete(
                "Write 3 email subject lines for a summer sale",
                temperature=0.9
            )
            
            # Analyze data
            response = llm.complete(
                "Summarize these key metrics: Open Rate: 25%, Click Rate: 3%",
                temperature=0.3
            )
        """
        # Use provided values or fall back to instance defaults
        temp = temperature if temperature is not None else self.temperature
        max_tok = max_tokens if max_tokens is not None else self.max_tokens
        
        logger.info(
            "Generating text completion",
            prompt_length=len(prompt),
            model=self.model,
            temperature=temp
        )
        
        try:
            session = self._get_session()
            
            # Build the SQL query to call Cortex Complete
            # SNOWFLAKE.CORTEX.COMPLETE is the LLM function
            # Note: Options must be an OBJECT constructed using OBJECT_CONSTRUCT()
            sql = f"""
                SELECT SNOWFLAKE.CORTEX.COMPLETE(
                    '{self.model}',
                    '{self._escape_quotes(prompt)}',
                    OBJECT_CONSTRUCT(
                        'temperature', {temp},
                        'max_tokens', {max_tok}
                    )
                ) AS completion
            """
            
            logger.debug("Executing Cortex Complete query", sql=sql.strip())
            
            # Execute the query
            result = session.sql(sql).collect()
            
            if result and len(result) > 0:
                completion_text = result[0]["COMPLETION"]
                
                logger.info(
                    "Text generation successful",
                    completion_length=len(completion_text)
                )
                
                return CompleteResponse(
                    prompt=prompt,
                    completion=completion_text,
                    model=self.model,
                    metadata={
                        "temperature": temp,
                        "max_tokens": max_tok,
                        "prompt_length": len(prompt),
                        "completion_length": len(completion_text)
                    }
                )
            else:
                error_msg = "No response from LLM"
                logger.error(error_msg)
                return CompleteResponse(prompt=prompt, error=error_msg)
        
        except Exception as e:
            error_msg = f"Error generating completion: {str(e)}"
            logger.error(error_msg, prompt=prompt)
            return CompleteResponse(prompt=prompt, error=error_msg)
    
    def summarize(self, text: str, max_length: int = 100) -> CompleteResponse:
        """
        Summarize a piece of text.
        
        Convenience method that creates a summarization prompt for you.
        
        Args:
            text: Text to summarize
            max_length: Maximum words in summary
        
        Returns:
            CompleteResponse with summary
        
        Example:
            long_text = "The email campaign ran for 2 weeks..."
            response = llm.summarize(long_text, max_length=50)
            print(response.completion)  # "The campaign achieved 25% open rate..."
        """
        prompt = f"""Summarize the following text in no more than {max_length} words. 
Be concise and focus on key points:

{text}

Summary:"""
        
        return self.complete(prompt, temperature=0.3)
    
    def generate_subject_lines(
        self,
        campaign_info: str,
        count: int = 3
    ) -> CompleteResponse:
        """
        Generate email subject lines for a campaign.
        
        Marketing-specific convenience method.
        
        Args:
            campaign_info: Description of your campaign
            count: How many subject lines to generate
        
        Returns:
            CompleteResponse with subject line suggestions
        
        Example:
            response = llm.generate_subject_lines(
                "Summer sale, 30% off all products, limited time",
                count=5
            )
        """
        prompt = f"""Generate {count} catchy email subject lines for this campaign:

{campaign_info}

Requirements:
- Keep them under 50 characters
- Make them action-oriented
- Create urgency or curiosity
- Avoid spam trigger words

Subject lines:"""
        
        return self.complete(prompt, temperature=0.8)
    
    def analyze_sentiment(self, text: str) -> CompleteResponse:
        """
        Analyze the sentiment of text.
        
        Returns: positive, negative, or neutral with explanation.
        
        Args:
            text: Text to analyze (email, feedback, etc.)
        
        Returns:
            CompleteResponse with sentiment analysis
        
        Example:
            response = llm.analyze_sentiment("This product is amazing!")
            # Result: "Positive - The text expresses strong enthusiasm..."
        """
        prompt = f"""Analyze the sentiment of this text. 
Classify as: Positive, Negative, or Neutral
Provide a brief explanation.

Text: {text}

Sentiment Analysis:"""
        
        return self.complete(prompt, temperature=0.2)
    
    # --------------------------------------------------------------------------
    # HELPER METHODS
    # --------------------------------------------------------------------------
    
    def _escape_quotes(self, text: str) -> str:
        """
        Escape quotes in text for SQL safety.
        
        Why needed: SQL strings use quotes, so we need to escape any quotes
        in the user's text to avoid breaking the SQL query.
        
        Args:
            text: Original text
        
        Returns:
            Text with escaped quotes
        """
        return text.replace("'", "''").replace('"', '\\"')
    
    def close(self) -> None:
        """
        Close Snowflake session and cleanup resources.
        
        Called automatically when using context manager (with statement).
        """
        if self._session is not None:
            self._session.close()
            self._session = None
            logger.info("Snowflake session closed")
    
    # --------------------------------------------------------------------------
    # CONTEXT MANAGER SUPPORT (for "with" statement)
    # --------------------------------------------------------------------------
    
    def __enter__(self):
        """Enable use with 'with' statement (context manager)"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Automatically close connection when exiting 'with' block"""
        self.close()
    
    def __del__(self):
        """Cleanup when object is destroyed"""
        self.close()


# ==============================================================================
# EXAMPLE USAGE (Run this file directly to see examples)
# ==============================================================================

if __name__ == "__main__":
    """
    Example usage of CortexComplete class.
    
    Run this file directly to test:
        python orchestrator/services/cortex_complete.py
    
    Or from Docker:
        docker exec dia-orchestrator python services/cortex_complete.py
    """
    
    print("=" * 70)
    print("CORTEX COMPLETE SERVICE - EXAMPLE USAGE")
    print("=" * 70)
    
    # Example 1: Basic text generation
    print("\n📝 Example 1: Generate Marketing Content")
    print("-" * 70)
    
    with CortexComplete(model="llama3-70b", temperature=0.8) as llm:
        response = llm.complete(
            "Write a creative tagline for a data analytics platform that helps marketers"
        )
        
        if response.error:
            print(f"❌ Error: {response.error}")
        else:
            print(f"✅ Generated: {response.completion}")
            print(f"   Model: {response.model}")
            print(f"   Tokens: ~{len(response.completion.split())}")
    
    # Example 2: Summarization
    print("\n📝 Example 2: Summarize Campaign Data")
    print("-" * 70)
    
    long_text = """
    The Q1 email marketing campaign ran from January 1 to March 31, 2026.
    We sent 500,000 emails across 50 different segments.
    Overall open rate was 24.5%, which exceeded our 20% target.
    Click-through rate was 3.2%, slightly below our 3.5% target.
    We generated $125,000 in revenue, a 15% increase from Q4 2025.
    The top performing segments were: Premium customers (35% open rate),
    and Recent purchasers (28% open rate).
    """
    
    with CortexComplete(model="mistral-large") as llm:
        response = llm.summarize(long_text, max_length=30)
        
        if response.error:
            print(f"❌ Error: {response.error}")
        else:
            print(f"✅ Summary: {response.completion}")
    
    # Example 3: Generate Subject Lines
    print("\n📝 Example 3: Generate Email Subject Lines")
    print("-" * 70)
    
    with CortexComplete(temperature=0.9) as llm:
        response = llm.generate_subject_lines(
            "Spring collection launch, 25% off, free shipping, limited time offer",
            count=3
        )
        
        if response.error:
            print(f"❌ Error: {response.error}")
        else:
            print(f"✅ Subject Lines:\n{response.completion}")
    
    # Example 4: Sentiment Analysis
    print("\n📝 Example 4: Analyze Sentiment")
    print("-" * 70)
    
    with CortexComplete(model="mistral-7b") as llm:
        response = llm.analyze_sentiment(
            "Your product broke after 2 days. Very disappointed with quality."
        )
        
        if response.error:
            print(f"❌ Error: {response.error}")
        else:
            print(f"✅ Sentiment: {response.completion}")
    
    print("\n" + "=" * 70)
    print("✅ Examples complete! Check the code to learn how it works.")
    print("=" * 70)
