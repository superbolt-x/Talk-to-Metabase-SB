"""
Main MCP server implementation for Metabase integration.
"""

import asyncio
import logging
import os
import sys
from contextlib import asynccontextmanager
from typing import Any, AsyncIterator, Dict, Optional

from mcp.server.fastmcp import Context, FastMCP

from .auth import MetabaseAuth
from .config import MetabaseConfig

# Set up logging
log_level = os.environ.get("LOG_LEVEL", "INFO").upper()
logging.basicConfig(
    level=getattr(logging, log_level),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)


class MetabaseContext:
    """Context object for Metabase integration."""
    
    def __init__(self, auth: MetabaseAuth):
        """Initialize with authentication."""
        self.auth = auth


@asynccontextmanager
async def metabase_lifespan(server: FastMCP) -> AsyncIterator[MetabaseContext]:
    """Manage application lifecycle with Metabase context."""
    config = MetabaseConfig.from_env()
    auth = MetabaseAuth(config)
    
    # Authenticate on startup
    if not await auth.authenticate():
        logger.error("Failed to authenticate with Metabase on startup")
        # We still continue, as we'll retry authentication on each request
    
    try:
        yield MetabaseContext(auth=auth)
    finally:
        # Cleanup on shutdown
        await auth.close()


def create_server() -> FastMCP:
    """Create and configure the MCP server for Metabase."""
    logger.info("Creating MCP server...")
    server_name = "Metabase"
    logger.info(f"Server name: {server_name}")
    mcp = FastMCP(
        server_name,
        lifespan=metabase_lifespan,
        dependencies=["httpx", "pydantic", "python-dotenv"],
    )
    return mcp


# Create a singleton instance of the server
_server_instance = None

def get_server_instance() -> FastMCP:
    """Get or create the server instance."""
    global _server_instance
    if _server_instance is None:
        _server_instance = create_server()
    return _server_instance


def run_server() -> None:
    """Run the server with appropriate transport."""
    # Get the server instance
    logger.info("Getting server instance...")
    mcp = get_server_instance()
    
    # Import tools modules to register tools with the server
    logger.info("Registering tools...")
    try:
        # Import resources module to ensure it's available
        from . import resources
        
        # This import triggers the tool registration
        from . import tools
        logger.info("Core tools registered successfully")
        
        # Load context tools if enabled (after environment is properly set)
        from .config import MetabaseConfig
        config = MetabaseConfig.from_env()
        if config.context_auto_inject:
            logger.info("Context auto-inject enabled, loading context tools...")
            from .tools import context
            logger.info("Context tools loaded successfully")
        else:
            logger.info("Context auto-inject disabled, context tools not loaded")
            
        logger.info("All tools registered successfully")
    except Exception as e:
        logger.error(f"Error registering tools: {e}")
        import traceback
        traceback.print_exc()
    
    # Log the registered tools for debugging
    logger.info(f"Server initialized with MCP tools")
    logger.info("The following tools should be available:")
    logger.info("- get_card: Retrieve a card by ID")
    logger.info("- get_dashboard: Retrieve a dashboard by ID")
    logger.info("- create_dashboard: Create a new dashboard")
    logger.info("- list_collections: List all collections")
    logger.info("- list_databases: List all databases")
    logger.info("- search_resources: Search for resources across Metabase")
    logger.info("- GET_METABASE_GUIDELINES: Get context guidelines (if enabled)")
    
    # Log context configuration status
    from .config import MetabaseConfig
    config = MetabaseConfig.from_env()
    if config.context_auto_inject:
        logger.info("Metabase context guidelines enabled")
    else:
        logger.info("Metabase context guidelines disabled")
    
    # Determine the transport method from the environment
    transport = os.environ.get("MCP_TRANSPORT", "stdio").lower()
    
    if transport == "stdio":
        logger.info("Running server with stdio transport")
        mcp.run(transport="stdio")
    elif transport == "sse":
        logger.info("Running server with SSE transport")
        mcp.run(transport="sse")
    elif transport == "streamable-http":
        logger.info("Running server with streamable-http transport")
        mcp.run(transport="streamable-http")
    else:
        logger.error(f"Unknown transport: {transport}")
        logger.info("Defaulting to stdio transport")
        mcp.run(transport="stdio")  # Default to stdio


if __name__ == "__main__":
    run_server()
