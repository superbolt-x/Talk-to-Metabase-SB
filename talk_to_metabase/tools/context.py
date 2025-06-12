"""
Context guidelines tool for Metabase MCP server.
"""

import json
import logging
from typing import Optional

from mcp.server.fastmcp import Context

from ..server import get_server_instance
from .common import format_error_response, check_response_size, get_metabase_client

logger = logging.getLogger(__name__)

# Register tools with the server
mcp = get_server_instance()


async def find_guidelines_dashboard(client) -> Optional[int]:
    """
    Find the "Talk to Metabase Guidelines" dashboard in the "000 Talk to Metabase" collection.
    
    Returns:
        Dashboard ID if found, None otherwise
    """
    try:
        # First, find the "000 Talk to Metabase" collection in root
        root_data, status, error = await client.auth.make_request(
            "GET", "collection/root/items", params={"models": ["collection"]}
        )
        
        if error:
            logger.error(f"Error fetching root collections: {error}")
            return None
        
        # Extract items from response
        collections = []
        if isinstance(root_data, dict) and "data" in root_data:
            collections = root_data["data"]
        elif isinstance(root_data, list):
            collections = root_data
        
        # Find the "000 Talk to Metabase" collection
        guidelines_collection_id = None
        for collection in collections:
            if collection.get("name") == "000 Talk to Metabase":
                guidelines_collection_id = collection.get("id")
                break
        
        if not guidelines_collection_id:
            logger.info("Collection '000 Talk to Metabase' not found in root")
            return None
        
        logger.info(f"Found '000 Talk to Metabase' collection with ID: {guidelines_collection_id}")
        
        # Now search for the dashboard in that collection
        collection_data, status, error = await client.auth.make_request(
            "GET", f"collection/{guidelines_collection_id}/items", 
            params={"models": ["dashboard"]}
        )
        
        if error:
            logger.error(f"Error fetching collection contents: {error}")
            return None
        
        # Extract dashboards from response
        dashboards = []
        if isinstance(collection_data, dict) and "data" in collection_data:
            dashboards = collection_data["data"]
        elif isinstance(collection_data, list):
            dashboards = collection_data
        
        # Find the "Talk to Metabase Guidelines" dashboard
        for dashboard in dashboards:
            if dashboard.get("name") == "Talk to Metabase Guidelines":
                dashboard_id = dashboard.get("id")
                logger.info(f"Found 'Talk to Metabase Guidelines' dashboard with ID: {dashboard_id}")
                return dashboard_id
        
        logger.info("Dashboard 'Talk to Metabase Guidelines' not found in collection")
        return None
        
    except Exception as e:
        logger.error(f"Error finding guidelines dashboard: {e}")
        return None


async def extract_guidelines_from_dashboard(client, dashboard_id: int) -> Optional[str]:
    """
    Extract guidelines text from the text box in the guidelines dashboard.
    
    Args:
        client: Metabase client
        dashboard_id: ID of the guidelines dashboard
        
    Returns:
        Guidelines text if found, None otherwise
    """
    try:
        # Get the dashboard data
        dashboard_data, status, error = await client.auth.make_request(
            "GET", f"dashboard/{dashboard_id}"
        )
        
        if error:
            logger.error(f"Error fetching dashboard {dashboard_id}: {error}")
            return None
        
        # Look for text boxes in dashcards
        dashcards = dashboard_data.get("dashcards", [])
        
        for dashcard in dashcards:
            # Check if this is a text card (no card_id and has visualization_settings with text)
            if (dashcard.get("card_id") is None and 
                "visualization_settings" in dashcard and 
                "text" in dashcard["visualization_settings"]):
                
                text_content = dashcard["visualization_settings"]["text"]
                logger.info(f"Found text content in dashcard {dashcard.get('id')}")
                return text_content
        
        logger.info(f"No text content found in dashboard {dashboard_id}")
        return None
        
    except Exception as e:
        logger.error(f"Error extracting guidelines from dashboard {dashboard_id}: {e}")
        return None


