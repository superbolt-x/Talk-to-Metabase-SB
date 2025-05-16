# SuperMetabase MCP Developer Guide

This document provides comprehensive guidance for developers who will be implementing or modifying tools in the SuperMetabase MCP server project.

## Project Overview

SuperMetabase is an MCP (Model Context Protocol) server that integrates Claude with Metabase, allowing Claude to interact with Metabase resources. The server follows the Model Context Protocol specification to expose Metabase functionality as tools that Claude can use.

### Key Components

1. **Authentication**: Session-based authentication with Metabase, with automatic re-authentication
2. **Tools**: Functions that map to Metabase API endpoints for resource operations
3. **Configuration**: Environment variable-based configuration with .env file support
4. **Response Handling**: Includes size limits to prevent oversized responses

## Project Structure

```
SuperMetabase/
├── supermetabase/              # Main package
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
1. User query → Claude → MCP client → SuperMetabase MCP server
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
        data = await client.some_method()
        
        # Convert data to JSON string
        response = json.dumps(data, indent=2)
        
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
            request_info={"endpoint": "/api/endpoint", "method": "METHOD"}
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
    
    with patch("supermetabase.tools.your_module.get_metabase_client", return_value=client_mock):
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

For API endpoints that may return large sets of data, implement pagination to ensure manageable response sizes:

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
        # Make API request
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

## Metabase API Endpoints

The following table shows the Metabase API endpoints that correspond to existing and planned tools, with an indicator of implementation status:

| Category | API Endpoint | Tool Name | Status |
|----------|-------------|-----------|--------|
| **Dashboard Operations** | `GET /api/dashboard/{id}` | `get_dashboard` | ✅ Implemented |
| | `POST /api/dashboard/` | `create_dashboard` | ✅ Implemented |
| | `PUT /api/dashboard/{id}` | `update_dashboard` | 📝 Planned |
| | `POST /api/dashboard/{dashboard-id}/cards` | `add_card_to_dashboard` | 📝 Planned |
| | `DELETE /api/dashboard/{id}` | `delete_dashboard` | 📝 Planned |
| **Card Operations** | `GET /api/card/{id}` | `get_card` | ✅ Implemented |
| | `POST /api/card/` | `create_card` | 📝 Planned |
| | `PUT /api/card/{id}` | `update_card` | 📝 Planned |
| | `POST /api/card/{card-id}/query` | `execute_card_query` | 📝 Planned |
| | `DELETE /api/card/{id}` | `delete_card` | 📝 Planned |
| **Collection Operations** | `GET /api/collection/` | `list_collections` | ✅ Implemented |
| | `GET /api/collection/{id}` | `get_collection` | 📝 Planned |
| | `POST /api/collection/` | `create_collection` | 📝 Planned |
| | `PUT /api/collection/{id}` | `update_collection` | 📝 Planned |
| | `GET /api/collection/{id}/items` | `get_collection_items` | 📝 Planned |
| **Database Operations** | `GET /api/database/` | `list_databases` | ✅ Implemented |
| | `GET /api/database/{id}/metadata` | `get_database_metadata` | 📝 Planned |
| | `GET /api/table/{id}` | `get_table` | 📝 Planned |
| | `GET /api/table/{id}/query_metadata` | `get_table_query_metadata` | 📝 Planned |
| **Query Operations** | `POST /api/dataset/` | `run_dataset_query` | 📝 Planned |
| **Search Operations** | `GET /api/search/` | `search_resources` | ✅ Implemented with pagination |

Implementation Legend:
- ✅ Implemented: Tool is fully implemented and available in the current version
- 📝 Planned: Tool is defined in specifications but not yet implemented

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

## Configuration Options

SuperMetabase is configured through environment variables, which can be set in a `.env` file or in the Claude Desktop configuration:

| Parameter | Description | Default |
|-----------|-------------|---------|
| METABASE_URL | Base URL of the Metabase instance | (Required) |
| METABASE_USERNAME | Username for authentication | (Required) |
| METABASE_PASSWORD | Password for authentication | (Required) |
| RESPONSE_SIZE_LIMIT | Maximum size (characters) for responses | 100000 |
| MCP_TRANSPORT | Transport method (stdio, sse, streamable-http) | stdio |
| LOG_LEVEL | Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL) | INFO |

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

### Testing with Claude Desktop

To test with Claude Desktop:

1. Update your Claude Desktop configuration to include the SuperMetabase server
2. Start a conversation with Claude
3. Ask questions that would trigger your new tool
4. Check the server logs for any issues

For paginated results, test navigation between pages by incrementing the page parameter.

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
- Adjust the `RESPONSE_SIZE_LIMIT` value if larger responses are required

### Parameter Parsing Issues

If string-formatted parameters (like JSON arrays or objects) aren't being parsed correctly:
- Add explicit parsing for string representation of complex types
- Include proper error handling for parsing failures
- Log the original parameter value and type for debugging

## Performance Considerations

### Authentication Caching

The server caches the authentication token to reduce API calls. The token is refreshed automatically if it expires.

### Response Size Limitations

Large responses are checked against the configured size limit to prevent overwhelming Claude or the client application. Use pagination to manage large result sets.

### Rate Limiting

Be aware of Metabase's rate limiting. If you implement tools that make many API calls, consider adding rate limiting or debouncing logic.

### Pagination Efficiency

For very large result sets, consider implementing:
- Client-side pagination (implemented in the search tool)
- Server-side pagination if the API supports it
- Cursor-based pagination for efficient scrolling through results

## Next Steps for Development

The current implementation includes functionality for retrieving and searching Metabase resources. Future development should focus on:

1. Implementing the remaining tools defined in the specifications
2. Adding integration tests with a real Metabase instance
3. Implementing caching for frequently accessed resources
4. Adding more sophisticated error handling
5. Implementing advanced query capabilities
6. Adding server-side pagination where applicable
7. Enhancing parameter parsing for complex types

## Conclusion

By following these guidelines, you can effectively extend and improve the SuperMetabase MCP server. Remember to maintain consistency with the existing code patterns and to thoroughly test your implementations.

Happy coding!
