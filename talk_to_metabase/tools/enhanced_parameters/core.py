"""
Enhanced card parameters implementation for Metabase MCP server.

This module provides comprehensive card parameter support including:
- Simple filters (category, number, date) 
- Field filters (string, numeric, date field filters)
- Automatic template tag generation
- UI widget configuration
- Value source management
"""

import json
import logging
import uuid
from typing import Dict, List, Tuple, Any, Optional, Union

import jsonschema
from mcp.server.fastmcp import Context

from ...server import get_server_instance
from ...resources import load_enhanced_card_parameters_schema, load_enhanced_card_parameters_docs
from ..common import format_error_response, get_metabase_client, check_response_size

logger = logging.getLogger(__name__)

# Register tools with the server
mcp = get_server_instance()

# Parameter type mappings
SIMPLE_PARAMETER_TYPES = {
    "category": "text",      # Maps to text template tag
    "number/=": "number",    # Maps to number template tag  
    "date/single": "date"    # Maps to date template tag
}

FIELD_FILTER_TYPES = {
    "string/=", "string/!=", "string/contains", "string/does-not-contain",
    "string/starts-with", "string/ends-with",
    "number/!=", "number/between", "number/>=", "number/<=", 
    "date/range", "date/relative", "date/all-options", "date/month-year", "date/quarter-year"
}

# UI widget mappings
UI_WIDGET_MAPPINGS = {
    "input": "none",
    "dropdown": "list", 
    "search": "search"
}


# Use the imported functions directly instead of creating wrapper functions
# load_enhanced_parameters_schema = load_enhanced_card_parameters_schema
# load_enhanced_parameters_docs = load_enhanced_card_parameters_docs


def generate_parameter_id() -> str:
    """Generate a unique UUID for parameter linking."""
    return str(uuid.uuid4())


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


def is_field_filter_parameter(param_type: str) -> bool:
    """Check if parameter type is a field filter."""
    return param_type in FIELD_FILTER_TYPES


def resolve_field_reference(field_config: Dict[str, Any]) -> List[Any]:
    """
    Convert field configuration to Metabase field reference format.
    
    Args:
        field_config: Field configuration with database_id, table_id, field_id
        
    Returns:
        Metabase field reference array: ["field", field_id, None]
    """
    return ["field", field_config["field_id"], None]


def get_parameter_target(param_name: str, is_field_filter: bool) -> List[Any]:
    """
    Generate parameter target based on parameter type.
    
    Args:
        param_name: Parameter name (used as template tag name)
        is_field_filter: Whether this is a field filter parameter
        
    Returns:
        Parameter target array
    """
    if is_field_filter:
        return ["dimension", ["template-tag", param_name]]
    else:
        return ["variable", ["template-tag", param_name]]


def convert_ui_widget_to_values_query_type(ui_widget: Optional[str]) -> str:
    """
    Convert UI widget specification to Metabase values_query_type.
    
    Args:
        ui_widget: UI widget type ("input", "dropdown", "search")
        
    Returns:
        Metabase values_query_type ("none", "list", "search")
    """
    if ui_widget is None:
        return "none"
    return UI_WIDGET_MAPPINGS.get(ui_widget, "none")


def build_values_source_config(values_source: Optional[Dict[str, Any]], field_config: Optional[Dict[str, Any]] = None) -> Tuple[Optional[str], Optional[Dict[str, Any]]]:
    """
    Build Metabase values_source_type and values_source_config from enhanced configuration.
    
    Args:
        values_source: Enhanced values source configuration
        field_config: Field configuration for connected field filters
        
    Returns:
        Tuple of (values_source_type, values_source_config)
    """
    if not values_source:
        return None, None
    
    source_type = values_source["type"]
    
    if source_type == "static":
        values = values_source["values"]
        # For number dropdowns, Metabase expects arrays of arrays
        if isinstance(values, list) and len(values) > 0:
            # Check if first value is a number (indicates this is a number dropdown)
            if isinstance(values[0], (int, float)):
                # Convert numbers to arrays of strings for Metabase format
                formatted_values = [[str(val)] for val in values]
            else:
                # String values - keep as is
                formatted_values = values
        else:
            formatted_values = values
            
        return "static-list", {
            "values": formatted_values
        }
    elif source_type == "card":
        config = {
            "card_id": values_source["card_id"],
            "value_field": ["field", values_source["value_field"], {"base-type": "type/Text"}]
        }
        if "label_field" in values_source:
            config["label_field"] = ["field", values_source["label_field"], {"base-type": "type/Text"}]
        return "card", config
    elif source_type == "connected" and field_config:
        # For connected field filters, use null values_source_type and empty config
        # This tells Metabase to use the field's values directly
        return None, {}
    
    return None, None


