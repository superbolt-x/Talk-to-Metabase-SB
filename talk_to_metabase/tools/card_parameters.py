"""
Card parameters validation tools for Metabase MCP server.
"""

import json
import logging
import random
import re
import string
from typing import Dict, List, Tuple, Any, Optional

import jsonschema
from mcp.server.fastmcp import Context

from ..server import get_server_instance
from ..resources import load_card_parameters_schema
from .common import format_error_response, check_response_size

logger = logging.getLogger(__name__)

# Register tools with the server
mcp = get_server_instance()


# Note: load_card_parameters_schema is now imported from resources module


def generate_parameter_id() -> str:
    """
    Generate a unique parameter ID.
    
    The ID is a UUID-style string that Metabase uses for parameter IDs.
    
    Returns:
        UUID-style string to use as parameter ID
    """
    # Generate a random UUID-style string
    import uuid
    return str(uuid.uuid4())


def generate_slug_from_name(name: str) -> str:
    """
    Generate a URL-friendly slug from a parameter name.
    
    Args:
        name: Parameter name
        
    Returns:
        URL-friendly slug
    """
    # Convert to lowercase, replace spaces and special chars with underscores
    slug = re.sub(r'[^a-zA-Z0-9]+', '_', name.lower().strip())
    # Remove leading/trailing underscores
    slug = slug.strip('_')
    # Ensure it's not empty
    if not slug:
        slug = "parameter"
    return slug


def extract_template_tag_name_from_target(target: List[Any]) -> Optional[str]:
    """
    Extract template tag name from a parameter target.
    
    Args:
        target: Parameter target array
        
    Returns:
        Template tag name or None if not found
    """
    try:
        if len(target) >= 2:
            if target[0] == "variable" and len(target[1]) >= 2:
                return target[1][1]  # ["variable", ["template-tag", "tag_name"]]
    except (IndexError, TypeError):
        pass
    return None


