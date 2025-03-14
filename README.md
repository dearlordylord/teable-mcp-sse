# Teable MCP Server 

This setup runs the OpenAPI MCP Server (https://github.com/snaggle-ai/openapi-mcp-server) in Docker with mcp-proxy (https://github.com/sparfenyuk/mcp-proxy) to expose the MCP server over HTTP/SSE.

It's pre-loaded with teable openapi definition and contains the most used functions.

## Setup

1. Set your API token as an environment variable:

```bash
export OPENAPI_TOKEN=your_token_here
```

2. Build and start the Docker container:

```bash
docker-compose up --build
```

## Usage

Once running, the MCP server is available at:

```
http://localhost:8080/sse
```

The server will use the token from the OPENAPI_TOKEN environment variable passed at build time as the Bearer token for API requests.

## Configuration

- The OpenAPI definition is mounted from `./teable-openapi.json` to `/app/teable-openapi.json` in the container
- The server listens on port 8080
- Authorization headers are set using the OPENAPI_TOKEN environment variable

## Architecture

```
Client ⟷ HTTP/SSE ⟷ mcp-proxy ⟷ stdio ⟷ openapi-mcp-server
```

The mcp-proxy converts between HTTP/SSE and stdio protocols, allowing the openapi-mcp-server (which only supports stdio) to be accessible over HTTP.
