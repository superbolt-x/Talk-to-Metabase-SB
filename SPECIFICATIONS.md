# Metabase MCP Server Specifications

## Overview

This document outlines the specifications for a Model Context Protocol (MCP) server that integrates Claude with Metabase. This integration will allow Claude to interact with Metabase resources, providing users with AI-powered data analysis, visualization, and dashboard management capabilities.

## Core Requirements

1. **Resource Access**: Read and write access to all types of Metabase resources
2. **Search Capabilities**: Ability to search and discover resources across Metabase
3. **Ownership Attribution**: Proper attribution of resources created or modified through the MCP server
4. **Simple Configuration**: Minimal configuration focused on user credentials and Metabase URL

## Configuration

The configuration will be integrated directly into the Claude Desktop configuration file for simplicity:

```json
{
  "mcpServers": {
    "metabase": {
      "command": "path-to-metabase-mcp-server",
      "args": ["--config", "stdio"],
      "env": {
        "METABASE_URL": "https://your-metabase-instance.company.com",
        "METABASE_USERNAME": "user@example.com",
        "METABASE_PASSWORD": "your-password"
      }
    }
  }
}
```

### Configuration Parameters

| Parameter | Description | Required |
|-----------|-------------|----------|
| METABASE_URL | Base URL of your Metabase instance | Yes |
| METABASE_USERNAME | Username for authentication | Yes |
| METABASE_PASSWORD | Password for authentication | Yes |

## Authentication

The server will use session-based authentication with Metabase:

1. On startup, authenticate with provided credentials using `/api/session/` endpoint
2. Store session token for subsequent API calls
3. Handle session expiration and re-authentication as needed
4. Properly attribute created/modified resources to the authenticated user

## Tool Specifications

The MCP server will implement tools that map directly to Metabase API endpoints, following a one-to-one mapping approach for clarity and ease of debugging.

### Dashboard Operations

#### `get_dashboard`
- **API Endpoint**: `GET /api/dashboard/{id}`
- **Description**: Retrieve a dashboard by ID
- **Parameters**:
  - `id`: Integer (Dashboard ID)
- **Returns**: Dashboard object with its details and cards

#### `create_dashboard`
- **API Endpoint**: `POST /api/dashboard/`
- **Description**: Create a new dashboard
- **Parameters**:
  - `name`: String (required)
  - `description`: String (optional)
  - `collection_id`: Integer (optional)
  - `parameters`: Array (optional dashboard filters)
- **Returns**: Created dashboard object with ID

#### `update_dashboard`
- **API Endpoint**: `PUT /api/dashboard/{id}`
- **Description**: Update an existing dashboard
- **Parameters**:
  - `id`: Integer (required)
  - `name`: String (optional)
  - `description`: String (optional)
  - `parameters`: Array (optional dashboard filters)
  - `cards`: Array (optional dashboard cards layout)
- **Returns**: Updated dashboard object

#### `add_card_to_dashboard`
- **API Endpoint**: `POST /api/dashboard/{dashboard-id}/cards`
- **Description**: Add a card to a dashboard
- **Parameters**:
  - `dashboard_id`: Integer (required)
  - `card_id`: Integer (required)
  - `size_x`: Integer (width, required)
  - `size_y`: Integer (height, required)
  - `row`: Integer (position, required)
  - `col`: Integer (position, required)
- **Returns**: Created dashcard object

#### `delete_dashboard`
- **API Endpoint**: `DELETE /api/dashboard/{id}`
- **Description**: Delete a dashboard
- **Parameters**:
  - `id`: Integer (required)
- **Returns**: Success confirmation

### Card (Question) Operations

#### `get_card`
- **API Endpoint**: `GET /api/card/{id}`
- **Description**: Retrieve a card (question) by ID
- **Parameters**:
  - `id`: Integer (required)
- **Returns**: Card object with its details

#### `create_card`
- **API Endpoint**: `POST /api/card/`
- **Description**: Create a new card (question)
- **Parameters**:
  - `name`: String (required)
  - `dataset_query`: Object (query definition, required)
  - `display`: String (visualization type, required)
  - `visualization_settings`: Object (required)
  - `collection_id`: Integer (optional)
  - `description`: String (optional)
- **Returns**: Created card object with ID

#### `update_card`
- **API Endpoint**: `PUT /api/card/{id}`
- **Description**: Update an existing card
- **Parameters**:
  - `id`: Integer (required)
  - `name`: String (optional)
  - `dataset_query`: Object (optional)
  - `display`: String (optional)
  - `visualization_settings`: Object (optional)
  - `collection_id`: Integer (optional)
  - `description`: String (optional)
- **Returns**: Updated card object

#### `execute_card_query`
- **API Endpoint**: `POST /api/card/{card-id}/query`
- **Description**: Run a card's query and get results
- **Parameters**:
  - `card_id`: Integer (required)
  - `parameters`: Object (optional query parameters)
- **Returns**: Query results

#### `delete_card`
- **API Endpoint**: `DELETE /api/card/{id}`
- **Description**: Delete a card
- **Parameters**:
  - `id`: Integer (required)
- **Returns**: Success confirmation

### Collection Management

#### `list_collections`
- **API Endpoint**: `GET /api/collection/`
- **Description**: List all collections
- **Parameters**:
  - `namespace`: String (optional)
  - `archived`: Boolean (optional)
- **Returns**: Array of collection objects

