# Talk to Metabase MCP Server

An advanced Model Context Protocol (MCP) server designed for LLM clients like Claude, seamlessly integrating AI assistants with Metabase to provide AI-powered data analysis, visualization, and dashboard management capabilities.

## 🚀 What is Talk to Metabase?

Talk to Metabase is a sophisticated MCP server that transforms LLM clients like Claude into powerful data analysts capable of:

- **🔍 Exploring your data**: Browse databases, tables, and schemas with ease
- **📊 Creating visualizations**: Build charts, graphs, and dashboards using natural language
- **🎯 Running queries**: Execute SQL and MBQL queries with intelligent parameter handling
- **📋 Managing dashboards**: Create, update, and organize interactive dashboards
- **🔧 Advanced filtering**: Set up sophisticated filters and parameters for dynamic data exploration
- **📈 17 Chart Types**: Full support for all Metabase visualization types with comprehensive settings

## ⚡ Quick Start

### Option 1: Download Prebuilt Executable (Recommended)

1. **Download** the appropriate executable for your platform from the [latest release](https://github.com/vincentgefflaut/talk-to-metabase/releases/latest):
   - `talk-to-metabase-macos-intel.tar.gz` - Intel Mac (x86_64)
   - `talk-to-metabase-macos-apple-silicon.tar.gz` - Apple Silicon Mac (M1/M2/M3)
   - `talk-to-metabase-linux.tar.gz` - Linux (x86_64)
   - `talk-to-metabase-windows.exe` - Windows (x86_64)

2. **Extract the archive** (macOS/Linux):
   ```bash
   # macOS/Linux - Extract the tar.gz file
   tar -xzf talk-to-metabase-*.tar.gz
   ```

3. **Allow execution** (macOS only):
   - Right-click the extracted executable and select "Open"
   - Click "Open" when prompted about unidentified developer

3. **Configure Claude Desktop** (see [Configuration](#configuration) section)

4. **Restart Claude Desktop** and start exploring your data!

### Option 2: Run from Source

```bash
# Clone the repository
git clone https://github.com/vincentgefflaut/talk-to-metabase.git
cd talk-to-metabase

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -e .
```

Then configure Claude Desktop to use the virtual environment:

```json
{
  "mcpServers": {
    "Talk to Metabase": {
      "command": "/absolute/path/to/talk-to-metabase/venv/bin/python",
      "args": ["/absolute/path/to/talk-to-metabase/metabase_mcp.py"],
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

## 🛠️ Configuration

Add this configuration to your Claude Desktop settings:

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

**Note**: For executables extracted from tar.gz files, use the full path to the extracted executable file.

### Configuration Parameters

| Parameter | Description | Required | Default |
|-----------|-------------|----------|---------|
| `METABASE_URL` | Base URL of your Metabase instance | ✅ Yes | - |
| `METABASE_USERNAME` | Username for authentication | ✅ Yes | - |
| `METABASE_PASSWORD` | Password for authentication | ✅ Yes | - |
| `RESPONSE_SIZE_LIMIT` | Maximum response size in characters | No | 100000 |
| `METABASE_CONTEXT_AUTO_INJECT` | Auto-load context guidelines | No | true |
| `MCP_TRANSPORT` | Transport method (stdio, sse, streamable-http) | No | stdio |
| `LOG_LEVEL` | Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL) | No | INFO |

## 🎯 Key Features & Capabilities

### 🗄️ Database & Data Operations
- **Database Exploration**: List databases, browse schemas and tables
- **Field Metadata**: Get detailed information about table fields for query building
- **Smart Search**: Search across all Metabase resources with advanced filtering
- **Query Execution**: Run SQL and MBQL queries with full parameter support

### 📊 Card (Question) Management
- **Create & Edit**: Build SQL cards with automatic query validation
- **Parameter System**: Comprehensive support for interactive filters
- **Visualization Settings**: Configure 17 chart types with JSON schema validation
- **MBQL Support**: Full Metabase Query Language support for database-agnostic queries

### 📋 Dashboard Operations
- **Dashboard Creation**: Build interactive dashboards with drag-and-drop precision
- **Multi-Tab Support**: Create complex dashboards with multiple tabs
- **Parameter Linking**: Connect dashboard filters to card parameters
- **Grid System**: 24-column responsive grid with automatic validation

### 🎨 Visualization Excellence
- **17 Chart Types**: Complete support for all Metabase visualizations
- **Rich Customization**: Colors, labels, axes, legends, and formatting options
- **Click Behaviors**: Interactive elements with crossfilter and drill-down capabilities
- **Schema Validation**: Built-in validation prevents configuration errors

### 🔧 Advanced Parameter System
- **Simple Variables**: Text, number, and date parameters for dynamic queries
- **Field Filters**: Database-connected filters that link directly to columns
- **UI Widgets**: Dropdown, search, and input widgets with automatic value population
- **Multi-Select Support**: Advanced filtering with multiple value selection

### 🏢 Organization Context
- **Custom Guidelines**: Store organization-specific data guidelines in Metabase
- **Template Variables**: Dynamic replacement of URLs and usernames
- **Automatic Discovery**: Finds guidelines in designated collection
- **Contextual Help**: Provides relevant guidance based on your organization's setup

## 🏢 Metabase Context Guidelines

The server includes a powerful context guidelines system that automatically retrieves organization-specific guidelines from your Metabase instance, providing contextual help tailored to your organization's data practices.

### How It Works

When `METABASE_CONTEXT_AUTO_INJECT=true` (default), the system automatically looks for custom guidelines stored in your Metabase instance and makes them available to Claude through the `GET_METABASE_GUIDELINES` tool.

### Setting Up Custom Guidelines

To create custom guidelines for your organization:

1. **Create the Collection**:
   - Go to your Metabase instance
   - Navigate to "Our Analytics" (the root collection)
   - Create a new collection named exactly: **`000 Talk to Metabase`**
   - Ensure it's readable by all users who will use Talk to Metabase

2. **Create the Guidelines Dashboard**:
   - Inside the "000 Talk to Metabase" collection
   - Create a new dashboard named exactly: **`Talk to Metabase Guidelines`**
   - Add a text card to this dashboard
   - Write your custom guidelines in the text card

3. **Guidelines Content Suggestions**:
   Your custom guidelines should include:
   - **Important collections and their purposes**
   - **Key databases and their usage guidelines** 
   - **Naming conventions and data governance standards**
   - **Query performance recommendations**
   - **Common use cases and workflows** specific to your organization
   - **Contact information** for data team or administrators
   - **Security and access guidelines**
   - **Custom context** any organization-specific context that might be useful to the AI assistant

### Template Variables

Your custom guidelines can use these template variables that will be automatically replaced:

- **`{METABASE_URL}`** - Replaced with your Metabase instance URL
- **`{METABASE_USERNAME}`** - Replaced with the configured username

Example:
```
Welcome to our company's data platform! 

Our Metabase instance ({METABASE_URL}) contains three main databases:
- Production Analytics: Customer and sales data
- Marketing Data: Campaign performance and attribution
- Financial Data: Revenue and cost analysis

For questions, contact the data team at data-team@company.com
or your current user account: {METABASE_USERNAME}
```

### Default Behavior

- **When custom guidelines are configured**: Claude automatically loads your organization-specific guidelines
- **When not configured**: The system provides default setup instructions and general guidance
- **Performance**: Guidelines are cached and only loaded when needed

### Benefits

- **Contextual Guidance**: Provides relevant help specific to your data environment
- **Consistent Standards**: Ensures all users follow your organization's data practices
- **Reduced Support**: Self-service guidance reduces data team support requests
- **Governance Integration**: Embeds data governance directly in the AI workflow

## 🛠️ Available Tools

### Database Operations
- `list_databases` - List all available databases
- `get_database_metadata` - Get database schema and table information
- `get_table_query_metadata` - Get detailed field metadata for query building

### Card (Question) Operations
- `get_card_definition` - Get card metadata with MBQL→SQL translation
- `create_card` - Create new cards with comprehensive validation
- `update_card` - Update existing cards with new queries or settings
- `execute_card_query` - Execute card queries in standalone or dashboard context

### Dashboard Operations
- `get_dashboard` - Get dashboard metadata and structure
- `create_dashboard` - Create new dashboards with full configuration
- `update_dashboard` - Add cards, tabs, parameters with validation
- `get_dashboard_tab` - Get paginated cards for specific dashboard tabs

### Collection Operations
- `explore_collection_tree` - Navigate collection hierarchy
- `view_collection_contents` - View all items in a collection with filtering

### Search & Discovery
- `search_resources` - Comprehensive search across all Metabase resources

### Query Operations
- `run_dataset_query` - Execute SQL or MBQL queries directly

### Visualization & Documentation
- `GET_VISUALIZATION_DOCUMENT` - Get documentation for any chart type
- `GET_CARD_PARAMETERS_DOCUMENTATION` - Complete parameter system guide
- `GET_DASHBOARD_PARAMETERS_DOCUMENTATION` - Dashboard filter documentation
- `GET_DASHCARDS_SCHEMA` - Schema for dashboard card validation
- `GET_METABASE_GUIDELINES` - Organization-specific guidelines

## 💡 Usage Examples

### Creating a Chart with Custom Visualization

```python
# Get documentation for the chart type
GET_VISUALIZATION_DOCUMENT(chart_type="bar")

# Create a bar chart with custom settings
create_card(
    database_id=195,
    query="SELECT category, SUM(revenue) FROM sales GROUP BY category",
    name="Revenue by Category",
    display="bar",
    visualization_settings={
        "graph.dimensions": ["category"],
        "graph.metrics": ["sum"],
        "graph.show_values": true,
        "graph.colors": ["#509EE3", "#88BF4D", "#A989C5"]
    }
)
```

### Building an Interactive Dashboard

```python
# Create dashboard with parameters and cards
update_dashboard(
    id=1864,
    parameters=[
        {
            "name": "Date Range",
            "type": "date/range",
            "default": "past30days"
        },
        {
            "name": "Category Filter",
            "type": "string/=",
            "default": ["electronics"],
            "values_source": {
                "type": "static",
                "values": ["electronics", "books", "clothing"]
            }
        }
    ],
    dashcards=[
        {
            "id": -1,
            "card_id": 53832,
            "col": 0,
            "row": 0,
            "size_x": 12,
            "size_y": 8,
            "parameter_mappings": [
                {
                    "dashboard_parameter_name": "Date Range",
                    "card_parameter_name": "date_filter"
                }
            ]
        }
    ]
)
```

### Creating Cards with Interactive Parameters

```python
# Create a card with field filters
create_card(
    database_id=195,
    query="SELECT * FROM orders WHERE {{date_filter}} AND {{status_filter}}",
    name="Filtered Orders",
    parameters=[
        {
            "name": "date_filter",
            "type": "date/range",
            "field": {"database_id": 195, "table_id": 1001, "field_id": 5001},
            "default": "past30days"
        },
        {
            "name": "status_filter",
            "type": "string/=",
            "field": {"database_id": 195, "table_id": 1001, "field_id": 5002},
            "ui_widget": "dropdown",
            "values_source": {"type": "connected"}
        }
    ]
)
```

## 🎨 Supported Chart Types

| Chart Type | Display Name | Description | Key Features |
|------------|--------------|-------------|--------------|
| `table` | Data Table | Tabular data display | Conditional formatting, sorting, mini-charts |
| `bar` | Bar Chart | Vertical bar charts | Stacking, grouping, value labels |
| `line` | Line Chart | Line graphs | Multiple series, trend lines, markers |
| `area` | Area Chart | Filled area graphs | Stacking, transparency, series blending |
| `pie` | Pie Chart | Circular charts | Slice customization, legends, percentages |
| `combo` | Combo Chart | Mixed chart types | Dual axes, line + bar combinations |
| `scatter` | Scatter Plot | X/Y point plots | Bubble sizing, trend analysis |
| `funnel` | Funnel Chart | Conversion analysis | Stage progression, drop-off rates |
| `gauge` | Gauge Chart | KPI displays | Color segments, goal tracking |
| `scalar` | Number | Single metrics | Formatting, prefixes, suffixes |
| `smartscalar` | Trend | Comparison metrics | Period-over-period analysis |
| `map` | Geographic Map | Location data | Regions, pins, heat maps |
| `waterfall` | Waterfall Chart | Cumulative changes | Positive/negative flows |
| `sankey` | Sankey Diagram | Flow visualization | Multi-step processes |
| `progress` | Progress Bar | Goal completion | Percentage tracking |
| `row` | Horizontal Bar | Horizontal charts | Category comparisons |
| `object` | Detail View | Record display | Single item focus |

## 🔧 Advanced Features

### Parameter Types

**Simple Variables** (use in SQL as `{{variable}}`):
- `category` - Text selection with dropdown/search
- `number/=` - Number input with optional dropdown
- `date/single` - Date picker for single dates

**Field Filters** (use in SQL as `WHERE {{field_filter}}`):
- String filters: `string/=`, `string/contains`, `string/starts-with`, etc.
- Number filters: `number/between`, `number/>=`, `number/<=`, etc.
- Date filters: `date/range`, `date/relative`, `date/all-options`, etc.

### Multi-Select Dashboard Parameters

Dashboard parameters support multi-select by default for:
- ✅ All string types (`string/=`, `string/!=`, `string/contains`, etc.)
- ✅ Number equality (`number/=`, `number/!=`)
- ✅ ID parameters
- ✅ Location parameters
- ❌ Date parameters (single values only)
- ❌ Number ranges (single ranges only)

### MBQL Query Support

Create database-agnostic queries using Metabase Query Language:

```python
create_card(
    database_id=195,
    query_type="query",  # MBQL instead of SQL
    query={
        "source-table": 1,
        "aggregation": [["sum", ["field", 123, null]]],
        "breakout": [["field", 456, {"temporal-unit": "month"}]],
        "filter": ["=", ["field", 789, null], "active"]
    },
    name="Monthly Revenue by Status"
)
```

## 📚 Documentation System

The server includes comprehensive built-in documentation:

- **`GET_VISUALIZATION_DOCUMENT`** - Complete chart type documentation with examples
- **`GET_CARD_PARAMETERS_DOCUMENTATION`** - Parameter system guide with SQL patterns
- **`GET_DASHBOARD_PARAMETERS_DOCUMENTATION`** - Dashboard filter configuration
- **`GET_DASHCARDS_SCHEMA`** - Dashboard card positioning and validation
- **`GET_METABASE_GUIDELINES`** - Organization-specific guidelines

## 🏗️ Architecture Highlights

### Modular Design
- **Specialized Tools**: Separate modules for different resource types
- **Shared Utilities**: Common functions for error handling and validation
- **Schema-Driven**: JSON schemas for automatic validation

### Robust Error Handling
- **Structured Responses**: Consistent error format across all tools
- **Detailed Validation**: Clear errors with specific guidance
- **Context Preservation**: Error responses include request details

### Performance Optimization
- **Response Size Management**: Configurable limits with automatic checking
- **Efficient Validation**: Schema-first approach minimizes code complexity
- **Smart Pagination**: Client-side pagination for large datasets

### Security & Authentication
- **Session Management**: Automatic token handling and re-authentication
- **Environment Configuration**: Secure credential management
- **Error Isolation**: Prevents sensitive information leakage

## 🚧 Planned Features

- **Models Support**: Build and use Metabase models
- **Dashboard Parameter Mapping to MBQL**: Connect dashboard parameters to MBQL-based cards
- **Safe Mode**: Read-only mode for restricted users
- **Auto-Debug**: Automatic query validation before execution
- **Pivot Tables**: Complete pivot table support

## 🔍 Troubleshooting

### Common Issues

**Connection Problems**:
- Verify your Metabase URL is accessible
- Check username/password credentials
- Ensure Metabase allows API access

**Performance Issues**:
- Adjust `RESPONSE_SIZE_LIMIT` for large datasets
- Use pagination for dashboard exploration
- Consider query optimization for complex operations

**Windows Security**:
- If Windows Defender blocks the executable, click "More info" then "Run anyway"
- Add an exception in Windows Security if needed

**macOS Security**:
- Right-click executable and select "Open"
- Click "Open" when prompted about unidentified developer

### Getting Help

1. Check the built-in documentation tools first
2. Review error messages for specific guidance
3. Consult the comprehensive examples in tool documentation
4. Verify your Metabase version compatibility

## 🤝 Contributing

We welcome contributions! Key areas for enhancement:

- **New Tools**: Implement additional Metabase API endpoints
- **Visualization Features**: Expand chart customization options
- **Documentation**: Enhance examples and use cases
- **Performance**: Optimize response handling and caching

## 📋 Dependencies

- **Python 3.10+**: Modern async features and type hints
- **MCP SDK**: Model Context Protocol implementation
- **httpx**: Async HTTP client for Metabase API
- **pydantic**: Data validation and settings management
- **jsonschema**: JSON schema validation for complex structures
- **python-dotenv**: Environment variable management

## 📄 License

This project is licensed under the terms specified in the LICENSE file.

---

**Ready to transform your data analysis workflow?** Download Talk to Metabase and start exploring your data with the power of AI!
