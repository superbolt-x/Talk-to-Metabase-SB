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


# Additional database tools will be implemented later
# Potential future tools:
# - get_database_metadata
# - get_table
# - get_table_query_metadata
