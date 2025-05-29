"""
Search operations MCP tools.
"""

import json
import logging
from typing import Dict, List, Optional, Any

from mcp.server.fastmcp import Context, FastMCP

from ..server import get_server_instance
from .common import format_error_response, get_metabase_client, check_response_size, check_guidelines_enforcement

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Register tools with the server
mcp = get_server_instance()
logger.info("Registering search tools with the server...")


@mcp.tool(name="search_resources", description="Search for resources across Metabase")
async def search_resources(
    ctx: Context,
    q: Optional[str] = None,
    models: Optional[List[str]] = None, 
    archived: bool = False,
    table_db_id: Optional[int] = None,
    filter_items_in_personal_collection: Optional[str] = None,
    created_at: Optional[str] = None,
    created_by: Optional[List[int]] = None,
    last_edited_at: Optional[str] = None,
    last_edited_by: Optional[List[int]] = None,
    search_native_query: Optional[bool] = None,
    verified: Optional[bool] = None,
    ids: Optional[List[int]] = None,
    include_dashboard_questions: bool = False,
    calculate_available_models: bool = False,
    context: Optional[str] = None,
    model_ancestors: bool = False,
    page: int = 1,
    page_size: int = 20,
) -> str:
    """
    Search for resources across Metabase with comprehensive filtering options and pagination.
    
    Args:
        ctx: MCP context
        q: Search term (value must be a non-blank string)
        models: Types of resources to search for. Allowed values: dashboard, table, dataset, 
               segment, collection, database, action, indexed-entity, metric, card
        archived: Include archived resources (default: False)
        table_db_id: Search for tables, cards, and models of a specific database ID
        filter_items_in_personal_collection: Filter items in personal collections.
                    Options: all, only, only-mine, exclude, exclude-others
        created_at: Search for items created at a specific timestamp
        created_by: Search for items created by specific user IDs
        last_edited_at: Search for items last edited at a specific timestamp
        last_edited_by: Search for items last edited by specific user IDs
        search_native_query: Whether to search the content of native queries
        verified: Whether to search for verified items only (requires Content Management or Official Collections premium feature)
        ids: Search for specific item IDs (works only when a single value is passed to models)
        include_dashboard_questions: Include questions from dashboards in results (default: False)
        calculate_available_models: Calculate which models are available given filters (default: False)
        context: Search context
        model_ancestors: Include model ancestors (default: False)
        page: Page number for pagination (default: 1)
        page_size: Number of results per page (default: 20)
        
    Returns:
        Search results as JSON string with pagination metadata
        
    Note:
        Not all item types support all filters, and the results will include only models that 
        support the provided filters. For example:
        - The created_by filter supports dashboards, models, actions, and cards.
        - The verified filter supports models and cards.
        A search query that has both filters applied will only return models and cards.
    """
    # Check guidelines enforcement first
    guidelines_error = check_guidelines_enforcement(ctx)
    if guidelines_error:
        return guidelines_error
        
    client = get_metabase_client(ctx)
    
    try:
        # Log the search parameters
        logger.info(f"Searching Metabase resources with query: {q}, models: {models}, page: {page}, page_size: {page_size}")
        
        # Handle models if it's a string representation of a list
        if isinstance(models, str) and models.startswith('[') and models.endswith(']'):
            try:
                models = json.loads(models)
                logger.info(f"Converted models string to list: {models}")
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse models string: {e}")
        
        # Execute the search with pagination
        result = await client.search(
            query=q,
            models=models,
            archived=archived,
            table_db_id=table_db_id,
            filter_items_in_personal_collection=filter_items_in_personal_collection,
            created_at=created_at,
            created_by=created_by,
            last_edited_at=last_edited_at,
            last_edited_by=last_edited_by,
            search_native_query=search_native_query,
            verified=verified,
            ids=ids,
            include_dashboard_questions=include_dashboard_questions,
            calculate_available_models=calculate_available_models,
            context=context,
            model_ancestors=model_ancestors,
            page=page,
            page_size=page_size,
        )
        
        # Debug: Log the results structure
        logger.info(f"Search returned {len(result['results'])} results on page {page} of {result['pagination']['total_pages']}")
        logger.info(f"Total results across all pages: {result['pagination']['total_count']}")
        
        # Convert data to JSON string
        response = json.dumps(result, indent=2)
        
        # Check response size before returning
        metabase_ctx = ctx.request_context.lifespan_context
        config = metabase_ctx.auth.config
        return check_response_size(response, config)
    except Exception as e:
        logger.error(f"Error searching resources: {e}")
        
        # Collect basic parameters for error reporting
        params = {}
        if q:
            params["q"] = q
        if models:
            params["models"] = models
        if page:
            params["page"] = page
        if page_size:
            params["page_size"] = page_size
            
        return format_error_response(
            status_code=500,
            error_type="search_error",
            message=str(e),
            request_info={"endpoint": "/api/search", "method": "GET", "params": params}
        )
