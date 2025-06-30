"""
Dashboard operations MCP tools.
"""

import json
import logging
import time
from typing import Dict, List, Optional, Any

from mcp.server.fastmcp import Context, FastMCP

from ..server import get_server_instance
from .common import format_error_response, get_metabase_client, check_response_size
from .dashcards import validate_dashcards_helper, validate_tabs_helper
from .dashboard_parameters import (
    process_dashboard_parameters,
    validate_dashboard_parameters_helper
)

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Register tools with the server
mcp = get_server_instance()
logger.info("Registering dashboard tools with the server...")


@mcp.tool(name="get_dashboard", description="Retrieve a dashboard by ID without card details")
async def get_dashboard(id: int, ctx: Context) -> str:
    """
    Retrieve a dashboard by ID without card details.
    
    Args:
        id: Dashboard ID
        ctx: MCP context
        
    Returns:
        Dashboard data as JSON string without card details
    """    
    client = get_metabase_client(ctx)
    
    try:
        data = await client.get_resource("dashboard", id)
        
        # Create a simplified dashboard object without cards
        simplified_data = {
            key: value for key, value in data.items() 
            if key != "dashcards"
        }
        
        # If there are tabs, keep tab information
        if "tabs" in data and isinstance(data["tabs"], list) and data["tabs"]:
            logger.info(f"Dashboard has {len(data['tabs'])} tabs")
            simplified_data["tabs"] = data["tabs"]
        else:
            # For non-tabbed dashboards, create an implicit default tab
            logger.info("Dashboard has no explicit tabs (single-tab dashboard)")
            simplified_data["is_single_tab"] = True
        
        # Return card count information rather than the cards themselves
        if "dashcards" in data and isinstance(data["dashcards"], list):
            simplified_data["dashcard_count"] = len(data["dashcards"])
            logger.info(f"Dashboard has {len(data['dashcards'])} cards")
        else:
            simplified_data["dashcard_count"] = 0
            logger.info("Dashboard has no cards")
            
        # Convert data to JSON string
        response = json.dumps(simplified_data, indent=2)
        
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


