"""
Collection management MCP tools.
"""

import json
import logging
from typing import Dict, List, Optional, Any, Union

from mcp.server.fastmcp import Context, FastMCP

from ..server import get_server_instance
from .common import format_error_response, get_metabase_client, check_response_size

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Register tools with the server
mcp = get_server_instance()
logger.info("Registering collection tools with the server...")

@mcp.tool(name="explore_collection_tree", description="Navigate the collection hierarchy - shows subcollections and summary of all content")
async def explore_collection_tree(
    ctx: Context,
    collection_id: Optional[int] = None,  # None means root level
    archived: bool = False
) -> str:
    """
    Navigate the collection hierarchy by showing direct child collections and a summary of all content.
    
    Args:
        ctx: MCP context
        collection_id: Collection ID (None for root level collections)
        archived: Include archived items (default: False)
        
    Returns:
        Child collections and content summary as JSON string
    """
    client = get_metabase_client(ctx)
    
    # Build the endpoint path - different for root vs. specific collection
    endpoint = "collection/root/items" if collection_id is None else f"collection/{collection_id}/items"
    
    # Build parameters - get all item types to create comprehensive summary
    params = {
        "archived": str(archived).lower()
    }
    
    try:
        # Get all items in the collection
        api_response, status, error = await client.auth.make_request(
            "GET", endpoint, params=params
        )
        
        if error:
            return format_error_response(
                status_code=status,
                error_type="retrieval_error",
                message=error,
                request_info={"endpoint": f"/api/{endpoint}", "method": "GET", "params": params}
            )
        
        # Extract the actual data from the response
        items_data: List[Dict[str, Any]] = []
        
        if isinstance(api_response, dict) and "data" in api_response:
            # Format: {"total": X, "data": [...]}
            items_data = api_response.get("data", [])
        elif isinstance(api_response, list):
            # Direct list format
            items_data = api_response
        else:
            logger.warning(f"Unexpected API response format: {type(api_response)}")
            items_data = []
        
        # Separate collections from other items and filter out databases
        child_collections = []
        
        # Initialize comprehensive summary with all model types
        content_summary = {
            "dashboard": 0,
            "card": 0,
            "collection": 0,
            "dataset": 0,
            "timeline": 0,
            "snippet": 0,
            "pulse": 0,
            "metric": 0
        }
        
        for item in items_data:
            # Skip database items
            if item.get("model") == "database":
                continue
                
            model_type = item.get("model")
            
            # Count all items for summary
            if model_type in content_summary:
                content_summary[model_type] += 1
            
            # Collect collections for the main list
            if model_type == "collection":
                simplified_collection = {
                    "id": item.get("id"),
                    "name": item.get("name"),
                    "model": item.get("model")
                }
                
                # Include location if available
                location = item.get("location")
                if location:
                    simplified_collection["location"] = location
                    
                child_collections.append(simplified_collection)
        
        # Create response
        response_data = {
            "collection_id": collection_id,
            "child_collections": child_collections,
            "content_summary": content_summary
        }
        
        # Convert data to JSON string
        response = json.dumps(response_data, indent=2)
        
        # Check response size before returning
        metabase_ctx = ctx.request_context.lifespan_context
        config = metabase_ctx.auth.config
        return check_response_size(response, config)
    except Exception as e:
        logger.error(f"Error exploring collection tree: {e}")
        return format_error_response(
            status_code=500,
            error_type="retrieval_error",
            message=str(e),
            request_info={"endpoint": f"/api/{endpoint}", "method": "GET", "params": params}
        )


