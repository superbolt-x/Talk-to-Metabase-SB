"""
Enhanced dashboard parameters implementation for Metabase MCP server.

This module provides comprehensive dashboard parameter support including:
- All dashboard parameter types (string, number, date, temporal-unit, location, ID)
- Multi-select support where applicable
- Automatic ID generation and slug creation
- UI widget configuration  
- Value source management (static, card, connected)
- Comprehensive validation
"""

import json
import logging
import random
import string
from typing import Dict, List, Tuple, Any, Optional, Union

import jsonschema
from mcp.server.fastmcp import Context

from ..server import get_server_instance
from ..resources import load_json_resource, load_text_resource
from .common import format_error_response, get_metabase_client, check_response_size

logger = logging.getLogger(__name__)

# Register tools with the server
mcp = get_server_instance()

# Dashboard parameter type categories
TEXT_PARAMETER_TYPES = {
    "string/=", "string/!=", "string/contains", "string/does-not-contain",
    "string/starts-with", "string/ends-with"
}

LOCATION_PARAMETER_TYPES = {
    "location/=", "location/!=", "location/contains", "location/does-not-contain",
    "location/starts-with", "location/ends-with"
}

NUMBER_PARAMETER_TYPES = {
    "number/=", "number/!=", "number/between", "number/>=", "number/<="
}

DATE_PARAMETER_TYPES = {
    "date/single", "date/range", "date/month-year", "date/quarter-year", 
    "date/relative", "date/all-options"
}

# Parameter types that support multi-select
MULTI_SELECT_SUPPORTED = {
    "string/=", "string/!=", "string/contains", "string/does-not-contain",
    "string/starts-with", "string/ends-with", "number/=", "number/!=", "id",
    "location/=", "location/!=", "location/contains", "location/does-not-contain",
    "location/starts-with", "location/ends-with"
}

# Parameter types that do NOT support multi-select
MULTI_SELECT_FORBIDDEN = {
    "date/single", "date/range", "date/month-year", "date/quarter-year", 
    "date/relative", "date/all-options", "temporal-unit", "number/between", "number/>=", "number/<="
}

# Valid temporal units for temporal-unit parameters
VALID_TEMPORAL_UNITS = {
    "minute", "hour", "day", "week", "month", "quarter", "year",
    "minute-of-hour", "hour-of-day", "day-of-week", "day-of-month",
    "day-of-year", "week-of-year", "month-of-year", "quarter-of-year"
}

# Section ID mappings based on parameter type
SECTION_ID_MAPPINGS = {
    # String parameters
    "string/=": "string",
    "string/!=": "string", 
    "string/contains": "string",
    "string/does-not-contain": "string",
    "string/starts-with": "string",
    "string/ends-with": "string",
    
    # Location parameters (translate to string types with location sectionId)
    "location/=": "location",
    "location/!=": "location",
    "location/contains": "location",
    "location/does-not-contain": "location",
    "location/starts-with": "location",
    "location/ends-with": "location",
    
    # Number parameters
    "number/=": "number",
    "number/!=": "number",
    "number/between": "number", 
    "number/>=": "number",
    "number/<=": "number",
    
    # Date parameters
    "date/single": "date",
    "date/range": "date",
    "date/month-year": "date",
    "date/quarter-year": "date",
    "date/relative": "date",
    "date/all-options": "date",
    
    # Special parameters
    "temporal-unit": "temporal-unit",
    "id": "id"
}

# Location parameter to string parameter mapping
LOCATION_TO_STRING_MAPPING = {
    "location/=": "string/=",
    "location/!=": "string/!=",
    "location/contains": "string/contains",
    "location/does-not-contain": "string/does-not-contain",
    "location/starts-with": "string/starts-with",
    "location/ends-with": "string/ends-with"
}


def load_enhanced_dashboard_parameters_schema() -> Optional[Dict[str, Any]]:
    """Load the enhanced dashboard parameters JSON schema."""
    return load_json_resource("schemas/enhanced_dashboard_parameters.json")


