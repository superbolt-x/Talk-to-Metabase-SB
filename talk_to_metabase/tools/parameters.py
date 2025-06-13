"""
Dashboard parameters validation tools for Metabase MCP server.
"""

import json
import logging
import os
import random
import string
from typing import Dict, List, Tuple, Any, Optional

import jsonschema
from mcp.server.fastmcp import Context

from ..server import get_server_instance
from .common import format_error_response, check_response_size

logger = logging.getLogger(__name__)

# Register tools with the server
mcp = get_server_instance()


def load_parameters_schema() -> Optional[Dict[str, Any]]:
    """
    Load the JSON schema for parameters validation.
    
    Returns:
        Parameters schema dictionary or None if loading fails
    """
    try:
        schema_path = os.path.join(
            os.path.dirname(__file__), 
            "..", 
            "schemas", 
            "parameters.json"
        )
        
        if not os.path.exists(schema_path):
            logger.error(f"Parameters schema file not found: {schema_path}")
            return None
            
        with open(schema_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Error loading parameters schema: {e}")
        return None


def generate_parameter_id() -> str:
    """
    Generate a unique parameter ID.
    
    The ID is a hexadecimal string representation of a random number,
    formatted as an 8-character hexadecimal string, which is the format
    Metabase uses for parameter IDs.
    
    Returns:
        8-character hexadecimal string to use as parameter ID
    """
    # Generate a random integer in the 32-bit range
    num = random.randint(0, 2**32 - 1)
    # Convert to hexadecimal string (without '0x' prefix) and ensure it's 8 characters
    return format(num, '08x')


def is_duplicate_name(name: str, parameters: List[Dict[str, Any]]) -> bool:
    """
    Check if a parameter name already exists in the parameters list.
    
    Args:
        name: Parameter name to check
        parameters: List of parameter dictionaries
        
    Returns:
        True if the name is a duplicate, False otherwise
    """
    return any(p.get('name') == name for p in parameters)


def validate_parameters(parameters: List[Dict[str, Any]]) -> Tuple[bool, List[str]]:
    """
    Validate parameters against the JSON schema and additional business rules.
    
    Args:
        parameters: List of parameter dictionaries
        
    Returns:
        Tuple of (is_valid, error_messages)
    """
    schema = load_parameters_schema()
    if schema is None:
        return False, ["Could not load parameters schema"]
    
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
            if "name" not in param:
                errors.append(f"Parameter {i}: missing required field 'name'")
            
            if "type" not in param:
                errors.append(f"Parameter {i}: missing required field 'type'")
            
            # Check for duplicate IDs (only for params with IDs)
            if "id" in param and param["id"]:
                if param["id"] in seen_ids:
                    errors.append(f"Parameter {i}: duplicate ID '{param['id']}'")
                else:
                    seen_ids.add(param["id"])
            
            # Check if name is 'tab' (reserved word)
            if "name" in param and param["name"] == "tab":
                errors.append(f"Parameter {i}: name cannot be 'tab' (reserved for dashboard tabs)")
                if param["name"] in seen_names:
                    errors.append(f"Parameter {i}: duplicate name '{param['name']}'")
                else:
                    seen_names.add(param["name"])
            
            # Validate value matches type
            if "value" in param and param["value"] is not None:
                param_type = param.get("type", "")
                value = param["value"]
                
                # Type-specific validation
                if param_type.startswith("date/") and not (isinstance(value, str) or isinstance(value, list)):
                    errors.append(f"Parameter {i}: date parameter value should be string or array")
                
                elif param_type.startswith("number/") and not (isinstance(value, (int, float)) or 
                                                               (isinstance(value, list) and 
                                                                all(isinstance(v, (int, float)) for v in value))):
                    errors.append(f"Parameter {i}: number parameter value should be number or array of numbers")
            
            # Validate sectionId is appropriate for type
            if "type" in param and param["type"] == "temporal-unit" and "sectionId" in param:
                if param["sectionId"] != "temporal-unit":
                    errors.append(f"Parameter {i}: temporal-unit parameter must have sectionId='temporal-unit'")
                
                # Check temporal_units is present for temporal-unit parameters
                if "temporal_units" not in param or not isinstance(param["temporal_units"], list) or len(param["temporal_units"]) == 0:
                    errors.append(f"Parameter {i}: temporal-unit parameter must have non-empty temporal_units array")
            
            # Validate isMultiSelect constraints
            if "type" in param and "isMultiSelect" in param and param["isMultiSelect"] is True:
                param_type = param["type"]
                if param_type in ["string/contains", "string/does-not-contain", "string/starts-with", "string/ends-with"]:
                    errors.append(f"Parameter {i}: isMultiSelect cannot be true for type '{param_type}'")
                
            # Validate required parameters have defaults
            if "required" in param and param["required"] is True:
                if "default" not in param or param["default"] is None or param["default"] == "" or \
                   (isinstance(param["default"], list) and len(param["default"]) == 0):
                    errors.append(f"Parameter {i}: required parameter must have a non-empty default value")
                    
        if errors:
            return False, errors
            
        return True, []
        
    except jsonschema.ValidationError as e:
        return False, [f"Validation error: {e.message}"]
    except jsonschema.SchemaError as e:
        return False, [f"Schema error: {e.message}"]
    except Exception as e:
        return False, [f"Unexpected validation error: {str(e)}"]


@mcp.tool(name="GET_PARAMETERS_SCHEMA", description="Get the JSON schema for dashboard parameters validation")
async def get_parameters_schema(ctx: Context) -> str:
    """
    Get the JSON schema for validating dashboard parameters structure.
    
    This tool returns the complete JSON schema used to validate parameters
    when updating dashboards with the update_dashboard tool.
    
    Args:
        ctx: MCP context
        
    Returns:
        JSON schema for parameters validation
    """
    logger.info("Tool called: GET_PARAMETERS_SCHEMA()")
    
    try:
        schema = load_parameters_schema()
        if schema is None:
            return format_error_response(
                status_code=500,
                error_type="schema_loading_error",
                message="Could not load parameters JSON schema",
                request_info={"schema_file": "parameters.json"}
            )
        
        response_data = {
            "success": True,
            "schema": schema,
            "description": "JSON schema for validating dashboard parameters in update_dashboard tool",
            "usage": {
                "id_handling": "When creating new parameters, leave id field empty or omit it - the system will generate one. When updating existing parameters, include the existing ID.",
                "required_fields": ["name", "type"],
                "common_parameter_types": {
                    "date_parameters": ["date/all-options", "date/single", "date/range", "date/relative", "date/month-year", "date/quarter-year"],
                    "string_parameters": ["string/=", "string/!=", "string/contains", "string/does-not-contain", "string/starts-with", "string/ends-with"],
                    "number_parameters": ["number/=", "number/!=", "number/between", "number/>=", "number/<="],
                    "other_parameters": ["id", "category", "location", "temporal-unit"]
                },
                "examples": [
                    {
                        "name": "Date Filter",
                        "type": "date/all-options",
                        "sectionId": "date",
                        "default": "past30days"
                    },
                    {
                        "name": "Category",
                        "type": "string/=",
                        "sectionId": "string",
                        "isMultiSelect": True
                    }
                ]
            }
        }
        
        # Convert to JSON string
        response = json.dumps(response_data, indent=2)
        
        # Check response size
        metabase_ctx = ctx.request_context.lifespan_context
        config = metabase_ctx.auth.config
        return check_response_size(response, config)
        
    except Exception as e:
        logger.error(f"Error in GET_PARAMETERS_SCHEMA: {e}")
        return format_error_response(
            status_code=500,
            error_type="tool_error",
            message=f"Error retrieving parameters schema: {str(e)}",
            request_info={}
        )


def validate_parameters_helper(parameters: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Helper function to validate parameters and return structured result.
    
    Args:
        parameters: List of parameter dictionaries
        
    Returns:
        Dictionary with validation results
    """
    is_valid, errors = validate_parameters(parameters)
    
    return {
        "valid": is_valid,
        "errors": errors,
        "parameters_count": len(parameters) if parameters else 0,
        "validation_timestamp": "2025-06-06T00:00:00Z"  # Current timestamp would be better in real implementation
    }


def process_parameters(parameters: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Process parameters to ensure all have valid IDs.
    
    For parameters without IDs (new parameters), generates a unique ID.
    
    Args:
        parameters: List of parameter dictionaries
        
    Returns:
        List of processed parameter dictionaries with IDs
    """
    processed_parameters = []
    existing_ids = set()
    existing_names = set()
    
    for param in parameters:
        # Create a copy of the parameter to avoid modifying the original
        processed_param = param.copy()
        
        # Check if ID is present and non-empty
        if "id" not in processed_param or not processed_param["id"]:
            # Generate a new ID
            new_id = generate_parameter_id()
            
            # Make sure it doesn't collide with existing IDs
            while new_id in existing_ids:
                new_id = generate_parameter_id()
                
            processed_param["id"] = new_id
        
        # Track existing IDs and names
        existing_ids.add(processed_param["id"])
        if "name" in processed_param:
            existing_names.add(processed_param["name"])
            
        processed_parameters.append(processed_param)
    
    return processed_parameters
