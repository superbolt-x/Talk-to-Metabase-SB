"""
Visualization documentation and validation tools for Metabase MCP server.
"""

import json
import logging
from typing import Dict, List, Tuple, Any, Optional

import jsonschema
from mcp.server.fastmcp import Context

from ..server import get_server_instance
from ..resources import load_visualization_schema, load_visualization_docs
from .common import format_error_response, check_response_size

logger = logging.getLogger(__name__)

# Register tools with the server
mcp = get_server_instance()

# Supported chart types (using API names)
SUPPORTED_CHART_TYPES = ["table", "line", "bar", "combo", "pie", "row", "area", "object", "funnel", "gauge", "progress", "sankey", "scalar", "scatter", "smartscalar", "map", "waterfall"]

# Mapping of common UI names to API names
UI_TO_API_MAPPING = {
    "detail": "object",
    "number": "scalar",
    "trend": "smartscalar",
}

# Mapping of API names to UI names for documentation
API_TO_UI_MAPPING = {
    "object": "detail",
    "scalar": "number",
    "smartscalar": "trend",
}

def load_schema(chart_type: str) -> Optional[Dict[str, Any]]:
    """Load JSON schema for a specific chart type."""
    try:
        # Convert UI name to API name if needed
        api_chart_type = UI_TO_API_MAPPING.get(chart_type, chart_type)
        
        # Use the resource utility to load the schema
        return load_visualization_schema(api_chart_type)
    except Exception as e:
        logger.error(f"Error loading schema for {chart_type}: {e}")
        return None

def load_documentation(chart_type: str) -> Optional[str]:
    """Load documentation for a specific chart type."""
    try:
        # Convert UI name to API name if needed
        api_chart_type = UI_TO_API_MAPPING.get(chart_type, chart_type)
        
        # Use the resource utility to load the documentation
        return load_visualization_docs(api_chart_type)
    except Exception as e:
        logger.error(f"Error loading documentation for {chart_type}: {e}")
        return None