def generate_parameter_id() -> str:
    """
    Generate a unique 8-character alphanumeric parameter ID for dashboard parameters.
    
    Returns:
        8-character alphanumeric string
    """
    # Generate 8-character alphanumeric ID (letters and numbers)
    return ''.join(random.choices(string.ascii_letters + string.digits, k=8))


def generate_slug(name: str) -> str:
    """
    Generate a URL-friendly slug from parameter name.
    
    Args:
        name: Parameter name
        
    Returns:
        URL-friendly slug
    """
    import re
    # Convert to lowercase, replace non-alphanumeric with underscores
    slug = re.sub(r'[^a-zA-Z0-9]+', '_', name.lower().strip())
    # Remove leading/trailing underscores
    slug = slug.strip('_')
    # Ensure it's not empty
    if not slug:
        slug = "parameter"
    return slug


def determine_section_id(param_type: str, param_name: str, values_source: Optional[Dict[str, Any]] = None) -> str:
    """
    Determine the appropriate sectionId for a parameter type.
    
    Args:
        param_type: Parameter type
        param_name: Parameter name (unused, kept for compatibility)
        values_source: Optional values source (unused, kept for compatibility)
        
    Returns:
        Appropriate sectionId
    """
    return SECTION_ID_MAPPINGS.get(param_type, "string")


def validate_multi_select_compatibility(param_type: str, is_multi_select: Optional[bool]) -> List[str]:
    """
    Validate multi-select compatibility with parameter type.
    Note: isMultiSelect defaults to True for supported parameter types.
    
    Args:
        param_type: Parameter type
        is_multi_select: Whether multi-select is enabled (None means use default)
        
    Returns:
        List of validation errors
    """
    errors = []
    
    # Determine actual multi-select setting with defaults
    if param_type in MULTI_SELECT_SUPPORTED:
        actual_is_multi_select = is_multi_select if is_multi_select is not None else True
    else:
        actual_is_multi_select = is_multi_select if is_multi_select is not None else False
    
    # Only validate if multi-select is explicitly enabled for forbidden types
    if actual_is_multi_select and param_type in MULTI_SELECT_FORBIDDEN:
        errors.append(f"Multi-select not supported for parameter type '{param_type}'")
    
    return errors


def validate_temporal_units(temporal_units: List[str]) -> List[str]:
    """
    Validate temporal units for temporal-unit parameters.
    
    Args:
        temporal_units: List of temporal units
        
    Returns:
        List of validation errors
    """
    errors = []
    
    for unit in temporal_units:
        if unit not in VALID_TEMPORAL_UNITS:
            errors.append(f"Invalid temporal unit '{unit}'. Valid units: {sorted(VALID_TEMPORAL_UNITS)}")
    
    return errors


def validate_values_source_config(param_config: Dict[str, Any]) -> List[str]:
    """
    Validate values source configuration.
    
    Args:
        param_config: Parameter configuration
        
    Returns:
        List of validation errors
    """
    errors = []
    
    values_source = param_config.get("values_source")
    if not values_source:
        return errors
    
    source_type = values_source.get("type")
    
    if source_type == "static":
        if "values" not in values_source or not values_source["values"]:
            errors.append("Static values source requires non-empty 'values' array")
    elif source_type == "card":
        if "card_id" not in values_source:
            errors.append("Card values source requires 'card_id'")
        if "value_field" not in values_source:
            errors.append("Card values source requires 'value_field'")
    
    return errors