def create_template_tag(param_name: str, param_type: str, param_config: Dict[str, Any], param_id: str) -> Dict[str, Any]:
    """
    Create template tag from parameter configuration.
    
    Args:
        param_name: Parameter name
        param_type: Parameter type
        param_config: Full parameter configuration
        param_id: Parameter UUID
        
    Returns:
        Template tag dictionary
    """
    # Determine template tag type
    if param_type in SIMPLE_PARAMETER_TYPES:
        tag_type = SIMPLE_PARAMETER_TYPES[param_type]
        template_tag = {
            "type": tag_type,
            "name": param_name,
            "id": param_id,
            "display-name": param_config.get("display_name", param_name)
        }
    else:
        # Field filter parameter
        template_tag = {
            "type": "dimension", 
            "name": param_name,
            "id": param_id,
            "display-name": param_config.get("display_name", param_name),
            "dimension": resolve_field_reference(param_config["field"]),
            "widget-type": param_type
        }
    
    # Add default value if provided with special handling for number dropdowns
    if "default" in param_config and param_config["default"] is not None:
        default_value = param_config["default"]
        
        # Check if this is a number parameter with dropdown
        is_number_dropdown = (
            param_type == "number/=" and 
            param_config.get("ui_widget") == "dropdown" and
            param_config.get("values_source", {}).get("type") == "static"
        )
        
        if is_number_dropdown and not isinstance(default_value, list):
            # Convert single number to array format for dropdowns
            template_tag["default"] = [str(default_value)]
        else:
            template_tag["default"] = default_value
    
    # Add required flag if provided
    if "required" in param_config:
        template_tag["required"] = param_config["required"]
    
    return template_tag


def process_single_parameter(param_config: Dict[str, Any], param_id: str) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    """
    Process a single parameter configuration into Metabase API format.
    
    Args:
        param_config: Enhanced parameter configuration
        param_id: Generated parameter UUID
        
    Returns:
        Tuple of (processed_parameter, template_tag)
    """
    param_name = param_config["name"]
    param_type = param_config["type"]
    is_field_filter = is_field_filter_parameter(param_type)
    
    # Build the processed parameter
    processed_param = {
        "id": param_id,
        "type": param_type,
        "target": get_parameter_target(param_name, is_field_filter),
        "name": param_config.get("display_name", param_name),
        "slug": generate_slug(param_name)
    }
    
    # Handle default value with special formatting for number dropdowns
    if "default" in param_config:
        default_value = param_config["default"]
        
        # Check if this is a number parameter with dropdown
        is_number_dropdown = (
            param_type == "number/=" and 
            param_config.get("ui_widget") == "dropdown" and
            param_config.get("values_source", {}).get("type") == "static"
        )
        
        if is_number_dropdown and not isinstance(default_value, list):
            # Convert single number to array format for dropdowns
            processed_param["default"] = [str(default_value)]
        else:
            processed_param["default"] = default_value
    
    # Add required flag if provided
    if "required" in param_config:
        processed_param["required"] = param_config["required"]
    
    # Handle values source configuration
    values_source = param_config.get("values_source")
    field_config = param_config.get("field")
    
    # Convert UI widget to values_query_type
    ui_widget = param_config.get("ui_widget")
    values_query_type = convert_ui_widget_to_values_query_type(ui_widget)
    processed_param["values_query_type"] = values_query_type
    
    # Build values source config if needed
    if values_query_type in ["list", "search"]:
        values_source_type, values_source_config = build_values_source_config(values_source, field_config)
        if values_source_type is not None:
            processed_param["values_source_type"] = values_source_type
        if values_source_config is not None:
            processed_param["values_source_config"] = values_source_config
    
    # Create corresponding template tag
    template_tag = create_template_tag(param_name, param_type, param_config, param_id)
    
    return processed_param, template_tag