@mcp.tool(name="update_dashboard", description="Update a dashboard with new cards, tabs and enhanced parameters")
async def update_dashboard(
    id: int,
    ctx: Context,
    dashcards: Optional[List[Dict[str, Any]]] = None,
    tabs: Optional[List[Dict[str, Any]]] = None,
    parameters: Optional[List[Dict[str, Any]]] = None,
    name: Optional[str] = None,
    description: Optional[str] = None,
    collection_id: Optional[int] = None,
    archived: Optional[bool] = None
) -> str:
    """
    Update a dashboard with new cards, tabs, enhanced parameters, and/or metadata.
    
    **IMPORTANT: Call GET_DASHCARDS_SCHEMA and GET_DASHBOARD_PARAMETERS_DOCUMENTATION first to understand the formats**
    
    This tool allows you to:
    - Add new cards to a dashboard using the dashcards parameter
    - Update existing cards by providing their existing ID
    - Add/update dashboard tabs using the tabs parameter
    - Add/update dashboard parameters using the parameters parameter
    - Update dashboard metadata (name, description, collection, archived status)
    
    DASHCARDS FORMAT:
    The dashcards parameter must be a list of objects with the following structure:
    {
        "id": integer,           // Existing ID for updates, negative (-1, -2, -3) for new cards
        "card_id": integer,      // Required: 5-digit card ID from Metabase
        "col": integer,          // Required: Column position (0-23)
        "row": integer,          // Required: Row position (0+)
        "size_x": integer,       // Required: Width in columns (1-24)
        "size_y": integer,       // Required: Height in rows (1+)
        "dashboard_tab_id": int  // Optional: Tab ID for multi-tab dashboards
    }
    
    TABS FORMAT:
    The tabs parameter must be a list of objects with the following structure:
    {
        "id": integer,           // Existing ID for updates, negative (-1, -2, -3) for new tabs
        "name": string           // Required: Tab name
    }
    
    DASHBOARD PARAMETERS:
    The new dashboard parameters system supports:
    - ALL dashboard parameter types (string, number, date, temporal-unit, location, ID)
    - Multi-select support where applicable (string/=, number/=, id, location)
    - Automatic ID generation (8-character alphanumeric)
    - Value sources: static lists, card sources, connected values
    - Comprehensive validation and error prevention
    - Name-based identification with automatic processing
    
    **CRITICAL**: Parameters are identified by NAME only. IDs are generated automatically.
    For parameters: call GET_DASHBOARD_PARAMETERS_DOCUMENTATION for complete format.

    GRID CONSTRAINTS:
    - Dashboard grid has 24 columns (col: 0-23)
    - col + size_x must not exceed 24
    - Cards cannot overlap (you must manage positioning)
    
    Args:
        id: Dashboard ID to update
        ctx: MCP context
        dashcards: List of dashboard cards to add/update (call GET_DASHCARDS_SCHEMA for format)
        tabs: List of dashboard tabs to add/update (format: [{"id": int, "name": string}])
        parameters: List of dashboard parameters (call GET_DASHBOARD_PARAMETERS_DOCUMENTATION for format)
        name: New dashboard name (optional)
        description: New dashboard description (optional)
        collection_id: New collection ID (optional)
        archived: Whether the dashboard is archived (optional)
        
    Returns:
        JSON string with update result or error information
    """
    client = get_metabase_client(ctx)

    logger.info(f"Tool called: update_dashboard(id={id}, name={name})")
    
    # Validate dashcards if provided
    if dashcards is not None:
        validation_result = validate_dashcards_helper(dashcards)
        if not validation_result["valid"]:
            return json.dumps({
                "success": False,
                "error": "Invalid dashcards format",
                "validation_errors": validation_result["errors"],
                "help": "Call GET_DASHCARDS_SCHEMA to understand the correct format. Forbidden keys: action_id, series, visualization_settings, parameter_mappings"
            }, indent=2)
    
    # Validate tabs if provided
    if tabs is not None:
        tabs_validation_result = validate_tabs_helper(tabs)
        if not tabs_validation_result["valid"]:
            return json.dumps({
                "success": False,
                "error": "Invalid tabs format",
                "validation_errors": tabs_validation_result["errors"],
                "help": "Tabs must have 'name' field (string) and optional 'id' field (integer). Use negative IDs for new tabs."
            }, indent=2)
    
    # Validate dashboard parameters if provided
    if parameters is not None:
        parameters_validation_result = validate_dashboard_parameters_helper(parameters)
        if not parameters_validation_result["valid"]:
            return json.dumps({
                "success": False,
                "error": "Invalid dashboard parameters format",
                "validation_errors": parameters_validation_result["errors"],
                "help": "Call GET_DASHBOARD_PARAMETERS_DOCUMENTATION to understand the correct format. Required fields: name, type."
            }, indent=2)
        
        # Process parameters with full validation
        try:
            processed_parameters, processing_errors = await process_dashboard_parameters(client, parameters)
            if processing_errors:
                return json.dumps({
                    "success": False,
                    "error": "Dashboard parameters processing failed",
                    "validation_errors": processing_errors,
                    "help": "Check parameter configuration and ensure referenced cards are accessible."
                }, indent=2)
            parameters = processed_parameters
        except Exception as e:
            return json.dumps({
                "success": False,
                "error": "Dashboard parameters processing error",
                "message": str(e)
            }, indent=2)
    
    try:
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
        if dashcards is not None:
            update_data["dashcards"] = dashcards
        if tabs is not None:
            update_data["tabs"] = tabs
        if parameters is not None:
            update_data["parameters"] = parameters
        
        # If no fields were provided to update, return early
        if not update_data:
            return json.dumps({
                "success": False,
                "error": "No fields provided for update"
            }, indent=2)
        
        # Perform the update
        data, status, error = await client.auth.make_request(
            "PUT", f"dashboard/{id}", json=update_data
        )
        
        if error:
            return format_error_response(
                status_code=status,
                error_type="update_error",
                message=error,
                request_info={
                    "endpoint": f"/api/dashboard/{id}", 
                    "method": "PUT"
                }
            )
        
        # Return a concise success response with essential info
        return json.dumps({
            "success": True,
            "dashboard_id": data.get("id"),
            "name": data.get("name"),
            "dashcard_count": len(data.get("dashcards", [])) if "dashcards" in data else None,
            "tab_count": len(data.get("tabs", [])) if "tabs" in data else None,
            "parameter_count": len(data.get("parameters", [])) if "parameters" in data else None
        }, indent=2)
        
    except Exception as e:
        logger.error(f"Error updating dashboard {id}: {e}")
        return format_error_response(
            status_code=500,
            error_type="update_error",
            message=str(e),
            request_info={
                "endpoint": f"/api/dashboard/{id}", 
                "method": "PUT"
            }
        )


