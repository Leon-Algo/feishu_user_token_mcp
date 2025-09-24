# Use Python 3.12 slim base image
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Install uv for faster dependency management
RUN pip install uv

# Copy project files
COPY . .

# Install dependencies and the package
RUN uv sync --frozen --no-dev

# Create startup script that starts the MCP server
RUN echo '#!/bin/bash\nset -e\nPORT=${PORT:-8080}\necho "Starting Feishu Token MCP server on port $PORT"\nexec uv run python -c "from feishu_token_mcp.server import create_server; import uvicorn; server = create_server(); uvicorn.run(server, host=\\"0.0.0.0\\", port=int(\\"$PORT\\"))"' > /app/start.sh && \
    chmod +x /app/start.sh

# Expose default port (Smithery will override with PORT env var)
EXPOSE 8080

# Set the command to run the MCP server
CMD ["/app/start.sh"]