async def validate_field_references(client, parameters: List[Dict[str, Any]]) -> List[str]:
    """
    Validate that field references in parameters exist in the database.
    
    Args:
        client: Metabase client
        parameters: List of parameter configurations
        
    Returns:
        List of validation error messages
    """
    errors = []
    
    for i, param in enumerate(parameters):
        if "field" not in param:
            continue
            
        field_config = param["field"]
        database_id = field_config["database_id"]
        table_id = field_config["table_id"] 
        field_id = field_config["field_id"]
        
        try:
            # Check if the field exists by trying to get table metadata
            data, status, error = await client.auth.make_request(
                "GET", f"table/{table_id}/query_metadata"
            )
            
            if error:
                errors.append(f"Parameter {i} ({param['name']}): Cannot access table {table_id} in database {database_id}")
                continue
            
            # Check if the field exists in the table
            fields = data.get("fields", [])
            field_exists = any(field.get("id") == field_id for field in fields)
            
            if not field_exists:
                errors.append(f"Parameter {i} ({param['name']}): Field {field_id} not found in table {table_id}")
                
        except Exception as e:
            errors.append(f"Parameter {i} ({param['name']}): Error validating field reference - {str(e)}")
    
    return errors


def validate_parameter_widget_compatibility(parameters: List[Dict[str, Any]]) -> List[str]:
    """
    Validate that UI widgets are compatible with parameter types.
    
    Args:
        parameters: List of parameter configurations
        
    Returns:
        List of validation error messages
    """
    errors = []
    
    for i, param in enumerate(parameters):
        param_type = param["type"]
        ui_widget = param.get("ui_widget")
        
        # Check widget compatibility
        if ui_widget == "search" and param_type not in ["category", "string/contains", "string/starts-with", "string/ends-with"]:
            errors.append(f"Parameter {i} ({param['name']}): Search widget not compatible with type '{param_type}'")
        
        if ui_widget == "dropdown" and param_type.startswith("date/") and param_type != "date/single":
            errors.append(f"Parameter {i} ({param['name']}): Dropdown widget not compatible with date field filter type '{param_type}'")
    
    return errors


def validate_enhanced_parameters(parameters: List[Dict[str, Any]]) -> Tuple[bool, List[str]]:
    """
    Validate enhanced parameters against schema and business rules.
    
    Args:
        parameters: List of enhanced parameter configurations
        
    Returns:
        Tuple of (is_valid, error_messages)
    """
    schema = load_enhanced_card_parameters_schema()
    if schema is None:
        return False, ["Could not load enhanced parameters schema"]
    
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
        
        # Check widget compatibility
        widget_errors = validate_parameter_widget_compatibility(parameters)
        errors.extend(widget_errors)
        
        # Check required parameters have default values
        for i, param in enumerate(parameters):
            if param.get("required", False) and ("default" not in param or param["default"] is None):
                errors.append(f"Parameter {i} ({param.get('name', 'unnamed')}): required parameters must have a default value")
        
        return len(errors) == 0, errors
        
    except jsonschema.ValidationError as e:
        # Provide more helpful error messages
        error_path = " -> ".join(str(p) for p in e.path) if e.path else "root"
        return False, [f"Validation error at {error_path}: {e.message}"]
    except jsonschema.SchemaError as e:
        return False, [f"Schema error: {e.message}"]
    except Exception as e:
        return False, [f"Unexpected validation error: {str(e)}"]


async def process_enhanced_parameters(client, parameters: List[Dict[str, Any]]) -> Tuple[List[Dict[str, Any]], Dict[str, Any], List[str]]:
    """
    Process enhanced parameters into Metabase API format with validation.
    
    Args:
        client: Metabase client for field validation
        parameters: List of enhanced parameter configurations
        
    Returns:
        Tuple of (processed_parameters, template_tags, errors)
    """
    # Basic validation first
    is_valid, validation_errors = validate_enhanced_parameters(parameters)
    if not is_valid:
        return [], {}, validation_errors
    
    # Validate field references
    field_errors = await validate_field_references(client, parameters)
    if field_errors:
        return [], {}, field_errors
    
    # Process parameters
    processed_parameters = []
    template_tags = {}
    
    for param_config in parameters:
        param_id = generate_parameter_id()
        processed_param, template_tag = process_single_parameter(param_config, param_id)
        
        processed_parameters.append(processed_param)
        template_tags[template_tag["name"]] = template_tag
    
    return processed_parameters, template_tags, []


