"""
Collection management MCP tools.
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
logger.info("Registering collection tools with the server...")


@mcp.tool(name="list_collections", description="List all collections")
async def list_collections(
    ctx: Context,
    namespace: Optional[str] = None, 
    archived: bool = False
) -> str:
    """
    List all collections.
    
    Args:
        ctx: MCP context
        namespace: Collection namespace (optional)
        archived: Include archived collections (default: False)
        
    Returns:
        List of collections as JSON string
    """
    client = get_metabase_client(ctx)
    
    params = {}
    if namespace:
        params["namespace"] = namespace
    
    if archived:
        params["archived"] = "true"
    
    try:
        data, status, error = await client.auth.make_request(
            "GET", "collection", params=params
        )
        
        if error:
            return format_error_response(
                status_code=status,
                error_type="retrieval_error",
                message=error,
                request_info={"endpoint": "/api/collection", "method": "GET", "params": params}
            )
        
        # Convert data to JSON string
        response = json.dumps(data, indent=2)
        
        # Check response size before returning
        metabase_ctx = ctx.request_context.lifespan_context
        config = metabase_ctx.auth.config
        return check_response_size(response, config)
    except Exception as e:
        logger.error(f"Error listing collections: {e}")
        return format_error_response(
            status_code=500,
            error_type="retrieval_error",
            message=str(e),
            request_info={"endpoint": "/api/collection", "method": "GET", "params": params}
        )


# Additional placeholder tools will be implemented later
