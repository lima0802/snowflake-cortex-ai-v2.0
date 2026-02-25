# syntax=docker/dockerfile:1
# ============================================================================
# Multi-Stage Dockerfile with UV for Fast Dependency Management
# ============================================================================
# This Dockerfile uses Astral's UV package manager for 10-100x faster builds
# compared to pip. Perfect for CI/CD pipelines with Snowflake dependencies.
# ============================================================================

# ============================================================================
# Stage 1: Builder - Install dependencies with UV
# ============================================================================
FROM ghcr.io/astral-sh/uv:python3.11-bookworm-slim AS builder

WORKDIR /app

# Copy dependency files
COPY pyproject.toml ./
# If you have uv.lock, copy it too for locked dependencies
# COPY uv.lock ./

# Install dependencies into a virtual environment
# --frozen: Use exact versions from lock file (if exists)
# --no-dev: Skip development dependencies in production
RUN uv venv /app/.venv && \
    uv pip install -r pyproject.toml

# ============================================================================
# Stage 2: Production - Slim runtime image
# ============================================================================
FROM python:3.11-slim AS production

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH="/app/.venv/bin:$PATH"

# Install minimal runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy virtual environment from builder
COPY --from=builder /app/.venv /app/.venv

# Copy application code
COPY . .

# Create non-root user for security
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app
USER appuser

# Expose port for FastAPI
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:8000/api/v1/health || exit 1

# Run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

# ============================================================================
# Stage 3: Development - Include dev tools
# ============================================================================
FROM production AS development

USER root

# Install development dependencies
RUN uv pip install pytest pytest-asyncio pytest-cov black ruff mypy

# Switch back to non-root user
USER appuser

# Development command with auto-reload
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
