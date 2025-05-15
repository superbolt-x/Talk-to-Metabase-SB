"""
Dashboard operations MCP tools.
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
logger.info("Registering dashboard tools with the server...")


@mcp.tool(name="get_dashboard", description="Retrieve a dashboard by ID")
async def get_dashboard(id: int, ctx: Context) -> str:
    """
    Retrieve a dashboard by ID.
    
    Args:
        id: Dashboard ID
        ctx: MCP context
        
    Returns:
        Dashboard data as JSON string
    """
    client = get_metabase_client(ctx)
    
    try:
        data = await client.get_resource("dashboard", id)
        # Convert data to JSON string
        response = json.dumps(data, indent=2)
        
        # Check response size before returning
        metabase_ctx = ctx.request_context.lifespan_context
        config = metabase_ctx.auth.config
        return check_response_size(response, config)
    except Exception as e:
        logger.error(f"Error getting dashboard {id}: {e}")
        return format_error_response(
            status_code=500,
            error_type="retrieval_error",
            message=str(e),
            request_info={"endpoint": f"/api/dashboard/{id}", "method": "GET"}
        )


@mcp.tool(name="create_dashboard", description="Create a new dashboard")
async def create_dashboard(
    name: str, 
    ctx: Context,
    description: Optional[str] = None, 
    collection_id: Optional[int] = None
) -> str:
    """
    Create a new dashboard.
    
    Args:
        name: Dashboard name
        ctx: MCP context
        description: Dashboard description (optional)
        collection_id: Collection ID to place the dashboard in (optional)
        
    Returns:
        Created dashboard data as JSON string
    """
    client = get_metabase_client(ctx)
    
    # Build dashboard data
    dashboard_data = {
        "name": name,
    }
    
    if description:
        dashboard_data["description"] = description
    
    if collection_id:
        dashboard_data["collection_id"] = collection_id
    
    try:
        data = await client.create_resource("dashboard", dashboard_data)
        # Convert data to JSON string
        response = json.dumps(data, indent=2)
        
        # Check response size before returning
        metabase_ctx = ctx.request_context.lifespan_context
        config = metabase_ctx.auth.config
        return check_response_size(response, config)
    except Exception as e:
        logger.error(f"Error creating dashboard: {e}")
        return format_error_response(
            status_code=500,
            error_type="creation_error",
            message=str(e),
            request_info={
                "endpoint": "/api/dashboard", 
                "method": "POST",
                "params": dashboard_data
            }
        )


# Additional placeholder tools will be implemented later
