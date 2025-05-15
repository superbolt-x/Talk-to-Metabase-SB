"""
Card (Question) operations MCP tools.
"""

import json
import logging
from typing import Dict, Optional

from mcp.server.fastmcp import Context, FastMCP

from ..server import get_server_instance
from .common import format_error_response, get_metabase_client, check_response_size

# Set up logging for this module
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
# Register tools with the server
mcp = get_server_instance()
logger.info("Registering get_card tool with the server...")


@mcp.tool(name="get_card", description="Retrieve a card (question) by ID")
async def get_card(id: int, ctx: Context, ignore_view: Optional[bool] = None, context: Optional[str] = None) -> str:
    """
    Retrieve a card (question) by ID.
    
    Args:
        id: Card ID (required, must be a positive integer)
        ctx: MCP context
        ignore_view: Optional flag to ignore view
        context: Optional context parameter (allowed value: "collection")
        
    Returns:
        Card data as JSON string
    """
    logger.info(f"Tool called: get_card(id={id}, ignore_view={ignore_view}, context={context})")
    
    # Log the context information
    logger.info(f"Context type: {type(ctx)}")
    try:
        metabase_ctx = ctx.request_context.lifespan_context
        logger.info(f"Metabase context found: {metabase_ctx}")
    except Exception as e:
        logger.error(f"Error accessing context: {e}")
    
    client = get_metabase_client(ctx)
    
    # Build query parameters
    params = {}
    if ignore_view is not None:
        params["ignore_view"] = str(ignore_view).lower()
    if context is not None:
        # Validate context parameter
        if context != "collection":
            return format_error_response(
                status_code=400,
                error_type="validation_error",
                message=f"Invalid context parameter: {context}. Allowed values: 'collection'",
                request_info={"endpoint": f"/api/card/{id}", "method": "GET"}
            )
        params["context"] = context
    
    try:
        # Use make_request directly to include query parameters
        data, status, error = await client.auth.make_request(
            "GET", f"card/{id}", params=params
        )
        
        if error:
            return format_error_response(
                status_code=status,
                error_type="retrieval_error",
                message=error,
                request_info={
                    "endpoint": f"/api/card/{id}", 
                    "method": "GET",
                    "params": params
                }
            )
        
        # Convert data to JSON string
        response = json.dumps(data, indent=2)
        
        # Check response size before returning
        metabase_ctx = ctx.request_context.lifespan_context
        config = metabase_ctx.auth.config
        return check_response_size(response, config)
    except Exception as e:
        logger.error(f"Error getting card {id}: {e}")
        return format_error_response(
            status_code=500,
            error_type="retrieval_error",
            message=str(e),
            request_info={
                "endpoint": f"/api/card/{id}", 
                "method": "GET",
                "params": params
            }
        )


# Additional placeholder tools will be implemented later
