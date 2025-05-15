"""
Search operations MCP tools.
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
logger.info("Registering search tools with the server...")


@mcp.tool(name="search_resources", description="Search for resources across Metabase")
async def search_resources(
    q: str, 
    ctx: Context,
    models: Optional[List[str]] = None, 
    archived: bool = False
) -> str:
    """
    Search for resources across Metabase.
    
    Args:
        q: Search term
        ctx: MCP context
        models: Types of resources to search for (card, dashboard, etc.)
        archived: Include archived resources (default: False)
        
    Returns:
        Search results as JSON string
    """
    client = get_metabase_client(ctx)
    
    try:
        results = await client.search(q, models, archived)
        # Convert data to JSON string
        response = json.dumps(results, indent=2)
        
        # Check response size before returning
        metabase_ctx = ctx.request_context.lifespan_context
        config = metabase_ctx.auth.config
        return check_response_size(response, config)
    except Exception as e:
        logger.error(f"Error searching resources: {e}")
        
        params = {"q": q}
        if models:
            params["models"] = models
        if archived:
            params["archived"] = "true"
            
        return format_error_response(
            status_code=500,
            error_type="search_error",
            message=str(e),
            request_info={"endpoint": "/api/search", "method": "GET", "params": params}
        )
