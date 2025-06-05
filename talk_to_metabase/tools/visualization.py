"""
Visualization settings tools for Metabase MCP server.
"""

import json
import logging
from typing import List, Dict, Any, Optional, Union, Tuple

from mcp.server.fastmcp import Context

from ..server import get_server_instance
from .common import format_error_response, check_response_size

logger = logging.getLogger(__name__)

# Register tools with the server
mcp = get_server_instance()


def get_visualization_docs_for_types(chart_types: List[str]) -> Dict[str, Any]:
    """
    Get filtered visualization documentation for specific chart types.
    
    Args:
        chart_types: List of chart types to get documentation for
        
    Returns:
        Dictionary with filtered documentation content
    """
    # Common settings available for all chart types
    common_settings = {
        "description": "Settings available for all chart types",
        "settings": {
            "card.title": {
                "type": "string",
                "description": "Custom title for the card",
                "example": "Sales Performance Q4"
            },
            "card.description": {
                "type": "string", 
                "description": "Custom description for the card",
                "example": "Quarterly sales analysis with regional breakdown"
            },
            "card.hide_empty": {
                "type": "boolean",
                "description": "Hide the card when it has no data",
                "default": False
            },
            "click_behavior": {
                "type": "object",
                "description": "Configure click behavior for chart elements",
                "properties": {
                    "type": {
                        "enum": ["crossfilter", "link", "none"],
                        "description": "Type of click behavior"
                    },
                    "linkType": {
                        "enum": ["question", "dashboard", "url"],
                        "description": "Type of link (when type is 'link')"
                    },
                    "targetId": {
                        "type": "integer",
                        "description": "ID of target question/dashboard (when linkType is question/dashboard)"
                    },
                    "linkTemplate": {
                        "type": "string",
                        "description": "URL template (when linkType is 'url')",
                        "example": "/dashboard/1?param={{column:Field}}"
                    }
                }
            }
        }
    }
    
    # Chart-specific documentation
    chart_docs = {
        "table": {
            "description": "Data table visualization settings",
            "settings": {
                "table.columns": {
                    "type": "array",
                    "description": "Column configuration for table display",
                    "items": {
                        "type": "object",
                        "properties": {
                            "name": {"type": "string", "description": "Column name"},
                            "fieldRef": {"description": "Field reference array"},
                            "enabled": {"type": "boolean", "description": "Whether column is visible"}
                        }
                    }
                },
                "column_settings": {
                    "type": "object",
                    "description": "Per-column formatting settings",
                    "note": "Keys use field reference format: ['ref',['field',123,null]] or ['name','Column Name']",
                    "properties": {
                        "column_title": {"type": "string", "description": "Custom column display name"},
                        "show_mini_bar": {"type": "boolean", "description": "Show mini bar chart in cells"},
                        "number_style": {"enum": ["currency", "percent", "scientific", "decimal"]},
                        "currency": {"type": "string", "example": "USD"},
                        "currency_style": {"enum": ["symbol", "code", "name"]},
                        "currency_in_header": {"type": "boolean"},
                        "number_separators": {"type": "string", "example": ",."},
                        "decimals": {"type": "integer", "description": "Number of decimal places"},
                        "scale": {"type": "number", "description": "Scaling factor"},
                        "prefix": {"type": "string", "description": "Text prefix"},
                        "suffix": {"type": "string", "description": "Text suffix"},
                        "date_style": {"type": "string", "example": "YYYY-MM-DD"},
                        "time_style": {"type": "string", "example": "HH:mm"}
                    }
                }
            },
            "example": {
                "table.columns": [
                    {"name": "ID", "fieldRef": ["field", 1, None], "enabled": True},
                    {"name": "Name", "fieldRef": ["expression", "Custom Name"], "enabled": True}
                ],
                "column_settings": {
                    "[\"ref\",[\"field\",1,null]]": {
                        "column_title": "Customer ID",
                        "show_mini_bar": False
                    },
                    "[\"name\",\"Revenue\"]": {
                        "column_title": "Total Revenue",
                        "number_style": "currency",
                        "currency": "USD",
                        "decimals": 2
                    }
                }
            }
        },
        
        "bar": {
            "description": "Bar chart visualization settings",
            "settings": {
                "graph.dimensions": {
                    "type": "array",
                    "description": "Fields to use for chart dimensions (X-axis categories)",
                    "example": ["Category", "Region"]
                },
                "graph.metrics": {
                    "type": "array", 
                    "description": "Fields to use for chart metrics (Y-axis values)",
                    "example": ["Revenue", "Profit"]
                },
                "stackable.stack_type": {
                    "enum": [None, "stacked", "normalized"],
                    "description": "How to stack multiple series"
                },
                "graph.show_values": {
                    "type": "boolean",
                    "description": "Show values on bars"
                },
                "graph.show_stack_values": {
                    "enum": ["total", "series", "all"],
                    "description": "Which values to show on stacked bars"
                },
                "graph.x_axis.scale": {
                    "enum": ["ordinal", "linear", "timeseries"],
                    "description": "X-axis scale type"
                },
                "graph.y_axis.scale": {
                    "enum": ["linear", "log", "pow"],
                    "description": "Y-axis scale type"
                },
                "graph.x_axis.axis_enabled": {"type": "boolean"},
                "graph.y_axis.axis_enabled": {"type": "boolean"},
                "graph.x_axis.labels_enabled": {"type": "boolean"},
                "graph.y_axis.labels_enabled": {"type": "boolean"},
                "graph.x_axis.title_text": {"type": "string", "description": "X-axis label"},
                "graph.y_axis.title_text": {"type": "string", "description": "Y-axis label"},
                "graph.y_axis.auto_range": {"type": "boolean"},
                "graph.y_axis.min": {"type": "number", "description": "Y-axis minimum value"},
                "graph.y_axis.max": {"type": "number", "description": "Y-axis maximum value"},
                "series_settings": {
                    "type": "object",
                    "description": "Per-series customization",
                    "note": "Keys are series names from your data",
                    "properties": {
                        "display": {"enum": ["bar"], "description": "Display type for this series"},
                        "color": {"type": "string", "description": "Series color (hex code)", "example": "#509EE3"},
                        "name": {"type": "string", "description": "Custom series name"}
                    }
                }
            },
            "example": {
                "graph.dimensions": ["Category"],
                "graph.metrics": ["Revenue"],
                "graph.show_values": True,
                "graph.y_axis.title_text": "Revenue ($)",
                "graph.x_axis.title_text": "Product Category",
                "series_settings": {
                    "Revenue": {
                        "color": "#509EE3",
                        "name": "Total Revenue"
                    }
                }
            }
        },
        
        "line": {
            "description": "Line chart visualization settings",
            "settings": {
                "graph.dimensions": {
                    "type": "array",
                    "description": "Fields to use for chart dimensions (X-axis)",
                    "example": ["Date", "Month"]
                },
                "graph.metrics": {
                    "type": "array",
                    "description": "Fields to use for chart metrics (Y-axis values)",
                    "example": ["Revenue", "Orders"]
                },
                "graph.x_axis.scale": {
                    "enum": ["linear", "log", "pow", "timeseries"],
                    "description": "X-axis scale type"
                },
                "graph.y_axis.scale": {
                    "enum": ["linear", "log", "pow"],
                    "description": "Y-axis scale type"
                },
                "graph.x_axis.axis_enabled": {"type": "boolean"},
                "graph.y_axis.axis_enabled": {"type": "boolean"},
                "graph.x_axis.labels_enabled": {"type": "boolean"},
                "graph.y_axis.labels_enabled": {"type": "boolean"},
                "graph.x_axis.title_text": {"type": "string", "description": "X-axis label"},
                "graph.y_axis.title_text": {"type": "string", "description": "Y-axis label"},
                "graph.y_axis.auto_range": {"type": "boolean"},
                "graph.y_axis.min": {"type": "number"},
                "graph.y_axis.max": {"type": "number"},
                "graph.y_axis.auto_split": {"type": "boolean", "description": "Auto-split Y-axis for multiple metrics"},
                "graph.y_axis.unpin_from_zero": {"type": "boolean"},
                "graph.show_values": {"type": "boolean", "description": "Show values on data points"},
                "graph.label_value_frequency": {"enum": ["fit", "all"]},
                "graph.label_value_formatting": {"enum": ["auto", "compact", "full"]},
                "graph.show_trendline": {"type": "boolean"},
                "graph.tooltip_type": {"enum": ["series_comparison", "default"]},
                "series_settings": {
                    "type": "object",
                    "description": "Per-series customization",
                    "properties": {
                        "display": {"enum": ["line", "bar", "area"]},
                        "line.interpolate": {"enum": ["linear", "cardinal", "step-before", "step-after"]},
                        "line.marker_enabled": {"type": "boolean"},
                        "line.missing": {"enum": ["interpolate", "zero", "none"], "description": "How to handle missing values"},
                        "color": {"type": "string", "example": "#509EE3"}
                    }
                }
            },
            "example": {
                "graph.dimensions": ["Date"],
                "graph.metrics": ["Revenue", "Orders"],
                "graph.x_axis.scale": "timeseries",
                "graph.y_axis.auto_split": True,
                "graph.show_trendline": False,
                "series_settings": {
                    "Revenue": {
                        "display": "line",
                        "line.interpolate": "linear",
                        "line.marker_enabled": True,
                        "color": "#509EE3"
                    },
                    "Orders": {
                        "display": "line",
                        "line.interpolate": "linear", 
                        "color": "#88BF4D"
                    }
                }
            }
        },
        
        "combo": {
            "description": "Combo chart visualization settings (combines multiple chart types)",
            "settings": {
                "graph.dimensions": {
                    "type": "array",
                    "description": "Fields to use for chart dimensions (X-axis)",
                    "example": ["Date"]
                },
                "graph.metrics": {
                    "type": "array",
                    "description": "Fields to use for chart metrics",
                    "example": ["Revenue", "Orders", "Conversion_Rate"]
                },
                "graph.x_axis.scale": {"enum": ["linear", "log", "pow", "timeseries"]},
                "graph.y_axis.scale": {"enum": ["linear", "log", "pow"]},
                "graph.x_axis.axis_enabled": {"type": "boolean"},
                "graph.y_axis.axis_enabled": {"type": "boolean"},
                "graph.x_axis.labels_enabled": {"type": "boolean"},
                "graph.y_axis.labels_enabled": {"type": "boolean"},
                "graph.x_axis.title_text": {"type": "string"},
                "graph.y_axis.title_text": {"type": "string"},
                "graph.y_axis.auto_split": {
                    "type": "boolean",
                    "description": "Automatically create separate Y-axes for different metrics"
                },
                "series_settings": {
                    "type": "object",
                    "description": "Per-series customization - KEY REQUIREMENT for combo charts",
                    "note": "Each metric must specify its display type and axis",
                    "properties": {
                        "display": {
                            "enum": ["line", "bar", "area"],
                            "description": "Chart type for this series"
                        },
                        "axis": {
                            "enum": ["left", "right"],
                            "description": "Which Y-axis to use"
                        },
                        "color": {"type": "string", "example": "#509EE3"},
                        "line.interpolate": {"enum": ["linear", "cardinal", "step-before", "step-after"]},
                        "line.marker_enabled": {"type": "boolean"}
                    }
                }
            },
            "example": {
                "graph.dimensions": ["Date"],
                "graph.metrics": ["Revenue", "Orders", "Conversion_Rate"],
                "graph.x_axis.scale": "timeseries",
                "graph.y_axis.auto_split": True,
                "series_settings": {
                    "Revenue": {
                        "display": "bar",
                        "axis": "left",
                        "color": "#509EE3"
                    },
                    "Orders": {
                        "display": "line",
                        "axis": "left",
                        "line.interpolate": "linear",
                        "line.marker_enabled": True,
                        "color": "#88BF4D"
                    },
                    "Conversion_Rate": {
                        "display": "line",
                        "axis": "right",
                        "line.interpolate": "linear",
                        "color": "#F9CF48"
                    }
                }
            }
        }
    }
    
    # Filter documentation for requested chart types
    filtered_docs = {}
    valid_types = []
    
    for chart_type in chart_types:
        if chart_type in chart_docs:
            filtered_docs[chart_type] = chart_docs[chart_type]
            valid_types.append(chart_type)
    
    return {
        "common_settings": common_settings,
        "chart_specific": filtered_docs,
        "requested_types": valid_types,
        "invalid_types": [t for t in chart_types if t not in chart_docs]
    }


