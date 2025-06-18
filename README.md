# Talk to Metabase MCP

A Model Context Protocol (MCP) server that integrates Claude with Metabase, providing AI-powered data analysis, visualization, and dashboard management capabilities.

## Quick Start

### Download Prebuilt Executable

1. **Download** the appropriate executable for your platform from the [latest release](https://github.com/vincentgefflaut/talk-to-metabase/releases/latest):
   - `talk-to-metabase-macos-intel` - Intel Mac (x86_64)
   - `talk-to-metabase-macos-apple-silicon` - Apple Silicon Mac (M1/M2/M3)
   - `talk-to-metabase-linux` - Linux (x86_64)
   - `talk-to-metabase-windows.exe` - Windows (x86_64)

2. **Allow the executable to run** (macOS only):
   On macOS, you'll need to bypass the security warning the first time[^1]:
   - Right-click the executable and select "Open"
   - Click "Open" when prompted about unidentified developer
   - The executable will be trusted for future runs
[^1]: no Apple I won't pay a $99 developer license

3. **Configure Claude Desktop** (see Configuration section below)

4. **Restart Claude Desktop** and start chatting with your Metabase data!

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
    "Talk to Metabase": {
      "command": "/path/to/talk-to-metabase-[your-platform]",
      "args": [],
      "env": {
        "METABASE_URL": "https://your-metabase-instance.company.com",
        "METABASE_USERNAME": "user@example.com",
        "METABASE_PASSWORD": "your-password",
        "RESPONSE_SIZE_LIMIT": "100000",
        "METABASE_CONTEXT_AUTO_INJECT": "true"
      }
    }
  }
}
```

### Configuration Parameters

| Parameter | Description | Required | Default |
|-----------|-------------|----------|----------|
| METABASE_URL | Base URL of your Metabase instance | ✅ Yes | - |
| METABASE_USERNAME | Username for authentication | ✅ Yes | - |
| METABASE_PASSWORD | Password for authentication | ✅ Yes | - |
| RESPONSE_SIZE_LIMIT | Maximum size (in characters) for responses sent to Claude | No | 100000 |
| METABASE_CONTEXT_AUTO_INJECT | Whether to automatically load context guidelines | No | true |
| MCP_TRANSPORT | Transport method (stdio, sse, streamable-http) | No | stdio |
| LOG_LEVEL | Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL) | No | INFO |

### Metabase Context Guidelines

The server includes a context guidelines system that automatically retrieves organization-specific guidelines from your Metabase instance:

#### Custom Guidelines from Metabase

The system automatically looks for custom guidelines stored in your Metabase instance:

1. **Collection**: "000 Talk to Metabase" (must be at root level)
2. **Dashboard**: "Talk to Metabase Guidelines" (inside the collection above)
3. **Content**: Guidelines text stored in a text box on the dashboard

**Template Variables**: Your custom guidelines can use these variables:
- `{METABASE_URL}` - Automatically replaced with your Metabase instance URL
- `{METABASE_USERNAME}` - Automatically replaced with the configured username

#### Setup Instructions

To create custom guidelines for your organization:

1. **Create the Collection**:
   - Go to your Metabase instance
   - Create a collection named exactly: `000 Talk to Metabase`
   - Place it at the root level (not inside any other collection)
   - Make sure it's readable by all Talk to Metabase users

2. **Create the Guidelines Dashboard**:
   - Inside the "000 Talk to Metabase" collection
   - Create a dashboard named exactly: `Talk to Metabase Guidelines`
   - Add a text box to this dashboard
   - Write your custom guidelines in the text box

3. **Guidelines Content Suggestions**:
   Include information about:
   - Important collections and their purposes
   - Key databases and their usage guidelines
   - Naming conventions and data governance standards
   - Query performance recommendations
   - Common use cases and workflows specific to your organization
   - Contact information for data team or administrators

#### Behavior

- **When `METABASE_CONTEXT_AUTO_INJECT=true` (default)**:
  - Loads the `GET_METABASE_GUIDELINES` tool
  - Automatically retrieves custom guidelines from Metabase if configured
  - Falls back to default guidelines with setup instructions if not found
  - Tool description recommends calling it first for best results
  - No enforcement - all other tools work normally

- **When `METABASE_CONTEXT_AUTO_INJECT=false`**: The guidelines tool is not loaded

**Usage**: The guidelines tool is designed to be called at the beginning of Metabase conversations to provide Claude with helpful context about your instance, collections, databases, and best practices.

## Development

For developers who want to run from source or contribute to the project:

1. Clone this repository
2. Install with pip:
   ```bash
   pip install -e .
   ```
3. Run the server:
   ```bash
   python metabase_mcp.py
   ```

See [DEVELOPMENT.md](DEVELOPMENT.md) for detailed development instructions.

## Troubleshooting

### Windows Security Warning
If Windows Defender blocks the executable:
1. Click "More info" then "Run anyway"
2. Or add an exception in Windows Security

### Connection Issues
- Verify your Metabase URL is accessible
- Check your username and password
- Ensure your Metabase instance allows API access

## Usage

Once configured, Claude will automatically discover and use the Metabase tools for data analysis and visualization.

## License

See the LICENSE file for details.
