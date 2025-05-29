"""
Card (Question) operations MCP tools.
"""

import json
import logging
from typing import Dict, Optional, Any, List, Union

from mcp.server.fastmcp import Context, FastMCP

from ..server import get_server_instance
from .common import format_error_response, get_metabase_client, check_response_size, check_guidelines_enforcement

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


async def execute_sql_query(client, database_id: int, query: str) -> Dict[str, Any]:
    """
    Execute a SQL query to validate it before creating a card.
    
    Args:
        client: Metabase client
        database_id: Database ID
        query: SQL query string
    
    Returns:
        Dictionary with execution result (success/error info)
    """
    try:
        # Prepare the query payload
        query_data = {
            "database": database_id,
            "type": "native",
            "native": {
                "query": query,
                "template-tags": {}
            }
        }
        
        # Execute the query
        data, status, error = await client.auth.make_request(
            "POST", "dataset", json=query_data
        )
        
        if error:
            # Extract the essential error message
            error_message = error
            if data and isinstance(data, dict):
                if "error" in data:
                    error_message = data["error"]
                    
            return {
                "success": False,
                "error": error_message,
                "status_code": status
            }
        
        # Query executed successfully
        return {
            "success": True,
            "result_metadata": data.get("data", {}).get("cols", []),
            "row_count": data.get("row_count", 0)
        }
        
    except Exception as e:
        logger.error(f"Error executing SQL query: {e}")
        return {
            "success": False,
            "error": str(e),
            "status_code": 500
        }


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
    
    # Check guidelines enforcement first
    guidelines_error = check_guidelines_enforcement(ctx)
    if guidelines_error:
        return guidelines_error
    
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


@mcp.tool(name="create_card", description="Create a new SQL card after validating the query")
async def create_card(
    database_id: int,
    query: str,
    name: str,
    ctx: Context,
    card_type: str = "question",
    collection_id: Optional[int] = None,
    description: Optional[str] = None
) -> str:
    """
    Create a new SQL card after validating the query.
    
    Args:
        database_id: Database ID to run the query against
        query: SQL query string
        name: Name for the new card
        ctx: MCP context
        card_type: Type of card (question, model, or metric)
        collection_id: ID of the collection to place the card in (optional)
        description: Optional description for the card
        
    Returns:
        JSON string with creation result or error information
    """
    logger.info(f"Tool called: create_card(database_id={database_id}, name={name}, card_type={card_type})")
    
    # Check guidelines enforcement first
    guidelines_error = check_guidelines_enforcement(ctx)
    if guidelines_error:
        return guidelines_error
    # Validate card type
    valid_card_types = ["question", "model", "metric"]
    if card_type not in valid_card_types:
        return format_error_response(
            status_code=400,
            error_type="invalid_parameter",
            message=f"Invalid card type: {card_type}. Must be one of: {', '.join(valid_card_types)}",
            request_info={"database_id": database_id, "name": name}
        )
    
    client = get_metabase_client(ctx)
    
    # Step 1: Execute the query to validate it
    execution_result = await execute_sql_query(client, database_id, query)
    
    if not execution_result["success"]:
        # Return a concise error response if query validation fails
        return json.dumps({
            "success": False,
            "error": execution_result["error"]
        }, indent=2)
    
    # Step 2: Query is valid, create the card
    try:
        # Prepare the card creation payload
        card_data = {
            "name": name,
            "dataset_query": {
                "database": database_id,
                "native": {
                    "query": query,
                    "template-tags": {}
                },
                "type": "native"
            },
            "display": "table",  # Default display type
            "type": card_type,
            "visualization_settings": {}  # Required field, even if empty
        }
        
        # Add optional fields if provided
        if description:
            card_data["description"] = description
            
        if collection_id:
            card_data["collection_id"] = collection_id
        
        # If we have result metadata from the query execution, include it
        if "result_metadata" in execution_result:
            card_data["result_metadata"] = execution_result["result_metadata"]
        
        # Create the card
        data, status, error = await client.auth.make_request(
            "POST", "card", json=card_data
        )
        
        if error:
            return format_error_response(
                status_code=status,
                error_type="creation_error",
                message=error,
                request_info={
                    "endpoint": "/api/card",
                    "method": "POST"
                }
            )
        
        # Return a concise success response with essential info
        return json.dumps({
            "success": True,
            "card_id": data.get("id"),
            "name": data.get("name")
        }, indent=2)
        
    except Exception as e:
        logger.error(f"Error creating card: {e}")
        return format_error_response(
            status_code=500,
            error_type="creation_error",
            message=str(e),
            request_info={
                "endpoint": "/api/card",
                "method": "POST"
            }
        )