def validate_default_value_format(param_config: Dict[str, Any]) -> List[str]:
    """
    Validate default value format matches parameter type and multi-select setting.
    Note: isMultiSelect defaults to True for supported parameter types.
    
    Args:
        param_config: Parameter configuration
        
    Returns:
        List of validation errors
    """
    errors = []
    
    if "default" not in param_config or param_config["default"] is None:
        return errors
    
    param_type = param_config["type"]
    default_value = param_config["default"]
    
    # Determine if multi-select is enabled
    # For supported types, isMultiSelect defaults to True unless explicitly set to False
    if param_type in MULTI_SELECT_SUPPORTED:
        is_multi_select = param_config.get("isMultiSelect", True)  # Default to True
    else:
        is_multi_select = param_config.get("isMultiSelect", False)  # Default to False for unsupported types
    
    # For multi-select parameters, default should be an array
    if is_multi_select and not isinstance(default_value, list):
        errors.append(f"Multi-select parameter default value must be an array, got {type(default_value).__name__}")
    
    # Type-specific validation
    if param_type in NUMBER_PARAMETER_TYPES:
        if is_multi_select:
            if not isinstance(default_value, list) or not all(isinstance(v, (int, float)) for v in default_value):
                errors.append("Number parameter with multi-select requires array of numbers as default")
        elif param_type == "number/between":
            if not isinstance(default_value, list) or len(default_value) != 2:
                errors.append("number/between parameter requires array of two numbers as default")
        elif not isinstance(default_value, (int, float)):
            errors.append("Number parameter requires numeric default value")
    
    elif param_type in DATE_PARAMETER_TYPES:
        # Date parameters never support multi-select, so default should be string
        if not isinstance(default_value, str):
            errors.append("Date parameter requires string default value")
    
    elif param_type in TEXT_PARAMETER_TYPES or param_type in LOCATION_PARAMETER_TYPES or param_type == "id":
        if is_multi_select:
            if not isinstance(default_value, list):
                errors.append("Multi-select parameter default value must be an array")
            else:
                # For ID parameters, allow mixed string/number arrays
                if param_type == "id":
                    if not all(isinstance(v, (str, int, float)) for v in default_value):
                        errors.append("ID parameter with multi-select requires array of strings or numbers as default")
                else:
                    # For text parameters, require strings
                    if not all(isinstance(v, str) for v in default_value):
                        errors.append("Text parameter with multi-select requires array of strings as default")
        else:
            # For single values, ID parameters can be string or number
            if param_type == "id":
                if not isinstance(default_value, (str, int, float)):
                    errors.append("ID parameter requires string or number default value")
            else:
                # Text parameters require strings
                if not isinstance(default_value, str):
                    errors.append("Text parameter requires string default value")
    
    elif param_type == "temporal-unit":
        if not isinstance(default_value, str) or default_value not in VALID_TEMPORAL_UNITS:
            errors.append(f"temporal-unit parameter requires valid temporal unit as default. Valid units: {sorted(VALID_TEMPORAL_UNITS)}")
    
    return errors


def process_static_values(values: List[Any], param_type: str) -> List[List[str]]:
    """
    Process static values into Metabase format (array of arrays).
    
    Args:
        values: Raw values list
        param_type: Parameter type
        
    Returns:
        Formatted values as array of arrays
    """
    formatted_values = []
    
    for value in values:
        if isinstance(value, (int, float)):
            # Convert numbers to strings for Metabase format
            formatted_values.append([str(value)])
        else:
            # Keep as string
            formatted_values.append([str(value)])
    
    return formatted_values


def build_values_source_config(param_config: Dict[str, Any]) -> Tuple[Optional[str], Optional[Dict[str, Any]]]:
    """
    Build Metabase values_source_type and values_source_config.
    
    Args:
        param_config: Parameter configuration
        
    Returns:
        Tuple of (values_source_type, values_source_config)
    """
    values_source = param_config.get("values_source")
    if not values_source:
        return None, None
    
    source_type = values_source["type"]
    param_type = param_config["type"]
    
    if source_type == "static":
        values = values_source["values"]
        formatted_values = process_static_values(values, param_type)
        return "static-list", {"values": formatted_values}
    
    elif source_type == "card":
        config = {
            "card_id": values_source["card_id"],
            "value_field": ["field", values_source["value_field"], {"base-type": "type/Text"}]
        }
        if "label_field" in values_source:
            config["label_field"] = ["field", values_source["label_field"], {"base-type": "type/Text"}]
        return "card", config
    
    return None, None


