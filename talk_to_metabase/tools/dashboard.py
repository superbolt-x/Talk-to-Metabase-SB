"""
Dashboard operations MCP tools.
"""

import json
import logging
import time
from typing import Dict, List, Optional, Any

from mcp.server.fastmcp import Context, FastMCP

from ..server import get_server_instance
from .common import format_error_response, get_metabase_client, check_response_size, check_guidelines_enforcement

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
    # Check guidelines enforcement first
    guidelines_error = check_guidelines_enforcement(ctx)
    if guidelines_error:
        return guidelines_error
        
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
    # Check guidelines enforcement first
    guidelines_error = check_guidelines_enforcement(ctx)
    if guidelines_error:
        return guidelines_error
        
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
    # Check guidelines enforcement first
    guidelines_error = check_guidelines_enforcement(ctx)
    if guidelines_error:
        return guidelines_error
        
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
    
    client = get_metabase_client(ctx)
    
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
    # Check guidelines enforcement first
    guidelines_error = check_guidelines_enforcement(ctx)
    if guidelines_error:
        return guidelines_error
        
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
