# Use Python 3.12 slim base image
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Copy dependency files first for better caching
COPY pyproject.toml uv.lock ./

# Install uv for faster dependency management
RUN pip install uv

# Install project dependencies
RUN uv sync --frozen --no-dev

# Copy the rest of the project files
COPY . .

# Create the package in the environment
RUN uv sync --frozen --no-dev

# Create startup script
RUN echo '#!/bin/bash\nset -e\nPORT=${PORT:-8080}\necho "Starting Feishu Token MCP server on port $PORT"\nexec uv run smithery.cli.dev:main --host 0.0.0.0 --port $PORT --transport shttp' > /app/start.sh && \
    chmod +x /app/start.sh

# Expose default port (Smithery will override with PORT env var)
EXPOSE 8080

# Set the command to run the MCP server
CMD ["/app/start.sh"]