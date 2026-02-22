"""
Structured logging configuration for DIA v2.0
Uses structlog for structured, context-rich logging
"""

import logging
import sys
from typing import Any

import structlog
from structlog.types import FilteringBoundLogger


def configure_logging(
    level: str = "INFO",
    json_output: bool = False,
    development: bool = True
) -> None:
    """
    Configure structured logging with structlog
    
    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        json_output: If True, output logs as JSON (for production)
        development: If True, use colored console output (for development)
    
    Example:
        configure_logging(level="DEBUG", development=True)
    """
    # Set log level
    log_level = getattr(logging, level.upper(), logging.INFO)
    
    # Configure stdlib logging
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=log_level,
    )
    
    # Configure structlog processors
    processors = [
        # Add log level to event dict
        structlog.stdlib.add_log_level,
        # Add logger name to event dict
        structlog.stdlib.add_logger_name,
        # Add timestamp
        structlog.processors.TimeStamper(fmt="iso"),
        # Include stack info for exceptions
        structlog.processors.StackInfoRenderer(),
        # Format exceptions
        structlog.processors.format_exc_info,
        # Decode unicode strings
        structlog.processors.UnicodeDecoder(),
    ]
    
    if json_output:
        # Production: JSON output
        processors.append(structlog.processors.JSONRenderer())
    elif development:
        # Development: Colored console output
        processors.extend([
            structlog.dev.ConsoleRenderer(
                colors=True,
                exception_formatter=structlog.dev.plain_traceback,
            )
        ])
    else:
        # Simple key-value output
        processors.append(structlog.processors.KeyValueRenderer())
    
    # Configure structlog
    structlog.configure(
        processors=processors,
        wrapper_class=structlog.stdlib.BoundLogger,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )


def get_logger(name: str = None) -> FilteringBoundLogger:
    """
    Get a structured logger instance
    
    Args:
        name: Logger name (typically __name__ of the module)
    
    Returns:
        Configured structlog logger instance
    
    Example:
        logger = get_logger(__name__)
        logger.info("user_logged_in", user_id=123, component="auth")
        logger.error("database_error", error=str(e), query=sql)
    """
    return structlog.get_logger(name)


def log_function_call(logger: FilteringBoundLogger, func_name: str, **kwargs: Any) -> None:
    """
    Log function call with parameters
    
    Args:
        logger: Logger instance
        func_name: Name of function being called
        **kwargs: Function parameters to log
    
    Example:
        log_function_call(logger, "send_message", query="test", session_id="123")
    """
    logger.debug("function_called", function=func_name, **kwargs)


def log_api_request(
    logger: FilteringBoundLogger,
    method: str,
    path: str,
    status_code: int = None,
    duration_ms: float = None,
    **kwargs: Any
) -> None:
    """
    Log API request with metadata
    
    Args:
        logger: Logger instance
        method: HTTP method (GET, POST, etc.)
        path: Request path
        status_code: HTTP status code
        duration_ms: Request duration in milliseconds
        **kwargs: Additional context
    
    Example:
        log_api_request(
            logger, 
            method="POST", 
            path="/api/v1/query",
            status_code=200,
            duration_ms=156.7
        )
    """
    logger.info(
        "api_request",
        method=method,
        path=path,
        status_code=status_code,
        duration_ms=duration_ms,
        **kwargs
    )


def log_cortex_call(
    logger: FilteringBoundLogger,
    service: str,
    operation: str,
    duration_ms: float = None,
    success: bool = True,
    **kwargs: Any
) -> None:
    """
    Log Snowflake Cortex service call
    
    Args:
        logger: Logger instance
        service: Cortex service name (analyst, complete, search, ml)
        operation: Operation performed
        duration_ms: Call duration in milliseconds
        success: Whether call succeeded
        **kwargs: Additional context
    
    Example:
        log_cortex_call(
            logger,
            service="analyst",
            operation="send_message",
            duration_ms=2341.5,
            success=True,
            query_length=45
        )
    """
    level = "info" if success else "error"
    getattr(logger, level)(
        "cortex_call",
        service=service,
        operation=operation,
        duration_ms=duration_ms,
        success=success,
        **kwargs
    )


"""
Example Usage:

    from utils.logging import configure_logging, get_logger
    
    # Configure logging (call once at application startup)
    configure_logging(level="DEBUG", development=True)
    
    # Get logger instance
    logger = get_logger(__name__)
    
    # Basic logging
    logger.info("application_started", version="2.0", environment="development")
    logger.debug("debug_message", component="setup", detail="Testing")
    logger.warning("warning_message", component="test", reason="Example")
    logger.error("error_occurred", error="Example error", component="test")
    
    # Structured context
    logger.info(
        "user_action",
        action="query", 
        user_id=123,
        query="What was the click rate?",
        component="orchestrator"
    )
    
    # Helper functions for common logging patterns
    from utils.logging import log_api_request, log_cortex_call
    
    log_api_request(
        logger,
        method="POST",
        path="/api/v1/query",
        status_code=200,
        duration_ms=156.7
    )
    
    log_cortex_call(
        logger,
        service="analyst",
        operation="send_message",
        duration_ms=2341.5,
        success=True
    )

Testing:
    Run the test script to verify logging is working:
    docker exec dia-orchestrator python /tests/test_logging.py
"""