def determine_values_query_type(param_config: Dict[str, Any]) -> str:
    """
    Determine values_query_type based on parameter configuration.
    
    Args:
        param_config: Parameter configuration
        
    Returns:
        Values query type ("none", "list", "search")
    """
    values_source = param_config.get("values_source")
    if not values_source:
        return "none"
    
    source_type = values_source["type"]
    
    if source_type == "static":
        return "list"
    elif source_type == "card":
        return "search"
    
    return "none"


def process_single_dashboard_parameter(param_config: Dict[str, Any], existing_ids: set) -> Dict[str, Any]:
    """
    Process a single dashboard parameter configuration into Metabase API format.
    
    Args:
        param_config: Enhanced parameter configuration
        existing_ids: Set of existing parameter IDs to avoid collisions
        
    Returns:
        Processed parameter in Metabase API format
    """
    param_name = param_config["name"]
    param_type = param_config["type"]
    
    # Generate ID if not provided
    param_id = param_config.get("id")
    if not param_id:
        param_id = generate_parameter_id()
        # Ensure uniqueness
        while param_id in existing_ids:
            param_id = generate_parameter_id()
    
    existing_ids.add(param_id)
    
    # Handle location parameter type translation
    if param_type in LOCATION_PARAMETER_TYPES:
        # Translate location/= to string/= but keep location sectionId
        actual_param_type = LOCATION_TO_STRING_MAPPING[param_type]
        section_id = "location"
    else:
        # Use original type and determine sectionId normally
        actual_param_type = param_type
        section_id = determine_section_id(param_type, param_name, param_config.get("values_source"))
    
    # Build the processed parameter
    processed_param = {
        "id": param_id,
        "name": param_name,
        "slug": generate_slug(param_name),
        "type": actual_param_type,
        "sectionId": section_id
    }
    
    # Add optional fields
    if "required" in param_config:
        processed_param["required"] = param_config["required"]
    
    if "default" in param_config and param_config["default"] is not None:
        processed_param["default"] = param_config["default"]
    
    if "isMultiSelect" in param_config:
        processed_param["isMultiSelect"] = param_config["isMultiSelect"]
    
    # Handle temporal units for temporal-unit parameters
    if param_type == "temporal-unit" and "temporal_units" in param_config:
        processed_param["temporal_units"] = param_config["temporal_units"]
    
    # Handle values source configuration
    values_query_type = determine_values_query_type(param_config)
    processed_param["values_query_type"] = values_query_type
    
    if values_query_type in ["list", "search"]:
        values_source_type, values_source_config = build_values_source_config(param_config)
        if values_source_type is not None:
            processed_param["values_source_type"] = values_source_type
        if values_source_config is not None:
            processed_param["values_source_config"] = values_source_config
    
    return processed_param


