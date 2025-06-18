"""
Card parameters validation tools for Metabase MCP server.
"""

import json
import logging
import os
import random
import re
import string
from typing import Dict, List, Tuple, Any, Optional

import jsonschema
from mcp.server.fastmcp import Context

from ..server import get_server_instance
from .common import format_error_response, check_response_size

logger = logging.getLogger(__name__)

# Register tools with the server
mcp = get_server_instance()


def load_card_parameters_schema() -> Optional[Dict[str, Any]]:
    """
    Load the JSON schema for card parameters validation.
    
    Returns:
        Card parameters schema dictionary or None if loading fails
    """
    try:
        schema_path = os.path.join(
            os.path.dirname(__file__), 
            "..", 
            "schemas", 
            "card_parameters.json"
        )
        
        if not os.path.exists(schema_path):
            logger.error(f"Card parameters schema file not found: {schema_path}")
            return None
            
        with open(schema_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Error loading card parameters schema: {e}")
        return None


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
            elif target[0] == "dimension" and len(target[1]) >= 2:
                return target[1][1]  # ["dimension", ["template-tag", "tag_name"]]
            elif target[0] == "text-tag" and len(target) >= 2:
                return target[1]     # ["text-tag", "tag_name"]
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
        
        # Map parameter types to template tag types
        if param_type.startswith("date/"):
            template_tag_type = "date"
        elif param_type.startswith("number/"):
            template_tag_type = "number"
        elif param_type.startswith("dimension") or param.get("target", [{}])[0] == "dimension":
            template_tag_type = "dimension"
        else:
            template_tag_type = "text"  # Default
        
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
        
        # For dimension type, add additional configuration
        if template_tag_type == "dimension":
            # This would need more sophisticated mapping based on the field
            # For now, keep it simple
            template_tag["widget-type"] = "none"
        
        template_tags[tag_name] = template_tag
    
    return template_tags


def validate_card_parameters(parameters: List[Dict[str, Any]]) -> Tuple[bool, List[str]]:
    """
    Validate card parameters against the JSON schema and additional business rules.
    
    Args:
        parameters: List of parameter dictionaries
        
    Returns:
        Tuple of (is_valid, error_messages)
    """
    schema = load_card_parameters_schema()
    if schema is None:
        return False, ["Could not load card parameters schema"]
    
    try:
        # First validate against JSON schema
        jsonschema.validate(parameters, schema)
        
        # Additional validation for business rules
        errors = []
        
        # Check for duplicate IDs and names
        seen_ids = set()
        seen_names = set()
        
        for i, param in enumerate(parameters):
            # Check for required fields
            if "name" not in param or not param["name"]:
                errors.append(f"Parameter {i}: missing required field 'name'")
                
            if "type" not in param or not param["type"]:
                errors.append(f"Parameter {i}: missing required field 'type'")
            
            # Check for duplicate IDs (only for params with IDs)
            if "id" in param and param["id"]:
                if param["id"] in seen_ids:
                    errors.append(f"Parameter {i}: duplicate ID '{param['id']}'")
                else:
                    seen_ids.add(param["id"])
            
            # Check for duplicate names
            if "name" in param and param["name"]:
                if param["name"] in seen_names:
                    errors.append(f"Parameter {i}: duplicate name '{param['name']}'")
                else:
                    seen_names.add(param["name"])
            
            # Validate target structure
            if "target" in param:
                target = param["target"]
                if not isinstance(target, list) or len(target) < 2:
                    errors.append(f"Parameter {i}: invalid target structure")
                else:
                    target_type = target[0]
                    if target_type not in ["variable", "dimension", "text-tag"]:
                        errors.append(f"Parameter {i}: invalid target type '{target_type}'")
                    
                    # Validate target format based on type
                    if target_type in ["variable", "dimension"]:
                        if len(target) < 2 or not isinstance(target[1], list) or len(target[1]) < 2:
                            errors.append(f"Parameter {i}: invalid {target_type} target format")
                        elif target[1][0] != "template-tag":
                            errors.append(f"Parameter {i}: {target_type} target must reference template-tag")
                    elif target_type == "text-tag":
                        if len(target) < 2 or not isinstance(target[1], str):
                            errors.append(f"Parameter {i}: invalid text-tag target format")
            
            # Validate required parameters have defaults
            if param.get("required") is True:
                default = param.get("default")
                if default is None or default == "" or (isinstance(default, list) and len(default) == 0):
                    errors.append(f"Parameter {i}: required parameter must have a non-empty default value")
            
            # Validate parameter type specific constraints
            param_type = param.get("type", "")
            
            # Validate isMultiSelect constraints for string types
            if "isMultiSelect" in param and param["isMultiSelect"] is True:
                if param_type in ["string/contains", "string/does-not-contain", "string/starts-with", "string/ends-with"]:
                    errors.append(f"Parameter {i}: isMultiSelect cannot be true for type '{param_type}'")
            
            # Validate temporal_units for temporal-unit parameters
            if param_type == "temporal-unit":
                if "temporal_units" not in param or not isinstance(param["temporal_units"], list) or len(param["temporal_units"]) == 0:
                    errors.append(f"Parameter {i}: temporal-unit parameter must have non-empty temporal_units array")
                
        if errors:
            return False, errors
            
        return True, []
        
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
            "usage": {
                "new_parameters": "For new parameters, omit the 'id' field - it will be auto-generated",
                "existing_parameters": "For updating existing parameters, include the existing 'id' from the current card",
                "required_fields": ["name", "type"],
                "auto_generated_fields": ["id (for new)", "slug (always)", "target (if not specified)"],
                "slug_generation": "Slugs are automatically generated from parameter names - do not specify manually"
            },
            "examples": [
                {
                    "name": "Order Status",
                    "type": "category",
                    "default": "pending"
                },
                {
                    "name": "Date Range",
                    "type": "date/all-options",
                    "default": "past30days"
                },
                {
                    "id": "existing-param-id",
                    "name": "Updated Filter",
                    "type": "string/=",
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
        
        # Generate target if not provided
        if "target" not in processed_param:
            slug = processed_param.get("slug", "parameter")
            # Default to variable target
            processed_param["target"] = ["variable", ["template-tag", slug]]
        
        # Track existing IDs
        existing_ids.add(processed_param["id"])
        processed_parameters.append(processed_param)
    
    return processed_parameters
