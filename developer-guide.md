## SQL Parameter Usage and Validation

Talk to Metabase implements comprehensive SQL parameter validation to prevent common AI assistant mistakes when writing SQL with Metabase parameters. This system addresses critical issues with parameter substitution understanding.

### Critical Parameter Substitution Rules

#### ⚠️ Common AI Assistant Mistakes to AVOID

**❌ WRONG: Adding quotes around parameters**
```sql
-- DON'T DO THIS - WRONG!
CASE 
    WHEN '{{metric_type}}' = 'spend' THEN spend    -- Extra quotes!
    WHEN '{{metric_type}}' = 'impressions' THEN impressions
END

-- DON'T DO THIS - WRONG!
WHERE channel = '{{channel_param}}'               -- Double quotes!

-- DON'T DO THIS - WRONG!
WHERE customer_name = {{customer_filter}}         -- Field filter used as value!
```

**✅ CORRECT: Parameters substitute with proper formatting**
```sql
-- CORRECT - Simple variable parameters
CASE 
    WHEN {{metric_type}} = 'spend' THEN spend      -- No extra quotes!
    WHEN {{metric_type}} = 'impressions' THEN impressions
END

-- CORRECT - Text parameter already includes quotes
WHERE channel = {{channel_param}}                  -- {{channel_param}} becomes 'Google'

-- CORRECT - Field filter as boolean condition
WHERE {{customer_filter}}                          -- Becomes true/false
```

### How Parameter Substitution Actually Works

#### Simple Variable Filters
Parameters substitute their **actual values** with proper formatting:

- **Text parameter**: `{{channel}}` → `'Google'` (quotes included automatically)
- **Number parameter**: `{{limit}}` → `100` (no quotes)
- **Date parameter**: `{{start_date}}` → `'2024-01-01'` (quotes included automatically)

#### Field Filters
Parameters substitute **boolean values** indicating if the condition is met:

- `{{customer_filter}}` → `true` (if customer matches filter) or `false`
- `{{date_range}}` → `true` (if date is in range) or `false`
- `{{spend_range}}` → `true` (if spend is in range) or `false`

**Field filters are NOT replaced with the actual filter condition - they become boolean evaluations!**

### SQL Parameter Validation System

The system includes comprehensive validation functions located in `enhanced_parameters/core.py`:

#### Key Validation Functions

```python
def extract_sql_parameters(query: str) -> Dict[str, List[str]]:
    """Extract parameter references from SQL query."""
    # Returns: {"required": [...], "optional": [...]}

def validate_sql_parameter_consistency(query: str, parameters: List[Dict[str, Any]]) -> List[str]:
    """Validate that SQL parameters match the provided parameters configuration."""
    # Returns: List of validation error/warning messages

def detect_sql_parameter_mistakes(query: str, parameter_names: List[str]) -> List[str]:
    """Detect common SQL parameter usage mistakes."""
    # Returns: List of warning messages about potential mistakes
```

#### Parameter Extraction Logic

- **Required parameters**: `{{parameter}}` used directly in WHERE clauses
- **Optional parameters**: `[[AND {{parameter}}]]` that can be turned on/off
- **Duplicate handling**: Removes duplicates and correctly categorizes optional vs required

#### Consistency Validation

- **Missing parameters**: SQL references parameters not in configuration
- **Unused parameters**: Configuration has parameters not used in SQL
- **Required parameter validation**: Checks that required SQL parameters have defaults or are marked as required

#### Integration with Card Tools

The validation is integrated into both `create_card` and `update_card` tools:

```python
# Check for common SQL parameter mistakes and parameter consistency
if processed_parameters:
    sql_warnings.extend(detect_sql_parameter_mistakes(query, parameter_names))
    
    # Check parameter consistency
    consistency_issues = validate_sql_parameter_consistency(query, processed_parameters)
    if consistency_issues:
        sql_warnings.extend([f"PARAMETER CONSISTENCY: {issue}" for issue in consistency_issues])
```

#### Example Validation Messages

```json
{
  "success": false,
  "error": "Invalid query",
  "sql_warnings": [
    "WARNING: Parameter 'metric_type' is quoted in SQL. Remove quotes - parameters include proper formatting automatically.",
    "PARAMETER CONSISTENCY: SQL references parameter 'date_range_filter' but no matching parameter configuration found",
    "PARAMETER CONSISTENCY: Parameter 'unused_param' is configured but not used in SQL query"
  ]
}
```

### Parameter Mappings Support

The tool supports linking dashboard parameters to card parameters through the `parameter_mappings` field in dashcards. This creates the connection that allows dashboard filters to control card behavior.

#### Parameter Mapping Structure
```json
{
  "dashboard_parameter_name": "Status Filter",
  "card_parameter_name": "order_status"
}
```

#### Key Features

1. **Name-Based Identification**: Both dashboard and card parameters are identified by their names
2. **Automatic ID Resolution**: The system automatically converts names to internal IDs and targets
3. **Validation**: Ensures both dashboard and card parameters exist before creating mappings
4. **Card Parameter Support**: Card parameters can be referenced by either name or slug
5. **Comprehensive Error Messages**: Clear feedback when parameter names don't match

#### Processing Flow

1. **Parameter Validation**: Validates that dashboard parameter names exist in the dashboard parameters configuration
2. **Card Parameter Retrieval**: Fetches card parameters from Metabase for each card with parameter mappings
3. **Name Resolution**: Matches card parameter names (or slugs) to actual parameter objects
4. **ID Conversion**: Converts name-based mappings to ID-based mappings for the Metabase API
5. **Target Extraction**: Extracts the appropriate target information from card parameters

#### Generated Metabase API Format

The system converts name-based mappings like this:

```json
// Input (name-based)
{
  "dashboard_parameter_name": "Status Filter",
  "card_parameter_name": "order_status"
}

// Generated (ID-based for Metabase API)
{
  "card_id": 54276,
  "parameter_id": "ab12cd34",  // Dashboard parameter ID
  "target": ["variable", ["template-tag", "order_status"]]  // Card parameter target
}
```

#### Usage Example

```json
{
  "method": "tools/call",
  "params": {
    "name": "update_dashboard",
    "arguments": {
      "id": 1864,
      "parameters": [
        {
          "name": "Status Filter",
          "type": "string/=",
          "default": ["active"],
          "values_source": {
            "type": "static",
            "values": ["active", "inactive", "pending"]
          }
        }
      ],
      "dashcards": [
        {
          "id": -1,
          "card_id": 54276,
          "col": 0,
          "row": 0,
          "size_x": 12,
          "size_y": 8,
          "parameter_mappings": [
            {
              "dashboard_parameter_name": "Status Filter",
              "card_parameter_name": "order_status"
            }
          ]
        }
      ]
    }
  }
}

### Parameter Preservation in Card Updates

The `update_card` tool has been enhanced to preserve existing parameters when updating queries:

```python
# If query is being updated but no new parameters provided, preserve existing parameters
if query is not None and "parameters" in current_data and current_data["parameters"]:
    update_data["parameters"] = current_data["parameters"]
    
# Also preserve existing template tags
if parameters is None and "dataset_query" in current_data:
    existing_native = current_data["dataset_query"].get("native", {})
    existing_template_tags = existing_native.get("template-tags", {})
```

This prevents the "template tag not found" error when updating cards without explicitly providing parameters.

### Benefits of SQL Parameter Validation

1. **Prevents Common Mistakes**: Detects quoted parameters and incorrect field filter usage
2. **Ensures Consistency**: Validates that SQL references match parameter configurations
3. **Provides Clear Guidance**: Offers specific correction suggestions
4. **Preserves Functionality**: Maintains existing parameters during query updates
5. **Comprehensive Coverage**: Validates both simple variables and field filters

This validation system significantly improves the reliability of AI-generated SQL with Metabase parameters, preventing runtime errors and ensuring proper parameter functionality.

## Visualization Settings Support

Talk to Metabase provides comprehensive support for customizing chart visualization settings across 17 different chart types. This functionality enables users to create sophisticated, well-formatted visualizations directly through Claude.

### Supported Chart Types

The implementation supports all major Metabase visualization types with full JSON schema validation:

| API Name | UI Name | Description | Status |
|----------|---------|-------------|--------|
| `table` | table | Data tables with formatting, conditional formatting, and click behaviors | ✅ Implemented |
| `line` | line | Line charts with series settings, axes configuration, and trend lines | ✅ Implemented |
| `bar` | bar | Vertical bar charts with stacking, series configuration, and value labels | ✅ Implemented |
| `combo` | combo | Combination charts mixing lines, bars, and areas with dual axes | ✅ Implemented |
| `pie` | pie | Pie charts with slice customization, legends, and percentage displays | ✅ Implemented |
| `row` | row | Horizontal bar charts with category management and goal lines | ✅ Implemented |
| `area` | area | Area charts with stacking, series blending, and trend visualization | ✅ Implemented |
| `object` | detail | Object detail views for displaying single record information | ✅ Implemented |
| `funnel` | funnel | Funnel charts for conversion analysis with stage progression | ✅ Implemented |
| `gauge` | gauge | Gauge charts for single KPI display with color-coded segments | ✅ Implemented |
| `progress` | progress | Progress bars showing completion toward a goal | ✅ Implemented |
| `sankey` | sankey | Sankey diagrams for visualizing flow between nodes | ✅ Implemented |
| `scalar` | number | Single number displays with formatting | ✅ Implemented |
| `scatter` | scatter | Scatter plots for analyzing relationships between two variables | ✅ Implemented |
| `smartscalar` | trend | Trend numbers with comparison values and indicators | ✅ Implemented |
| `map` | map | Geographic maps for location-based data visualization | ✅ Implemented |
| `waterfall` | waterfall | Waterfall charts for showing cumulative effects of sequential changes | ✅ Implemented |

### UI vs API Name Mapping

Some chart types have different names in the Metabase UI versus the API. The system handles this automatically:

```python
# UI to API name mappings
UI_TO_API_MAPPING = {
    "detail": "object",     # Object detail views
    "number": "scalar",     # Single number displays
    "trend": "smartscalar",  # Trend indicators
}
```

Users can use either name - the system automatically converts UI names to API names internally.

### Key Tools

#### GET_VISUALIZATION_DOCUMENT

The primary tool for working with visualization settings:

```python
@mcp.tool(name="GET_VISUALIZATION_DOCUMENT")
async def get_visualization_document(chart_type: str, ctx: Context) -> str:
    """Get comprehensive documentation and schema for a chart type."""