@mcp.tool(name="view_collection_contents", description="View all direct children items in a collection")
async def view_collection_contents(
    ctx: Context,
    collection_id: Optional[int] = None,  # None means root level
    models: Optional[List[str]] = None,  # Filter by specific model types
    archived: bool = False
) -> str:
    """
    View all direct children items in a collection.
    
    Args:
        ctx: MCP context
        collection_id: Collection ID (None for root level collections)
        models: Types of items to include. Valid values: dashboard, card, collection, dataset, 
               no_models, timeline, snippet, pulse, metric. If not specified, shows all types.
        archived: Include archived items (default: False)
        
    Returns:
        All collection items as JSON string with summary information
    """
    client = get_metabase_client(ctx)
    
    # Build the endpoint path - different for root vs. specific collection
    endpoint = "collection/root/items" if collection_id is None else f"collection/{collection_id}/items"
    
    # Build parameters
    params = {
        "archived": str(archived).lower()
    }
    
    if models:
        # Handle string input for models parameter (for convenience)
        if isinstance(models, str):
            try:
                models = json.loads(models)
            except json.JSONDecodeError:
                # If it's a single model name and not JSON
                if models.strip():
                    models = [models.strip()]
                else:
                    models = None
        
        if models:
            params["models"] = models
    
    try:
        # Get the items in the collection
        api_response, status, error = await client.auth.make_request(
            "GET", endpoint, params=params
        )
        
        if error:
            return format_error_response(
                status_code=status,
                error_type="retrieval_error",
                message=error,
                request_info={"endpoint": f"/api/{endpoint}", "method": "GET", "params": params}
            )
        
        # Extract the actual data from the response
        items_data: List[Dict[str, Any]] = []
        
        if isinstance(api_response, dict) and "data" in api_response:
            # Format: {"total": X, "data": [...]}
            items_data = api_response.get("data", [])
        elif isinstance(api_response, list):
            # Direct list format
            items_data = api_response
        else:
            logger.warning(f"Unexpected API response format: {type(api_response)}")
            items_data = []
        
        # Filter out database items and simplify each item
        simplified_items = []
        
        # Initialize comprehensive summary with all model types
        content_summary = {
            "dashboard": 0,
            "card": 0,
            "collection": 0,
            "dataset": 0,
            "timeline": 0,
            "snippet": 0,
            "pulse": 0,
            "metric": 0
        }
        
        for item in items_data:
            # Skip database items
            if item.get("model") == "database":
                continue
                
            # Create a simplified item with only essential fields
            simplified_item = {
                "id": item.get("id"),
                "name": item.get("name"),
                "model": item.get("model")
            }
            
            # Include location if available
            location = item.get("location")
            if location:
                simplified_item["location"] = location

            model_type = item.get("model")
            
            if not models or model_type in models:
                simplified_items.append(simplified_item)
            
            # Count for summary
            if model_type in content_summary:
                content_summary[model_type] += 1
        
        # Create response
        response_data = {
            "collection_id": collection_id,
            "items": simplified_items,
            "content_summary": content_summary
        }
        
        # Convert data to JSON string
        response = json.dumps(response_data, indent=2)
        
        # Check response size before returning
        metabase_ctx = ctx.request_context.lifespan_context
        config = metabase_ctx.auth.config
        return check_response_size(response, config)
    except Exception as e:
        logger.error(f"Error viewing collection contents: {e}")
        return format_error_response(
            status_code=500,
            error_type="retrieval_error",
            message=str(e),
            request_info={"endpoint": f"/api/{endpoint}", "method": "GET", "params": params}
        )


@mcp.tool(name="create_collection", description="Create a new collection")
async def create_collection(
    name: str,
    ctx: Context,
    description: Optional[str] = None,
    parent_id: Optional[int] = None
) -> str:
    """
    Create a new collection.
    
    Args:
        name: Collection name
        ctx: MCP context
        description: Collection description (optional)
        parent_id: Parent collection ID to place this collection under (optional)
        
    Returns:
        Created collection data as JSON string with essential information
    """
    logger.info(f"Tool called: create_collection(name={name}, description={description}, parent_id={parent_id})")
    client = get_metabase_client(ctx)
    
    # Build collection data
    collection_data = {
        "name": name
    }
    
    if description:
        collection_data["description"] = description
    
    if parent_id:
        collection_data["parent_id"] = parent_id
    
    try:
        data = await client.create_resource("collection", collection_data)
        
        # Return a concise success response with essential info
        response = {
            "success": True,
            "collection_id": data.get("id"),
            "name": data.get("name")
        }
        
        response_json = json.dumps(response, indent=2)
        
        # Check response size before returning
        metabase_ctx = ctx.request_context.lifespan_context
        config = metabase_ctx.auth.config
        return check_response_size(response_json, config)
    except Exception as e:
        logger.error(f"Error creating collection: {e}")
        return format_error_response(
            status_code=500,
            error_type="creation_error",
            message=str(e),
            request_info={
                "endpoint": "/api/collection",
                "method": "POST",
                "params": collection_data
            }
        )
