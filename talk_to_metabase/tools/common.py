"""
Common utilities and helpers for Metabase MCP tools.
"""

import json
import logging
from typing import Any, Dict, Optional

from mcp.server.fastmcp import Context

from ..client import MetabaseClient
from ..server import MetabaseContext

logger = logging.getLogger(__name__)


def get_metabase_client(ctx: Context) -> MetabaseClient:
    """Get the Metabase client from the context."""
    metabase_ctx: MetabaseContext = ctx.request_context.lifespan_context
    return MetabaseClient(metabase_ctx.auth)


def format_error_response(
    status_code: int,
    error_type: str,
    message: str,
    metabase_error: Optional[Dict[str, Any]] = None,
    request_info: Optional[Dict[str, Any]] = None,
    raw_response: Optional[str] = None,
) -> str:
    """Format an error response for Claude."""
    error_data = {
        "success": False,
        "error": {
            "status_code": status_code,
            "error_type": error_type,
            "message": message,
        },
    }
    
    if metabase_error:
        error_data["error"]["metabase_error"] = metabase_error
    
    if request_info:
        error_data["error"]["request_info"] = request_info
    
    if raw_response:
        error_data["error"]["raw_response"] = raw_response
    
    return json.dumps(error_data, indent=2)


def check_response_size(response: str, config) -> str:
    """Check if response exceeds size limit and format appropriately.
    
    Args:
        response: The response string
        config: Configuration object containing size limit
        
    Returns:
        Original response if within limits, or error message if too large
    """
    response_length = len(response)
    limit = config.response_size_limit
    
    if response_length <= limit:
        return response
    
    logger.warning(f"Response size ({response_length}) exceeds limit ({limit})")
    
    # Create a summary with size information and truncate the response
    error_response = {
        "success": False,
        "error": {
            "error_type": "response_size_exceeded",
            "message": f"Response size ({response_length} characters) exceeds the configured limit ({limit} characters).",
            "size_info": {
                "actual_size": response_length,
                "size_limit": limit,
                "exceeded_by": response_length - limit
            }
        }
    }
    
    return json.dumps(error_response, indent=2)