def validate_enhanced_dashboard_parameters(parameters: List[Dict[str, Any]]) -> Tuple[bool, List[str]]:
    """
    Validate enhanced dashboard parameters against schema and business rules.
    
    Args:
        parameters: List of enhanced parameter configurations
        
    Returns:
        Tuple of (is_valid, error_messages)
    """
    schema = load_enhanced_dashboard_parameters_schema()
    if schema is None:
        return False, ["Could not load enhanced dashboard parameters schema"]
    
    try:
        # JSON Schema validation handles most validation automatically
        jsonschema.validate(parameters, schema)
        
        # Additional business logic validation
        errors = []
        
        # Check for duplicate names
        seen_names = set()
        for i, param in enumerate(parameters):
            name = param.get("name")
            if name and name in seen_names:
                errors.append(f"Parameter {i}: duplicate name '{name}'")
            elif name:
                seen_names.add(name)
            
            # Check for reserved name 'tab'
            if name == "tab":
                errors.append(f"Parameter {i}: name 'tab' is reserved and cannot be used")
        
        # Validate each parameter individually
        for i, param in enumerate(parameters):
            param_name = param.get("name", f"parameter_{i}")
            param_type = param.get("type")
            
            # Multi-select validation
            is_multi_select = param.get("isMultiSelect")  # Get actual value, could be None
            multi_select_errors = validate_multi_select_compatibility(param_type, is_multi_select)
            for error in multi_select_errors:
                errors.append(f"Parameter {i} ({param_name}): {error}")
            
            # Temporal units validation
            if param_type == "temporal-unit":
                temporal_units = param.get("temporal_units", [])
                if not temporal_units:
                    errors.append(f"Parameter {i} ({param_name}): temporal-unit parameter requires non-empty temporal_units array")
                else:
                    temporal_errors = validate_temporal_units(temporal_units)
                    for error in temporal_errors:
                        errors.append(f"Parameter {i} ({param_name}): {error}")
            
            # Values source validation
            values_source_errors = validate_values_source_config(param)
            for error in values_source_errors:
                errors.append(f"Parameter {i} ({param_name}): {error}")
            
            # Default value format validation
            default_errors = validate_default_value_format(param)
            for error in default_errors:
                errors.append(f"Parameter {i} ({param_name}): {error}")
            
            # Required parameter validation
            if param.get("required", False):
                if "default" not in param or param["default"] is None:
                    errors.append(f"Parameter {i} ({param_name}): required parameters must have a default value")
                else:
                    # Check if default is empty based on multi-select behavior
                    default_value = param["default"]
                    
                    # Determine if this parameter uses multi-select by default
                    param_is_multi_select = param.get("isMultiSelect")
                    if param_type in MULTI_SELECT_SUPPORTED:
                        actual_is_multi_select = param_is_multi_select if param_is_multi_select is not None else True
                    else:
                        actual_is_multi_select = param_is_multi_select if param_is_multi_select is not None else False
                    
                    if actual_is_multi_select:
                        if isinstance(default_value, list) and len(default_value) == 0:
                            errors.append(f"Parameter {i} ({param_name}): required parameters must have a non-empty default value")
                    else:
                        if isinstance(default_value, str) and default_value == "":
                            errors.append(f"Parameter {i} ({param_name}): required parameters must have a non-empty default value")
        
        return len(errors) == 0, errors
        
    except jsonschema.ValidationError as e:
        # Provide more helpful error messages
        error_path = " -> ".join(str(p) for p in e.path) if e.path else "root"
        return False, [f"Validation error at {error_path}: {e.message}"]
    except jsonschema.SchemaError as e:
        return False, [f"Schema error: {e.message}"]
    except Exception as e:
        return False, [f"Unexpected validation error: {str(e)}"]


async def validate_card_references(client, parameters: List[Dict[str, Any]]) -> List[str]:
    """
    Validate that card references in values_source exist and are accessible.
    
    Args:
        client: Metabase client
        parameters: List of parameter configurations
        
    Returns:
        List of validation error messages
    """
    errors = []
    
    for i, param in enumerate(parameters):
        values_source = param.get("values_source")
        if not values_source or values_source.get("type") != "card":
            continue
        
        card_id = values_source.get("card_id")
        if not card_id:
            continue
        
        param_name = param.get("name", f"parameter_{i}")
        
        try:
            # Check if the card exists and is accessible
            data, status, error = await client.auth.make_request(
                "GET", f"card/{card_id}"
            )
            
            if error:
                errors.append(f"Parameter {i} ({param_name}): Cannot access card {card_id} for values source - {error}")
                continue
            
            # Verify the card has result metadata (has been run)
            if not data.get("result_metadata"):
                errors.append(f"Parameter {i} ({param_name}): Card {card_id} has no result metadata. Run the card first to use it as a values source.")
                continue
            
            # Check if the specified value_field exists
            value_field = values_source.get("value_field")
            if value_field:
                field_names = [field.get("name") for field in data.get("result_metadata", [])]
                if value_field not in field_names:
                    errors.append(f"Parameter {i} ({param_name}): Field '{value_field}' not found in card {card_id}. Available fields: {field_names}")
            
            # Check label_field if specified
            label_field = values_source.get("label_field")
            if label_field:
                field_names = [field.get("name") for field in data.get("result_metadata", [])]
                if label_field not in field_names:
                    errors.append(f"Parameter {i} ({param_name}): Label field '{label_field}' not found in card {card_id}. Available fields: {field_names}")
                    
        except Exception as e:
            errors.append(f"Parameter {i} ({param_name}): Error validating card reference {card_id} - {str(e)}")
    
    return errors


