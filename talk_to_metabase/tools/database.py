"""
Database & Table operations MCP tools.
"""

import json
import logging
from typing import Dict, List, Optional

from mcp.server.fastmcp import Context, FastMCP

from ..server import get_server_instance
from .common import format_error_response, get_metabase_client, check_response_size, check_guidelines_enforcement

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Register tools with the server
mcp = get_server_instance()
logger.info("Registering database tools with the server...")


@mcp.tool(name="list_databases", description="List all available databases with essential information only")
async def list_databases(ctx: Context) -> str:
    """
    List all available databases with essential information only.
    
    Args:
        ctx: MCP context
        
    Returns:
        Simplified list of databases as JSON string with id, name, and engine only
    """
    logger.info("Tool called: list_databases()")
    
    # Check guidelines enforcement first
    guidelines_error = check_guidelines_enforcement(ctx)
    if guidelines_error:
        return guidelines_error
        
    client = get_metabase_client(ctx)
    
    try:
        data, status, error = await client.auth.make_request(
            "GET", "database"
        )
        
        if error:
            return format_error_response(
                status_code=status,
                error_type="retrieval_error",
                message=error,
                request_info={"endpoint": "/api/database", "method": "GET"}
            )
        
        # Extract only essential information
        if isinstance(data, dict) and "data" in data:
            databases = data["data"]
        elif isinstance(data, list):
            databases = data
        else:
            logger.error(f"Unexpected data format: {type(data)}")
            return format_error_response(
                status_code=500,
                error_type="unexpected_format",
                message="Unexpected response format from Metabase API",
                request_info={"endpoint": "/api/database", "method": "GET"}
            )
        
        # Create simplified database entries
        simplified_databases = []
        for db in databases:
            simplified_db = {
                "id": db.get("id"),
                "name": db.get("name"),
                "engine": db.get("engine")
            }
            simplified_databases.append(simplified_db)
        
        # Create final response
        response_data = {
            "databases": simplified_databases
        }
        
        # Convert to JSON string
        response = json.dumps(response_data, indent=2)
        
        # Check response size before returning
        metabase_ctx = ctx.request_context.lifespan_context
        config = metabase_ctx.auth.config
        return check_response_size(response, config)
    except Exception as e:
        logger.error(f"Error listing databases: {e}")
        return format_error_response(
            status_code=500,
            error_type="retrieval_error",
            message=str(e),
            request_info={"endpoint": "/api/database", "method": "GET"}
        )


@mcp.tool(name="get_database_metadata", description="Retrieve essential metadata about a database, including its tables and schemas")
async def get_database_metadata(id: int, ctx: Context) -> str:
    """
    Retrieve essential metadata about a database, including its tables and schemas.
    
    Args:
        id: Database ID
        ctx: MCP context
        
    Returns:
        Simplified database metadata as JSON string, including tables organized by schema
    """
    logger.info(f"Tool called: get_database_metadata({id})")
    
    # Check guidelines enforcement first
    guidelines_error = check_guidelines_enforcement(ctx)
    if guidelines_error:
        return guidelines_error
        
    client = get_metabase_client(ctx)
    
    try:
        # Always use skip_fields=true to avoid fetching all field metadata which can be huge
        data, status, error = await client.auth.make_request(
            "GET", f"database/{id}/metadata", params={"skip_fields": "true"}
        )
        
        if error:
            return format_error_response(
                status_code=status,
                error_type="retrieval_error",
                message=error,
                request_info={"endpoint": f"/api/database/{id}/metadata", "method": "GET"}
            )
        
        # Create a simplified response with only essential information
        # Extract database basic info
        simplified_db = {
            "id": data.get("id"),
            "name": data.get("name"),
            "engine": data.get("engine"),
            "timezone": data.get("timezone")
        }
        
        # Extract table information, organized by schema
        tables_by_schema = {}
        for table in data.get("tables", []):
            schema_name = table.get("schema", "")
            
            # Create a simplified table entry without redundant schema field
            table_entry = {
                "id": table.get("id"),
                "name": table.get("name"),
                "entity_type": table.get("entity_type")
            }
            
            # Add to the appropriate schema group
            if schema_name not in tables_by_schema:
                tables_by_schema[schema_name] = []
            
            tables_by_schema[schema_name].append(table_entry)
        
        # Create final response structure
        response_data = {
            "database": simplified_db,
            "schemas": [{
                "name": schema_name,
                "tables": tables
            } for schema_name, tables in tables_by_schema.items()]
        }
        
        # Add table count summary
        response_data["table_count"] = sum(len(tables) for tables in tables_by_schema.values())
        response_data["schema_count"] = len(tables_by_schema)
        
        # Convert to JSON string
        response = json.dumps(response_data, indent=2)
        
        # Check response size before returning
        metabase_ctx = ctx.request_context.lifespan_context
        config = metabase_ctx.auth.config
        return check_response_size(response, config)
    except Exception as e:
        logger.error(f"Error getting database metadata: {e}")
        return format_error_response(
            status_code=500,
            error_type="retrieval_error",
            message=str(e),
            request_info={"endpoint": f"/api/database/{id}/metadata", "method": "GET"}
        )