def get_default_guidelines_with_setup(metabase_url: str, username: str) -> str:
    """
    Return default guidelines with setup instructions.
    
    Args:
        metabase_url: Metabase instance URL
        username: Current username
        
    Returns:
        Default guidelines with setup instructions
    """
    return f"""# Metabase Guidelines for {metabase_url}

## Setup Required

Custom guidelines are not yet configured for this Metabase instance.

### To Set Up Custom Guidelines:

1. **Create the Collection**:
   - Go to your Metabase instance: {metabase_url}
   - Create a collection named exactly: `000 Talk to Metabase`
   - Place it at the root level (not inside any other collection)
   - Make sure it's readable by all Talk to Metabase users

2. **Create the Guidelines Dashboard**:
   - Inside the "000 Talk to Metabase" collection
   - Create a dashboard named exactly: `Talk to Metabase Guidelines`
   - Add a text box to this dashboard
   - Write your custom guidelines in the text box

3. **Guidelines Content Suggestions**:
   Include information about:
   - Important collections and their purposes
   - Key databases and their usage guidelines
   - Naming conventions and data governance standards
   - Query performance recommendations
   - Common use cases and workflows specific to your organization
   - Contact information for data team or administrators

### Current Session Information
- **URL**: {metabase_url}
- **User**: {username}

## Default Recommendations

Until custom guidelines are set up, here are some general best practices:

### Query Performance
- Always use date filters to limit data scope
- Add LIMIT clauses when exploring large datasets
- Prefer aggregated views over raw table scans

### Dashboard Design
- Keep dashboards focused on a single business area
- Use consistent naming conventions
- Include data freshness indicators where relevant

### Data Exploration
- Use the search function to find existing resources
- Explore collection hierarchies to understand data organization
- Check existing questions before creating new ones

### Support
- Contact your data team for instance-specific guidance
- Check existing documentation and collections for help materials

Once you set up the custom guidelines dashboard, this tool will automatically use your organization-specific content instead of these default instructions."""


@mcp.tool(name="GET_METABASE_GUIDELINES", description="IMPORTANT: Get essential Metabase context guidelines - Should be called first in any Metabase conversation")
async def get_metabase_guidelines(ctx: Context) -> str:
    """
    **IMPORTANT: Call this tool first for best results**
    
    Get essential Metabase context guidelines for this instance.
    
    This tool automatically retrieves custom guidelines from your Metabase instance.
    Guidelines are stored in a text box within the "Talk to Metabase Guidelines" 
    dashboard in the "000 Talk to Metabase" collection.
    
    If custom guidelines are not found, provides default guidelines with setup
    instructions for creating your own custom guidelines.
    
    This tool provides instance-specific information and best practices that help
    ensure accurate and contextually appropriate responses when working with Metabase.
    While not technically required, calling this tool at the beginning of Metabase
    conversations will significantly improve response quality.
    
    Provides:
    - Custom organization-specific guidelines (if configured)
    - Setup instructions for custom guidelines (if not configured)
    - Instance-specific information and URLs
    - Best practices and recommendations
    
    Args:
        ctx: MCP context
        
    Returns:
        Metabase guidelines and context information for this instance
    """
    logger.info("Tool called: GET_METABASE_GUIDELINES()")
    
    try:
        # Get the configuration and client from the context
        metabase_ctx = ctx.request_context.lifespan_context
        config = metabase_ctx.auth.config
        client = get_metabase_client(ctx)
        
        clean_url = config.url.rstrip('/')
        
        # Try to find and extract custom guidelines from Metabase
        dashboard_id = await find_guidelines_dashboard(client)
        
        guidelines_content = None
        
        if dashboard_id:
            guidelines_content = await extract_guidelines_from_dashboard(client, dashboard_id)
            if guidelines_content:
                # Apply template substitution for custom guidelines
                guidelines_content = guidelines_content.replace('{METABASE_URL}', clean_url)
                guidelines_content = guidelines_content.replace('{METABASE_USERNAME}', config.username)
                logger.info(f"Successfully retrieved custom guidelines from dashboard {dashboard_id}")
            else:
                logger.info(f"Dashboard {dashboard_id} found but no text content extracted")
        
        # Fall back to default guidelines with setup instructions if no custom guidelines found
        if not guidelines_content:
            guidelines_content = get_default_guidelines_with_setup(clean_url, config.username)
            logger.info("Using default guidelines with setup instructions")
        
        response_data = {
            "success": True,
            "guidelines": guidelines_content,
            "metabase_url": clean_url,
            "username": config.username
        }
        
        logger.info("Guidelines provided successfully")
        
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