async def process_enhanced_dashboard_parameters(client, parameters: List[Dict[str, Any]]) -> Tuple[List[Dict[str, Any]], List[str]]:
    """
    Process enhanced dashboard parameters into Metabase API format with validation.
    
    Args:
        client: Metabase client for card validation
        parameters: List of enhanced parameter configurations
        
    Returns:
        Tuple of (processed_parameters, errors)
    """
    # Basic validation first
    is_valid, validation_errors = validate_enhanced_dashboard_parameters(parameters)
    if not is_valid:
        return [], validation_errors
    
    # Validate card references
    card_errors = await validate_card_references(client, parameters)
    if card_errors:
        return [], card_errors
    
    # Process parameters
    processed_parameters = []
    existing_ids = set()
    
    for param_config in parameters:
        processed_param = process_single_dashboard_parameter(param_config, existing_ids)
        processed_parameters.append(processed_param)
    
    return processed_parameters, []


def validate_enhanced_dashboard_parameters_helper(parameters: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Helper function to validate enhanced dashboard parameters and return structured result.
    
    Args:
        parameters: List of enhanced parameter configurations
        
    Returns:
        Dictionary with validation results
    """
    is_valid, errors = validate_enhanced_dashboard_parameters(parameters)
    
    return {
        "valid": is_valid,
        "errors": errors,
        "parameters_count": len(parameters) if parameters else 0,
        "validation_type": "enhanced_dashboard_parameters"
    }


@mcp.tool(name="GET_ENHANCED_DASHBOARD_PARAMETERS_DOCUMENTATION", description="Get complete schema and documentation for enhanced dashboard parameters")
async def get_enhanced_dashboard_parameters_documentation(ctx: Context) -> str:
    """
    Get complete schema and documentation for enhanced dashboard parameters.
    All documentation is embedded in the JSON schema.
    
    Args:
        ctx: MCP context
        
    Returns:
        JSON schema with embedded documentation
    """
    logger.info("Tool called: GET_ENHANCED_DASHBOARD_PARAMETERS_DOCUMENTATION()")
    
    try:
        schema = load_enhanced_dashboard_parameters_schema()
        
        if schema is None:
            return format_error_response(
                status_code=500,
                error_type="schema_loading_error",
                message="Could not load enhanced dashboard parameters JSON schema",
                request_info={"schema_file": "enhanced_dashboard_parameters.json"}
            )
        
        # Return the schema directly - all documentation is embedded
        response = json.dumps(schema, indent=2)
        
        # Check response size
        metabase_ctx = ctx.request_context.lifespan_context
        config = metabase_ctx.auth.config
        return check_response_size(response, config)
        
    except Exception as e:
        logger.error(f"Error in GET_ENHANCED_DASHBOARD_PARAMETERS_DOCUMENTATION: {e}")
        return format_error_response(
            status_code=500,
            error_type="tool_error",
            message=f"Error retrieving enhanced dashboard parameters documentation: {str(e)}",
            request_info={}
        )