def get_validation_notes() -> List[str]:
    """Get general validation notes for visualization settings."""
    return [
        "Field references must use exact format: [\"ref\",[\"field\",123,null]] for database fields",
        "Field references for expressions: [\"ref\",[\"expression\",\"Expression Name\"]]",
        "Field references by name: [\"name\",\"Column Name\"] for aggregations/custom columns",
        "Color values must be hex codes (#509EE3) or Metabase color names",
        "For combo charts, each series in series_settings must specify 'display' and 'axis'",
        "graph.dimensions and graph.metrics arrays should contain field names from your query results",
        "When using column_settings, ensure the key format matches your field structure exactly",
        "Enum values are case-sensitive and must match exactly as specified",
        "Boolean values should be true/false (lowercase)",
        "Numbers can be integers or floats as appropriate for the setting"
    ]


def validate_visualization_settings(
    settings: Dict[str, Any], 
    display_type: str,
    field_names: Optional[List[str]] = None
) -> Tuple[bool, List[str]]:
    """
    Validate visualization settings for correctness.
    
    Args:
        settings: Visualization settings to validate
        display_type: Chart display type (table, bar, line, combo)
        field_names: Optional list of available field names for validation
        
    Returns:
        Tuple of (is_valid, error_messages)
    """
    errors = []
    
    if not isinstance(settings, dict):
        errors.append("Visualization settings must be a JSON object")
        return False, errors
    
    # Validate based on chart type
    if display_type == "bar":
        # Bar charts should have dimensions and metrics
        if "graph.dimensions" not in settings:
            errors.append("Bar charts require 'graph.dimensions' to be specified")
        if "graph.metrics" not in settings:
            errors.append("Bar charts require 'graph.metrics' to be specified")
            
        # Validate stackable.stack_type if present
        if "stackable.stack_type" in settings:
            valid_stack_types = [None, "stacked", "normalized"]
            if settings["stackable.stack_type"] not in valid_stack_types:
                errors.append(f"Invalid stackable.stack_type. Must be one of: {valid_stack_types}")
                
        # Validate axis scales
        if "graph.x_axis.scale" in settings:
            valid_x_scales = ["ordinal", "linear", "timeseries"]
            if settings["graph.x_axis.scale"] not in valid_x_scales:
                errors.append(f"Invalid graph.x_axis.scale. Must be one of: {valid_x_scales}")
                
        if "graph.y_axis.scale" in settings:
            valid_y_scales = ["linear", "log", "pow"]
            if settings["graph.y_axis.scale"] not in valid_y_scales:
                errors.append(f"Invalid graph.y_axis.scale. Must be one of: {valid_y_scales}")
    
    elif display_type == "line":
        # Line charts should have dimensions and metrics
        if "graph.dimensions" not in settings:
            errors.append("Line charts require 'graph.dimensions' to be specified")
        if "graph.metrics" not in settings:
            errors.append("Line charts require 'graph.metrics' to be specified")
            
        # Validate axis scales
        if "graph.x_axis.scale" in settings:
            valid_x_scales = ["linear", "log", "pow", "timeseries"]
            if settings["graph.x_axis.scale"] not in valid_x_scales:
                errors.append(f"Invalid graph.x_axis.scale. Must be one of: {valid_x_scales}")
                
        if "graph.y_axis.scale" in settings:
            valid_y_scales = ["linear", "log", "pow"]
            if settings["graph.y_axis.scale"] not in valid_y_scales:
                errors.append(f"Invalid graph.y_axis.scale. Must be one of: {valid_y_scales}")
    
    elif display_type == "combo":
        # Combo charts require dimensions, metrics, and series_settings
        if "graph.dimensions" not in settings:
            errors.append("Combo charts require 'graph.dimensions' to be specified")
        if "graph.metrics" not in settings:
            errors.append("Combo charts require 'graph.metrics' to be specified")
        if "series_settings" not in settings:
            errors.append("Combo charts require 'series_settings' to be specified")
        elif isinstance(settings["series_settings"], dict):
            # Validate each series has required fields
            for series_name, series_config in settings["series_settings"].items():
                if not isinstance(series_config, dict):
                    errors.append(f"Series '{series_name}' settings must be an object")
                    continue
                    
                if "display" not in series_config:
                    errors.append(f"Series '{series_name}' must specify 'display' type")
                elif series_config["display"] not in ["line", "bar", "area"]:
                    errors.append(f"Series '{series_name}' display type must be 'line', 'bar', or 'area'")
                    
                if "axis" not in series_config:
                    errors.append(f"Series '{series_name}' must specify 'axis' (left or right)")
                elif series_config["axis"] not in ["left", "right"]:
                    errors.append(f"Series '{series_name}' axis must be 'left' or 'right'")
    
    elif display_type == "table":
        # Table-specific validations
        if "column_settings" in settings:
            if not isinstance(settings["column_settings"], dict):
                errors.append("column_settings must be an object")
    
    # Validate series_settings if present (for any chart type)
    if "series_settings" in settings and isinstance(settings["series_settings"], dict):
        for series_name, series_config in settings["series_settings"].items():
            if isinstance(series_config, dict):
                # Validate color format if present
                if "color" in series_config:
                    color = series_config["color"]
                    if isinstance(color, str) and not (color.startswith("#") and len(color) == 7):
                        # Allow common Metabase color names
                        valid_color_names = ["brand", "accent1", "accent2", "accent3", "accent4", "accent5", "accent6", "accent7"]
                        if color not in valid_color_names:
                            errors.append(f"Series '{series_name}' color must be a hex code (#RRGGBB) or valid color name")
                
                # Validate line interpolation if present
                if "line.interpolate" in series_config:
                    valid_interpolations = ["linear", "cardinal", "step-before", "step-after"]
                    if series_config["line.interpolate"] not in valid_interpolations:
                        errors.append(f"Series '{series_name}' line.interpolate must be one of: {valid_interpolations}")
    
    # Validate boolean fields
    boolean_fields = [
        "card.hide_empty", "graph.show_values", "graph.x_axis.axis_enabled", 
        "graph.y_axis.axis_enabled", "graph.x_axis.labels_enabled", 
        "graph.y_axis.labels_enabled", "graph.y_axis.auto_range", 
        "graph.y_axis.auto_split", "graph.y_axis.unpin_from_zero", 
        "graph.show_trendline"
    ]
    
    for field in boolean_fields:
        if field in settings and not isinstance(settings[field], bool):
            errors.append(f"'{field}' must be a boolean value (true/false)")
    
    # Validate numeric fields
    numeric_fields = ["graph.y_axis.min", "graph.y_axis.max"]
    for field in numeric_fields:
        if field in settings and not isinstance(settings[field], (int, float)):
            errors.append(f"'{field}' must be a number")
    
    return len(errors) == 0, errors


