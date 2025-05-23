"""
Card (Question) operations MCP tools.
"""

import json
import logging
from typing import Dict, Optional, Any, List

from mcp.server.fastmcp import Context, FastMCP

from ..server import get_server_instance
from .common import format_error_response, get_metabase_client, check_response_size

# Set up logging for this module
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
# Register tools with the server
mcp = get_server_instance()
logger.info("Registering card definition tools with the server...")


def extract_essential_card_info(card_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extract only essential information about a card's definition.
    Focuses on metadata and query definition, not results.
    
    Args:
        card_data: Raw card data from Metabase API
        
    Returns:
        Dictionary with essential card definition information
    """
    # Basic card metadata
    essential_info = {
        "id": card_data.get("id"),
        "name": card_data.get("name"),
        "description": card_data.get("description"),
        "type": card_data.get("type"),
        "display": card_data.get("display"), 
        "database_id": card_data.get("database_id"),
        "query_type": card_data.get("query_type"),
    }
    
    # Add collection information if available
    if "collection" in card_data and card_data["collection"]:
        essential_info["collection"] = {
            "id": card_data["collection"].get("id"),
            "name": card_data["collection"].get("name"),
            "location": card_data["collection"].get("location")
        }
    elif "collection_id" in card_data:
        essential_info["collection_id"] = card_data.get("collection_id")
    
    # Add creator information if available
    if "creator" in card_data and card_data["creator"]:
        essential_info["creator"] = {
            "id": card_data["creator"].get("id"),
            "name": card_data["creator"].get("common_name") or 
                   f"{card_data['creator'].get('first_name', '')} {card_data['creator'].get('last_name', '')}".strip()
        }
    
    # Add query information
    if "dataset_query" in card_data:
        dataset_query = card_data["dataset_query"]
        
        # For native queries, extract only the query and template tags
        if dataset_query.get("type") == "native":
            essential_info["dataset_query"] = {
                "type": "native",
                "database": dataset_query.get("database"),
                "native": {
                    "query": dataset_query.get("native", {}).get("query")
                }
            }
            
            # Add template tags if they exist
            if "template-tags" in dataset_query.get("native", {}):
                essential_info["dataset_query"]["native"]["template-tags"] = dataset_query["native"]["template-tags"]
        
        # For MBQL queries, keep the essential structure
        elif dataset_query.get("type") == "query":
            essential_info["dataset_query"] = {
                "type": "query",
                "database": dataset_query.get("database"),
                "query": dataset_query.get("query", {})
            }
    
    # Add simplified visualization settings
    if "visualization_settings" in card_data and card_data["visualization_settings"]:
        # Extract only the most important visualization settings
        vis_settings = card_data["visualization_settings"]
        essential_vis_settings = {}
        
        # Common visualization settings
        for key in ["graph.dimensions", "graph.metrics", "table.pivot_column", 
                    "table.cell_column", "graph.x_axis.scale", "stackable.stack_type"]:
            if key in vis_settings:
                essential_vis_settings[key] = vis_settings[key]
        
        # Series settings (colors, labels)
        if "series_settings" in vis_settings:
            essential_vis_settings["series_settings"] = vis_settings["series_settings"]
        
        essential_info["visualization_settings"] = essential_vis_settings
    
    # Add simplified parameters
    if "parameters" in card_data and card_data["parameters"]:
        simplified_parameters = []
        for param in card_data["parameters"]:
            simplified_param = {
                "id": param.get("id"),
                "name": param.get("name"),
                "type": param.get("type"),
                "slug": param.get("slug")
            }
            
            # Add target information if available
            if "target" in param:
                simplified_param["target"] = param["target"]
            
            # Add values source if available
            if "values_source_type" in param:
                simplified_param["values_source_type"] = param["values_source_type"]
                if "values_source_config" in param:
                    simplified_param["values_source_config"] = param["values_source_config"]
            
            simplified_parameters.append(simplified_param)
        
        essential_info["parameters"] = simplified_parameters
    
    # Add field metadata without excessive details
    if "result_metadata" in card_data and card_data["result_metadata"]:
        simplified_metadata = []
        for field in card_data["result_metadata"]:
            simplified_field = {
                "name": field.get("name"),
                "display_name": field.get("display_name"),
                "base_type": field.get("base_type"),
                "semantic_type": field.get("semantic_type")
            }
            simplified_metadata.append(simplified_field)
        
        essential_info["result_metadata"] = simplified_metadata
    
    # Add dashboard reference count if available (not the details)
    if "dashboard_count" in card_data and card_data["dashboard_count"] > 0:
        essential_info["dashboard_count"] = card_data["dashboard_count"]
    
    return essential_info


async def get_sql_translation(client, card_data: Dict[str, Any]) -> Optional[str]:
    """
    Get SQL translation for MBQL queries using the /api/dataset/native endpoint.
    
    Args:
        client: Metabase client
        card_data: Card data containing the MBQL query
        
    Returns:
        SQL translation as string, or None if translation failed
    """
    # Check if this is an MBQL query that needs translation
    dataset_query = card_data.get("dataset_query", {})
    if dataset_query.get("type") != "query":
        return None
    
    try:
        # Prepare the request payload
        translation_request = {
            "database": dataset_query.get("database"),
            "query": dataset_query.get("query", {}),
            "type": "query"
        }
        
        # Make the request to translate MBQL to SQL
        data, status, error = await client.auth.make_request(
            "POST", "dataset/native", json=translation_request
        )
        
        if error or not data:
            logger.warning(f"Failed to translate MBQL to SQL: {error}")
            return None
        
        # Return the SQL query string
        return data.get("query")
    
    except Exception as e:
        logger.error(f"Error translating MBQL to SQL: {e}")
        return None


@mcp.tool(name="get_card_definition", description="Retrieve a card's definition and metadata without results")
async def get_card_definition(id: int, ctx: Context, ignore_view: Optional[bool] = None, translate_mbql: bool = True) -> str:
    """
    Retrieve a card's definition and metadata without query results.
    For MBQL queries, optionally includes a translation to SQL.
    
    Args:
        id: Card ID (required, must be a positive integer)
        ctx: MCP context
        ignore_view: Optional flag to ignore view count increment
        translate_mbql: Whether to include SQL translation for MBQL queries (default: True)
        
    Returns:
        Card definition as JSON string with essential fields only
    """
    logger.info(f"Tool called: get_card_definition(id={id}, ignore_view={ignore_view}, translate_mbql={translate_mbql})")
    
    client = get_metabase_client(ctx)
    
    # Build query parameters
    params = {}
    if ignore_view is not None:
        params["ignore_view"] = str(ignore_view).lower()
    
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
        
        # Extract essential information
        essential_info = extract_essential_card_info(data)
        
        # If this is an MBQL query and translation is requested, get SQL translation
        if (data.get("query_type") == "query" or 
            (data.get("dataset_query", {}).get("type") == "query")) and translate_mbql:
            sql_translation = await get_sql_translation(client, data)
            if sql_translation:
                essential_info["sql_translation"] = sql_translation
        
        # Convert to JSON string
        response = json.dumps(essential_info, indent=2)
        
        # Check response size before returning
        metabase_ctx = ctx.request_context.lifespan_context
        config = metabase_ctx.auth.config
        return check_response_size(response, config)
    except Exception as e:
        logger.error(f"Error getting card definition {id}: {e}")
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