def validate_visualization_settings(chart_type: str, settings: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """
    Validate visualization settings against the JSON schema.
    
    Args:
        chart_type: Type of chart (UI name or API name)
        settings: Visualization settings dictionary
        
    Returns:
        Tuple of (is_valid, error_messages)
    """
    # Convert UI name to API name if needed
    api_chart_type = UI_TO_API_MAPPING.get(chart_type, chart_type)
    
    if api_chart_type not in SUPPORTED_CHART_TYPES:
        supported_types = SUPPORTED_CHART_TYPES + list(UI_TO_API_MAPPING.keys())
        return False, [f"Unsupported chart type: {chart_type}. Supported types: {', '.join(supported_types)}"]
    
    schema = load_schema(api_chart_type)
    if schema is None:
        return False, [f"Could not load schema for chart type: {chart_type}"]
    
    try:
        jsonschema.validate(settings, schema)
        return True, []
    except jsonschema.ValidationError as e:
        return False, [f"Validation error: {e.message}"]
    except jsonschema.SchemaError as e:
        return False, [f"Schema error: {e.message}"]
    except Exception as e:
        return False, [f"Unexpected validation error: {str(e)}"]

@mcp.tool(name="GET_VISUALIZATION_DOCUMENT", description="IMPORTANT: Get visualization settings documentation - Call before creating/editing card visualization settings")
async def get_visualization_document(chart_type: str, ctx: Context) -> str:
    """
    **IMPORTANT: Call this tool before creating or editing visualization settings**
    
    Get comprehensive documentation and examples for visualization settings of a specific chart type.
    
    This tool provides:
    - Complete documentation for all available settings
    - JSON schema for validation
    - Practical examples and common patterns
    - Best practices and tips
    
    Currently supported chart types:
    - table: Data tables with formatting, conditional formatting, and click behaviors
    - line: Line charts with series settings, axes configuration, and trend lines
    - bar: Bar charts with stacking, series configuration, and value labels
    - combo: Combination charts mixing lines, bars, and areas with dual axes
    - pie: Pie charts with slice customization, legends, and percentage displays
    - row: Horizontal bar charts with category management and goal lines
    - area: Area charts with stacking, series blending, and trend visualization
    - object: Object detail views for displaying single record information (UI name: detail)
    - funnel: Funnel charts for conversion analysis with stage progression
    - gauge: Gauge charts for single KPI display with color-coded segments
    - progress: Progress bars showing completion toward a goal
    - sankey: Sankey diagrams for visualizing flow between nodes
    - scalar: Single number displays with formatting (UI name: number)
    - scatter: Scatter plots for analyzing relationships between two variables
    - smartscalar: Trend numbers with comparison values and indicators (UI name: trend)
    - map: Geographic maps for location-based data visualization
    - waterfall: Waterfall charts for showing cumulative effects of sequential changes
    
    Note: Some chart types have different names in the Metabase UI vs API.
    Both names are supported - use either the API name (e.g., "scalar") or UI name (e.g., "number").
    
    Args:
        chart_type: Type of chart visualization. Supports API names ("table", "line", "bar", "combo", "pie", "row", "area", "object", "funnel", "gauge", "progress", "sankey", "scalar", "scatter", "smartscalar", "map", "waterfall") and UI names ("detail" for "object", "number" for "scalar", "trend" for "smartscalar")
        ctx: MCP context
        
    Returns:
        Comprehensive documentation and schema for the requested chart type
    """
    logger.info(f"Tool called: GET_VISUALIZATION_DOCUMENT(chart_type={chart_type})")
    
    try:
        # Validate chart type
        api_chart_type = UI_TO_API_MAPPING.get(chart_type, chart_type)
        if api_chart_type not in SUPPORTED_CHART_TYPES:
            supported_types = SUPPORTED_CHART_TYPES + list(UI_TO_API_MAPPING.keys())
            return format_error_response(
                status_code=400,
                error_type="unsupported_chart_type",
                message=f"Chart type '{chart_type}' is not supported. Supported types: {', '.join(sorted(supported_types))}",
                request_info={"chart_type": chart_type, "supported_types": sorted(supported_types)}
            )
        
        # Load documentation
        documentation = load_documentation(chart_type)
        if documentation is None:
            return format_error_response(
                status_code=500,
                error_type="documentation_loading_error",
                message=f"Could not load documentation for chart type: {chart_type}",
                request_info={"chart_type": chart_type}
            )
        
        # Load schema
        schema = load_schema(chart_type)
        if schema is None:
            return format_error_response(
                status_code=500,
                error_type="schema_loading_error",
                message=f"Could not load JSON schema for chart type: {chart_type}",
                request_info={"chart_type": chart_type}
            )
        
        # Extract examples from schema
        examples = schema.get("examples", [])
        
        # Create response
        ui_name = API_TO_UI_MAPPING.get(api_chart_type, api_chart_type)
        response_data = {
            "success": True,
            "chart_type": chart_type,
            "api_name": api_chart_type,
            "ui_name": ui_name,
            "documentation": documentation,
            "json_schema": schema,
            "examples": examples,
            "validation_info": {
                "use_validate_visualization_settings": "Call validate_visualization_settings() before using settings in create_card or update_card",
                "supported_properties": list(schema.get("properties", {}).keys()) if "properties" in schema else [],
                "note": f"This chart type uses API name '{api_chart_type}' and UI name '{ui_name}'"
            }
        }
        
        logger.info(f"Documentation provided successfully for chart type: {chart_type}")
        
        # Convert to JSON string
        response = json.dumps(response_data, indent=2)
        
        # Check response size
        metabase_ctx = ctx.request_context.lifespan_context
        config = metabase_ctx.auth.config
        return check_response_size(response, config)
        
    except Exception as e:
        logger.error(f"Error in GET_VISUALIZATION_DOCUMENT: {e}")
        return format_error_response(
            status_code=500,
            error_type="tool_error",
            message=f"Error retrieving visualization documentation: {str(e)}",
            request_info={"chart_type": chart_type}
        )

def validate_visualization_settings_helper(chart_type: str, settings: Dict[str, Any]) -> Dict[str, Any]:
    """
    Helper function to validate visualization settings and return structured result.
    
    Args:
        chart_type: Type of chart (e.g., "table")
        settings: Visualization settings dictionary
        
    Returns:
        Dictionary with validation results
    """
    is_valid, errors = validate_visualization_settings(chart_type, settings)
    
    return {
        "valid": is_valid,
        "errors": errors,
        "chart_type": chart_type,
        "settings_provided": bool(settings),
        "validation_timestamp": "2025-06-06T00:00:00Z"  # Current timestamp would be better in real implementation
    }