@mcp.tool(name="get_dashboard_tab", description="Retrieve cards for a specific dashboard tab with pagination")
async def get_dashboard_tab(
    dashboard_id: int, 
    ctx: Context, 
    tab_id: Optional[int] = None,
    page: int = 1,
    page_size: int = 20
) -> str:
    """
    Retrieve cards for a specific dashboard tab with pagination.
    
    Args:
        dashboard_id: Dashboard ID
        ctx: MCP context
        tab_id: Tab ID (optional, if not provided for single-tab dashboards)
        page: Page number for pagination (default: 1)
        page_size: Number of cards per page (default: 20)
        
    Returns:
        Dashboard tab data with paginated cards as JSON string
    """
    client = get_metabase_client(ctx)
    
    # Validate pagination parameters
    if page < 1:
        return format_error_response(
            status_code=400,
            error_type="invalid_pagination",
            message="Page number must be greater than or equal to 1",
            request_info={"dashboard_id": dashboard_id, "tab_id": tab_id, "page": page}
        )
    
    if page_size < 1:
        return format_error_response(
            status_code=400,
            error_type="invalid_pagination",
            message="Page size must be greater than or equal to 1",
            request_info={"dashboard_id": dashboard_id, "tab_id": tab_id, "page_size": page_size}
        )
    
    try:
        # Get the full dashboard first
        data = await client.get_resource("dashboard", dashboard_id)
        
        # Check if the dashboard has tabs
        has_tabs = "tabs" in data and isinstance(data["tabs"], list) and data["tabs"]
        
        # If tab_id is provided, validate it
        if tab_id is not None:
            if not has_tabs:
                # No tabs but tab_id was provided
                return format_error_response(
                    status_code=400,
                    error_type="invalid_tab",
                    message=f"Dashboard {dashboard_id} does not have explicit tabs, but tab_id {tab_id} was provided",
                    request_info={"dashboard_id": dashboard_id, "tab_id": tab_id}
                )
            
            # Check if the tab_id exists
            tab_exists = any(tab["id"] == tab_id for tab in data["tabs"])
            if not tab_exists:
                return format_error_response(
                    status_code=404,
                    error_type="tab_not_found",
                    message=f"Tab {tab_id} not found in dashboard {dashboard_id}",
                    request_info={"dashboard_id": dashboard_id, "tab_id": tab_id}
                )
        elif has_tabs:
            # No tab_id provided but dashboard has tabs
            return format_error_response(
                status_code=400,
                error_type="missing_tab_id",
                message=f"Dashboard {dashboard_id} has multiple tabs, but no tab_id was provided",
                request_info={"dashboard_id": dashboard_id, "available_tabs": data["tabs"]}
            )
        
        # Filter dashcards by tab_id if tabs exist, otherwise return all cards
        filtered_dashcards = []
        
        if "dashcards" in data and isinstance(data["dashcards"], list):
            for dashcard in data["dashcards"]:
                # For single-tab dashboards or cards with matching tab_id
                if (not has_tabs) or ("dashboard_tab_id" in dashcard and dashcard["dashboard_tab_id"] == tab_id):
                    # Process card data to make it more manageable
                    processed_dashcard = dashcard.copy()
                    
                    # Process regular card
                    if "card" in processed_dashcard and processed_dashcard["card"] is not None:
                        card = processed_dashcard["card"]
                        processed_dashcard["card_summary"] = {
                            "id": card.get("id"),
                            "name": card.get("name"),
                            "description": card.get("description"),
                            "display": card.get("display"),
                            "collection_id": card.get("collection_id"),
                            "database_id": card.get("database_id"),
                            "table_id": card.get("table_id"),
                            "query_type": card.get("query_type"),
                        }
                        # Remove the full card object but keep visualization settings
                        if "visualization_settings" in card:
                            processed_dashcard["card_visualization_settings"] = card["visualization_settings"]
                        processed_dashcard["card"] = None
                    
                    # Process series cards if present
                    if "series" in processed_dashcard and isinstance(processed_dashcard["series"], list):
                        series_summaries = []
                        for series_card in processed_dashcard["series"]:
                            if series_card is not None:
                                series_summaries.append({
                                    "id": series_card.get("id"),
                                    "name": series_card.get("name"),
                                    "description": series_card.get("description")
                                })
                        processed_dashcard["series_summary"] = series_summaries
                        processed_dashcard["series"] = []
                    
                    filtered_dashcards.append(processed_dashcard)
            
        # Sort dashcards by position (top to bottom, left to right)
        # This means sorting primarily by row and secondarily by col
        filtered_dashcards.sort(key=lambda card: (card.get("row", 0), card.get("col", 0)))
        
        # Apply pagination
        total_cards = len(filtered_dashcards)
        total_pages = (total_cards + page_size - 1) // page_size if total_cards > 0 else 1
        
        # Adjust page if it's beyond the available pages
        if page > total_pages and total_pages > 0:
            return format_error_response(
                status_code=400,
                error_type="page_out_of_range",
                message=f"Page {page} exceeds the total number of pages ({total_pages})",
                request_info={"dashboard_id": dashboard_id, "tab_id": tab_id, "page": page, "total_pages": total_pages}
            )
        
        # Calculate page indices
        start_idx = (page - 1) * page_size
        end_idx = min(start_idx + page_size, total_cards)
        
        # Get the paginated dashcards
        paginated_dashcards = filtered_dashcards[start_idx:end_idx]
        
        # Prepare the response object
        tab_data = {
            "dashboard_id": dashboard_id,
            "dashcards": paginated_dashcards,
            "dashcard_count": len(paginated_dashcards),
            "pagination": {
                "page": page,
                "page_size": page_size,
                "total_cards": total_cards,
                "total_pages": total_pages,
                "has_more": page < total_pages,
                "note": "Pagination is handled by the tool and not by the Metabase API"
            }
        }
        
        # Add tab information if it exists
        if has_tabs and tab_id is not None:
            tab_info = next((tab for tab in data["tabs"] if tab["id"] == tab_id), None)
            if tab_info:
                tab_data["tab"] = tab_info
        else:
            tab_data["is_single_tab"] = True
        
        # Add dashboard metadata
        for key in ["name", "description", "collection_id", "collection", "updated_at", "created_at"]:
            if key in data:
                tab_data[key] = data[key]
        
        logger.info(f"Returning {len(paginated_dashcards)} cards (page {page}/{total_pages}) " + 
                  f"for dashboard {dashboard_id}" + 
                  (f", tab {tab_id}" if tab_id is not None else ""))
        
        # Convert data to JSON string
        response = json.dumps(tab_data, indent=2)
        
        # Check response size before returning
        metabase_ctx = ctx.request_context.lifespan_context
        config = metabase_ctx.auth.config
        return check_response_size(response, config)
    except Exception as e:
        logger.error(f"Error getting dashboard tab: {e}")
        return format_error_response(
            status_code=500,
            error_type="retrieval_error",
            message=str(e),
            request_info={"endpoint": f"/api/dashboard/{dashboard_id}", "method": "GET", "tab_id": tab_id, "page": page, "page_size": page_size}
        )