def generate_template_tags_from_parameters(parameters: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Generate template tags from parameters.
    
    Args:
        parameters: List of parameter dictionaries
        
    Returns:
        Dictionary of template tags
    """
    template_tags = {}
    
    for param in parameters:
        # Get template tag name from target or generate from slug
        tag_name = None
        if "target" in param:
            tag_name = extract_template_tag_name_from_target(param["target"])
        
        if not tag_name:
            tag_name = param.get("slug") or generate_slug_from_name(param.get("name", "parameter"))
        
        # Determine template tag type based on parameter type
        param_type = param.get("type", "category")
        
        # Map parameter types to template tag types (simplified)
        if param_type == "date/single":
            template_tag_type = "date"
        elif param_type == "number/=":
            template_tag_type = "number"
        else:  # category or any other type defaults to text
            template_tag_type = "text"
        
        template_tag = {
            "type": template_tag_type,
            "name": tag_name,
            "id": param["id"],
            "display-name": param.get("name", tag_name)
        }
        
        # Add default value if provided
        if "default" in param and param["default"] is not None:
            template_tag["default"] = param["default"]
        
        # Add required flag if provided
        if "required" in param:
            template_tag["required"] = param["required"]
        
        template_tags[tag_name] = template_tag
    
    return template_tags


def validate_card_parameters(parameters: List[Dict[str, Any]]) -> Tuple[bool, List[str]]:
    """
    Validate card parameters against the JSON schema and essential business rules.
    
    Args:
        parameters: List of parameter dictionaries
        
    Returns:
        Tuple of (is_valid, error_messages)
    """
    schema = load_card_parameters_schema()
    if schema is None:
        return False, ["Could not load card parameters schema"]
    
    try:
        # JSON Schema handles most validation automatically:
        # - Required fields (type, name, default)
        # - Valid parameter types (enum validation)
        # - Field structure and data types
        # - Conditional requirements (if/then for values_query_type)
        jsonschema.validate(parameters, schema)
        
        # Only add business logic that JSON Schema can't handle:
        errors = []
        
        # Check for duplicate names (JSON Schema can't validate across array items)
        seen_names = set()
        for i, param in enumerate(parameters):
            name = param.get("name")
            if name and name in seen_names:
                errors.append(f"Parameter {i}: duplicate name '{name}'")
            elif name:
                seen_names.add(name)
        
        # Check for duplicate IDs (only for parameters that have IDs)
        seen_ids = set()
        for i, param in enumerate(parameters):
            param_id = param.get("id")
            if param_id and param_id in seen_ids:
                errors.append(f"Parameter {i}: duplicate ID '{param_id}'")
            elif param_id:
                seen_ids.add(param_id)
        
        return len(errors) == 0, errors
        
    except jsonschema.ValidationError as e:
        return False, [f"Validation error: {e.message}"]
    except jsonschema.SchemaError as e:
        return False, [f"Schema error: {e.message}"]
    except Exception as e:
        return False, [f"Unexpected validation error: {str(e)}"]


@mcp.tool(name="GET_CARD_PARAMETERS_SCHEMA", description="Get the JSON schema for card parameters validation")
async def get_card_parameters_schema(ctx: Context) -> str:
    """
    Get the JSON schema for validating card parameters structure.
    
    This tool returns the complete JSON schema used to validate parameters
    when creating or updating cards with the create_card and update_card tools.
    
    Args:
        ctx: MCP context
        
    Returns:
        JSON schema for card parameters validation
    """
    logger.info("Tool called: GET_CARD_PARAMETERS_SCHEMA()")
    
    try:
        schema = load_card_parameters_schema()
        if schema is None:
            return format_error_response(
                status_code=500,
                error_type="schema_loading_error",
                message="Could not load card parameters JSON schema",
                request_info={"schema_file": "card_parameters.json"}
            )
        
        response_data = {
            "success": True,
            "schema": schema,
            "description": "JSON schema for validating card parameters in create_card and update_card tools",
            "simplified_note": "This is a simplified parameter system with only 3 parameter types and variable targets only. JSON Schema handles most validation automatically.",
            "supported_types": {
                "category": "Text input with autocomplete (from text template tags)",
                "number/=": "Number input (from number template tags)",
                "date/single": "Date picker (from date template tags)"
            },
            "usage": {
                "new_parameters": "For new parameters, omit the 'id' field - it will be auto-generated",
                "existing_parameters": "For updating existing parameters, include the existing 'id' from the current card",
                "required_fields": ["type", "name", "default"],
                "auto_generated_fields": ["id (for new)", "slug (always)", "target (if not specified)"],
                "slug_generation": "Slugs are automatically generated from parameter names - do not specify manually",
                "target_type": "All parameters use variable targets only - no field filters supported"
            },
            "examples": [
                {
                    "name": "order_status",
                    "type": "category",
                    "default": "pending"
                },
                {
                    "name": "price_limit",
                    "type": "number/=",
                    "default": 100
                },
                {
                    "name": "created_date",
                    "type": "date/single",
                    "default": "2024-01-01"
                },
                {
                    "id": "existing-param-id",
                    "name": "updated_filter",
                    "type": "category",
                    "note": "Include existing ID when updating"
                }
            ]
        }
        
        # Convert to JSON string
        response = json.dumps(response_data, indent=2)
        
        # Check response size
        metabase_ctx = ctx.request_context.lifespan_context
        config = metabase_ctx.auth.config
        return check_response_size(response, config)
        
    except Exception as e:
        logger.error(f"Error in GET_CARD_PARAMETERS_SCHEMA: {e}")
        return format_error_response(
            status_code=500,
            error_type="tool_error",
            message=f"Error retrieving card parameters schema: {str(e)}",
            request_info={}
        )


def validate_card_parameters_helper(parameters: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Helper function to validate card parameters and return structured result.
    
    Args:
        parameters: List of parameter dictionaries
        
    Returns:
        Dictionary with validation results
    """
    is_valid, errors = validate_card_parameters(parameters)
    
    return {
        "valid": is_valid,
        "errors": errors,
        "parameters_count": len(parameters) if parameters else 0,
        "validation_timestamp": "2025-06-13T00:00:00Z"
    }


def process_card_parameters(parameters: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Process card parameters to ensure all have valid IDs and slugs.
    
    For parameters without IDs (new parameters), generates a unique ID.
    For all parameters, generates slug from name.
    
    Args:
        parameters: List of parameter dictionaries
        
    Returns:
        List of processed parameter dictionaries with IDs and slugs
    """
    processed_parameters = []
    existing_ids = set()
    existing_slugs = set()
    
    for param in parameters:
        # Create a copy of the parameter to avoid modifying the original
        processed_param = param.copy()
        
        # Generate ID if not present or empty
        if "id" not in processed_param or not processed_param["id"]:
            new_id = generate_parameter_id()
            # Make sure it doesn't collide with existing IDs
            while new_id in existing_ids:
                new_id = generate_parameter_id()
            processed_param["id"] = new_id
        
        # Always generate slug from name (never use user-provided slug)
        if "name" in processed_param:
            base_slug = generate_slug_from_name(processed_param["name"])
            slug = base_slug
            counter = 1
            # Ensure slug uniqueness
            while slug in existing_slugs:
                slug = f"{base_slug}_{counter}"
                counter += 1
            processed_param["slug"] = slug
            existing_slugs.add(slug)
        
        # Generate target if not provided (always variable target)
        if "target" not in processed_param:
            slug = processed_param.get("slug", "parameter")
            # All targets are variable targets in the simplified system
            processed_param["target"] = ["variable", ["template-tag", slug]]
        
        # Track existing IDs
        existing_ids.add(processed_param["id"])
        processed_parameters.append(processed_param)
    
    return processed_parameters
