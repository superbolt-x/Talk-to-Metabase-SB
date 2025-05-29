"""
Context guidelines tool for Metabase MCP server.
"""

import json
import logging
import os

from mcp.server.fastmcp import Context

from ..server import get_server_instance
from ..context_state import mark_guidelines_called
from .common import get_metabase_client, format_error_response, check_response_size

logger = logging.getLogger(__name__)

# Register tools with the server
mcp = get_server_instance()


@mcp.tool(name="GET_METABASE_GUIDELINES", description="REQUIRED: Get Metabase context guidelines - MUST be called first in any Metabase conversation when context is activated")
async def get_metabase_guidelines(ctx: Context) -> str:
    """
    **REQUIRED TOOL - MUST BE CALLED FIRST**
    
    Get essential Metabase context guidelines for this instance.
    
    When Metabase context is activated, this tool MUST be called at the beginning 
    of any Metabase-related conversation before using any other Metabase tools.
    
    This tool provides:
    - Instance-specific information and best practices
    - Important collections and their purposes
    - Database information and usage guidelines
    - Query performance recommendations
    - Data governance standards
    
    Args:
        ctx: MCP context
        
    Returns:
        Essential Metabase guidelines and context information for this instance
    """
    logger.info("Tool called: GET_METABASE_GUIDELINES()")
    
    try:
        # Get the configuration from the context
        metabase_ctx = ctx.request_context.lifespan_context
        config = metabase_ctx.auth.config
        
        # Mark that guidelines have been called for this context
        mark_guidelines_called(ctx)
        logger.info("Context marked as having called guidelines - enforcement should now pass")
        
        # Provide the default guidelines with template substitution
        guidelines_template = f"""# Metabase Guidelines for {{METABASE_URL}}

## Instance Information
- **URL**: {{METABASE_URL}}
- **User**: {{METABASE_USERNAME}}

## Important Collections

### Executive Dashboards
- Contains high-level KPI dashboards for leadership team
- Key metrics: Revenue, Growth, Customer Acquisition
- Usually found in collections named "Executive", "Leadership", or "KPIs"

### Marketing Analytics
- Campaign performance, attribution analysis, and funnel metrics
- Updated daily with fresh data
- Look for collections named "Marketing", "Campaigns", or "Attribution"

### Sales Reports
- Pipeline analysis, forecasting, and team performance
- Real-time sales tracking and quota monitoring
- Typically in collections named "Sales", "Pipeline", or "Revenue"

## Key Databases

### Production Analytics
- Primary data warehouse with cleaned, transformed data
- Use for most analysis and reporting needs
- Tables are well-documented with clear naming conventions

### Raw Data
- Contains unprocessed source data
- Use with caution - data quality may vary
- Primarily for data engineering and troubleshooting

## Best Practices

### Query Performance
- Always use date filters to limit data scope
- Prefer materialized views over raw tables when available
- Add LIMIT clauses when exploring large datasets

### Dashboard Design
- Keep dashboards focused on a single business area
- Use consistent color schemes and formatting
- Include data freshness indicators where relevant

### Data Governance
- Follow naming conventions: snake_case for tables/columns
- Add descriptions to all cards and dashboards
- Tag resources appropriately for easy discovery

## Common Use Cases

### Weekly Business Review
1. Start with Executive Dashboard collection
2. Focus on revenue trends and key KPIs
3. Drill down into specific metrics as needed

### Campaign Analysis
1. Use Marketing Analytics collection
2. Look at attribution models and funnel metrics
3. Compare performance across channels and time periods

### Sales Performance
1. Check Sales Reports collection for pipeline status
2. Review team performance and quota attainment
3. Analyze conversion rates and deal velocity

## Support and Help

For questions about this Metabase instance:
- Contact your data team or Metabase administrator
- Documentation: {{METABASE_URL}}/reference
- Training materials: Look for "Getting Started" or "Help" collections

## Quick Tips

- Use the search function to quickly find existing dashboards and questions
- Create questions in appropriate collections to keep things organized
- Share dashboard links instead of screenshots for better collaboration
- Set up alerts for critical metrics to stay informed of changes
"""
        
        # Apply template substitution
        clean_url = config.url.rstrip('/')
        guidelines_content = guidelines_template.replace('{METABASE_URL}', clean_url)
        guidelines_content = guidelines_content.replace('{METABASE_USERNAME}', config.username)
        
        response_data = {
            "success": True,
            "guidelines": guidelines_content,
            "source": "built_in_guidelines",
            "metabase_url": clean_url,
            "username": config.username,
            "context_enforced": True
        }
        
        logger.info("Guidelines provided and context marked as called")
        
        # Convert to JSON string
        response = json.dumps(response_data, indent=2)
        
        # Check response size
        return check_response_size(response, config)
        
    except Exception as e:
        logger.error(f"Error in GET_METABASE_GUIDELINES: {e}")
        return format_error_response(
            status_code=500,
            error_type="context_error",
            message=f"Error loading Metabase guidelines: {str(e)}",
            request_info={"tool": "GET_METABASE_GUIDELINES"}
        )
