FROM node:18-slim AS node-base

# Clone and install openapi-mcp-server from GitHub
WORKDIR /app
RUN apt-get update && apt-get install -y git && \
    git clone https://github.com/snaggle-ai/openapi-mcp-server.git && \
    cd openapi-mcp-server && \
    npm install && \
    npm run build

# Use a Python image that also has Node.js
FROM python:3.11-slim

WORKDIR /app

# Install Node.js
RUN apt-get update && apt-get install -y \
    curl \
    gnupg \
    && curl -fsSL https://deb.nodesource.com/setup_18.x | bash - \
    && apt-get install -y nodejs \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy from node base
COPY --from=node-base /app/openapi-mcp-server /app/openapi-mcp-server

# Install mcp-proxy 
RUN pip install --no-cache-dir mcp-proxy

# Copy OpenAPI spec file
COPY ./teable-openapi.json /app/teable-openapi.json

# Script to start the services
COPY start.sh /app/start.sh
RUN chmod +x /app/start.sh

# Expose the port for mcp-proxy SSE server
EXPOSE 8080

CMD ["/app/start.sh"]