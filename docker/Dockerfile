FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy package files
COPY pyproject.toml README.md LICENSE ./
COPY src/ ./src/
COPY examples/ ./examples/

# Install package
RUN pip install --no-cache-dir -e ".[simroute]"

# Create directories for logs and data
RUN mkdir -p /app/data /app/logs /app/docs/run

# Set environment variables
ENV RUN_LOG_DIR=/app/docs/run
ENV RUN_LOG_WRITE_COMPAT=0
ENV PYTHONPATH=/app

# Expose any necessary ports (if needed for future web UI)
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD srd --help || exit 1

# Default command
CMD ["srd", "--help"]