@mcp.tool(name="get_table_query_metadata", description="Get metadata about a table useful for running queries, with essential field information only")
async def get_table_query_metadata(
    id: int,
    ctx: Context,
    include_sensitive_fields: bool = False,
    include_hidden_fields: bool = False,
    include_editable_data_model: bool = False
) -> str:
    """
    Get metadata about a table useful for running queries, with essential field information only.
    
    Args:
        id: Table ID
        ctx: MCP context
        include_sensitive_fields: Include sensitive fields in response (default: False)
        include_hidden_fields: Include hidden fields in response (default: False)
        include_editable_data_model: Check write permissions instead of read permissions (default: False)
        
    Returns:
        Table query metadata as JSON string with essential field information for query building
    """
    logger.info(f"Tool called: get_table_query_metadata(id={id}, include_sensitive_fields={include_sensitive_fields}, include_hidden_fields={include_hidden_fields}, include_editable_data_model={include_editable_data_model})")
    
    # Check guidelines enforcement first
    guidelines_error = check_guidelines_enforcement(ctx)
    if guidelines_error:
        return guidelines_error
        
    client = get_metabase_client(ctx)
    
    try:
        # Build query parameters
        params = {}
        if include_sensitive_fields:
            params["include_sensitive_fields"] = "true"
        if include_hidden_fields:
            params["include_hidden_fields"] = "true"
        if include_editable_data_model:
            params["include_editable_data_model"] = "true"
        
        data, status, error = await client.auth.make_request(
            "GET", f"table/{id}/query_metadata", params=params
        )
        
        if error:
            return format_error_response(
                status_code=status,
                error_type="retrieval_error",
                message=error,
                request_info={"endpoint": f"/api/table/{id}/query_metadata", "method": "GET", "params": params}
            )
        
        # Extract essential table information
        table_info = {
            "id": data.get("id"),
            "name": data.get("name"),
            "schema": data.get("schema"),
            "entity_type": data.get("entity_type"),
            "description": data.get("description"),
            "view_count": data.get("view_count")
        }
        
        # Extract essential database information
        db_data = data.get("db", {})
        database_info = {
            "id": db_data.get("id"),
            "name": db_data.get("name"),
            "engine": db_data.get("engine"),
            "timezone": db_data.get("timezone")
        }
        
        # Process fields with essential information only
        fields = []
        primary_key_fields = []
        date_fields = []
        
        for field in data.get("fields", []):
            # Extract ONLY essential field information
            field_info = {
                "id": field.get("id"),
                "name": field.get("name"),
                "display_name": field.get("display_name"),
                "base_type": field.get("base_type"),
                "effective_type": field.get("effective_type"),
                "semantic_type": field.get("semantic_type"),
                "database_type": field.get("database_type"),
                "active": field.get("active"),
                "visibility_type": field.get("visibility_type"),
                "has_field_values": field.get("has_field_values"),
                "position": field.get("position")
            }
            
            fields.append(field_info)
            
            # Categorize special field types for summary
            semantic_type = field.get("semantic_type")
            base_type = field.get("base_type")
            
            if semantic_type == "type/PK":
                primary_key_fields.append(field.get("name"))
            
            if base_type in ["type/Date", "type/DateTime", "type/DateTimeWithLocalTZ", "type/Time"]:
                date_fields.append(field.get("name"))
        
        # Sort fields by position for consistent ordering
        fields.sort(key=lambda f: f.get("position", 0))
        
        # Create final response structure
        response_data = {
            "table": table_info,
            "database": database_info,
            "fields": fields,
            "field_count": len(fields),
            "primary_key_fields": primary_key_fields,
            "date_fields": date_fields
        }
        
        # Convert to JSON string
        response = json.dumps(response_data, indent=2)
        
        # Check response size before returning
        metabase_ctx = ctx.request_context.lifespan_context
        config = metabase_ctx.auth.config
        return check_response_size(response, config)
    except Exception as e:
        logger.error(f"Error getting table query metadata: {e}")
        return format_error_response(
            status_code=500,
            error_type="retrieval_error",
            message=str(e),
            request_info={"endpoint": f"/api/table/{id}/query_metadata", "method": "GET"}
        )


# Additional database tools can be implemented here
# Future tools might include:
# - get_table (basic table info without query metadata)
# - run_native_query
# - get_field_values