```

**Features:**
- Complete documentation with examples for each chart type
- JSON schema for validation
- API/UI name mapping information
- Common patterns and use cases

#### Enhanced create_card and update_card

Both tools now support visualization settings with validation:

```python
async def create_card(
    database_id: int,
    query: str,
    name: str,
    ctx: Context,
    display: str = "table",
    visualization_settings: Optional[Dict[str, Any]] = None
) -> str:
```

**Validation Process:**
1. Validates visualization_settings against JSON schema
2. Returns clear error messages if validation fails
3. Suggests calling GET_VISUALIZATION_DOCUMENT for help

### Implementation Architecture

#### Schema and Documentation Structure

```
talk_to_metabase/schemas/
├── table_visualization.json
├── table_visualization_docs.md
├── line_visualization.json
├── line_visualization_docs.md
├── object_visualization.json     # API name used for files
├── object_visualization_docs.md
└── ... (all chart types)
```

#### Core Functions

```python
def validate_visualization_settings(chart_type: str, settings: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """Validate settings against JSON schema with UI/API name conversion."""
    
def load_schema(chart_type: str) -> Optional[Dict[str, Any]]:
    """Load JSON schema with automatic name mapping."""
    
def load_documentation(chart_type: str) -> Optional[str]:
    """Load documentation with automatic name mapping."""
```

### Usage Workflow

The intended workflow for users:

1. **Get Documentation**: Call `GET_VISUALIZATION_DOCUMENT` with desired chart type
2. **Review Examples**: Examine the provided examples and schema
3. **Build Settings**: Create visualization_settings object
4. **Create/Update Card**: Use settings in `create_card` or `update_card`
5. **Validation**: System automatically validates and provides feedback

### Example Implementation

```python
# User calls: GET_VISUALIZATION_DOCUMENT(chart_type="table")
# System returns: Complete documentation + JSON schema + examples

# User then calls: create_card with visualization_settings
await create_card(
    database_id=195,
    query="SELECT * FROM products",
    name="Product List",
    display="table",
    visualization_settings={
        "column_settings": {
            "[\"name\",\"price\"]": {
                "number_style": "currency",
                "currency": "USD"
            }
        }
    }
)
```

### Benefits

1. **Complete Coverage**: All 17 chart types supported with full customization
2. **Type Safety**: JSON schema validation prevents invalid configurations
3. **User-Friendly**: Supports both UI and API names seamlessly
4. **Self-Documenting**: Comprehensive examples and documentation
5. **Error Handling**: Clear validation errors with helpful guidance
6. **Extensible**: Easy to add new chart types following the same pattern

## MBQL (Metabase Query Language) Implementation

Talk to Metabase now supports MBQL queries alongside SQL, providing database-agnostic structured queries with comprehensive schema validation.

### Key Features

1. **Complete MBQL Support**: All MBQL features (aggregations, filters, expressions, joins, nested queries)
2. **JSON Schema Validation**: Comprehensive validation without query execution
3. **Database-Agnostic**: Works across all Metabase-supported databases
4. **Integrated with Card Tools**: Seamlessly works with `create_card` and `update_card`

### When to Use MBQL vs SQL

**Use MBQL ("query" type) - RECOMMENDED DEFAULT:**
- Standard analytical queries (aggregations, grouping, filtering)
- Database-agnostic queries
- Structured, validated queries with clear semantics

**Use SQL ("native" type) only when:**
- Database-specific SQL features not available in MBQL
- Complex custom SQL logic beyond MBQL capabilities
- Template parameters for dynamic filtering

### Basic MBQL Structure

```json
{
  "source-table": 1,
  "aggregation": [["sum", ["field", 123, null]]],
  "breakout": [["field", 456, {"temporal-unit": "month"}]],
  "filter": ["=", ["field", 789, null], "active"]
}
```

### Implementation

- **MBQL Schema**: `/talk_to_metabase/schemas/mbql_schema.json`
- **Tools Module**: `/talk_to_metabase/tools/mbql.py`
- **Enhanced Card Tools**: Updated with `query_type` parameter

### Tools

**GET_MBQL_SCHEMA**: Get comprehensive MBQL documentation and schema
**create_card/update_card**: Now support `query_type: "query"` for MBQL queries

### Usage Example

```json
{
  "name": "create_card",
  "arguments": {
    "database_id": 195,
    "query_type": "query",
    "query": {
      "source-table": 1,
      "aggregation": [["count"]],
      "breakout": [["field", 456, {"temporal-unit": "month"}]]
    },
    "name": "Monthly Count"
  }
}
```

# Talk to Metabase MCP Developer Guide

This document provides comprehensive guidance for developers who will be implementing or modifying tools in the Talk to Metabase MCP server project.

## Project Overview

Talk to Metabase is an MCP (Model Context Protocol) server that integrates Claude with Metabase, allowing Claude to interact with Metabase resources. The server follows the Model Context Protocol specification to expose Metabase functionality as tools that Claude can use.

### Key Components

1. **Authentication**: Session-based authentication with Metabase, with automatic re-authentication
2. **Tools**: Functions that map to Metabase API endpoints for resource operations
3. **Configuration**: Environment variable-based configuration with .env file support
4. **Response Handling**: Includes size limits to prevent oversized responses
5. **Pagination**: Client-side pagination for large data sets where API doesn't natively support it
6. **Unified Query Execution**: Flexible tool for executing queries in both standalone and dashboard contexts
7. **Simplified Parameter System**: Streamlined card parameters with automatic JSON Schema validation
8. **MBQL Query Support**: Full support for Metabase Query Language with comprehensive schema validation

## Card Parameters Implementation

The card parameters system provides comprehensive support for creating sophisticated interactive filters in Metabase cards, including both simple variable filters and advanced field filters that connect directly to database columns.

### Key Features

1. **Comprehensive Parameter Types**:
   - **Simple Filters**: `category`, `number/=`, `date/single` (work with `{{variable}}` in SQL)
   - **Field Filters**: `string/=`, `string/contains`, `number/between`, `date/range`, etc. (connect to database columns)

2. **UI Widget Support**:
   - `input` - Free text/number entry
   - `dropdown` - Select from predefined values
   - `search` - Search with suggestions

3. **Value Source Management**:
   - `static` - Predefined list of values
   - `card` - Values from another card/model
   - `connected` - Values from connected database field (field filters only)

4. **Automatic Processing**:
   - UUID generation and parameter linking
   - Template tag creation from parameters
   - Target mapping (variable vs dimension)
   - Slug generation from parameter names

5. **Comprehensive Validation**:
   - JSON Schema for structure and type validation
   - Field reference validation against database
   - UI widget compatibility checking
   - Required parameter default value validation

### Critical Distinction: Variable vs Field Filters

#### Simple Variable Filters
- **SQL Usage**: `WHERE column = {{variable_name}}`
- **How it works**: Parameter value gets substituted directly into SQL
- **You control**: Column name, operator, SQL structure
- **Example**: `WHERE status = {{order_status}}` → becomes `WHERE status = 'pending'`

#### Field Filters
- **SQL Usage**: `WHERE {{field_filter_name}}`
- **How it works**: Field filters are replaced with BOOLEAN VALUES (true/false) indicating if the condition is met
- **Metabase controls**: The actual filtering logic based on field mapping
- **Example**: `WHERE {{customer_filter}}` → becomes `WHERE true` or `WHERE false` (boolean result)

#### Key Rules
- ✅ **Simple filters**: `WHERE column = {{variable}}`
- ✅ **Field filters**: `WHERE {{field_filter}}`
- ❌ **Never**: `WHERE column = {{field_filter}}` (field filters are booleans, not values!)
- ❌ **Never**: `WHERE column = '{{variable}}'` (don't add extra quotes to text parameters)

### Card Parameter Structure

```json
{
  "name": "parameter_name",           // Required: Parameter name (used in SQL)
  "type": "parameter_type",           // Required: Parameter type
  "display_name": "Display Name",     // Optional: Human-readable name
  "default": "default_value",         // Optional: Default value
  "required": false,                   // Optional: Whether parameter is required
  "field": {                          // Required for field filters
    "database_id": 195,
    "table_id": 50112,
    "field_id": 50705149
  },
  "ui_widget": "dropdown",            // Optional: UI widget type
  "values_source": {                  // Optional: Value source configuration
    "type": "static",
    "values": ["value1", "value2"]
  }
}
```

### Implementation Architecture

#### Core Components

1. **Card Parameters Module** (`/talk_to_metabase/tools/card_parameters/`):
   - `core.py` - Main implementation with validation and processing
   - `__init__.py` - Module exports

2. **JSON Schema Validation** (`/talk_to_metabase/schemas/card_parameters.json`):
   - Comprehensive validation for all parameter types
   - Conditional validation for field filters
   - UI widget compatibility rules
   - Connected field filter exception handling

3. **Documentation** (`/talk_to_metabase/schemas/card_parameters_docs.md`):
   - Complete examples for all parameter types
   - SQL usage patterns and best practices
   - UI widget and value source configuration

#### Key Functions

```python
# Main processing function
async def process_card_parameters(
    client, 
    parameters: List[Dict[str, Any]]
) -> Tuple[List[Dict[str, Any]], Dict[str, Any], List[str]]:
    """Process card parameters into Metabase API format with validation."""

# Validation function
def validate_card_parameters(
    parameters: List[Dict[str, Any]]
) -> Tuple[bool, List[str]]:
    """Validate card parameters against schema and business rules."""

# Individual parameter processing
def process_single_parameter(
    param_config: Dict[str, Any], 
    param_id: str
) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    """Process a single parameter configuration into Metabase API format."""
```

### Card Validation System

The validation system has been significantly improved to prevent common AI assistant mistakes:

1. **SQL Parameter Consistency Validation**: 
   - Validates that SQL references match parameter configurations
   - Checks for missing or unused parameters
   - Validates required parameter default values

2. **SQL Mistake Detection**:
   - Detects quoted parameters (`'{{param}}'`)
   - Identifies incorrect CASE WHEN usage
   - Provides specific correction guidance

3. **UI Widget Compatibility**:
   - Improved to allow search widgets with all string field filter types
   - Validates dropdown/search widget requirements
   - Prevents incompatible widget configurations

4. **Parameter Preservation**:
   - Automatically preserves existing parameters during query-only updates
   - Maintains template tag consistency
   - Prevents "template tag not found" errors

### Validation Functions Location

All parameter validation functions are centralized in `card_parameters/core.py`:

- `extract_sql_parameters()` - Extracts required/optional parameters from SQL
- `validate_sql_parameter_consistency()` - Validates SQL-parameter alignment  
- `detect_sql_parameter_mistakes()` - Detects common usage errors
- `validate_parameter_widget_compatibility()` - Validates UI widget compatibility

### Special Handling for Number Dropdowns

Number parameters with dropdowns require special formatting:

```python
# Input format
{
  "type": "number/=",
  "default": 100,
  "values_source": {
    "type": "static",
    "values": [50, 100, 200, 500]
  }
}

# Generated API format
{
  "default": ["100"],
  "values_source_config": {
    "values": [["50"], ["100"], ["200"], ["500"]]
  },
  "template-tags": {
    "parameter_name": {
      "default": ["100"]
    }
  }
}
```

### Connected Field Filter Configuration

Connected field filters use a special configuration:

```python
# Input
{
  "ui_widget": "dropdown",
  "values_source": {"type": "connected"}
}

# Generated API format
{
  "values_source_type": null,
  "values_source_config": {}
}
```

### Tools Integration

#### GET_CARD_PARAMETERS_DOCUMENTATION

Provides comprehensive documentation and examples:

```python
@mcp.tool(name="GET_CARD_PARAMETERS_DOCUMENTATION")
async def get_card_parameters_documentation(ctx: Context) -> str:
    """Get comprehensive documentation for card parameters."""
```

#### Card Creation/Update Tools

Both tools now support card parameters with validation:

```python
# Parameters processing in card creation/update
if CARD_PARAMETERS_AVAILABLE and parsed_parameters:
    processed_parameters, template_tags, errors = await process_card_parameters(
        client, parsed_parameters
    )
    if errors:
        return validation_error_response
```

### Migration from Legacy System

The card parameters system completely replaces the old simplified card parameters:

1. **Legacy Files Removed**: Old card_parameters.py moved to .deprecated
2. **Improved Validation**: More comprehensive and reliable
3. **Field Filter Support**: Advanced filtering capabilities
4. **Backward Compatibility**: Simple use cases work the same way

### Performance Optimizations

1. **Schema-First Validation**: JSON Schema handles most validation automatically
2. **Reduced Code Complexity**: 75% less validation code compared to manual validation
3. **Field Validation**: Database field references validated efficiently
4. **Automatic Processing**: All complex configuration generated automatically

### Usage Examples

#### Simple Category Filter
```json
{
  "name": "order_status",
  "type": "category",
  "default": "pending",
  "ui_widget": "dropdown",
  "values_source": {
    "type": "static",
    "values": ["pending", "shipped", "delivered"]
  }
}
```

#### Field Filter with Connected Values
```json
{
  "name": "customer_filter",
  "type": "string/=",
  "field": {
    "database_id": 195,
    "table_id": 50112,
    "field_id": 50705149
  },
  "ui_widget": "dropdown",
  "values_source": {
    "type": "connected"
  }
}
```

#### Number Range Field Filter
```json
{
  "name": "spend_range",
  "type": "number/between",
  "field": {
    "database_id": 195,
    "table_id": 50112,
    "field_id": 50705151
  },
  "default": [100, 5000]
}
```

#### Date Field Filter
```json
{
  "name": "date_filter",
  "type": "date/all-options",
  "field": {
    "database_id": 195,
    "table_id": 50112,
    "field_id": 50705150
  },
  "default": "past30days"
}
```

### Benefits

1. **Comprehensive Filtering**: Support for all Metabase parameter types
2. **Type Safety**: JSON Schema validation prevents configuration errors
3. **Database Integration**: Field filters connect directly to database columns
4. **User Experience**: Appropriate UI widgets with automatic value population
5. **Developer Experience**: Clear error messages and comprehensive documentation
6. **Performance**: Optimized validation and processing
7. **Maintainability**: Clean, modular architecture

## Dashboard Parameters Implementation

The dashboard parameters system provides comprehensive support for all Metabase dashboard filter types with automatic ID generation, intelligent defaults, and complete validation. This system completely replaces the previous simplified dashboard parameters implementation and is designed for maximum AI assistant usability.

### Key Features

1. **Complete Parameter Type Support**:
   - **Text Parameters**: All 6 string parameter types with full multi-select support by default
   - **Location Parameters**: All 6 location parameter types with full multi-select support by default  
   - **Number Parameters**: 5 number parameter types with multi-select for equality types
   - **Date Parameters**: 6 date parameter types (no multi-select support)
   - **Special Parameters**: `temporal-unit`, `id`

2. **Multi-Select Default Behavior**:
   - ✅ **Multi-select enabled by default** for all supported parameter types
   - ✅ **Supported**: All string types (`string/=`, `string/!=`, `string/contains`, `string/does-not-contain`, `string/starts-with`, `string/ends-with`)
   - ✅ **Supported**: All location types (`location/=`, `location/!=`, `location/contains`, `location/does-not-contain`, `location/starts-with`, `location/ends-with`)
   - ✅ **Supported**: Number equality types (`number/=`, `number/!=`)
   - ✅ **Supported**: `id` parameters
   - ❌ **Not Supported**: All date parameters, `temporal-unit`, number range/comparison parameters

3. **Value Sources**: Only "static" and "card" sources - no "connected" option

4. **Automatic Processing**: ID generation (8-character alphanumeric), slug creation, automatic location detection

5. **AI-Friendly Design**: Parameters identified by name only, all complex processing handled automatically

### Implementation Architecture

#### Core Files

1. **Main Implementation** (`dashboard_parameters.py`):
   - Parameter processing and validation logic
   - Multi-select compatibility checking
   - Value source configuration
   - Automatic ID and slug generation
   - `GET_DASHBOARD_PARAMETERS_DOCUMENTATION` tool

2. **JSON Schema** (`dashboard_parameters.json`):
   - Validates all parameter types and configurations
   - Enforces multi-select restrictions
   - Sets `isMultiSelect` default to `true` for supported types
   - Prevents use of unauthorized fields (no `id` or `sectionId` allowed)
   - Only allows "static" and "card" value sources

3. **Documentation**: All documentation is embedded directly in the JSON schema
   - Examples for all parameter types showing default multi-select behavior
   - Usage guidelines focused on AI assistant needs
   - Default value format specifications
   - No separate markdown file needed

4. **Updated Dashboard Tool** (`dashboard.py`):
   - Uses enhanced validation and processing
   - Replaced old parameters system
   - Updated documentation and error messages

#### Parameter Type Categories

```python
# Text parameters - all support multi-select
TEXT_PARAMETER_TYPES = {
"string/=", "string/!=", "string/contains", "string/does-not-contain",
"string/starts-with", "string/ends-with"
}

# Location parameters - all support multi-select
LOCATION_PARAMETER_TYPES = {
"location/=", "location/!=", "location/contains", "location/does-not-contain",
    "location/starts-with", "location/ends-with"
}

# Number parameters - equality types support multi-select
NUMBER_PARAMETER_TYPES = {
"number/=", "number/!=", "number/between", "number/>=", "number/<=" 
}

# Date parameters - none support multi-select
DATE_PARAMETER_TYPES = {
    "date/single", "date/range", "date/month-year", "date/quarter-year", 
    "date/relative", "date/all-options"
}
```

#### Key Validation Changes for Multi-Select Default

The validation system has been updated to handle the new default behavior:

```python
def validate_default_value_format(param_config: Dict[str, Any]) -> List[str]:
    # Determine if multi-select is enabled
    # For supported types, isMultiSelect defaults to True unless explicitly set to False
    if param_type in MULTI_SELECT_SUPPORTED:
        is_multi_select = param_config.get("isMultiSelect", True)  # Default to True
    else:
        is_multi_select = param_config.get("isMultiSelect", False)  # Default to False for unsupported types
```

This ensures that:
- Parameters without explicit `isMultiSelect` are treated as multi-select for supported types
- Array defaults are expected for these implicitly multi-select parameters
- Explicit `isMultiSelect: false` still works to create single-value parameters

#### Location Parameter Types

**Location parameters** are explicitly specified using dedicated parameter types:

```python
# Location parameter types - all support multi-select
LOCATION_PARAMETER_TYPES = {
    "location/=", "location/!=", "location/contains", "location/does-not-contain",
    "location/starts-with", "location/ends-with"
}

# Location parameters are translated to string types with location sectionId
LOCATION_TO_STRING_MAPPING = {
    "location/=": "string/=",
    "location/!=": "string/!=",
    "location/contains": "string/contains",
    "location/does-not-contain": "string/does-not-contain",
    "location/starts-with": "string/starts-with",
    "location/ends-with": "string/ends-with"
}
```

### Usage Pattern

#### Tools Integration

```python
# Documentation tool
@mcp.tool(name="GET_DASHBOARD_PARAMETERS_DOCUMENTATION")
async def get_dashboard_parameters_documentation(ctx: Context) -> str:
    # Returns comprehensive documentation and schema

# Dashboard update with dashboard parameters
@mcp.tool(name="update_dashboard")
async def update_dashboard(
    id: int,
    ctx: Context,
    parameters: Optional[List[Dict[str, Any]]] = None,
    # ... other parameters
) -> str:
    # Uses dashboard parameter validation and processing
```

#### Parameter Configuration Format

```python
# AI assistant only needs to provide these fields
{
    "name": "Parameter Name",        # Required: Used for identification
    "type": "string/=",              # Required: Parameter type
    "default": ["value1", "value2"], # Optional: Array for multi-select (default), single for isMultiSelect: false
    "isMultiSelect": False,          # Optional: Set to false for single-value parameters
    "required": True,                # Optional: Whether parameter is required
    "values_source": {               # Optional: Value source configuration
        "type": "static",             # Only "static" or "card" allowed
        "values": ["option1", "option2"]
    },
    "temporal_units": ["day", "week"] # Required only for temporal-unit parameters
}
```

**Forbidden Fields** (prevented by schema):
- `id` - Generated automatically
- `sectionId` - Determined automatically (including location detection)
- Any other internal Metabase fields

### Processing Flow

1. **Initial Validation**: JSON schema validation for structure and types
2. **Business Logic Validation**: Multi-select compatibility, temporal units, value sources
3. **Card Reference Validation**: Check accessibility of referenced cards
4. **Parameter Processing**: Generate IDs, slugs, and convert to Metabase API format
5. **Final Validation**: Ensure processed parameters are valid

### Error Handling

The system provides detailed error messages for:
- Schema validation failures with specific field paths
- Multi-select compatibility issues
- Invalid temporal units
- Missing or inaccessible card references
- Required parameter validation
- Value source configuration errors

### Key Improvements Over Previous System

1. **AI-Friendly Defaults**: Multi-select enabled by default for supported types
2. **Simplified Interface**: No manual ID or sectionId management required
3. **Automatic Processing**: ID generation, slug creation
4. **Explicit Location Types**: Direct specification with `location/=`, `location/contains`, etc.
5. **Streamlined Value Sources**: Only "static" and "card" sources (no confusing "connected" option)
6. **Schema-Only Documentation**: All guidance embedded in JSON schema
7. **Robust Validation**: Prevents AI assistant configuration errors
8. **Clean Error Messages**: Clear, actionable feedback for validation issues

### Usage Examples

#### Multi-Select Parameter (Default Behavior)
```json
{
  "name": "Categories",
  "type": "string/=",
  "default": ["electronics", "books"],
  "values_source": {
    "type": "static",
    "values": ["electronics", "books", "clothing"]
  }
}
```

#### Single-Value Parameter (Explicit)
```json
{
  "name": "Department",
  "type": "string/=",
  "isMultiSelect": false,
  "default": "engineering",
  "values_source": {
    "type": "static",
    "values": ["engineering", "product", "design"]
  }
}
```

#### Location Parameter
```json
{
  "name": "Cities",
  "type": "location/=",
  "default": ["New York", "Chicago"],
  "values_source": {
    "type": "static",
    "values": ["New York", "Chicago", "Boston"]
  }
}
```

#### Location Parameter with Contains Operation
```json
{
  "name": "City Search",
  "type": "location/contains",
  "default": ["York"],
  "values_source": {
    "type": "static",
    "values": ["York", "Angeles", "Francisco"]
  }
}
```

#### ID Parameter with Mixed Types
```json
{
  "name": "Product IDs",
  "type": "id",
  "default": [1001, 1002, "SPECIAL-001"],
  "values_source": {
    "type": "static",
    "values": [1001, 1002, 1003, "SPECIAL-001"]
  }
}
```

#### Card Source Parameter
```json
{
  "name": "User Names",
  "type": "string/=",
  "values_source": {
    "type": "card",
    "card_id": 98765,
    "value_field": "user_id",
    "label_field": "user_name"
  }
}
```

## Project Structure

```
Talk to Metabase/
├── talk_to_metabase/              # Main package
│   ├── __init__.py             # Package initialization
│   ├── auth.py                 # Metabase authentication
│   ├── client.py               # Metabase API client
│   ├── config.py               # Configuration management
│   ├── errors.py               # Error handling utilities
│   ├── models.py               # Data models
│   ├── server.py               # MCP server implementation
│   └── tools/                  # MCP tools for Metabase operations
│       ├── __init__.py         # Tools registration
│       ├── common.py           # Shared utilities
│       ├── dashboard.py        # Dashboard operations
│       ├── card.py             # Card operations
│       ├── collection.py       # Collection operations
│       ├── database.py         # Database operations
│       └── search.py           # Search operations
├── tests/                      # Test suite
│   ├── unit/                   # Unit tests
│   └── integration/            # Integration tests
├── .env.example                # Example environment variables
├── metabase_mcp.py             # CLI entry point
├── pyproject.toml              # Project configuration
└── README.md                   # Project documentation
```

## Architecture

The architecture follows a modular design pattern:

1. **Entry Point**: `metabase_mcp.py` creates and runs the server
2. **Server**: `server.py` manages the MCP server lifecycle and tool registration
3. **Authentication**: `auth.py` handles Metabase session management
4. **Client**: `client.py` provides methods to interact with Metabase API
5. **Tools**: Individual modules in the `tools/` directory expose Metabase functionality

The core pattern is:
1. User query → Claude → MCP client → Talk to Metabase MCP server
2. Server authenticates with Metabase
3. Tool executes corresponding API call
4. Response is formatted and returned to Claude
5. Claude processes and presents the information to the user

## How to Implement a New Tool

To implement a new tool, follow these steps:

### 1. Identify the Metabase API Endpoint

Review the Metabase API documentation or the OpenAPI specification to identify the API endpoint for the functionality you want to expose.

### 2. Choose the Appropriate Module

Add your tool to the appropriate module based on the resource type:
- Dashboard operations → `dashboard.py`
- Card operations → `card.py`
- Collection operations → `collection.py`
- Database operations → `database.py`
- Search operations → `search.py`

Or create a new module if necessary.

### 3. Implement the Tool Function

Here's a template for implementing a new tool:

```python
@mcp.tool(name="tool_name", description="Tool description")
async def tool_name(
    param1: type,  # Required parameter
    ctx: Context,  # Always include the context parameter after required parameters
    optional_param: Optional[type] = None,  # Optional parameters with defaults come last
) -> str:
    """
    Tool docstring with detailed description.
    
    Args:
        param1: Description of parameter
        ctx: MCP context
        optional_param: Description of optional parameter
        
    Returns:
        JSON string with result or error information
    """
    # Log the tool invocation
    logger.info(f"Tool called: tool_name(param1={param1}, optional_param={optional_param})")
    
    # Get Metabase client from context
    client = get_metabase_client(ctx)
    
    try:
        # Make the API request using the client
        data, status, error = await client.auth.make_request(
            "GET", "endpoint"
        )
        
        if error:
            return format_error_response(
                status_code=status,
                error_type="retrieval_error",
                message=error,
                request_info={"endpoint": "/api/endpoint", "method": "GET"}
            )
        
        # Extract and simplify data if needed for performance
        # For simple tools, consider returning only essential fields
        if should_simplify_response:
            simplified_data = extract_essential_fields(data)
            response_data = {"items": simplified_data}
        else:
            response_data = data
        
        # Convert data to JSON string
        response = json.dumps(response_data, indent=2)
        
        # Check response size before returning
        metabase_ctx = ctx.request_context.lifespan_context
        config = metabase_ctx.auth.config
        return check_response_size(response, config)
    except Exception as e:
        logger.error(f"Error in tool_name: {e}")
        return format_error_response(
            status_code=500,
            error_type="tool_error",
            message=str(e),
            request_info={"endpoint": "/api/endpoint", "method": "GET"}
        )
```

#### Template for Simplified Tools

For tools that need to return only essential information (like `list_databases`), use this pattern:

```python
@mcp.tool(name="list_items", description="List items with essential information only")
async def list_items(ctx: Context) -> str:
    """
    List items with essential information only.
    
    Args:
        ctx: MCP context
        
    Returns:
        Simplified list of items as JSON string with essential fields only
    """
    logger.info("Tool called: list_items()")
    client = get_metabase_client(ctx)
    
    try:
        data, status, error = await client.auth.make_request(
            "GET", "items"
        )
        
        if error:
            return format_error_response(
                status_code=status,
                error_type="retrieval_error",
                message=error,
                request_info={"endpoint": "/api/items", "method": "GET"}
            )
        
        # Handle different response formats
        if isinstance(data, dict) and "data" in data:
            items = data["data"]
        elif isinstance(data, list):
            items = data
        else:
            logger.error(f"Unexpected data format: {type(data)}")
            return format_error_response(
                status_code=500,
                error_type="unexpected_format",
                message="Unexpected response format from Metabase API",
                request_info={"endpoint": "/api/items", "method": "GET"}
            )
        
        # Extract only essential fields
        simplified_items = []
        for item in items:
            simplified_item = {
                "id": item.get("id"),
                "name": item.get("name"),
                "type": item.get("type")
                # Add only fields that are essential for the tool's purpose
            }
            simplified_items.append(simplified_item)
        
        # Create final response structure
        response_data = {
            "items": simplified_items
        }
        
        # Convert to JSON string
        response = json.dumps(response_data, indent=2)
        
        # Check response size before returning
        metabase_ctx = ctx.request_context.lifespan_context
        config = metabase_ctx.auth.config
        return check_response_size(response, config)
    except Exception as e:
        logger.error(f"Error in list_items: {e}")
        return format_error_response(
            status_code=500,
            error_type="retrieval_error",
            message=str(e),
            request_info={"endpoint": "/api/items", "method": "GET"}
        )
```

### 4. Register the Tool with the Server

The `@mcp.tool()` decorator automatically registers the tool with the MCP server. Ensure you're using the singleton server instance:

```python
from ..server import get_server_instance

# Register tools with the server
mcp = get_server_instance()
```

### 5. Add Unit Tests

Create or update the test file for your module in the `tests/unit/` directory:

```python
@pytest.mark.asyncio
async def test_tool_name_success(mock_context, sample_data):
    """Test successful tool execution."""
    # Set up the mock
    client_mock = MagicMock()
    client_mock.some_method = AsyncMock(return_value=sample_data)
    
    with patch("talk_to_metabase.tools.your_module.get_metabase_client", return_value=client_mock):
        # Call the tool
        result = await tool_name(param1="value", ctx=mock_context)
        
        # Verify the result
        assert isinstance(result, str)
        result_data = json.loads(result)
        assert result_data["expected_field"] == "expected_value"
        
        # Verify the mock was called correctly
        client_mock.some_method.assert_called_once()
```

## Important Patterns and Requirements

### Parameter Order

Python requires that parameters with default values appear after parameters without default values. The correct order is:
1. Required parameters without defaults
2. The `ctx: Context` parameter
3. Optional parameters with default values

```python
async def tool_function(
    required_param: str,  # Required first
    ctx: Context,         # Context next
    optional_param: Optional[str] = None  # Optional with defaults last
) -> str:
```

### Response Size Limitation

All tools must use the `check_response_size` function to ensure responses don't exceed the configured size limit:

```python
# Convert data to JSON string
response = json.dumps(data, indent=2)

# Check response size before returning
metabase_ctx = ctx.request_context.lifespan_context
config = metabase_ctx.auth.config
return check_response_size(response, config)
```

### Simplifying Responses for Performance

For tools that may return large amounts of data, consider implementing response simplification:

```python
# Example: Extract only essential fields from a complex API response
def extract_essential_fields(items_data):
    """Extract only essential fields from API response."""
    simplified_items = []
    for item in items_data:
        simplified_item = {
            "id": item.get("id"),
            "name": item.get("name"),
            "type": item.get("type"),
            # Include only fields necessary for the tool's purpose
            # Exclude: detailed configurations, metadata, nested objects
        }
        simplified_items.append(simplified_item)
    return simplified_items

# Usage in tool implementation
simplified_data = extract_essential_fields(data)
response_data = {"items": simplified_data}
```

This approach provides several benefits:
- **Dramatically smaller responses** (often 10-100x reduction)
- **Faster processing** by Claude
- **Better user experience** with cleaner, focused data
- **Reduced bandwidth usage**
- **Enhanced security** by excluding sensitive configuration details

### Error Handling

Use the `format_error_response` function for consistent error responses:

```python
return format_error_response(
    status_code=status_code,  # HTTP status code
    error_type="error_type",  # Short error type identifier
    message="Error message",  # Human-readable error message
    request_info={           # Optional request context
        "endpoint": "/api/path",
        "method": "GET",
        "params": params
    }
)
```

### Logging

Use the module logger for consistent logging:

```python
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Log tool execution
logger.info(f"Tool called: tool_name()")

# Log errors
logger.error(f"Error in tool_name: {e}")
```

### Pagination for Large Result Sets

For API endpoints that may return large sets of data, implement pagination to ensure manageable response sizes. There are two types of pagination implementations in Talk to Metabase:

#### 1. API-Based Pagination

When the Metabase API natively supports pagination:

```python
@mcp.tool(name="list_resources", description="List resources with pagination")
async def list_resources(
    ctx: Context,
    page: int = 1,
    page_size: int = 50,
    # ... other filter parameters
) -> str:
    """
    List resources with pagination.
    
    Args:
        ctx: MCP context
        page: Page number (default: 1)
        page_size: Number of results per page (default: 50)
        # ... other filter parameter descriptions
        
    Returns:
        JSON string with paginated results and pagination metadata
    """
    client = get_metabase_client(ctx)
    
    try:
        # Make API request with pagination parameters
        data = await client.get_resources(page=page, page_size=page_size)
        
        # Format and return response with pagination metadata
        response = json.dumps({
            "results": data["items"],
            "pagination": {
                "page": page,
                "page_size": page_size,
                "total_count": data["total_count"],
                "total_pages": (data["total_count"] + page_size - 1) // page_size,
                "has_more": page < ((data["total_count"] + page_size - 1) // page_size)
            }
        }, indent=2)
        
        return check_response_size(response, ctx.request_context.lifespan_context.auth.config)
    except Exception as e:
        # ... error handling
```

#### 2. Client-Side Pagination

When the Metabase API doesn't support pagination but responses are too large:

```python
@mcp.tool(name="get_resource_with_items", description="Get resource with paginated items")
async def get_resource_with_items(
    id: int,
    ctx: Context,
    page: int = 1,
    page_size: int = 20
) -> str:
    """
    Get a resource with its items, applying client-side pagination.
    
    Args:
        id: Resource ID
        ctx: MCP context
        page: Page number (default: 1)
        page_size: Number of items per page (default: 20)
        
    Returns:
        JSON string with resource data and paginated items
    """
    # Validation for pagination parameters
    if page < 1:
        return format_error_response(
            status_code=400,
            error_type="invalid_pagination",
            message="Page number must be greater than or equal to 1",
            request_info={"resource_id": id, "page": page}
        )
    
    client = get_metabase_client(ctx)
    
    try:
        # Get the full resource (API doesn't support pagination)
        data = await client.get_resource(id)
        
        # Extract all items
        all_items = data.get("items", [])
        
        # Sort items if needed
        # all_items.sort(key=lambda item: (item.get("position", 0)))
        
        # Calculate pagination metadata
        total_items = len(all_items)
        total_pages = (total_items + page_size - 1) // page_size if total_items > 0 else 1
        
        if page > total_pages and total_pages > 0:
            return format_error_response(
                status_code=400,
                error_type="page_out_of_range",
                message=f"Page {page} exceeds the total number of pages ({total_pages})",
                request_info={"resource_id": id, "page": page, "total_pages": total_pages}
            )
        
        # Apply pagination
        start_idx = (page - 1) * page_size
        end_idx = min(start_idx + page_size, total_items)
        
        # Create paginated response
        paginated_data = {
            "id": data.get("id"),
            "name": data.get("name"),
            # Include other resource metadata...
            "items": all_items[start_idx:end_idx],
            "pagination": {
                "page": page,
                "page_size": page_size,
                "total_items": total_items,
                "total_pages": total_pages,
                "has_more": page < total_pages,
                "note": "Pagination is handled by the tool and not by the Metabase API"
            }
        }
        
        # Return the paginated response
        response = json.dumps(paginated_data, indent=2)
        return check_response_size(response, ctx.request_context.lifespan_context.auth.config)
    except Exception as e:
        # ... error handling
```

## Dashboard Tools with Pagination

Talk to Metabase implements a two-step approach for handling dashboards with large numbers of cards:

### 1. `get_dashboard` Tool

This tool provides metadata about a dashboard without including the full card data:

```python
@mcp.tool(name="get_dashboard", description="Retrieve a dashboard by ID without card details")
async def get_dashboard(id: int, ctx: Context) -> str:
    """
    Retrieve a dashboard by ID without card details.
    
    Args:
        id: Dashboard ID
        ctx: MCP context
        
    Returns:
        Dashboard data as JSON string without card details
    """
    # ... implementation details
```

Key features:
- Returns dashboard metadata (name, description, etc.)
- Includes tab information for multi-tab dashboards
- Parameters Management: Add and configure dashboard parameters for interactive filtering
- Provides total card count but doesn't include the cards themselves
- Adds an `is_single_tab` flag for dashboards without explicit tabs
- Significantly reduces response size by omitting card data

Example response:
```json
{
  "id": 1864,
  "name": "Analytics Dashboard",
  "description": "Key performance metrics",
  "dashcard_count": 35,
  "is_single_tab": true
}
```

### 2. `get_dashboard_tab` Tool

This tool retrieves the cards for a specific dashboard tab with pagination:

```python
@mcp.tool(name="get_dashboard_tab", description="Retrieve cards for a specific dashboard tab with pagination")
async def get_dashboard_tab(
    dashboard_id: int, 
    ctx: Context, 
    tab_id: Optional[int] = None,
    page: int = 1,
    page_size: int = 20
) -> str:
    """
    Retrieve cards for a specific dashboard tab with pagination.
    
    Args:
        dashboard_id: Dashboard ID
        ctx: MCP context
        tab_id: Tab ID (optional, if not provided for single-tab dashboards)
        page: Page number for pagination (default: 1)
        page_size: Number of cards per page (default: 20)
        
    Returns:
        Dashboard tab data with paginated cards as JSON string
    """
    # ... implementation details
```

Key features:
- Supports both single-tab and multi-tab dashboards
- Requires a tab_id parameter for multi-tab dashboards
- Returns cards in a consistent order (top to bottom, left to right)
- Applies client-side pagination to limit response size
- Processes each card to include essential information while reducing size
- Provides comprehensive pagination metadata

Example response:
```json
{
  "dashboard_id": 1864,
  "dashcards": [
    {
      "id": 55882,
      "card_id": null,
      "row": 0,
      "col": 0,
      "size_x": 24,
      "size_y": 1,
      "card_summary": {
        "id": null,
        "name": null
      },
      "visualization_settings": {
        "text": "### Overall",
        "text.align_vertical": "middle",
        "text.align_horizontal": "center"
      }
    },
    // ... more cards
  ],
  "pagination": {
    "page": 1,
    "page_size": 20,
    "total_cards": 35,
    "total_pages": 2,
    "has_more": true,
    "note": "Pagination is handled by the tool and not by the Metabase API"
  },
  "is_single_tab": true,
  "name": "Analytics Dashboard"
}
```

Implementation considerations:
- Cards are sorted by position (row, col) to match visual layout
- Card objects are simplified to include only essential information
- Card visualization settings are preserved to understand chart configuration
- Series cards are also processed and simplified

## Metabase API Endpoints

The following table shows the Metabase API endpoints that correspond to existing and planned tools, with an indicator of implementation status:

| Category | API Endpoint | Tool Name | Status |
|----------|-------------|-----------|--------|
| **Dashboard Operations** | `GET /api/dashboard/{id}` | `get_dashboard` | ✅ Implemented |
| | `GET /api/dashboard/{id}` | `get_dashboard_tab` | ✅ Implemented (with client-side pagination) |
| | `POST /api/dashboard/` | `create_dashboard` | ✅ Implemented |
| | `PUT /api/dashboard/{id}` | `update_dashboard` | ✅ Implemented (with dashcards, tabs and parameters support) |
| | `POST /api/dashboard/{dashboard-id}/cards` | `add_card_to_dashboard` | 📝 Planned |
| | `DELETE /api/dashboard/{id}` | `delete_dashboard` | 📝 Planned |
| **Card Operations** | `GET /api/card/{id}` | `get_card_definition` | ✅ Implemented |
| | `POST /api/card/` | `create_card` | ✅ Implemented (MBQL & SQL support) |
| | `PUT /api/card/{id}` | `update_card` | ✅ Implemented (MBQL & SQL support) |
| | `POST /api/card/{card-id}/query` | `execute_card_query` | ✅ Implemented (with dashboard context support) |
| | `DELETE /api/card/{id}` | `delete_card` | 📝 Planned |
| **Collection Operations** | `GET /api/collection/root/items` & `GET /api/collection/{id}/items` | `explore_collection_tree` & `view_collection_contents` | ✅ Implemented |
| | `GET /api/collection/{id}` | `get_collection` | 📝 Planned |
| | `POST /api/collection/` | `create_collection` | 📝 Planned |
| | `PUT /api/collection/{id}` | `update_collection` | 📝 Planned |
| **Database Operations** | `GET /api/database/` | `list_databases` | ✅ Implemented (simplified output) |
| | `GET /api/database/{id}/metadata` | `get_database_metadata` | ✅ Implemented (with schema organization) |
| | `GET /api/table/{id}` | `get_table` | 📝 Planned |
| | `GET /api/table/{id}/query_metadata` | `get_table_query_metadata` | ✅ Implemented (essential fields only) |
| **Query Operations** | `POST /api/dataset/` | `run_dataset_query` | ✅ Implemented |
| **MBQL Operations** | Schema-based | `GET_MBQL_SCHEMA` | ✅ Implemented (comprehensive MBQL documentation) |
| **Search Operations** | `GET /api/search/` | `search_resources` | ✅ Implemented with pagination |
| **Visualization Operations** | Various | `GET_VISUALIZATION_DOCUMENT` | ✅ Implemented (17 chart types) |

Implementation Legend:
- ✅ Implemented: Tool is fully implemented and available in the current version
- 📝 Planned: Tool is defined in specifications but not yet implemented

## Unified Card Query Execution Tool

The `execute_card_query` tool has been implemented as a unified solution for executing queries associated with cards, both as standalone cards and within dashboards. This implementation provides a flexible interface with contextual behavior based on the parameters provided.

### Key Features

1. **Contextual Behavior**: The tool automatically selects the appropriate API endpoint:
   - For standalone cards: `/api/card/{card-id}/query`
   - For dashboard cards: `/api/dashboard/{dashboard-id}/dashcard/{dashcard-id}/card/{card-id}/query`

2. **Parameter Validation**: The tool enforces validation rules for parameters:
   - `card_id` is always required
   - If `dashboard_id` is provided, `dashcard_id` is required
   - Optional parameters are properly handled with default values

3. **Enhanced Metadata**: The response includes additional metadata:
   - Execution context (card ID, dashboard ID if applicable)
   - Row count for the result set
   - Query type (standalone or dashboard)
   - Timestamp of execution

4. **Error Handling**: Comprehensive error handling for:
   - Missing required parameters
   - API errors from Metabase
   - Query execution failures

### Usage Examples

#### Standalone Card Query

```json
{
  "method": "tools/call",
  "params": {
    "name": "execute_card_query",
    "arguments": {
      "card_id": 123,
      "ignore_cache": true
    }
  },
  "jsonrpc": "2.0",
  "id": 1
}
```

#### Dashboard Card Query with Parameters

```json
{
  "method": "tools/call",
  "params": {
    "name": "execute_card_query",
    "arguments": {
      "card_id": 123,
      "dashboard_id": 456,
      "dashcard_id": 789,
      "parameters": [
        {"id": "date_range", "value": ["2023-01-01", "2023-12-31"]},
        {"id": "category", "value": "Electronics"}
      ]
    }
  },
  "jsonrpc": "2.0",
  "id": 2
}
```

### Response Structure

```json
{
  "data": {
    "rows": [
      ["Value 1", "Value 2", 123],
      ["Value 3", "Value 4", 456]
    ],
    "cols": [
      {"name": "Column 1", "display_name": "Column 1", "base_type": "type/Text"},
      {"name": "Column 2", "display_name": "Column 2", "base_type": "type/Text"},
      {"name": "Column 3", "display_name": "Column 3", "base_type": "type/Number"}
    ]
  },
  "status": "completed",
  "metadata": {
    "execution_context": {
      "card_id": 123,
      "dashboard_id": 456,
      "dashcard_id": 789,
      "query_type": "dashboard_card",
      "timestamp": 1684789123.456
    },
    "row_count": 2
  }
}
```

### Implementation Details

- The tool works directly with the Metabase API endpoints, making the appropriate POST requests
- For dashboard-contextualized queries, it provides a `dashboard_load_id` based on the current timestamp
- The implementation carefully processes and structures response data for Claude to use effectively
- Robust error handling captures and reports issues at all stages of execution

This unified implementation eliminates redundancy while providing a clean, flexible interface for executing card queries in different contexts. It gives Claude a powerful tool to access actual query data from both standalone cards and dashboard-contextualized cards, while preserving all the necessary context and parameters.

## Card Creation Tool

The `create_card` tool implements a flexible process for creating new cards in Metabase, supporting both SQL and MBQL queries. It provides a streamlined way to create questions, models, or metrics from either structured MBQL queries or raw SQL.

### Key Features

1. **Dual Query Support**: Supports both MBQL (query type) and SQL (native type) queries
2. **MBQL Schema Validation**: Comprehensive validation for MBQL queries without execution
3. **SQL Query Validation**: Executes SQL queries first to validate them before creating the card
4. **Support for Multiple Card Types**: Creates cards of type "question", "model", or "metric"
5. **Concise Responses**: Returns simplified success/error responses focused on essential information
6. **Optional Parameters**: Supports collection placement and descriptions
7. **Automatic Metadata**: Captures result metadata from validation query for better card integration

### Implementation Approach

The tool uses different validation approaches based on query type:

#### For MBQL Queries (query_type="query") - RECOMMENDED DEFAULT
1. Validates the MBQL query structure against comprehensive JSON schema
2. If the query is valid, creates a new card using the `/api/card/` endpoint
3. If validation fails, returns detailed schema validation errors

#### For SQL Queries (query_type="native")
1. First, executes the SQL query using the `/api/dataset/` endpoint to validate the query
2. If the query is valid, creates a new card using the `/api/card/` endpoint
3. If the query fails, returns the error message in a concise format

### Usage Examples

#### MBQL Query (Recommended)
```json
{
  "method": "tools/call",
  "params": {
    "name": "create_card",
    "arguments": {
      "database_id": 195,
      "query_type": "query",
      "query": {
        "source-table": 1,
        "aggregation": [["sum", ["field", 123, null]]],
        "breakout": [["field", 456, {"temporal-unit": "month"}]]
      },
      "name": "Monthly Revenue"
    }
  }
}
```

#### SQL Query
```json
{
  "method": "tools/call",
  "params": {
    "name": "create_card",
    "arguments": {
      "database_id": 195,
      "query_type": "native",
      "query": "SELECT * FROM reporting.bariendo_blended LIMIT 5",
      "name": "My New SQL Card",
      "collection_id": 123,
      "description": "A test card created via MCP"
    }
  },
  "jsonrpc": "2.0",
  "id": 1
}
```

### Response Structure

#### Success Response

```json
{
  "success": true,
  "card_id": 53832,
  "name": "My New SQL Card"
}
```

#### Error Response (MBQL Query Validation Failed)

```json
{
  "success": false,
  "error": "Invalid MBQL query",
  "validation_errors": [
    "Validation error at breakout -> 0: Expected array with 2-3 items"
  ],
  "help": "Call GET_MBQL_SCHEMA first to understand the correct MBQL format"
}
```

#### Error Response (SQL Query Validation Failed)

```json
{
  "success": false,
  "error": "ERROR: column \"non_existent_column\" does not exist"
}
```

### Implementation Details

- **Query Validation**: Uses a helper function `execute_sql_query` that executes the SQL and returns success/error information
- **Card Creation**: On successful validation, prepares a card creation payload with all necessary fields, including an empty `visualization_settings` object that's required by the Metabase API
- **Card Types**: Validates that the card_type is one of the supported types ("question", "model", or "metric")
- **Minimal Response**: Returns only essential information (success status, card ID, name) in the response
- **Error Handling**: Extracts clean error messages from Metabase's sometimes verbose error responses

### Helper Function: execute_sql_query

A utility function that executes SQL queries and processes the results:

```python
async def execute_sql_query(client, database_id: int, query: str) -> Dict[str, Any]:
    """Execute a SQL query to validate it before creating a card."""
    # Prepare the query payload
    query_data = {
        "database": database_id,
        "type": "native",
        "native": {
            "query": query,
            "template-tags": {}
        }
    }
    
    # Execute the query and handle results/errors
    # Returns a dict with success/error information
```

### Complete Examples

#### MBQL Card Creation
```python
async def create_card_mbql(database_id: int, query: dict, name: str, ctx: Context):
    """Create an MBQL-based card after validating the query."""
    # Validate MBQL query using schema
    if MBQL_AVAILABLE:
        validation_result = validate_mbql_query_helper(query)
        if not validation_result["valid"]:
            return json.dumps({
                "success": False, 
                "error": "Invalid MBQL query",
                "validation_errors": validation_result["errors"]
            })
    
    # Create the card with MBQL query
    card_data = {
        "name": name,
        "dataset_query": {
            "database": database_id,
            "query": query,
            "type": "query"
        },
        "display": "table",
        "type": "question",
        "visualization_settings": {}
    }
    
    # Submit to API and return success response
```

#### SQL Card Creation
```python
async def create_card_sql(database_id: int, query: str, name: str, ctx: Context):
    """Create a SQL-based card after validating the query."""
    # Validate the query by executing it
    query_result = await execute_sql_query(client, database_id, query)
    
    if not query_result["success"]:
        return json.dumps({"success": False, "error": query_result["error"]})
    
    # Create the card with all required fields
    card_data = {
    card_data = {
        "name": name,
        "dataset_query": {
            "database": database_id,
            "native": {"query": query, "template-tags": {}},
            "type": "native"
        },
        "display": "table",
        "type": "question",
        "visualization_settings": {}  # Required field, even if empty
    }
    
    # Submit to API and return success response
```

This implementation provides a clean, user-friendly way to create both MBQL and SQL cards in Metabase. MBQL queries benefit from comprehensive schema validation without execution overhead, while SQL queries are validated through execution to ensure they work correctly.

## Context Guidelines Tool

The `GET_METABASE_GUIDELINES` tool is a simple tool that provides instance-specific context and guidelines to Claude.

### Tool Characteristics

- **Conditional Loading**: Only loaded when `METABASE_CONTEXT_AUTO_INJECT=true`
- **Helpful Guidance**: Tool description recommends calling it first for best results
- **Built-in Content**: Contains comprehensive guidelines with template variable substitution
- **No Enforcement**: All other tools work normally regardless of whether guidelines are called

### Implementation Details

```python
@mcp.tool(name="GET_METABASE_GUIDELINES", description="IMPORTANT: Get essential Metabase context guidelines - Should be called first in any Metabase conversation")
async def get_metabase_guidelines(ctx: Context) -> str:
    """**IMPORTANT: Call this tool first for best results**
    
    Get essential Metabase context guidelines for this instance.
    While not technically required, calling this tool at the beginning of Metabase
    conversations will significantly improve response quality.
    """
    # Get configuration
    metabase_ctx = ctx.request_context.lifespan_context
    config = metabase_ctx.auth.config
    
    # Provide guidelines with template substitution
    # ... (template processing and response generation)
```

### Template Processing

The tool processes built-in guidelines and performs template variable substitution:
- `{METABASE_URL}` → Cleaned URL without trailing slashes
- `{METABASE_USERNAME}` → Configured username

### Response Format

```json
{
  "success": true,
  "guidelines": "# Metabase Guidelines for https://example.com\n\n...",
  "source": "built_in_guidelines",
  "metabase_url": "https://example.com",
  "username": "user@example.com"
}
```

### Error Handling

The tool includes comprehensive error handling and logging to track when guidelines are provided.

## Enhanced Search Tool with Pagination

The `search_resources` tool has been implemented with comprehensive pagination support to handle large result sets. This implementation includes:

### Response Structure

```json
{
  "results": [
    {
      "id": 1,
      "name": "Test Dashboard",
      "description": "A test dashboard",
      "model": "dashboard",
      ...
    },
    ... more items up to page_size
  ],
  "pagination": {
    "page": 1,
    "page_size": 50,
    "total_count": 243,
    "total_pages": 5,
    "has_more": true
  }
}
```

### Usage Example

```json
{
  "method": "tools/call",
  "params": {
    "name": "search_resources",
    "arguments": {
      "q": "Bariendo",
      "models": "[\"card\"]",
      "page": 1,
      "page_size": 50
    }
  },
  "jsonrpc": "2.0",
  "id": 5
}
```

### Implementation Details

The search tool supports all Metabase search API parameters, including:
- Full-text search query
- Filtering by model type (dashboard, card, collection, etc.)
- Filtering by created/edited timestamp and user
- Filtering by database ID
- Filtering by collection (personal/shared)
- Support for verified items
- Pagination parameters (page and page_size)

The implementation handles both JSON-formatted string parameters and native types, with proper error handling for parameter parsing issues.

## Collection Tools

Talk to Metabase provides two specialized tools for collection exploration and content viewing, each optimized for different use cases:

### 1. Collection Tree Explorer (`explore_collection_tree`)

This tool is designed for navigating the collection hierarchy. It shows only direct child collections while providing a comprehensive summary of all content types in the collection.

#### Key Features

1. **Collection Navigation**: Shows only child collections for easy hierarchy navigation
2. **Comprehensive Content Summary**: Provides counts for all item types (dashboard, card, collection, dataset, timeline, snippet, pulse, metric) in the collection
3. **Database Filtering**: Automatically filters out database items
4. **Simplified Collection Data**: Returns only essential collection information (id, name, model, location)

#### Usage Example

```json
{
  "method": "tools/call",
  "params": {
    "name": "explore_collection_tree",
    "arguments": {
      "collection_id": 123
    }
  },
  "jsonrpc": "2.0",
  "id": 1
}
```

#### Response Structure

```json
{
  "collection_id": 123,
  "child_collections": [
    {
      "id": 456,
      "name": "Marketing Analytics",
      "model": "collection",
      "location": "/"
    },
    {
      "id": 789,
      "name": "Sales Reports",
      "model": "collection"
    }
  ],
  "content_summary": {
    "dashboard": 18,
    "card": 15,
    "collection": 12,
    "dataset": 3,
    "timeline": 0,
    "snippet": 2,
    "pulse": 1,
    "metric": 0
  }
}
```

### 2. Collection Content Viewer (`view_collection_contents`)

This tool is designed for viewing all items within a collection, with optional filtering by content type.

#### Key Features

1. **Complete Content View**: Shows all direct children items in a collection
2. **Flexible Filtering**: Optional filtering by model types using the `models` parameter
3. **Simplified Item Data**: Returns only essential item information (id, name, model, location)
4. **Comprehensive Summary**: Provides counts for all item types in the collection

#### Usage Examples

**View all items:**
```json
{
  "method": "tools/call",
  "params": {
    "name": "view_collection_contents",
    "arguments": {
      "collection_id": 123
    }
  },
  "jsonrpc": "2.0",
  "id": 1
}
```

**View specific item types:**
```json
{
  "method": "tools/call",
  "params": {
    "name": "view_collection_contents",
    "arguments": {
      "collection_id": 123,
      "models": ["dashboard", "card"]
    }
  },
  "jsonrpc": "2.0",
  "id": 2
}
```

#### Response Structure

```json
{
  "collection_id": 123,
  "items": [
    {
      "id": 456,
      "name": "Q4 Revenue Dashboard",
      "model": "dashboard"
    },
    {
      "id": 789,
      "name": "Customer Analysis",
      "model": "card"
    },
    {
      "id": 101,
      "name": "Sales Data",
      "model": "dataset"
    }
  ],
  "content_summary": {
    "dashboard": 18,
    "card": 15,
    "collection": 12,
    "dataset": 3,
    "timeline": 0,
    "snippet": 2,
    "pulse": 1,
    "metric": 0
  }
}
```

#### Supported Model Types

Both tools support filtering and summarizing the following model types:
- `dashboard` - Interactive dashboards
- `card` - Questions/queries 
- `collection` - Sub-collections
- `dataset` - Models/datasets
- `timeline` - Timeline events
- `snippet` - SQL snippets
- `pulse` - Automated reports
- `metric` - Business metrics

### Implementation Details

- Both tools use the `/api/collection/root/items` endpoint for root collections and `/api/collection/{id}/items` for specific collections
- Database items are automatically filtered out as they are managed by separate database tools
- The tree explorer always fetches all item types to provide accurate summaries, then filters the display to show only collections
- The content viewer respects the `models` parameter for API-level filtering when specified
- All responses include comprehensive summaries with counts for all supported model types
- Items are simplified to include only essential fields for efficient exploration

This two-tool approach provides both efficient collection hierarchy navigation and detailed content viewing, allowing Claude to choose the appropriate tool based on the user's needs.

## Dataset Query Tool

The `run_dataset_query` tool has been implemented to allow direct execution of both native SQL and structured MBQL queries against Metabase databases. The implementation follows Talk to Metabase best practices by focusing on essential fields while maintaining all critical information.

### Key Features

1. **Dual Query Support**: Handles both native SQL queries and structured MBQL queries
2. **Essential Field Focus**: Returns only the most important fields for query results
3. **Comprehensive Error Handling**: Preserves detailed error information for debugging SQL issues
4. **Parameter Validation**: Validates required parameters based on query type
5. **Clean Response Structure**: Organized, consistent response format for all query types

### Usage Examples

#### Native SQL Query

```json
{
  "method": "tools/call",
  "params": {
    "name": "run_dataset_query",
    "arguments": {
      "database": 195,
      "native": {
        "query": "select channel, date, SUM(spend) from reporting.bariendo_blended WHERE date_granularity='week' GROUP BY 1,2"
      }
    }
  },
  "jsonrpc": "2.0",
  "id": 1
}
```

#### MBQL Structured Query

```json
{
  "method": "tools/call",
  "params": {
    "name": "run_dataset_query",
    "arguments": {
      "database": 195,
      "query": {
        "source-table": 50112,
        "aggregation": [["sum", ["field", 50705151, null]]],
        "breakout": [
          ["field", 50705149, null],
          ["field", 50705150, null]
        ]
      },
      "type": "query"
    }
  },
  "jsonrpc": "2.0",
  "id": 2
}
```

### Response Structure

```json
{
  "data": {
    "rows": [
      ["Google", "2025-04-14T00:00:00Z", 18316.65625],
      ["Meta", "2025-03-10T00:00:00Z", 15587.970000000001]
    ],
    "cols": [
      {"name": "channel", "display_name": "channel", "base_type": "type/Text"},
      {"name": "date", "display_name": "date", "base_type": "type/Date"},
      {"name": "sum", "display_name": "sum", "base_type": "type/Float"}
    ],
    "native_form": {
      "query": "select channel, date, SUM(spend) from reporting.bariendo_blended WHERE date_granularity='week' GROUP BY 1,2"
    }
  },
  "status": "completed",
  "database_id": 195,
  "started_at": "2025-05-23T15:26:04.524227594Z",
  "running_time": 6242,
  "row_count": 2,
  "results_timezone": "UTC"
}
```

### Error Response Example

```json
{
  "success": false,
  "error": {
    "status_code": 400,
    "error_type": "query_error",
    "message": "ERROR: column \"bariendo_blended.channel\" must appear in the GROUP BY clause or be used in an aggregate function",
    "request_info": {
      "endpoint": "/api/dataset",
      "method": "POST",
      "database": 195,
      "query_type": "native"
    },
    "raw_response": {
      "database_id": 195,
      "started_at": "2025-05-23T15:36:30.405166542Z",
      "status": "failed",
      "error": "ERROR: column \"bariendo_blended.channel\" must appear in the GROUP BY clause or be used in an aggregate function",
      "error_type": "invalid-query"
    }
  }
}
```

### Implementation Details

- The tool works directly with the Metabase `/api/dataset/` endpoint for executing queries
- Parameter validation ensures the appropriate query objects are provided based on type
- Responses include only essential fields to maintain performance and readability
- Comprehensive error handling captures and formats SQL errors for easier debugging
- The implementation follows the same patterns as other Talk to Metabase tools for consistency

This implementation provides Claude with a powerful way to directly execute SQL and MBQL queries against Metabase databases, while focusing on essential output fields for better performance and readability.

## Dashboard Update Tool with Cards, Tabs, Parameters and Parameter Mappings

The `update_dashboard` tool has been enhanced to support adding cards, managing tabs, configuring parameters, and establishing parameter mappings in Metabase dashboards, providing comprehensive dashboard management capabilities.

### Key Features

1. **Dashcards Management**: Add new cards to dashboards with precise grid positioning
2. **Parameter Mappings**: Link dashboard parameters to card parameters by name
3. **Tabs Management**: Create and manage dashboard tabs for multi-tab dashboards
4. **Parameters Management**: Add and configure dashboard parameters for interactive filtering
5. **Strict Validation**: JSON schema validation for dashcards and parameters with business rule enforcement
6. **Grid Constraints**: Automatic validation of dashboard grid boundaries (24-column system)
7. **Automatic Processing**: Convert name-based parameter mappings to ID-based mappings for Metabase API
8. **Metadata Updates**: Support for updating dashboard name, description, collection, and archived status

### Dashcards Support

The tool supports adding cards to dashboards using the `dashcards` parameter with strict validation:

#### Dashcard Structure
```json
{
  "id": integer,           // Existing ID for updates, negative (-1, -2, -3) for new cards
  "card_id": integer,      // Required: 5-digit card ID from Metabase
  "col": integer,          // Required: Column position (0-23)
  "row": integer,          // Required: Row position (0+)
  "size_x": integer,       // Required: Width in columns (1-24)
  "size_y": integer,       // Required: Height in rows (1+)
  "dashboard_tab_id": int, // Optional: Tab ID for multi-tab dashboards
  "parameter_mappings": [  // Optional: Link dashboard parameters to card parameters
    {
      "dashboard_parameter_name": "Status Filter",
      "card_parameter_name": "order_status"
    }
  ]
}
```

#### Validation Rules

1. **Required Fields**: `card_id`, `col`, `row`, `size_x`, `size_y`
2. **Grid Constraints**: 
   - `col` range: 0-23 (24 columns total)
   - `size_x` range: 1-24
   - `col + size_x` must not exceed 24
3. **Forbidden Keys**: `action_id`, `series`, `visualization_settings` (parameter_mappings is now allowed)
4. **ID Convention**: Use existing positive IDs for updates, negative IDs (-1, -2, -3) for new cards

#### Usage Example

```json
{
  "method": "tools/call",
  "params": {
    "name": "update_dashboard",
    "arguments": {
      "id": 1864,
      "dashcards": [
        {
          "id": -1,
          "card_id": 53832,
          "col": 0,
          "row": 0,
          "size_x": 12,
          "size_y": 8
        },
        {
          "id": -2,
          "card_id": 53845,
          "col": 12,
          "row": 0,
          "size_x": 12,
          "size_y": 8,
          "parameter_mappings": [
            {
              "dashboard_parameter_name": "Status Filter",
              "card_parameter_name": "order_status"
            },
            {
              "dashboard_parameter_name": "Date Range",
              "card_parameter_name": "date_filter"
            }
          ]
        }
      ]
    }
  }
}
```

### Parameter Mappings Support

The tool supports linking dashboard parameters to card parameters through the `parameter_mappings` field in dashcards. This creates the connection that allows dashboard filters to control card behavior.

#### Parameter Mapping Structure
```json
{
  "dashboard_parameter_name": "Status Filter",
  "card_parameter_name": "order_status"
}
```

#### Key Features

1. **Name-Based Identification**: Both dashboard and card parameters are identified by their names
2. **Automatic ID Resolution**: The system automatically converts names to internal IDs and targets
3. **Validation**: Ensures both dashboard and card parameters exist before creating mappings
4. **Card Parameter Support**: Card parameters can be referenced by either name or slug
5. **Comprehensive Error Messages**: Clear feedback when parameter names don't match

#### Processing Flow

1. **Parameter Validation**: Validates that dashboard parameter names exist in the dashboard parameters configuration
2. **Card Parameter Retrieval**: Fetches card parameters from Metabase for each card with parameter mappings
3. **Name Resolution**: Matches card parameter names (or slugs) to actual parameter objects
4. **ID Conversion**: Converts name-based mappings to ID-based mappings for the Metabase API
5. **Target Extraction**: Extracts the appropriate target information from card parameters

#### Generated Metabase API Format

The system converts name-based mappings like this:

```json
// Input (name-based)
{
  "dashboard_parameter_name": "Status Filter",
  "card_parameter_name": "order_status"
}

// Generated (ID-based for Metabase API)
{
  "card_id": 54276,
  "parameter_id": "ab12cd34",  // Dashboard parameter ID
  "target": ["variable", ["template-tag", "order_status"]]  // Card parameter target
}
```

#### Error Handling

The system provides detailed error messages for parameter mapping issues:

```json
{
  "success": false,
  "error": "Parameter mapping validation failed",
  "validation_errors": [
    "Dashcard 0 mapping 0: Dashboard parameter 'Status Filter' not found in dashboard parameters",
    "Dashcard 1 mapping 0: Card parameter 'customer_filter' not found in card 54276. Available: ['order_status', 'date_filter']"
  ],
  "help": "Check that dashboard parameter names and card parameter names match exactly."
}
```

### Tabs Support

The tool supports creating and managing dashboard tabs using the `tabs` parameter:

#### Tab Structure
```json
{
  "id": integer,           // Existing ID for updates, negative (-1, -2, -3) for new tabs
  "name": string           // Required: Tab name
}
```

#### Validation Rules

1. **Required Fields**: `name` (must be string)
2. **Optional Fields**: `id` (must be integer if provided)
3. **ID Convention**: Use existing positive IDs for updates, negative IDs for new tabs
4. **Restricted Fields**: Only `id` and `name` are allowed

#### Usage Example

```json
{
  "method": "tools/call",
  "params": {
    "name": "update_dashboard",
    "arguments": {
      "id": 1864,
      "tabs": [
        {
          "id": 1,
          "name": "Overview"
        },
        {
          "id": -1,
          "name": "Details"
        }
      ]
    }
  }
}
```

### Parameters Support

The tool supports adding and managing dashboard parameters using the `parameters` parameter with strict validation:

#### Parameter Structure
```json
{
  "id": string,            // 8-character hex ID, auto-generated for new parameters
  "name": string,          // Required: Parameter name (cannot be 'tab')
  "type": string,          // Required: Parameter type (e.g., "date/all-options", "string/=")
  "sectionId": string,     // Optional: Parameter section ("date", "string", etc.)
  "default": value,        // Optional: Default value (required if parameter is required)
  "isMultiSelect": boolean // Optional: Whether multiple values can be selected
}
```

#### Validation Rules

1. **Required Fields**: `name`, `type`
2. **Name Constraints**: Cannot be 'tab' (reserved for dashboard tabs)
3. **ID Format**: 8-character hexadecimal string, auto-generated for new parameters
4. **Type-Specific Validation**:
   - `temporal-unit` parameters must have `sectionId` set to "temporal-unit" and non-empty `temporal_units` array
   - String contains/starts-with/ends-with cannot have `isMultiSelect` set to true
5. **Required Parameters**: If `required` is true, must have a non-empty default value

#### Usage Example

```json
{
  "method": "tools/call",
  "params": {
    "name": "update_dashboard",
    "arguments": {
      "id": 1864,
      "parameters": [
        {
          "name": "Date Filter",
          "type": "date/all-options",
          "sectionId": "date",
          "default": "past30days"
        },
        {
          "id": "fa3f29d7",
          "name": "Category",
          "type": "string/=",
          "sectionId": "string",
          "isMultiSelect": true
        }
      ]
    }
  }
}
```

### Combined Updates

The tool supports updating multiple aspects of a dashboard simultaneously:

```json
{
  "method": "tools/call",
  "params": {
    "name": "update_dashboard",
    "arguments": {
      "id": 1864,
      "name": "Updated Dashboard Name",
      "description": "New description",
      "tabs": [
        {"id": -1, "name": "New Tab"}
      ],
      "dashcards": [
        {
          "id": -1,
          "card_id": 53832,
          "col": 0,
          "row": 0,
          "size_x": 24,
          "size_y": 12,
          "dashboard_tab_id": -1
        }
      ],
      "parameters": [
        {
          "name": "Date Range",
          "type": "date/range",
          "sectionId": "date"
        }
      ]
    }
  }
}
```

### Supporting Tools

#### GET_DASHCARDS_SCHEMA

A dedicated tool that returns the JSON schema for dashcards validation:

```json
{
  "method": "tools/call",
  "params": {
    "name": "GET_DASHCARDS_SCHEMA",
    "arguments": {}
  }
}
```

Returns the complete schema with usage guidelines, constraints, and examples.

#### GET_PARAMETERS_SCHEMA

A dedicated tool that returns the JSON schema for parameters validation:

```json
{
  "method": "tools/call",
  "params": {
    "name": "GET_PARAMETERS_SCHEMA",
    "arguments": {}
  }
}
```

Returns the complete schema with usage guidelines, constraints, and examples.

### Implementation Architecture

#### Validation Modules

1. **Dashcards Validation** (`/talk_to_metabase/tools/dashcards.py`):
   - JSON schema validation against `/talk_to_metabase/schemas/dashcards.json`
   - Business rule validation (grid constraints)
   - Parameter mapping validation and processing
   - Helper functions for structured validation results

2. **Tabs Validation** (in `dashcards.py`):
   - Simple validation for tab structure
   - Field type checking and constraint validation
   - No JSON schema required due to simplicity

3. **Parameters Validation** (`/talk_to_metabase/tools/parameters.py`):
   - JSON schema validation against `/talk_to_metabase/schemas/parameters.json`
   - Business rule validation (type-specific constraints)
   - Automatic ID generation for new parameters (8-character hex format)
   - Helper functions for structured validation results

#### Validation Flow

```python
# Dashcards validation
if dashcards is not None:
    validation_result = validate_dashcards_helper(dashcards)
    if not validation_result["valid"]:
        return validation_error_response

# Tabs validation  
if tabs is not None:
    tabs_validation_result = validate_tabs_helper(tabs)
    if not tabs_validation_result["valid"]:
        return validation_error_response

# Parameters validation
if parameters is not None:
    parameters_validation_result = validate_parameters_helper(parameters)
    if not parameters_validation_result["valid"]:
        return validation_error_response
    
    # Process parameters to ensure all have IDs
    parameters = process_parameters(parameters)

# Parameter mappings validation and processing
if dashcards is not None and parameters is not None:
    # Check if any dashcard has parameter mappings
    has_parameter_mappings = any(
        "parameter_mappings" in dashcard and dashcard["parameter_mappings"]
        for dashcard in dashcards
    )
    
    if has_parameter_mappings:
        # Validate parameter mappings and collect card parameters
        card_parameters_by_card, mapping_errors = await validate_parameter_mappings(
            client, dashcards, parameters
        )
        
        if mapping_errors:
            return validation_error_response
        
        # Process parameter mappings to convert from name-based to ID-based
        processed_dashcards, processing_errors = await process_parameter_mappings(
            client, dashcards, parameters, card_parameters_by_card
        )
        
        if processing_errors:
            return validation_error_response
        
        # Replace original dashcards with processed ones
        dashcards = processed_dashcards

# Proceed with update if all validations pass
```

#### Error Responses

Validation errors provide clear, actionable feedback:

```json
{
  "success": false,
  "error": "Invalid dashcards format",
  "validation_errors": [
    "Dashcard 0: forbidden key 'action_id' is not allowed",
    "Dashcard 1: col (20) + size_x (10) = 30 exceeds grid width of 24"
  ],
  "help": "Call GET_DASHCARDS_SCHEMA to understand the correct format."
}
```

### Success Response

The tool returns a concise success response with essential information:

```json
{
  "success": true,
  "dashboard_id": 1864,
  "name": "Updated Dashboard",
  "dashcard_count": 2,
  "tab_count": 2,
  "parameter_count": 3
}
```

### Benefits

1. **Complete Dashboard Management**: Single tool for all dashboard update operations including parameter linking
2. **Type Safety**: Strict validation prevents invalid configurations
3. **Parameter Integration**: Seamless linking between dashboard and card parameters
4. **Grid System Support**: Automatic validation of Metabase's 24-column grid system
5. **Name-Based Parameter Mapping**: Intuitive parameter linking using names instead of IDs
6. **Future Extensibility**: Architecture supports adding more complex features later
7. **Clear Error Messages**: Actionable validation feedback with specific error locations
8. **Modular Design**: Validation logic separated into reusable modules

### Future Extensibility

The implementation is designed to easily support additional features:

1. **Visualization Settings**: Can be added by removing from forbidden keys and adding validation
2. **Advanced Parameter Mappings**: Support for field filters and complex target types
3. **Series Cards**: Can be supported by extending the validation system
4. **Advanced Grid Features**: Layout optimization and collision detection
5. **Parameter Mapping Templates**: Pre-defined mapping patterns for common use cases

This implementation provides a solid foundation for dashboard management while maintaining simplicity and leaving room for future enhancements.

## Configuration Options

Talk to Metabase is configured through environment variables, which can be set in a `.env` file or in the Claude Desktop configuration:

| Parameter | Description | Default |
|-----------|-------------|---------|
| METABASE_URL | Base URL of the Metabase instance | (Required) |
| METABASE_USERNAME | Username for authentication | (Required) |
| METABASE_PASSWORD | Password for authentication | (Required) |
| RESPONSE_SIZE_LIMIT | Maximum size (characters) for responses | 100000 |
| METABASE_CONTEXT_AUTO_INJECT | Whether to automatically load context guidelines | true |
| MCP_TRANSPORT | Transport method (stdio, sse, streamable-http) | stdio |
| LOG_LEVEL | Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL) | INFO |

## Metabase Context Guidelines System

Talk to Metabase includes a context guidelines system that automatically retrieves organization-specific guidelines from your Metabase instance.

### Overview

The context system operates in two modes:

#### Default Mode (`METABASE_CONTEXT_AUTO_INJECT=true`)
- Loads the `GET_METABASE_GUIDELINES` tool
- Automatically retrieves custom guidelines from Metabase if available
- Falls back to default guidelines with setup instructions if not found
- No enforcement - all tools work normally
- Provides comprehensive information about the Metabase instance

#### Disabled Mode (`METABASE_CONTEXT_AUTO_INJECT=false`)
- Guidelines tool is not loaded
- All other tools work normally without any guidelines functionality

### Custom Guidelines Storage

Custom guidelines are stored directly in your Metabase instance:

1. **Collection Location**: "000 Talk to Metabase" collection at root level
2. **Dashboard**: "Talk to Metabase Guidelines" dashboard within that collection
3. **Content**: Guidelines text stored in a text box dashcard

### Template Variable Substitution

Both custom and default guidelines support template variables that are automatically replaced:
- `{METABASE_URL}` → Your configured Metabase URL (without trailing slash)
- `{METABASE_USERNAME}` → Your configured username

### Implementation Details

The context system uses:

- **Conditional Tool Loading** (`tools/__init__.py`): Only loads context tools when enabled
- **Dynamic Guidelines Retrieval** (`tools/context.py`): Searches Metabase for custom guidelines
- **Fallback Mechanism**: Provides setup instructions when custom guidelines aren't found
- **Simple Implementation**: No state tracking or enforcement - just helpful guidance

### API Flow for Custom Guidelines

When `GET_METABASE_GUIDELINES` is called, the system:

1. **Searches for Collection**:
   ```
   GET /api/collection/root/items?models=collection
   ```
   Looks for collection named "000 Talk to Metabase"

2. **Searches for Dashboard** (if collection found):
   ```
   GET /api/collection/{collection_id}/items?models=dashboard
   ```
   Looks for dashboard named "Talk to Metabase Guidelines"

3. **Retrieves Dashboard Content** (if dashboard found):
   ```
   GET /api/dashboard/{dashboard_id}
   ```
   Extracts text content from text box dashcards

4. **Template Substitution**: Replaces `{METABASE_URL}` and `{METABASE_USERNAME}` in the content

5. **Fallback**: If any step fails, returns default guidelines with setup instructions

### Default Guidelines Content

When custom guidelines are not found, the system provides:
- Setup instructions for creating custom guidelines
- General best practices for Metabase usage
- Instance-specific information (URL, username)
- Recommendations for query performance and dashboard design

### Benefits

- **Organization-Specific**: Guidelines can be tailored to your specific Metabase setup
- **Centrally Managed**: Guidelines are stored and managed within Metabase itself
- **Version Controlled**: Changes to guidelines are tracked in Metabase
- **User-Friendly**: No technical setup required - just create dashboard content
- **Template Support**: Automatic variable substitution for dynamic content
- **Graceful Fallback**: Provides helpful setup instructions when not configured

## Testing Your Implementation

### Unit Testing

Run the unit tests to ensure your implementation works correctly:

```bash
pytest -v tests/unit/test_your_module.py
```

For testing pagination functionality, create tests that verify:
1. Correct page slicing with different page sizes
2. Accurate metadata calculation (total pages, has_more flag)
3. Edge cases (first page, last page, empty results)
4. Validation of pagination parameters
5. Proper sorting of results before pagination

### Testing with Claude Desktop

To test with Claude Desktop:

1. Update your Claude Desktop configuration to include the Talk to Metabase server
2. Start a conversation with Claude
3. Ask questions that would trigger your new tool
4. Check the server logs for any issues

For paginated results, test multi-step interactions where Claude requests:
1. First dashboard metadata with `get_dashboard`
2. Then a specific tab's cards with `get_dashboard_tab` 
3. Then navigates through pages by incrementing the page parameter

## Common Issues and Troubleshooting

### Authentication Issues

If authentication fails:
- Check the Metabase credentials in the `.env` file
- Verify the Metabase URL is correct and accessible
- Check for network connectivity issues

### Tool Registration Issues

If tools aren't appearing in Claude:
- Ensure the tool is properly decorated with `@mcp.tool(name="name", description="description")`
- Check that the module is imported in `tools/__init__.py`
- Verify the parameter order in the function signature

### Response Size Issues

If responses are being truncated:
- The response likely exceeds the configured size limit
- Use pagination with appropriate page_size to reduce response size
- For large dashboards, use the two-step approach with `get_dashboard` followed by `get_dashboard_tab`
- Adjust the `RESPONSE_SIZE_LIMIT` value if larger responses are required

### Parameter Parsing Issues

If string-formatted parameters (like JSON arrays or objects) aren't being parsed correctly:
- Add explicit parsing for string representation of complex types
- Include proper error handling for parsing failures
- Log the original parameter value and type for debugging

### Tab ID Issues

If experiencing issues with dashboard tabs:
- Verify that the tab_id parameter is only provided for multi-tab dashboards
- Ensure tab_id is correctly validated against the available tabs
- Check that client-side pagination is working correctly for the specific tab

## Database Tools

Talk to Metabase provides essential database connectivity tools optimized for performance and usability.

### List Databases Tool (`list_databases`)

The `list_databases` tool has been optimized to provide only essential database information, dramatically reducing response size while maintaining all necessary functionality for database selection.

#### Key Features

1. **Ultra-Minimal Response**: Returns only `id`, `name`, and `engine` for each database
2. **Dramatic Size Reduction**: Reduces response size from ~500 lines to ~5 lines per database
3. **Fast Performance**: Eliminates unnecessary data processing and transmission
4. **Easy Database Selection**: Provides exactly what's needed to identify and work with databases

#### Usage Example

```json
{
  "method": "tools/call",
  "params": {
    "name": "list_databases",
    "arguments": {}
  },
  "jsonrpc": "2.0",
  "id": 1
}
```

#### Response Structure

```json
{
  "databases": [
    {
      "id": 130,
      "name": "Ask Tia",
      "engine": "redshift"
    },
    {
      "id": 144,
      "name": "AUrate",
      "engine": "redshift"
    },
    {
      "id": 189,
      "name": "Baret Scholars",
      "engine": "redshift"
    }
  ]
}
```

#### Implementation Details

- **Response Processing**: Extracts only essential fields from the full Metabase API response
- **Error Handling**: Handles both list and dict response formats from the API
- **Size Optimization**: Eliminates detailed connection info, features arrays, and metadata
- **Simplified Structure**: Returns a clean `databases` array without pagination (databases are typically few in number)

#### Benefits Over Previous Implementation

- **Performance**: ~100x smaller response size (from ~500 lines to ~5 lines per database)
- **Clarity**: Users can quickly scan available databases
- **Security**: Removes sensitive connection details and configuration
- **Efficiency**: Faster parsing and processing for Claude
- **Usability**: Clean, readable output focused on user needs

### Database Metadata Tool (`get_database_metadata`)

The `get_database_metadata` tool retrieves essential metadata about a database, including its tables organized by schema. It's designed to provide a clean, hierarchical view of database structure while keeping the response size manageable.

#### Key Features

1. **Simplified Database Info**: Returns only essential database information (`id`, `name`, `engine`, `timezone`)
2. **Schema Organization**: Tables are grouped by schema for easier navigation
3. **Simplified Table Details**: Each table includes only essential information (`id`, `name`, `entity_type`)
4. **Summary Statistics**: Includes total table count and schema count
5. **Performance Optimization**: Always uses `skip_fields=true` to avoid fetching field metadata

#### Usage Example

```json
{
  "method": "tools/call",
  "params": {
    "name": "get_database_metadata",
    "arguments": {
      "id": 130
    }
  },
  "jsonrpc": "2.0",
  "id": 1
}
```

#### Response Structure

```json
{
  "database": {
    "id": 130,
    "name": "Ask Tia",
    "engine": "redshift",
    "timezone": "GMT"
  },
  "schemas": [
    {
      "name": "facebook_raw",
      "tables": [
        {
          "id": 34320,
          "name": "account_history",
          "entity_type": "entity/UserTable"
        },
        {
          "id": 34429,
          "name": "ad_campaign_issues_info",
          "entity_type": "entity/GenericTable"
        }
      ]
    },
    {
      "name": "googleads_raw",
      "tables": [
        {
          "id": 34422,
          "name": "account_history",
          "entity_type": "entity/UserTable"
        },
        {
          "id": 34322,
          "name": "account_hourly_stats",
          "entity_type": "entity/UserTable"
        }
      ]
    }
  ],
  "table_count": 4,
  "schema_count": 2
}
```

#### Implementation Details

- **Skip Fields**: Always uses the `skip_fields=true` parameter to avoid fetching field metadata, which can be extremely large
- **Schema Organization**: Tables are grouped by their schema name for easier navigation
- **No Redundancy**: Schema name only appears once as the key for each group of tables
- **Essential Information**: Only includes the minimal information needed to understand and navigate the database structure
- **Error Handling**: Handles missing schemas gracefully by grouping tables with empty schema under an empty string key

#### Benefits

- **Structured View**: Provides a clear hierarchical view of the database organization
- **Reduced Size**: Significantly smaller response size compared to raw Metabase API response
- **Schema Navigation**: Easy to understand which tables belong to which schemas
- **Quick Statistics**: Includes table count and schema count for quick reference
- **Simplified Integration**: Makes it easier for Claude to understand and navigate database structure

### Table Query Metadata Tool (`get_table_query_metadata`)

The `get_table_query_metadata` tool retrieves detailed metadata about a specific table that is essential for building and executing queries. This tool provides comprehensive field information while maintaining a clean, simplified output structure.

#### Key Features

1. **Essential Information Only**: Returns only the fields necessary for query building, excluding optional metadata like fingerprints and dimension options
2. **Field Categorization**: Automatically categorizes fields as primary keys and date fields for easy identification
3. **Optional Parameters**: Supports Metabase API parameters for including sensitive, hidden, or editable data model fields
4. **Simplified Structure**: Clean, organized response structure with table, database, and field information
5. **Performance Optimization**: Excludes verbose metadata to keep response size manageable

#### Usage Example

```json
{
  "method": "tools/call",
  "params": {
    "name": "get_table_query_metadata",
    "arguments": {
      "id": 50112,
      "include_sensitive_fields": false,
      "include_hidden_fields": false,
      "include_editable_data_model": false
    }
  },
  "jsonrpc": "2.0",
  "id": 1
}
```

#### Response Structure

```json
{
  "table": {
    "id": 50112,
    "name": "bariendo_blended",
    "schema": "reporting",
    "entity_type": "entity/GenericTable",
    "description": null,
    "view_count": 75
  },
  "database": {
    "id": 195,
    "name": "Bariendo",
    "engine": "redshift",
    "timezone": "UTC"
  },
  "fields": [
    {
      "id": 50705149,
      "name": "date",
      "display_name": "Date",
      "base_type": "type/Date",
      "effective_type": "type/Date",
      "semantic_type": null,
      "database_type": "date",
      "active": true,
      "visibility_type": "normal",
      "has_field_values": "none",
      "position": 0
    }
    // ... more fields
  ],
  "field_count": 11,
  "primary_key_fields": [],
  "date_fields": ["date"]
}
```

#### Implementation Details

- **Essential Fields Only**: Each field includes only the 11 essential properties needed for query building
- **Field Categorization**: Automatically identifies primary key fields (semantic_type = "type/PK") and date fields (base_type includes Date/DateTime variants)
- **Sorted Output**: Fields are sorted by position for consistent ordering
- **Parameter Support**: All three Metabase API optional parameters are supported with proper boolean handling
- **Error Handling**: Comprehensive error handling for API failures and missing data
- **Response Size Control**: Uses the standard response size checking mechanism

#### Excluded Information

To maintain clean, focused output, the following information is intentionally excluded:
- Field fingerprint statistical data
- Dimension options arrays and counts
- Internal metadata fields (entity_id, fingerprint_version, etc.)
- Database connection details and verbose configuration
- Field relationship information and constraints

#### Benefits

- **Clean Output**: Dramatically smaller response size compared to raw Metabase API response
- **Query-Focused**: Includes exactly what's needed for building queries and understanding table structure
- **Fast Processing**: Efficient for Claude to parse and understand
- **Categorized Fields**: Easy identification of key field types (primary keys, dates)
- **Essential Context**: Maintains necessary database and table context information

## Performance Considerations

### Authentication Caching

The server caches the authentication token to reduce API calls. The token is refreshed automatically if it expires.

### Response Size Limitations

Large responses are checked against the configured size limit to prevent overwhelming Claude or the client application. Use pagination to manage large result sets.

#### Response Size Optimization Strategies

1. **Simplified Tool Outputs**: Tools like `list_databases` return only essential information
2. **Pagination**: Implement client-side or server-side pagination for large datasets
3. **Two-Step Approaches**: Use metadata tools followed by detailed data tools (e.g., `get_dashboard` + `get_dashboard_tab`)
4. **Field Selection**: Extract only necessary fields from API responses

### Rate Limiting

Be aware of Metabase's rate limiting. If you implement tools that make many API calls, consider adding rate limiting or debouncing logic.

### Pagination Efficiency

For very large result sets, consider implementing:
- Client-side pagination (implemented in dashboard and search tools)
- Server-side pagination if the API supports it
- Cursor-based pagination for efficient scrolling through results
- Appropriate caching for paginated results

### Dashboard Processing

When working with dashboards:
- Remove nested card data in the `get_dashboard` tool to reduce response size
- Process dashcards in `get_dashboard_tab` to include only essential information
- Sort dashcards by position for a consistent user experience
- Use appropriate page sizes based on typical dashboard layouts

## Next Steps for Development

The current implementation includes comprehensive functionality for retrieving and searching Metabase resources with pagination, executing queries for both standalone cards and cards within dashboards, creating new cards with both MBQL and SQL support, comprehensive MBQL schema validation, and providing dynamic context guidelines. Future development should focus on:

1. Implementing the remaining tools defined in the specifications
2. Adding integration tests with a real Metabase instance
3. Implementing caching for frequently accessed resources
4. Adding more sophisticated error handling
5. Implementing additional advanced query capabilities
6. Enhancing pagination for other large resource types
7. Improving parameter parsing for complex types
8. Enhancing dashboard filter and parameter support
9. **MBQL Enhancements**:
   - Adding SQL-to-MBQL conversion utilities
   - Implementing MBQL query optimization suggestions
   - Adding support for MBQL query templates
   - Enhancing MBQL documentation with more complex examples
10. **Context System Enhancements**:
    - Adding validation for guidelines content format
    - Implementing role-based context variations
    - Adding collection-specific context information
    - Supporting multiple text boxes for structured guidelines

## Conclusion

By following these guidelines, you can effectively extend and improve the Talk to Metabase MCP server. The comprehensive MBQL implementation provides a powerful, database-agnostic way to create analytical queries that leverage Metabase's native query format. The pagination patterns established for dashboard and search resources provide a robust foundation for handling large datasets while maintaining performance and usability.

Remember to maintain consistency with the existing code patterns and to thoroughly test your implementations, especially for MBQL queries and pagination functionality which requires careful validation of edge cases.

The MBQL implementation represents a significant enhancement to Talk to Metabase, enabling users to create sophisticated analytical queries using Metabase's structured query language. This approach offers superior type safety, database portability, and semantic clarity compared to raw SQL for most analytical use cases.

The enhanced context guidelines system provides a powerful way to ensure Claude has organization-specific context when working with Metabase. By storing guidelines directly in Metabase, organizations can easily maintain and update their AI assistant's knowledge about their specific data infrastructure, leading to more accurate and contextually appropriate responses.

Happy coding!
