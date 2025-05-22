"""
Database & Table operations MCP tools.
"""

import json
import logging
from typing import Dict, List, Optional

from mcp.server.fastmcp import Context, FastMCP

from ..server import get_server_instance
from .common import format_error_response, get_metabase_client, check_response_size

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


# Additional database tools will be implemented later
# Potential future tools:
# - get_table
# - get_table_query_metadata
