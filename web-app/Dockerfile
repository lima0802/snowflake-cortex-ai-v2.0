# syntax=docker/dockerfile:1
# ============================================================================
# Multi-Stage Dockerfile with UV for Streamlit Web App
# ============================================================================

# ============================================================================
# Stage 1: Builder - Install dependencies with UV
# ============================================================================
FROM ghcr.io/astral-sh/uv:python3.11-bookworm-slim AS builder

WORKDIR /app

# Copy dependency files
COPY pyproject.toml ./

# Install dependencies into a virtual environment
RUN uv venv /app/.venv && \
    uv pip install -r pyproject.toml

# ============================================================================
# Stage 2: Production - Slim runtime image
# ============================================================================
FROM python:3.11-slim AS production

WORKDIR /app

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH="/app/.venv/bin:$PATH"

# Install curl for healthcheck
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

# Expose port for Streamlit
EXPOSE 8501

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl --fail http://localhost:8501/_stcore/health || exit 1

# Run Streamlit
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]

# ============================================================================
# Stage 3: Development - Include dev tools
# ============================================================================
FROM production AS development

USER root

# Install development dependencies
RUN uv pip install pytest black ruff

USER appuser

# Development mode with file watching
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0", "--server.runOnSave=true"]
