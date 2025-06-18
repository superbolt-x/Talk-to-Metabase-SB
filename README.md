# Talk to Metabase MCP

A Model Context Protocol (MCP) server that integrates Claude with Metabase, providing AI-powered data analysis, visualization, and dashboard management capabilities.

## Overview

This MCP server implements the [Model Context Protocol](https://modelcontextprotocol.io/) specification to connect Claude with Metabase, allowing Claude to:

- **📊 Database Operations**: List databases, explore schemas and tables, get field metadata
- **🔍 Search & Discovery**: Search across all Metabase resources with advanced filtering
- **📈 Cards (Questions)**: Create, read, update SQL cards with visualization settings
- **📋 Dashboards**: Create, view, and update dashboards with cards, tabs, and parameters
- **📁 Collections**: Navigate collection hierarchies and view contents
- **⚙️ Query Execution**: Run SQL queries directly or execute card queries with dashboard context
- **🎨 Visualization Settings**: Comprehensive support for 17 chart types with JSON schema validation
- **📝 Context Guidelines**: Custom organization-specific guidelines stored in Metabase

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

## Key Features & Capabilities

### 🎯 Advanced Dashboard Management
- **Cards Management**: Add/update dashboard cards with precise grid positioning (24-column system)
- **Tabs Support**: Create and manage multi-tab dashboards
- **Parameters**: Add interactive filters with type validation and auto-ID generation
- **Grid Validation**: Automatic validation of positioning and size constraints
- **Schema Validation**: JSON schema validation for all dashboard components

### 📊 Comprehensive Visualization Support
- **17 Chart Types**: Full support for all Metabase visualization types except pivot tables
- **JSON Schema Validation**: Built-in validation for visualization settings
- **Documentation System**: Complete documentation with examples for each chart type
- **UI/API Name Mapping**: Supports both UI names (e.g., "number") and API names (e.g., "scalar")

### 🔧 Simplified Parameter System
- **3 Basic Types**: Streamlined to category, number/=, and date/single parameter types
- **Automatic Validation**: JSON Schema handles most validation automatically
- **Required Defaults**: All parameters must have default values for reliable query execution
- **Template Tag Linking**: Parameter names directly correspond to {{template_tags}} in SQL
- **UI Widget Control**: Clear mapping between parameter types and UI widgets (dropdown, search, input)

### 🔄 Smart Query Execution
- **Dual Context Support**: Execute queries both standalone and within dashboard context
- **SQL Validation**: Pre-validation of SQL queries before card creation
- **MBQL Translation**: Automatic translation of MBQL queries to SQL for better understanding when reading a card
- **Template Variables**: Support for customizable filters using {{variable}} syntax

### 📐 Performance Optimization
- **Response Size Management**: Configurable response size limits with automatic checking
- **Simplified Outputs**: Essential-field-only responses for better performance
- **Pagination**: Client-side pagination for large datasets (dashboards, search results)
- **Essential Information**: Streamlined responses focusing on actionable data

### 🏢 Organization Context
- **Custom Guidelines**: Store organization-specific guidelines in Metabase itself
- **Template Variables**: Support for `{METABASE_URL}` and `{METABASE_USERNAME}` in guidelines
- **Automatic Discovery**: Finds guidelines in "000 Talk to Metabase" collection
- **Fallback System**: Provides setup instructions when custom guidelines aren't configured

## Not Yet Implemented

### 🚧 Planned Features
- **Models** : Build and use models
- **Complex parameters**: Advanced parameter types and field filters (simplified system focuses on basic types)
- **Safe mode**: Disable editing features for read-only users
- **Auto-debug mode**: Always run a query before pushing it
- **MQBL support**: Create and edit UI-built cards
- **Pivot tables**: Handle pivot tables visualization settings (only works with MBQL questions)

## Architecture Highlights

### Modular Tool Design
- **Specialized Modules**: Separate modules for different resource types
- **Shared Utilities**: Common functions for error handling, validation, and response formatting
- **Schema-Driven Validation**: JSON schemas for complex data structures

### Robust Error Handling
- **Structured Error Responses**: Consistent error format across all tools
- **Detailed Validation**: Clear validation errors with specific guidance
- **Request Context**: Error responses include request details for debugging

### Efficient Validation Architecture
- **JSON Schema First**: Leverages JSON Schema for automatic validation of structure, types, and business rules
- **Minimal Manual Validation**: Only handles cross-item validation (duplicates) that JSON Schema cannot express
- **Conditional Requirements**: Uses JSON Schema if/then patterns for complex validation rules

### Authentication & Session Management
- **Session Caching**: Automatic session token management
- **Re-authentication**: Automatic re-authentication on token expiry
- **Environment Configuration**: Secure credential management

## Existing tools in detail

#### Database & Table Operations
- **`list_databases`** - List all available databases (simplified output)
- **`get_database_metadata`** - Get database schema and table information
- **`get_table_query_metadata`** - Get detailed table field metadata for query building

#### Card (Question) Operations
- **`get_card_definition`** - Get card metadata and query definition (with MBQL→SQL translation)
- **`create_card`** - Create new SQL cards with query validation and simplified parameter system
- **`update_card`** - Update existing cards with new queries, metadata, or visualization settings
- **`execute_card_query`** - Execute card queries in standalone or dashboard context
- **`GET_CARD_PARAMETERS_SCHEMA`** - Get simplified JSON schema for card parameters validation

#### Dashboard Operations
- **`get_dashboard`** - Get dashboard metadata without card details
- **`create_dashboard`** - Create new dashboards
- **`update_dashboard`** - Add cards, tabs, parameters, and update metadata with full validation
- **`get_dashboard_tab`** - Get paginated cards for specific dashboard tabs

#### Collection Operations
- **`explore_collection_tree`** - Navigate collection hierarchy (shows subcollections + content summary)
- **`view_collection_contents`** - View all items in a collection with optional filtering

#### Search Operations
- **`search_resources`** - Comprehensive search with pagination and filtering across all resource types

#### Query Operations
- **`run_dataset_query`** - Execute native SQL or MBQL queries directly against databases

#### Visualization Settings (17 Chart Types)
- **`GET_VISUALIZATION_DOCUMENT`** - Get documentation and schema for any chart type
- **Supported chart types**: table, line, bar, combo, pie, row, area, object (detail), funnel, gauge, progress, sankey, scalar (number), scatter, smartscalar (trend), map, waterfall

#### Dashboard Enhancement Tools
- **`GET_DASHCARDS_SCHEMA`** - Get schema for dashboard card validation
- **`GET_PARAMETERS_SCHEMA`** - Get schema for dashboard parameter validation

#### Context Guidelines
- **`GET_METABASE_GUIDELINES`** - Retrieve custom organization guidelines from Metabase or default setup instructions

## Metabase Context Guidelines

The server includes a context guidelines system that automatically retrieves organization-specific guidelines from your Metabase instance:

### Custom Guidelines from Metabase

The system automatically looks for custom guidelines stored in your Metabase instance:

1. **Collection**: "000 Talk to Metabase" (must be at root level i.e. in "Our Analytics")
2. **Dashboard**: "Talk to Metabase Guidelines" (inside the collection above)
3. **Content**: Guidelines text stored in a text box on the dashboard

**Template Variables**: Your custom guidelines can use these variables:
- `{METABASE_URL}` - Automatically replaced with your Metabase instance URL
- `{METABASE_USERNAME}` - Automatically replaced with the configured username

### Setup Instructions

To create custom guidelines for your organization:

1. **Create the Collection**:
   - Go to your Metabase instance
   - Create a collection named exactly: `000 Talk to Metabase`
   - Place it at the root level - also called "Our Analytics" (not inside any other collection)
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

### Behavior

- **When `METABASE_CONTEXT_AUTO_INJECT=true` (default)**:
  - Loads the `GET_METABASE_GUIDELINES` tool
  - Automatically retrieves custom guidelines from Metabase if configured
  - Falls back to default guidelines with setup instructions if not found
  - Tool description recommends calling it first for best results
  - No enforcement - all other tools work normally

- **When `METABASE_CONTEXT_AUTO_INJECT=false`**: The guidelines tool is not loaded

## Usage Examples

### Creating a Card with Visualization Settings

```json
// First, get documentation for the chart type
GET_VISUALIZATION_DOCUMENT(chart_type="bar")

// Then create the card with settings
create_card(
  database_id=195,
  query="SELECT category, SUM(revenue) FROM sales GROUP BY category",
  name="Revenue by Category",
  display="bar",
  visualization_settings={
    "graph.dimensions": ["category"],
    "graph.metrics": ["sum"],
    "graph.colors": ["#509EE3", "#88BF4D", "#A989C5"]
  }
)
```

### Managing Dashboard with Cards and Parameters

```json
// Get dashboard structure first
get_dashboard(id=1864)

// Add cards and parameters
update_dashboard(
  id=1864,
  dashcards=[
    {
      "id": -1,
      "card_id": 53832,
      "col": 0,
      "row": 0,
      "size_x": 12,
      "size_y": 8
    }
  ],
  parameters=[
    {
      "name": "Date Range",
      "type": "date/range",
      "sectionId": "date"
    }
  ]
)
```

### Exploring Data Structure

```json
// Start with databases
list_databases()

// Explore specific database
get_database_metadata(id=195)

// Get table details for queries
get_table_query_metadata(id=50112)
```

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

## Dependencies

- **Python 3.10+**: Required for modern async features and type hints
- **MCP SDK**: Model Context Protocol implementation
- **httpx**: Modern async HTTP client for Metabase API calls
- **pydantic**: Data validation and settings management
- **jsonschema**: JSON schema validation for complex data structures
- **python-dotenv**: Environment variable management

## Troubleshooting

### Windows Security Warning
If Windows Defender blocks the executable:
1. Click "More info" then "Run anyway"
2. Or add an exception in Windows Security

### Connection Issues
- Verify your Metabase URL is accessible
- Check your username and password
- Ensure your Metabase instance allows API access

### Performance Issues
- Adjust `RESPONSE_SIZE_LIMIT` if responses are too large
- Use pagination parameters for large datasets
- Consider using simplified tools for exploration before detailed operations

## Contributing

This project is actively developed and welcomes contributions. Key areas for contribution:

- **New Tools**: Implement remaining Metabase API endpoints
- **Visualization Enhancements**: Add support for more complex visualization settings
- **Testing**: Expand test coverage for edge cases
- **Documentation**: Improve tool documentation and examples
- **Performance**: Optimize response handling and caching

## License

See the LICENSE file for details.
