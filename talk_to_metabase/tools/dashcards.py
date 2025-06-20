"""
Dashboard cards validation tools for Metabase MCP server.
"""

import json
import logging
from typing import Dict, List, Tuple, Any, Optional

import jsonschema
from mcp.server.fastmcp import Context

from ..server import get_server_instance
from ..resources import load_dashcards_schema
from .common import format_error_response, check_response_size

logger = logging.getLogger(__name__)

# Register tools with the server
mcp = get_server_instance()


# Note: load_dashcards_schema is now imported from resources module


def validate_dashcards(dashcards: List[Dict[str, Any]]) -> Tuple[bool, List[str]]:
    """
    Validate dashcards against the JSON schema and additional business rules.
    
    Args:
        dashcards: List of dashcard dictionaries
        
    Returns:
        Tuple of (is_valid, error_messages)
    """
    schema = load_dashcards_schema()
    if schema is None:
        return False, ["Could not load dashcards schema"]
    
    try:
        # First validate against JSON schema
        jsonschema.validate(dashcards, schema)
        
        # Additional validation for business rules
        errors = []
        
        # Check for forbidden keys
        forbidden_keys = {"action_id", "series", "visualization_settings", "parameter_mappings"}
        
        for i, dashcard in enumerate(dashcards):
            # Check for forbidden keys
            for key in forbidden_keys:
                if key in dashcard:
                    errors.append(f"Dashcard {i}: forbidden key '{key}' is not allowed")
            
            # Validate grid boundaries
            col = dashcard.get("col", 0)
            size_x = dashcard.get("size_x", 1)
            if col + size_x > 24:
                errors.append(f"Dashcard {i}: col ({col}) + size_x ({size_x}) = {col + size_x} exceeds grid width of 24")
            
            # Validate negative IDs for new cards
            card_id = dashcard.get("id")
            if card_id is not None and card_id < 0:
                # This is a new card, make sure all required fields are present
                required_fields = ["card_id", "col", "row", "size_x", "size_y"]
                for field in required_fields:
                    if field not in dashcard:
                        errors.append(f"Dashcard {i}: missing required field '{field}' for new card")
        
        if errors:
            return False, errors
            
        return True, []
        
    except jsonschema.ValidationError as e:
        return False, [f"Validation error: {e.message}"]
    except jsonschema.SchemaError as e:
        return False, [f"Schema error: {e.message}"]
    except Exception as e:
        return False, [f"Unexpected validation error: {str(e)}"]


@mcp.tool(name="GET_DASHCARDS_SCHEMA", description="Get the JSON schema for dashboard cards validation")
async def get_dashcards_schema(ctx: Context) -> str:
    """
    Get the JSON schema for validating dashboard cards (dashcards) structure.
    
    This tool returns the complete JSON schema used to validate dashcards
    when updating dashboards with the update_dashboard tool.
    
    Args:
        ctx: MCP context
        
    Returns:
        JSON schema for dashcards validation
    """
    logger.info("Tool called: GET_DASHCARDS_SCHEMA()")
    
    try:
        schema = load_dashcards_schema()
        if schema is None:
            return format_error_response(
                status_code=500,
                error_type="schema_loading_error",
                message="Could not load dashcards JSON schema",
                request_info={"schema_file": "dashcards.json"}
            )
        
        response_data = {
            "success": True,
            "schema": schema,
            "description": "JSON schema for validating dashboard cards in update_dashboard tool",
            "usage": {
                "forbidden_keys": ["action_id", "series", "visualization_settings", "parameter_mappings"],
                "required_keys": ["card_id", "col", "row", "size_x", "size_y"],
                "optional_keys": ["id", "dashboard_tab_id"],
                "grid_constraints": {
                    "col_range": "0-23 (24 columns total)",
                    "size_x_range": "1-24",
                    "col_plus_size_x_max": 24
                },
                "id_convention": "Use existing ID for updating, negative values (-1, -2, -3) for new cards"
            }
        }
        
        # Convert to JSON string
        response = json.dumps(response_data, indent=2)
        
        # Check response size
        metabase_ctx = ctx.request_context.lifespan_context
        config = metabase_ctx.auth.config
        return check_response_size(response, config)
        
    except Exception as e:
        logger.error(f"Error in GET_DASHCARDS_SCHEMA: {e}")
        return format_error_response(
            status_code=500,
            error_type="tool_error",
            message=f"Error retrieving dashcards schema: {str(e)}",
            request_info={}
        )


def validate_dashcards_helper(dashcards: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Helper function to validate dashcards and return structured result.
    
    Args:
        dashcards: List of dashcard dictionaries
        
    Returns:
        Dictionary with validation results
    """
    is_valid, errors = validate_dashcards(dashcards)
    
    return {
        "valid": is_valid,
        "errors": errors,
        "dashcards_count": len(dashcards) if dashcards else 0,
        "validation_timestamp": "2025-06-06T00:00:00Z"  # Current timestamp would be better in real implementation
    }


def validate_tabs(tabs: List[Dict[str, Any]]) -> Tuple[bool, List[str]]:
    """
    Validate tabs structure for dashboard updates.
    
    Args:
        tabs: List of tab dictionaries
        
    Returns:
        Tuple of (is_valid, error_messages)
    """
    errors = []
    
    for i, tab in enumerate(tabs):
        # Check required fields
        if "name" not in tab:
            errors.append(f"Tab {i}: missing required field 'name'")
        
        # Check that name is a string
        if "name" in tab and not isinstance(tab["name"], str):
            errors.append(f"Tab {i}: 'name' must be a string")
        
        # Check for id field (optional, but if present should be integer)
        if "id" in tab:
            if not isinstance(tab["id"], int):
                errors.append(f"Tab {i}: 'id' must be an integer")
        
        # Check for unexpected fields
        allowed_fields = {"id", "name"}
        for key in tab.keys():
            if key not in allowed_fields:
                errors.append(f"Tab {i}: unexpected field '{key}'. Only 'id' and 'name' are allowed")
    
    return len(errors) == 0, errors


def validate_tabs_helper(tabs: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Helper function to validate tabs and return structured result.
    
    Args:
        tabs: List of tab dictionaries
        
    Returns:
        Dictionary with validation results
    """
    is_valid, errors = validate_tabs(tabs)
    
    return {
        "valid": is_valid,
        "errors": errors,
        "tabs_count": len(tabs) if tabs else 0,
        "validation_timestamp": "2025-06-06T00:00:00Z"
    }