@mcp.tool(name="execute_card_query", description="Execute a card's query to get its data results, optionally in a dashboard context")
async def execute_card_query(
    card_id: int,
    ctx: Context,
    dashboard_id: Optional[int] = None,
    dashcard_id: Optional[int] = None,
    parameters: Optional[List[Dict[str, Any]]] = None,
    ignore_cache: bool = False,
    collection_preview: Optional[bool] = None
) -> str:
    """
    Execute the query associated with a card to get its data results,
    optionally in the context of a dashboard.
    
    Args:
        card_id: Card ID
        ctx: MCP context
        dashboard_id: Optional dashboard ID for dashboard context (default: None)
        dashcard_id: Dashboard Card ID, required if dashboard_id is provided (default: None)
        parameters: List of parameter values to apply (default: None)
        ignore_cache: Whether to ignore cached results (default: False)
        collection_preview: Whether this is for a collection preview (default: None)
        
    Returns:
        Query results as JSON string, potentially with dashboard context
    """
    client = get_metabase_client(ctx)
    
    try:
        # Validate parameters
        if dashboard_id is not None and dashcard_id is None:
            return format_error_response(
                status_code=400,
                error_type="missing_parameter",
                message="dashcard_id is required when dashboard_id is provided",
                request_info={"card_id": card_id, "dashboard_id": dashboard_id}
            )
        
        # Build request data
        request_data = {}
        if ignore_cache:
            request_data["ignore_cache"] = ignore_cache
        if collection_preview is not None:
            request_data["collection_preview"] = collection_preview
        
        # Determine which endpoint to use based on parameters
        if dashboard_id is not None and dashcard_id is not None:
            # Use dashboard card context
            endpoint = f"dashboard/{dashboard_id}/dashcard/{dashcard_id}/card/{card_id}/query"
            
            # Add dashboard-specific parameters
            if parameters:
                request_data["parameters"] = parameters
            # Add a random dashboard_load_id for tracking
            request_data["dashboard_load_id"] = f"query_{dashboard_id}_{int(time.time())}"
            
            logger.info(f"Executing card query in dashboard context: dashboard_id={dashboard_id}, dashcard_id={dashcard_id}, card_id={card_id}")
        else:
            # Use standalone card context
            endpoint = f"card/{card_id}/query"
            if dashboard_id is not None:
                request_data["dashboard_id"] = dashboard_id
            
            logger.info(f"Executing standalone card query: card_id={card_id}")
        
        # Execute the query
        data, status, error = await client.auth.make_request(
            "POST", endpoint, json=request_data
        )
        
        if error:
            return format_error_response(
                status_code=status,
                error_type="query_error",
                message=str(error),
                request_info={
                    "endpoint": endpoint,
                    "card_id": card_id,
                    "dashboard_id": dashboard_id,
                    "dashcard_id": dashcard_id
                }
            )
        
        # Add metadata about the execution context
        if "data" in data:
            metadata = {
                "execution_context": {
                    "card_id": card_id,
                    "timestamp": time.time(),
                    "query_type": "dashboard_card" if dashboard_id and dashcard_id else "standalone_card"
                }
            }
            
            if dashboard_id:
                metadata["execution_context"]["dashboard_id"] = dashboard_id
            if dashcard_id:
                metadata["execution_context"]["dashcard_id"] = dashcard_id
            
            # Add row count if available
            if "rows" in data["data"]:
                row_count = len(data["data"]["rows"])
                metadata["row_count"] = row_count
                logger.info(f"Query returned {row_count} rows")
            
            # Add metadata to the response
            data["metadata"] = metadata
        
        # Convert to JSON string
        response = json.dumps(data, indent=2)
        
        # Check response size before returning
        metabase_ctx = ctx.request_context.lifespan_context
        config = metabase_ctx.auth.config
        return check_response_size(response, config)
        
    except Exception as e:
        logger.error(f"Error executing card query: {e}")
        return format_error_response(
            status_code=500,
            error_type="execution_error",
            message=str(e),
            request_info={
                "card_id": card_id,
                "dashboard_id": dashboard_id,
                "dashcard_id": dashcard_id
            }
        )