#### `get_collection`
- **API Endpoint**: `GET /api/collection/{id}`
- **Description**: Get a specific collection by ID
- **Parameters**:
  - `id`: Integer (required)
- **Returns**: Collection object

#### `create_collection`
- **API Endpoint**: `POST /api/collection/`
- **Description**: Create a new collection
- **Parameters**:
  - `name`: String (required)
  - `description`: String (optional)
  - `parent_id`: Integer (optional)
- **Returns**: Created collection object

#### `update_collection`
- **API Endpoint**: `PUT /api/collection/{id}`
- **Description**: Update collection properties such as name, description, or parent collection
- **Parameters**:
  - `id`: Integer (required)
  - `name`: String (optional)
  - `description`: String (optional)
  - `parent_id`: Integer (optional)
- **Returns**: Updated collection object

#### `get_collection_items`
- **API Endpoint**: `GET /api/collection/{id}/items`
- **Description**: Get items in a collection
- **Parameters**:
  - `id`: Integer (required)
  - `models`: Array (optional, types of items to include)
- **Returns**: Array of items in the collection

### Database & Table Operations

#### `list_databases`
- **API Endpoint**: `GET /api/database/`
- **Description**: List all available databases
- **Parameters**:
  - `include_tables`: Boolean (optional)
- **Returns**: Array of database objects

#### `get_database_metadata`
- **API Endpoint**: `GET /api/database/{id}/metadata`
- **Description**: Get metadata about a database
- **Parameters**:
  - `id`: Integer (required)
- **Returns**: Database metadata including tables

#### `get_table`
- **API Endpoint**: `GET /api/table/{id}`
- **Description**: Get a table by ID
- **Parameters**:
  - `id`: Integer (required)
- **Returns**: Table object

#### `get_table_query_metadata`
- **API Endpoint**: `GET /api/table/{id}/query_metadata`
- **Description**: Get detailed query metadata for a table, including fields, foreign keys, and field fingerprints
- **Parameters**:
  - `id`: Integer (required)
- **Returns**: Comprehensive table metadata useful for constructing queries

### Search Operations

#### `search_resources`
- **API Endpoint**: `GET /api/search/`
- **Description**: Search for resources across Metabase
- **Parameters**:
  - `q`: String (search term, required)
  - `models`: Array (optional, types to search)
  - `archived`: Boolean (optional)
- **Returns**: Array of matching resources with IDs and metadata

### Dataset Query Operations

#### `run_dataset_query`
- **API Endpoint**: `POST /api/dataset/`
- **Description**: Execute an ad-hoc query against a database
- **Parameters**:
  - `database`: Integer (database ID, required)
  - `native`: Object (native query with SQL, required for native queries)
  - `query`: Object (MBQL query definition, required for structured queries)
  - `type`: String ("query" or "native", default: "native")
- **Returns**: Query results with essential fields including:
  - `data.rows`: Array of result rows
  - `data.cols`: Column metadata
  - `data.native_form`: Original query
  - `status`: Query execution status
  - `error`: Error message if query failed
  - `error_type`: Type of error if query failed
  - `database_id`: Database ID
  - `started_at`: Query start timestamp
  - `running_time`: Query execution time in ms
  - `row_count`: Number of rows returned
  - `results_timezone`: Timezone used for results

## Resource Identification Strategy

All operations will use resource IDs rather than names for identification to ensure:
1. Uniqueness (avoiding ambiguity from duplicate names)
2. Stability (names can change, IDs don't)
3. Consistency with Metabase's API
4. Error reduction

When Claude needs to find resources by name, it will:
1. Use the search tool to find resources
2. Extract IDs from search results
3. Use IDs for subsequent operations

## Error Handling

Errors will be communicated to Claude in a structured format optimized for AI understanding:

```json
{
  "success": false,
  "error": {
    "status_code": 403,
    "error_type": "permissions",
    "message": "You don't have permissions to do this.",
    "metabase_error": {
      "status": "failed",
      "error_code": "permissions-error",
      "error_details": { ... }
    },
    "request_info": {
      "endpoint": "/api/card/123",
      "method": "PUT",
      "params": { ... }
    },
    "raw_response": "..."
  }
}
```

This approach provides:
1. Detailed technical information (not simplified for humans)
2. Context about the operation being attempted
3. Structured format for easier debugging
4. Complete raw error data from Metabase

## Implementation Guidelines

### Authentication Flow

1. On server startup:
   - Read environment variables for Metabase URL and credentials
   - Authenticate with Metabase using `/api/session/` endpoint
   - Store session token for subsequent requests
   - Handle authentication errors appropriately

2. For each API request:
   - Include authentication in headers
   - Handle 401 errors by re-authenticating
   - Properly attribute ownership of created/modified resources

### Tool Implementation

Each tool should:
1. Map directly to a single Metabase API endpoint
2. Validate required parameters before making API calls
3. Convert parameter formats if needed to match Metabase's expectations
4. Return structured responses that Claude can easily parse
5. Include comprehensive error information when operations fail

### Security Considerations

1. Credentials are stored in the Claude Desktop config file
2. Server operates with the permissions of the configured user
3. All operations respect Metabase's permission system
4. Sensitive information is not exposed in error messages

## Conclusion

This MCP server will enable Claude to interact with Metabase through a well-defined set of tools that map directly to Metabase's API endpoints. By using resource IDs and providing detailed error information, the server will allow Claude to effectively navigate, analyze, and modify Metabase resources while properly attributing actions to the configured user.
