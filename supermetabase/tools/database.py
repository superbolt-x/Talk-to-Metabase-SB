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


@mcp.tool(name="list_databases", description="List all available databases")
async def list_databases(ctx: Context, include_tables: bool = False) -> str:
    """
    List all available databases.
    
    Args:
        ctx: MCP context
        include_tables: Include tables in the response (default: False)
        
    Returns:
        List of databases as JSON string
    """
    client = get_metabase_client(ctx)
    
    params = {}
    if include_tables:
        params["include_tables"] = "true"
    
    try:
        data, status, error = await client.auth.make_request(
            "GET", "database", params=params
        )
        
        if error:
            return format_error_response(
                status_code=status,
                error_type="retrieval_error",
                message=error,
                request_info={"endpoint": "/api/database", "method": "GET", "params": params}
            )
        
        # Convert data to JSON string
        response = json.dumps(data, indent=2)
        
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
            request_info={"endpoint": "/api/database", "method": "GET", "params": params}
        )


# Additional placeholder tools will be implemented later
