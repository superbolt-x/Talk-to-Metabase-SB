# SuperMetabase MCP

A Model Context Protocol (MCP) server that integrates Claude with Metabase, providing AI-powered data analysis, visualization, and dashboard management capabilities.

## Overview

This MCP server implements the [Model Context Protocol](https://modelcontextprotocol.io/) specification to connect Claude with Metabase, allowing Claude to:

- Access and manage Metabase resources (dashboards, cards, collections)
- Execute queries against databases configured in Metabase
- Create and modify visualizations
- Search and discover resources across Metabase

## Configuration

Configure the server through environment variables or directly in the Claude Desktop configuration file:

```json
{
  "mcpServers": {
    "metabase": {
      "command": "path-to-metabase-mcp-server",
      "args": ["--config", "stdio"],
      "env": {
        "METABASE_URL": "https://your-metabase-instance.company.com",
        "METABASE_USERNAME": "user@example.com",
        "METABASE_PASSWORD": "your-password",
        "RESPONSE_SIZE_LIMIT": "100000"
      }
    }
  }
}
```

### Configuration Parameters

| Parameter | Description | Default |
|-----------|-------------|--------|
| METABASE_URL | Base URL of your Metabase instance | (Required) |
| METABASE_USERNAME | Username for authentication | (Required) |
| METABASE_PASSWORD | Password for authentication | (Required) |
| RESPONSE_SIZE_LIMIT | Maximum size (in characters) for responses sent to Claude | 100000 |
| MCP_TRANSPORT | Transport method (stdio, sse, streamable-http) | stdio |
| LOG_LEVEL | Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL) | INFO |

## Installation

1. Clone this repository
2. Install with pip:
   ```
   pip install -e .
   ```

## Usage

Once configured, Claude will automatically discover and use the Metabase tools for data analysis and visualization.

## License

See the LICENSE file for details.