@mcp.tool(name="GET_ENHANCED_CARD_PARAMETERS_DOCUMENTATION", description="Get comprehensive documentation for enhanced card parameters")
async def get_enhanced_card_parameters_documentation(ctx: Context) -> str:
    """
    Get comprehensive documentation for enhanced card parameters including:
    - Simple filters (category, number, date)
    - Field filters (string, numeric, date field filters)  
    - UI widget options and their API values
    - Value source configuration
    - Complete examples for all parameter types
    
    Args:
        ctx: MCP context
        
    Returns:
        Complete documentation and examples as JSON string
    """
    logger.info("Tool called: GET_ENHANCED_CARD_PARAMETERS_DOCUMENTATION()")
    
    try:
        schema = load_enhanced_card_parameters_schema()
        docs = load_enhanced_card_parameters_docs()
        
        if schema is None:
            return format_error_response(
                status_code=500,
                error_type="schema_loading_error",
                message="Could not load enhanced card parameters JSON schema",
                request_info={"schema_file": "enhanced_card_parameters.json"}
            )
        
        if docs is None:
            return format_error_response(
                status_code=500,
                error_type="docs_loading_error", 
                message="Could not load enhanced card parameters documentation",
                request_info={"docs_file": "enhanced_card_parameters_docs.md"}
            )
        
        response_data = {
            "success": True,
            "documentation": docs,
            "schema": schema,
            "parameter_types": {
                "simple_filters": {
                    "category": "Text input with autocomplete and dropdown options",
                    "number/=": "Number input with dropdown options",
                    "date/single": "Single date picker"
                },
                "field_filters": {
                    "string_filters": [
                        "string/=", "string/!=", "string/contains", 
                        "string/does-not-contain", "string/starts-with", "string/ends-with"
                    ],
                    "numeric_filters": [
                        "number/=", "number/!=", "number/between", 
                        "number/>=", "number/<="
                    ],
                    "date_filters": [
                        "date/single", "date/range", "date/relative", 
                        "date/all-options", "date/month-year", "date/quarter-year"
                    ]
                }
            },
            "ui_widgets": {
                "input": "Free input (maps to values_query_type: 'none')",
                "dropdown": "Select from list (maps to values_query_type: 'list')", 
                "search": "Search with suggestions (maps to values_query_type: 'search')"
            },
            "value_sources": {
                "static": "Predefined list of values",
                "card": "Values from another card/model",
                "connected": "Values from connected database field (field filters only)"
            },
            "usage_notes": [
                "CRITICAL: NEVER add quotes around parameters - they substitute with proper formatting automatically",
                "Simple variables like {{text_param}} become 'value' (quotes included automatically)", 
                "Field filters like {{field_filter}} become true/false (boolean conditions)",
                "All UUIDs, template tags, targets, and slugs are generated automatically",
                "Parameter names must start with a letter and contain only letters, numbers, and underscores",
                "Field references are validated against the database",
                "UI widgets are validated for compatibility with parameter types",
                "Use parameter names in SQL queries as {{parameter_name}} or [[AND condition = {{parameter_name}}]]"
            ],
            "common_mistakes": {
                "quoted_parameters": {
                    "wrong": "WHERE status = '{{order_status}}'",
                    "correct": "WHERE status = {{order_status}}",
                    "explanation": "Parameters include quotes automatically for text values"
                },
                "case_when_quotes": {
                    "wrong": "CASE WHEN '{{metric_type}}' = 'spend' THEN spend",
                    "correct": "CASE WHEN {{metric_type}} = 'spend' THEN spend", 
                    "explanation": "Remove quotes around parameters in CASE WHEN statements"
                },
                "field_filter_as_value": {
                    "wrong": "WHERE customer_name = {{customer_filter}}",
                    "correct": "WHERE {{customer_filter}}",
                    "explanation": "Field filters are boolean conditions, not values"
                }
            }
        }
        
        # Convert to JSON string
        response = json.dumps(response_data, indent=2)
        
        # Check response size
        metabase_ctx = ctx.request_context.lifespan_context
        config = metabase_ctx.auth.config
        return check_response_size(response, config)
        
    except Exception as e:
        logger.error(f"Error in GET_ENHANCED_CARD_PARAMETERS_DOCUMENTATION: {e}")
        return format_error_response(
            status_code=500,
            error_type="tool_error",
            message=f"Error retrieving enhanced card parameters documentation: {str(e)}",
            request_info={}
        )


def validate_enhanced_parameters_helper(parameters: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Helper function to validate enhanced parameters and return structured result.
    
    Args:
        parameters: List of enhanced parameter configurations
        
    Returns:
        Dictionary with validation results
    """
    is_valid, errors = validate_enhanced_parameters(parameters)
    
    return {
        "valid": is_valid,
        "errors": errors,
        "parameters_count": len(parameters) if parameters else 0,
        "validation_type": "enhanced_parameters"
    }
