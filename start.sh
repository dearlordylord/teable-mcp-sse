#!/bin/bash
set -e

# Set authorization header with the token passed from environment
HEADERS="{\"Authorization\": \"Bearer $OPENAPI_TOKEN\"}"
export OPENAPI_MCP_HEADERS="$HEADERS"

echo "Starting openapi-mcp-server with proxy..."
echo "Using headers: $OPENAPI_MCP_HEADERS"

# Install the server locally 
cd /app/openapi-mcp-server && npm link

# Start the proxy in SSE server mode, passing through to the CLI tool
mcp-proxy --sse-port=8080 --sse-host=0.0.0.0 --pass-environment -- openapi-mcp-server /app/teable-openapi.json