@mcp.tool(
    name="GET_VISUALIZATION_DOCUMENT", 
    description="CRITICAL: Get Metabase visualization settings documentation for chart types (table, bar, line, combo) - MUST be called before creating/updating card visualization settings"
)
async def get_visualization_document(
    chart_types: List[str],
    ctx: Context
) -> str:
    """
    **CRITICAL: Call this tool before working with visualization settings**
    
    Get comprehensive Metabase visualization settings documentation for specific chart types.
    
    This tool provides the exact syntax, structure, and examples needed to correctly
    configure visualization settings for Metabase cards. It includes:
    - Common settings available for all chart types
    - Chart-specific settings and their valid values
    - Complete working examples for each chart type
    - Validation guidelines and best practices
    
    You MUST call this tool before creating or updating cards with custom visualization
    settings to ensure correct syntax and avoid validation errors.
    
    SUPPORTED CHART TYPES:
    - table: Data table with column formatting, sorting, and conditional formatting
    - bar: Bar charts with stacking options, axis configuration, and series customization
    - line: Line charts with interpolation, markers, trend lines, and multiple Y-axes
    - combo: Combination charts mixing different chart types (bars, lines, areas)
    
    Args:
        chart_types: List of chart types to get documentation for (e.g., ["bar", "line"])
                    Must be from: table, bar, line, combo
        
    Returns:
        Comprehensive visualization settings documentation as JSON string
    """
    logger.info(f"Tool called: GET_VISUALIZATION_DOCUMENT(chart_types={chart_types})")
    
    try:
        # Validate input
        if not isinstance(chart_types, list) or not chart_types:
            return format_error_response(
                status_code=400,
                error_type="invalid_parameter",
                message="chart_types must be a non-empty list of chart type strings",
                request_info={"chart_types": chart_types}
            )
        
        # Get filtered documentation
        docs = get_visualization_docs_for_types(chart_types)
        
        # Build response
        response_data = {
            "success": True,
            "requested_types": chart_types,
            "valid_types": docs["requested_types"],
            "invalid_types": docs["invalid_types"],
            "documentation": {
                "common_settings": docs["common_settings"],
                "chart_specific": docs["chart_specific"]
            },
            "validation_notes": get_validation_notes(),
            "usage_note": "Use this documentation to structure visualization_settings objects for create_card and update_card tools"
        }
        
        # Add warning for invalid types
        if docs["invalid_types"]:
            response_data["warning"] = f"Unsupported chart types: {docs['invalid_types']}. SUPPORTED TYPES: table, bar, line, combo"
        
        logger.info(f"Documentation provided for chart types: {docs['requested_types']}")
        
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
            error_type="documentation_error",
            message=f"Error loading visualization documentation: {str(e)}",
            request_info={"chart_types": chart_types}
        )