@mcp.tool(name="update_card", description="Update an existing card with a new SQL query")
async def update_card(
    id: int,
    ctx: Context,
    query: Optional[str] = None,
    name: Optional[str] = None,
    description: Optional[str] = None,
    collection_id: Optional[int] = None,
    archived: Optional[bool] = None
) -> str:
    """
    Update an existing card with a new SQL query or metadata.
    
    Args:
        id: Card ID to update (required, must be a positive integer)
        ctx: MCP context
        query: New SQL query string (optional)
        name: New name for the card (optional)
        description: New description for the card (optional)
        collection_id: New collection ID to move the card to (optional)
        archived: Whether the card is archived (optional)
        
    Returns:
        JSON string with update result or error information
    """
    logger.info(f"Tool called: update_card(id={id}, name={name})")
    
    # Check guidelines enforcement first
    guidelines_error = check_guidelines_enforcement(ctx)
    if guidelines_error:
        return guidelines_error
    
    client = get_metabase_client(ctx)
    
    try:
        # First, fetch the current card to ensure it exists
        current_data, status, error = await client.auth.make_request(
            "GET", f"card/{id}"
        )
        
        if error:
            return format_error_response(
                status_code=status,
                error_type="retrieval_error",
                message=f"Cannot update card {id}: {error}",
                request_info={
                    "endpoint": f"/api/card/{id}", 
                    "method": "GET"
                }
            )
        
        # Get the database ID from the existing card for SQL validation
        database_id = None
        if "dataset_query" in current_data and "database" in current_data["dataset_query"]:
            database_id = current_data["dataset_query"]["database"]
        
        # Prepare update payload with only the fields to be updated
        update_data = {}
        
        # Add fields that are provided
        if name is not None:
            update_data["name"] = name
        if description is not None:
            update_data["description"] = description
        if collection_id is not None:
            update_data["collection_id"] = collection_id
        if archived is not None:
            update_data["archived"] = archived
        
        # If query is provided, validate it and update the dataset_query
        if query is not None:
            if database_id is None:
                return format_error_response(
                    status_code=400,
                    error_type="validation_error",
                    message="Cannot update query: database_id not found in existing card",
                    request_info={
                        "endpoint": f"/api/card/{id}", 
                        "method": "PUT"
                    }
                )
            
            # Validate the SQL query
            execution_result = await execute_sql_query(client, database_id, query)
            
            if not execution_result["success"]:
                # Return a concise error response if query validation fails
                return json.dumps({
                    "success": False,
                    "error": execution_result["error"]
                }, indent=2)
            
            # Add the validated query to the update data
            update_data["dataset_query"] = {
                "type": "native",
                "database": database_id,
                "native": {
                    "query": query,
                    "template-tags": {}
                }
            }
            
            # If we have result metadata from the query execution, include it
            if "result_metadata" in execution_result:
                update_data["result_metadata"] = execution_result["result_metadata"]
        
        # If no fields were provided to update, return early
        if not update_data:
            return json.dumps({
                "success": False,
                "error": "No fields provided for update"
            }, indent=2)
        
        # Perform the update
        data, status, error = await client.auth.make_request(
            "PUT", f"card/{id}", json=update_data
        )
        
        if error:
            return format_error_response(
                status_code=status,
                error_type="update_error",
                message=error,
                request_info={
                    "endpoint": f"/api/card/{id}", 
                    "method": "PUT"
                }
            )
        
        # Return a concise success response with essential info
        return json.dumps({
            "success": True,
            "card_id": data.get("id"),
            "name": data.get("name")
        }, indent=2)
        
    except Exception as e:
        logger.error(f"Error updating card {id}: {e}")
        return format_error_response(
            status_code=500,
            error_type="update_error",
            message=str(e),
            request_info={
                "endpoint": f"/api/card/{id}", 
                "method": "PUT"
            }
        )
