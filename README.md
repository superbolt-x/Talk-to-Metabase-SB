# Talk to Metabase MCP

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
        "RESPONSE_SIZE_LIMIT": "100000",
        "ACTIVATE_METABASE_CONTEXT": "false"
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
| ACTIVATE_METABASE_CONTEXT | Whether to activate and enforce Metabase context guidelines | false |
| MCP_TRANSPORT | Transport method (stdio, sse, streamable-http) | stdio |
| LOG_LEVEL | Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL) | INFO |

### Metabase Context Guidelines

The server includes an optional context guidelines system that provides Claude with instance-specific information and best practices:

- **When `ACTIVATE_METABASE_CONTEXT=false` (default)**: All tools work normally without any requirements
- **When `ACTIVATE_METABASE_CONTEXT=true`**: 
  - Loads the `GET_METABASE_GUIDELINES` tool with essential context information
  - **Enforces** that this tool must be called first before using any other Metabase tools
  - Provides built-in guidelines with your instance URL and username automatically substituted
  - Helps ensure Claude has proper context about your Metabase setup before performing operations

**Important**: When context is activated, Claude will be required to call `GET_METABASE_GUIDELINES` at the beginning of any Metabase-related conversation. If you see enforcement errors, make sure the guidelines tool is enabled in your MCP client interface.

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
