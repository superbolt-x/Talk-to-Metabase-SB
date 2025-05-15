# Testing SuperMetabase

This document provides instructions for testing the SuperMetabase MCP server.

## Prerequisites

1. Python 3.10 or higher
2. Access to a Metabase instance
3. Valid Metabase username and password

## Setup

1. Clone the repository and navigate to the project directory:

```bash
cd /Users/Pro/Workspace/SuperMetabase
```

2. Create a `.env` file with your Metabase credentials:

```bash
cp .env.example .env
```

3. Edit the `.env` file and provide your actual Metabase credentials:

```
METABASE_URL=https://your-metabase-instance.company.com
METABASE_USERNAME=your-username
METABASE_PASSWORD=your-password
MCP_TRANSPORT=stdio
LOG_LEVEL=INFO
```

## Installation

### Option 1: Use the installation script

For Unix/macOS:
```bash
chmod +x install.sh
./install.sh
```

For Windows:
```cmd
install.bat
```

### Option 2: Manual installation

```bash
# Create and activate a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install the package in development mode
pip install -e .
```

## Testing

### 1. Check Imports

First, test if the package structure is correct:

```bash
python test_import.py
```

If successful, you should see:
```
All imports successful!
SuperMetabase version: 0.1.0
Package structure seems correct.
```

### 2. Test Authentication

Test authentication with your Metabase instance:

```bash
python test_auth.py
```

This will attempt to authenticate with your Metabase instance and make a simple API call to retrieve the current user.

### 3. Run Unit Tests

Run the unit tests:

```bash
pytest -v tests/unit
```

### 5. Test Response Size Limits

Test the response size limitation feature:

```bash
python test_size_limit.py
```

This test will verify that responses that exceed the configured size limit are properly handled. You can configure the size limit in the `.env` file using the `RESPONSE_SIZE_LIMIT` parameter.

### 6. Run the MCP Server

Run the MCP server directly:

```bash
./metabase_mcp.py
```

Or with the MCP development tools:

```bash
mcp dev metabase_mcp.py
```

## Integrating with Claude Desktop

To integrate with Claude Desktop:

1. Install Claude Desktop from [claude.ai/download](https://claude.ai/download)

2. Configure Claude Desktop by editing the configuration file:

On macOS:
```bash
vi ~/Library/Application\ Support/Claude/claude_desktop_config.json
```

On Windows:
```bash
notepad %APPDATA%\Claude\claude_desktop_config.json
```

3. Add your SuperMetabase server configuration:

```json
{
  "mcpServers": {
    "metabase": {
      "command": "python",
      "args": ["/absolute/path/to/SuperMetabase/metabase_mcp.py"],
      "env": {
        "METABASE_URL": "https://your-metabase-instance.company.com",
        "METABASE_USERNAME": "your-username",
        "METABASE_PASSWORD": "your-password"
      }
    }
  }
}
```

4. Restart Claude Desktop

5. Test the integration by asking Claude questions about your Metabase resources
