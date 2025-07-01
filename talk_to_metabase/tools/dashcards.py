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
        
        # Check for forbidden keys (parameter_mappings is now allowed but will be processed)
        forbidden_keys = {"action_id", "series", "visualization_settings"}
        
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
                "forbidden_keys": ["action_id", "series", "visualization_settings"],
                "required_keys": ["card_id", "col", "row", "size_x", "size_y"],
                "optional_keys": ["id", "dashboard_tab_id", "parameter_mappings"],
                "parameter_mappings": {
                    "description": "Optional array to connect dashboard parameters to card parameters by name",
                    "format": [
                        {
                            "dashboard_parameter_name": "Name of dashboard parameter",
                            "card_parameter_name": "Name of card parameter (or slug)"
                        }
                    ]
                },
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


async def process_parameter_mappings(
    client,
    dashcards: List[Dict[str, Any]],
    dashboard_parameters: List[Dict[str, Any]],
    card_parameters_by_card: Dict[int, List[Dict[str, Any]]]
) -> Tuple[List[Dict[str, Any]], List[str]]:
    """
    Process parameter mappings for dashcards, converting name-based mappings to ID-based mappings.
    
    Args:
        client: Metabase client
        dashcards: List of dashcard configurations
        dashboard_parameters: List of processed dashboard parameters with generated IDs
        card_parameters_by_card: Dictionary mapping card_id to list of card parameters
        
    Returns:
        Tuple of (processed_dashcards, errors)
    """
    errors = []
    processed_dashcards = []
    
    # Create lookup dictionaries for parameters
    dashboard_param_by_name = {param["name"]: param for param in dashboard_parameters}
    
    for i, dashcard in enumerate(dashcards):
        processed_dashcard = dashcard.copy()
        card_id = dashcard["card_id"]
        
        # Process parameter mappings if present
        if "parameter_mappings" in dashcard and dashcard["parameter_mappings"]:
            # Get card parameters for this card
            card_parameters = card_parameters_by_card.get(card_id, [])
            card_param_by_name = {param.get("name", ""): param for param in card_parameters if "name" in param}
            
            # Also check for slug-based mapping (parameters can be referenced by slug)
            card_param_by_slug = {param.get("slug", ""): param for param in card_parameters if "slug" in param}
            
            metabase_parameter_mappings = []
            
            for j, mapping in enumerate(dashcard["parameter_mappings"]):
                dashboard_param_name = mapping["dashboard_parameter_name"]
                card_param_name = mapping["card_parameter_name"]
                
                # Find dashboard parameter by name
                dashboard_param = dashboard_param_by_name.get(dashboard_param_name)
                if not dashboard_param:
                    errors.append(
                        f"Dashcard {i} mapping {j}: Dashboard parameter '{dashboard_param_name}' not found"
                    )
                    continue
                
                # Find card parameter by name or slug
                card_param = card_param_by_name.get(card_param_name) or card_param_by_slug.get(card_param_name)
                if not card_param:
                    errors.append(
                        f"Dashcard {i} mapping {j}: Card parameter '{card_param_name}' not found in card {card_id}"
                    )
                    continue
                
                # Create Metabase API parameter mapping
                metabase_mapping = {
                    "card_id": card_id,
                    "parameter_id": dashboard_param["id"],  # Dashboard parameter ID
                    "target": card_param["target"]  # Card parameter target
                }
                
                metabase_parameter_mappings.append(metabase_mapping)
            
            # Replace name-based mappings with ID-based mappings
            processed_dashcard["parameter_mappings"] = metabase_parameter_mappings
        
        processed_dashcards.append(processed_dashcard)
    
    return processed_dashcards, errors


async def get_card_parameters(client, card_id: int) -> Tuple[List[Dict[str, Any]], Optional[str]]:
    """
    Get parameters for a specific card.
    
    Args:
        client: Metabase client
        card_id: Card ID
        
    Returns:
        Tuple of (parameters_list, error_message)
    """
    try:
        # Get card definition
        data, status, error = await client.auth.make_request(
            "GET", f"card/{card_id}"
        )
        
        if error:
            return [], f"Cannot access card {card_id}: {error}"
        
        # Extract parameters from card
        parameters = data.get("parameters", [])
        return parameters, None
        
    except Exception as e:
        return [], f"Error getting parameters for card {card_id}: {str(e)}"


async def validate_parameter_mappings(
    client,
    dashcards: List[Dict[str, Any]],
    dashboard_parameters: List[Dict[str, Any]]
) -> Tuple[Dict[int, List[Dict[str, Any]]], List[str]]:
    """
    Validate parameter mappings and collect card parameters.
    
    Args:
        client: Metabase client
        dashcards: List of dashcard configurations
        dashboard_parameters: List of dashboard parameters
        
    Returns:
        Tuple of (card_parameters_by_card, errors)
    """
    errors = []
    card_parameters_by_card = {}
    dashboard_param_names = {param["name"] for param in dashboard_parameters}
    
    for i, dashcard in enumerate(dashcards):
        card_id = dashcard["card_id"]
        
        # Get card parameters if this card has parameter mappings
        if "parameter_mappings" in dashcard and dashcard["parameter_mappings"]:
            if card_id not in card_parameters_by_card:
                card_parameters, error = await get_card_parameters(client, card_id)
                if error:
                    errors.append(f"Dashcard {i}: {error}")
                    continue
                card_parameters_by_card[card_id] = card_parameters
            
            card_parameters = card_parameters_by_card[card_id]
            card_param_names = {param.get("name", "") for param in card_parameters if "name" in param}
            card_param_slugs = {param.get("slug", "") for param in card_parameters if "slug" in param}
            card_param_identifiers = card_param_names.union(card_param_slugs)
            
            # Validate each mapping
            for j, mapping in enumerate(dashcard["parameter_mappings"]):
                dashboard_param_name = mapping["dashboard_parameter_name"]
                card_param_name = mapping["card_parameter_name"]
                
                # Check if dashboard parameter exists
                if dashboard_param_name not in dashboard_param_names:
                    errors.append(
                        f"Dashcard {i} mapping {j}: Dashboard parameter '{dashboard_param_name}' not found in dashboard parameters"
                    )
                
                # Check if card parameter exists
                if card_param_name not in card_param_identifiers:
                    errors.append(
                        f"Dashcard {i} mapping {j}: Card parameter '{card_param_name}' not found in card {card_id}. Available: {list(card_param_identifiers)}"
                    )
    
    return card_parameters_by_card, errors
