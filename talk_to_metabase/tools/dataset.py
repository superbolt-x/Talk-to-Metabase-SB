"""
Dataset query operations MCP tools.
"""

import json
import logging
from typing import Dict, Optional, Any

from mcp.server.fastmcp import Context, FastMCP

from ..server import get_server_instance
from .common import format_error_response, get_metabase_client, check_response_size

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Register tools with the server
mcp = get_server_instance()
logger.info("Registering dataset tools with the server...")


@mcp.tool(name="run_dataset_query", description="Execute a native SQL or MBQL query directly")
async def run_dataset_query(
    database: int,
    ctx: Context,
    native: Optional[Dict[str, Any]] = None,
    query: Optional[Dict[str, Any]] = None,
    type: str = "native"
) -> str:
    """
    Execute a query directly against a database using the Metabase dataset API.
    Supports both native SQL queries and structured MBQL queries.
    
    Args:
        database: Database ID
        ctx: MCP context
        native: Native query object with SQL (required for native queries)
        query: MBQL query object (required for structured queries)
        type: Query type, either "native" or "query" (default: "native")
        
    Returns:
        Query results as JSON string with essential fields
    """
    logger.info(f"Tool called: run_dataset_query(database={database}, type={type})")
    
    # Validate parameters
    if type == "native" and not native:
        return format_error_response(
            status_code=400,
            error_type="missing_parameter",
            message="Native query object is required for native query type",
            request_info={"database": database, "type": type}
        )
    
    if type == "query" and not query:
        return format_error_response(
            status_code=400,
            error_type="missing_parameter",
            message="MBQL query object is required for query type",
            request_info={"database": database, "type": type}
        )
    
    if type not in ["native", "query"]:
        return format_error_response(
            status_code=400,
            error_type="invalid_parameter",
            message=f"Invalid query type: {type}. Must be 'native' or 'query'",
            request_info={"database": database, "type": type}
        )
    
    client = get_metabase_client(ctx)
    
    try:
        # Build the query data
        query_data = {"database": database, "type": type}
        
        if type == "native":
            query_data["native"] = native
        else:
            query_data["query"] = query
        
        # Execute the query
        data, status, error = await client.auth.make_request(
            "POST", "dataset", json=query_data
        )
        
        if error:
            # For dataset errors, the response often contains useful information
            # about SQL errors, so include it in the error response
            return format_error_response(
                status_code=status,
                error_type="query_error",
                message=error,
                request_info={
                    "endpoint": "/api/dataset",
                    "method": "POST", 
                    "database": database,
                    "query_type": type
                },
                raw_response=data
            )
        
        # Extract only essential fields for the response
        essential_data = {
            "data": {
                "rows": data.get("data", {}).get("rows", []),
                "cols": data.get("data", {}).get("cols", []),
                "native_form": data.get("data", {}).get("native_form", {})
            },
            "status": data.get("status"),
            "database_id": data.get("database_id"),
            "started_at": data.get("started_at"),
            "running_time": data.get("running_time"),
            "row_count": data.get("row_count", len(data.get("data", {}).get("rows", []))),
            "results_timezone": data.get("results_timezone")
        }
        
        # Include error information if present
        if data.get("error"):
            essential_data["error"] = data.get("error")
            essential_data["error_type"] = data.get("error_type")
            
            # For more detailed error information
            if data.get("stacktrace"):
                essential_data["stacktrace"] = data.get("stacktrace")
            
            logger.error(f"Query failed with error: {data.get('error')}")
        
        # Convert to JSON string
        response = json.dumps(essential_data, indent=2)
        
        # Check response size before returning
        metabase_ctx = ctx.request_context.lifespan_context
        config = metabase_ctx.auth.config
        return check_response_size(response, config)
        
    except Exception as e:
        logger.error(f"Error executing dataset query: {e}")
        return format_error_response(
            status_code=500,
            error_type="execution_error",
            message=str(e),
            request_info={
                "endpoint": "/api/dataset",
                "method": "POST",
                "database": database,
                "query_type": type
            }
        )
