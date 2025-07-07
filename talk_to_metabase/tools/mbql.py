"""
MBQL (Metabase Query Language) schema and validation tools.
"""

import json
import logging
from typing import Dict, List, Tuple, Any, Optional

import jsonschema
from mcp.server.fastmcp import Context

from ..server import get_server_instance
from ..resources import load_json_resource
from .common import format_error_response, check_response_size

logger = logging.getLogger(__name__)

# Register tools with the server
mcp = get_server_instance()

def load_mbql_schema() -> Optional[Dict[str, Any]]:
    """Load MBQL JSON schema."""
    try:
        return load_json_resource("schemas/mbql_schema.json")
    except Exception as e:
        logger.error(f"Error loading MBQL schema: {e}")
        return None

def validate_mbql_query(query: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """
    Validate MBQL query against the JSON schema.
    
    Args:
        query: MBQL query dictionary
        
    Returns:
        Tuple of (is_valid, error_messages)
    """
    schema = load_mbql_schema()
    if schema is None:
        return False, ["Could not load MBQL schema"]
    
    try:
        jsonschema.validate(query, schema)
        return True, []
    except jsonschema.ValidationError as e:
        error_path = " -> ".join(str(p) for p in e.absolute_path) if e.absolute_path else "root"
        return False, [f"Validation error at {error_path}: {e.message}"]
    except jsonschema.SchemaError as e:
        return False, [f"Schema error: {e.message}"]
    except Exception as e:
        return False, [f"Unexpected validation error: {str(e)}"]

def validate_mbql_query_helper(query: Dict[str, Any]) -> Dict[str, Any]:
    """
    Helper function to validate MBQL query and return structured result.
    
    Args:
        query: MBQL query dictionary
        
    Returns:
        Dictionary with validation results
    """
    is_valid, errors = validate_mbql_query(query)
    
    return {
        "valid": is_valid,
        "errors": errors,
        "query_provided": bool(query),
        "validation_timestamp": "2025-01-03T00:00:00Z"
    }

@mcp.tool(name="GET_MBQL_SCHEMA", description="IMPORTANT: Get comprehensive MBQL query schema - Call before creating/editing MBQL queries")
async def get_mbql_schema(ctx: Context) -> str:
    """
    **IMPORTANT: Call this tool before creating or editing MBQL queries**
    
    Get comprehensive JSON schema for MBQL (Metabase Query Language) queries.
    
    **🎯 MBQL IS METABASE'S NATIVE QUERY FORMAT**
    
    MBQL is the structured query language that Metabase's user-friendly UI generates when users 
    create questions through the visual query builder. It's database-agnostic, semantically rich, 
    and the recommended way to create analytical queries in Metabase.
    
    **Why use MBQL:**
    - It's what Metabase's UI creates - you're working with Metabase's native format
    - Database-agnostic - works across PostgreSQL, MySQL, BigQuery, etc.
    - Structured and validated - prevents SQL injection and syntax errors
    - Semantically rich - clear meaning for aggregations, grouping, filtering
    - Future-proof - evolves with Metabase's capabilities
    
    **This schema includes:**
    - Complete structure definitions for all MBQL clauses
    - Examples for each clause type  
    - Validation rules and constraints
    - Documentation for field references, expressions, filters, and aggregations
    
    Args:
        ctx: MCP context
        
    Returns:
        Complete MBQL schema as JSON string with comprehensive documentation and examples
    """
    logger.info("Tool called: GET_MBQL_SCHEMA()")
    
    try:
        schema = load_mbql_schema()
        if schema is None:
            return format_error_response(
                status_code=500,
                error_type="schema_load_error",
                message="Could not load MBQL schema",
                request_info={"tool": "GET_MBQL_SCHEMA"}
            )
        
        # Convert to JSON string
        response = json.dumps(schema, indent=2)
        
        # Check response size before returning
        metabase_ctx = ctx.request_context.lifespan_context
        config = metabase_ctx.auth.config
        return check_response_size(response, config)
        
    except Exception as e:
        logger.error(f"Error in GET_MBQL_SCHEMA: {e}")
        return format_error_response(
            status_code=500,
            error_type="tool_error",
            message=f"Error retrieving MBQL schema: {str(e)}",
            request_info={"tool": "GET_MBQL_SCHEMA"}
        )
